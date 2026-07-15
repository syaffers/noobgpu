class NoobGpuError(Exception):
    """Base class for all NoobGPU errors."""


class GpuNotAvailableError(NoobGpuError):
    """No NVIDIA GPU (or driver) is available on this machine."""


class CudaToolkitNotFoundError(NoobGpuError):
    """nvcc is not on PATH; the CUDA toolkit is missing or not configured."""
