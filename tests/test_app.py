import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from app import create_app

KEY = "test-key-1"
AUTH = {"Authorization": f"Bearer {KEY}"}


@pytest.fixture
def client():
    return create_app({"DATABASE_URL": "sqlite://", "API_KEYS": [KEY, "other-key"]}).test_client()


def test_index_returns_200(client):
    assert client.get("/").status_code == 200


def test_healthz_returns_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.get_json() == {"status": "ok"}


def test_readyz_checks_database(client):
    assert client.get("/readyz").get_json() == {"status": "ready"}


def test_security_headers_present(client):
    r = client.get("/")
    assert "max-age" in r.headers["Strict-Transport-Security"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Request-Id"]


def test_requests_are_audit_logged_as_json(client, caplog):
    with caplog.at_level("INFO", logger="audit"):
        client.get("/healthz")
    events = [json.loads(r.getMessage()) for r in caplog.records]
    assert any(e["event"] == "http.request" and e["path"] == "/healthz" for e in events)


def test_notes_require_auth(client, caplog):
    with caplog.at_level("INFO", logger="audit"):
        assert client.get("/api/notes").status_code == 401
        assert client.get("/api/notes", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert any("auth.denied" in r.getMessage() for r in caplog.records)


def test_no_api_keys_configured_fails_closed():
    c = create_app({"DATABASE_URL": "sqlite://", "API_KEYS": []}).test_client()
    assert c.get("/api/notes", headers=AUTH).status_code == 401


def test_note_crud_and_owner_isolation(client):
    r = client.post("/api/notes", json={"body": "hello"}, headers=AUTH)
    assert r.status_code == 201
    nid = r.get_json()["id"]
    assert [n["body"] for n in client.get("/api/notes", headers=AUTH).get_json()] == ["hello"]
    other = {"Authorization": "Bearer other-key"}
    assert client.get("/api/notes", headers=other).get_json() == []
    assert client.delete(f"/api/notes/{nid}", headers=other).status_code == 404
    assert client.delete(f"/api/notes/{nid}", headers=AUTH).status_code == 204


def test_note_validation(client):
    assert client.post("/api/notes", json={}, headers=AUTH).status_code == 400
    assert client.post("/api/notes", json={"body": "x" * 5000}, headers=AUTH).status_code == 413


def test_raw_api_key_never_logged(client, caplog):
    with caplog.at_level("INFO", logger="audit"):
        client.post("/api/notes", json={"body": "x"}, headers=AUTH)
    assert all(KEY not in r.getMessage() for r in caplog.records)
