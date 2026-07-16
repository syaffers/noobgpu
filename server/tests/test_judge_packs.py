"""M2 done-when: for every seed pack, the reference solution is Accepted and a
deliberately wrong one is Wrong Answer — judged end-to-end on the real GPU."""

from pathlib import Path

import pytest

from noobgpu.challenges import load_challenge
from noobgpu.judge import Verdict, judge_submission
from noobgpu.runner import SubprocessRunner

ROOT = Path(__file__).parents[2] / "challenges"
WRONG = Path(__file__).parent / "data" / "wrong"
PACK_IDS = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith("_"))

runner = SubprocessRunner()


@pytest.mark.gpu
@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_reference_solution_is_accepted(pack_id: str):
    challenge = load_challenge(ROOT / pack_id)
    result = judge_submission(
        challenge, challenge.reference_path.read_text(), ROOT, runner
    )
    assert result.verdict == Verdict.ACCEPTED, result.to_dict()
    assert len(result.tests) == len(challenge.tests)
    assert result.kernel_ms is not None and result.kernel_ms >= 0


@pytest.mark.gpu
@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_wrong_solution_is_rejected(pack_id: str):
    challenge = load_challenge(ROOT / pack_id)
    result = judge_submission(
        challenge, (WRONG / f"{pack_id}.cu").read_text(), ROOT, runner
    )
    assert result.verdict == Verdict.WRONG_ANSWER, result.to_dict()
    assert result.failed_test is not None


@pytest.mark.gpu
def test_starter_code_does_not_pass():
    # Empty solve() must never be Accepted; harness zeroes output buffers so
    # stale memory can't accidentally match.
    challenge = load_challenge(ROOT / "vector-addition")
    result = judge_submission(challenge, challenge.starter_path.read_text(), ROOT, runner)
    assert result.verdict == Verdict.WRONG_ANSWER


@pytest.mark.gpu
def test_compile_error_verdict():
    challenge = load_challenge(ROOT / "vector-addition")
    result = judge_submission(challenge, "this is not cuda\n", ROOT, runner)
    assert result.verdict == Verdict.COMPILE_ERROR
    assert "error" in result.compile_result.stderr


@pytest.mark.gpu
def test_runtime_error_verdict():
    challenge = load_challenge(ROOT / "vector-addition")
    code = (
        "#include <cstdlib>\n"
        'extern "C" void solve(const float* A, const float* B, float* C, int N) '
        "{ abort(); }\n"
    )
    result = judge_submission(challenge, code, ROOT, runner)
    assert result.verdict == Verdict.RUNTIME_ERROR


@pytest.mark.gpu
def test_time_limit_exceeded_verdict():
    challenge = load_challenge(ROOT / "vector-addition")
    code = (
        "#include <cuda_runtime.h>\n"
        "__global__ void spin(volatile float* C) { while (C[0] == 0.0f) {} }\n"
        'extern "C" void solve(const float* A, const float* B, float* C, int N) '
        "{ spin<<<1, 1>>>(C); cudaDeviceSynchronize(); }\n"
    )
    result = judge_submission(challenge, code, ROOT, runner)
    assert result.verdict == Verdict.TIME_LIMIT_EXCEEDED
    assert result.failed_test == challenge.tests[0].name


@pytest.mark.gpu
def test_sample_only_runs_sample_tests():
    challenge = load_challenge(ROOT / "relu")
    result = judge_submission(
        challenge, challenge.reference_path.read_text(), ROOT, runner, sample_only=True
    )
    assert result.verdict == Verdict.ACCEPTED
    assert all(t.sample for t in result.tests)
    assert len(result.tests) == len(challenge.sample_tests())


@pytest.mark.gpu
def test_expected_outputs_are_cached():
    challenge = load_challenge(ROOT / "relu")
    judge_submission(challenge, challenge.reference_path.read_text(), ROOT, runner)
    cached = list(challenge.cache_dir.glob("*.bin"))
    assert len(cached) == len(challenge.tests)


def test_all_packs_have_wrong_solutions():
    assert {p.stem for p in WRONG.glob("*.cu")} == set(PACK_IDS)
