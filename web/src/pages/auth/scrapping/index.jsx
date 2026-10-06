import { useEffect, useState } from 'react'
import { triggerScrape, getScrapeStatus, listInstagramAccounts } from 'src/services/api'
import useScrapingStore from 'src/store/scrapingStore'
import { Card, CardContent, CardHeader, CardTitle } from 'src/components/ui/card'
import { Button } from 'src/components/ui/button'
import { Input } from 'src/components/ui/input'
import { Play, RefreshCw, CheckCircle, AlertCircle, Clock, Trash2 } from 'lucide-react'

const STATUS_ICON = {
  queued:  <Clock className="h-4 w-4 text-muted-foreground" />,
  running: <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />,
  done:    <CheckCircle className="h-4 w-4 text-green-500" />,
  error:   <AlertCircle className="h-4 w-4 text-red-500" />,
}

const SOURCES = [
  { value: 'youtube',     label: 'YouTube' },
  { value: 'reddit',      label: 'Reddit (post específico)' },
  { value: 'reddit_auto', label: 'Reddit (busca automática)' },
  { value: 'twitter',     label: 'Twitter' },
  { value: 'instagram',   label: 'Instagram' },
]

const TWITTER_MODES = [
  { value: 'post',     label: 'Post (URL completa)' },
  { value: 'profile',  label: 'Perfil (username)' },
  { value: 'hashtag',  label: 'Hashtag' },
]

const INSTAGRAM_MODES = [
  { value: 'post',  label: 'Post (ID)' },
  { value: 'reel',  label: 'Reel (ID)' },
]

function identifierLabel(source, twitterMode) {
  if (source === 'youtube') return 'ID do vídeo'
  if (source === 'reddit') return 'ID do post Reddit'
  if (source === 'twitter') {
    if (twitterMode === 'profile') return 'Username (sem @)'
    if (twitterMode === 'hashtag') return 'Hashtag (sem #)'
    return 'URL do tweet'
  }
  if (source === 'instagram') return 'ID do post/reel'
  return 'Identificador'
}

function identifierPlaceholder(source, twitterMode, instagramMode) {
  if (source === 'youtube') return 'ex: dQw4w9WgXcQ'
  if (source === 'reddit') return 'ex: abc123'
  if (source === 'twitter') {
    if (twitterMode === 'profile') return 'ex: elonmusk'
    if (twitterMode === 'hashtag') return 'ex: brasil'
    return 'ex: https://twitter.com/user/status/123'
  }
  if (source === 'instagram') return instagramMode === 'reel' ? 'ex: C1a2b3c4d5e' : 'ex: C1a2b3c4d5e'
  return ''
}

function JobRow({ job }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0">
      <div className="shrink-0">{STATUS_ICON[job.status] || STATUS_ICON.queued}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{job.identifier}</p>
        <p className="text-xs text-muted-foreground capitalize">{job.source} · {job.status}</p>
      </div>
      {job.summary && (
        <div className="text-xs text-right shrink-0 space-y-0.5">
          <div className="text-red-600">{job.summary.suspeito} suspeito</div>
          <div className="text-yellow-600">{job.summary.atencao} atenção</div>
        </div>
      )}
      {job.error && (
        <p className="text-xs text-red-500 max-w-[160px] truncate" title={job.error}>{job.error}</p>
      )}
    </div>
  )
}

