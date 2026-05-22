# src/ingestion/reddit_util.py
from urllib.parse import urlparse

def extract_submission_id(s: str) -> str:

    if not s:
        raise ValueError("Identificador vazio.")
    if s.startswith("http://") or s.startswith("https://"):
        path = urlparse(s).path  # '/r/sub/comments/abc123/titulo/'
        parts = [p for p in path.split("/") if p]
        if "comments" in parts:
            i = parts.index("comments")
            if i + 1 < len(parts):
                return parts[i + 1]
        raise ValueError("URL de Reddit inválida: não encontrei /comments/<id>/")
    return s
