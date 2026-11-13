# -*- coding: utf-8 -*-
"""Build the Warranty Summary Matrix (PDF) and, optionally, the Warranty
Binder (cover + table of contents + merged manufacturer warranty PDFs with
"Back to Table of Contents" links).

Usage:
    python build_warranty_matrix.py [data.json] [out_dir] [--company company.json]

All arguments optional. data.json defaults to sample_data.json next to
this script; out_dir defaults to _sample_output next to this script;
--company defaults to ../../company.example.json (the template-library
company config, two folders up from this script). The PDF author and the
default "Mechanical Contractor" line come from the company config; nothing
about the company is hard-coded here.

All other variable content lives in the JSON data file; this script holds
only fixed wording and layout. Deterministic: no clock reads, no
randomness. Every date comes from the data file. Same JSON in, same bytes
out.
"""
import argparse
import io
import json
import os
import sys

import fitz  # PyMuPDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COMPANY = os.path.normpath(os.path.join(HERE, "..", "..",
                                                "company.example.json"))

# ---------------------------------------------------------------- constants
# Matrix page: letter LANDSCAPE.
MX_W, MX_H = 792.0, 612.0
MX_MARGIN_X = 42.0                 # title / meta block left edge
MX_TITLE_BASE = 56.0               # title baseline, from TOP of page
MX_META_BASES = (79.0, 91.0, 103.0)  # three meta line baselines, from top
MX_TABLE_TOP = 122.0               # table top edge on page 1, from top
MX_TABLE_TOP_CONT = 41.0           # table top edge on continuation pages
MX_BOTTOM_LIMIT = 571.0            # table may not pass this line (from top)
# Column x edges (8 edges = 7 columns):
MX_COLS = (1.0, 166.0, 306.0, 441.0, 511.0, 586.0, 661.0, 791.0)
MX_CELL_PAD_X = 6.0                # text inset from column edge
MX_LINE_H = 11.0                   # per text line inside a cell
MX_ROW_PAD = 12.0                  # row height = 11 * lines + 12
MX_FIRST_BASE = 14.0               # first baseline below row top
MX_HEADER_FILL = HexColor('#D3D3D3')
MX_GRID = HexColor('#808080')
MX_GRID_W = 0.5
MX_TITLE = "WARRANTY SUMMARY MATRIX"
MX_META_PREFIXES = ("Project: ",
                    "Warranty Commencement Date (System Startup): ",
                    "Mechanical Contractor: ")
MX_HEADERS = ("ITEM / SYSTEM", "MANUFACTURER / PROVIDER", "WARRANTY TYPE",
              "TERM", "START DATE", "END DATE", "CLAIM CONTACT")
MX_ROW_KEYS = ("manufacturer", "warranty_type", "term",
               "start_date", "end_date", "claim_contact")

# Binder cover: letter PORTRAIT, Helvetica (Arial equivalent).
BD_W, BD_H = 612.0, 792.0
BD_LM = 72.0                       # left margin
BD_RIGHT = 540.0                   # wrap limit
BD_BOTTOM = 720.0                  # last allowed baseline (from top)
BD_CONT_TOP = 83.0                 # first baseline on continuation pages
BD_TITLE_BASE = 111.0              # cover title baseline (from top)
BD_LINE = 13.8                     # contact block line step
BD_GROUP_GAP = 9.1                 # extra gap between contact groups
BD_SECT_GAP = 27.8                 # gap before a 14 pt section heading
BD_TOC_LINE = 15.6                 # TOC line step
BD_TOC_GROUP_GAP = 13.8            # extra gap between TOC entries
DEFAULT_ACCENT = '4F81BD'          # heading blue
LINK_BLUE = (0, 0, 1)
BACK_LABEL = "Back to Table of Contents"
CONTACT_LABELS = (("company", "Company Name: "),
                  ("contact", "Contact Person: "),
                  ("phone", "Phone Number: "),
                  ("email", "Email Address: "))
FIXED_PROJECT_CONTACTS = "Project Contacts"
FIXED_STARTUP = "Start-Up Date"
FIXED_TOC = "Table of Contents"
BULLET = u"•"

CREATOR = "Template Library warranty-matrix"
DEFAULT_PDF_DATE = "D:20260101120000-06'00'"
EM, EN = u"\u2014", u"\u2013"     # dash characters the house rule bans


