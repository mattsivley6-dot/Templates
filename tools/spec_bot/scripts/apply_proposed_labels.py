"""Apply hand-picked (line item -> spec section) decisions as gold labels.

Use this instead of the CSV review step when you already know which spec
sections each estimate line item covers. The decisions live in a JSON file
you write (see examples/decisions.example.json): each key is a line-item
description substring, each value is a list of CSI sections to accept. An
empty list means "skip" (the line item is operational or not covered by the
spec, e.g. bond, contingency, temp labor).

Each accepted (line item, section) pair is written as a synthetic match on
the first paragraph of that section. The labeling logic from
apply_estimate_labels.py is then applied: matched paragraphs become
project_specific_gold; other paragraphs in the same section become
project_specific_context; Div 00 is boilerplate_gold; everything else is
boilerplate_candidate.

Usage:
    python apply_proposed_labels.py --bid "Sample Elementary" --decisions examples/decisions.example.json

Output:
    data/labels/<bid_slug>__estimate_labels.jsonl

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
SPECS_DIR = DATA_DIR / "specs"
ESTIMATES_DIR = DATA_DIR / "estimates"
LABELS_DIR = DATA_DIR / "labels"


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def load_decisions(path: Path) -> dict[str, list[str]]:
    """Load {line-item substring: [CSI sections]} from a JSON file.

    Keys starting with "_" are treated as comments and ignored. Order is kept:
    the first key that matches a line item wins.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit(f"Decisions file must hold a JSON object: {path}")
    out: dict[str, list[str]] = {}
    for key, secs in raw.items():
        if key.startswith("_"):
            continue
        if not isinstance(secs, list):
            raise SystemExit(f"Decision {key!r} must map to a list of sections.")
        out[key] = [str(s) for s in secs]
    return out


def load_line_items(bid: str) -> list[dict]:
    p = ESTIMATES_DIR / f"{slug(bid)}.jsonl"
    if not p.exists():
        raise SystemExit(f"Line items not found: {p}\nRun extract_estimate.py first.")
    return [
        json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()
    ]


def load_spec_paragraphs(bid: str) -> list[dict]:
    paras: list[dict] = []
    bid_slug = slug(bid)
    for f in SPECS_DIR.glob("*.jsonl"):
        for ln in f.read_text(encoding="utf-8").split("\n"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if slug(r["bid"]) == bid_slug or bid_slug in slug(r["bid"]):
                paras.append(r)
    return paras


def first_paragraph_in_section(paras: list[dict], section: str) -> dict | None:
    for p in paras:
        if p["section"] == section:
            return p
    return None


def apply(bid: str, decisions: dict[str, list[str]]) -> dict:
    line_items = load_line_items(bid)
    paras = load_spec_paragraphs(bid)
    bid_slug = slug(bid)

    # Build the matched_paragraphs map directly.
    matched_paragraphs: dict[str, list[dict]] = {}  # paragraph_id -> [line items]
    sections_with_matches: set[str] = set()
    unresolved_lis: list[str] = []
    missing_sections: list[str] = []

    for li in line_items:
        desc = li["description"]
        # Find first matching key in decisions.
        sections: list[str] | None = None
        for key, secs in decisions.items():
            if key.lower() in desc.lower():
                sections = secs
                break
        if sections is None:
            unresolved_lis.append(desc[:80])
            continue
        if not sections:
            continue  # explicit skip
        for section in sections:
            anchor = first_paragraph_in_section(paras, section)
            if anchor is None:
                missing_sections.append(f"{desc[:50]} -> {section}")
                continue
            pid = anchor["paragraph_id"]
            matched_paragraphs.setdefault(pid, []).append({
                "line_item_id": li["line_item_id"],
                "description": desc,
                "similarity": 1.0,  # confirmed by user
            })
            sections_with_matches.add(section)

    # Write the labels file.
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LABELS_DIR / f"{bid_slug}__estimate_labels.jsonl"
    counts = {"project_specific_gold": 0, "project_specific_context": 0,
              "boilerplate_candidate": 0, "boilerplate_gold": 0}

    with out_path.open("w", encoding="utf-8") as f:
        for p in paras:
            pid = p["paragraph_id"]
            section = p["section"]
            division = p["division"]
            if division == "00":
                label, source, matches = "boilerplate_gold", "div_00_rule", []
            elif pid in matched_paragraphs:
                label, source = "project_specific_gold", "estimate_match"
                matches = matched_paragraphs[pid]
            elif section in sections_with_matches:
                label, source, matches = "project_specific_context", "section_context", []
            else:
                label, source, matches = "boilerplate_candidate", "no_section_match", []
            counts[label] += 1
            f.write(json.dumps({
                "bid": p["bid"],
                "spec_pdf": p["spec_pdf"],
                "paragraph_id": pid,
                "section": section,
                "section_title": p.get("section_title", ""),
                "division": division,
                "page": p.get("page"),
                "label": label,
                "label_source": source,
                "matched_line_items": matches,
            }, ensure_ascii=False) + "\n")

    return {
        "bid": bid,
        "out_path": str(out_path),
        "counts": counts,
        "n_paragraphs": len(paras),
        "n_anchor_matches": len(matched_paragraphs),
        "n_sections_with_matches": len(sections_with_matches),
        "unresolved_line_items": unresolved_lis,
        "missing_sections": missing_sections,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bid", required=True, help="Bid name used when the spec and estimate were extracted")
    ap.add_argument("--decisions", type=Path, required=True,
                    help="JSON file mapping line-item substrings to lists of CSI sections")
    args = ap.parse_args()

    decisions = load_decisions(args.decisions)
    res = apply(args.bid, decisions)
    print(f"=== {res['bid']} ===")
    print(f"  Wrote {res['out_path']}")
    print(f"  Paragraphs:     {res['n_paragraphs']:>6,}")
    print(f"  Anchor matches: {res['n_anchor_matches']:>6}")
    print(f"  Sections w/ matches: {res['n_sections_with_matches']}")
    for k, v in res["counts"].items():
        pct = 100 * v / max(1, res['n_paragraphs'])
        print(f"    {k:30s} {v:>6,}  ({pct:.1f}%)")
    if res["unresolved_line_items"]:
        print(f"  UNRESOLVED line items (no key match in decisions file):")
        for d in res["unresolved_line_items"]:
            print(f"    - {d}")
    if res["missing_sections"]:
        print(f"  MISSING sections in spec (asked for but not found):")
        for m in res["missing_sections"]:
            print(f"    - {m}")
    print()


if __name__ == "__main__":
    main()
