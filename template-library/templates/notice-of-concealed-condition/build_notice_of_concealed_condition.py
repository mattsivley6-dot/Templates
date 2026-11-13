# -*- coding: utf-8 -*-
"""
Certified-Mail Notice of Concealed Condition (Claim Letter) builder.

One-page certified-mail letter on a simple generic letterhead. Formal
written notice under the contract's concealed-condition, claims, and notice
sections; reserves rights and serves as the Notice of Claim. Usually issued
in paired variants per event (one letter to the Owner, one to the Engineer,
same body, different address block, salutation, and cc list), so one run of
this script emits one PDF per recipient in the JSON.

Letterhead: built from the company config (template-library/
company.example.json by default, or --company). Company name, address,
phone, website, brand colors, optional logo and optional signature image all
come from that file. Nothing about the company is hard-coded here.

Usage:  python build_notice_of_concealed_condition.py [data.json]
                [--company path/to/company.json]
        (data defaults to sample_data.json next to this script)

Output: <job_slug>_[<file_ref>_]Notice_of_Concealed_Condition_<tag>.pdf
        per recipient, in meta.output_dir (default _sample_output).

House style: no em or en dashes anywhere (the script refuses data that
contains them). Use commas, periods, or hyphens instead.

Determinism: no datetime.now/random anywhere; reportlab canvas built with
invariant=1; final PDF metadata dates come from meta.created in the JSON;
the trailer /ID is rewritten to a content hash so identical data gives
byte-identical PDFs.

Libraries: stdlib + reportlab + PyMuPDF (fitz) only.
"""
import argparse
import hashlib
import io
import json
import os
import re

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

# ---- colors (primary and accent come from the company config) ---------------
DEFAULT_PRIMARY = "#1F3A5F"
DEFAULT_ACCENT = "#2E7D32"
GRAY = colors.HexColor("#5A5A5A")       # address block, cert line, cc block
FOOT_GRAY = colors.HexColor("#8C8C8C")  # footer text
RULE_LGRAY = colors.HexColor("#D9D9D9") # footer hairline
INK = colors.HexColor("#1A1A1A")        # body text

PW, PH = letter                  # 612 x 792 pt, portrait
LEFT = 72.0                      # 1 inch
RIGHT = 540.0                    # 612 - 1 inch
COL = RIGHT - LEFT               # 468 pt text column

# masthead / footer geometry (baselines, bottom-up coordinates)
NAME_Y = 730.0                   # company name, bold 20
SUBNAME_Y = 716.0                # legal name line (if it differs), 8 pt
ADDR_TOP_Y = 742.0               # first right-aligned address baseline
ADDR_LEAD = 11.0
MAST_RULE_Y = 700.0              # accent rule, width 1.5
FOOT_RULE_Y = 56.0               # light gray rule, width 0.75
FOOT_TEXT_Y = 45.0               # footer baseline, 7.5 pt
LOGO_MAX_H = 40.0                # optional logo height in the masthead
LOGO_MAX_W = 180.0

# letter block geometry (gaps are baseline-to-baseline)
DATE_Y = 682.0                   # date baseline, 10.5 pt
GAP_CERT = 26.0                  # date -> SENT BY CERTIFIED MAIL line
GAP_RECIPIENT = 27.0             # cert line -> first recipient line
LEAD_RECIPIENT = 13.5
GAP_RE = 30.0                    # last recipient line -> first Re: line
LEAD_RE = 14.5                   # Re: block wraps at body leading
GAP_SALUTATION = 24.0            # last Re: line -> salutation
GAP_PARA_PLAIN = 23.0            # gap before a paragraph after a plain block
GAP_PARA_AFTER_NUM = 22.0        # gap before a paragraph after a numbered item
LEAD_BODY = 14.5
GAP_CLOSING = 28.0               # last body line -> "Respectfully,"
GAP_SIGNATURE = 64.0             # "Respectfully," -> typed name (signature room)
LEAD_SIG = 13.5
GAP_CC = 27.0                    # last signature line -> first cc line
LEAD_CC = 12.5

HANG_INDENT = 16.0               # continuation indent for numbered items
SQUEEZE_TOL = 3.0                # keep a word on the line if it overflows by
                                 # no more than this, tightening word spacing
