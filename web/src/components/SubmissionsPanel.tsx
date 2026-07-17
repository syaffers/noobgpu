import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import type { SubmissionDetail, SubmissionSummary, Verdict } from '../lib/types'

const VERDICT_BADGE: Record<Verdict, string> = {
  accepted: 'bg-emerald-900/60 text-emerald-300',
  wrong_answer: 'bg-red-900/60 text-red-300',
  compile_error: 'bg-red-900/60 text-red-300',
  runtime_error: 'bg-orange-900/60 text-orange-300',
  time_limit_exceeded: 'bg-amber-900/60 text-amber-300',
}

const label = (v: Verdict) => v.replaceAll('_', ' ')

type Props = {
  challengeId: string
  refreshKey: number
  onRestore: (code: string) => void
}

export default function SubmissionsPanel({ challengeId, refreshKey, onRestore }: Props) {
  const [submissions, setSubmissions] = useState<SubmissionSummary[] | null>(null)
  const [selected, setSelected] = useState<SubmissionDetail | null>(null)

  useEffect(() => {
    setSelected(null)
    api.fetchSubmissions(challengeId).then(setSubmissions)
  }, [challengeId, refreshKey])

  if (submissions === null)
    return <p className="px-6 py-4 text-sm text-neutral-500">loading…</p>

  if (submissions.length === 0)
    return (
      <p className="px-6 py-8 text-center text-sm text-neutral-500">
        No submissions yet — hit Submit to record one.
      </p>
    )

  if (selected)
    return (
      <div className="flex h-full flex-col overflow-y-auto px-6 py-4">
        <div className="mb-3 flex items-center gap-3">
          <button
            onClick={() => setSelected(null)}
            className="rounded border border-neutral-700 px-2 py-0.5 text-xs hover:bg-neutral-800"
          >
            ← Back
          </button>
          <span
            className={`rounded-full px-3 py-0.5 text-xs font-semibold capitalize ${VERDICT_BADGE[selected.verdict]}`}
          >
            {label(selected.verdict)}
          </span>
          <span className="text-xs text-neutral-500">
            #{selected.id} · {selected.created_at}
          </span>
          <button
            onClick={() => onRestore(selected.code)}
            className="ml-auto rounded bg-blue-600 px-3 py-1 text-xs font-semibold hover:bg-blue-500"
          >
            Restore to editor
          </button>
        </div>
        <pre className="min-h-0 flex-1 overflow-auto rounded bg-neutral-900 p-3 font-mono text-xs leading-relaxed">
          {selected.code}
        </pre>
      </div>
    )

  return (
    <ul className="divide-y divide-neutral-800 overflow-y-auto">
      {submissions.map((s) => (
        <li key={s.id}>
          <button
            onClick={() => api.fetchSubmission(s.id).then(setSelected)}
            className="flex w-full items-center gap-3 px-6 py-3 text-left text-sm hover:bg-neutral-900"
          >
            <span
              className={`rounded-full px-3 py-0.5 text-xs font-semibold capitalize ${VERDICT_BADGE[s.verdict]}`}
            >
              {label(s.verdict)}
            </span>
            {s.verdict === 'accepted' && s.kernel_ms !== null && (
              <span className="font-mono text-xs text-neutral-400">
                {s.kernel_ms.toFixed(3)} ms
              </span>
            )}
            {s.failed_test && (
              <span className="font-mono text-xs text-neutral-500">
                failed {s.failed_test}
              </span>
            )}
            <span className="ml-auto text-xs text-neutral-500">{s.created_at}</span>
          </button>
        </li>
      ))}
    </ul>
  )
}
