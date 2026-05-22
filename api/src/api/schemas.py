from typing import Literal, Optional
from pydantic import BaseModel


class CommentOut(BaseModel):
    id: str
    platform: str
    source_id: Optional[str] = None
    author: Optional[str] = None
    text: str
    classification: str
    final_score: float
    flagged: bool
    ingested_at: Optional[str] = None


class StatsOut(BaseModel):
    total: int
    suspeito: int
    atencao: int
    ok: int
    by_platform: dict[str, int]


class ScrapeRequest(BaseModel):
    source: Literal["youtube", "reddit", "reddit_auto"]
    identifier: Optional[str] = None
    options: dict = {}


class JobStatusOut(BaseModel):
    job_id: str
    status: str
    summary: Optional[dict] = None
    error: Optional[str] = None
