import { useEffect, useState } from 'react'
import { listInstagramAccounts, addInstagramAccount, deleteInstagramAccount } from 'src/services/api'
import { Card, CardContent, CardHeader, CardTitle } from 'src/components/ui/card'
import { Button } from 'src/components/ui/button'
import { Input } from 'src/components/ui/input'
import { Trash2, Plus, Camera, LogOut } from 'lucide-react'
import useAuth from 'src/hooks/auth'

export default function Configuracoes() {
  const { logout } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', password: '', label: '' })
  const [formError, setFormError] = useState(null)
  const [adding, setAdding] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const loadAccounts = async () => {
    setLoading(true)
    try {
      setAccounts(await listInstagramAccounts())
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { loadAccounts() }, [])

  const handleAdd = async () => {
    setFormError(null)
    if (!form.username || !form.password) {
      setFormError('Username e senha são obrigatórios.')
      return
    }
    setAdding(true)
    try {
      await addInstagramAccount({ username: form.username, password: form.password, label: form.label || undefined })
      setForm({ username: '', password: '', label: '' })
      setShowForm(false)
      await loadAccounts()
    } catch (e) {
      setFormError(e.message)
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Remover esta conta?')) return
    try {
      await deleteInstagramAccount(id)
      setAccounts((prev) => prev.filter((a) => a.id !== id))
    } catch {}
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Configurações</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={logout}
          className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700 hover:border-red-300"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sair da conta
        </Button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            <CardTitle className="text-base">Contas Instagram</CardTitle>
          </div>
          <Button size="sm" onClick={() => setShowForm((v) => !v)}>
            <Plus className="h-4 w-4 mr-1" />
            Adicionar conta
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          {showForm && (
            <div className="rounded-lg border p-4 space-y-3 bg-muted/30">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <Input
                  placeholder="Username"
                  value={form.username}
                  onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
                />
                <Input
                  type="password"
                  placeholder="Senha"
                  value={form.password}
                  onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                />
                <Input
                  placeholder="Label (opcional)"
                  value={form.label}
                  onChange={(e) => setForm((f) => ({ ...f, label: e.target.value }))}
                />
              </div>
              {formError && <p className="text-sm text-red-500">{formError}</p>}
              <div className="flex gap-2 justify-end">
                <Button variant="outline" size="sm" onClick={() => { setShowForm(false); setFormError(null) }}>
                  Cancelar
                </Button>
                <Button size="sm" onClick={handleAdd} disabled={adding}>
                  {adding ? 'Salvando...' : 'Salvar'}
                </Button>
              </div>
            </div>
          )}

          {loading ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Carregando...</p>
          ) : accounts.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Nenhuma conta cadastrada.</p>
          ) : (
            <div className="divide-y">
              {accounts.map((acc) => (
                <div key={acc.id} className="flex items-center justify-between py-3">
                  <div>
                    <span className="font-medium text-sm">@{acc.username}</span>
                    {acc.label && (
                      <span className="ml-2 text-xs text-muted-foreground">{acc.label}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                      {acc.created_at ? new Date(acc.created_at).toLocaleDateString('pt-BR') : ''}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-red-500"
                      onClick={() => handleDelete(acc.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
