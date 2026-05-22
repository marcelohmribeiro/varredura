"""
src/services/perspective.py
Integração opcional com Google Perspective API para obter score de conteúdo sexual.
"""

import os
import requests
from typing import Optional, Dict, Any

PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY", None)
PERSPECTIVE_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

def get_sexually_explicit_score(text: str, lang: str = "pt") -> Optional[float]:
    if not PERSPECTIVE_API_KEY:
        return None

    payload: Dict[str, Any] = {
        "comment": {"text": text},
        "languages": [lang],
        "requestedAttributes": {"SEXUALLY_EXPLICIT": {}}
    }

    params = {"key": PERSPECTIVE_API_KEY}
    r = requests.post(PERSPECTIVE_URL, params=params, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    try:
        val = data["attributeScores"]["SEXUALLY_EXPLICIT"]["summaryScore"]["value"]
        return float(val)
    except Exception:
        return None
