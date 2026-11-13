"""Flag spec paragraphs the estimate skipped that look like real scope.

A paragraph is flagged as a possible miss if:
  - it has NO matching estimate line item, AND
  - it carries at least one 'scope signal':
      capacity number (CFM/MBH/GPM/TON/HP/V/AMP/etc.)
      equipment tag (RTU-1, CH-1, AHU-2, etc.)
      schedule reference (terms like 'as scheduled', 'schedule indicates')
      explicit quantity (e.g. '(4) units', 'four units')

Output: data/missed_scope/<bid_slug>__possible_misses.csv

Usage:
    python find_missed_scope.py --bid "Sample Elementary"

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

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
LABELS_DIR = DATA_DIR / "labels"
SPECS_DIR = DATA_DIR / "specs"
OUT_DIR = DATA_DIR / "missed_scope"

CAPACITY_RE = re.compile(
    r"\b\d{1,6}(?:[,.]\d+)?\s*"
    r"(?:CFM|MBH|GPM|TONS?|HP|KW|MCA|MOCP|VAC|AMPS?|BTUH|MMBH|FLA|RLA|PSI|FPM)\b",
    re.IGNORECASE,
)
EQUIPMENT_TAG_RE = re.compile(
    r"\b(?:RTU|AHU|FCU|VAV|FPB|ERV|MAU|DOAS|EF|RF|SF|KEF|CH|CT|CWP|HWP|HX|CU|"
    r"VFD|MCC|VRF|WH)[-\s]?\d+[A-Z]?\b"
)
QUANTITY_PHRASE_RE = re.compile(
    r"\(\s*\d+\s*\)\s*[a-zA-Z]|\bfour\b|\bfive\b|\bsix\b|\bseven\b|\beight\b|"
    r"\bnine\b|\bten\b|\btwelve\b|\bfifteen\b|\btwenty\b",
    re.IGNORECASE,
)
SCHEDULE_REF_RE = re.compile(
    r"\b(?:as\s+scheduled|per\s+schedule|schedule\s+indicates|"
    r"refer\s+to\s+(?:the\s+)?schedule|equipment\s+schedule)\b",
    re.IGNORECASE,
)


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True)
    ap.add_argument("--include-context", action="store_true",
                    help="Also include project_specific_context paragraphs (not just unmatched)")
    args = ap.parse_args()

    labels_path = LABELS_DIR / f"{slug(args.bid)}__estimate_labels.jsonl"
    if not labels_path.exists():
        raise SystemExit(f"Labels file not found: {labels_path}\nRun apply_estimate_labels.py first.")

    labels = [json.loads(l) for l in labels_path.read_text(encoding="utf-8").split("\n") if l.strip()]

    # Build a paragraph_id -> text map by re-reading the spec JSONL.
    text_lookup: dict[str, dict] = {}
    bid_slug = slug(args.bid)
    for f in SPECS_DIR.glob("*.jsonl"):
        for ln in f.read_text(encoding="utf-8").split("\n"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if slug(r["bid"]) == bid_slug or bid_slug in slug(r["bid"]):
                text_lookup[r["paragraph_id"]] = r

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{slug(args.bid)}__possible_misses.csv"

    counts = {"flagged": 0, "examined": 0}
    interesting_labels = {"boilerplate_candidate"}
    if args.include_context:
        interesting_labels.add("project_specific_context")

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "division", "section", "section_title", "page",
            "signals", "confidence", "snippet", "paragraph_id",
        ])
        for lab in labels:
            if lab["label"] not in interesting_labels:
                continue
            counts["examined"] += 1
            para = text_lookup.get(lab["paragraph_id"])
            if not para:
                continue
            text = para["text"]
            signals = []
            if CAPACITY_RE.search(text):
                signals.append("capacity")
            if EQUIPMENT_TAG_RE.search(text):
                signals.append("equipment_tag")
            if QUANTITY_PHRASE_RE.search(text):
                signals.append("quantity")
            if SCHEDULE_REF_RE.search(text):
                signals.append("schedule_ref")
            if not signals:
                continue
            if len(signals) >= 2:
                confidence = "high"
            elif "capacity" in signals or "equipment_tag" in signals:
                confidence = "medium"
            else:
                confidence = "low"
            counts["flagged"] += 1
            w.writerow([
                lab["division"], lab["section"], lab.get("section_title", ""),
                lab.get("page", ""),
                "|".join(signals), confidence,
                text[:300].replace("\n", " "),
                lab["paragraph_id"],
            ])

    print(f"Examined {counts['examined']} unmatched/context paragraphs.")
    print(f"Flagged {counts['flagged']} as possible misses.")
    print(f"Wrote {out_path}")
    print(f"\nSort the CSV by 'confidence' descending in Excel and review the 'high' rows first.")


if __name__ == "__main__":
    main()
