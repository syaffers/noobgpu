"""Judge CLI.

    python -m noobgpu.judge run <file.cu> [--timeout S]
        Compile and run a freeform .cu file (has its own main()).

    python -m noobgpu.judge submit <challenge-id> <file.cu> [--sample-only]
        Judge a solution against a challenge pack's tests.

Prints a structured JSON result to stdout. Exit codes: 0 success/accepted,
1 the program failed or was not accepted, 2 environment or pack error.
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from noobgpu.challenges import find_challenges_root, load_challenge
from noobgpu.errors import NoobGpuError
from noobgpu.gpu import detect_gpu
from noobgpu.judge import Verdict, compile_cuda, judge_submission, run_binary
from noobgpu.runner import Limits, SubprocessRunner


def cmd_run(args: argparse.Namespace) -> int:
    gpu = detect_gpu()
    runner = SubprocessRunner()
    result: dict = {"gpu": gpu.to_dict()}

    with tempfile.TemporaryDirectory(prefix="noobgpu-") as tmp:
        workdir = Path(tmp)
        source = workdir / args.source.name
        shutil.copy(args.source, source)

        compile_result = compile_cuda([source], workdir / "program", runner)
        result["compile"] = compile_result.to_dict()
        if not compile_result.ok:
            print(json.dumps(result, indent=2))
            return 1

        run_result = run_binary(workdir / "program", runner, Limits(wall_time_s=args.timeout))
        result["run"] = run_result.to_dict()
        print(json.dumps(result, indent=2))
        return 0 if run_result.ok else 1


def cmd_submit(args: argparse.Namespace) -> int:
    gpu = detect_gpu()
    root = args.challenges_dir or find_challenges_root()
    challenge = load_challenge(root / args.challenge_id)
    judged = judge_submission(
        challenge,
        args.source.read_text(),
        root,
        SubprocessRunner(),
        sample_only=args.sample_only,
    )
    print(json.dumps({"gpu": gpu.to_dict(), **judged.to_dict()}, indent=2))
    return 0 if judged.verdict == Verdict.ACCEPTED else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m noobgpu.judge")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="compile and run a freeform .cu file")
    p_run.add_argument("source", type=Path)
    p_run.add_argument("--timeout", type=float, default=10.0)
    p_run.set_defaults(func=cmd_run)

    p_submit = sub.add_parser("submit", help="judge a solution against a challenge")
    p_submit.add_argument("challenge_id")
    p_submit.add_argument("source", type=Path)
    p_submit.add_argument("--sample-only", action="store_true")
    p_submit.add_argument("--challenges-dir", type=Path, default=None)
    p_submit.set_defaults(func=cmd_submit)

    args = parser.parse_args()
    try:
        return args.func(args)
    except NoobGpuError as exc:
        print(json.dumps({"error": {"type": type(exc).__name__, "message": str(exc)}}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
