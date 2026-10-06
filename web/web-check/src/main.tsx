import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './AppLazy.tsx'
import { PasswordGate } from './ui/PasswordGate'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PasswordGate>
      <Suspense fallback={null}>
        <App />
      </Suspense>
    </PasswordGate>
  </StrictMode>,
)
