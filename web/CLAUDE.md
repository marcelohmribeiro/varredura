# Web — Frontend React/Vite

Dashboard para visualização e controle do sistema de detecção.

## Stack

- **React 19** + **Vite 6**
- **TailwindCSS 4** + **shadcn/ui** (Radix UI)
- **Zustand** (estado global, auth com persist no localStorage)
- **react-router-dom 7**
- **lucide-react** (ícones)
- **html2canvas + jsPDF** (exportação)

## Rodar

```bash
cd web
bun dev       # dev server
bun run build # build para produção
```

## Estrutura

```
web/src/
├── main.jsx                     # Entry point
├── routes/index.jsx             # Definição de todas as rotas
├── config/index.js              # Lê VITE_APP_NAME do .env
├── constants/index.js           # Itens de navegação do sidebar
├── store/
│   └── authStore.js             # Zustand — isAuthenticated, token, user
├── hooks/
│   └── auth.js                  # Hook useAuth (signin, logout)
├── components/
│   ├── _protected-route.jsx     # Guard de rota autenticada
│   └── ui/                      # Componentes shadcn (button, card, input)
└── pages/
    ├── index.jsx                # Redireciona para /login
    ├── layout.jsx               # Layout raiz (sem proteção)
    ├── auth/
    │   └── layout.jsx           # Layout protegido (Sidebar + ProtectedRoute)
    ├── (public)/
    │   └── login.jsx            # Página de login
    └── components/
        └── _sidebar.jsx         # Sidebar colapsável com navegação
```

## Rotas

| Path | Componente | Protegida |
|---|---|---|
| `/` | Redireciona → `/login` | Não |
| `/login` | Login | Não |
| `/auth/dashboard` | `<h1>Dashboard</h1>` (placeholder) | Sim |
| `/auth/configuracoes` | `<h1>Configurações</h1>` (placeholder) | Sim |

## Estado Atual (maio/2026)

- Login com Supabase Auth real (email + senha)
- Dashboard com stats cards, tabela de comentários, filtros e modal de trigger de scraping
- Integração completa com a API FastAPI (GET /comments, GET /comments/stats, POST /scrape)
- Sidebar com branding "FonoSystem" ainda pendente de atualização

## Variáveis de Ambiente (web/.env)

```
VITE_APP_NAME=AlertaSeguranca
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://...supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## Serviços

- `web/src/lib/supabase.js` — cliente Supabase (Auth)
- `web/src/services/api.js` — fetchApi + getComments, getStats, triggerScrape, getScrapeStatus

## Próximos Passos

- Atualizar branding do sidebar (logo + nome)
- Página de Configurações (thresholds, vocab)
- Paginação na tabela de comentários
