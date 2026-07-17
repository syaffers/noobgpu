import type { GpuInfo } from '../lib/types'

/** Full-width guidance banner when code can't run. Null when all is well. */
export default function StatusBanner({ gpu }: { gpu: GpuInfo | null }) {
  if (gpu === null || (gpu.available && gpu.nvcc.available)) return null

  const [title, guidance, detail] = !gpu.available
    ? [
        'No NVIDIA GPU detected',
        'NoobGPU runs your code on a local NVIDIA GPU. Install the NVIDIA driver, then restart the server.',
        gpu.error,
      ]
    : [
        'CUDA toolkit not found',
        'nvcc is not on the server’s PATH. Install the CUDA toolkit (or add /usr/local/cuda/bin to PATH), then restart the server.',
        null,
      ]

  return (
    <div className="border-b border-red-900 bg-red-950/60 px-4 py-2 text-sm">
      <span className="font-semibold text-red-300">{title}</span>
      <span className="ml-2 text-red-200/80">{guidance}</span>
      {detail && <span className="ml-2 font-mono text-xs text-red-400/70">({detail})</span>}
    </div>
  )
}
