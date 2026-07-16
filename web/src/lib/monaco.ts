// Bundle Monaco locally instead of @monaco-editor/react's default CDN loader —
// NoobGPU must work offline.
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import { loader } from '@monaco-editor/react'

;(self as unknown as { MonacoEnvironment: object }).MonacoEnvironment = {
  getWorker: () => new editorWorker(),
}
loader.config({ monaco })
