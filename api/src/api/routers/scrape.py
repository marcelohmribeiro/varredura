import argparse
import threading
import uuid
from fastapi import APIRouter, HTTPException
from api.schemas import ScrapeRequest, JobStatusOut

router = APIRouter()

_jobs: dict[str, dict] = {}


def _run_job(job_id: str, req: ScrapeRequest):
    from main import run_pipeline

    _jobs[job_id]["status"] = "running"
    try:
        args = _build_args(req)
        results = run_pipeline(args)
        sus = sum(1 for r in results if r.classification == "suspeito")
        aten = sum(1 for r in results if r.classification == "atencao")
        ok = sum(1 for r in results if r.classification == "ok")
        _jobs[job_id].update({
            "status": "done",
            "summary": {"total": len(results), "suspeito": sus, "atencao": aten, "ok": ok},
        })
    except Exception as e:
        _jobs[job_id].update({"status": "error", "error": str(e)})


def _build_args(req: ScrapeRequest) -> argparse.Namespace:
    opts = req.options or {}
    ns = argparse.Namespace(
        video_id=req.identifier if req.source == "youtube" else None,
        reddit_submission=req.identifier if req.source == "reddit" else None,
        reddit_search_auto=(req.source == "reddit_auto"),
        page_size=opts.get("page_size", 50),
        max_pages=opts.get("max_pages", 3),
        limit=opts.get("limit", 200),
        reddit_sort=opts.get("reddit_sort", "new"),
        reddit_only_root=opts.get("reddit_only_root", False),
        subreddits=opts.get("subreddits", "all"),
        reddit_posts_per_query=opts.get("reddit_posts_per_query", 15),
        reddit_per_submission_limit=opts.get("reddit_per_submission_limit", 80),
        reddit_time_filter=opts.get("reddit_time_filter", "week"),
        reddit_search_sort=opts.get("reddit_search_sort", "new"),
        reddit_max_terms=opts.get("reddit_max_terms", 20),
        limit_total=opts.get("limit_total", 300),
        persist=True,
    )
    return ns


@router.post("", response_model=JobStatusOut, status_code=202)
def trigger_scrape(req: ScrapeRequest):
    if req.source in ("youtube", "reddit") and not req.identifier:
        raise HTTPException(400, "identifier é obrigatório para youtube e reddit")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "summary": None, "error": None}

    thread = threading.Thread(target=_run_job, args=(job_id, req), daemon=True)
    thread.start()

    return JobStatusOut(job_id=job_id, status="queued")


@router.get("/status/{job_id}", response_model=JobStatusOut)
def scrape_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job não encontrado")
    return JobStatusOut(job_id=job_id, **job)
