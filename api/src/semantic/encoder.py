"""
src/semantic/encoder.py
Calcula a similaridade semântica entre o comentário e exemplos suspeitos.
"""

from typing import List
from sentence_transformers import SentenceTransformer, util

class SemanticEncoder:
    def __init__(self, model_name: str, suspect_examples: List[str]):
        # Carrega o modelo (multilíngue recomendado)
        self.model = SentenceTransformer(model_name)
        # Pré-codifica os exemplos para acelerar runtime
        self.examples = suspect_examples
        self.examples_emb = self.model.encode(
            suspect_examples, convert_to_tensor=True, normalize_embeddings=True
        )

    def score(self, preprocessed_text: str) -> float:
        if not preprocessed_text.strip():
            return 0.0
        emb = self.model.encode([preprocessed_text], convert_to_tensor=True, normalize_embeddings=True)
        cos = util.cos_sim(emb, self.examples_emb)  # shape [1, N]
        return float(cos.max().item())
