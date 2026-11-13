"""For each estimate line item, find the top-N most similar spec paragraphs
using sentence-transformer embeddings. Outputs a CSV for manual review.

The user opens the CSV in Excel, puts Y / N in the 'accept' column, saves.
That reviewed CSV feeds apply_estimate_labels.py.

Usage:
    python match_lineitems_to_spec.py --bid "Sample Elementary"
    python match_lineitems_to_spec.py --bid "Sample Elementary" --top-n 3 --threshold 0.35

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    raise SystemExit(
        "sentence-transformers not installed. Run:\n"
        "  pip install sentence-transformers numpy\n"
        "First run downloads the all-MiniLM-L6-v2 model (~80MB) to your local cache."
    )

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
SPECS_DIR = DATA_DIR / "specs"
ESTIMATES_DIR = DATA_DIR / "estimates"
OUT_DIR = DATA_DIR / "estimates"

MODEL_NAME = "all-MiniLM-L6-v2"


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def load_line_items(bid: str) -> list[dict]:
    p = ESTIMATES_DIR / f"{slug(bid)}.jsonl"
    if not p.exists():
        raise SystemExit(f"Line items not found: {p}\nRun extract_estimate.py first.")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_spec_paragraphs(bid: str) -> list[dict]:
    """Find all spec JSONL files that belong to this bid and concatenate."""
    paras: list[dict] = []
    bid_slug = slug(bid)
    for f in SPECS_DIR.glob("*.jsonl"):
        # Match if the file slug starts with the bid slug, OR the bid field matches.
        for ln in f.read_text(encoding="utf-8").split("\n"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if slug(r["bid"]) == bid_slug or bid_slug in slug(r["bid"]):
                paras.append(r)
    if not paras:
        raise SystemExit(
            f"No spec paragraphs found for bid {bid!r}.\n"
            f"Check that data/specs/ has a file containing bid={bid!r}."
        )
    return paras


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True)
    ap.add_argument("--top-n", type=int, default=3, help="Top N spec paragraphs per line item")
    ap.add_argument("--threshold", type=float, default=0.30,
                    help="Min cosine similarity to surface a match (still emitted, just flagged low-conf)")
    args = ap.parse_args()

    items = load_line_items(args.bid)
    paras = load_spec_paragraphs(args.bid)
    print(f"Loaded {len(items)} line items, {len(paras)} spec paragraphs.")

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding spec paragraphs...")
    para_texts = [(p["text"][:512]) for p in paras]
    para_emb = model.encode(para_texts, show_progress_bar=True, batch_size=64, convert_to_numpy=True, normalize_embeddings=True)

    print("Embedding line items...")
    item_texts = [it["description"][:512] for it in items]
    item_emb = model.encode(item_texts, show_progress_bar=True, batch_size=64, convert_to_numpy=True, normalize_embeddings=True)

    # Cosine similarity = dot product on normalized vectors.
    sims = item_emb @ para_emb.T  # shape (n_items, n_paras)

    out_path = OUT_DIR / f"{slug(args.bid)}__matches.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "line_item_id", "line_item_desc", "qty", "unit", "total_$",
            "rank", "spec_paragraph_id", "spec_section", "spec_section_title",
            "similarity", "spec_paragraph_text", "accept", "notes",
        ])
        for i, it in enumerate(items):
            top_idx = np.argsort(-sims[i])[: args.top_n]
            for rank, pi in enumerate(top_idx, start=1):
                p = paras[int(pi)]
                score = float(sims[i, pi])
                w.writerow([
                    it["line_item_id"],
                    it["description"][:200],
                    it.get("quantity") or "",
                    it.get("unit") or "",
                    it.get("total") or "",
                    rank,
                    p["paragraph_id"],
                    p["section"],
                    p.get("section_title", ""),
                    round(score, 3),
                    p["text"][:300].replace("\n", " "),
                    "",  # accept (user fills in)
                    "",  # notes
                ])

    n_above = int((sims.max(axis=1) >= args.threshold).sum())
    print(f"\nWrote {out_path}")
    print(f"Line items with at least one match above {args.threshold}: {n_above} / {len(items)}")
    print(f"\nNext: open the CSV in Excel, put Y in 'accept' for good matches, save,")
    print(f"      then run apply_estimate_labels.py --bid {args.bid!r} --reviewed-csv {out_path}")


if __name__ == "__main__":
    main()
