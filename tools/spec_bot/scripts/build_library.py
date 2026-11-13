"""Score every spec paragraph and persist labels.

Label sources (in priority order):
  1. Rule       - paragraph contains a capacity value (CFM/MBH/GPM/etc.) or
                   an equipment tag (RTU-1, CH-2, AHU-3 ...). Always project_specific.
  2. Gold       - from data/labels/<bid>__estimate_labels.jsonl. Only bids
                   with a finished, reviewed priced estimate have these; they
                   are the only ground truth we trust.
  3. Repetition - paragraph appears nearly verbatim in 2+ OTHER bids. Strong
                   signal of boilerplate regardless of who wrote it.
  4. Ambiguous  - default when none of the above apply.

The proposal-based attention scoring was removed: sub/vendor proposals are too
noisy to be a reliable label source. Cross-bid repetition + gold labels carry
the signal now.

Output:
  data/library.sqlite - paragraphs table with scores and labels

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
SPECS_DIR = DATA_DIR / "specs"
LABELS_DIR = DATA_DIR / "labels"
DB_PATH = DATA_DIR / "library.sqlite"

EQUIPMENT_TAG_PREFIXES = (
    "RTU", "AHU", "FCU", "VAV", "FPB", "ERV", "MAU", "DOAS",
    "EF", "RF", "SF", "KEF", "MUA", "UH",
    "CH", "CT", "CWP", "HWP", "HX", "EXP", "EXT",
    "CU", "CCU", "VRF", "ODU", "IDU", "VFD", "MCC", "ATS", "GEN",
)
EQUIPMENT_TAG_RE = re.compile(
    r"\b(?P<prefix>"
    + "|".join(sorted(EQUIPMENT_TAG_PREFIXES, key=len, reverse=True))
    + r")[-\s]?(?P<num>\d+[A-Z]?)\b"
)

CAPACITY_UNIT_RE = re.compile(
    r"\d+(?:[,.]\d+)?\s*"
    r"(?:CFM|MBH|GPM|TONS?|HP|KW|MCA|MOCP|VAC|VDC|AMPS?|FLA|RLA|PSI|FPM|RPM|"
    r"BTUH|BTU/H|MMBH|SCFM|ACFM|KW/TON|EER|IEER|SEER|COP)\b",
    re.IGNORECASE,
)

PREFIX_LEN = 60


def normalize_for_repetition(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:PREFIX_LEN]


def load_specs() -> list[dict]:
    rows: list[dict] = []
    for f in sorted(SPECS_DIR.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").split("\n"):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_gold_labels() -> dict[tuple[str, str], dict]:
    """Return {(bid_slug, paragraph_id) -> label record}.

    Bid slug normalizes the bid name so a label file written for
    'Sample Elementary' matches paragraphs whose bid field is
    'Sample Elementary'. Use the same bid name in every step.
    """
    def slug(s: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()

    out: dict[tuple[str, str], dict] = {}
    for f in sorted(LABELS_DIR.glob("*__estimate_labels.jsonl")):
        for line in f.read_text(encoding="utf-8").split("\n"):
            if not line.strip():
                continue
            r = json.loads(line)
            key = (slug(r["bid"]), r["paragraph_id"])
            out[key] = r
    return out


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE paragraphs (
            id INTEGER PRIMARY KEY,
            bid TEXT NOT NULL,
            spec_pdf TEXT,
            division TEXT,
            section TEXT,
            section_title TEXT,
            paragraph_id TEXT,
            page INTEGER,
            text TEXT,
            char_count INTEGER,
            normalized_prefix TEXT,
            has_capacity INTEGER,
            has_tag INTEGER,
            repetition_score INTEGER,
            gold_label TEXT,         -- raw label from labels file, if any
            gold_source TEXT,        -- raw source from labels file, if any
            label TEXT,              -- final 3-class label
            label_source TEXT,       -- which signal won
            confidence REAL
        )
    """)
    conn.execute("CREATE INDEX idx_section ON paragraphs(section)")
    conn.execute("CREATE INDEX idx_bid ON paragraphs(bid)")
    conn.execute("CREATE INDEX idx_label ON paragraphs(label)")
    return conn


