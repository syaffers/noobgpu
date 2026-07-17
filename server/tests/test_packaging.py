from pathlib import Path

from fastapi.testclient import TestClient

from conftest import REPO_CHALLENGES
from noobgpu.app import create_app
from noobgpu.challenges import load_challenge


def make_static(tmp_path: Path) -> Path:
    static = tmp_path / "static"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<html>noobgpu spa</html>")
    (static / "assets" / "app.js").write_text("// bundle")
    return static


def client_with_static(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            challenges_root=REPO_CHALLENGES,
            db_path=tmp_path / "db.sqlite3",
            static_dir=make_static(tmp_path),
        )
    )


def test_serves_index_at_root(tmp_path: Path):
    response = client_with_static(tmp_path).get("/")
    assert response.status_code == 200
    assert "noobgpu spa" in response.text


def test_spa_fallback_for_client_routes(tmp_path: Path):
    response = client_with_static(tmp_path).get("/challenges/vector-addition")
    assert "noobgpu spa" in response.text


def test_static_assets_served(tmp_path: Path):
    response = client_with_static(tmp_path).get("/assets/app.js")
    assert response.text == "// bundle"


def test_api_wins_over_spa(tmp_path: Path):
    response = client_with_static(tmp_path).get("/api/health")
    assert response.json()["status"] == "ok"


def test_no_static_dir_means_api_only(tmp_path: Path):
    client = TestClient(
        create_app(
            challenges_root=REPO_CHALLENGES,
            db_path=tmp_path / "db.sqlite3",
            static_dir=tmp_path / "missing",
        )
    )
    assert client.get("/api/health").status_code == 200
    assert client.get("/").status_code == 404


def test_cache_dir_env_override(monkeypatch, tmp_path: Path):
    challenge = load_challenge(REPO_CHALLENGES / "relu")
    assert challenge.cache_dir == challenge.dir / ".cache"
    monkeypatch.setenv("NOOBGPU_CACHE_DIR", str(tmp_path / "cache"))
    assert challenge.cache_dir == tmp_path / "cache" / "relu"