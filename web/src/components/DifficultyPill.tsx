export const DIFFICULTY_STYLE = {
  easy: 'bg-emerald-900/60 text-emerald-300',
  medium: 'bg-amber-900/60 text-amber-300',
  hard: 'bg-red-900/60 text-red-300',
} as const

export type Difficulty = keyof typeof DIFFICULTY_STYLE

export default function DifficultyPill({ difficulty }: { difficulty: Difficulty }) {
  return (
    <span
      className={`mb-3 inline-block rounded-full px-3 py-0.5 text-xs font-semibold capitalize ${DIFFICULTY_STYLE[difficulty]}`}
    >
      {difficulty}
    </span>
  )
}
