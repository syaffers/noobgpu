import { useCallback, useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import ServerDown from './components/ServerDown'
import ChallengeList from './pages/ChallengeList'
import Workspace from './pages/Workspace'
import * as api from './lib/api'
import type { ChallengeSummary, GpuInfo } from './lib/types'

export default function App() {
  const [challenges, setChallenges] = useState<ChallengeSummary[] | null>(null)
  const [gpu, setGpu] = useState<GpuInfo | null>(null)
  const [serverDown, setServerDown] = useState(false)

  const load = useCallback(() => {
    setServerDown(false)
    Promise.all([api.fetchChallenges(), api.fetchGpu()])
      .then(([list, gpuInfo]) => {
        setChallenges(list)
        setGpu(gpuInfo)
      })
      .catch(() => setServerDown(true))
  }, [])

  useEffect(load, [load])

  if (serverDown) return <ServerDown onRetry={load} />
  if (challenges === null)
    return (
      <div className="flex h-screen items-center justify-center bg-neutral-950 text-neutral-500">
        loading…
      </div>
    )

  return (
    <Routes>
      <Route path="/" element={<ChallengeList challenges={challenges} gpu={gpu} />} />
      <Route path="/challenges/:id" element={<Workspace gpu={gpu} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
