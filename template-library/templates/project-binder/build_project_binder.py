#!/usr/bin/env python3
"""
Project Binder (registers + core sections).

Builds the core tabs of a printable project record binder, one PDF per
tab, then merges them into "<output_prefix> Project Binder.pdf" with one
bookmark per tab:

    00  Cover and Contents   (cover page, table of contents, how to read)
    01  Project Summary      (fact grid, status bullets, scope, milestones)
    02  Directory            (contact register, formal notice addresses)
    09  RFI Log              (register plus one page per RFI)
    10  Submittal Log        (register plus notes)
    11  Change Orders        (register, contingency ledger, one page per PCO)

Any section missing from the data file is skipped. Tab numbers, titles,
and subtitles come from the data file, so a job with different tab
numbering just changes the JSON.

Usage:
    python build_project_binder.py [data.json] [out_dir] [--company company.json]

Defaults: data.json = sample_data.json next to this script,
out_dir = _sample_output next to this script, --company =
../../company.example.json (the template-library company config, two
folders up from this script). The masthead wordmark, footer company name,
PDF author and brand colors come from the company config; nothing about
the company is hard-coded here.

Deterministic: no calls to datetime.now(), no random; reportlab
invariant=1; merged PDF metadata dates come from the data file.
Requires: reportlab, PyMuPDF (fitz).
"""
import os
import re
import sys
import json
import argparse
import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, Table, TableStyle,
                                KeepTogether, PageBreak)
from reportlab.pdfgen import canvas as rl_canvas

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COMPANY = os.path.normpath(os.path.join(HERE, "..", "..",
                                                "company.example.json"))

EM, EN = "\u2014", "\u2013"   # dash characters the house rule removes

# ======================================================================
# STYLE CONSTANTS
# ======================================================================
# ACCENT and HEADING are neutral defaults; configure_company() replaces them
# with brand.accent_color and brand.primary_color from the company config.
ACCENT    = colors.HexColor("#666666")   # wordmark, masthead rule
HEADING  = colors.HexColor("#333333")   # h2 headings, register table headers
GRAY     = colors.HexColor("#595959")   # secondary text, footer
LGRAY    = colors.HexColor("#BFBFBF")   # footer rule, horizontal rules
FAINT    = colors.HexColor("#F2F5EF")   # reserved tint (unused here)
ROW      = colors.HexColor("#F7F7F5")   # alternating register row stripe
INK      = colors.HexColor("#1A1A1A")   # body text
RED      = colors.HexColor("#B23A2F")   # reserved status color
AMBER    = colors.HexColor("#B07A1E")   # reserved status color
HAIRLINE = colors.HexColor("#E3E3E0")   # register row separator line

PAGE_W, PAGE_H = letter
LEFT  = 1.15 * inch          # binder punch side
RIGHT = PAGE_W - 0.70 * inch
TOP_Y = PAGE_H - 0.55 * inch
W = RIGHT - LEFT             # 6.65 inch working width

CREATOR = "Template Library project-binder"

# ======================================================================
# RUNTIME CONFIG
# ======================================================================
FOOTER_COMPANY = ""              # company legal name, from the company config
WORDMARK = ["", ""]              # masthead left, 2 lines, from the company config
PREPARED = ""                    # footer center, "Prepared March 2, 2026"
PROJECT_RIGHT = ["", ""]         # masthead right, 2 lines
FOOTER_BINDER_LABEL = "Binder"   # footer right label on pages with no tab
PDF_SUBJECT = ""
_ALLOW = []                      # regexes whose dashes are protected
_REF_FIX = []                    # normalization rules applied by clean()
_JOINS = {}                      # hyphenated words joined before de-dashing

# generic reference fixes, always applied (job specific ones come from JSON)
_REF_FIX_BASE = [
    (r"\bPCO[-\u2013\u2014](\d+)", r"PCO \1"),
    (r"\bRFI[-\u2013\u2014](\d+)", r"RFI \1"),
    (r"\bPA[-\u2013\u2014](\d+)", r"PA \1"),
    (r"\bRTU[-\u2013\u2014]", "RTU "),
]

