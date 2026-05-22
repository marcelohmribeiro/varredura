"""
src/rules/filter.py
"""

import re
from typing import List, Dict

def compile_regex_patterns(regex_map: Dict[str, str]) -> Dict[str, re.Pattern]:
    compiled: Dict[str, re.Pattern] = {}
    for name, pattern in regex_map.items():
        compiled[name] = re.compile(pattern, flags=re.IGNORECASE)
    return compiled

def apply_rules(
    text_original: str,
    text_preprocessed: str,
    keywords_explicit: List[str],
    regex_compiled: Dict[str, re.Pattern]
) -> List[str]:

    hits: List[str] = []
    haystacks = [text_original.lower(), text_preprocessed.lower()]

    # Palavras-chave explícitas
    for kw in keywords_explicit:
        if any(kw.lower() in h for h in haystacks):
            hits.append(f"KW:{kw}")

    # Regex (ex.: idade 10-17)
    for name, pattern in regex_compiled.items():
        if pattern.search(text_original) or pattern.search(text_preprocessed):
            hits.append(f"REGEX:{name}")

    return hits
