import { useEffect, useState } from 'react'

type Health = { status: string; version: string }

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setError(true))
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-neutral-950 text-neutral-100">
      <h1 className="text-4xl font-bold tracking-tight text-teal-300">NoobGPU</h1>
      <p className="text-neutral-400">Local-first CUDA challenge playground</p>
      <p className="font-mono text-sm">
        {health && (
          <span className="text-emerald-400">server ok · v{health.version}</span>
        )}
        {error && <span className="text-red-400">server unreachable</span>}
        {!health && !error && <span className="text-neutral-500">connecting…</span>}
      </p>
    </div>
  )
}