# generic hyphenated words, joined or spaced before the de-dash pass
_JOINS_BASE = {
    "start-up": "startup", "Start-up": "Startup",
    "walk-through": "walkthrough", "re-roof": "re roof",
    "re-detail": "re detail", "sub-contractor": "subcontractor",
    "as-built": "as built", "As-built": "As built",
    "hot-work": "hot work", "in-house": "in house",
    "on-site": "on site", "off-site": "off site",
    "tie-in": "tie in", "clock-in": "clock in", "no-cost": "no cost",
}


def configure_company(company):
    """Load company name, wordmark and brand colors from the company config."""
    global FOOTER_COMPANY, WORDMARK, ACCENT, HEADING
    legal = str(company.get("legal_name") or "")
    dba = str(company.get("dba") or legal)
    FOOTER_COMPANY = legal
    WORDMARK = [dba.upper(), legal.upper() if legal != dba else ""]
    brand = company.get("brand") or {}
    if brand.get("accent_color"):
        ACCENT = colors.HexColor(brand["accent_color"])
    if brand.get("primary_color"):
        HEADING = colors.HexColor(brand["primary_color"])


def configure(meta):
    """Load job level style config from the data file's meta block."""
    global PREPARED, PROJECT_RIGHT, FOOTER_BINDER_LABEL, PDF_SUBJECT
    global _ALLOW, _REF_FIX, _JOINS
    PREPARED = meta["prepared_line"]
    PROJECT_RIGHT = [meta["header_project_line1"], meta["header_project_line2"]]
    FOOTER_BINDER_LABEL = meta.get("footer_binder_label", "Binder")
    PDF_SUBJECT = meta.get("pdf_subject", "")
    _ALLOW = list(meta.get("allowed_dash_tokens", []))
    _REF_FIX = ([(re.compile(p), r) for p, r in meta.get("ref_fixes", [])]
                + [(re.compile(p), r) for p, r in _REF_FIX_BASE])
    _JOINS = dict(_JOINS_BASE)
    _JOINS.update(meta.get("word_joins", {}))


# ======================================================================
# TEXT RULES
# No em dash, no en dash, no hyphens inside words or numbers.
# ======================================================================
def clean(s):
    """Normalize refs, convert remaining dashes to safe forms."""
    if s is None:
        return ""
    s = str(s)
    for pat, rep in _REF_FIX:
        s = pat.sub(rep, s)
    # protect allowed identifiers (project numbers, permit numbers, etc.)
    keep = {}
    for i, pat in enumerate(_ALLOW):
        for m in set(re.findall(pat, s)):
            key = "\x01%d_%d\x02" % (i, len(keep))
            keep[key] = m
            s = s.replace(m, key)
    s = s.replace(EM, ", ").replace(EN, " to ")
    # ISO dates and numeric ranges
    s = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\2/\3/\1", s)
    s = re.sub(r"(\d)\s*-\s*(\d)", r"\1 to \2", s)
    # hyphenated words: join common ones, then space out the rest
    for a, b in _JOINS.items():
        s = s.replace(a, b)
    s = re.sub(r"(\w)-(\w)", r"\1 \2", s)
    s = s.replace(" - ", ", ").replace("-", " ")
    for key, val in keep.items():
        s = s.replace(key, val)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", s)   # XML safe for Paragraph
    return s.strip()


def money(x):
    if isinstance(x, str):
        return clean(x)
    neg = x < 0
    t = "${:,.2f}".format(abs(x))
    return "({})".format(t) if neg else t


def shorten(s, n=95):
    s = clean(s)
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(",.;: ") + " ..."


def fmt_date(iso, fmt="%B %d, %Y"):
    try:
        return datetime.date(*map(int, iso.split("-"))).strftime(fmt)
    except Exception:
        return clean(iso)


