"""Extract paragraph-level records from a CSI project manual PDF.

Output: one JSONL record per paragraph, with division/section/page metadata.
The downstream scorer consumes these to build the labeled library.

Usage:
    python extract_spec.py <pdf_path> --bid "Sample Elementary"
    python extract_spec.py <pdf_path> --bid "Sample Elementary" --out data/specs/sample_elementary.jsonl
    python extract_spec.py <pdf_path> --bid "Sample Elementary" --divisions 01,22,23,26
    python extract_spec.py <pdf_path> --bid "Sample Elementary" --ignore-words "SAMPLE ISD,SAMPLE ENGINEERING"

Page chrome (owner, engineer and project names printed above the footer) can
be confused with the section title. List words that mark such lines in
config/title_ignore_words.txt (one per line) or pass them with --ignore-words.

The data folder defaults to ./data in the tool folder. Set the SPEC_BOT_DATA
environment variable to use a different one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

import fitz  # pymupdf

SPEC_BOT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SPEC_BOT_DATA") or SPEC_BOT_ROOT / "data")
DEFAULT_OUT_DIR = DATA_DIR / "specs"
IGNORE_WORDS_FILE = SPEC_BOT_ROOT / "config" / "title_ignore_words.txt"

# Upper-case words that mark a line as project chrome (owner, engineer,
# architect or project name) rather than a section title. Filled from
# IGNORE_WORDS_FILE and --ignore-words at startup.
USER_IGNORE_WORDS: list[str] = []


def load_ignore_words(path: Path, extra: str = "") -> list[str]:
    words: list[str] = []
    if path.exists():
        for ln in path.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                words.append(ln.upper())
    for w in extra.split(","):
        w = w.strip()
        if w:
            words.append(w.upper())
    return words

# Matches CSI section numbers in either format:
#   "02 41 19"   (spaced)
#   "024119"     (compressed)
#   "02 41 19.13" (with optional subsection)
CSI_SECTION_RE = re.compile(
    r"\b(?P<sec>(?P<div>\d{2})\s?(?P<mid>\d{2})\s?(?P<minor>\d{2})(?:\.(?P<sub>\d{2}))?)\b"
)
END_OF_SECTION_RE = re.compile(
    r"END\s+OF\s+SECTION\s+(?P<sec>\d{2}\s?\d{2}\s?\d{2}(?:\.\d{2})?)",
    re.IGNORECASE,
)

# Lines like "PART 1 - GENERAL" or "PART 2 PRODUCTS"
PART_RE = re.compile(r"^\s*PART\s+\d\b", re.IGNORECASE)
# Numbered/lettered list items (typical spec structure)
LIST_ITEM_RE = re.compile(r"^\s*(?:\d+\.\d+|\d+\.|[A-Z]\.|\d+\)|[a-z]\))\s")


@dataclass
class ParagraphRecord:
    bid: str
    spec_pdf: str
    division: str           # e.g. "23"
    section: str            # e.g. "23 81 19" (always normalized to spaced form)
    section_title: str      # best-effort
    paragraph_id: str       # e.g. "23 81 19_p001"
    page: int               # 1-indexed
    text: str
    char_count: int


def normalize_section(raw: str) -> str:
    """Normalize section numbers to spaced canonical form, e.g. '23 81 19'."""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 6:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]}"
    if len(digits) == 8:  # with subsection
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]}.{digits[6:8]}"
    return raw.strip()


def division_of(section: str) -> str:
    """Extract the 2-digit division from a normalized section string."""
    return section[:2] if len(section) >= 2 else ""


# Page footer pattern: matches both spaced ("04 20 00 - 7") and compressed
# ("002100 - 7") section number formats. Some AE firms use one or the other.
SECTION_FOOTER_RE = re.compile(
    r"\b(?P<sec>\d{2}\s?\d{2}\s?\d{2}(?:\.\d{2})?)\s*-\s*\d+\b"
)

# Sub-section headings like "1.01 RELATED DOCUMENTS" / "2.3 PRODUCTS"
SUBSECTION_HEADING_RE = re.compile(r"^\s*\d+\.\d+\s+[A-Z][A-Z\s,&/-]+$")


def page_to_section(page_text: str) -> tuple[str, str] | None:
    """Return (section_normalized, title_guess) for a page, or None.

    Uses the footer pattern 'XX XX XX - N' as primary signal. Title is the
    non-empty line directly above the footer (or 1-2 above if first line is
    also chrome like the AE firm or project name).
    """
    lines = page_text.split("\n")
    # Search from bottom up: footer lives at end of page.
    for i in range(len(lines) - 1, -1, -1):
        ln = lines[i]
        m = SECTION_FOOTER_RE.search(ln)
        if not m:
            continue
        sec = normalize_section(m.group("sec"))
        # Title: walk upward past blank lines / AE firm / project name boilerplate.
        title = ""
        for j in range(i - 1, max(-1, i - 6), -1):
            cand = lines[j].strip()
            if not cand:
                continue
            # Skip lines that are themselves chrome or trivially short
            if (
                cand.isdigit()
                or len(cand) < 4
                or len(cand) > 80
            ):
                continue
            # Skip obvious chrome
            upper = cand.upper()
            if (
                "ENGINEERING" in upper and "CONSULTING" in upper
            ) or "INDEPENDENT SCHOOL DISTRICT" in upper or (
                "ELEMENTARY SCHOOL" in upper
            ) or any(w in upper for w in USER_IGNORE_WORDS):
                continue
            title = cand
            break
        return sec, title
    return None


def is_valid_csi_section(section: str) -> bool:
    """Reject obvious false positives.

    Valid CSI MasterFormat divisions are 00-49 (and 50-99 reserved/site).
    We additionally require the section to appear on >=2 pages later in the
    pipeline; single-page hits get filtered as noise.
    """
    digits = re.sub(r"\D", "", section)
    if len(digits) < 6:
        return False
    div = int(digits[:2])
    if div > 49:
        return False
    return True


def detect_repeating_headers_footers(
    pages: list[str], threshold: float = 0.25
) -> set[str]:
    """Find lines that appear on >threshold of pages (those are page chrome).

    Normalization here is more conservative than before: we DO NOT collapse
    digits, because the section-page footer ('04 20 00 - 7') varies per page
    and we want to preserve it for section detection. We do collapse whitespace.
    """
    line_counter: Counter[str] = Counter()
    for page in pages:
        lines = [ln.strip() for ln in page.split("\n") if ln.strip()]
        sample = lines[:4] + lines[-4:]
        for ln in sample:
            # Don't normalize digits: we want to preserve unique footers.
            norm = re.sub(r"\s+", " ", ln).strip()
            # But do skip section-footer-shaped lines so they survive.
            if SECTION_FOOTER_RE.search(norm):
                continue
            if 4 <= len(norm) <= 120:
                line_counter[norm] += 1

    n_pages = max(1, len(pages))
    chrome = {
        norm for norm, count in line_counter.items()
        if count / n_pages >= threshold
    }
    return chrome


def strip_chrome(page_text: str, chrome: set[str]) -> str:
    out_lines: list[str] = []
    for ln in page_text.split("\n"):
        norm = re.sub(r"\s+", " ", ln).strip()
        if norm in chrome:
            continue
        # Also strip the section footer itself from body text.
        if SECTION_FOOTER_RE.search(norm) and len(norm) < 30:
            continue
        out_lines.append(ln)
    return "\n".join(out_lines)


def find_section_pages(
    page_texts: list[str],
) -> dict[str, dict]:
    """For each CSI section, collect the pages whose footer matches it.

    Returns: {section_normalized: {"pages": [0-indexed page idx ...],
                                    "title": best_title}}
    Pages without a clear CSI footer (cover sheets, embedded contracts,
    ToC) are excluded. That prevents embedded owner contract documents
    (general conditions, contract forms) from being attributed to the
    previous CSI section.
    """
    per_section: dict[str, dict] = {}
    for i, page in enumerate(page_texts):
        hit = page_to_section(page)
        if hit is None:
            continue
        sec, title = hit
        if not is_valid_csi_section(sec):
            continue
        entry = per_section.setdefault(sec, {"pages": [], "titles": Counter()})
        entry["pages"].append(i)
        if title:
            entry["titles"][title] += 1

    # Pick the best title per section.
    for sec, entry in per_section.items():
        titles = entry.pop("titles")
        best = ""
        for cand, _ in titles.most_common():
            if cand and not _looks_like_project_chrome(cand):
                best = cand
                break
        # Fallback: any title at all, even if it's project chrome.
        if not best and titles:
            best = titles.most_common(1)[0][0]
        entry["title"] = best
    return per_section


def _looks_like_project_chrome(s: str) -> bool:
    """Reject title candidates that are obviously project metadata, not titles."""
    upper = s.upper()
    bad_signals = [
        "PROJECT", "ELEMENTARY",
        "MIDDLE SCHOOL", "HIGH SCHOOL", "CONSULTING", "ENGINEERING",
        "REGISTRATION", "ARCHITECTS",
        " ISD", "INDEPENDENT SCHOOL DISTRICT",
        "EFFECTIVE DATE", "ISSUE DATE",
    ] + USER_IGNORE_WORDS
    if any(b in upper for b in bad_signals):
        return True
    # Lines that look like a project number ("12345", "1234.00") aren't titles.
    if re.fullmatch(r"[\d\s.\-#]+", s):
        return True
    return False


def split_into_paragraphs(text: str) -> list[str]:
    """Split a section body into paragraphs.

    Spec books use a mix of blank-line separation and numbered list items.
    We treat a new numbered/lettered list item as a paragraph boundary too.
    Subsection headings ('1.01 RELATED DOCUMENTS') are merged with the
    following content so they don't pollute the corpus as standalone short
    "paragraphs" that match each other across every section.
    """
    raw_paragraphs = re.split(r"\n\s*\n+", text)
    out: list[str] = []
    for chunk in raw_paragraphs:
        lines = chunk.split("\n")
        current: list[str] = []
        for ln in lines:
            if LIST_ITEM_RE.match(ln) and current:
                joined = " ".join(s.strip() for s in current if s.strip())
                if joined:
                    out.append(joined)
                current = [ln]
            else:
                current.append(ln)
        if current:
            joined = " ".join(s.strip() for s in current if s.strip())
            if joined:
                out.append(joined)

    # Merge bare subsection headings (1.01 RELATED DOCUMENTS) into the next paragraph.
    merged: list[str] = []
    pending_heading: str | None = None
    for p in out:
        stripped = p.strip()
        if SUBSECTION_HEADING_RE.match(stripped) and len(stripped) < 60:
            pending_heading = stripped
            continue
        if pending_heading:
            merged.append(f"{pending_heading}: {p}")
            pending_heading = None
        else:
            merged.append(p)
    if pending_heading:
        merged.append(pending_heading)

    # Filter out trivial paragraphs.
    merged = [p for p in merged if len(p) >= 30]
    return merged


def extract(
    pdf_path: Path,
    bid: str,
    divisions_filter: set[str] | None = None,
) -> list[ParagraphRecord]:
    doc = fitz.open(pdf_path)
    page_texts = [page.get_text() for page in doc]
    doc.close()

    # Map each section to the pages whose footer it appears on.
    per_section = find_section_pages(page_texts)
    if not per_section:
        return []

    # Strip chrome for body extraction.
    chrome = detect_repeating_headers_footers(page_texts)
    page_texts_clean = [strip_chrome(pt, chrome) for pt in page_texts]

    records: list[ParagraphRecord] = []
    for section, info in sorted(per_section.items()):
        division = division_of(section)
        if divisions_filter and division not in divisions_filter:
            continue
        title = info["title"]
        page_indices = sorted(set(info["pages"]))

        # Concatenate text only for pages whose footer directly named this section.
        section_text_parts: list[tuple[int, str]] = [
            (p + 1, page_texts_clean[p]) for p in page_indices
        ]
        full_text = "\n\n".join(t for _, t in section_text_parts)

        paragraphs = split_into_paragraphs(full_text)
        for pi, ptext in enumerate(paragraphs, start=1):
            probe = ptext[:40]
            page_no = (page_indices[0] + 1) if page_indices else 0
            for p, pt in section_text_parts:
                if probe in pt:
                    page_no = p
                    break
            records.append(
                ParagraphRecord(
                    bid=bid,
                    spec_pdf=pdf_path.name,
                    division=division,
                    section=section,
                    section_title=title,
                    paragraph_id=f"{section}_p{pi:03d}",
                    page=page_no,
                    text=ptext,
                    char_count=len(ptext),
                )
            )

    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Path to the project manual PDF")
    ap.add_argument("--bid", required=True, help="Bid name (e.g. 'Sample Elementary')")
    ap.add_argument(
        "--ignore-words",
        default="",
        help="Comma-separated words that mark page chrome lines (owner, engineer, "
             "project name). Added to config/title_ignore_words.txt if present.",
    )
    ap.add_argument(
        "--divisions",
        default="",
        help="Comma-separated divisions to keep (e.g. '01,22,23,26'). Empty = all.",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSONL path (default: data/specs/<bid_slug>.jsonl)",
    )
    args = ap.parse_args()

    USER_IGNORE_WORDS[:] = load_ignore_words(IGNORE_WORDS_FILE, args.ignore_words)

    div_filter: set[str] | None = None
    if args.divisions.strip():
        div_filter = {d.strip().zfill(2) for d in args.divisions.split(",")}

    out_path = args.out
    if out_path is None:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", args.bid).strip("_").lower()
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DEFAULT_OUT_DIR / f"{slug}.jsonl"

    records = extract(args.pdf, args.bid, div_filter)
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    # Summary
    div_counts: Counter[str] = Counter(r.division for r in records)
    sec_counts: Counter[str] = Counter(r.section for r in records)
    print(f"Extracted {len(records)} paragraphs from {args.pdf.name}")
    print(f"  divisions: {dict(div_counts)}")
    print(f"  sections : {len(sec_counts)}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
