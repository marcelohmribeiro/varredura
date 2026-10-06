import { supabase } from 'src/lib/supabase'

const BASE = import.meta.env.VITE_API_URL

async function fetchApi(path, opts = {}) {
  const { data: { session } } = await supabase.auth.getSession()
  const res = await fetch(BASE + path, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
      ...opts.headers,
    },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Erro ${res.status}`)
  }
  return res.json()
}

export const getComments = (params = {}) =>
  fetchApi('/comments?' + new URLSearchParams(params))

export const getStats = () =>
  fetchApi('/comments/stats')

export const triggerScrape = (body) =>
  fetchApi('/scrape', { method: 'POST', body: JSON.stringify(body) })

export const getScrapeStatus = (jobId) =>
  fetchApi(`/scrape/status/${jobId}`)

export const listInstagramAccounts = () =>
  fetchApi('/accounts/instagram')

export const addInstagramAccount = (body) =>
  fetchApi('/accounts/instagram', { method: 'POST', body: JSON.stringify(body) })

export const deleteInstagramAccount = (id) =>
  fetchApi(`/accounts/instagram/${id}`, { method: 'DELETE' })
