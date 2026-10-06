"""
src/services/vocab_client.py
"""

import os
import requests
from typing import Any, Dict

VOCAB_URL = os.getenv("VOCAB_API_URL", "http://localhost:8001/v1/vocab")

_EMPTY_VOCAB: Dict[str, Any] = {
    "keywords_explicit": [],
    "examples_implicit": [],
    "regex_patterns": {},
}

def fetch_vocab() -> Dict[str, Any]:
    try:
        r = requests.get(VOCAB_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        import logging
        logging.getLogger("vocab_client").warning(
            "Vocab API indisponível em %s — prosseguindo sem vocabulário.", VOCAB_URL
        )
        return _EMPTY_VOCAB
