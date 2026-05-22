# src/ingestion/reddit.py
from datetime import datetime
from typing import List, Dict
import praw
import pandas as pd

from .reddit_client import get_client


def fetch_submission_comments(
    submission_id: str,
    limit: int = 200,
    sort: str = "new",
    only_root: bool = False,
) -> List[Dict]:
    reddit = get_client()
    sub = reddit.submission(id=submission_id)

    # sort aceitos pelo Reddit
    if sort in {"new", "top", "best", "controversial", "old", "qa"}:
        sub.comment_sort = sort

    # expande 'MoreComments'
    sub.comments.replace_more(limit=0)

    comments = sub.comments if only_root else sub.comments.list()

    out: List[Dict] = []
    count = 0
    for c in comments:
        if not isinstance(c, praw.models.Comment):
            continue
        if only_root and not c.is_root:
            continue

        author = str(c.author) if c.author else "[deleted]"
        out.append({
            "comment_id": f"{sub.id}:{c.id}",
            "platform": "reddit",
            "source_id": sub.id,
            "author": author,
            "text": c.body or "",
            "likeCount": getattr(c, "score", 0),
            "publishedAt": datetime.utcfromtimestamp(c.created_utc).isoformat() + "Z",
            "permalink": f"https://www.reddit.com{c.permalink}",
        })

        count += 1
        if limit and count >= limit:
            break

    return out


def _extract_submission_id(url_or_id: str) -> str:
    """Aceita tanto a URL quanto o ID do post"""
    if "reddit.com" in url_or_id:
        parts = url_or_id.split("/")
        # ID do post está sempre depois de "comments"
        if "comments" in parts:
            idx = parts.index("comments")
            return parts[idx + 1]
    return url_or_id  # já é o ID puro


def get_reddit_comments(url_or_id: str, limit: int = 100) -> pd.DataFrame:
    """
    Busca e retorna comentários do Reddit em um DataFrame.
    """
    submission_id = _extract_submission_id(url_or_id)
    raw_comments = fetch_submission_comments(submission_id=submission_id, limit=limit)
    return pd.DataFrame(raw_comments)