MIN_Y = 62.0                     # lowest allowed baseline (above footer rule)

# optional signature image box (sits in the gap under "Respectfully,")
SIG_IMG_W = 144.0
SIG_IMG_H = 46.0
SIG_IMG_TOP_DROP = 2.0           # image top sits this far below "Respectfully,"

# ---- fixed wording ----------------------------------------------------------
CERT_LINE = "SENT BY CERTIFIED MAIL, RETURN RECEIPT REQUESTED"
CLOSING = "Respectfully,"
CC_PREFIX = "cc:  "
DOC_SLUG = "Notice_of_Concealed_Condition"

NUMBERED = re.compile(r"^\d+\.\s")


# ---- company config -----------------------------------------------------------
def default_company_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "company.example.json"))


def load_company(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        co = json.load(fh)
    co["_dir"] = os.path.dirname(os.path.abspath(path))
    return co


def resolve_image(path_value, bases):
    """Return an existing absolute path for an optional image, or None when
    the value is empty. Raise if a value is given but the file is missing."""
    if not path_value:
        return None
    cands = [path_value] if os.path.isabs(path_value) else \
        [os.path.join(b, path_value) for b in bases]
    for cand in cands:
        if os.path.exists(cand):
            return cand
    raise SystemExit("image not found: %s" % path_value)


def hex_color(value, default):
    try:
        return colors.HexColor(value or default)
    except Exception:
        return colors.HexColor(default)


def company_lines(co):
    addr = [co.get("address_line1"), co.get("city_state_zip"),
            co.get("phone"), co.get("website")]
    return [a for a in addr if a]


def footer_text(co):
    parts = [co.get("legal_name") or co.get("dba") or ""]
    street = ", ".join(x for x in (co.get("address_line1"),
                                   co.get("city_state_zip")) if x)
    for x in (street, co.get("phone"), co.get("website")):
        if x:
            parts.append(x)
    return "   |   ".join(p for p in parts if p)


def default_signature_lines(co):
    contact = "  |  ".join(x for x in (
        ("Direct " + co["pm_phone"]) if co.get("pm_phone") else "",
        co.get("pm_email", "")) if x)
    lines = [co.get("pm_name", ""), co.get("pm_title", ""),
             co.get("legal_name") or co.get("dba") or "", contact]
    return [ln for ln in lines if ln]


# ---- greedy wrap with a small word-space squeeze ------------------------------
def wrap(text, font, size, first_width, rest_width):
    """Greedy word wrap. If the word that would overflow fits within
    SQUEEZE_TOL points, keep it and return a negative word-space adjustment
    for that line. Returns a list of (line_text, word_space) tuples."""
    words = text.split(" ")
    lines = []
    cur = ""
    width = first_width
    for w in words:
        cand = w if not cur else cur + " " + w
        cw = stringWidth(cand, font, size)
        if cw <= width or not cur:
            cur = cand
            continue
        over = cw - width
        nsp = cand.count(" ")
        if over <= SQUEEZE_TOL and nsp:
            lines.append((cand, -over / nsp))
            cur = ""
            width = rest_width
            continue
        lines.append((cur, 0.0))
        cur = w
        width = rest_width
    if cur:
        lines.append((cur, 0.0))
    return lines


class Cursor(object):
    """Y-cursor text layout on a reportlab canvas."""

    def __init__(self, c):
        self.c = c
        self.y = DATE_Y

    def line(self, x, text, font, size, color, word_space=0.0):
        if self.y < MIN_Y:
            raise SystemExit(
                "Letter overflows one page (baseline %.1f). Certified notices "
                "are one page; shorten the body paragraphs." % self.y)
        t = self.c.beginText(x, self.y)
        t.setFont(font, size)
        t.setFillColor(color)
        if word_space:
            t.setWordSpace(word_space)
        t.textLine(text)
        self.c.drawText(t)

    def block(self, text, font, size, color, gap, lead,
              hang=0.0):
        """Drop the cursor by gap, then draw a wrapped paragraph."""
        self.y -= gap
        parts = wrap(text, font, size, COL, COL - hang)
        for i, (ln, ws) in enumerate(parts):
            if i:
                self.y -= lead
            x = LEFT if i == 0 else LEFT + hang
            self.line(x, ln, font, size, color, ws)


def masthead(c, co, logo_path):
    """Generic letterhead from the company config: logo or company name on
    the left, contact block on the right, accent rule, one-line footer."""
    brand = co.get("brand") or {}
    primary = hex_color(brand.get("primary_color"), DEFAULT_PRIMARY)
    accent = hex_color(brand.get("accent_color"), DEFAULT_ACCENT)
    name = co.get("dba") or co.get("legal_name") or ""
    legal = co.get("legal_name") or ""

    c.saveState()
    if logo_path:
        iw, ih = ImageReader(logo_path).getSize()
        scale = min(LOGO_MAX_H / float(ih), LOGO_MAX_W / float(iw))
        w, h = iw * scale, ih * scale
        c.drawImage(logo_path, LEFT, MAST_RULE_Y + 8, width=w, height=h,
                    mask="auto")
    else:
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(LEFT, NAME_Y, name)
        if legal and legal != name:
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 8)
            c.drawString(LEFT, SUBNAME_Y, legal)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8.5)
    for i, ln in enumerate(company_lines(co)):
        c.drawRightString(RIGHT, ADDR_TOP_Y - i * ADDR_LEAD, ln)
    c.setStrokeColor(accent)
    c.setLineWidth(1.5)
    c.line(LEFT, MAST_RULE_Y, RIGHT, MAST_RULE_Y)
    c.setStrokeColor(RULE_LGRAY)
    c.setLineWidth(0.75)
    c.line(LEFT, FOOT_RULE_Y, RIGHT, FOOT_RULE_Y)
    c.setFillColor(FOOT_GRAY)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(PW / 2.0, FOOT_TEXT_Y, footer_text(co))
    c.restoreState()


