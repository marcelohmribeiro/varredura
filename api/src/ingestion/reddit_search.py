# src/ingestion/reddit_search.py
from typing import List, Dict, Iterable, Set
from .reddit_client import get_client
from .reddit import fetch_submission_comments

def search_and_collect_comments(
    queries: List[str],
    subreddits: List[str],
    limit_per_query: int = 15,
    time_filter: str = "week",       
    sort: str = "new",               
    per_submission_limit: int = 80,
    max_total: int = 300,
) -> List[Dict]:

    reddit = get_client()
    total: List[Dict] = []
    seen_submissions: Set[str] = set()

    def _iter_subs() -> Iterable[str]:
        return subreddits or ["all"]

    for q in queries:
        if len(total) >= max_total:
            break

        for s in _iter_subs():
            if len(total) >= max_total:
                break

            sr = reddit.subreddit(s)
            submissions = sr.search(
                q, sort=sort, time_filter=time_filter, limit=limit_per_query
            )

            for sub in submissions:
                sid = sub.id
                if sid in seen_submissions:
                    continue
                seen_submissions.add(sid)

                rows = fetch_submission_comments(
                    submission_id=sid,
                    limit=per_submission_limit,
                    sort="new",
                    only_root=False,
                )
                total.extend(rows)

                if len(total) >= max_total:
                    break

    if len(total) > max_total:
        total = total[:max_total]
    return total