# ---------------------------------------------------------------- helpers
def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def check_no_dashes(obj, path="data"):
    """House rule: no em or en dashes anywhere. Fail loudly if found."""
    if isinstance(obj, str):
        if EM in obj or EN in obj:
            fail("em/en dash found at %s: %r" % (path, obj[:80]))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_no_dashes(v, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_no_dashes(v, "%s[%d]" % (path, i))


def wrap_text(text, font, size, maxw):
    """Word-wrap. Honors explicit \\n. Breaks over-long single words (long
    URLs) by characters. The 0.25 pt tolerance lets a phrase that measures
    exactly the column width (for example 'Contractor Workmanship
    Warranty') stay on one line. Returns a list of lines."""
    out = []
    for seg in str(text).split("\n"):
        words = seg.split()
        if not words:
            out.append("")
            continue
        cur = ""
        for w in words:
            cand = (cur + " " + w) if cur else w
            if stringWidth(cand, font, size) <= maxw + 0.25:
                cur = cand
                continue
            if cur:
                out.append(cur)
                cur = ""
            # place w, char-breaking if it alone exceeds the width
            while stringWidth(w, font, size) > maxw + 0.25:
                k = len(w)
                while k > 1 and stringWidth(w[:k], font, size) > maxw + 0.25:
                    k -= 1
                out.append(w[:k])
                w = w[k:]
            cur = w
        if cur:
            out.append(cur)
    return out or [""]


# ---------------------------------------------------------------- matrix
def cell_lines(row):
    """Wrapped lines for each of the 7 columns of one data row."""
    widths = [MX_COLS[i + 1] - MX_COLS[i] - 2 * MX_CELL_PAD_X
              for i in range(7)]
    item = str(row.get("item", ""))
    detail = str(row.get("item_detail", "") or "")
    lines0 = wrap_text(item, "Helvetica", 8, widths[0])
    if detail:
        lines0 += wrap_text(detail, "Helvetica", 8, widths[0])
    cols = [lines0]
    for i, key in enumerate(MX_ROW_KEYS):
        cols.append(wrap_text(str(row.get(key, "")), "Helvetica", 8,
                              widths[i + 1]))
    return cols


def draw_matrix_segment(c, top, rows_lines, heights, with_header):
    """Draw header (optional) + data rows starting at 'top' (from page top).
    Returns bottom y (from top)."""
    y = top
    boundaries = [y]
    if with_header:
        c.setFillColor(MX_HEADER_FILL)
        c.rect(MX_COLS[0], MX_H - (y + 23.0), MX_COLS[-1] - MX_COLS[0],
               23.0, stroke=0, fill=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        for i, h in enumerate(MX_HEADERS):
            c.drawString(MX_COLS[i] + MX_CELL_PAD_X,
                         MX_H - (y + MX_FIRST_BASE), h)
        y += 23.0
        boundaries.append(y)
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0, 0, 0)
    for cols, rh in zip(rows_lines, heights):
        for i, lines in enumerate(cols):
            for j, line in enumerate(lines):
                c.drawString(MX_COLS[i] + MX_CELL_PAD_X,
                             MX_H - (y + MX_FIRST_BASE + j * MX_LINE_H),
                             line)
        y += rh
        boundaries.append(y)
    # grid
    c.setStrokeColor(MX_GRID)
    c.setLineWidth(MX_GRID_W)
    for by in boundaries:
        c.line(MX_COLS[0], MX_H - by, MX_COLS[-1], MX_H - by)
    for bx in MX_COLS:
        c.line(bx, MX_H - top, bx, MX_H - y)
    return y


def build_matrix(matrix, meta, out_path):
    rows = matrix.get("rows") or fail("matrix.rows is required and non-empty")
    c = Canvas(out_path, pagesize=(MX_W, MX_H), invariant=1)
    c.setTitle("Warranty Summary Matrix - %s" % matrix["project"])
    c.setAuthor(meta["author"])
    c.setSubject(str(matrix["project"]))
    c.setCreator(CREATOR)

    # title + meta block (page 1 only)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(MX_MARGIN_X, MX_H - MX_TITLE_BASE, MX_TITLE)
    c.setFont("Helvetica", 9)
    meta_vals = (matrix["project"], matrix["commencement"],
                 matrix["contractor"])
    for base, prefix, val in zip(MX_META_BASES, MX_META_PREFIXES, meta_vals):
        c.drawString(MX_MARGIN_X, MX_H - base, prefix + str(val))

    all_lines = [cell_lines(r) for r in rows]
    all_heights = [MX_LINE_H * max(len(col) for col in cols) + MX_ROW_PAD
                   for cols in all_lines]

    top = MX_TABLE_TOP
    pending_lines, pending_heights = [], []
    y = top + 23.0  # header row on every page
    for cols, rh in zip(all_lines, all_heights):
        if pending_lines and y + rh > MX_BOTTOM_LIMIT:
            draw_matrix_segment(c, top, pending_lines, pending_heights, True)
            c.showPage()
            top = MX_TABLE_TOP_CONT
            y = top + 23.0
            pending_lines, pending_heights = [], []
        pending_lines.append(cols)
        pending_heights.append(rh)
        y += rh
    if pending_lines:
        draw_matrix_segment(c, top, pending_lines, pending_heights, True)
        c.showPage()
    c.save()
    print("built matrix:", out_path)


# ---------------------------------------------------------------- binder
def build_cover(binder, meta):
    """Render the binder cover + TOC pages with reportlab into memory.
    Returns (pdf_bytes, toc_rects, startup_rect, page_count) where rects are
    (page_index, x0, y0, x1, y1) in TOP-DOWN page coordinates for links."""
    accent = HexColor('#' + binder.get("accent_hex", DEFAULT_ACCENT))
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(BD_W, BD_H), invariant=1)
    c.setTitle("%s - Warranty Binder" % binder["title"])
    c.setAuthor(meta["author"])
    c.setCreator(CREATOR)

    state = {"y": 0.0, "page": 0}

    def ensure(dy):
        """Advance y by dy; page-break if past the bottom limit."""
        if state["y"] + dy > BD_BOTTOM:
            c.showPage()
            state["page"] += 1
            state["y"] = BD_CONT_TOP
        else:
            state["y"] += dy

    def put(x, text, font, size, color):
        c.setFont(font, size)
        c.setFillColor(color)
        c.drawString(x, BD_H - state["y"], text)

    # title
    state["y"] = BD_TITLE_BASE
    for i, line in enumerate(wrap_text(binder["title"], "Helvetica-Bold", 16,
                                       BD_RIGHT - BD_LM)):
        if i:
            ensure(20.0)
        put(BD_LM, line, "Helvetica-Bold", 16, accent)

    # contacts
    contacts = binder.get("contacts") or []
    if contacts:
        ensure(23.0)
        put(BD_LM, FIXED_PROJECT_CONTACTS, "Helvetica-Bold", 12,
            HexColor('#000000'))
        for grp in contacts:
            ensure(BD_LINE + BD_GROUP_GAP)
            put(BD_LM, str(grp["heading"]), "Helvetica-Bold", 12,
                HexColor('#000000'))
            for key, label in CONTACT_LABELS:
                if not grp.get(key):
                    continue
                for j, line in enumerate(wrap_text(label + str(grp[key]),
                                                   "Helvetica", 12,
                                                   BD_RIGHT - BD_LM)):
                    ensure(BD_LINE)
                    put(BD_LM, line, "Helvetica", 12, HexColor('#000000'))

    # start-up date
    startup_rect = None
    if binder.get("startup_date"):
        ensure(BD_SECT_GAP)
        put(BD_LM, FIXED_STARTUP, "Helvetica-Bold", 14, accent)
        ensure(22.1)
        put(BD_LM, str(binder["startup_date"]), "Helvetica", 12, accent)
        w = stringWidth(str(binder["startup_date"]), "Helvetica", 12)
        startup_rect = (state["page"], BD_LM, state["y"] - 12.2,
                        BD_LM + w, state["y"] + 4.2)

    # table of contents
    ensure(BD_SECT_GAP)
    put(BD_LM, FIXED_TOC, "Helvetica-Bold", 14, accent)
    toc_rects = []
    first = True
    for sect in binder["sections"]:
        ensure(14.9 if first else BD_TOC_LINE + BD_TOC_GROUP_GAP)
        first = False
        put(84.0, str(sect["number"]) + ".", "Helvetica", 12,
            HexColor('#000000'))
        lines = wrap_text(str(sect["title"]), "Helvetica", 12,
                          BD_RIGHT - 108.0)
        put(108.0, lines[0], "Helvetica", 12, accent)
        w = stringWidth(lines[0], "Helvetica", 12)
        toc_rects.append((state["page"], 108.0, state["y"] - 12.2,
                          108.0 + w, state["y"] + 4.2))
        for line in lines[1:]:
            ensure(BD_TOC_LINE)
            put(108.0, line, "Helvetica", 12, accent)
        for sub in sect.get("subitems") or []:
            for j, line in enumerate(wrap_text(str(sub), "Helvetica", 12,
                                               BD_RIGHT - 144.0)):
                ensure(BD_TOC_LINE)
                if j == 0:
                    put(120.0, BULLET, "Helvetica", 12, HexColor('#000000'))
                put(144.0, line, "Helvetica", 12, HexColor('#000000'))

    c.showPage()
    c.save()
    return buf.getvalue(), toc_rects, startup_rect, state["page"] + 1


