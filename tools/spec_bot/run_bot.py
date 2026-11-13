"""End-to-end pipeline runner driven by the desktop launcher.

Takes a spec PDF path and a bid name. Runs:
  1. extract_spec.py   - segment the PDF into paragraph records
  2. build_library.py  - rebuild the labeled library so cross-bid
                          repetition counts include this new spec
  3. to_excel.py       - emit the takeoff checklist xlsx, filtered to
                          Div 01/22/23/26 (HVAC bid scope)
Then opens the resulting Excel file in the default app.

Data and output folders default to ./data and ./outputs next to this file.
Override with --data-dir / --out-dir (or the SPEC_BOT_DATA and
SPEC_BOT_OUTPUTS environment variables).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

SPEC_BOT = Path(__file__).resolve().parent
SCRIPTS = SPEC_BOT / "scripts"


def run(label: str, args: list[str], env: dict[str, str]) -> None:
    print(f"\n{label}")
    print("-" * len(label))
    result = subprocess.run(args, env=env)
    if result.returncode != 0:
        raise SystemExit(f"\n!! Step failed: {label}\n!! See messages above for the cause.")


def open_path(path: Path) -> None:
    """Open a file or folder in the default app (Windows, macOS, Linux)."""
    if hasattr(os, "startfile"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Path to the project manual PDF")
    ap.add_argument("bid_name", help="Short name for the bid, e.g. 'Sample Elementary'")
    ap.add_argument(
        "--divisions",
        default="01,22,23,26",
        help="CSI divisions to include in the Excel (default: 01,22,23,26)",
    )
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data"),
        help="Working data folder (default: ./data next to this file)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path(os.environ.get("SPEC_BOT_OUTPUTS") or SPEC_BOT / "outputs"),
        help="Folder for the Excel checklist (default: ./outputs next to this file)",
    )
    args = ap.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"\n!! PDF not found: {args.pdf}\n")

    out_dir = args.out_dir.resolve()
    env = dict(os.environ)
    env["SPEC_BOT_DATA"] = str(args.data_dir.resolve())
    env["SPEC_BOT_OUTPUTS"] = str(out_dir)

    py = sys.executable

    run("[1/3] Reading the PDF and breaking it into paragraphs", [
        py, str(SCRIPTS / "extract_spec.py"),
        str(args.pdf), "--bid", args.bid_name,
    ], env)

    run("[2/3] Comparing it against your past bids", [
        py, str(SCRIPTS / "build_library.py"),
    ], env)

    run("[3/3] Building your Excel takeoff checklist", [
        py, str(SCRIPTS / "to_excel.py"),
        "--bid", args.bid_name,
        "--divisions", args.divisions,
    ], env)

    # The to_excel.py output path is derived from the bid name. Re-derive it
    # here so we can open it for the user automatically.
    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.bid_name).strip("_")
    out_file = out_dir / f"{slug}_takeoff_checklist.xlsx"
    if not out_file.exists():
        # Fallback: open the outputs folder so the user can see what's there.
        print("\n!! Could not auto-locate the output. Opening the outputs folder.")
        open_path(out_dir)
        return

    print(f"\n[OK] Opening: {out_file}")
    open_path(out_file)


if __name__ == "__main__":
    main()
