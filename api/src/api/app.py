import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.comments import router as comments_router
from api.routers.scrape import router as scrape_router
from api.routers.accounts import router as accounts_router

app = FastAPI(title="Alerta Segurança API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments_router, prefix="/comments", tags=["comments"])
app.include_router(scrape_router, prefix="/scrape", tags=["scrape"])
app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])


@app.get("/health")
def health():
    return {"status": "ok"}
