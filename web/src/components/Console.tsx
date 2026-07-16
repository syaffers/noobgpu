import { useEffect, useRef } from 'react'
import type { JudgeEvent, Verdict } from '../lib/types'

const VERDICT_STYLE: Record<Verdict, { label: string; className: string }> = {
  accepted: { label: 'Accepted', className: 'bg-emerald-900/50 text-emerald-300 border-emerald-700' },
  wrong_answer: { label: 'Wrong Answer', className: 'bg-red-900/50 text-red-300 border-red-700' },
  compile_error: { label: 'Compile Error', className: 'bg-red-900/50 text-red-300 border-red-700' },
  runtime_error: { label: 'Runtime Error', className: 'bg-orange-900/50 text-orange-300 border-orange-700' },
  time_limit_exceeded: { label: 'Time Limit Exceeded', className: 'bg-amber-900/50 text-amber-300 border-amber-700' },
}

function Line({ event }: { event: JudgeEvent }) {
  switch (event.type) {
    case 'prepare_start':
      return <p className="text-neutral-500">preparing expected outputs…</p>
    case 'prepare_end':
      return null
    case 'compile_start':
      return <p className="text-neutral-400">compiling with nvcc…</p>
    case 'compile_end':
      return event.ok ? (
        <p className="text-neutral-400">compiled in {event.duration_s.toFixed(2)}s</p>
      ) : (
        <pre className="whitespace-pre-wrap rounded bg-red-950/40 p-2 text-red-300">
          {event.stderr}
        </pre>
      )
    case 'test_start':
      return null
    case 'test_end':
      return event.passed ? (
        <p className="text-emerald-400">
          ✓ {event.name}
          <span className="text-neutral-500"> · {event.kernel_ms?.toFixed(3)} ms</span>
        </p>
      ) : (
        <div>
          <p className="text-red-400">
            ✗ {event.name}
            {event.max_abs_err !== null && (
              <span className="text-neutral-500"> · max abs err {event.max_abs_err}</span>
            )}
          </p>
          {event.stderr && (
            <pre className="whitespace-pre-wrap rounded bg-red-950/40 p-2 text-red-300">
              {event.stderr}
            </pre>
          )}
        </div>
      )
    case 'result': {
      const style = VERDICT_STYLE[event.verdict]
      return (
        <div className={`mt-1 rounded border px-3 py-2 font-semibold ${style.className}`}>
          {style.label}
          {event.verdict === 'accepted' && event.kernel_ms !== null && (
            <span className="font-normal"> · kernel time {event.kernel_ms.toFixed(3)} ms</span>
          )}
          {event.failed_test && (
            <span className="font-normal"> · failed on {event.failed_test}</span>
          )}
        </div>
      )
    }
    case 'error':
      return (
        <p className="text-red-400">
          {event.error_type}: {event.message}
        </p>
      )
  }
}

type Props = { events: JudgeEvent[]; idle: boolean }

export default function Console({ events, idle }: Props) {
  const bottom = useRef<HTMLDivElement>(null)
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  return (
    <div className="flex h-full flex-col border-t border-neutral-800">
      <div className="border-b border-neutral-800 px-4 py-1.5 font-mono text-sm text-neutral-300">
        Console Output
      </div>
      <div className="min-h-0 flex-1 space-y-1 overflow-y-auto px-4 py-2 font-mono text-xs">
        {idle && events.length === 0 && (
          <p className="text-neutral-600">Run your code to see output here.</p>
        )}
        {events.map((event, i) => (
          <Line key={i} event={event} />
        ))}
        <div ref={bottom} />
      </div>
    </div>
  )
}