def build_binder(binder, meta, out_path, json_dir):
    sections = binder.get("sections") or fail("binder.sections is required")
    fronts = binder.get("front_attachments") or []

    def resolve(p):
        p = str(p)
        return p if os.path.isabs(p) else os.path.join(json_dir, p)

    missing = [resolve(s["path"]) for s in list(fronts) + list(sections)
               if not os.path.isfile(resolve(s["path"]))]
    if missing:
        fail("binder source PDF(s) not found:\n  " + "\n  ".join(missing))

    cover_bytes, toc_rects, startup_rect, n_cover = build_cover(binder, meta)

    out = fitz.open()
    cover = fitz.open("pdf", cover_bytes)
    out.insert_pdf(cover)
    cover.close()

    starts = []  # 0-based start page of every front attachment and section
    for s in list(fronts) + list(sections):
        src = fitz.open(resolve(s["path"]))
        starts.append(out.page_count)
        out.insert_pdf(src)
        src.close()
    front_starts = starts[:len(fronts)]
    sect_starts = starts[len(fronts):]

    # TOC links (cover -> section first pages)
    for (pidx, x0, y0, x1, y1), target in zip(toc_rects, sect_starts):
        out[pidx].insert_link({"kind": fitz.LINK_GOTO,
                               "from": fitz.Rect(x0, y0, x1, y1),
                               "page": target, "to": fitz.Point(0, 0)})
    # start-up date link -> first front attachment (else first section)
    if startup_rect and (front_starts or sect_starts):
        pidx, x0, y0, x1, y1 = startup_rect
        out[pidx].insert_link({"kind": fitz.LINK_GOTO,
                               "from": fitz.Rect(x0, y0, x1, y1),
                               "page": (front_starts or sect_starts)[0],
                               "to": fitz.Point(0, 0)})

    # back links on every merged content page
    w = stringWidth(BACK_LABEL, "Helvetica", 8)
    for pno in range(n_cover, out.page_count):
        page = out[pno]
        h = page.rect.height
        try:
            page.insert_text(fitz.Point(72.0, h - 31.0), BACK_LABEL,
                             fontname="helv", fontsize=8, color=LINK_BLUE)
            page.insert_link({"kind": fitz.LINK_GOTO,
                              "from": fitz.Rect(72.0, h - 42.0,
                                                72.0 + w, h - 27.0),
                              "page": 0, "to": fitz.Point(0, 0)})
        except Exception as e:
            print("warning: back link skipped on page %d: %s" % (pno + 1, e))

    pdf_date = meta.get("pdf_date", DEFAULT_PDF_DATE)
    out.set_metadata({"title": "%s - Warranty Binder" % binder["title"],
                      "author": meta["author"],
                      "subject": str(binder["title"]),
                      "creator": CREATOR,
                      "producer": "PyMuPDF",
                      "creationDate": pdf_date, "modDate": pdf_date})
    out.save(out_path, garbage=4, deflate=True, no_new_id=True)
    out.close()
    print("built binder:", out_path)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Build the warranty matrix and optional binder.")
    ap.add_argument("data", nargs="?", default=os.path.join(HERE, "sample_data.json"),
                    help="data JSON (default: sample_data.json next to this script)")
    ap.add_argument("out_dir", nargs="?", default=os.path.join(HERE, "_sample_output"),
                    help="output folder (default: _sample_output next to this script)")
    ap.add_argument("--company", default=DEFAULT_COMPANY,
                    help="company config JSON (default: template-library/company.example.json)")
    args = ap.parse_args()

    data_path, out_dir = args.data, args.out_dir
    if not os.path.isfile(data_path):
        fail("data file not found: " + data_path)
    if not os.path.isfile(args.company):
        fail("company config not found: " + args.company)
    os.makedirs(out_dir, exist_ok=True)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(args.company, "r", encoding="utf-8") as f:
        company = json.load(f)
    check_no_dashes(data)
    meta = dict(data.get("meta", {}))
    meta.setdefault("author", company.get("legal_name", ""))
    json_dir = os.path.dirname(os.path.abspath(data_path))

    matrix = data.get("matrix") or fail("matrix section is required")
    matrix.setdefault("contractor", company.get("legal_name", ""))
    for key in ("project", "commencement", "contractor"):
        if key not in matrix:
            fail("matrix.%s is required" % key)
    mx_out = os.path.join(out_dir,
                          matrix.get("output_name", "Warranty Matrix.pdf"))
    build_matrix(matrix, meta, mx_out)

    binder = data.get("binder")
    if binder:
        for key in ("title", "sections"):
            if key not in binder:
                fail("binder.%s is required" % key)
        bd_out = os.path.join(out_dir,
                              binder.get("output_name",
                                         "Warranty Binder.pdf"))
        build_binder(binder, meta, bd_out, json_dir)
    else:
        print("no binder section in data; matrix only")

    # self check
    for p in [mx_out] + ([bd_out] if binder else []):
        d = fitz.open(p)
        if d.page_count < 1:
            fail("output has no pages: " + p)
        print("verified %s: %d page(s)" % (os.path.basename(p),
                                           d.page_count))
        d.close()


if __name__ == "__main__":
    main()
