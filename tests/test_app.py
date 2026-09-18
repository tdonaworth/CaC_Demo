import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from app import app


def test_index_returns_200():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_healthz_returns_ok():
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_requests_are_audit_logged(caplog):
    client = app.test_client()
    with caplog.at_level("INFO", logger="audit"):
        client.get("/healthz")
    assert any("path=/healthz" in record.getMessage() for record in caplog.records)
