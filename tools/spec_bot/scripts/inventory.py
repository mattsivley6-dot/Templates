"""Inventory your job folders.

For each job folder under the given jobs folders (for example one folder per
year), classify as:
  TRAINING        - has spec book + sub proposals (use to label paragraphs)
  PREDICTION      - has spec book, no proposals yet (target the bot will run on)
  PARTIAL         - spec book + only a few proposals (use w/ caution)
  SKIP            - service/T&M/no spec book (ignore)

Writes:
  data/inventory.json   - machine-readable per-job manifest
  data/inventory.md     - human summary table

Usage:
    python inventory.py --jobs-dir "path/to/2025-JOBS" --jobs-dir "path/to/2026-JOBS"
    python inventory.py --jobs-dir "path/to/JOBS" --skip "Old Bid Folder"

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime

SPEC_BOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")

# Folders to exclude from the inventory regardless of contents.
# Add names here or pass --skip on the command line.
SKIPLIST: set[str] = set()

SPEC_NAME_HINTS = [
    "PROJECT MANUAL", "PROJECT_MANUAL",
    "RFCSP", "RFP",
    "SPEC", "SPECIFICATION",
    "SYST COMPL", "SYSTEMS AND COMPLIANCE", "SYSTEMS & COMPLIANCE",
    "BID DOC", "BID_DOC",
    "MANUAL",
]
SPEC_NEGATIVE_HINTS = [
    "TERMS", "EVALUATION", "BONDING", "W-9", "CIQ", "1295",
    "ADDENDUM", "AIA",
    "PROPOSAL FORM", "REGISTRATION", "INSURANCE",
]
PROPOSAL_NEGATIVE_HINTS = [
    "DRAWINGS", "SPECS.PDF",
    "PHOTOS", "PICS",
    "MARGIN", "BID TAB", "LEVELING",  # internal comparison sheets
    "REV ", " REV",
    "PERMIT",
    "TRANSMITTAL", "SUBMITTAL LOG",
]

CSI_SECTION_RE = re.compile(r"\b\d{2}\s?\d{2}\s?\d{2}\b")


def has_spec_book(bid_docs: Path) -> tuple[bool, list[str]]:
    if not bid_docs.is_dir():
        return False, []
    candidates: list[str] = []
    for f in bid_docs.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() != ".pdf":
            continue
        name_upper = f.name.upper()
        if any(neg in name_upper for neg in SPEC_NEGATIVE_HINTS):
            continue
        # size > 200 KB AND name contains a positive hint, OR > 1MB regardless
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        positive = any(hint in name_upper for hint in SPEC_NAME_HINTS)
        if positive and size > 200_000:
            candidates.append(f.name)
        elif size > 1_500_000 and not positive:
            # large unnamed PDF, likely a spec
            candidates.append(f.name + " (?large unnamed)")
    return bool(candidates), candidates


def count_proposals(prop_dir: Path) -> tuple[int, list[str]]:
    if not prop_dir.is_dir():
        return 0, []
    vendor_files: list[str] = []
    for f in prop_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in (".pdf", ".docx"):
            continue
        name_upper = f.name.upper()
        if any(neg in name_upper for neg in PROPOSAL_NEGATIVE_HINTS):
            continue
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        if size < 30_000:
            continue
        vendor_files.append(f.name)
    return len(vendor_files), vendor_files


def has_addenda(add_dir: Path) -> int:
    if not add_dir.is_dir():
        return 0
    return sum(
        1 for f in add_dir.iterdir()
        if f.is_file() and f.suffix.lower() == ".pdf"
    )


def has_scope_letters(scope_dir: Path) -> int:
    if not scope_dir.is_dir():
        return 0
    return sum(
        1 for f in scope_dir.iterdir()
        if f.is_file() and f.suffix.lower() in (".pdf", ".docx")
    )


def classify(spec_pdfs: int, proposals: int, scopes: int) -> str:
    if spec_pdfs == 0:
        return "SKIP"
    if proposals >= 5:
        return "TRAINING"
    if proposals >= 1:
        return "PARTIAL"
    return "PREDICTION"


def find_dir(parent: Path, names: list[str]) -> Path | None:
    """Find a subdir by any of the given name prefixes (case-insensitive)."""
    if not parent.is_dir():
        return None
    for child in parent.iterdir():
        if not child.is_dir():
            continue
        upper = child.name.upper()
        for n in names:
            if upper.startswith(n.upper()):
                return child
    return None


# Job subfolder name prefixes (case-insensitive). Edit to match your own
# job folder layout.
BID_DOCS_NAMES = ["01-Bid Docs", "01-BID DOCS", "Bid Docs"]
PROPOSALS_NAMES = ["05-Proposals", "Proposals", "Proposals and Scopes"]
ADDENDA_NAMES = ["02-Addendums", "Addendum"]
SCOPES_NAMES = ["10-Scopes", "Scope"]


def inventory_job(job_path: Path) -> dict:
    bid_docs = find_dir(job_path, BID_DOCS_NAMES)
    proposals = find_dir(job_path, PROPOSALS_NAMES)
    addenda = find_dir(job_path, ADDENDA_NAMES)
    scopes = find_dir(job_path, SCOPES_NAMES)

    spec_ok, spec_files = (False, [])
    # Bid docs is the primary location for a spec book, but some job
    # folders keep the RFP / RFCSP at the job root.
    if bid_docs:
        spec_ok, spec_files = has_spec_book(bid_docs)
    if not spec_ok:
        spec_ok, spec_files = has_spec_book(job_path)

    n_proposals, proposal_files = count_proposals(proposals) if proposals else (0, [])
    n_addenda = has_addenda(addenda) if addenda else 0
    n_scopes = has_scope_letters(scopes) if scopes else 0

    label = classify(len(spec_files), n_proposals, n_scopes)

    return {
        "job": job_path.name,
        "path": str(job_path),
        "classification": label,
        "spec_files": spec_files,
        "n_spec_files": len(spec_files),
        "n_proposals": n_proposals,
        "n_addenda": n_addenda,
        "n_scopes": n_scopes,
        "proposal_files_sample": proposal_files[:5],
        "has_bid_docs_folder": bid_docs is not None,
        "has_proposals_folder": proposals is not None,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs-dir", type=Path, action="append", required=True,
                    help="Folder that holds one subfolder per job. Repeat for several.")
    ap.add_argument("--skip", action="append", default=[],
                    help="Job folder name to leave out. Repeat for several.")
    args = ap.parse_args()

    skiplist = SKIPLIST | set(args.skip)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for year_folder in args.jobs_dir:
        if not year_folder.is_dir():
            print(f"  [skip] not a folder: {year_folder}")
            continue
        for job in sorted(year_folder.iterdir()):
            if not job.is_dir():
                continue
            if job.name in skiplist:
                continue
            rows.append(inventory_job(job))

    # Write JSON
    (OUT_DIR / "inventory.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )

    # Buckets
    buckets: dict[str, list[dict]] = {
        "TRAINING": [], "PARTIAL": [], "PREDICTION": [], "SKIP": []
    }
    for r in rows:
        buckets[r["classification"]].append(r)

    lines: list[str] = []
    lines.append(f"# Spec Bot Inventory  ({datetime.now():%Y-%m-%d %H:%M})\n")
    lines.append(f"Total jobs scanned: {len(rows)}\n")
    for k, items in buckets.items():
        lines.append(f"- **{k}**: {len(items)}")
    lines.append("")

    for k in ["TRAINING", "PARTIAL", "PREDICTION", "SKIP"]:
        items = buckets[k]
        lines.append(f"\n## {k}  ({len(items)})\n")
        if not items:
            lines.append("_none_")
            continue
        if k == "SKIP":
            for it in items:
                lines.append(f"- {it['job']}")
            continue
        lines.append("| Job | Specs | Props | Adds | Scopes |")
        lines.append("|---|---:|---:|---:|---:|")
        for it in items:
            lines.append(
                f"| {it['job']} | {it['n_spec_files']} | {it['n_proposals']} "
                f"| {it['n_addenda']} | {it['n_scopes']} |"
            )

    (OUT_DIR / "inventory.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    # Console summary
    print(f"Scanned {len(rows)} job folders")
    for k in ["TRAINING", "PARTIAL", "PREDICTION", "SKIP"]:
        print(f"  {k:11s}: {len(buckets[k])}")
    print(f"\nWrote {OUT_DIR / 'inventory.json'}")
    print(f"Wrote {OUT_DIR / 'inventory.md'}")


if __name__ == "__main__":
    main()
