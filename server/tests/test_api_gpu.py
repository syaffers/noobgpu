"""M3 done-when: the full challenge lifecycle over HTTP, including SSE streams,
with submissions surviving a store restart."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from conftest import REPO_CHALLENGES, sse_events
from noobgpu.app import create_app

REFERENCE = (REPO_CHALLENGES / "vector-addition" / "reference.cu").read_text()


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.sqlite3"


@pytest.fixture
def client(db_path: Path) -> TestClient:
    return TestClient(create_app(challenges_root=REPO_CHALLENGES, db_path=db_path))


@pytest.mark.gpu
def test_run_streams_events_without_persisting(client: TestClient):
    response = client.post(
        "/api/challenges/vector-addition/run", json={"code": REFERENCE}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = sse_events(response.text)
    types = [e["type"] for e in events]
    assert "compile_start" in types and "compile_end" in types
    assert types[-1] == "result"

    result = events[-1]
    assert result["verdict"] == "accepted"
    assert result["submission_id"] is None
    # Run judges sample tests only.
    test_ends = [e for e in events if e["type"] == "test_end"]
    assert test_ends and all(e["sample"] for e in test_ends)
    assert client.get("/api/challenges/vector-addition/submissions").json() == []


@pytest.mark.gpu
def test_submit_persists_and_survives_restart(client: TestClient, db_path: Path):
    events = sse_events(
        client.post(
            "/api/challenges/vector-addition/submit", json={"code": REFERENCE}
        ).text
    )
    result = events[-1]
    assert result["verdict"] == "accepted"
    submission_id = result["submission_id"]
    assert submission_id is not None
    assert len([e for e in events if e["type"] == "test_end"]) == 4  # all tests

    listed = client.get("/api/challenges/vector-addition/submissions").json()
    assert [s["id"] for s in listed] == [submission_id]
    assert listed[0]["verdict"] == "accepted"

    detail = client.get(f"/api/submissions/{submission_id}").json()
    assert detail["code"] == REFERENCE
    assert len(detail["tests"]) == 4

    # A brand-new app over the same DB file still sees it ("server restart").
    fresh = TestClient(create_app(challenges_root=REPO_CHALLENGES, db_path=db_path))
    assert [s["id"] for s in fresh.get(
        "/api/challenges/vector-addition/submissions").json()] == [submission_id]


@pytest.mark.gpu
def test_submit_wrong_answer_reports_failed_test(client: TestClient):
    wrong = (Path(__file__).parent / "data" / "wrong" / "vector-addition.cu").read_text()
    events = sse_events(
        client.post("/api/challenges/vector-addition/submit", json={"code": wrong}).text
    )
    result = events[-1]
    assert result["verdict"] == "wrong_answer"
    assert result["failed_test"] == "sample-16"


@pytest.mark.gpu
def test_compile_error_streams_stderr(client: TestClient):
    events = sse_events(
        client.post(
            "/api/challenges/vector-addition/run", json={"code": "not cuda"}
        ).text
    )
    compile_end = next(e for e in events if e["type"] == "compile_end")
    assert compile_end["ok"] is False
    assert "error" in compile_end["stderr"]
    assert events[-1]["verdict"] == "compile_error"
