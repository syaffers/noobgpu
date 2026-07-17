import { useState } from 'react'
import GpuModal from './GpuModal'
import type { GpuInfo } from '../lib/types'

export default function GpuBadge({ gpu }: { gpu: GpuInfo | null }) {
  const [show, setShow] = useState(false)
  const ok = gpu?.available === true && gpu.nvcc.available
  return (
    <>
      <button
        onClick={() => setShow(true)}
        className="flex items-center gap-2 rounded border border-neutral-700 px-3 py-1 text-sm hover:bg-neutral-800"
        title="GPU specifications"
      >
        <span
          className={`inline-block h-2 w-2 rounded-full ${ok ? 'bg-emerald-400' : 'bg-red-500'}`}
        />
        {gpu === null ? 'detecting GPU…' : gpu.available ? gpu.name : 'no GPU'}
      </button>
      {show && gpu && <GpuModal gpu={gpu} onClose={() => setShow(false)} />}
    </>
  )
}