# ======================================================================
# PARAGRAPH STYLES
# ======================================================================
def S(name, **kw):
    base = dict(fontName="Helvetica", textColor=INK, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


def make_styles():
    return {
        "h1":    S("h1", fontName="Helvetica-Bold", fontSize=22, leading=26, spaceAfter=4),
        "h2":    S("h2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                   spaceBefore=10, spaceAfter=5, textColor=HEADING),
        "kicker": S("kicker", fontName="Helvetica-Bold", fontSize=9, leading=12,
                    textColor=GRAY),
        "body":  S("body", fontSize=10.5, leading=14.5, spaceAfter=5),
        "big":   S("big", fontSize=12.5, leading=17, spaceAfter=6),
        "cell":  S("cell", fontSize=9.3, leading=12),
        "cellb": S("cellb", fontName="Helvetica-Bold", fontSize=9.3, leading=12),
        "cellg": S("cellg", fontSize=9.3, leading=12, textColor=GRAY),
        "hcell": S("hcell", fontName="Helvetica-Bold", fontSize=8.6, leading=11,
                   textColor=colors.white),
        "label": S("label", fontName="Helvetica-Bold", fontSize=8.4, leading=11,
                   textColor=GRAY),
        "value": S("value", fontName="Helvetica-Bold", fontSize=11.5, leading=15),
        "note":  S("note", fontSize=8.6, leading=11.6, textColor=GRAY),
        "bullet": S("bullet", fontSize=10.3, leading=14.2, spaceAfter=3,
                    leftIndent=14, bulletIndent=2),
        "bignum": S("bignum", fontName="Helvetica-Bold", fontSize=19, leading=22),
    }


ST = make_styles()   # rebuilt in main() after the brand colors are loaded


def P(text, style="body"):
    return Paragraph(clean(text), ST[style])


def B(text):
    return Paragraph(clean(text), ST["bullet"], bulletText="•")


# ======================================================================
# PAGE FURNITURE
# ======================================================================
class NumberedCanvas(rl_canvas.Canvas):
    """Two pass canvas so each page can print 'Page X of Y'."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self.draw_page_number(n)
            super().showPage()
        super().save()

    def draw_page_number(self, total):
        tab = getattr(self, "_tab_label", "")
        self.setFont("Helvetica", 7.6)
        self.setFillColor(GRAY)
        self.drawRightString(RIGHT, 0.52 * inch,
                             "{}  ·  Page {} of {}".format(
                                 tab, self._pageNumber, total))


def _furniture(tab_no, tab_title, subtitle=""):
    def draw(c, doc):
        c.saveState()
        c._tab_label = "Tab {}".format(tab_no) if tab_no else FOOTER_BINDER_LABEL
        # masthead wordmark (company DBA, legal name under it), from the company config
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(LEFT, TOP_Y - 4, WORDMARK[0])
        if WORDMARK[1]:
            t = c.beginText(LEFT + 1, TOP_Y - 13)
            t.setFont("Helvetica", 5.6)
            t.setFillColor(GRAY)
            t.setCharSpace(2.6)
            t.textLine(WORDMARK[1])
            t.setCharSpace(0)          # Tc persists in the content stream; reset it
            c.drawText(t)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.2)
        c.drawRightString(RIGHT, TOP_Y - 2, PROJECT_RIGHT[0])
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7.6)
        c.drawRightString(RIGHT, TOP_Y - 13, PROJECT_RIGHT[1])
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.4)
        c.line(LEFT, TOP_Y - 22, RIGHT, TOP_Y - 22)
        # tab band
        if tab_no:
            c.setFillColor(GRAY)
            c.setFont("Helvetica-Bold", 7.8)
            c.drawString(LEFT, TOP_Y - 38, "TAB {}".format(tab_no))
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(LEFT, TOP_Y - 56, tab_title.upper())
            if subtitle:
                c.setFillColor(GRAY)
                c.setFont("Helvetica", 8.8)
                c.drawRightString(RIGHT, TOP_Y - 56, clean(subtitle))
        # footer
        c.setStrokeColor(LGRAY)
        c.setLineWidth(0.5)
        c.line(LEFT, 0.68 * inch, RIGHT, 0.68 * inch)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7.6)
        c.drawString(LEFT, 0.52 * inch, FOOTER_COMPANY)
        c.drawCentredString((LEFT + RIGHT) / 2, 0.52 * inch, PREPARED)
        c.restoreState()
    return draw


def make_doc(path, tab_no, tab_title, subtitle="", title=None):
    top_pad = 1.35 * inch if tab_no else 1.0 * inch
    doc = BaseDocTemplate(
        path, pagesize=letter,
        leftMargin=LEFT, rightMargin=PAGE_W - RIGHT,
        topMargin=top_pad, bottomMargin=0.85 * inch,
        title=title or tab_title, author=FOOTER_COMPANY,
        creator=CREATOR,
        subject=PDF_SUBJECT,
        invariant=1)          # identical data gives byte identical PDFs
    frame = Frame(LEFT, 0.85 * inch, RIGHT - LEFT,
                  PAGE_H - top_pad - 0.85 * inch, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame],
                                       onPage=_furniture(tab_no, tab_title,
                                                         subtitle))])
    return doc


def build(path, tab_no, tab_title, flow, subtitle="", title=None):
    doc = make_doc(path, tab_no, tab_title, subtitle, title)
    doc.build(flow, canvasmaker=NumberedCanvas)
    print("wrote:", path)


# ======================================================================
# REUSABLE BLOCKS
# ======================================================================
def fact_grid(pairs, cols=2, col_w=None):
    """pairs: [(label, value)]  ->  grid of label over bold value."""
    cells, row = [], []
    for lab, val in pairs:
        row.append([Paragraph(clean(lab).upper(), ST["label"]),
                    Paragraph(clean(str(val)), ST["value"])])
        if len(row) == cols:
            cells.append(row)
            row = []
    if row:
        while len(row) < cols:
            row.append(["", ""])
        cells.append(row)
    w = col_w or (RIGHT - LEFT) / cols
    data = []
    for r in cells:
        data.append([Table([[c[0]], [c[1]]], colWidths=[w - 10],
                           style=TableStyle([
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                           ])) if c != ["", ""] else "" for c in r])
    t = Table(data, colWidths=[w] * cols)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def reg_table(headers, rows, widths, header_bg=None, styles=None):
    """Register table with colored header, alternating rows, repeats header."""
    header_bg = header_bg or HEADING
    hdr = [Paragraph(clean(h).upper(), ST["hcell"]) for h in headers]
    body = []
    for r in rows:
        line = []
        for i, cell in enumerate(r):
            st = (styles[i] if styles else "cell")
            if hasattr(cell, "wrapOn"):
                line.append(cell)
            else:
                line.append(Paragraph(clean(str(cell)), ST[st]))
        body.append(line)
    t = Table([hdr] + body, colWidths=widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, header_bg),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, HAIRLINE),
    ]
    for i in range(len(body)):
        if i % 2 == 1:
            cmds.append(("BACKGROUND", (0, i + 1), (-1, i + 1), ROW))
    t.setStyle(TableStyle(cmds))
    return t


def rule(space=8):
    t = Table([[""]], colWidths=[RIGHT - LEFT], rowHeights=[0.8])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.7, LGRAY)]))
    return [Spacer(1, space), t, Spacer(1, space)]


# ======================================================================
# QUALITY GATE: no dash characters in rendered output (house rule)
# ======================================================================
def sweep_check(*paths):
    """Post build audit: report any dash characters left in rendered text."""
    import fitz
    bad = []
    for p in paths:
        d = fitz.open(p)
        for i, pg in enumerate(d):
            txt = pg.get_text()
            for ch in (EN, EM):
                if ch in txt:
                    bad.append((p, i + 1, ch,
                                [l for l in txt.splitlines() if ch in l][:2]))
            for line in txt.splitlines():
                s = line
                for pat in _ALLOW:
                    s = re.sub(pat, "", s)
                if re.search(r"\w-\w| - |^-|-$", s):
                    bad.append((p, i + 1, "-", [line]))
    return bad


# ======================================================================
# TAB 00, COVER + TOC + HOW TO USE
# ======================================================================
def build_cover(cfg, out_dir):
    f = [Spacer(1, 1.1 * inch)]
    f.append(P(cfg["kicker"], "kicker"))
    f.append(Spacer(1, 6))
    for line in cfg["title_lines"]:
        f.append(P(line, "h1"))
    f.append(Spacer(1, 14))
    f.append(fact_grid([tuple(p) for p in cfg["facts"]]))
    f.append(Spacer(1, 22))
    f += rule(4)
    f.append(P(cfg["record_period"], "big"))
    f.append(P(cfg["record_intro"], "body"))
    f.append(PageBreak())
    # TOC
    f.append(P("What is in this binder", "h2"))
    rows = [("Tab {}".format(n), t, d) for n, t, d in cfg["toc"]]
    f.append(reg_table(["Tab", "Section", "What it holds"], rows,
                       [0.75 * inch, 2.0 * inch, W - 2.75 * inch]))
    f.append(PageBreak())
    f.append(P("How to read this binder", "h2"))
    f.append(P(cfg["how_to_read_lead"], "big"))
    for t in cfg["how_to_read"]:
        f.append(B(t))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["section_name"]))
    build(path, "", "Cover", f, title=cfg["binder_title"])
    return path


# ======================================================================
# TAB 01, PROJECT SUMMARY
# ======================================================================
def build_summary(cfg, out_dir):
    f = []
    f.append(P("The job in one page", "h2"))
    f.append(P(cfg["headline"], "big"))
    f.append(fact_grid([tuple(p) for p in cfg["facts"]]))
    f += rule()
    f.append(P(cfg["status_heading"], "h2"))
    for t in cfg["status_bullets"]:
        f.append(B(t))
    f.append(PageBreak())
    f.append(P("Scope of work", "h2"))
    scope = [tuple(r) for r in cfg["scope_rows"]]
    f.append(reg_table(["Trade", "What we are delivering"], scope,
                       [1.35 * inch, W - 1.35 * inch]))
    milestones = cfg.get("milestones") or []
    if milestones:
        f.append(PageBreak())
        f.append(P("Milestones to date", "h2"))
        rows = [(m.get("date", ""), m.get("event", "")) for m in milestones]
        f.append(reg_table(["Date", "Event"], rows,
                           [1.1 * inch, W - 1.1 * inch]))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["tab_title"]))
    build(path, cfg["tab_no"], cfg["tab_title"], f, cfg["subtitle"])
    return path


# ======================================================================
# TAB 02, DIRECTORY
# ======================================================================
def build_directory(cfg, out_dir):
    f = [P("Who is who", "h2")]
    rows = []
    for c in cfg["contacts"]:
        rows.append((c.get("org", ""), c.get("name", ""),
                     shorten(c.get("title", ""), 60),
                     c.get("phone", "").replace("-", "."),
                     c.get("email", "")))
    f.append(reg_table(["Organization", "Name", "Role", "Phone", "Email"],
                       rows, [1.25 * inch, 1.15 * inch, 1.7 * inch,
                              0.95 * inch, W - 5.05 * inch]))
    f.append(Spacer(1, 10))
    f.append(P(cfg["notice_heading"], "h2"))
    f.append(reg_table(["Party", "Address"],
                       [tuple(r) for r in cfg["notice_addresses"]],
                       [2.6 * inch, W - 2.6 * inch]))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["tab_title"]))
    build(path, cfg["tab_no"], cfg["tab_title"], f, cfg["subtitle"])
    return path


# ======================================================================
# TAB 09, RFI LOG
# ======================================================================
def build_rfi_log(cfg, out_dir, co_tab_no):
    rfis = cfg["rfis"]
    f = [P("RFI register", "h2")]
    rows = []
    for r in rfis:
        rows.append((r.get("number", ""), shorten(r.get("title", ""), 60),
                     fmt_date(r.get("date_sent", ""), "%m/%d/%y"),
                     fmt_date(r.get("date_answered", ""), "%m/%d/%y") or "",
                     r.get("status", ""), r.get("linked_pco", "") or ""))
    f.append(reg_table(["RFI", "Subject", "Sent", "Answered", "Status", "PCO"],
                       rows, [0.5 * inch, W - 3.9 * inch, 0.75 * inch,
                              0.85 * inch, 0.8 * inch, 1.0 * inch]))
    if cfg.get("register_note"):
        f.append(Spacer(1, 8))
        f.append(P(cfg["register_note"], "note"))
    for r in rfis:
        f.append(PageBreak())
        f.append(P("RFI {}".format(r.get("number", "")), "kicker"))
        f.append(P(shorten(r.get("title", ""), 160), "h1"))
        f.append(Spacer(1, 8))
        f.append(fact_grid([
            ("Sent", fmt_date(r.get("date_sent", "")) or "Not sent"),
            ("To", shorten(r.get("sent_to", ""), 50)),
            ("Answered", fmt_date(r.get("date_answered", "")) or "Open"),
            ("Status", r.get("status", "")),
        ]))
        f += rule()
        if r.get("answer"):
            f.append(P("The answer", "h2"))
            f.append(P(r["answer"], "body"))
        if r.get("linked_pco"):
            f.append(P("Cost path", "h2"))
            f.append(P("This RFI became {}. See Tab {}.".format(
                r["linked_pco"], co_tab_no), "body"))
        if r.get("note"):
            f.append(P("Record note", "h2"))
            f.append(P(r["note"], "body"))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["tab_title"]))
    build(path, cfg["tab_no"], cfg["tab_title"], f, cfg["subtitle"])
    return path


# ======================================================================
# TAB 10, SUBMITTAL LOG
# ======================================================================
def build_submittal_log(cfg, out_dir):
    subs = cfg["submittals"]
    f = [P("Submittal register", "h2")]
    rows = []
    for s in subs:
        rows.append((shorten(s.get("item", ""), 70),
                     s.get("spec", "").replace("N/A", ""),
                     fmt_date(s.get("date_submitted", ""), "%m/%d/%y"),
                     fmt_date(s.get("date_returned", ""), "%m/%d/%y"),
                     s.get("action", "") or s.get("status", "")))
    f.append(reg_table(["Item", "Spec", "Sent", "Returned", "Action"], rows,
                       [W - 3.6 * inch, 0.85 * inch, 0.75 * inch,
                        0.8 * inch, 1.2 * inch]))
    f.append(Spacer(1, 8))
    notes = [s for s in subs if s.get("note")]
    if notes:
        f.append(P("Notes", "h2"))
        for s in notes[:12]:
            f.append(B("{}: {}".format(shorten(s.get("item", ""), 46),
                                       shorten(s["note"], 110))))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["tab_title"]))
    build(path, cfg["tab_no"], cfg["tab_title"], f, cfg["subtitle"])
    return path


# ======================================================================
# TAB 11, CHANGE ORDERS
# ======================================================================
def build_change_orders(cfg, out_dir):
    f = [P("Change order register", "h2")]
    rows = []
    for p in cfg["pcos"]:
        rows.append(("PCO {}".format(p.get("number", "")),
                     shorten(p.get("title", ""), 62),
                     p.get("amount", ""),
                     shorten(p.get("amount_type", ""), 28),
                     shorten(p.get("status", ""), 48)))
    f.append(reg_table(["No.", "Scope", "Amount", "Type", "Status"], rows,
                       [0.65 * inch, W - 4.35 * inch, 0.95 * inch,
                        1.25 * inch, 1.5 * inch]))
    if cfg.get("labor_rate_basis"):
        f.append(Spacer(1, 8))
        f.append(P(cfg["labor_rate_basis"], "note"))
    if cfg.get("contingency"):
        f.append(Spacer(1, 10))
        f.append(P("Contingency ledger", "h2"))
        led, run = [], 0.0
        for c in cfg["contingency"]:
            run += c["amount"]
            led.append((shorten(c["item"], 75), money(c["amount"]),
                        money(run)))
        f.append(reg_table(["Item", "Amount", "Running balance"], led,
                           [W - 2.5 * inch, 1.2 * inch, 1.3 * inch]))
        f.append(Spacer(1, 6))
        f.append(P("Remaining with every PCO at full value: {}. {}".format(
            cfg.get("contingency_remaining", ""),
            shorten(cfg.get("contingency_note", ""), 220)), "note"))
    for p in cfg["pcos"]:
        f.append(PageBreak())
        f.append(P("PCO {}".format(p.get("number", "")), "kicker"))
        f.append(P(shorten(p.get("title", ""), 150), "h1"))
        f.append(Spacer(1, 8))
        f.append(fact_grid([
            ("Amount", p.get("amount", "")),
            ("Type", shorten(p.get("amount_type", ""), 55)),
            ("Where it came from", shorten(p.get("origin", ""), 90)),
            ("Funding", p.get("funding", cfg.get("funding_default", ""))),
        ]))
        f += rule()
        f.append(P("Status", "h2"))
        f.append(P(p.get("status", ""), "body"))
        if p.get("key_dates"):
            f.append(P("How it moved", "h2"))
            for k in p["key_dates"]:
                f.append(B(k))
        if p.get("history"):
            f.append(P("Price history", "h2"))
            f.append(P(p["history"], "body"))
        if p.get("note"):
            f.append(P("Note", "h2"))
            f.append(P(p["note"], "note"))
    path = os.path.join(out_dir, "{} {}.pdf".format(cfg["tab_no"],
                                                    cfg["tab_title"]))
    build(path, cfg["tab_no"], cfg["tab_title"], f, cfg["subtitle"])
    return path


# ======================================================================
# PIPELINE
# ======================================================================
def main():
    global ST
    ap = argparse.ArgumentParser(description="Build the core project binder tabs.")
    ap.add_argument("data", nargs="?", default=os.path.join(HERE, "sample_data.json"),
                    help="data JSON (default: sample_data.json next to this script)")
    ap.add_argument("out_dir", nargs="?", default=os.path.join(HERE, "_sample_output"),
                    help="output folder (default: _sample_output next to this script)")
    ap.add_argument("--company", default=DEFAULT_COMPANY,
                    help="company config JSON (default: template-library/company.example.json)")
    args = ap.parse_args()

    data_path, out_dir = args.data, args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    with open(args.company, encoding="utf-8") as fh:
        configure_company(json.load(fh))
    ST = make_styles()   # pick up the brand colors

    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    meta = data["meta"]
    configure(meta)

    co_tab_no = (data.get("change_orders") or {}).get("tab_no", "11")

    built = []   # (bookmark label, path)
    if data.get("cover"):
        cfg = data["cover"]
        cfg["binder_title"] = meta["binder_title"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["section_name"]),
                      build_cover(cfg, out_dir)))
    if data.get("summary"):
        cfg = data["summary"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["tab_title"]),
                      build_summary(cfg, out_dir)))
    if data.get("directory"):
        cfg = data["directory"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["tab_title"]),
                      build_directory(cfg, out_dir)))
    if data.get("rfi_log"):
        cfg = data["rfi_log"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["tab_title"]),
                      build_rfi_log(cfg, out_dir, co_tab_no)))
    if data.get("submittal_log"):
        cfg = data["submittal_log"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["tab_title"]),
                      build_submittal_log(cfg, out_dir)))
    if data.get("change_orders"):
        cfg = data["change_orders"]
        built.append(("{} - {}".format(cfg["tab_no"], cfg["tab_title"]),
                      build_change_orders(cfg, out_dir)))

    if not built:
        sys.exit("no sections present in the data file, nothing to build")

    # merge with one bookmark per tab
    import fitz
    outdoc = fitz.open()
    toc = []
    for label, p in built:
        d = fitz.open(p)
        toc.append([1, label, len(outdoc) + 1])
        outdoc.insert_pdf(d)
    outdoc.set_toc(toc)
    outdoc.set_metadata({
        "title": meta["binder_title"],
        "author": FOOTER_COMPANY,
        "creator": CREATOR,
        "producer": "PyMuPDF",
        "subject": PDF_SUBJECT,
        "creationDate": meta.get("pdf_date", ""),
        "modDate": meta.get("pdf_date", ""),
    })
    merged = os.path.join(out_dir,
                          "{} Project Binder.pdf".format(meta["output_prefix"]))
    try:
        outdoc.save(merged, no_new_id=True)   # keep output byte identical
    except TypeError:                          # older PyMuPDF without the arg
        outdoc.save(merged)
    print("merged: {} ({} pages from {} tab PDFs)".format(
        merged, len(outdoc), len(built)))

    # quality gate: the no dash house rule, enforced on rendered text
    bad = sweep_check(*[p for _, p in built])
    if bad:
        print("== DASH SWEEP FAILED ==")
        for hit in bad[:10]:
            print(" X", hit)
        sys.exit(1)
    print("dash sweep clean:", len(built), "tab PDFs")


if __name__ == "__main__":
    main()
