export type GpuInfo =
  | {
      available: true
      name: string
      driver_version: string
      memory_total_mib: number
      compute_capability: string
    }
  | { available: false; error: string }

export type ChallengeSummary = {
  id: string
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  blurb: string
}

export type ChallengeDetail = {
  id: string
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  tolerance: number
  description: string
  starter_code: string
  tests: { name: string; sample: boolean }[]
}

export type Verdict =
  | 'accepted'
  | 'wrong_answer'
  | 'compile_error'
  | 'runtime_error'
  | 'time_limit_exceeded'

export type JudgeEvent =
  | { type: 'prepare_start' }
  | { type: 'prepare_end' }
  | { type: 'compile_start' }
  | { type: 'compile_end'; ok: boolean; stderr: string; duration_s: number }
  | { type: 'test_start'; name: string; sample: boolean }
  | {
      type: 'test_end'
      name: string
      sample: boolean
      passed: boolean
      max_abs_err: number | null
      kernel_ms: number | null
      stderr: string
    }
  | {
      type: 'result'
      verdict: Verdict
      kernel_ms: number | null
      failed_test: string | null
      submission_id: number | null
    }
  | { type: 'error'; error_type: string; message: string }
