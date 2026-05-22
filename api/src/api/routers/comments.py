from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from storage.supabase import get_client
from api.schemas import CommentOut, StatsOut

router = APIRouter()


@router.get("", response_model=list[CommentOut])
def list_comments(
    platform: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    client = get_client()
    q = client.table("comments").select(
        "id,platform,source_id,author,text,classification,final_score,flagged,ingested_at"
    )
    if platform:
        q = q.eq("platform", platform)
    if classification:
        q = q.eq("classification", classification)

    result = q.order("ingested_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.get("/stats", response_model=StatsOut)
def get_stats():
    client = get_client()

    all_rows = client.table("comments").select("classification,platform").execute()
    rows = all_rows.data or []

    total = len(rows)
    suspeito = sum(1 for r in rows if r.get("classification") == "suspeito")
    atencao = sum(1 for r in rows if r.get("classification") == "atencao")
    ok = sum(1 for r in rows if r.get("classification") == "ok")

    by_platform: dict[str, int] = {}
    for r in rows:
        p = r.get("platform") or "unknown"
        by_platform[p] = by_platform.get(p, 0) + 1

    return StatsOut(total=total, suspeito=suspeito, atencao=atencao, ok=ok, by_platform=by_platform)
