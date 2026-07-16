import { useCallback, useEffect, useRef, useState } from 'react'
import Console from './components/Console'
import EditorPanel from './components/EditorPanel'
import GpuModal from './components/GpuModal'
import Header from './components/Header'
import ProblemPanel from './components/ProblemPanel'
import * as api from './lib/api'
import type { ChallengeDetail, ChallengeSummary, GpuInfo, JudgeEvent } from './lib/types'

function challengeFromUrl(): string | null {
  return new URLSearchParams(window.location.search).get('challenge')
}

export default function App() {
  const [challenges, setChallenges] = useState<ChallengeSummary[]>([])
  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null)
  const [gpu, setGpu] = useState<GpuInfo | null>(null)
  const [code, setCode] = useState('')
  const [events, setEvents] = useState<JudgeEvent[]>([])
  const [running, setRunning] = useState(false)
  const [showGpu, setShowGpu] = useState(false)
  const draftTimer = useRef<number | undefined>(undefined)

  useEffect(() => {
    api.fetchGpu().then(setGpu)
    api.fetchChallenges().then((list) => {
      setChallenges(list)
      const fromUrl = challengeFromUrl()
      const id = list.some((c) => c.id === fromUrl) ? fromUrl! : list[0]?.id
      if (id) selectChallenge(id)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const selectChallenge = useCallback(async (id: string) => {
    const [detail, draft] = await Promise.all([api.fetchChallenge(id), api.fetchDraft(id)])
    setChallenge(detail)
    setCode(draft ?? detail.starter_code)
    setEvents([])
    const url = new URL(window.location.href)
    url.searchParams.set('challenge', id)
    window.history.replaceState(null, '', url)
  }, [])

  const onCodeChange = useCallback(
    (next: string) => {
      setCode(next)
      if (!challenge) return
      window.clearTimeout(draftTimer.current)
      draftTimer.current = window.setTimeout(() => {
        api.saveDraft(challenge.id, next)
      }, 800)
    },
    [challenge],
  )

  const judge = useCallback(
    async (action: 'run' | 'submit') => {
      if (!challenge || running) return
      window.clearTimeout(draftTimer.current)
      api.saveDraft(challenge.id, code)
      setRunning(true)
      setEvents([])
      try {
        for await (const event of api.streamJudge(challenge.id, action, code)) {
          setEvents((prev) => [...prev, event])
        }
      } catch (err) {
        setEvents((prev) => [
          ...prev,
          { type: 'error', error_type: 'RequestFailed', message: String(err) },
        ])
      } finally {
        setRunning(false)
      }
    },
    [challenge, code, running],
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
    api.saveDraft(challenge.id, challenge.starter_code)
  }, [challenge])

  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-neutral-100">
      <Header
        challenges={challenges}
        selectedId={challenge?.id ?? ''}
        onSelect={selectChallenge}
        gpu={gpu}
        onShowGpu={() => setShowGpu(true)}
        running={running}
        onRun={() => judge('run')}
        onSubmit={() => judge('submit')}
      />

      {challenge ? (
        <main className="grid min-h-0 flex-1 grid-cols-2">
          <section className="min-h-0 border-r border-neutral-800">
            <ProblemPanel
              description={challenge.description}
              difficulty={challenge.difficulty}
            />
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

      {showGpu && gpu && <GpuModal gpu={gpu} onClose={() => setShowGpu(false)} />}
    </div>
  )
}
