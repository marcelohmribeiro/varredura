# src/tools/firestore_to_bq.py
from datetime import datetime
from typing import List, Dict, Optional
import os

from google.cloud import firestore, bigquery

DATASET = "bd_adultzacao"
DATASET_LOCATION = "southamerica-east1"  
TABLE = "comments"                       
DEDUP_VIEW = "v_comments_dedup"          
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")  

SCHEMA = [
    bigquery.SchemaField("doc_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("platform", "STRING"),
    bigquery.SchemaField("source_id", "STRING"),
    bigquery.SchemaField("comment_id", "STRING"),
    bigquery.SchemaField("author", "STRING"),
    bigquery.SchemaField("text", "STRING"),
    bigquery.SchemaField("preprocessed", "STRING"),
    bigquery.SchemaField("rule_hits", "STRING", description="concat '|'"),
    bigquery.SchemaField("semantic_score", "FLOAT"),
    bigquery.SchemaField("perspective_sexual", "FLOAT"),
    bigquery.SchemaField("final_score", "FLOAT"),
    bigquery.SchemaField("classification", "STRING"),
    bigquery.SchemaField("ingestedAt", "TIMESTAMP"),
]

def _ensure_dataset(bq: bigquery.Client):
    ds_id = f"{bq.project}.{DATASET}"
    try:
        bq.get_dataset(ds_id)
    except Exception:
        ds = bigquery.Dataset(ds_id)
        ds.location = DATASET_LOCATION
        bq.create_dataset(ds, exists_ok=True)

def _ensure_target_table(bq: bigquery.Client):
    table_id = f"{bq.project}.{DATASET}.{TABLE}"
    try:
        bq.get_table(table_id)
    except Exception:
        table = bigquery.Table(table_id, schema=SCHEMA)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="ingestedAt",
        )
        bq.create_table(table)

def _to_rfc3339(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    if dt.tzinfo:
        return dt.astimezone().isoformat()
    return dt.isoformat() + "Z"

def _rows_from_firestore(source_id: str) -> List[Dict]:
    fs = firestore.Client()
    rows: List[Dict] = []

    query = fs.collection("comments").where(
        filter=firestore.FieldFilter("source_id", "==", source_id)
    )
    for snap in query.stream():
        d = snap.to_dict()

        rule_hits_list = d.get("rule_hits", [])
        if isinstance(rule_hits_list, list):
            rule_hits_str = "|".join(map(str, rule_hits_list))
        else:
            rule_hits_str = str(rule_hits_list) if rule_hits_list is not None else ""

        def _float_or_none(x):
            try:
                return float(x) if x is not None else None
            except Exception:
                return None

        semantic_score = _float_or_none(d.get("semantic_score"))
        perspective_sexual = _float_or_none(d.get("perspective_sexual"))
        final_score = _float_or_none(d.get("final_score"))

        ing = d.get("ingestedAt")
        if isinstance(ing, datetime):
            ing_str = _to_rfc3339(ing)
        else:
            ing_str = ing if isinstance(ing, str) else _to_rfc3339(datetime.utcnow())

        rows.append({
            "doc_id": str(snap.id),
            "platform": str(d.get("platform") or ""),
            "source_id": str(d.get("source_id") or ""),
            "comment_id": str(d.get("comment_id") or ""),
            "author": str(d.get("author") or ""),
            "text": str(d.get("text") or ""),
            "preprocessed": str(d.get("preprocessed") or ""),
            "rule_hits": rule_hits_str,
            "semantic_score": semantic_score,
            "perspective_sexual": perspective_sexual,
            "final_score": final_score,
            "classification": str(d.get("classification") or ""),
            "ingestedAt": ing_str,
        })

    return rows

def _create_or_replace_dedup_view(bq: bigquery.Client):
    table_id = f"{bq.project}.{DATASET}.{TABLE}"
    view_id = f"{bq.project}.{DATASET}.{DEDUP_VIEW}"

    sql = f"""
    CREATE OR REPLACE VIEW `{view_id}` AS
    SELECT
      doc_id,
      platform,
      source_id,
      comment_id,
      author,
      text,
      preprocessed,
      rule_hits,
      semantic_score,
      perspective_sexual,
      final_score,
      classification,
      ingestedAt
    FROM (
      SELECT
        t.*,
        ROW_NUMBER() OVER (PARTITION BY doc_id ORDER BY ingestedAt DESC) AS rn
      FROM `{table_id}` t
    )
    WHERE rn = 1
    """
    bq.query(sql, location=DATASET_LOCATION).result()
    print(f"[OK] View de deduplicação atualizada: {view_id}")

def sync(source_id: str):
    bq = bigquery.Client()

    # 1) Dataset e Tabela
    _ensure_dataset(bq)
    _ensure_target_table(bq)

    # 2) Coleta os documentos do Firestore para esse source_id (YouTube ou Reddit)
    rows = _rows_from_firestore(source_id)
    if not rows:
        print(f"[WARN] Nenhum documento encontrado no Firestore para source_id={source_id}.")
        return

    # 3) Load APPEND direto para a tabela destino (SEM DML)
    table_id = f"{bq.project}.{DATASET}.{TABLE}"
    load_cfg = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND, 
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    bq.load_table_from_json(
        rows,
        destination=table_id,
        job_config=load_cfg,
        location=DATASET_LOCATION
    ).result()

    # 4) Atualiza/Cria a VIEW de deduplicação
    _create_or_replace_dedup_view(bq)

    print(f"[OK] BigQuery (append) atualizado em `{table_id}` e view `{DEDUP_VIEW}` pronta para consumo.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--video-id",
        required=True,
        help="Use o mesmo valor de source_id gravado no Firestore (YouTube videoId OU Reddit submissionId base36)."
    )
    args = ap.parse_args()
    sync(args.video_id)
