import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import Console from '../components/Console'
import EditorPanel from '../components/EditorPanel'
import GpuBadge from '../components/GpuBadge'
import ProblemPanel from '../components/ProblemPanel'
import StatusBanner from '../components/StatusBanner'
import SubmissionsPanel from '../components/SubmissionsPanel'
import * as api from '../lib/api'
import type { ChallengeDetail, GpuInfo, JudgeEvent } from '../lib/types'

type Tab = 'description' | 'submissions'

export default function Workspace({ gpu }: { gpu: GpuInfo | null }) {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null)
  const [code, setCode] = useState('')
  const [events, setEvents] = useState<JudgeEvent[]>([])
  const [running, setRunning] = useState(false)
  const [tab, setTab] = useState<Tab>('description')
  const [submissionsKey, setSubmissionsKey] = useState(0)
  const draftTimer = useRef<number | undefined>(undefined)

  const canRun = gpu?.available === true && gpu.nvcc.available

  useEffect(() => {
    let cancelled = false
    Promise.all([api.fetchChallenge(id), api.fetchDraft(id)])
      .then(([detail, draft]) => {
        if (cancelled) return
        setChallenge(detail)
        setCode(draft ?? detail.starter_code)
        setEvents([])
        setTab('description')
      })
      .catch(() => navigate('/', { replace: true }))
    return () => {
      cancelled = true
    }
  }, [id, navigate])

  const onCodeChange = useCallback(
    (next: string) => {
      setCode(next)
      window.clearTimeout(draftTimer.current)
      draftTimer.current = window.setTimeout(() => api.saveDraft(id, next), 800)
    },
    [id],
  )

  const judge = useCallback(
    async (action: 'run' | 'submit') => {
      if (!challenge || running || !canRun) return
      window.clearTimeout(draftTimer.current)
      api.saveDraft(id, code)
      setRunning(true)
      setEvents([])
      try {
        for await (const event of api.streamJudge(id, action, code)) {
          setEvents((prev) => [...prev, event])
        }
      } catch (err) {
        setEvents((prev) => [
          ...prev,
          { type: 'error', error_type: 'RequestFailed', message: String(err) },
        ])
      } finally {
        setRunning(false)
        if (action === 'submit') setSubmissionsKey((k) => k + 1)
      }
    },
    [challenge, code, id, running, canRun],
  )

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault()
        judge('run')
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [judge])

  const onReset = useCallback(() => {
    if (!challenge) return
    setCode(challenge.starter_code)
    api.saveDraft(id, challenge.starter_code)
  }, [challenge, id])

  const onRestore = useCallback(
    (restored: string) => {
      setCode(restored)
      api.saveDraft(id, restored)
      setTab('description')
    },
    [id],
  )

  const tabClass = (t: Tab) =>
    `rounded-t px-4 py-1.5 text-sm ${
      tab === t
        ? 'bg-neutral-900 font-semibold text-neutral-100'
        : 'text-neutral-400 hover:text-neutral-200'
    }`

  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-neutral-100">
      <header className="flex items-center gap-4 border-b border-neutral-800 px-4 py-2">
        <Link to="/" className="text-xl font-bold tracking-tight text-teal-300">
          NoobGPU
        </Link>
        <span className="text-sm text-neutral-400">{challenge?.title ?? '…'}</span>
        <div className="ml-auto flex items-center gap-4">
          <GpuBadge gpu={gpu} />
          <button
            onClick={() => judge('run')}
            disabled={running || !canRun}
            className="rounded bg-blue-600 px-4 py-1 text-sm font-semibold hover:bg-blue-500 disabled:opacity-40"
            title="Run sample tests (Ctrl+Enter)"
          >
            {running ? 'Running…' : '▶ Run'}
          </button>
          <button
            onClick={() => judge('submit')}
            disabled={running || !canRun}
            className="rounded bg-emerald-600 px-4 py-1 text-sm font-semibold hover:bg-emerald-500 disabled:opacity-40"
            title="Submit against all tests"
          >
            🚀 Submit
          </button>
        </div>
      </header>
      <StatusBanner gpu={gpu} />

      {challenge ? (
        <main className="grid min-h-0 flex-1 grid-cols-2">
          <section className="flex min-h-0 flex-col border-r border-neutral-800">
            <nav className="flex gap-1 border-b border-neutral-800 px-4 pt-2">
              <button className={tabClass('description')} onClick={() => setTab('description')}>
                Description
              </button>
              <button className={tabClass('submissions')} onClick={() => setTab('submissions')}>
                Submissions
              </button>
            </nav>
            <div className="min-h-0 flex-1">
              {tab === 'description' ? (
                <ProblemPanel
                  description={challenge.description}
                  difficulty={challenge.difficulty}
                />
              ) : (
                <SubmissionsPanel
                  challengeId={id}
                  refreshKey={submissionsKey}
                  onRestore={onRestore}
                />
              )}
            </div>
          </section>
          <section className="grid min-h-0 grid-rows-[minmax(0,1.8fr)_minmax(0,1fr)]">
            <EditorPanel code={code} onChange={onCodeChange} onReset={onReset} />
            <Console events={events} idle={!running} />
          </section>
        </main>
      ) : (
        <main className="flex flex-1 items-center justify-center text-neutral-500">
          loading…
        </main>
      )}
    </div>
  )
}
