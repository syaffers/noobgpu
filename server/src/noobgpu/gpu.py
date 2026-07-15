from dataclasses import asdict, dataclass

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
