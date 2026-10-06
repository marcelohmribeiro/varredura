import { useEffect, useState, useCallback } from 'react'
import { getStats, getComments, triggerScrape, getScrapeStatus } from 'src/services/api'
import { Card, CardContent, CardHeader, CardTitle } from 'src/components/ui/card'
import { Button } from 'src/components/ui/button'
import { Input } from 'src/components/ui/input'
import { AlertTriangle, CheckCircle, Eye, BarChart2, RefreshCw, Play } from 'lucide-react'

const LABEL_STYLES = {
  suspeito: 'bg-red-100 text-red-700',
  atencao: 'bg-yellow-100 text-yellow-700',
  ok: 'bg-green-100 text-green-700',
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 pt-6">
        <div className={`rounded-full p-3 ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-bold">{value ?? '—'}</p>
        </div>
      </CardContent>
    </Card>
  )
}

function ScrapeModal({ onClose, onDone }) {
  const [source, setSource] = useState('youtube')
  const [identifier, setIdentifier] = useState('')
  const [twitterMode, setTwitterMode] = useState('post')
  const [instagramMode, setInstagramMode] = useState('post')
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const identifierLabel = source === 'youtube'
    ? 'ID do vídeo'
    : source === 'reddit'
    ? 'ID do post Reddit'
    : source === 'twitter'
    ? (twitterMode === 'post' ? 'URL do tweet' : twitterMode === 'profile' ? 'Username (sem @)' : 'Hashtag (sem #)')
    : source === 'instagram'
    ? `ID do ${instagramMode}`
    : 'Identificador'

  const identifierPlaceholder = source === 'youtube'
    ? 'ex: dQw4w9WgXcQ'
    : source === 'reddit'
    ? 'ex: abc123'
    : source === 'twitter'
    ? (twitterMode === 'post' ? 'ex: https://twitter.com/user/status/123' : twitterMode === 'profile' ? 'ex: elonmusk' : 'ex: brasil')
    : source === 'instagram'
    ? (instagramMode === 'reel' ? 'ex: C1a2b3c4d5e' : 'ex: C1a2b3c4d5e')
    : ''

  const buildOptions = () => {
    if (source === 'twitter') return { twitter_mode: twitterMode }
    if (source === 'instagram') return { instagram_mode: instagramMode }
    return {}
  }

  const start = async () => {
    setError(null)
    setLoading(true)
    try {
      const res = await triggerScrape({
        source,
        identifier: identifier || undefined,
        options: buildOptions(),
      })
      setJobId(res.job_id)
      setStatus(res.status)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!jobId || status === 'done' || status === 'error') return
    const interval = setInterval(async () => {
      try {
        const res = await getScrapeStatus(jobId)
        setStatus(res.status)
        if (res.status === 'done') { onDone(); clearInterval(interval) }
        if (res.status === 'error') { setError(res.error); clearInterval(interval) }
      } catch {}
    }, 3000)
    return () => clearInterval(interval)
  }, [jobId, status, onDone])

  const needsIdentifier = source !== 'reddit_auto'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>Novo Scraping</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Fonte</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="youtube">YouTube</option>
              <option value="reddit">Reddit (post específico)</option>
              <option value="reddit_auto">Reddit (busca automática)</option>
              <option value="twitter">Twitter</option>
              <option value="instagram">Instagram</option>
            </select>
          </div>

          {source === 'twitter' && (
            <div className="space-y-1">
              <label className="text-sm font-medium">Modo</label>
              <select
                value={twitterMode}
                onChange={(e) => setTwitterMode(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="post">Post (URL completa)</option>
                <option value="profile">Perfil (username)</option>
                <option value="hashtag">Hashtag</option>
              </select>
            </div>
          )}

          {source === 'instagram' && (
            <div className="space-y-1">
              <label className="text-sm font-medium">Modo</label>
              <select
                value={instagramMode}
                onChange={(e) => setInstagramMode(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="post">Post (ID)</option>
                <option value="reel">Reel (ID)</option>
              </select>
            </div>
          )}

          {needsIdentifier && (
            <div className="space-y-1">
              <label className="text-sm font-medium">{identifierLabel}</label>
              <Input
                placeholder={identifierPlaceholder}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
              />
            </div>
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}

          {status && (
            <div className="text-sm text-muted-foreground">
              Status: <span className="font-medium">{status}</span>
              {status === 'running' && <RefreshCw className="inline ml-2 h-3 w-3 animate-spin" />}
              {status === 'done' && <span className="text-green-600 ml-2">Concluído!</span>}
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>Fechar</Button>
            <Button onClick={start} disabled={loading || status === 'running'}>
              <Play className="h-4 w-4 mr-2" />
              {loading ? 'Iniciando...' : 'Iniciar'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [comments, setComments] = useState([])
  const [platform, setPlatform] = useState('')
  const [classification, setClassification] = useState('')
  const [loadingComments, setLoadingComments] = useState(false)
  const [showScrape, setShowScrape] = useState(false)

  const loadStats = useCallback(async () => {
    try { setStats(await getStats()) } catch {}
  }, [])

  const loadComments = useCallback(async () => {
    setLoadingComments(true)
    try {
      const params = {}
      if (platform) params.platform = platform
      if (classification) params.classification = classification
      setComments(await getComments(params))
    } catch {}
    finally { setLoadingComments(false) }
  }, [platform, classification])

  useEffect(() => { loadStats() }, [loadStats])
  useEffect(() => { loadComments() }, [loadComments])

  const handleScrapeDone = () => {
    loadStats()
    loadComments()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Button onClick={() => setShowScrape(true)}>
          <Play className="h-4 w-4 mr-2" />
          Novo Scraping
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={BarChart2} label="Total" value={stats?.total} color="bg-blue-100 text-blue-700" />
        <StatCard icon={AlertTriangle} label="Suspeito" value={stats?.suspeito} color="bg-red-100 text-red-700" />
        <StatCard icon={Eye} label="Atenção" value={stats?.atencao} color="bg-yellow-100 text-yellow-700" />
        <StatCard icon={CheckCircle} label="OK" value={stats?.ok} color="bg-green-100 text-green-700" />
      </div>

      {/* Filtros */}
      <div className="flex gap-3 flex-wrap">
        <select
          value={platform}
          onChange={(e) => setPlatform(e.target.value)}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Todas as plataformas</option>
          <option value="youtube">YouTube</option>
          <option value="reddit">Reddit</option>
          <option value="twitter">Twitter</option>
          <option value="instagram">Instagram</option>
        </select>

        <select
          value={classification}
          onChange={(e) => setClassification(e.target.value)}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Todas as classificações</option>
          <option value="suspeito">Suspeito</option>
          <option value="atencao">Atenção</option>
          <option value="ok">OK</option>
        </select>

        <Button variant="outline" onClick={loadComments} disabled={loadingComments}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loadingComments ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="px-4 py-3 text-left font-medium">Autor</th>
                  <th className="px-4 py-3 text-left font-medium">Comentário</th>
                  <th className="px-4 py-3 text-left font-medium">Plataforma</th>
                  <th className="px-4 py-3 text-left font-medium">Score</th>
                  <th className="px-4 py-3 text-left font-medium">Label</th>
                </tr>
              </thead>
              <tbody>
                {loadingComments && (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Carregando...</td></tr>
                )}
                {!loadingComments && comments.length === 0 && (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Nenhum comentário encontrado.</td></tr>
                )}
                {comments.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-muted/20">
                    <td className="px-4 py-3 font-medium text-nowrap">{c.author || '—'}</td>
                    <td className="px-4 py-3 max-w-sm truncate" title={c.text}>{c.text}</td>
                    <td className="px-4 py-3 capitalize">{c.platform}</td>
                    <td className="px-4 py-3">{c.final_score?.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LABEL_STYLES[c.classification] || ''}`}>
                        {c.classification}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {showScrape && (
        <ScrapeModal onClose={() => setShowScrape(false)} onDone={handleScrapeDone} />
      )}
    </div>
  )
}
