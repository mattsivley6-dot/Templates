"""Extract attention signals from sub/vendor proposals for one bid.

For each proposal PDF/DOCX in the job's proposals folder (and its scopes and
addenda folders; see FOLDER_LAYOUT below to match your own folder names),
emit a JSON record with:
  - explicit CSI section citations  -> "this paragraph matters"
  - equipment tag mentions          -> "RTU-1, CH-2, AHU-3 are scope"
  - quantity mentions               -> "(50) RTUs", "(8) exhaust fans"
  - capacity values                 -> "1200 ton", "3200 CFM"
  - full text                       -> downstream semantic matching

Output: data/proposals/<bid_slug>.jsonl  (one line per proposal file)

Usage:
    python extract_proposals.py --bid "Sample Elementary"
    python extract_proposals.py --all

Run inventory.py first to build data/inventory.json. The data folder defaults
to ./data in the tool folder. Set the SPEC_BOT_DATA environment variable to
use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

import fitz  # pymupdf
from docx import Document as DocxDocument

SPEC_BOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT / "data")
INVENTORY = DATA_DIR / "inventory.json"
OUT_DIR = DATA_DIR / "proposals"

# Job subfolders to scan, as (label, [folder-name prefixes]). The first child
# folder whose name starts with any prefix is used for that label. Edit these
# to match your own job folder layout.
FOLDER_LAYOUT = [
    ("05-Proposals", ["05-Proposals", "Proposals and Scopes", "Proposals"]),
    ("10-Scopes", ["10-Scopes", "Scope"]),
    ("02-Addendums", ["02-Addendums", "Addendum"]),
]

# ---------------------------------------------------------------------------
# CSI section citation regex.
#
# Matches:
#   "23 81 19"          (spaced)
#   "23-81-19"          (dashed)
#   "23.81.19"          (dotted)
#   "238119"            (compressed, validated below)
#   "Section 23 81 19"  (with prefix)
#   "230923-I"          (with letter suffix like 230923-I)
#
# Validation: division must be 00..49 to avoid matching things like
# "2026" inside dates or "1200 ton" capacities.
# ---------------------------------------------------------------------------
# Strict spaced form: actual CSI citations use spaces or non-breaking spaces.
# Dotted/dashed forms ("01.28.26") are almost always dates in real proposals,
# so we only accept those when explicitly prefixed (see CSI_PREFIXED_RE).
CSI_SPACED_RE = re.compile(r"\b(?P<sec>\d{2}\s\d{2}\s\d{2}(?:\.\d{2})?)\b")
CSI_PREFIXED_RE = re.compile(
    r"(?:Section|Spec(?:ification)?|Division|Div\.?)\s+"
    r"(?P<sec>\d{2}[\s\-.]\d{2}[\s\-.]\d{2}(?:\.\d{2})?)",
    re.IGNORECASE,
)
CSI_COMPRESSED_RE = re.compile(r"\b(?P<sec>\d{6})\b")

# Known HVAC / plumbing / electrical equipment tag prefixes.
# A whitelist avoids false positives on random "P-1" or "B-3" text in drawings.
EQUIPMENT_TAG_PREFIXES = (
    # HVAC air
    "RTU", "AHU", "FCU", "VAV", "FPB", "ERV", "MAU", "DOAS", "UH",
    "EF", "RF", "SF", "KEF", "MUA", "GH",
    # Hydronics / chilled water
    "CH", "CT", "CWP", "HWP", "HX", "EXP", "EXT",
    # Refrigerant
    "CU", "CCU", "VRF", "ODU", "IDU",
    # Plumbing
    "WH", "WHP", "SP", "GR",
    # Electrical / controls
    "VFD", "MCC", "ATS", "GEN", "DDC",
    # Generic plant
    "P", "B",
)
EQUIPMENT_TAG_RE = re.compile(
    r"\b(?P<prefix>"
    + "|".join(sorted(EQUIPMENT_TAG_PREFIXES, key=len, reverse=True))
    + r")[-\s]?(?P<num>\d+[A-Z]?)\b"
)

# Quantity mentions: "(50) RTUs" or "50 RTUs" or "fifty RTUs" (ignore the last
# for v1). Capture nearby equipment word.
QUANTITY_RE = re.compile(
    r"\(?(?P<qty>\d{1,3})\)?\s*"
    r"(?:new\s+|existing\s+|additional\s+|total\s+)?"
    r"(?P<item>RTUs?|AHUs?|FCUs?|VAVs?|FPBs?|chillers?|cooling\s+towers?|"
    r"pumps?|boilers?|exhaust\s+fans?|kitchen\s+(?:exhaust\s+)?fans?|"
    r"makeup\s+air\s+units?|MAUs?|ERVs?|VFDs?|"
    r"controllers?|thermostats?|sensors?|dampers?|"
    r"valves?|coils?|filters?|grilles?|registers?|"
    r"split\s+systems?|mini[\s-]?splits?|condensers?|condensing\s+units?|"
    r"unit\s+heaters?|heat\s+pumps?|water\s+heaters?)",
    re.IGNORECASE,
)

# Capacity values with engineering units.
CAPACITY_RE = re.compile(
    r"(?P<val>\d{1,6}(?:[,.]\d+)?)\s*"
    r"(?P<unit>CFM|MBH|GPM|TONS?|HP|KW|MCA|MOCP|VAC|VDC|AMPS?|FLA|RLA|"
    r"PSI|FPM|RPM|BTUH|BTU/H|MMBH|SCFM|ACFM|°F|F\b|KW/TON|EER|IEER|SEER|COP)",
    re.IGNORECASE,
)

# Inclusion / exclusion / clarification headings, used to find scope bullets.
SCOPE_HEADING_RE = re.compile(
    r"^(?P<head>"
    r"INCLU(?:SIONS?|DES?|DED|DING)|"
    r"EXCLU(?:SIONS?|DES?|DED|DING)|"
    r"CLARIFICAT(?:IONS?|E)|"
    r"QUALIFICAT(?:IONS?)?|"
    r"SCOPE\s+OF\s+WORK|"
    r"PROPOSAL\s+INCLUDES?|"
    r"NOT\s+INCLUDED"
    r")\s*[:\-]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Files we don't want to treat as proposals.
PROPOSAL_NEGATIVE_HINTS = (
    "DRAWINGS", "SPECS.PDF",
    "PHOTOS", "PICS",
    "MARGIN", "BID TAB", "LEVELING",  # internal comparison sheets
    " REV ", "_REV_",
    "PERMIT",
    "TRANSMITTAL", "SUBMITTAL LOG",
    "AIA 305", "W-9", "CIQ",
    "FORM",  # proposal forms (filled-out by us, not by subs)
)
# Trade hints. Filename is a stronger signal than body text: we check the
# filename first with stricter substrings, then fall back to body keywords.
# Order matters: earlier rules win. Add your own subs' and vendors' names to
# the lists if their file names don't carry a trade word.
TRADE_HINTS_FILENAME = [
    ("crane",      ["CRANE", "LIFT PLAN", "RIGGING"]),
    ("sign",       ["SIGN"]),
    ("roofing",    ["ROOFING", "ROOF CURB"]),
    ("rtu_vendor", ["TRANE", "CARRIER", "LENNOX", "DAIKIN", "YORK", "RHEEM"]),
    ("sheetmetal", ["SHEET METAL", "SHEETMETAL"]),
    ("electrical", ["ELECTRICAL", " ELECTRIC"]),
    ("balance",    ["BALANCE", " TAB", "TESTING ADJUSTING"]),
    ("controls",   ["EMCS", " BAS", "AUTOMATION", "CONTROLS PROPOSAL", "CONTROLS"]),
    ("chiller",    ["CHILLER"]),
    ("plumbing",   ["PLUMB"]),
    ("insulation", ["INSULATION", "ARMACELL"]),
]


def guess_trade_filename(filename: str) -> str | None:
    upper = filename.upper()
    for trade, hints in TRADE_HINTS_FILENAME:
        if any(h in upper for h in hints):
            return trade
    return None


def normalize_section(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 6:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]}"
    if len(digits) == 8:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]}.{digits[6:8]}"
    return raw


def is_valid_division(section: str) -> bool:
    digits = re.sub(r"\D", "", section)
    if len(digits) < 6:
        return False
    div = int(digits[:2])
    return 0 <= div <= 49


def guess_trade(filename: str, body: str) -> str:
    by_name = guess_trade_filename(filename)
    if by_name:
        return by_name
    # Fallback: look at body for specific markers.
    upper = body[:2000].upper()
    if "BUILDING AUTOMATION" in upper or "EMCS" in upper:
        return "controls"
    if "LIFT PLAN" in upper or "RIGGING" in upper:
        return "crane"
    if "TESTING, ADJUSTING" in upper or "AIR BALANCE" in upper:
        return "balance"
    if "INSULATION" in upper:
        return "insulation"
    return "unknown"


def read_pdf(path: Path) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def read_docx(path: Path) -> str:
    d = DocxDocument(str(path))
    parts: list[str] = [p.text for p in d.paragraphs if p.text and p.text.strip()]
    # Also pull text out of tables (sub proposals often use tables for line items).
    for table in d.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text and cell.text.strip():
                    parts.append(cell.text)
    return "\n".join(parts)


_SANITIZE_TABLE = {
    0x2028: " ",  # LINE SEPARATOR
    0x2029: " ",  # PARAGRAPH SEPARATOR
    0x0085: " ",  # NEXT LINE
    0x000B: " ",  # vertical tab
    0x000C: " ",  # form feed
    0x001C: " ", 0x001D: " ", 0x001E: " ",  # information separators
}


def _sanitize(text: str) -> str:
    """Strip unicode line/paragraph separators that break naive line splitters.

    Why: pymupdf and docx return text containing U+2028 / U+2029 / form-feed
    that are not a plain newline but ARE treated as line breaks by
    str.splitlines(). That
    corrupts JSONL line iteration downstream.
    """
    return text.translate(_SANITIZE_TABLE)


def read_any(path: Path) -> str | None:
    try:
        if path.suffix.lower() == ".pdf":
            return _sanitize(read_pdf(path))
        if path.suffix.lower() == ".docx":
            return _sanitize(read_docx(path))
    except Exception as e:
        print(f"    !! read failed for {path.name}: {e}")
        return None
    return None


@dataclass
class ProposalRecord:
    bid: str
    proposal_file: str
    source_folder: str  # a label from FOLDER_LAYOUT
    trade_guess: str
    section_citations: list[str] = field(default_factory=list)
    equipment_tags: list[dict] = field(default_factory=list)
    quantities: list[dict] = field(default_factory=list)
    capacities: list[dict] = field(default_factory=list)
    scope_headings_found: list[str] = field(default_factory=list)
    text_chars: int = 0
    full_text: str = ""


def extract_signals(text: str) -> dict:
    citations: set[str] = set()

    # Strict spaced form (must use literal spaces, not dots or dashes).
    for m in CSI_SPACED_RE.finditer(text):
        sec = normalize_section(m.group("sec"))
        if is_valid_division(sec):
            citations.add(sec)

    # Explicit-prefix form (catches "Section 23 81 19", "Spec 23-81-19", etc.)
    for m in CSI_PREFIXED_RE.finditer(text):
        sec = normalize_section(m.group("sec"))
        if is_valid_division(sec):
            citations.add(sec)

    # Compressed form: narrower validity to avoid hits inside random numbers.
    # Only accept if preceded/followed by spec-style context word ("section",
    # "spec", "division", "230923-I" style suffix, etc.) OR is a standalone
    # token of exactly 6 digits.
    for m in CSI_COMPRESSED_RE.finditer(text):
        digits = m.group("sec")
        # Reject if surrounded by other digits (e.g. part of phone number "5550100100")
        start, end = m.span()
        before = text[max(0, start - 1):start]
        after = text[end:end + 1]
        if before.isdigit() or after.isdigit():
            continue
        sec = normalize_section(digits)
        if is_valid_division(sec):
            citations.add(sec)

    # Equipment tags. The single-letter prefixes (B, P) are noisy: they match
    # boxes, beams, registers, etc. Require a domain word nearby to keep them.
    SINGLE_LETTER_CONTEXT = {
        "B": ("BOILER", "BLR"),
        "P": ("PUMP", "CWP", "HWP"),
    }
    tags: list[dict] = []
    seen_tags: set[tuple[str, str]] = set()
    for m in EQUIPMENT_TAG_RE.finditer(text):
        prefix = m.group("prefix").upper()
        num = m.group("num").upper()
        ctx_start = max(0, m.start() - 60)
        ctx_end = min(len(text), m.end() + 60)
        context = text[ctx_start:ctx_end].replace("\n", " ").strip()

        if prefix in SINGLE_LETTER_CONTEXT:
            required = SINGLE_LETTER_CONTEXT[prefix]
            if not any(r in context.upper() for r in required):
                continue

        key = (prefix, num)
        if key in seen_tags:
            continue
        seen_tags.add(key)
        tags.append(
            {
                "tag": f"{prefix}-{num}",
                "prefix": prefix,
                "number": num,
                "context": context,
            }
        )

    # Quantities
    qtys: list[dict] = []
    for m in QUANTITY_RE.finditer(text):
        ctx_start = max(0, m.start() - 20)
        ctx_end = min(len(text), m.end() + 20)
        qtys.append(
            {
                "qty": int(m.group("qty")),
                "item": m.group("item").lower().strip(),
                "context": text[ctx_start:ctx_end].replace("\n", " ").strip(),
            }
        )

    # Capacities
    caps: list[dict] = []
    for m in CAPACITY_RE.finditer(text):
        try:
            val_str = m.group("val").replace(",", "")
            val = float(val_str)
        except ValueError:
            continue
        unit = m.group("unit").upper().rstrip("S")
        # Skip implausible values (e.g., "2026 F" from dates with "F")
        if unit in ("CFM", "MBH", "GPM", "BTUH", "MMBH", "SCFM", "ACFM") and val < 1:
            continue
        ctx_start = max(0, m.start() - 30)
        ctx_end = min(len(text), m.end() + 30)
        caps.append(
            {
                "value": val,
                "unit": unit,
                "context": text[ctx_start:ctx_end].replace("\n", " ").strip(),
            }
        )

    # Scope-section headings
    headings = [m.group("head").upper() for m in SCOPE_HEADING_RE.finditer(text)]

    return {
        "citations": sorted(citations),
        "tags": tags,
        "qtys": qtys,
        "caps": caps,
        "scope_headings": headings,
    }


def gather_files(bid_path: Path) -> list[tuple[Path, str]]:
    """Return list of (file_path, source_folder_name)."""
    out: list[tuple[Path, str]] = []
    for label, name_prefixes in FOLDER_LAYOUT:
        for child in bid_path.iterdir():
            if not child.is_dir():
                continue
            upper = child.name.upper()
            if any(upper.startswith(p.upper()) for p in name_prefixes):
                for f in child.iterdir():
                    if not f.is_file():
                        continue
                    if f.suffix.lower() not in (".pdf", ".docx"):
                        continue
                    name_upper = f.name.upper()
                    if any(neg in name_upper for neg in PROPOSAL_NEGATIVE_HINTS):
                        continue
                    try:
                        if f.stat().st_size < 20_000:
                            continue
                    except OSError:
                        continue
                    out.append((f, label))
                break  # only one match per label
    return out


def extract_bid(bid_row: dict) -> int:
    bid = bid_row["job"]
    bid_path = Path(bid_row["path"])
    slug = re.sub(r"[^A-Za-z0-9]+", "_", bid).strip("_").lower()
    out_path = OUT_DIR / f"{slug}.jsonl"

    files = gather_files(bid_path)
    print(f"  {bid}: {len(files)} files to process")
    if not files:
        return 0

    records: list[ProposalRecord] = []
    for path, src_folder in files:
        text = read_any(path)
        if not text or len(text.strip()) < 100:
            continue
        sig = extract_signals(text)
        rec = ProposalRecord(
            bid=bid,
            proposal_file=path.name,
            source_folder=src_folder,
            trade_guess=guess_trade(path.name, text),
            section_citations=sig["citations"],
            equipment_tags=sig["tags"],
            quantities=sig["qtys"],
            capacities=sig["caps"],
            scope_headings_found=sig["scope_headings"],
            text_chars=len(text),
            full_text=text,
        )
        records.append(rec)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    print(
        f"    -> {len(records)} proposals  "
        f"({sum(len(r.section_citations) for r in records)} citations, "
        f"{sum(len(r.equipment_tags) for r in records)} tags, "
        f"{sum(len(r.capacities) for r in records)} capacities)"
    )
    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", help="Single bid name to process")
    ap.add_argument("--all", action="store_true", help="Process all training/partial bids")
    args = ap.parse_args()

    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if args.all:
        targets = [r for r in rows if r["classification"] in ("TRAINING", "PARTIAL")]
    elif args.bid:
        targets = [r for r in rows if r["job"] == args.bid or args.bid in r["job"]]
        if not targets:
            raise SystemExit(f"No bid matching {args.bid!r}")
    else:
        raise SystemExit("Pass --bid NAME or --all")

    total = 0
    for row in targets:
        total += extract_bid(row)
    print(f"\nTotal proposals processed: {total}")


if __name__ == "__main__":
    main()
