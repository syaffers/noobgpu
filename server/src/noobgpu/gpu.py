import contextlib
import ctypes
from dataclasses import asdict, dataclass
from functools import lru_cache

import pynvml

from noobgpu.errors import GpuNotAvailableError


@dataclass(frozen=True)
class GpuInfo:
    name: str
    driver_version: str
    memory_total_mib: int
    compute_capability: str

    def to_dict(self) -> dict:
        return asdict(self)


def _text(value: str | bytes) -> str:
    return value.decode() if isinstance(value, bytes) else value


def detect_gpu(index: int = 0) -> GpuInfo:
    """Return info for one GPU, or raise GpuNotAvailableError."""
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError as exc:
        raise GpuNotAvailableError(
            "NVIDIA driver not available (NVML initialization failed)"
        ) from exc
    try:
        if pynvml.nvmlDeviceGetCount() == 0:
            raise GpuNotAvailableError("NVIDIA driver loaded but no GPU devices found")
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)
        major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
        return GpuInfo(
            name=_text(pynvml.nvmlDeviceGetName(handle)),
            driver_version=_text(pynvml.nvmlSystemGetDriverVersion()),
            memory_total_mib=pynvml.nvmlDeviceGetMemoryInfo(handle).total // (1024 * 1024),
            compute_capability=f"{major}.{minor}",
        )
    except pynvml.NVMLError as exc:
        raise GpuNotAvailableError(f"Failed to query GPU {index}: {exc}") from exc
    finally:
        pynvml.nvmlShutdown()


# ---------------------------------------------------------------------------
# Full spec sheet. Everything below is discovered from the hardware itself:
# no GPU database — NVML and the CUDA driver API answer in microseconds, so
# the only caching needed is a per-process memo.
# ---------------------------------------------------------------------------

# CU_DEVICE_ATTRIBUTE_* ids from cuda.h (stable ABI constants).
_CU_ATTR = {
    "max_threads_per_block": 1,
    "shared_per_block_bytes": 8,
    "warp_size": 10,
    "regs_per_block": 12,
    "clock_khz": 13,
    "sm_count": 16,
    "mem_clock_khz": 36,
    "bus_width_bits": 37,
    "l2_bytes": 38,
    "max_threads_per_sm": 39,
    "cc_major": 75,
    "cc_minor": 76,
    "shared_per_sm_bytes": 81,
    "regs_per_sm": 82,
    "shared_per_block_optin_bytes": 97,
    "max_blocks_per_sm": 106,
}


def arch_name(major: int, minor: int) -> str:
    if major == 7:
        return "Turing" if minor >= 5 else "Volta"
    if major == 8:
        return "Ada Lovelace" if minor >= 9 else "Ampere"
    names = {3: "Kepler", 5: "Maxwell", 6: "Pascal", 9: "Hopper", 10: "Blackwell", 12: "Blackwell"}
    return names.get(major, f"CC {major}.{minor}")


def tensor_cores_per_sm(major: int, minor: int) -> int:
    """Architectural constant: 8/SM on Volta+Turing, 4/SM since Ampere."""
    if major < 7:
        return 0
    return 8 if major == 7 else 4


def _cuda_attributes(index: int = 0) -> dict[str, int]:
    """Query CU_DEVICE_ATTRIBUTE_* straight from libcuda (ships with the
    driver); returns whatever attributes answered successfully."""
    try:
        libcuda = ctypes.CDLL("libcuda.so.1")
    except OSError:
        return {}
    if libcuda.cuInit(0) != 0:
        return {}
    device = ctypes.c_int()
    if libcuda.cuDeviceGet(ctypes.byref(device), index) != 0:
        return {}
    attrs: dict[str, int] = {}
    for name, attr_id in _CU_ATTR.items():
        value = ctypes.c_int()
        if libcuda.cuDeviceGetAttribute(ctypes.byref(value), attr_id, device) == 0:
            attrs[name] = value.value
    return attrs


