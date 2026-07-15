from fastapi.testclient import TestClient

from noobgpu import __version__
from noobgpu.app import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
