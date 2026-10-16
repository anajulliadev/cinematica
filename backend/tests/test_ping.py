from fastapi.testclient import TestClient

from app.main import app


def test_ping():
    resposta = TestClient(app).get("/api/ping")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}

