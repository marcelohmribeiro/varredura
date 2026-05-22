"""
src/services/vocab_client.py
"""

import os
import requests
from typing import Any, Dict

VOCAB_URL = os.getenv("VOCAB_API_URL", "http://localhost:8001/v1/vocab")

def fetch_vocab() -> Dict[str, Any]:
    r = requests.get(VOCAB_URL, timeout=10)
    r.raise_for_status()
    return r.json()
