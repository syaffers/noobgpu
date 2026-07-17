import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from noobgpu.errors import NoobGpuError
from noobgpu.runner import Limits


class ChallengePackError(NoobGpuError):
    """A challenge pack is malformed; the message names the pack and the problem."""


DIFFICULTIES = ("easy", "medium", "hard")
PACK_FILES = ("challenge.toml", "description.md", "starter.cu", "reference.cu", "harness.cu")
COMMON_DIR = "_common"


@dataclass(frozen=True)
class TestCase:
    name: str
    args: tuple[int, ...]
    sample: bool = False


@dataclass(frozen=True)
class Challenge:
    id: str
    title: str
    difficulty: str
    tolerance: float
    dir: Path
    tests: tuple[TestCase, ...] = field(repr=False)
    limits: Limits = field(repr=False)

    @property
    def description_path(self) -> Path:
        return self.dir / "description.md"

    @property
    def starter_path(self) -> Path:
        return self.dir / "starter.cu"

    @property
    def reference_path(self) -> Path:
        return self.dir / "reference.cu"

    @property
    def harness_path(self) -> Path:
        return self.dir / "harness.cu"

    @property
    def cache_dir(self) -> Path:
        """Expected-output cache. NOOBGPU_CACHE_DIR redirects it (the packaged
        install sets this so site-packages stays pristine)."""
        if base := os.environ.get("NOOBGPU_CACHE_DIR"):
            return Path(base) / self.id
        return self.dir / ".cache"

    def sample_tests(self) -> tuple[TestCase, ...]:
        return tuple(t for t in self.tests if t.sample)

    def blurb(self) -> str:
        """First prose line of the description, for challenge cards.
        Inline markdown markers are stripped — cards render plain text."""
        for line in self.description_path.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped.replace("`", "").replace("**", "")
        return ""


def _fail(pack: Path, problem: str) -> ChallengePackError:
    return ChallengePackError(f"challenge pack {pack.name}: {problem}")


def load_challenge(pack_dir: Path) -> Challenge:
    for name in PACK_FILES:
        if not (pack_dir / name).is_file():
            raise _fail(pack_dir, f"missing required file {name}")

    try:
        with open(pack_dir / "challenge.toml", "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise _fail(pack_dir, f"challenge.toml is not valid TOML: {exc}") from exc

    for key in ("id", "title", "difficulty", "tolerance", "tests"):
        if key not in data:
            raise _fail(pack_dir, f"challenge.toml is missing required key '{key}'")
    if data["id"] != pack_dir.name:
        raise _fail(pack_dir, f"id '{data['id']}' does not match directory name")
    if data["difficulty"] not in DIFFICULTIES:
        raise _fail(pack_dir, f"difficulty must be one of {DIFFICULTIES}")
    tolerance = data["tolerance"]
    if not isinstance(tolerance, int | float) or tolerance < 0:
        raise _fail(pack_dir, "tolerance must be a non-negative number")

    tests = []
    for i, raw in enumerate(data["tests"]):
        if "name" not in raw or "args" not in raw:
            raise _fail(pack_dir, f"tests[{i}] needs 'name' and 'args'")
        if not all(isinstance(a, int) for a in raw["args"]):
            raise _fail(pack_dir, f"tests[{i}] args must all be integers")
        tests.append(
            TestCase(name=raw["name"], args=tuple(raw["args"]), sample=raw.get("sample", False))
        )
    names = [t.name for t in tests]
    if len(set(names)) != len(names):
        raise _fail(pack_dir, "test names must be unique")
    if not any(t.sample for t in tests):
        raise _fail(pack_dir, "at least one test must be marked sample = true")
    if all(t.sample for t in tests):
        raise _fail(pack_dir, "at least one test must be hidden (sample = false)")

    limits_raw = data.get("limits", {})
    unknown = set(limits_raw) - {"wall_time_s", "cpu_time_s"}
    if unknown:
        raise _fail(pack_dir, f"unknown limits keys: {sorted(unknown)}")
    limits = Limits(
        wall_time_s=float(limits_raw.get("wall_time_s", Limits.wall_time_s)),
        cpu_time_s=limits_raw.get("cpu_time_s"),
    )

    return Challenge(
        id=data["id"],
        title=data["title"],
        difficulty=data["difficulty"],
        tolerance=float(tolerance),
        dir=pack_dir,
        tests=tuple(tests),
        limits=limits,
    )


def load_challenges(root: Path) -> list[Challenge]:
    """Load every pack under root, sorted by id. Skips _common and dot-dirs."""
    if not root.is_dir():
        raise ChallengePackError(f"challenges directory not found: {root}")
    packs = [
        p
        for p in sorted(root.iterdir())
        if p.is_dir() and not p.name.startswith((".", "_"))
    ]
    return [load_challenge(p) for p in packs]


def common_include_dir(root: Path) -> Path:
    return root / COMMON_DIR


PACKAGED_CHALLENGES = Path(__file__).parent / "data" / "challenges"


def find_challenges_root() -> Path:
    """NOOBGPU_CHALLENGES_DIR, else the nearest 'challenges' directory upward
    from cwd, else the copy shipped inside the installed package."""
    if env := os.environ.get("NOOBGPU_CHALLENGES_DIR"):
        return Path(env)
    for base in (Path.cwd(), *Path.cwd().parents):
        candidate = base / "challenges"
        if candidate.is_dir():
            return candidate
    if PACKAGED_CHALLENGES.is_dir():
        return PACKAGED_CHALLENGES
    raise NoobGpuError(
        "no challenges directory found — set NOOBGPU_CHALLENGES_DIR or run from the repo"
    )
