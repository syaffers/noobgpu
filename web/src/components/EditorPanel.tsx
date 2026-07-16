import Editor from '@monaco-editor/react'
import '../lib/monaco'

type Props = {
  code: string
  onChange: (code: string) => void
  onReset: () => void
}

export default function EditorPanel({ code, onChange, onReset }: Props) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-neutral-800 px-4 py-1.5">
        <span className="font-mono text-sm text-neutral-300">solution.cu</span>
        <button
          onClick={onReset}
          className="rounded border border-neutral-700 px-2 py-0.5 text-xs text-neutral-300 hover:bg-neutral-800"
          title="Reset to starter code"
        >
          ↺ Reset
        </button>
      </div>
      <div className="min-h-0 flex-1">
        <Editor
          language="cpp"
          theme="vs-dark"
          value={code}
          onChange={(value) => onChange(value ?? '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
          }}
        />
      </div>
    </div>
  )
}
