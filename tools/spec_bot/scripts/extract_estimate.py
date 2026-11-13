"""Extract line items from one estimate workbook.

Auto-detects which sheet has the line items (the one with the most rows
containing both a text description and a numeric price). Then guesses the
description / quantity / unit / cost columns by header keyword match,
falling back to column-content heuristics.

Output:
    data/estimates/<bid_slug>.jsonl   one JSON record per priced row

Usage:
    python extract_estimate.py --bid "Sample Elementary" --workbook path/to/estimate.xlsx
    python extract_estimate.py --bid "Sample Elementary" --workbook path/to/estimate.xlsx --sheet "Recap"

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    raise SystemExit(
        "openpyxl not installed. Run: pip install openpyxl"
    )

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
OUT_DIR = DATA_DIR / "estimates"

DESC_HEADERS = ("description", "desc", "item", "scope", "scope of work", "line item", "narrative")
QTY_HEADERS = ("qty", "quantity", "count", "ea", "each")
UNIT_HEADERS = ("unit", "uom", "u/m", "u of m", "measure")
COST_HEADERS = ("unit cost", "unit price", "rate", "$/unit", "$/ea", "price")
TOTAL_HEADERS = ("total", "extension", "amount", "subtotal", "ext cost", "ext")


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


@dataclass
class LineItem:
    bid: str
    workbook: str
    sheet: str
    row: int
    line_item_id: str
    description: str
    quantity: float | None
    unit: str | None
    unit_cost: float | None
    total: float | None


def _is_number(v) -> bool:
    if v is None or isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v.replace(",", "").replace("$", "").strip())
            return True
        except ValueError:
            return False
    return False


def _to_number(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.replace(",", "").replace("$", "").strip())
        except ValueError:
            return None
    return None


def detect_sheet(wb) -> str:
    """Pick the sheet most likely to contain the line-item list.

    Heuristic: count rows that have a substantial text description (>=10 chars)
    that isn't a stub like '0'. Sheets with many descriptions win over sheets
    that are mostly numeric rollups.
    """
    best_sheet = wb.sheetnames[0]
    best_score = -1
    for name in wb.sheetnames:
        ws = wb[name]
        score = 0
        for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 500), values_only=True):
            for v in row:
                if isinstance(v, str):
                    s = v.strip()
                    if len(s) >= 10 and s not in ("0", "0.0", "-"):
                        score += 1
                        break  # one credit per row
        # Tie-break: prefer sheets whose name contains "field" or "detail" or
        # "estimate" (the per-line sheet) over "summary" / "recap".
        upper = name.upper()
        if "FIELD" in upper or "DETAIL" in upper:
            score += 50
        if "SUMMARY" in upper or "RECAP" in upper or "ROLLUP" in upper:
            score -= 50
        if score > best_score:
            best_score = score
            best_sheet = name
    return best_sheet


def detect_columns(ws) -> tuple[dict[str, int], int]:
    """Return ({role: col_index_0based}, header_row) by header keyword match.

    Some estimate templates use a form-style layout where the line-item header
    row is buried (e.g. row 38 after a customer-info form). Scan up to row 60.
    """
    cols = {"description": -1, "quantity": -1, "unit": -1, "unit_cost": -1, "total": -1}
    header_row = 0

    def _matches(header_text: str, header_list: tuple) -> bool:
        # Exact (case-insensitive) match, or whole-token substring.
        # Reject form-field labels ending in ":" since those are not column headers.
        if header_text.endswith(":"):
            return False
        return any(k == header_text for k in header_list)

    for ri, row in enumerate(ws.iter_rows(min_row=1, max_row=60, values_only=True), start=1):
        # Find header-shaped cells in THIS row only.
        row_cols = {"description": -1, "quantity": -1, "unit": -1, "unit_cost": -1, "total": -1}
        for ci, v in enumerate(row):
            if not isinstance(v, str):
                continue
            h = v.strip().lower().rstrip(".").rstrip()
            if not h:
                continue
            if row_cols["description"] < 0 and _matches(h, DESC_HEADERS):
                row_cols["description"] = ci
            elif row_cols["quantity"] < 0 and (
                _matches(h, QTY_HEADERS) or h.startswith("quantit")
            ):
                row_cols["quantity"] = ci
            elif row_cols["unit"] < 0 and _matches(h, UNIT_HEADERS):
                row_cols["unit"] = ci
            elif row_cols["unit_cost"] < 0 and _matches(h, COST_HEADERS):
                row_cols["unit_cost"] = ci
            elif row_cols["total"] < 0 and _matches(h, TOTAL_HEADERS):
                row_cols["total"] = ci

        # Only adopt this row as the header if it has at least 2 header-shaped
        # cells (a real table header has multiple), OR if we get to the very
        # last allowable row and have a description (last-ditch).
        n_found = sum(1 for v in row_cols.values() if v >= 0)
        if n_found >= 2 and row_cols["description"] >= 0:
            cols = row_cols
            header_row = ri
            break
        if cols["description"] < 0 and row_cols["description"] >= 0:
            # Remember the first candidate but keep searching for a stronger one.
            cols = row_cols
            header_row = ri
    # Fallback: pick the widest text column for description, rightmost numeric column for total.
    if cols["description"] < 0:
        text_widths: dict[int, int] = {}
        for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 200), values_only=True):
            for ci, v in enumerate(row):
                if isinstance(v, str):
                    text_widths[ci] = max(text_widths.get(ci, 0), len(v))
        if text_widths:
            cols["description"] = max(text_widths, key=lambda k: text_widths[k])
    return cols, header_row


def extract(workbook_path: Path, bid: str, sheet_override: str | None) -> list[LineItem]:
    wb = load_workbook(workbook_path, data_only=True, read_only=True)
    sheet = sheet_override or detect_sheet(wb)
    if sheet not in wb.sheetnames:
        raise SystemExit(f"Sheet {sheet!r} not in workbook. Available: {wb.sheetnames}")
    ws = wb[sheet]
    cols, header_row = detect_columns(ws)
    if cols["description"] < 0:
        raise SystemExit(f"Could not locate a description column on sheet {sheet!r}.")

    items: list[LineItem] = []
    counter = 0
    # Skip everything up to and including the header row.
    start_row = max(1, header_row + 1)
    for ri, row in enumerate(ws.iter_rows(min_row=start_row, values_only=True), start=start_row):
        desc_val = row[cols["description"]] if cols["description"] < len(row) else None
        if not isinstance(desc_val, str):
            continue
        desc = desc_val.strip()
        # Reject too-short or stub values (some templates pre-fill "0" in unused rows).
        if len(desc) < 4 or desc in ("0", "0.0", "-"):
            continue
        if desc.lower() in ("total", "subtotal", "grand total", "description"):
            continue

        def cell(role: str):
            ci = cols[role]
            return row[ci] if 0 <= ci < len(row) else None

        qty = _to_number(cell("quantity"))
        unit = cell("unit")
        unit = unit.strip() if isinstance(unit, str) else None
        unit_cost = _to_number(cell("unit_cost"))
        total = _to_number(cell("total"))
        if total is None and qty is not None and unit_cost is not None:
            total = qty * unit_cost
        # Description-only rows are STILL acceptable: some estimate templates list
        # priced scope items in the field-file sheet without per-line totals,
        # with pricing rolled up on the recap sheet. The description alone is
        # enough to label which spec paragraphs were touched.

        counter += 1
        items.append(LineItem(
            bid=bid,
            workbook=workbook_path.name,
            sheet=sheet,
            row=ri,
            line_item_id=f"{slug(bid)}_li{counter:04d}",
            description=desc,
            quantity=qty,
            unit=unit,
            unit_cost=unit_cost,
            total=total,
        ))
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True)
    ap.add_argument("--workbook", type=Path, required=True)
    ap.add_argument("--sheet", default=None, help="Sheet name (auto-detect if omitted)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    if not args.workbook.exists():
        raise SystemExit(f"Workbook not found: {args.workbook}")

    items = extract(args.workbook, args.bid, args.sheet)
    out_path = args.out or (OUT_DIR / f"{slug(args.bid)}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(asdict(it), ensure_ascii=False) + "\n")

    total_priced = sum(it.total or 0 for it in items)
    print(f"Extracted {len(items)} line items from {args.workbook.name}")
    print(f"  sheet:       {items[0].sheet if items else '(none)'}")
    print(f"  total $:     {total_priced:,.2f}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
