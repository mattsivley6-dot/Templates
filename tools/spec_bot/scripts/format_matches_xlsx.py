"""Convert a matches CSV into a reviewable XLSX with proper formatting.

For each line item, all top-N candidate spec paragraphs are shown as a
group of consecutive rows with alternating colors so you can compare
them side-by-side. The accept column has a Y/N data-validation dropdown.

Usage:
    python format_matches_xlsx.py --csv data/estimates/sample_elementary__matches.csv
    python format_matches_xlsx.py --csv data/estimates/sample_middle__matches.csv --out review.xlsx
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

# Visual palette
FILL_HEADER = PatternFill("solid", fgColor="305496")
FILL_GROUP_A = PatternFill("solid", fgColor="FFFFFF")
FILL_GROUP_B = PatternFill("solid", fgColor="F2F2F2")
FILL_SIM_HIGH = PatternFill("solid", fgColor="C6EFCE")  # green  >= 0.55
FILL_SIM_MID = PatternFill("solid", fgColor="FFEB9C")   # yellow >= 0.40
FILL_SIM_LOW = PatternFill("solid", fgColor="FFC7CE")   # red    <  0.40
FILL_ACCEPT = PatternFill("solid", fgColor="FFF2CC")    # warm   for the input column

HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAP_CENTER = Alignment(wrap_text=True, vertical="center", horizontal="center")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def sim_fill(sim: float) -> PatternFill:
    if sim >= 0.55:
        return FILL_SIM_HIGH
    if sim >= 0.40:
        return FILL_SIM_MID
    return FILL_SIM_LOW


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.csv.open(encoding="utf-8")))
    if not rows:
        raise SystemExit(f"No rows in {args.csv}")

    # Group by line_item_id, preserve original order.
    groups: dict[str, list[dict]] = defaultdict(list)
    order: list[str] = []
    for r in rows:
        lid = r["line_item_id"]
        if lid not in groups:
            order.append(lid)
        groups[lid].append(r)

    wb = Workbook()
    ws = wb.active
    ws.title = "Review"

    # Visible columns, in the order the user sees.
    # Two hidden tail columns carry the line_item_id and spec_paragraph_id so
    # apply_estimate_labels.py can map rows back to records.
    headers = [
        ("Rank",          5),
        ("Accept (Y/N)",  10),
        ("Line Item",     38),
        ("Qty",            6),
        ("Sim",            6),
        ("Section",        9),
        ("Section Title", 28),
        ("Spec Paragraph (top 300 chars)", 75),
        ("Notes",         20),
        ("line_item_id",  20),       # hidden tail
        ("spec_paragraph_id", 20),   # hidden tail
    ]
    HIDDEN_COLS = {"line_item_id", "spec_paragraph_id"}

    # Write header row
    for ci, (name, width) in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=ci, value=name)
        cell.font = HEADER_FONT
        cell.fill = FILL_HEADER
        cell.alignment = WRAP_CENTER
        cell.border = BORDER
        col_letter = get_column_letter(ci)
        ws.column_dimensions[col_letter].width = width
        if name in HIDDEN_COLS:
            ws.column_dimensions[col_letter].hidden = True
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "C2"

    # Data rows, grouped by line item
    r_idx = 2
    for gi, lid in enumerate(order):
        items = sorted(groups[lid], key=lambda x: int(x["rank"]))
        group_fill = FILL_GROUP_A if gi % 2 == 0 else FILL_GROUP_B
        first = items[0]
        n = len(items)

        for k, item in enumerate(items):
            rank = int(item["rank"])
            sim = float(item["similarity"])
            # Line item description only on the first row of the group
            li_desc = first["line_item_desc"] if k == 0 else ""
            qty = first.get("qty") or "" if k == 0 else ""
            values = [
                rank,
                "",                                # accept (user fills in)
                li_desc,
                qty,
                f"{sim:.2f}",
                item["spec_section"],
                item["spec_section_title"][:60],
                item["spec_paragraph_text"][:300],
                "",                                 # notes
                item["line_item_id"],               # hidden
                item["spec_paragraph_id"],          # hidden
            ]
            for ci, val in enumerate(values, start=1):
                cell = ws.cell(row=r_idx, column=ci, value=val)
                cell.alignment = WRAP
                cell.border = BORDER
                cell.fill = group_fill
            # Color the similarity cell explicitly
            ws.cell(row=r_idx, column=5).fill = sim_fill(sim)
            ws.cell(row=r_idx, column=5).alignment = WRAP_CENTER
            # Highlight the accept input cell
            ws.cell(row=r_idx, column=2).fill = FILL_ACCEPT
            ws.cell(row=r_idx, column=2).alignment = WRAP_CENTER
            ws.cell(row=r_idx, column=2).font = BOLD
            # Bold the line-item description on the first row only
            if k == 0:
                ws.cell(row=r_idx, column=3).font = BOLD
            # Tall row for wrapped text readability
            ws.row_dimensions[r_idx].height = 64
            r_idx += 1

    # Data validation: dropdown Y / N for the accept column
    dv = DataValidation(type="list", formula1='"Y,N"', allow_blank=True, showDropDown=False)
    dv.error = "Please enter Y, N, or leave blank"
    dv.errorTitle = "Invalid value"
    dv.add(f"B2:B{r_idx-1}")
    ws.add_data_validation(dv)

    # Set auto-filter on the header so user can filter by similarity / section
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{r_idx-1}"

    out_path = args.out or args.csv.with_suffix(".xlsx")
    wb.save(out_path)
    print(f"Wrote {out_path}")
    print(f"  {len(order)} line items, {sum(len(v) for v in groups.values())} candidate matches")


if __name__ == "__main__":
    main()
