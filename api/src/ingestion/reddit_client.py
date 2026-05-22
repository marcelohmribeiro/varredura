# src/ingestion/reddit_client.py
from functools import lru_cache
import praw
from src.common.config import get_env

@lru_cache(maxsize=1)
def get_client() -> praw.Reddit:
    client_id = get_env("REDDIT_CLIENT_ID")
    client_secret = get_env("REDDIT_CLIENT_SECRET")
    user_agent = get_env("REDDIT_USER_AGENT") or "AlertaSegurancaOnline/0.1 by u/unknown"

    if not (client_id and client_secret):
        raise SystemExit("Defina REDDIT_CLIENT_ID e REDDIT_CLIENT_SECRET no .env")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False,
    )
