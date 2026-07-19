import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import DifficultyPill, { type Difficulty } from './DifficultyPill'

type Props = { description: string; difficulty?: Difficulty }

export default function ProblemPanel({ description, difficulty }: Props) {
  return (
    <div className="h-full overflow-y-auto px-6 py-4">
      <div className="mx-auto max-w-3xl">
        {difficulty && <DifficultyPill difficulty={difficulty} />}
        <div className="prose-invert space-y-4 text-sm leading-relaxed [&_code]:rounded [&_code]:bg-neutral-800 [&_code]:px-1 [&_code]:font-mono [&_h1]:text-2xl [&_h1]:font-bold [&_h2]:mt-6 [&_h2]:text-lg [&_h2]:font-semibold [&_li]:ml-5 [&_li]:list-disc [&_pre]:overflow-x-auto [&_pre]:rounded [&_pre]:bg-neutral-900 [&_pre]:p-3 [&_pre_code]:bg-transparent [&_pre_code]:p-0">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{description}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
