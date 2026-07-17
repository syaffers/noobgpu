import pytest

from noobgpu.gpu import arch_name, gpu_spec_sheet, tensor_cores_per_sm


def test_arch_names():
    assert arch_name(7, 5) == "Turing"
    assert arch_name(7, 0) == "Volta"
    assert arch_name(8, 6) == "Ampere"
    assert arch_name(8, 9) == "Ada Lovelace"
    assert arch_name(9, 0) == "Hopper"
    assert arch_name(12, 0) == "Blackwell"
    assert arch_name(4, 2) == "CC 4.2"  # unknown majors degrade gracefully


def test_tensor_cores_per_sm():
    assert tensor_cores_per_sm(6, 1) == 0  # Pascal predates tensor cores
    assert tensor_cores_per_sm(7, 5) == 8  # Turing (T4: 40 SMs x 8 = 320)
    assert tensor_cores_per_sm(8, 6) == 4
    assert tensor_cores_per_sm(12, 0) == 4


@pytest.mark.gpu
def test_spec_sheet_discovers_real_hardware():
    sections = gpu_spec_sheet()
    titles = [s["title"] for s in sections]
    assert "Core Specifications" in titles
    assert "Thread & Block Limits" in titles

    rows = {label: value for s in sections for label, value in s["rows"]}
    assert rows["Warp Size"] == "32"
    assert int(rows["SM Count"]) > 0
    assert "MHz" in rows["Boost Clock"]
    assert rows["Compute Capability"].count(".") == 1
    # Memoized: second call returns the identical object without re-probing.
    assert gpu_spec_sheet() is sections
