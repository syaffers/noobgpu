from pathlib import Path

from noobgpu.runner import Limits, SubprocessRunner

runner = SubprocessRunner()


def test_captures_stdout_and_exit_code(tmp_path: Path):
    result = runner.run(["sh", "-c", "echo hello"], tmp_path, Limits())
    assert result.ok
    assert result.stdout == "hello\n"
    assert result.exit_code == 0


def test_nonzero_exit_code(tmp_path: Path):
    result = runner.run(["sh", "-c", "echo oops >&2; exit 3"], tmp_path, Limits())
    assert not result.ok
    assert result.exit_code == 3
    assert result.stderr == "oops\n"


def test_wall_timeout_kills_process(tmp_path: Path):
    result = runner.run(["sh", "-c", "sleep 30"], tmp_path, Limits(wall_time_s=0.5))
    assert result.timed_out
    assert not result.ok
    assert result.duration_s < 5


def test_timeout_kills_whole_process_tree(tmp_path: Path):
    # The child spawns its own child; both must die at the timeout.
    result = runner.run(
        ["sh", "-c", "sleep 30 & wait"], tmp_path, Limits(wall_time_s=0.5)
    )
    assert result.timed_out
    assert result.duration_s < 5


def test_file_size_limit(tmp_path: Path):
    result = runner.run(
        ["sh", "-c", "yes x > big.txt"],
        tmp_path,
        Limits(wall_time_s=10.0, file_size_bytes=1024),
    )
    assert not result.ok
    assert (tmp_path / "big.txt").stat().st_size <= 1024


def test_runs_in_workdir(tmp_path: Path):
    result = runner.run(["pwd"], tmp_path, Limits())
    assert result.stdout.strip() == str(tmp_path)
