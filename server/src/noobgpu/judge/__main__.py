"""Throwaway M1 CLI: compile and run a single .cu file on the local GPU.

Usage: python -m noobgpu.judge path/to/solution.cu [--timeout SECONDS]
Prints a structured JSON result to stdout. Exit codes: 0 success, 1 the
program failed (compile or runtime), 2 environment error (no GPU / no nvcc).
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from noobgpu.errors import NoobGpuError
from noobgpu.gpu import detect_gpu
from noobgpu.judge import compile_cuda, run_binary
from noobgpu.runner import Limits, SubprocessRunner


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m noobgpu.judge")
    parser.add_argument("source", type=Path, help="CUDA source file (.cu)")
    parser.add_argument("--timeout", type=float, default=10.0, help="run wall-time limit (s)")
    args = parser.parse_args()

    try:
        gpu = detect_gpu()
        runner = SubprocessRunner()
        result: dict = {"gpu": gpu.to_dict()}

        with tempfile.TemporaryDirectory(prefix="noobgpu-") as tmp:
            workdir = Path(tmp)
            source = workdir / args.source.name
            shutil.copy(args.source, source)

            compile_result = compile_cuda(source, workdir / "program", runner)
            result["compile"] = compile_result.to_dict()
            if not compile_result.ok:
                print(json.dumps(result, indent=2))
                return 1

            run_result = run_binary(
                workdir / "program", runner, Limits(wall_time_s=args.timeout)
            )
            result["run"] = run_result.to_dict()
            print(json.dumps(result, indent=2))
            return 0 if run_result.ok else 1
    except NoobGpuError as exc:
        print(json.dumps({"error": {"type": type(exc).__name__, "message": str(exc)}}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
