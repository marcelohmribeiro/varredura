from typing import Dict
from . import twitter_web

def get_twitter_comments(mode: str, query: str, limit: int = 20) -> Dict[str, Dict]:
    """
    Interface única para buscar comentários do Twitter.
    """
    return twitter_web.fetch_comments(mode=mode, query=query, limit=limit)
