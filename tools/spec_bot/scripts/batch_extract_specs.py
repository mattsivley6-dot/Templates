"""Batch-extract spec books for every TRAINING/PARTIAL bid in the inventory.

Skips re-extraction if the output JSONL already exists. Logs failures to
data/extract_errors.log so you can re-run only the problem PDFs.

Run inventory.py first to build data/inventory.json.

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
INVENTORY = DATA_DIR / "inventory.json"
OUT_DIR = DATA_DIR / "specs"
EXTRACT_SCRIPT = SPEC_BOT / "scripts" / "extract_spec.py"
ERROR_LOG = DATA_DIR / "extract_errors.log"

# Subfolder inside each job folder where the spec book usually lives.
# Change with --bid-docs-subfolder to match your own folder layout.
DEFAULT_BID_DOCS_SUBFOLDER = "01-Bid Docs"


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--bid-docs-subfolder",
        default=DEFAULT_BID_DOCS_SUBFOLDER,
        help=f"Subfolder of each job folder that holds the spec (default: {DEFAULT_BID_DOCS_SUBFOLDER!r})",
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    targets = [r for r in rows if r["classification"] in ("TRAINING", "PARTIAL")]
    print(f"Found {len(targets)} training/partial bids to extract.")

    errors: list[str] = []
    done = skipped = 0

    for row in targets:
        bid = row["job"]
        bid_path = Path(row["path"])
        for spec_filename in row["spec_files"]:
            clean = spec_filename.replace(" (?large unnamed)", "").strip()
            # Spec may live in the bid docs subfolder OR at the job root.
            candidates = [
                bid_path / args.bid_docs_subfolder / clean,
                bid_path / clean,
            ]
            pdf = next((c for c in candidates if c.exists()), None)
            if pdf is None:
                msg = f"NOT FOUND: {bid} / {clean}"
                print(f"  [skip] {msg}")
                errors.append(msg)
                continue

            # Tag the bid name with the PDF stem so multi-spec bids
            # don't overwrite each other.
            bid_slug = slug(f"{bid}__{pdf.stem}")
            out_path = OUT_DIR / f"{bid_slug}.jsonl"
            if out_path.exists() and out_path.stat().st_size > 0:
                print(f"  [keep] {out_path.name}")
                skipped += 1
                continue

            print(f"  [run ] {bid}  <-  {pdf.name}")
            try:
                result = subprocess.run(
                    [
                        sys.executable, str(EXTRACT_SCRIPT),
                        str(pdf),
                        "--bid", bid,
                        "--out", str(out_path),
                    ],
                    capture_output=True, text=True, timeout=300,
                )
                if result.returncode != 0:
                    msg = f"FAILED rc={result.returncode}: {bid} / {pdf.name}\n  stderr: {result.stderr[:500]}"
                    print(f"    !! {msg}")
                    errors.append(msg)
                    continue
                # Echo extractor summary line
                tail = result.stdout.strip().split("\n")[-2:]
                for ln in tail:
                    print(f"    {ln}")
                done += 1
            except subprocess.TimeoutExpired:
                msg = f"TIMEOUT: {bid} / {pdf.name}"
                print(f"    !! {msg}")
                errors.append(msg)

    print(f"\nExtracted {done} new specs, skipped {skipped} already-done.")
    if errors:
        ERROR_LOG.write_text("\n".join(errors), encoding="utf-8")
        print(f"Logged {len(errors)} errors to {ERROR_LOG}")


if __name__ == "__main__":
    main()
