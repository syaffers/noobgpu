import json
from pathlib import Path

import pytest

from noobgpu.errors import GpuNotAvailableError
from noobgpu.gpu import detect_gpu

REPO_CHALLENGES = Path(__file__).parents[2] / "challenges"


def sse_events(text: str) -> list[dict]:
    return [json.loads(line[len("data: "):]) for line in text.splitlines()
            if line.startswith("data: ")]


def _gpu_available() -> bool:
    try:
        detect_gpu()
    except GpuNotAvailableError:
        return False
    return True


def pytest_collection_modifyitems(config, items):
    if _gpu_available():
        return
    skip = pytest.mark.skip(reason="no NVIDIA GPU available")
    for item in items:
        if "gpu" in item.keywords:
            item.add_marker(skip)