def build_one(data, co, recipient, logo_path, sig_img_path):
    """Render one letter (one recipient), return PDF bytes."""
    L = data["letter"]
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=letter, invariant=1)
    c.setTitle(data["meta"]["pdf_title"])
    c.setAuthor(co.get("dba") or co.get("legal_name") or "")
    masthead(c, co, logo_path)

    cur = Cursor(c)
    # date
    cur.line(LEFT, L["date_display"], "Helvetica", 10.5, INK)
    # certified-mail banner
    cur.y -= GAP_CERT
    cur.line(LEFT, CERT_LINE, "Helvetica-Bold", 9, GRAY)
    # recipient address block
    cur.y -= GAP_RECIPIENT
    for i, ln in enumerate(recipient["address_lines"]):
        if i:
            cur.y -= LEAD_RECIPIENT
        cur.line(LEFT, ln, "Helvetica", 10.5, INK)
    # Re: block (bold, wrapped)
    cur.block(L["re_text"], "Helvetica-Bold", 10.5, INK, GAP_RE, LEAD_RE)
    # salutation
    cur.y -= GAP_SALUTATION
    cur.line(LEFT, recipient["salutation"], "Helvetica", 10.5, INK)
    # body paragraphs; numbered items get a hanging indent, and the gap
    # before a paragraph is tighter when the previous one was numbered
    prev_numbered = False
    for p in L["body_paragraphs"]:
        gap = GAP_PARA_AFTER_NUM if prev_numbered else GAP_PARA_PLAIN
        numbered = bool(NUMBERED.match(p))
        cur.block(p, "Helvetica", 10.5, INK, gap, LEAD_BODY,
                  hang=HANG_INDENT if numbered else 0.0)
        prev_numbered = numbered
    # closing
    cur.y -= GAP_CLOSING
    cur.line(LEFT, CLOSING, "Helvetica", 10.5, INK)
    resp_y = cur.y
    # signature image (optional; without it the gap stays for a wet signature)
    if sig_img_path:
        c.drawImage(sig_img_path, LEFT,
                    resp_y - SIG_IMG_TOP_DROP - SIG_IMG_H,
                    width=SIG_IMG_W, height=SIG_IMG_H,
                    preserveAspectRatio=True, anchor="w", mask="auto")
    # typed signature block
    cur.y -= GAP_SIGNATURE
    sig_lines = L.get("signature_lines") or default_signature_lines(co)
    for i, ln in enumerate(sig_lines):
        if i:
            cur.y -= LEAD_SIG
        cur.line(LEFT, ln, "Helvetica", 10.5, INK)
    # cc block
    cc = recipient.get("cc_lines") or []
    if cc:
        cur.y -= GAP_CC
    for i, ln in enumerate(cc):
        if i:
            cur.y -= LEAD_CC
        text = (CC_PREFIX + ln) if i == 0 else ln
        cur.line(LEFT, text, "Helvetica", 8.5, GRAY)

    c.showPage()
    c.save()
    return buf.getvalue()


