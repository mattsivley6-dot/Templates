"""Quick inspector for proposal extraction quality.

Usage:
    python inspect_proposals.py sample_elementary
    python inspect_proposals.py sample_elementary --sample "Controls"

The first argument is the bid slug (the file name of
data/proposals/<bid_slug>.jsonl without the extension). --sample prints
example capacities and tags from the first proposal whose file name
contains the given text.

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

# Force stdout to utf-8 so we can print unicode safely on Windows.
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")

ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("bid_slug", help="Bid slug, e.g. sample_elementary")
ap.add_argument("--sample", default=None,
                help="Show sample capacities and tags from the proposal whose file name contains this text")
args = ap.parse_args()

bid_slug = args.bid_slug
f = DATA_DIR / "proposals" / f"{bid_slug}.jsonl"
if not f.exists():
    raise SystemExit(f"Not found: {f}\nRun extract_proposals.py first.")
records = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

print(f"=== {bid_slug} ===  records={len(records)}")
print()
print("Per-proposal summary:")
for r in sorted(records, key=lambda x: -len(x["section_citations"])):
    print(
        f"  {r['trade_guess']:12s}  "
        f"{r['proposal_file'][:55]:55s}  "
        f"cites={len(r['section_citations']):2d}  "
        f"tags={len(r['equipment_tags']):2d}  "
        f"caps={len(r['capacities']):3d}  "
        f"qtys={len(r['quantities']):3d}"
    )

print()
print("CSI citations across all proposals (most-cited first):")
all_cites = Counter()
for r in records:
    all_cites.update(r["section_citations"])
for sec, n in all_cites.most_common(20):
    print(f"  {sec}  cited by {n} proposals")

print()
print("Equipment tags aggregated:")
all_tags = Counter()
for r in records:
    for t in r["equipment_tags"]:
        all_tags[t["tag"]] += 1
for tag, n in all_tags.most_common(20):
    print(f"  {tag}  {n}")

print()
print("Capacity unit distribution (sanity check):")
cap_units = Counter()
for r in records:
    for c in r["capacities"]:
        cap_units[c["unit"]] += 1
for u, n in cap_units.most_common():
    print(f"  {u}: {n}")

if args.sample:
    needle = args.sample.lower()
    rec = next((r for r in records if needle in r["proposal_file"].lower()), None)
    print()
    if rec is None:
        print(f"No proposal file name contains {args.sample!r}.")
    else:
        print(f"Sample from {rec['proposal_file']}:")
        print("  capacities:")
        for c in rec["capacities"][:8]:
            print(f"    {c['value']} {c['unit']}: {c['context']!r}")
        print("  tags:")
        for t in rec["equipment_tags"][:10]:
            print(f"    {t['tag']}: {t['context']!r}")
        print(f"  citations: {rec['section_citations']}")
        print(f"  quantities: {rec['quantities'][:8]}")
