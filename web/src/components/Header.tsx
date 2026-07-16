import type { ChallengeSummary, GpuInfo } from '../lib/types'

type Props = {
  challenges: ChallengeSummary[]
  selectedId: string
  onSelect: (id: string) => void
  gpu: GpuInfo | null
  onShowGpu: () => void
  running: boolean
  onRun: () => void
  onSubmit: () => void
}

export default function Header(props: Props) {
  const gpuOk = props.gpu?.available === true
  return (
    <header className="flex items-center gap-4 border-b border-neutral-800 px-4 py-2">
      <h1 className="text-xl font-bold tracking-tight text-teal-300">NoobGPU</h1>

      <select
        className="rounded border border-neutral-700 bg-neutral-900 px-2 py-1 text-sm"
        value={props.selectedId}
        onChange={(e) => props.onSelect(e.target.value)}
        title="Challenge (list page arrives in M5)"
      >
        {props.challenges.map((c) => (
          <option key={c.id} value={c.id}>
            {c.title}
          </option>
        ))}
      </select>

      <button
        onClick={props.onShowGpu}
        className="ml-auto flex items-center gap-2 rounded border border-neutral-700 px-3 py-1 text-sm hover:bg-neutral-800"
        title="GPU specifications"
      >
        <span
          className={`inline-block h-2 w-2 rounded-full ${gpuOk ? 'bg-emerald-400' : 'bg-red-500'}`}
        />
        {props.gpu === null
          ? 'detecting GPU…'
          : props.gpu.available
            ? props.gpu.name
            : 'no GPU'}
      </button>

      <button
        onClick={props.onRun}
        disabled={props.running || !gpuOk}
        className="rounded bg-blue-600 px-4 py-1 text-sm font-semibold hover:bg-blue-500 disabled:opacity-40"
        title="Run sample tests (Ctrl+Enter)"
      >
        {props.running ? 'Running…' : '▶ Run'}
      </button>
      <button
        onClick={props.onSubmit}
        disabled={props.running || !gpuOk}
        className="rounded bg-emerald-600 px-4 py-1 text-sm font-semibold hover:bg-emerald-500 disabled:opacity-40"
        title="Submit against all tests"
      >
        🚀 Submit
      </button>
    </header>
  )
}
