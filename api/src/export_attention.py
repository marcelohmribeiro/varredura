"""
src/export_attention.py
Filtra apenas os comentários classificados como 'atencao',
salva em CSV (data/out) e imprime um resumo no console.
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import List
from main import run_pipeline  # reutiliza o pipeline completo

def to_row(rec) -> dict:
    like_count = rec.extras.get("likeCount", 0) if rec.extras else 0
    published_at = rec.extras.get("publishedAt") if rec.extras else None
    return {
        "platform": rec.platform,
        "source_id": rec.source_id,
        "comment_id": rec.comment_id,
        "author": rec.author or "",
        "text": (rec.text or "").replace("\n", " ").strip(),
        "preprocessed": rec.preprocessed,
        "rule_hits": "|".join(rec.rule_hits),
        "semantic_score": rec.semantic_score,
        "perspective_sexual": rec.perspective_sexual if rec.perspective_sexual is not None else "",
        "final_score": rec.final_score,
        "classification": rec.classification,
        "likeCount": like_count,
        "publishedAt": published_at,
    }

def main():
    parser = argparse.ArgumentParser(description="Exporta somente comentários 'atenção' para CSV.")
    parser.add_argument("--video-id", required=True, help="ID do vídeo do YouTube")
    parser.add_argument("--limit", type=int, default=50, help="Quantos imprimir no console (apenas resumo)")
    args = parser.parse_args()

    results: List = run_pipeline(video_id=args.video_id, persist=False)

    # Filtra só 'atenção' e ordena pelos maiores scores
    attn = [r for r in results if r.classification == "atencao"]
    attn.sort(key=lambda r: r.final_score, reverse=True)

    out_dir = Path(__file__).resolve().parents[1] / "data" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"{args.video_id}-attention-{ts}.csv"

    fieldnames = [
        "platform","source_id","comment_id","author","text","preprocessed",
        "rule_hits","semantic_score","perspective_sexual","final_score",
        "classification","likeCount","publishedAt"
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in attn:
            writer.writerow(to_row(r))

    print(f"✅ Encontrados {len(attn)} comentários classificados como 'atenção'.")
    print(f"📄 CSV salvo em: {out_path}")
    print("\nTop (console):")
    for i, r in enumerate(attn[:args.limit], start=1):
        hits = ",".join(r.rule_hits) if r.rule_hits else "-"
        text_preview = (r.text or "").replace("\n", " ")
        if len(text_preview) > 160:
            text_preview = text_preview[:160] + "..."
        print(f"{i:02d}) score={r.final_score:.2f}  sem={r.semantic_score:.2f}  hits={hits}")
        print(f"    author={r.author or '-'} | {text_preview}")

if __name__ == "__main__":
    main()
