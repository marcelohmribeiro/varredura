# API — Backend Python

Pipeline completo de coleta, pré-processamento, classificação e armazenamento de comentários.

## Como Rodar a API REST (frontend)

```bash
cd api && source venv/bin/activate
uvicorn src.api.app:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

## Endpoints da API REST

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/comments` | Lista comentários (filtros: platform, classification, limit, offset) |
| GET | `/comments/stats` | Totais por label e por plataforma |
| POST | `/scrape` | Dispara pipeline em background, retorna `job_id` |
| GET | `/scrape/status/{job_id}` | Consulta status do job |

## Estrutura

```
api/
├── src/
│   ├── api/
│   │   ├── app.py               # FastAPI principal + CORS — rodar com uvicorn
│   │   ├── schemas.py           # Pydantic: CommentOut, StatsOut, ScrapeRequest, JobStatusOut
│   │   └── routers/
│   │       ├── comments.py      # GET /comments, GET /comments/stats
│   │       └── scrape.py        # POST /scrape, GET /scrape/status/{job_id}
│   ├── main.py                  # CLI principal — entry point do pipeline
│   ├── export_attention.py      # Exporta só comentários "atencao" para CSV
│   ├── ingestion/
│   │   ├── youtube.py           # Coleta via YouTube Data API v3
│   │   ├── reddit.py            # Coleta submission específico via PRAW
│   │   ├── reddit_search.py     # Busca inteligente no Reddit por keywords
│   │   ├── reddit_util.py       # Utilitário: extrai submission_id de URL
│   │   ├── twitter.py           # Twitter (incompleto/legado)
│   │   ├── twitter_web.py       # Twitter web scraping (incompleto)
│   │   └── instagram_web.py     # Instagram (incompleto)
│   ├── preprocess/
│   │   └── text.py              # Limpeza + lematização PT-BR (spaCy + NLTK)
│   ├── classify/
│   │   └── aggregator.py        # Agrega scores → label final
│   ├── storage/
│   │   ├── firestore.py         # Persistência no Firestore (upsert por doc_id)
│   │   ├── mongo.py             # MongoDB (não é o storage principal)
│   │   └── csv_exporter.py      # Export para CSV
│   ├── tools/
│   │   ├── firestore_to_bq.py   # Migração Firestore → BigQuery
│   │   ├── upload_to_firestore.py
│   │   └── smoke_teste.py
│   └── services/
│       ├── vocab_client.py      # Busca keywords/exemplos/regex na Vocab API
│       └── filter_csv.py        # Chama Google Perspective API
├── scraper_manager.py           # CLI interativo legado (não usa o pipeline novo)
├── cleanCsv.py                  # Utilitário para limpar CSVs
├── configs/settings.yaml        # Configurações de NLP, thresholds, storage
├── secrets/firebase-key.json    # Credencial Firebase (não commitar)
└── requirements.txt
```

## Pipeline (main.py → run_pipeline)

1. **Vocab** — busca `keywords_explicit`, `examples_implicit`, `regex_patterns` da Vocab API
2. **Ingestion** — coleta comentários da plataforma escolhida
3. **Preprocess** — limpa URLs/@/#, lowercase, lematização PT-BR com spaCy, remove stopwords
4. **Rules** — aplica regex e keywords (hits = lista de termos encontrados)
5. **Semantic** — similaridade do texto pré-processado com exemplos via sentence-transformers
6. **Perspective** (opcional) — toxicidade sexual via Google Perspective API
7. **Aggregate** — score final e label
8. **Persist** (opcional com `--persist`) — salva no Firestore com upsert

## Lógica de Classificação (aggregator.py)

```python
rules_component  = rule_weight (0.6) se houve hits, senão 0
semantic_component = semantic_weight (0.6) se score >= similarity_threshold (0.55), senão 0
final_score = rules_component + semantic_component + (perspective * 0.4 se habilitado)

label = "suspeito"  se final_score >= 0.9
      = "atencao"   se final_score >= 0.54  (60% de 0.9)
      = "ok"        caso contrário
```

## Firestore

- **Collection**: `comments`
- **doc_id**: `{platform}:{source_id}:{comment_id}` (determinístico, permite upsert)
- **TTL**: deleta docs com `ingestedAt` mais antigos que `ttl_days` (default: 1 dia)
- **Credencial**: variável `GOOGLE_APPLICATION_CREDENTIALS` apontando para `secrets/firebase-key.json`

## Vocab API

- Roda em `http://localhost:8001/v1/vocab` (serviço separado)
- Retorna `{ keywords_explicit, examples_implicit, regex_patterns }`

## Modelo de Dados (CommentRecord)

```python
platform, source_id, comment_id, author, text, preprocessed,
rule_hits (list[str]), semantic_score (float), perspective_sexual (float|None),
final_score (float), classification ("suspeito"|"atencao"|"ok"),
extras { likeCount, publishedAt, permalink }, ingestedAt
```

## Plataformas Suportadas (status)

| Plataforma | Status |
|---|---|
| YouTube | Funcional (YouTube Data API v3) |
| Reddit (post específico) | Funcional (PRAW) |
| Reddit (busca por keywords) | Funcional |
| Twitter | Código presente mas incompleto/quebrado |
| Instagram | Código presente mas incompleto |

## Atenção

- `scraper_manager.py` na raiz é legado/MVP inicial — não usa o pipeline atual de NLP/classificação
- `settings.yaml` tem dois blocos `storage:` (duplicação, só o segundo é lido pelo Python)
- O modelo spaCy PT-BR precisa ser instalado: `python -m spacy download pt_core_news_sm`