export default function Scraping() {
  const [source, setSource] = useState('youtube')
  const [twitterMode, setTwitterMode] = useState('post')
  const [instagramMode, setInstagramMode] = useState('post')
  const [accountId, setAccountId] = useState('')
  const [accounts, setAccounts] = useState([])
  const [mode, setMode] = useState('individual')
  const [identifier, setIdentifier] = useState('')
  const [batchIds, setBatchIds] = useState('')
  const [limit, setLimit] = useState(100)
  const [launching, setLaunching] = useState(false)
  const [error, setError] = useState(null)

  const { jobs, addJobs, updateJob, updateJobByKey, clearDone } = useScrapingStore()

  useEffect(() => {
    if (source === 'instagram') {
      listInstagramAccounts().then(setAccounts).catch(() => {})
    }
  }, [source])

  const buildOptions = () => {
    const opts = { limit: Number(limit) || 100 }
    if (source === 'twitter') opts.twitter_mode = twitterMode
    if (source === 'instagram') {
      opts.instagram_mode = instagramMode
      if (accountId) opts.account_id = accountId
    }
    return opts
  }

  const parseIds = () => {
    if (mode === 'individual') return identifier.trim() ? [identifier.trim()] : []
    return batchIds
      .split(/[\n,]+/)
      .map((s) => s.trim())
      .filter(Boolean)
  }

  const start = async () => {
    const ids = parseIds()
    if (!ids.length && source !== 'reddit_auto') {
      setError('Informe ao menos um identificador.')
      return
    }
    setError(null)
    setLaunching(true)

    const targets = source === 'reddit_auto' ? [null] : ids
    const options = buildOptions()

    const newJobs = targets.map((id) => ({
      _key: Math.random().toString(36).slice(2),
      identifier: id || '(busca automática)',
      source,
      status: 'queued',
      jobId: null,
      summary: null,
      error: null,
    }))
    addJobs(newJobs)

    for (let i = 0; i < targets.length; i++) {
      const id = targets[i]
      const key = newJobs[i]._key
      try {
        const res = await triggerScrape({ source, identifier: id || undefined, options })
        updateJobByKey(key, { jobId: res.job_id, status: res.status })
      } catch (e) {
        updateJobByKey(key, { status: 'error', error: e.message })
      }
    }
    setLaunching(false)
  }

  // Polling: reinicia sempre que a lista de jobs ativos muda (inclusive ao voltar para a página)
  const activeJobIds = jobs
    .filter((j) => j.jobId && j.status !== 'done' && j.status !== 'error')
    .map((j) => j.jobId)
    .join(',')

  useEffect(() => {
    const active = jobs.filter((j) => j.jobId && j.status !== 'done' && j.status !== 'error')
    if (!active.length) return

    const interval = setInterval(async () => {
      await Promise.all(
        active.map(async (j) => {
          try {
            const res = await getScrapeStatus(j.jobId)
            updateJob(j.jobId, {
              status: res.status,
              summary: res.summary || null,
              error: res.error || null,
            })
          } catch {}
        })
      )
    }, 3000)

    return () => clearInterval(interval)
  }, [activeJobIds]) // eslint-disable-line react-hooks/exhaustive-deps

  const needsIdentifier = source !== 'reddit_auto'
  const doneCount = jobs.filter((j) => j.status === 'done').length
  const runningCount = jobs.filter((j) => j.status === 'running' || j.status === 'queued').length

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Scraping</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nova coleta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Fonte</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
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
                  {TWITTER_MODES.map((m) => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>
            )}

            {source === 'instagram' && (
              <>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Modo</label>
                  <select
                    value={instagramMode}
                    onChange={(e) => setInstagramMode(e.target.value)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {INSTAGRAM_MODES.map((m) => (
                      <option key={m.value} value={m.value}>{m.label}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="text-sm font-medium">Conta Instagram</label>
                  <select
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="">Usar variável de ambiente (.env)</option>
                    {accounts.map((acc) => (
                      <option key={acc.id} value={acc.id}>
                        @{acc.username}{acc.label ? ` — ${acc.label}` : ''}
                      </option>
                    ))}
                  </select>
                  {accounts.length === 0 && (
                    <p className="text-xs text-muted-foreground">
                      Nenhuma conta cadastrada. Adicione em Configurações.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>

          <div className="space-y-1 w-40">
            <label className="text-sm font-medium">Limite de comentários</label>
            <Input
              type="number"
              min={1}
              max={2000}
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
            />
          </div>

          {needsIdentifier && (
            <>
              <div className="flex gap-2">
                <button
                  onClick={() => setMode('individual')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${mode === 'individual' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-accent'}`}
                >
                  Individual
                </button>
                <button
                  onClick={() => setMode('lote')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${mode === 'lote' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-accent'}`}
                >
                  Lote
                </button>
              </div>

              {mode === 'individual' ? (
                <div className="space-y-1">
                  <label className="text-sm font-medium">{identifierLabel(source, twitterMode)}</label>
                  <Input
                    placeholder={identifierPlaceholder(source, twitterMode, instagramMode)}
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                  />
                </div>
              ) : (
                <div className="space-y-1">
                  <label className="text-sm font-medium">
                    {identifierLabel(source, twitterMode)}s — um por linha
                  </label>
                  <textarea
                    rows={5}
                    placeholder={`${identifierPlaceholder(source, twitterMode, instagramMode)}\n...`}
                    value={batchIds}
                    onChange={(e) => setBatchIds(e.target.value)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono resize-y"
                  />
                  <p className="text-xs text-muted-foreground">
                    {parseIds().length} {parseIds().length === 1 ? 'item' : 'itens'} detectados
                  </p>
                </div>
              )}
            </>
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}

          <div className="flex justify-end">
            <Button onClick={start} disabled={launching}>
              <Play className="h-4 w-4 mr-2" />
              {launching ? 'Iniciando...' : 'Iniciar'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {jobs.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between py-3">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base">Jobs</CardTitle>
              <span className="text-xs text-muted-foreground">
                {doneCount}/{jobs.length} concluídos
                {runningCount > 0 && <RefreshCw className="inline ml-1 h-3 w-3 animate-spin" />}
              </span>
            </div>
            {doneCount > 0 && (
              <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-7" onClick={clearDone}>
                <Trash2 className="h-3 w-3 mr-1" />
                Limpar concluídos
              </Button>
            )}
          </CardHeader>
          <CardContent className="p-0 px-4 pb-2">
            {jobs.map((job) => (
              <JobRow key={job._key} job={job} />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
