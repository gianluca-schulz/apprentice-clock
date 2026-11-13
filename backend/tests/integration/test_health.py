from fastapi.testclient import TestClient


def test_health_endpoint_returns_200_and_status_ok(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
