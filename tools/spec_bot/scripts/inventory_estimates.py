"""List candidate estimate workbooks per bid, so the user can pick which one
to treat as the authoritative priced estimate for label generation.

Output:
    data/estimates/inventory.json   machine-readable
    data/estimates/inventory.md     human summary

Usage:
    python inventory_estimates.py

Run inventory.py first to build data/inventory.json. The data folder defaults
to ./data in the tool folder. Set the SPEC_BOT_DATA environment variable to
use a different one.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
INVENTORY = DATA_DIR / "inventory.json"
OUT_DIR = DATA_DIR / "estimates"

ESTIMATE_FOLDER_HINTS = ("estim",)  # case-insensitive substring match
ESTIMATE_EXT = (".xlsx", ".xlsm")

# Filenames we treat as backups / drafts, not the priced version.
SKIP_HINTS = ("BACKUP", "BAK", "OLD", "DRAFT", "WORKING", "COPY OF", " - COPY", "TEMP", "RECOVERED")

# Filenames that suggest this is the final priced workbook.
PRIORITY_HINTS = ("FINAL", "PRICED", "SUBMITTED", "BID", "TURNED IN")


def find_estimate_folders(bid_path: Path) -> list[Path]:
    found: list[Path] = []
    for child in bid_path.iterdir():
        if not child.is_dir():
            continue
        if any(h in child.name.lower() for h in ESTIMATE_FOLDER_HINTS):
            found.append(child)
    return found


def score_candidate(path: Path) -> int:
    """Higher = more likely the canonical priced estimate."""
    score = 0
    name = path.name.upper()
    if any(h in name for h in PRIORITY_HINTS):
        score += 10
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    score += min(size // 100_000, 20)  # cap size contribution
    return score


def inventory_one(bid_row: dict) -> dict:
    bid = bid_row["job"]
    bid_path = Path(bid_row["path"])
    folders = find_estimate_folders(bid_path)
    candidates: list[dict] = []
    for folder in folders:
        for f in folder.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() not in ESTIMATE_EXT:
                continue
            name_upper = f.name.upper()
            if any(h in name_upper for h in SKIP_HINTS):
                continue
            if f.name.startswith("~$"):  # Excel lock files
                continue
            try:
                stat = f.stat()
            except OSError:
                continue
            candidates.append({
                "path": str(f),
                "name": f.name,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="minutes"),
                "score": score_candidate(f),
                "folder": folder.name,
            })
    candidates.sort(key=lambda c: -c["score"])
    return {"job": bid, "path": str(bid_path), "candidates": candidates}


def main() -> None:
    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    targets = [r for r in rows if r["classification"] in ("TRAINING", "PARTIAL")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = [inventory_one(r) for r in targets]
    (OUT_DIR / "inventory.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = [f"# Estimate Inventory  ({datetime.now():%Y-%m-%d %H:%M})\n"]
    for r in results:
        lines.append(f"\n## {r['job']}\n")
        if not r["candidates"]:
            lines.append("_no estimate workbooks found_\n")
            continue
        lines.append("| Score | Name | Size (KB) | Modified | Folder |")
        lines.append("|---:|---|---:|---|---|")
        for c in r["candidates"]:
            lines.append(f"| {c['score']} | {c['name']} | {c['size_kb']} | {c['modified']} | {c['folder']} |")
    (OUT_DIR / "inventory.md").write_text("\n".join(lines), encoding="utf-8")
    total_candidates = sum(len(r["candidates"]) for r in results)
    bids_with = sum(1 for r in results if r["candidates"])
    print(f"Scanned {len(results)} bids, found estimates in {bids_with} of them.")
    print(f"Total candidate workbooks: {total_candidates}")
    print(f"Wrote {OUT_DIR / 'inventory.json'}")
    print(f"Wrote {OUT_DIR / 'inventory.md'}")


if __name__ == "__main__":
    main()
