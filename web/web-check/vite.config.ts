import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import path from 'node:path'

// Review M3 (HMR): the scene registry (`reg`), the raycast filter functions, the cut caches and the
// zustand store are module singletons bound to the cached useGLTF scenes. A hot update of any of them
// would leave a fresh, empty registry next to scenes already marked as rigged. So every change under
// src/ except builder A's UI components in src/ui/ (plain React, safe for fast refresh) and CSS forces
// a full page reload.
function fullReloadOutsideUi(): Plugin {
  const src = path.resolve(import.meta.dirname, 'src') + path.sep
  const ui = path.resolve(import.meta.dirname, 'src/ui') + path.sep
  return {
    name: 'ze-full-reload-outside-ui',
    apply: 'serve',
    hotUpdate({ file }) {
      if (this.environment.name !== 'client') return
      if (!file.startsWith(src) || file.startsWith(ui) || file.endsWith('.css')) return
      this.environment.hot.send({ type: 'full-reload', path: '*' })
      return []
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), fullReloadOutsideUi()],
  server: { port: 5178, strictPort: true },
})
