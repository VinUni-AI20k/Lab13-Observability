from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_page_serves_html_with_panels_and_flowchart() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Latency P50 / P95 / P99" in body
    assert "Error Rate With Breakdown" in body
    assert "Quality Proxy" in body
    assert "Observability Flow" in body
    assert "/metrics" in body
    assert "chart.js" in body.lower()
