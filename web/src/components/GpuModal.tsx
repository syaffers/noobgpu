import type { GpuInfo } from '../lib/types'

export default function GpuModal({ gpu, onClose }: { gpu: GpuInfo; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className="w-96 rounded-lg border border-neutral-700 bg-neutral-900 p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between">
          <h2 className="font-mono text-lg font-bold">
            {gpu.available ? gpu.name : 'No GPU detected'}
          </h2>
          <button onClick={onClose} className="text-neutral-400 hover:text-white">
            ✕
          </button>
        </div>

        {gpu.available ? (
          <dl className="space-y-3 text-sm">
            {[
              ['Driver version', gpu.driver_version],
              ['Memory', `${gpu.memory_total_mib.toLocaleString()} MiB`],
              ['Compute capability', gpu.compute_capability],
            ].map(([label, value]) => (
              <div key={label} className="border-b border-neutral-800 pb-2">
                <dt className="text-neutral-400">{label}</dt>
                <dd className="font-mono">{value}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="text-sm text-neutral-400">{gpu.error}</p>
        )}
      </div>
    </div>
  )
}
