# src/tools/smoke_test.py
import logging
from typing import List
from dataclasses import asdict

from common.config import load_settings
from common.models import CommentRecord
from services.vocab_client import fetch_vocab
from preprocess.text import Preprocessor
from rules.filter import compile_regex_patterns, apply_rules
from semantic.encoder import SemanticEncoder
from classify.aggregator import aggregate_risk
from storage.firestore import get_client as fs_client, save_records as fs_save, delete_older_than as fs_ttl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("smoke")

def run(persist: bool = False) -> List[CommentRecord]:
    settings = load_settings()
    nlp_cfg = settings.nlp
    thr = settings.thresholds
    svc = settings.services
    storage = settings.storage

    vocab = fetch_vocab()
    keywords = vocab.get("keywords_explicit", [])
    examples = vocab.get("examples_implicit", [])
    regex_map = vocab.get("regex_patterns", {})
    regex_compiled = compile_regex_patterns(regex_map)
    log.info("Vocab OK. KW=%d | EX=%d | Regex=%d", len(keywords), len(examples), len(regex_compiled))

    # ---- NLP + Encoder semântico
    pre = Preprocessor(nlp_cfg.get("spacy_model", "pt_core_news_sm"))
    enc = SemanticEncoder("paraphrase-multilingual-MiniLM-L12-v2", examples)

    # ---- Apenas dados de teste (mock) para avaliação de como a anlise de dados esta sendo feita 
    # e se esta pegando corretamente comentarios maliciosos, como não consegui pela api encontrar
    # decidi inserir na mão inicialmente 
    raw = [
        {
            "platform": "youtube",
            "source_id": "TEST_VIDEO",
            "comment_id": "yt1",
            "author": "userA",
            "text": "Ela tem carinha de bebê, nem parece ter a idade que diz.",
        },
        {
            "platform": "reddit",
            "source_id": "TEST_POST",
            "comment_id": "rd1",
            "author": "userB",
            "text": "Acabou de virar mulher, mal saiu da escola...",
        },
        {
            "platform": "youtube",
            "source_id": "TEST_VIDEO",
            "comment_id": "yt2",
            "author": "userC",
            "text": "Vídeo ótimo! parabéns pelo conteúdo.",
        },
    ]

    results: List[CommentRecord] = []
    for item in raw:
        text = item["text"]
        preprocessed = pre.preprocess(text)

        hits = apply_rules(text, preprocessed, keywords, regex_compiled)
        sem_score = enc.score(preprocessed)

        perspective_score = None

        final_score, label = aggregate_risk(
            rule_hits=hits,
            semantic_score=sem_score,
            thresholds=thr,
            perspective_sexual=perspective_score,
            perspective_weight=float(svc.get("perspective_weight", 0.4)),
        )

        rec = CommentRecord(
            platform=item["platform"],
            source_id=item["source_id"],
            comment_id=item["comment_id"],
            author=item["author"],
            text=text,
            preprocessed=preprocessed,
            rule_hits=hits,
            semantic_score=sem_score,
            perspective_sexual=perspective_score,
            final_score=final_score,
            classification=label,
            extras={}
        )
        results.append(rec)

    if persist:
        client = fs_client()
        try:
            ttl_days = int(settings.storage.get("ttl_days", 30))
            deleted = fs_ttl(client, "comments", days=ttl_days)
            log.info("[Firestore] TTL por código: removidos %d docs antigos (ttl_days=%d).", deleted, ttl_days)
        except Exception as e:
            log.warning("[Firestore] TTL falhou (ignorado no teste): %s", e)

        created, _ = fs_save(client, "comments", results)
        log.info("[Firestore] Gravados %d documentos (upsert).", created)

    sus = sum(1 for r in results if r.classification == "suspeito")
    aten = sum(1 for r in results if r.classification == "atencao")
    ok = sum(1 for r in results if r.classification == "ok")
    log.info("Resumo (SMOKE) → suspeito=%d | atencao=%d | ok=%d", sus, aten, ok)

    # Mostra cada classificação
    for r in results:
        log.info("ID=%s | platform=%s | label=%s | score=%.3f | hits=%s",
                 r.comment_id, r.platform, r.classification, r.final_score, "|".join(r.rule_hits))

    return results

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--persist", action="store_true", help="Salvar os mocks no Firestore para testar integração")
    args = ap.parse_args()
    run(persist=args.persist)
