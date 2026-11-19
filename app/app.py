import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from functools import wraps

from flask import Flask, g, jsonify, render_template, request

import config
import db

logging.basicConfig(level=logging.INFO, format="%(message)s")
audit_log = logging.getLogger("audit")


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(config.load())
    app.config.update(overrides or {})
    app.extensions["engine"] = db.make_engine(app.config["DATABASE_URL"])

    def audit(event: str, **fields):
        """Structured (JSON) audit event -> stdout -> CloudWatch Logs (KSI-MLA-*)."""
        audit_log.info(json.dumps({
            "event": event, "request_id": getattr(g, "request_id", None),
            "ts": time.time(), **fields}))

    def principal_for(key: str) -> str | None:
        for valid in app.config["API_KEYS"]:
            if hmac.compare_digest(key.encode(), valid.encode()):
                # Never log or store the raw key; use a short stable fingerprint.
                return hashlib.sha256(valid.encode()).hexdigest()[:16]
        return None

    def require_api_key(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            header = request.headers.get("Authorization", "")
            key = header[7:] if header.startswith("Bearer ") else ""
            principal = principal_for(key) if key else None
            if principal is None:
                audit("auth.denied", path=request.path, remote_addr=request.remote_addr)
                return jsonify(error="unauthorized"), 401
            g.principal = principal
            return fn(*a, **kw)
        return wrapper

    @app.before_request
    def start():
        g.request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    @app.after_request
    def finish(response):
        response.headers["X-Request-Id"] = g.request_id
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Cache-Control"] = "no-store"
        audit("http.request", method=request.method, path=request.path,
              status=response.status_code, remote_addr=request.remote_addr,
              principal=getattr(g, "principal", None))
        return response

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/healthz")
    def healthz():
        # Liveness: process is up. Used by the container HEALTHCHECK.
        return {"status": "ok"}

    @app.route("/readyz")
    def readyz():
        # Readiness: dependencies reachable. Used by the ALB target group.
        if db.ping(app.extensions["engine"]):
            return {"status": "ready"}
        return {"status": "unavailable"}, 503

    @app.get("/api/notes")
    @require_api_key
    def list_notes():
        return jsonify(db.list_notes(app.extensions["engine"], g.principal))

    @app.post("/api/notes")
    @require_api_key
    def create_note():
        body = (request.get_json(silent=True) or {}).get("body")
        if not isinstance(body, str) or not body.strip():
            return jsonify(error="body is required"), 400
        if len(body) > app.config["MAX_NOTE_LENGTH"]:
            return jsonify(error="body too long"), 413
        note = db.add_note(app.extensions["engine"], g.principal, body)
        audit("note.created", note_id=note["id"], principal=g.principal)
        return jsonify(note), 201

    @app.delete("/api/notes/<int:note_id>")
    @require_api_key
    def remove_note(note_id):
        if not db.delete_note(app.extensions["engine"], g.principal, note_id):
            return jsonify(error="not found"), 404
        audit("note.deleted", note_id=note_id, principal=g.principal)
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    # Local dev only. In the container, gunicorn serves `app:app`.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
