"""
src/preprocess/text.py
Foco é limpeza, normalização e lematização (PT-BR).
"""

import re
import nltk
import spacy
from typing import Optional
import logging

logger = logging.getLogger("preprocess.text")

class Preprocessor:
    def __init__(self, spacy_model: str):
        self._ensure_nltk()
        self.nlp = spacy.load(spacy_model)
        self.stopwords = set(nltk.corpus.stopwords.words("portuguese"))

    def _ensure_nltk(self):
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")

    def preprocess(self, text: str) -> str:
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"[@#]\w+", " ", text)

        text = text.lower().strip()

        doc = self.nlp(text)
        tokens = []
        for tok in doc:
            if tok.is_punct or tok.is_space:
                continue
            lemma = tok.lemma_.strip()
            if not lemma:
                continue
            if lemma in self.stopwords:
                continue
            tokens.append(lemma)

        return " ".join(tokens)
