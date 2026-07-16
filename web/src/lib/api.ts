import type { ChallengeDetail, ChallengeSummary, GpuInfo, JudgeEvent } from './types'

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url}: ${res.status}`)
  return res.json()
}

export const fetchGpu = () => getJson<GpuInfo>('/api/gpu')
export const fetchChallenges = () => getJson<ChallengeSummary[]>('/api/challenges')
export const fetchChallenge = (id: string) => getJson<ChallengeDetail>(`/api/challenges/${id}`)

export async function fetchDraft(id: string): Promise<string | null> {
  const res = await fetch(`/api/challenges/${id}/draft`)
  if (!res.ok) throw new Error(`draft: ${res.status}`)
  return (await res.json()).code
}

export async function saveDraft(id: string, code: string): Promise<void> {
  await fetch(`/api/challenges/${id}/draft`, {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ code }),
  })
}

/** POST code and yield judge events as the SSE stream arrives. */
export async function* streamJudge(
  id: string,
  action: 'run' | 'submit',
  code: string,
  signal?: AbortSignal,
): AsyncGenerator<JudgeEvent> {
  const res = await fetch(`/api/challenges/${id}/${action}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ code }),
    signal,
  })
  if (!res.ok || !res.body) throw new Error(`${action}: ${res.status}`)

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''
    for (const frame of frames) {
      for (const line of frame.split('\n')) {
        if (line.startsWith('data: ')) yield JSON.parse(line.slice(6)) as JudgeEvent
      }
    }
  }
}