def _nvml_extras(index: int = 0) -> dict[str, int]:
    """Best-effort NVML facts beyond detect_gpu; absent keys mean the driver
    or binding doesn't expose them."""
    extras: dict[str, int] = {}
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError:
        return extras
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)
        for key, call, args in (
            ("cuda_cores", "nvmlDeviceGetNumGpuCores", ()),
            ("boost_clock_mhz", "nvmlDeviceGetMaxClockInfo", (pynvml.NVML_CLOCK_SM,)),
            ("pcie_gen", "nvmlDeviceGetMaxPcieLinkGeneration", ()),
            ("tdp_mw", "nvmlDeviceGetPowerManagementDefaultLimit", ()),
        ):
            with contextlib.suppress(pynvml.NVMLError, AttributeError):
                extras[key] = getattr(pynvml, call)(handle, *args)
    except pynvml.NVMLError:
        pass
    finally:
        pynvml.nvmlShutdown()
    return extras


def _row(rows: list, label: str, value: str | None) -> None:
    if value is not None:
        rows.append([label, value])


@lru_cache(maxsize=1)
def gpu_spec_sheet(index: int = 0) -> list[dict]:
    """Display-ready spec sections for the modal. Memoized per process —
    discovery is milliseconds, but there's no reason to repeat it per request.
    Raises GpuNotAvailableError when no GPU is present (not cached)."""
    info = detect_gpu(index)
    cu = _cuda_attributes(index)
    nv = _nvml_extras(index)
    major, minor = cu.get("cc_major"), cu.get("cc_minor")

    core: list = []
    if major is not None:
        _row(core, "Architecture", arch_name(major, minor or 0))
    _row(core, "CUDA Cores", f"{nv['cuda_cores']:,}" if "cuda_cores" in nv else None)
    _row(core, "SM Count", str(cu["sm_count"]) if "sm_count" in cu else None)
    if major is not None and "sm_count" in cu and tensor_cores_per_sm(major, minor or 0):
        _row(core, "Tensor Cores", f"{tensor_cores_per_sm(major, minor or 0) * cu['sm_count']}")
    _row(core, "Compute Capability", info.compute_capability)
    _row(core, "Boost Clock", f"{nv['boost_clock_mhz']:,} MHz" if "boost_clock_mhz" in nv else None)
    if "cuda_cores" in nv and "boost_clock_mhz" in nv:
        tflops = 2 * nv["cuda_cores"] * nv["boost_clock_mhz"] / 1e6
        _row(core, "FP32 Performance", f"{tflops:.1f} TFLOPS (peak, computed)")

    def cu_row(rows: list, label: str, key: str, template: str = "{:,}", div: int = 1) -> None:
        if key in cu:
            rows.append([label, template.format(cu[key] // div)])

    memory: list = []
    _row(memory, "Memory", f"{info.memory_total_mib / 1024:.1f} GB")
    cu_row(memory, "Memory Bus Width", "bus_width_bits", "{}-bit")
    cu_row(memory, "Memory Clock", "mem_clock_khz", "{:,} MHz", div=1000)
    if cu.get("mem_clock_khz") and cu.get("bus_width_bits"):
        gbs = cu["mem_clock_khz"] * 1000 * (cu["bus_width_bits"] / 8) * 2 / 1e9
        _row(memory, "Peak Memory Bandwidth", f"{gbs:.0f} GB/s (computed)")
    cu_row(memory, "L2 Cache Size", "l2_bytes", "{} MB", div=1024 * 1024)
    cu_row(memory, "Shared Memory per SM", "shared_per_sm_bytes", "{} KB", div=1024)
    cu_row(memory, "Max Shared Memory per Block", "shared_per_block_optin_bytes", "{} KB", div=1024)
    cu_row(memory, "Registers per SM", "regs_per_sm")
    cu_row(memory, "Registers per Block", "regs_per_block")

    limits: list = []
    cu_row(limits, "Warp Size", "warp_size", "{}")
    cu_row(limits, "Max Threads per Block", "max_threads_per_block")
    cu_row(limits, "Max Threads per SM", "max_threads_per_sm")
    cu_row(limits, "Max Blocks per SM", "max_blocks_per_sm", "{}")

    other: list = []
    _row(other, "Interconnect", f"PCIe Gen{nv['pcie_gen']}" if "pcie_gen" in nv else None)
    _row(other, "TDP", f"{nv['tdp_mw'] // 1000} W" if "tdp_mw" in nv else None)
    _row(other, "Driver Version", info.driver_version)

    sections = [
        {"title": "Core Specifications", "rows": core},
        {"title": "Memory & Cache", "rows": memory},
        {"title": "Thread & Block Limits", "rows": limits},
        {"title": "Other", "rows": other},
    ]
    return [s for s in sections if s["rows"]]
