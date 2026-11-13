"""Emit a takeoff checklist .xlsx for one bid in the library.

Usage:
    python to_excel.py --bid "Sample Elementary"
    python to_excel.py --bid "Sample"           # substring match
    python to_excel.py --bid "Sample Elementary" --divisions 01,22,23,26

Output: outputs/<bid_slug>_takeoff_checklist.xlsx

The data folder defaults to ./data and the output folder to ./outputs in the
tool folder. Set the SPEC_BOT_DATA and SPEC_BOT_OUTPUTS environment variables
to use different ones.

Layout:
  Tab 1: "Summary"          - counts by division + label, top sections
  Tab 2: "Project-Specific" - paragraphs estimator MUST read
  Tab 3: "Ambiguous"        - paragraphs to scan / triage
  Tab 4: "Boilerplate"      - paragraphs estimator can skip (hidden by default)
  Tab 5: "All"              - everything, for cross-checking
"""
from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
DB_PATH = DATA_DIR / "library.sqlite"
OUT_DIR = Path(os.environ.get("SPEC_BOT_OUTPUTS") or SPEC_BOT / "outputs")

# Light fills so the workbook is readable without being garish.
FILL_PROJECT = PatternFill("solid", fgColor="FFF2CC")   # warm yellow
FILL_AMBIGUOUS = PatternFill("solid", fgColor="EAF1F8")  # light blue
FILL_BOILERPLATE = PatternFill("solid", fgColor="E8E8E8")  # light gray
FILL_HEADER = PatternFill("solid", fgColor="305496")
HEADER_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

COLUMNS = [
    ("Division", 8),
    ("Section", 10),
    ("Section Title", 32),
    ("Page", 6),
    ("Paragraph", 14),
    ("Classification", 16),
    ("Confidence", 10),
    ("Source", 28),
    ("Has Cap", 8),
    ("Has Tag", 8),
    ("Repetition", 10),
    ("Text", 80),
    ("Estimator Notes", 22),
]


def write_header(ws, headers: list[tuple[str, int]]) -> None:
    for ci, (name, width) in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=ci, value=name)
        cell.font = HEADER_FONT
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "D2"


def fill_for(label: str) -> PatternFill | None:
    return {
        "project_specific": FILL_PROJECT,
        "ambiguous": FILL_AMBIGUOUS,
        "boilerplate": FILL_BOILERPLATE,
    }.get(label)


