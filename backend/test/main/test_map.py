from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_map_url():
    response = client.get("/map")
    assert response.status_code == 200
    assert "map_url" in response.json()
    assert response.json()["map_url"].endswith(".jpg")