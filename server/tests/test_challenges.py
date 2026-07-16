from pathlib import Path

import pytest

from noobgpu.challenges import ChallengePackError, load_challenge, load_challenges

REPO_CHALLENGES = Path(__file__).parents[2] / "challenges"

VALID_TOML = """\
id = "{id}"
title = "Demo"
difficulty = "easy"
tolerance = 1e-5

[[tests]]
name = "sample"
sample = true
args = [4, 1]

[[tests]]
name = "hidden"
args = [64, 2]
"""


def make_pack(root: Path, pack_id: str = "demo", toml: str | None = None) -> Path:
    pack = root / pack_id
    pack.mkdir()
    (pack / "challenge.toml").write_text(toml or VALID_TOML.format(id=pack_id))
    for name in ("description.md", "starter.cu", "reference.cu", "harness.cu"):
        (pack / name).write_text(f"// {name}\n")
    return pack


def test_valid_pack_loads(tmp_path: Path):
    challenge = load_challenge(make_pack(tmp_path))
    assert challenge.id == "demo"
    assert challenge.tolerance == 1e-5
    assert len(challenge.tests) == 2
    assert challenge.sample_tests()[0].name == "sample"
    assert challenge.limits.wall_time_s == 10.0  # default


def test_missing_file_is_reported(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack / "reference.cu").unlink()
    with pytest.raises(ChallengePackError, match="missing required file reference.cu"):
        load_challenge(pack)


def test_id_must_match_directory(tmp_path: Path):
    pack = make_pack(tmp_path, toml=VALID_TOML.format(id="not-demo"))
    with pytest.raises(ChallengePackError, match="does not match directory"):
        load_challenge(pack)


def test_bad_difficulty(tmp_path: Path):
    toml = VALID_TOML.format(id="demo").replace('"easy"', '"extreme"')
    with pytest.raises(ChallengePackError, match="difficulty"):
        load_challenge(make_pack(tmp_path, toml=toml))


def test_needs_sample_and_hidden_tests(tmp_path: Path):
    toml = VALID_TOML.format(id="demo").replace("sample = true", "sample = false")
    with pytest.raises(ChallengePackError, match="sample"):
        load_challenge(make_pack(tmp_path, toml=toml))


def test_duplicate_test_names(tmp_path: Path):
    toml = VALID_TOML.format(id="demo").replace('name = "hidden"', 'name = "sample"')
    with pytest.raises(ChallengePackError, match="unique"):
        load_challenge(make_pack(tmp_path, toml=toml))


def test_limits_override(tmp_path: Path):
    pack = tmp_path / "demo"
    pack.mkdir()
    (pack / "challenge.toml").write_text(
        'id = "demo"\ntitle = "Demo"\ndifficulty = "easy"\ntolerance = 0.0\n'
        "[limits]\nwall_time_s = 3.5\n"
        '[[tests]]\nname = "s"\nsample = true\nargs = [1]\n'
        '[[tests]]\nname = "h"\nargs = [2]\n'
    )
    for name in ("description.md", "starter.cu", "reference.cu", "harness.cu"):
        (pack / name).write_text("//\n")
    assert load_challenge(pack).limits.wall_time_s == 3.5


def test_load_challenges_skips_common(tmp_path: Path):
    make_pack(tmp_path, "aaa")
    (tmp_path / "_common").mkdir()
    (tmp_path / ".hidden").mkdir()
    challenges = load_challenges(tmp_path)
    assert [c.id for c in challenges] == ["aaa"]


def test_repo_packs_all_load():
    challenges = load_challenges(REPO_CHALLENGES)
    ids = [c.id for c in challenges]
    assert ids == sorted(ids)
    assert set(ids) == {
        "matrix-multiplication",
        "matrix-transpose",
        "relu",
        "reverse-array",
        "vector-addition",
    }
