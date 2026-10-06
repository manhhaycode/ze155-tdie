import { lazy } from 'react'

/** the viewer (three, the GLBs) as a separate chunk: it loads only after the password gate opens */
const LazyApp = lazy(() => import('./App.tsx'))
export default LazyApp
