import { Link } from 'react-router'
import GpuBadge from '../components/GpuBadge'
import ProblemPanel from '../components/ProblemPanel'
import guide from '../guide.md?raw'
import type { GpuInfo } from '../lib/types'

export default function Guide({ gpu }: { gpu: GpuInfo | null }) {
  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-neutral-100">
      <header className="flex items-center gap-4 border-b border-neutral-800 px-6 py-3">
        <Link to="/" className="text-xl font-bold tracking-tight text-teal-300">
          NoobGPU
        </Link>
        <span className="text-sm text-neutral-400">Guide</span>
        <div className="ml-auto">
          <GpuBadge gpu={gpu} />
        </div>
      </header>
      <main className="mx-auto min-h-0 w-full max-w-3xl flex-1">
        <ProblemPanel description={guide} />
      </main>
    </div>
  )
}
