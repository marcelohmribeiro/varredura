import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.comments import router as comments_router
from api.routers.scrape import router as scrape_router

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


@app.get("/health")
def health():
    return {"status": "ok"}