def write_paragraphs(ws, rows: list[tuple]) -> None:
    write_header(ws, COLUMNS)
    for ri, row in enumerate(rows, start=2):
        (
            division, section, section_title, page, paragraph_id,
            label, confidence, label_source,
            has_capacity, has_tag, repetition_score, text,
        ) = row
        values = [
            division,
            section,
            section_title or "",
            page,
            paragraph_id,
            label,
            f"{confidence:.2f}",
            label_source,
            "Y" if has_capacity else "",
            "Y" if has_tag else "",
            repetition_score,
            text,
            "",
        ]
        fill = fill_for(label)
        for ci, val in enumerate(values, start=1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.alignment = WRAP
            c.border = BORDER
            if fill:
                c.fill = fill
        ws.row_dimensions[ri].height = 32  # roomy for wrapped text


def write_summary(ws, bid: str, all_rows: list[tuple]) -> None:
    ws.title = "Summary"
    ws["A1"] = f"Takeoff Checklist - {bid}"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:E1")

    label_counts = Counter(r[5] for r in all_rows)
    division_counts = Counter(r[0] for r in all_rows)

    ws["A3"] = "Label distribution"
    ws["A3"].font = Font(bold=True)
    for i, (label, n) in enumerate(label_counts.most_common(), start=4):
        ws.cell(row=i, column=1, value=label)
        ws.cell(row=i, column=2, value=n)
        ws.cell(row=i, column=3, value=f"{100*n/max(1,len(all_rows)):.1f}%")
        fill = fill_for(label)
        if fill:
            for c in (1, 2, 3):
                ws.cell(row=i, column=c).fill = fill

    next_row = 4 + len(label_counts) + 2
    ws.cell(row=next_row, column=1, value="Division breakdown").font = Font(bold=True)
    div_start = next_row + 1
    for i, (div, n) in enumerate(sorted(division_counts.items()), start=div_start):
        # Count by label within this division
        ps = sum(1 for r in all_rows if r[0] == div and r[5] == "project_specific")
        amb = sum(1 for r in all_rows if r[0] == div and r[5] == "ambiguous")
        bp = sum(1 for r in all_rows if r[0] == div and r[5] == "boilerplate")
        ws.cell(row=i, column=1, value=f"Div {div}")
        ws.cell(row=i, column=2, value=n)
        ws.cell(row=i, column=3, value=ps).fill = FILL_PROJECT
        ws.cell(row=i, column=4, value=amb).fill = FILL_AMBIGUOUS
        ws.cell(row=i, column=5, value=bp).fill = FILL_BOILERPLATE
    # Column header for the division table
    hdr_row = div_start - 1
    for col, h in enumerate(["Div", "Total", "Specific", "Ambig.", "Boiler"], start=1):
        c = ws.cell(row=hdr_row, column=col, value=h)
        c.font = Font(bold=True)
    for w, col in zip([12, 10, 12, 10, 10], "ABCDE"):
        ws.column_dimensions[col].width = w


def find_bid(conn: sqlite3.Connection, search: str) -> str:
    rows = conn.execute(
        "SELECT DISTINCT bid FROM paragraphs WHERE bid LIKE ?",
        (f"%{search}%",),
    ).fetchall()
    if not rows:
        raise SystemExit(f"No bid matching {search!r}")
    if len(rows) > 1:
        names = [r[0] for r in rows]
        raise SystemExit(f"Ambiguous bid {search!r}: {names}")
    return rows[0][0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True, help="Bid name or substring")
    ap.add_argument(
        "--divisions",
        default="",
        help="Comma-separated divisions to include. Empty = all detected.",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: outputs/<bid>_takeoff_checklist.xlsx)",
    )
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    bid = find_bid(conn, args.bid)
    div_filter: set[str] = (
        {d.strip().zfill(2) for d in args.divisions.split(",") if d.strip()}
        if args.divisions else set()
    )

    where = ["bid = ?"]
    params: list = [bid]
    if div_filter:
        placeholders = ",".join("?" * len(div_filter))
        where.append(f"division IN ({placeholders})")
        params.extend(sorted(div_filter))

    sql = f"""
        SELECT division, section, section_title, page, paragraph_id,
               label, confidence, label_source,
               has_capacity, has_tag, repetition_score, text
        FROM paragraphs
        WHERE {' AND '.join(where)}
        ORDER BY division, section, paragraph_id
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        raise SystemExit("No paragraphs match the filter.")

    by_label = {
        "project_specific": [r for r in rows if r[5] == "project_specific"],
        "ambiguous":        [r for r in rows if r[5] == "ambiguous"],
        "boilerplate":      [r for r in rows if r[5] == "boilerplate"],
    }

    wb = Workbook()
    summary_ws = wb.active
    write_summary(summary_ws, bid, rows)

    ws_ps = wb.create_sheet(f"Project-Specific ({len(by_label['project_specific'])})")
    write_paragraphs(ws_ps, by_label["project_specific"])

    ws_amb = wb.create_sheet(f"Ambiguous ({len(by_label['ambiguous'])})")
    write_paragraphs(ws_amb, by_label["ambiguous"])

    ws_bp = wb.create_sheet(f"Boilerplate ({len(by_label['boilerplate'])})")
    write_paragraphs(ws_bp, by_label["boilerplate"])
    ws_bp.sheet_state = "hidden"

    ws_all = wb.create_sheet(f"All ({len(rows)})")
    write_paragraphs(ws_all, rows)
    ws_all.sheet_state = "hidden"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.out
    if out_path is None:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", bid).strip("_")
        out_path = OUT_DIR / f"{slug}_takeoff_checklist.xlsx"
    wb.save(out_path)

    print(f"Wrote {out_path}")
    print(f"  bid: {bid}")
    print(f"  paragraphs: {len(rows):,}  (filter: divisions={sorted(div_filter) or 'ALL'})")
    for lbl, items in by_label.items():
        pct = 100 * len(items) / len(rows)
        print(f"    {lbl:18s}: {len(items):>5,} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
