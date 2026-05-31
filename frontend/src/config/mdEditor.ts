import { config } from 'md-editor-v3'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

let configured = false

/** 禁用 md-editor 默认 unpkg CDN，改用本地 highlight.js */
export function ensureMdEditorLocalExtensions() {
  if (configured) return
  configured = true
  config({
    editorExtensions: {
      highlight: {
        instance: hljs,
        js: '',
        css: { github: { light: '', dark: '' } },
      },
      prettier: { standaloneJs: '', parserMarkdownJs: '' },
      screenfull: { js: '' },
      mermaid: { js: '' },
      katex: { js: '', css: '' },
      cropper: { js: '', css: '' },
    },
  })
}
