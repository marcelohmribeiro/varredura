import { useState } from 'react'
import { Input } from 'src/components/ui/input'
import { Button } from 'src/components/ui/button'
import { Mail, Lock, AlertCircle } from 'lucide-react'
import useAuth from 'src/hooks/auth'
import logonobg from 'src/assets/logo-no-bg.png'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { signin } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) return
    setLoading(true)
    setError(null)
    try {
      await signin(email, password)
    } catch (err) {
      setError(err.message || 'Credenciais inválidas.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full flex">
      {/* ── ESQUERDA: formulário (dark) ── */}
      <div
        className="w-full lg:w-1/2 flex flex-col justify-center px-8 sm:px-16 xl:px-24 py-12"
        style={{ background: 'linear-gradient(160deg, #071527 0%, #0d2444 100%)', minHeight: '100vh' }}
      >
        <div className="w-full max-w-sm mx-auto space-y-8">
          {/* logo compacta só no mobile */}
          <div className="flex justify-center lg:hidden pb-2">
            <img src={logonobg} alt="Varredura" className="h-14" />
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-white tracking-tight">Bem-vindo de volta</h1>
            <p className="text-slate-400 text-sm">Entre com suas credenciais para acessar o painel.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-300">E-mail</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                <Input
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 h-11 bg-white/5 border-white/10 text-white placeholder:text-slate-600 focus-visible:border-blue-500 focus-visible:ring-blue-500/20"
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-300">Senha</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 h-11 bg-white/5 border-white/10 text-white placeholder:text-slate-600 focus-visible:border-blue-500 focus-visible:ring-blue-500/20"
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-2.5 text-sm text-red-400">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-11 text-sm font-semibold cursor-pointer border-0"
              style={{ background: 'linear-gradient(135deg, #1e4fa3, #2563eb)' }}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Conectando...
                </span>
              ) : 'Entrar'}
            </Button>
          </form>
        </div>
      </div>

      {/* ── DIREITA: logo no fundo claro ── */}
      <div className="hidden lg:flex w-1/2 flex-col items-center justify-center bg-slate-50 relative overflow-hidden">
        {/* detalhe decorativo canto */}
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-blue-100 opacity-60 pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-72 h-72 rounded-full bg-slate-200 opacity-50 pointer-events-none" />

        <div className="relative z-10 flex flex-col items-center gap-6 px-16">
          <img src={logonobg} alt="Varredura" className="w-full max-w-sm" />
          <p className="text-slate-400 text-xs tracking-widest uppercase">
            Monitoramento inteligente de comentários
          </p>
        </div>
      </div>
    </div>
  )
}