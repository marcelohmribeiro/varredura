# src/storage/firestore.py
from datetime import datetime, timedelta
from typing import List, Tuple
from google.cloud import firestore

def get_client():
    return firestore.Client()  # usa GOOGLE_APPLICATION_CREDENTIALS

def _doc_id(platform: str, source_id: str, comment_id: str) -> str:
    return f"{platform}:{source_id}:{comment_id}"

def delete_older_than(client, collection: str, days: int) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    q = client.collection(collection).where("ingestedAt", "<", cutoff).limit(500)
    deleted = 0
    while True:
        docs = list(q.stream())
        if not docs:
            break
        batch = client.batch()
        for d in docs:
            batch.delete(d.reference)
        batch.commit()
        deleted += len(docs)
        if len(docs) < 500:
            break
    return deleted

def save_records(client, collection: str, records: List) -> Tuple[int, int]:
    """Upsert por doc_id determinístico. Retorna (criados, atualizados=0)."""
    batch = client.batch()
    ops_in_batch = 0
    for r in records:
        try:
            doc = r.model_dump()
        except AttributeError:
            doc = r.__dict__ if hasattr(r, "__dict__") else dict(r)
        doc["ingestedAt"] = doc.get("ingestedAt") or datetime.utcnow()
        ref = client.collection(collection).document(
            _doc_id(doc["platform"], doc["source_id"], doc["comment_id"])
        )
        batch.set(ref, doc, merge=True)
        ops_in_batch += 1
        if ops_in_batch >= 450:
            batch.commit()
            batch = client.batch()
            ops_in_batch = 0
    if ops_in_batch:
        batch.commit()
    return (len(records), 0)
