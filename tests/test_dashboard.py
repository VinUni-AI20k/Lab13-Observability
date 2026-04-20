from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_page_renders() -> None:
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Observability Control Deck" in response.text
    assert "Latency P50 / P95 / P99" in response.text
