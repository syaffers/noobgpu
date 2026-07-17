from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from conftest import REPO_CHALLENGES
from noobgpu.app import create_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    app = create_app(challenges_root=REPO_CHALLENGES, db_path=tmp_path / "test.sqlite3")
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_gpu_endpoint_shape(client: TestClient):
    body = client.get("/api/gpu").json()
    assert "available" in body
    if body["available"]:
        assert body["name"]
    else:
        assert body["error"]
    assert "available" in body["nvcc"]
    if body["nvcc"]["available"]:
        assert body["nvcc"]["version"]


def test_challenge_list(client: TestClient):
    challenges = client.get("/api/challenges").json()
    assert len(challenges) == 5
    entry = next(c for c in challenges if c["id"] == "vector-addition")
    assert entry["title"] == "Vector Addition"
    assert entry["difficulty"] == "easy"
    assert entry["blurb"]


def test_challenge_detail(client: TestClient):
    detail = client.get("/api/challenges/relu").json()
    assert detail["title"] == "ReLU"
    assert "solve" in detail["starter_code"]
    assert detail["description"].startswith("# ReLU")
    assert any(t["sample"] for t in detail["tests"])


def test_unknown_challenge_is_404(client: TestClient):
    assert client.get("/api/challenges/nope").status_code == 404
    assert client.get("/api/challenges/nope/submissions").status_code == 404
    assert client.put("/api/challenges/nope/draft", json={"code": "x"}).status_code == 404


def test_draft_roundtrip(client: TestClient):
    assert client.get("/api/challenges/relu/draft").json() == {"code": None}
    assert client.put(
        "/api/challenges/relu/draft", json={"code": "// my work"}
    ).status_code == 204
    assert client.get("/api/challenges/relu/draft").json() == {"code": "// my work"}
    client.put("/api/challenges/relu/draft", json={"code": "// v2"})
    assert client.get("/api/challenges/relu/draft").json() == {"code": "// v2"}


def test_submissions_empty(client: TestClient):
    assert client.get("/api/challenges/relu/submissions").json() == []
    assert client.get("/api/submissions/999").status_code == 404


def test_unexpected_judge_crash_ends_stream_with_error_event(
    client: TestClient, monkeypatch
):
    import noobgpu.api
    from conftest import sse_events

    def boom(*args, **kwargs):
        raise RuntimeError("judge exploded")

    monkeypatch.setattr(noobgpu.api, "judge_submission", boom)
    events = sse_events(
        client.post("/api/challenges/relu/run", json={"code": "x"}).text
    )
    assert events[-1]["type"] == "error"
    assert events[-1]["error_type"] == "RuntimeError"
