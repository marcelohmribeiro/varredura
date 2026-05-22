"""
src/ingestion/youtube.py
"""
import os
import time
import logging
import pandas as pd
from typing import List, Dict, Tuple
from googleapiclient.discovery import build
from dotenv import load_dotenv

logger = logging.getLogger("ingestion.youtube")

# carrega variáveis do .env
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def _extract_video_id(url_or_id: str) -> str:
    """
    Aceita tanto a URL completa do YouTube quanto o ID puro.
    """
    if "youtube.com" in url_or_id and "v=" in url_or_id:
        return url_or_id.split("v=")[-1].split("&")[0]
    if "youtu.be" in url_or_id:
        return url_or_id.split("/")[-1].split("?")[0]
    return url_or_id


def fetch_comments(
    video_id: str,
    api_key: str,
    max_pages: int = 3,
    page_size: int = 100
) -> List[Dict]:
    """
    Busca comentários usando a YouTube Data API v3.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    comments_raw: List[Dict] = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=min(page_size, 100),
        textFormat="plainText",
        order="time"
    )

    page = 0
    while request and page < max_pages:
        response = request.execute()
        items = response.get("items", [])
        comments_raw.extend(items)
        logger.info(f"[YouTube] Página {page+1}: {len(items)} comentários")
        request = youtube.commentThreads().list_next(request, response)
        page += 1
        time.sleep(0.3)

    return comments_raw


def normalize_comment(item: Dict) -> Dict:
    """
    Normaliza um comentário do YouTube.
    """
    snippet = item.get("snippet", {})
    top = snippet.get("topLevelComment", {}).get("snippet", {})

    return {
        "comment_id": item.get("id", ""),
        "author": top.get("authorDisplayName"),
        "text": top.get("textDisplay", ""),
        "likeCount": top.get("likeCount", 0),
        "publishedAt": top.get("publishedAt")
    }


def get_youtube_comments(url_or_id: str, limit: int = 100) -> pd.DataFrame:
    """
    Função de alto nível para buscar comentários normalizados em DataFrame.
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY não configurada no .env")

    video_id = _extract_video_id(url_or_id)
    raw_comments = fetch_comments(video_id=video_id, api_key=YOUTUBE_API_KEY, max_pages=limit // 100 + 1)
    normalized = [normalize_comment(item) for item in raw_comments]

    return pd.DataFrame(normalized[:limit])
