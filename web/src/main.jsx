import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './css/index.css'
import { router } from './routes'
import { supabase } from './lib/supabase'
import useAuthStore from './store/authStore'

supabase.auth.onAuthStateChange((_event, session) => {
  useAuthStore.getState().setSession(session)
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
