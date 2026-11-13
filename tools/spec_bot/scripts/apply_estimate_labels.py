"""Read the reviewed matches CSV, apply gold labels to spec paragraphs.

Label scheme:
    project_specific_gold      paragraph matched by an accepted line item
    project_specific_context   paragraph in same section as a gold paragraph
    boilerplate_candidate      paragraph in section with zero matches
    boilerplate_gold           paragraph in Division 00 (procurement language)

Output:
    data/labels/<bid_slug>__estimate_labels.jsonl

The main classifier should treat these as overrides when computing its final
labels: gold labels win over similarity-based labels.

Usage:
    python apply_estimate_labels.py --bid "Sample Elementary" --reviewed-csv data/estimates/sample_elementary__matches.csv
    python apply_estimate_labels.py --bid "Sample Elementary" --auto-accept-threshold 0.55

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
SPECS_DIR = DATA_DIR / "specs"
OUT_DIR = DATA_DIR / "labels"


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def _iter_reviewed_rows(path: Path):
    """Iterate review rows from either CSV or XLSX.

    XLSX support so the user can review in Excel with formatting and save
    without exporting back to CSV. Both formats present the same columns.
    The formatted XLSX uses these columns: Rank, Accept (Y/N), Line Item,
    Qty, Sim, Section, Section Title, Spec Paragraph, Notes. We map those
    back to the CSV schema apply_estimate_labels expects.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(encoding="utf-8") as f:
            yield from csv.DictReader(f)
        return
    if suffix == ".xlsx":
        from openpyxl import load_workbook  # local import to avoid hard dep
        wb = load_workbook(path, data_only=True, read_only=True)
        ws = wb[wb.sheetnames[0]]
        rows_iter = ws.iter_rows(values_only=True)
        header = next(rows_iter, None)
        if header is None:
            return
        idx = {str(h).strip().lower(): i for i, h in enumerate(header) if h is not None}

        def col(row, *names):
            for n in names:
                if n in idx and idx[n] < len(row):
                    v = row[idx[n]]
                    if v is not None:
                        return str(v)
            return ""

        # Carry the current group's line_item_desc downward because the
        # formatted xlsx only writes it on the first row of each group.
        cur_desc = ""
        cur_qty = ""
        for row in rows_iter:
            if row is None or all(v is None for v in row):
                continue
            new_desc = col(row, "line item", "line_item_desc")
            new_qty = col(row, "qty")
            if new_desc:
                cur_desc = new_desc
            if new_qty:
                cur_qty = new_qty
            yield {
                "line_item_id": col(row, "line_item_id"),  # may be empty in xlsx
                "line_item_desc": cur_desc,
                "qty": cur_qty,
                "rank": col(row, "rank"),
                "spec_paragraph_id": col(row, "spec_paragraph_id"),
                "spec_section": col(row, "section", "spec_section"),
                "spec_section_title": col(row, "section title", "spec_section_title"),
                "similarity": col(row, "sim", "similarity"),
                "accept": col(row, "accept (y/n)", "accept"),
                "notes": col(row, "notes"),
            }
        return
    raise SystemExit(f"Unsupported review file extension: {suffix}")


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True)
    ap.add_argument("--reviewed-csv", type=Path,
                    help="CSV with Y/N in accept column. If omitted, auto-accept by threshold.")
    ap.add_argument("--auto-accept-threshold", type=float, default=0.55,
                    help="If no reviewed CSV, accept matches with similarity >= this.")
    args = ap.parse_args()

    paras = load_spec_paragraphs(args.bid)
    if not paras:
        raise SystemExit(f"No spec paragraphs found for bid {args.bid!r}.")

    # Load reviewed CSV (or fall back to the raw matches file with auto-accept).
    csv_path = args.reviewed_csv
    if csv_path is None:
        csv_path = DATA_DIR / "estimates" / f"{slug(args.bid)}__matches.csv"
    if not csv_path.exists():
        raise SystemExit(f"Matches CSV not found: {csv_path}")

    accepted_pairs: set[tuple[str, str]] = set()  # (line_item_id, paragraph_id)
    matched_paragraphs: dict[str, list[dict]] = {}  # paragraph_id -> list of line-item dicts

    rows_iter = _iter_reviewed_rows(csv_path)
    for row in rows_iter:
            accept_raw = (row.get("accept") or "").strip().upper()
            sim = float(row.get("similarity") or 0)
            if args.reviewed_csv is not None:
                if accept_raw not in ("Y", "YES", "1", "TRUE"):
                    continue
            else:
                if sim < args.auto_accept_threshold:
                    continue
            pid = row["spec_paragraph_id"]
            lid = row["line_item_id"]
            accepted_pairs.add((lid, pid))
            matched_paragraphs.setdefault(pid, []).append({
                "line_item_id": lid,
                "description": row["line_item_desc"],
                "similarity": sim,
            })

    # Compute section-level rollups.
    sections_with_matches: set[str] = set()
    for pid in matched_paragraphs:
        for p in paras:
            if p["paragraph_id"] == pid:
                sections_with_matches.add(p["section"])
                break

    # Build label records.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{slug(args.bid)}__estimate_labels.jsonl"
    counts = {"project_specific_gold": 0, "project_specific_context": 0,
              "boilerplate_candidate": 0, "boilerplate_gold": 0}

    with out_path.open("w", encoding="utf-8") as f:
        for p in paras:
            pid = p["paragraph_id"]
            section = p["section"]
            division = p["division"]
            if division == "00":
                label = "boilerplate_gold"
                source = "div_00_rule"
                matches = []
            elif pid in matched_paragraphs:
                label = "project_specific_gold"
                source = "estimate_match"
                matches = matched_paragraphs[pid]
            elif section in sections_with_matches:
                label = "project_specific_context"
                source = "section_context"
                matches = []
            else:
                label = "boilerplate_candidate"
                source = "no_section_match"
                matches = []
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

    print(f"Wrote {out_path}")
    print(f"  Accepted matches:           {len(accepted_pairs):>6}")
    print(f"  Paragraphs matched (uniq):  {len(matched_paragraphs):>6}")
    print(f"  Sections with matches:      {len(sections_with_matches):>6}")
    print(f"  Label counts:")
    for k, v in counts.items():
        print(f"    {k:30s} {v:>6}")


if __name__ == "__main__":
    main()