# ---- deterministic assembly ---------------------------------------------------
def meta_dates(data, co):
    created = data["meta"].get("created", "2026-01-01")
    d = "D:%s000000" % created.replace("-", "")
    return {"title": data["meta"]["pdf_title"],
            "author": co.get("dba") or co.get("legal_name") or "",
            "subject": "", "keywords": "",
            "producer": "", "creator": "",
            "creationDate": d, "modDate": d}


def make_deterministic_id(path):
    """MuPDF writes a fresh random /ID on every save; everything else is
    byte-stable (reportlab invariant=1). Replace the trailer /ID with an MD5
    of the file content so identical data gives byte-identical PDFs."""
    with open(path, "rb") as f:
        raw = f.read()
    matches = list(re.finditer(
        rb"/ID\[<([0-9A-Fa-f]{32})><([0-9A-Fa-f]{32})>\]", raw))
    if not matches:
        return
    m = matches[-1]
    zeroed = (raw[:m.start(1)] + b"0" * 32 + raw[m.end(1):m.start(2)]
              + b"0" * 32 + raw[m.end(2):])
    dig = hashlib.md5(zeroed).hexdigest().upper().encode("ascii")
    fixed = (raw[:m.start(1)] + dig + raw[m.end(1):m.start(2)]
             + dig + raw[m.end(2):])
    with open(path, "wb") as f:
        f.write(fixed)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        description="Build certified-mail Notice of Concealed Condition letters (PDF).")
    ap.add_argument("data", nargs="?", default=os.path.join(here, "sample_data.json"),
                    help="letter data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=default_company_path(),
                    help="company config JSON (default: ../../company.example.json)")
    args = ap.parse_args()

    data_path = args.data
    raw = io.open(data_path, "r", encoding="utf-8").read()
    for ch, name in ((chr(0x2014), "em dash"), (chr(0x2013), "en dash")):
        if ch in raw:
            raise SystemExit("House style violation: %s found in %s. Use "
                             "commas, periods, or hyphens instead."
                             % (name, data_path))
    data = json.loads(raw)
    co = load_company(args.company)

    out_dir = data["meta"].get("output_dir") or os.path.join(
        here, "_sample_output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(here, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    data_dir = os.path.dirname(os.path.abspath(data_path))
    # optional images: null/empty in the config means skip cleanly
    logo_path = resolve_image(co.get("logo_path"), [co["_dir"], here])
    # signature: letter.signature_image overrides the company signature_path
    sig_key = data["letter"].get("signature_image")
    if sig_key:
        sig_img_path = resolve_image(sig_key, [data_dir, here])
    else:
        sig_img_path = resolve_image(co.get("signature_path"), [co["_dir"], here])

    file_ref = data["meta"].get("file_ref") or ""
    prefix = (file_ref + "_") if file_ref else ""
    for recipient in data["recipients"]:
        pdf_bytes = build_one(data, co, recipient, logo_path, sig_img_path)
        name = "%s_%s%s_%s.pdf" % (data["meta"]["job_slug"], prefix,
                                   DOC_SLUG, recipient["tag"])
        out_path = os.path.join(out_dir, name)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        doc.set_metadata(meta_dates(data, co))
        doc.save(out_path, garbage=4, deflate=True)
        print("wrote", out_path, "| pages", doc.page_count)
        doc.close()
        make_deterministic_id(out_path)


if __name__ == "__main__":
    main()
