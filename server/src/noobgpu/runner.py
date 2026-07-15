import contextlib
import os
import resource
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Limits:
    wall_time_s: float = 10.0
    cpu_time_s: int | None = None
    file_size_bytes: int | None = 16 * 2**20
    # RLIMIT_AS is deliberately absent: the CUDA runtime reserves enormous
    # virtual address ranges at context creation, so capping address space
    # breaks every GPU binary. Wall/CPU time are the effective guards.


@dataclass(frozen=True)
class RunResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_s": round(self.duration_s, 4),
            "timed_out": self.timed_out,
        }


class Runner(Protocol):
    def run(
        self,
        cmd: list[str],
        workdir: Path,
        limits: Limits,
        env: dict[str, str] | None = None,
    ) -> RunResult: ...


class SubprocessRunner:
    """Runs commands as child processes with rlimit caps and a wall-clock timeout.

    Isolation scope: protects against accidents (runaway CPU, giant output
    files, hangs), not against malicious code — the child runs as the current
    user. See ROADMAP.md for the DockerRunner plan covering untrusted code.
    """

    def run(
        self,
        cmd: list[str],
        workdir: Path,
        limits: Limits,
        env: dict[str, str] | None = None,
    ) -> RunResult:
        def apply_rlimits() -> None:
            if limits.cpu_time_s is not None:
                resource.setrlimit(
                    resource.RLIMIT_CPU, (limits.cpu_time_s, limits.cpu_time_s + 1)
                )
            if limits.file_size_bytes is not None:
                resource.setrlimit(
                    resource.RLIMIT_FSIZE, (limits.file_size_bytes, limits.file_size_bytes)
                )

        start = time.monotonic()
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            preexec_fn=apply_rlimits,
            start_new_session=True,  # own process group, so we can kill the whole tree
        )
        try:
            stdout, stderr = proc.communicate(timeout=limits.wall_time_s)
            timed_out = False
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            timed_out = True
        return RunResult(
            exit_code=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_s=time.monotonic() - start,
            timed_out=timed_out,
        )
