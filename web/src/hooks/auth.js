import { useNavigate } from 'react-router-dom'
import { supabase } from 'src/lib/supabase'
import useAuthStore from 'src/store/authStore'

const useAuth = () => {
  const navigate = useNavigate()
  const { isAuthenticated, setSession, logout: clearStore } = useAuthStore()

  const signin = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    setSession(data.session)
    navigate('/auth/dashboard')
  }

  const logout = async () => {
    await supabase.auth.signOut()
    clearStore()
    navigate('/login')
  }

  return { signin, logout, isAuthenticated }
}

export default useAuth
export { useAuth }