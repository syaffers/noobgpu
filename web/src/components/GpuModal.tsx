import type { GpuInfo } from '../lib/types'

export default function GpuModal({ gpu, onClose }: { gpu: GpuInfo; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6"
      onClick={onClose}
    >
      <div
        className="flex max-h-full w-full max-w-5xl flex-col rounded-lg border border-neutral-700 bg-neutral-900 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-neutral-800 p-5">
          <h2 className="font-mono text-lg font-bold uppercase">
            {gpu.available ? gpu.name : 'No GPU detected'}
          </h2>
          <button onClick={onClose} className="text-neutral-400 hover:text-white">
            ✕
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-5">
          {gpu.available ? (
            <div className="columns-1 gap-6 sm:columns-2 xl:columns-3">
              {gpu.specs.map((section) => (
                <section key={section.title} className="mb-6 break-inside-avoid">
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
                    {section.title}
                  </h3>
                  <dl className="text-sm">
                    {section.rows.map(([label, value]) => (
                      <div
                        key={label}
                        className="flex items-baseline justify-between gap-4 border-b border-neutral-800/70 py-1.5"
                      >
                        <dt className="text-neutral-400">{label}</dt>
                        <dd className="text-right font-mono">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </section>
              ))}
            </div>
          ) : (
            <p className="text-sm text-neutral-400">{gpu.error}</p>
          )}
        </div>
      </div>
    </div>
  )
}
