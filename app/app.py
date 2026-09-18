import logging

from flask import Flask, render_template, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
audit_log = logging.getLogger("audit")


@app.after_request
def log_request(response):
    audit_log.info(
        "method=%s path=%s status=%s remote_addr=%s",
        request.method,
        request.path,
        response.status_code,
        request.remote_addr,
    )
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
