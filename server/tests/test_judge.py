import json
import subprocess
import sys
from pathlib import Path

import pytest

from noobgpu.errors import CudaToolkitNotFoundError
from noobgpu.judge import compile_cuda, find_nvcc, run_binary
from noobgpu.runner import Limits, SubprocessRunner

DATA = Path(__file__).parent / "data"


def test_missing_nvcc_is_typed_error(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("PATH", str(tmp_path))  # empty dir: no nvcc anywhere
    with pytest.raises(CudaToolkitNotFoundError):
        find_nvcc()


@pytest.mark.gpu
def test_vector_add_compiles_and_passes(tmp_path: Path):
    runner = SubprocessRunner()
    binary = tmp_path / "program"
    compile_result = compile_cuda(DATA / "vector_add.cu", binary, runner)
    assert compile_result.ok, compile_result.stderr
    run_result = run_binary(binary, runner)
    assert run_result.ok, run_result.stderr
    assert run_result.stdout == "PASS\n"


@pytest.mark.gpu
def test_compile_error_is_captured(tmp_path: Path):
    bad = tmp_path / "bad.cu"
    bad.write_text("int main() { this is not cuda }\n")
    result = compile_cuda(bad, tmp_path / "program", SubprocessRunner())
    assert not result.ok
    assert "error" in result.stderr


@pytest.mark.gpu
def test_infinite_loop_killed_at_timeout(tmp_path: Path):
    runner = SubprocessRunner()
    binary = tmp_path / "program"
    assert compile_cuda(DATA / "infinite_loop.cu", binary, runner).ok
    result = run_binary(binary, runner, Limits(wall_time_s=2.0))
    assert result.timed_out
    assert result.duration_s < 10


@pytest.mark.gpu
def test_cli_end_to_end():
    proc = subprocess.run(
        [sys.executable, "-m", "noobgpu.judge", str(DATA / "vector_add.cu")],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result["gpu"]["name"]
    assert result["compile"]["exit_code"] == 0
    assert result["run"]["stdout"] == "PASS\n"
