"""
src/common/config.py
"""

from dataclasses import dataclass
from typing import Any, Dict
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv
load_dotenv()

SETTINGS_PATH = Path(__file__).parents[2] / "configs" / "settings.yaml"

@dataclass
class Settings:
    ingestion: Dict[str, Any]
    nlp: Dict[str, Any]
    thresholds: Dict[str, float]
    services: Dict[str, Any]
    storage: Dict[str, Any]

def load_settings() -> Settings:
    """
    Lê o settings.yaml e retorna um objeto Settings.
    """
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return Settings(
        ingestion=raw.get("ingestion", {}),
        nlp=raw.get("nlp", {}),
        thresholds=raw.get("thresholds", {}),
        services=raw.get("services", {}),
        storage=raw.get("storage", {}),
    )

def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)
