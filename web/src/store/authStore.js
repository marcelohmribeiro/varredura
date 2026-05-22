import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { settings } from 'src/config'

const { APP_NAME } = settings

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      session: null,
      isAuthenticated: false,

      setSession: (session) =>
        set({
          session,
          user: session?.user ?? null,
          isAuthenticated: !!session,
        }),

      logout: () => {
        localStorage.removeItem(APP_NAME)
        set({ session: null, user: null, isAuthenticated: false })
      },
    }),
    {
      name: APP_NAME,
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
)

export default useAuthStore
export { useAuthStore }