def assign_label(
    has_capacity: int,
    has_tag: int,
    gold: dict | None,
    repetition_score: int,
) -> tuple[str, str, float]:
    """Return (label, label_source, confidence)."""
    # 1. Paragraph-intrinsic rule (always wins)
    if has_capacity or has_tag:
        return ("project_specific", "rule", 0.95)

    # 2. Gold label from estimate review
    if gold:
        g = gold["label"]
        if g in ("project_specific_gold", "project_specific_context"):
            conf = 0.95 if g == "project_specific_gold" else 0.85
            return ("project_specific", f"gold:{g}", conf)
        if g == "boilerplate_gold":
            return ("boilerplate", "gold:boilerplate_gold", 0.95)
        # boilerplate_candidate from gold = "no estimate match", still ambiguous
        # unless repetition agrees.
        if g == "boilerplate_candidate" and repetition_score >= 2:
            return ("boilerplate", "gold+repetition", 0.9)
        if g == "boilerplate_candidate":
            return ("ambiguous", "gold:no_match_no_repetition", 0.3)

    # 3. Cross-bid repetition (works for bids without gold labels)
    if repetition_score >= 2:
        return ("boilerplate", "repetition", min(0.9, 0.5 + 0.1 * repetition_score))

    return ("ambiguous", "tbd", 0.0)


def main() -> None:
    specs = load_specs()
    gold = load_gold_labels()
    print(f"Loaded {len(specs):,} spec paragraphs across {len({s['bid'] for s in specs})} bids")
    print(f"Loaded {len(gold):,} gold label records from {len(list(LABELS_DIR.glob('*.jsonl')))} bid files")

    for s in specs:
        s["_norm"] = normalize_for_repetition(s["text"])

    # Repetition: distinct bids per (section, normalized_prefix).
    bid_set_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    for s in specs:
        bid_set_by_key[(s["section"], s["_norm"])].add(s["bid"])

    def slug(x: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "_", x).strip("_").lower()

    conn = init_db(DB_PATH)
    cur = conn.cursor()
    label_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()

    for s in specs:
        text = s["text"]
        has_capacity = 1 if CAPACITY_UNIT_RE.search(text) else 0
        has_tag = 1 if EQUIPMENT_TAG_RE.search(text) else 0

        # Repetition = # OTHER bids with this same (section, prefix).
        same_key_bids = bid_set_by_key.get((s["section"], s["_norm"]), set())
        repetition_score = max(0, len(same_key_bids) - 1)

        # Gold label lookup.
        g = gold.get((slug(s["bid"]), s["paragraph_id"]))

        label, source, conf = assign_label(has_capacity, has_tag, g, repetition_score)
        label_counter[label] += 1
        source_counter[source] += 1

        cur.execute(
            """INSERT INTO paragraphs (bid, spec_pdf, division, section, section_title,
            paragraph_id, page, text, char_count, normalized_prefix,
            has_capacity, has_tag, repetition_score,
            gold_label, gold_source, label, label_source, confidence)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                s["bid"], s["spec_pdf"], s["division"], s["section"], s["section_title"],
                s["paragraph_id"], s["page"], text, s["char_count"], s["_norm"],
                has_capacity, has_tag, repetition_score,
                g["label"] if g else None,
                g["label_source"] if g else None,
                label, source, conf,
            ),
        )

    conn.commit()
    conn.close()

    total = len(specs)
    print(f"\nLabel distribution (all {total:,} paragraphs):")
    for lab, n in label_counter.most_common():
        print(f"  {lab:18s}: {n:>6,} ({100*n/total:.1f}%)")
    print(f"\nLabel source breakdown:")
    for src, n in source_counter.most_common():
        print(f"  {src:30s}: {n:>6,}")

    # Per-bid breakdown for the bids that have gold labels.
    print(f"\nPer-bid breakdown:")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT bid, label, COUNT(*)
        FROM paragraphs GROUP BY bid, label ORDER BY bid, label
    """).fetchall()
    by_bid: dict[str, dict[str, int]] = defaultdict(dict)
    for bid, label, n in rows:
        by_bid[bid][label] = n
    for bid, counts in by_bid.items():
        total_bid = sum(counts.values())
        line = f"  {bid[:60]:60s}  total={total_bid:>5}  "
        for lab in ("project_specific", "ambiguous", "boilerplate"):
            n = counts.get(lab, 0)
            line += f"{lab[:4]}={n:>5}({100*n/total_bid:>4.1f}%)  "
        print(line)
    conn.close()
    print(f"\nWrote {DB_PATH}")


if __name__ == "__main__":
    main()
