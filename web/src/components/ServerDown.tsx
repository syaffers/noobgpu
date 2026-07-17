export default function ServerDown({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-4 bg-neutral-950 text-neutral-100">
      <h1 className="text-2xl font-bold text-red-400">Server unreachable</h1>
      <p className="max-w-md text-center text-sm text-neutral-400">
        The NoobGPU backend isn&apos;t responding. Start it with{' '}
        <code className="rounded bg-neutral-800 px-1 font-mono">make dev</code> (or{' '}
        <code className="rounded bg-neutral-800 px-1 font-mono">noobgpu</code> once installed)
        and try again.
      </p>
      <button
        onClick={onRetry}
        className="rounded bg-blue-600 px-4 py-1.5 text-sm font-semibold hover:bg-blue-500"
      >
        Retry
      </button>
    </div>
  )
}
