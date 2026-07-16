import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from noobgpu.challenges import Challenge, ChallengePackError, TestCase, common_include_dir
from noobgpu.errors import CudaToolkitNotFoundError
from noobgpu.runner import Limits, Runner, RunResult

COMPILE_LIMITS = Limits(wall_time_s=90.0, file_size_bytes=256 * 2**20)
GEN_LIMITS = Limits(wall_time_s=60.0, file_size_bytes=256 * 2**20)


class Verdict(StrEnum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"


@dataclass(frozen=True)
class TestOutcome:
    name: str
    sample: bool
    passed: bool
    max_abs_err: float | None
    kernel_ms: float | None
    run: RunResult = field(repr=False)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sample": self.sample,
            "passed": self.passed,
            "max_abs_err": self.max_abs_err,
            "kernel_ms": self.kernel_ms,
        }


@dataclass(frozen=True)
class JudgeResult:
    verdict: Verdict
    compile_result: RunResult
    tests: tuple[TestOutcome, ...] = ()
    failed_test: str | None = None

    @property
    def kernel_ms(self) -> float | None:
        """Worst-case solve() time across passed tests (the largest test dominates)."""
        times = [t.kernel_ms for t in self.tests if t.kernel_ms is not None]
        return max(times) if times else None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "kernel_ms": self.kernel_ms,
            "failed_test": self.failed_test,
            "compile": self.compile_result.to_dict(),
            "tests": [t.to_dict() for t in self.tests],
        }


def find_nvcc() -> str:
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        raise CudaToolkitNotFoundError(
            "nvcc not found on PATH — install the CUDA toolkit or add it to PATH"
        )
    return nvcc


def compile_cuda(
    sources: list[Path], binary: Path, runner: Runner, include_dir: Path | None = None
) -> RunResult:
    """Compile .cu files with nvcc, targeting the GPU present on this machine."""
    cmd = [find_nvcc(), "-O2", "-arch=native"]
    if include_dir is not None:
        cmd += ["-I", str(include_dir)]
    cmd += [str(s) for s in sources] + ["-o", str(binary)]
    return runner.run(cmd, workdir=binary.parent, limits=COMPILE_LIMITS)


def run_binary(binary: Path, runner: Runner, limits: Limits | None = None) -> RunResult:
    return runner.run([str(binary)], workdir=binary.parent, limits=limits or Limits())


def _expected_hash(challenge: Challenge, root: Path, case: TestCase) -> str:
    """Content hash for one case's expected output: any input to the reference
    computation changes it, forcing a lazy rebuild."""
    h = hashlib.sha256()
    for path in (
        common_include_dir(root) / "noobgpu_harness.h",
        challenge.harness_path,
        challenge.reference_path,
    ):
        h.update(path.read_bytes())
    h.update(f"{challenge.tolerance}|{case.args}".encode())
    return h.hexdigest()[:12]


def _expected_path(challenge: Challenge, root: Path, case: TestCase) -> Path:
    return challenge.cache_dir / f"{case.name}-{_expected_hash(challenge, root, case)}.bin"


def ensure_expected_outputs(
    challenge: Challenge, root: Path, runner: Runner
) -> dict[str, Path]:
    """Build (lazily, content-addressed) the expected output for every test case
    by compiling and running the reference solution."""
    paths = {case.name: _expected_path(challenge, root, case) for case in challenge.tests}
    missing = [case for case in challenge.tests if not paths[case.name].is_file()]
    if not missing:
        return paths

    challenge.cache_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="noobgpu-ref-") as tmp:
        binary = Path(tmp) / "reference"
        compiled = compile_cuda(
            [challenge.harness_path, challenge.reference_path],
            binary,
            runner,
            include_dir=common_include_dir(root),
        )
        if not compiled.ok:
            raise ChallengePackError(
                f"challenge pack {challenge.id}: reference solution failed to "
                f"compile:\n{compiled.stderr}"
            )
        for case in missing:
            target = paths[case.name]
            cmd = [str(binary), "gen", str(target), str(challenge.tolerance)]
            cmd += [str(a) for a in case.args]
            result = runner.run(cmd, workdir=Path(tmp), limits=GEN_LIMITS)
            if not result.ok or not target.is_file():
                raise ChallengePackError(
                    f"challenge pack {challenge.id}: reference run failed on "
                    f"test '{case.name}':\n{result.stderr}"
                )
    return paths


def _parse_report(stdout: str) -> dict | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                return None
    return None


def judge_submission(
    challenge: Challenge,
    solution_code: str,
    root: Path,
    runner: Runner,
    sample_only: bool = False,
) -> JudgeResult:
    """Compile solution_code against the challenge harness and run its tests
    in order, stopping at the first failure."""
    expected = ensure_expected_outputs(challenge, root, runner)
    cases = challenge.sample_tests() if sample_only else challenge.tests

    with tempfile.TemporaryDirectory(prefix="noobgpu-judge-") as tmp:
        workdir = Path(tmp)
        solution = workdir / "solution.cu"
        solution.write_text(solution_code)
        binary = workdir / "program"

        compiled = compile_cuda(
            [challenge.harness_path, solution],
            binary,
            runner,
            include_dir=common_include_dir(root),
        )
        if not compiled.ok:
            return JudgeResult(verdict=Verdict.COMPILE_ERROR, compile_result=compiled)

        outcomes: list[TestOutcome] = []
        for case in cases:
            cmd = [str(binary), "check", str(expected[case.name]), str(challenge.tolerance)]
            cmd += [str(a) for a in case.args]
            run = runner.run(cmd, workdir=workdir, limits=challenge.limits)
            report = _parse_report(run.stdout)

            if run.timed_out:
                verdict = Verdict.TIME_LIMIT_EXCEEDED
            elif run.exit_code != 0 or report is None:
                verdict = Verdict.RUNTIME_ERROR
            elif not report["pass"]:
                verdict = Verdict.WRONG_ANSWER
            else:
                verdict = Verdict.ACCEPTED

            outcomes.append(
                TestOutcome(
                    name=case.name,
                    sample=case.sample,
                    passed=verdict == Verdict.ACCEPTED,
                    max_abs_err=report.get("max_abs_err") if report else None,
                    kernel_ms=report.get("kernel_ms") if report else None,
                    run=run,
                )
            )
            if verdict != Verdict.ACCEPTED:
                return JudgeResult(
                    verdict=verdict,
                    compile_result=compiled,
                    tests=tuple(outcomes),
                    failed_test=case.name,
                )

    return JudgeResult(
        verdict=Verdict.ACCEPTED, compile_result=compiled, tests=tuple(outcomes)
    )
