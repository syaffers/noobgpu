import json
import queue
import re
import shutil
import subprocess
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from noobgpu.challenges import Challenge, ChallengePackError, load_challenge, load_challenges
from noobgpu.errors import GpuNotAvailableError
from noobgpu.gpu import detect_gpu
from noobgpu.judge import judge_submission
from noobgpu.runner import SubprocessRunner
from noobgpu.store import Store

router = APIRouter(prefix="/api")


class CodeBody(BaseModel):
    code: str


def _root(request: Request) -> Path:
    return request.app.state.challenges_root


def _store(request: Request) -> Store:
    return request.app.state.store


def _challenge_or_404(root: Path, challenge_id: str) -> Challenge:
    pack_dir = root / challenge_id
    if not pack_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"no challenge '{challenge_id}'")
    try:
        return load_challenge(pack_dir)
    except ChallengePackError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _nvcc_status() -> dict:
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        return {"available": False, "version": None}
    try:
        out = subprocess.run(
            [nvcc, "--version"], capture_output=True, text=True, timeout=10
        ).stdout
        match = re.search(r"release (\S+?),", out)
        return {"available": True, "version": match.group(1) if match else None}
    except (OSError, subprocess.TimeoutExpired):
        return {"available": False, "version": None}


@router.get("/gpu")
def gpu_info() -> dict:
    nvcc = _nvcc_status()
    try:
        return {"available": True, **detect_gpu().to_dict(), "nvcc": nvcc}
    except GpuNotAvailableError as exc:
        return {"available": False, "error": str(exc), "nvcc": nvcc}


@router.get("/challenges")
def list_all(request: Request) -> list[dict]:
    return [
        {
            "id": c.id,
            "title": c.title,
            "difficulty": c.difficulty,
            "blurb": c.blurb(),
        }
        for c in load_challenges(_root(request))
    ]


@router.get("/challenges/{challenge_id}")
def challenge_detail(challenge_id: str, request: Request) -> dict:
    c = _challenge_or_404(_root(request), challenge_id)
    return {
        "id": c.id,
        "title": c.title,
        "difficulty": c.difficulty,
        "tolerance": c.tolerance,
        "description": c.description_path.read_text(),
        "starter_code": c.starter_path.read_text(),
        "tests": [
            {"name": t.name, "sample": t.sample} for t in c.tests
        ],
    }


def _sse_judge(
    challenge: Challenge,
    code: str,
    root: Path,
    store: Store,
    sample_only: bool,
    persist: bool,
):
    """Run the judge in a worker thread, yielding SSE frames as events arrive."""
    events: queue.Queue[dict | None] = queue.Queue()

    def work() -> None:
        try:
            result = judge_submission(
                challenge,
                code,
                root,
                SubprocessRunner(),
                sample_only=sample_only,
                on_event=events.put,
            )
            submission_id = None
            if persist:
                submission_id = store.add_submission(
                    challenge_id=challenge.id,
                    code=code,
                    verdict=result.verdict.value,
                    kernel_ms=result.kernel_ms,
                    failed_test=result.failed_test,
                    compile_stderr=result.compile_result.stderr,
                    tests=[t.to_dict() for t in result.tests],
                )
            events.put(
                {
                    "type": "result",
                    "verdict": result.verdict.value,
                    "kernel_ms": result.kernel_ms,
                    "failed_test": result.failed_test,
                    "submission_id": submission_id,
                }
            )
        except Exception as exc:  # noqa: BLE001 — the stream must always end with
            # a visible error event; a silent stop looks like a hang in the UI.
            events.put(
                {"type": "error", "error_type": type(exc).__name__, "message": str(exc)}
            )
        finally:
            events.put(None)

    threading.Thread(target=work, daemon=True).start()
    while (event := events.get()) is not None:
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/challenges/{challenge_id}/run")
def run_samples(challenge_id: str, body: CodeBody, request: Request) -> StreamingResponse:
    challenge = _challenge_or_404(_root(request), challenge_id)
    return StreamingResponse(
        _sse_judge(challenge, body.code, _root(request), _store(request),
                   sample_only=True, persist=False),
        media_type="text/event-stream",
    )


@router.post("/challenges/{challenge_id}/submit")
def submit(challenge_id: str, body: CodeBody, request: Request) -> StreamingResponse:
    challenge = _challenge_or_404(_root(request), challenge_id)
    return StreamingResponse(
        _sse_judge(challenge, body.code, _root(request), _store(request),
                   sample_only=False, persist=True),
        media_type="text/event-stream",
    )


@router.get("/challenges/{challenge_id}/submissions")
def submissions(challenge_id: str, request: Request) -> list[dict]:
    _challenge_or_404(_root(request), challenge_id)
    return _store(request).list_submissions(challenge_id)


@router.get("/submissions/{submission_id}")
def submission_detail(submission_id: int, request: Request) -> dict:
    result = _store(request).get_submission(submission_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"no submission {submission_id}")
    return result


@router.put("/challenges/{challenge_id}/draft", status_code=204)
def save_draft(challenge_id: str, body: CodeBody, request: Request) -> None:
    _challenge_or_404(_root(request), challenge_id)
    _store(request).save_draft(challenge_id, body.code)


@router.get("/challenges/{challenge_id}/draft")
def get_draft(challenge_id: str, request: Request) -> dict:
    """code is null when no draft is saved — not a 404, so fresh challenge
    loads don't spray expected errors into the browser console."""
    _challenge_or_404(_root(request), challenge_id)
    return {"code": _store(request).get_draft(challenge_id)}
