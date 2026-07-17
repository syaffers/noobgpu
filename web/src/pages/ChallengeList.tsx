import { useMemo, useState } from 'react'
import { Link } from 'react-router'
import GpuBadge from '../components/GpuBadge'
import StatusBanner from '../components/StatusBanner'
import type { ChallengeSummary, GpuInfo } from '../lib/types'

const DIFFICULTY_STYLE = {
  easy: 'bg-emerald-900/60 text-emerald-300',
  medium: 'bg-amber-900/60 text-amber-300',
  hard: 'bg-red-900/60 text-red-300',
} as const

const FILTERS = ['all', 'easy', 'medium', 'hard'] as const

type Props = { challenges: ChallengeSummary[]; gpu: GpuInfo | null }

export default function ChallengeList({ challenges, gpu }: Props) {
  const [query, setQuery] = useState('')
  const [difficulty, setDifficulty] = useState<(typeof FILTERS)[number]>('all')

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    return challenges.filter(
      (c) =>
        (difficulty === 'all' || c.difficulty === difficulty) &&
        (q === '' || c.title.toLowerCase().includes(q) || c.blurb.toLowerCase().includes(q)),
    )
  }, [challenges, query, difficulty])

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="flex items-center gap-4 border-b border-neutral-800 px-6 py-3">
        <h1 className="text-xl font-bold tracking-tight text-teal-300">NoobGPU</h1>
        <div className="ml-auto">
          <GpuBadge gpu={gpu} />
        </div>
      </header>
      <StatusBanner gpu={gpu} />

      <main className="mx-auto max-w-5xl px-6 py-8">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <h2 className="mr-auto text-2xl font-bold">Challenges</h2>
          <input
            type="search"
            placeholder="Search challenges…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-64 rounded border border-neutral-700 bg-neutral-900 px-3 py-1.5 text-sm placeholder:text-neutral-500"
          />
          <div className="flex gap-1">
            {FILTERS.map((f) => (
              <button
                key={f}
                onClick={() => setDifficulty(f)}
                className={`rounded-full px-3 py-1 text-sm capitalize ${
                  difficulty === f
                    ? 'bg-neutral-200 font-semibold text-neutral-900'
                    : 'border border-neutral-700 text-neutral-300 hover:bg-neutral-800'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {visible.length === 0 ? (
          <p className="py-16 text-center text-neutral-500">No challenges match.</p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {visible.map((c) => (
              <Link
                key={c.id}
                to={`/challenges/${c.id}`}
                className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-5 transition hover:border-neutral-600 hover:bg-neutral-900"
              >
                <span
                  className={`mb-3 inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${DIFFICULTY_STYLE[c.difficulty]}`}
                >
                  {c.difficulty}
                </span>
                <h3 className="mb-2 text-lg font-semibold">{c.title}</h3>
                <p className="line-clamp-3 text-sm text-neutral-400">{c.blurb}</p>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
