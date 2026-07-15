import shutil
from pathlib import Path

from noobgpu.errors import CudaToolkitNotFoundError
from noobgpu.runner import Limits, Runner, RunResult

COMPILE_LIMITS = Limits(wall_time_s=90.0, file_size_bytes=256 * 2**20)


def find_nvcc() -> str:
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        raise CudaToolkitNotFoundError(
            "nvcc not found on PATH — install the CUDA toolkit or add it to PATH"
        )
    return nvcc


def compile_cuda(source: Path, binary: Path, runner: Runner) -> RunResult:
    """Compile one .cu file with nvcc, targeting the GPU present on this machine."""
    cmd = [find_nvcc(), "-O2", "-arch=native", str(source), "-o", str(binary)]
    return runner.run(cmd, workdir=source.parent, limits=COMPILE_LIMITS)


def run_binary(binary: Path, runner: Runner, limits: Limits | None = None) -> RunResult:
    return runner.run([str(binary)], workdir=binary.parent, limits=limits or Limits())
