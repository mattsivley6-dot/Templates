# -*- coding: utf-8 -*-
"""
Bonding Capacity Correspondence packet builder.

Builds a formal one-page (or more) bonding capacity letter on company
letterhead, then appends enclosure PDFs (typically the surety broker's
written confirmation, e.g. an email thread printed to PDF) to form a single
packet suitable for a bid qualification submission.

The letterhead (company name, address, phone, website, optional logo and
brand colors) comes from the company config file, by default
template-library/company.example.json. Every job-specific value comes from
a JSON data file; this script holds only fixed wording and layout.

Usage:  python build_capacity_letter.py [data.json] [--company company.json]
        (data defaults to sample_data.json next to this script; company
        defaults to ../../company.example.json relative to this script)

Company tokens: any string in the data file may contain {legal_name},
{dba}, {address_line1}, {city_state_zip}, {phone}, {email}, {website},
{license}, {pm_name}, {pm_title}, {pm_phone} or {pm_email}; they are filled
from the company config.

Output: <job_slug>_Bonding_Capacity_Packet_<letter_date_iso>.pdf in the
        output dir (default: _sample_output next to this script).

House style: no em or en dashes anywhere (the script refuses data that
contains them). Use commas, periods, or hyphens instead.

Determinism: no datetime.now/random anywhere; the reportlab document is
built with invariant=1; final PDF metadata dates come from meta.created in
the JSON; the trailer /ID is rewritten to a content hash so identical data
gives byte-identical PDFs.

Libraries: stdlib + reportlab + PyMuPDF (fitz) only.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COMPANY = os.path.join(HERE, "..", "..", "company.example.json")

# ---- fixed layout colors ----------------------------------------------------
DEFAULT_ACCENT = "#2E7D32"           # used if the config has no accent color
DEFAULT_PRIMARY = "#1F3A5F"          # used if the config has no primary color
GRAY = colors.HexColor("#595959")    # secondary text
LGRAY = colors.HexColor("#BFBFBF")   # hairlines
INK = colors.HexColor("#1A1A1A")     # body text
FILL_LABEL = colors.HexColor("#eef2f7")
RULE_GRID = colors.HexColor("#cccccc")

PW, PH = letter                      # 612 x 792 pt, portrait
LEFT = 0.75 * inch
RIGHT = PW - 0.75 * inch
W = RIGHT - LEFT

# ---- fixed wording (never varies between jobs) ------------------------------
DOC_LABEL = "Bonding Capacity Correspondence"
CAPACITY_HEADING = "Bonding Capacity Summary"
TABLE_HDR_ITEM = "Item"
TABLE_HDR_VALUE = "Confirmed Capacity"
SURETY_HEADING = "Confirmed by Surety Broker of Record"
CLOSING = "Sincerely,"
ENCLOSURES_LABEL = "Enclosures:"

_TOKEN = re.compile(r"\{([a-z_0-9]+)\}")


# ---- company config ---------------------------------------------------------
def load_company(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        company = json.load(fh)
    company["_dir"] = os.path.dirname(os.path.abspath(path))
    return company


def fill_tokens(obj, tokens):
    """Replace {company_key} tokens in every string of the data."""
    if isinstance(obj, str):
        return _TOKEN.sub(lambda m: tokens.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, list):
        return [fill_tokens(x, tokens) for x in obj]
    if isinstance(obj, dict):
        return {k: fill_tokens(v, tokens) for k, v in obj.items()}
    return obj


def brand_colors(company):
    brand = company.get("brand") or {}
    return (colors.HexColor(brand.get("accent_color") or DEFAULT_ACCENT),
            colors.HexColor(brand.get("primary_color") or DEFAULT_PRIMARY))


# ---- paragraph styles -------------------------------------------------------
def make_styles(primary):
    styles = getSampleStyleSheet()
    s = {}
    s["BODY"] = ParagraphStyle("body", parent=styles["Normal"],
                               fontName="Helvetica", fontSize=10,
                               leading=13.5, spaceAfter=7, textColor=INK)
    s["TIGHT"] = ParagraphStyle("tight", parent=s["BODY"], leading=13,
                                spaceAfter=0)
    s["H1"] = ParagraphStyle("h1", parent=styles["Heading2"],
                             fontName="Helvetica-Bold", fontSize=12,
                             leading=15, spaceBefore=8, spaceAfter=5,
                             textColor=primary)
    s["NOTE"] = ParagraphStyle("note", parent=s["BODY"], fontSize=9,
                               leading=11.5,
                               textColor=colors.HexColor("#555555"),
                               spaceAfter=4, leftIndent=8)
    s["CELL"] = ParagraphStyle("cell", parent=styles["Normal"],
                               fontName="Helvetica", fontSize=10, leading=13,
                               textColor=INK)
    s["CELLB"] = ParagraphStyle("cellb", parent=s["CELL"],
                                fontName="Helvetica-Bold")
    s["HDRCELL"] = ParagraphStyle("hdrcell", parent=s["CELLB"],
                                  textColor=colors.white)
    return s


def masthead_factory(date_display, company):
    """Company letterhead masthead plus footer, drawn on every letter page."""
    accent, _ = brand_colors(company)
    addr = [x for x in (company.get("address_line1"),
                        company.get("city_state_zip"),
                        company.get("phone"), company.get("website")) if x]
    foot = "    |    ".join(x for x in (
        company.get("legal_name"),
        ", ".join(y for y in (company.get("address_line1"),
                              company.get("city_state_zip")) if y),
        company.get("phone"), company.get("website")) if x)
    wordmark = (company.get("dba") or company.get("legal_name") or "").upper()
    license_no = company.get("license")
    logo = None
    if company.get("logo_path"):
        p = company["logo_path"]
        if not os.path.isabs(p):
            p = os.path.join(company.get("_dir", HERE), p)
        if os.path.exists(p):
            logo = p
        else:
            print("  MISSING logo (skipped):", p)

    def draw(c, doc):
        page = c.getPageNumber()
        c.saveState()
        if logo:
            img = ImageReader(logo)
            iw, ih = img.getSize()
            h = 40.0
            w = min(iw * h / ih, W * 0.55)
            c.drawImage(img, LEFT, PH - 78, width=w, height=w * ih / iw,
                        mask="auto", preserveAspectRatio=True)
        elif wordmark:
            size = 22
            while size > 12 and stringWidth(wordmark, "Helvetica-Bold",
                                            size) > W * 0.6:
                size -= 1
            c.setFillColor(accent)
            c.setFont("Helvetica-Bold", size)
            c.drawString(LEFT, PH - 62, wordmark)
            if license_no:
                c.saveState()
                t = c.beginText(LEFT + 1, PH - 73)
                t.setFont("Helvetica", 7)
                t.setFillColor(GRAY)
                t.setCharSpace(1.5)
                t.textLine("LICENSE %s" % license_no)
                c.drawText(t)
                c.restoreState()
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7.6)
        for i, ln in enumerate(addr):
            c.drawRightString(RIGHT, PH - 52 - i * 9, ln)
        c.setStrokeColor(accent)
        c.setLineWidth(1.4)
        c.line(LEFT, PH - 88, RIGHT, PH - 88)
        # footer
        c.setStrokeColor(LGRAY)
        c.setLineWidth(0.5)
        c.line(LEFT, 46, RIGHT, 46)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 6.8)
        c.drawCentredString(PW / 2, 36, foot)
        c.setFont("Helvetica", 7.2)
        c.drawRightString(RIGHT, 55, "%s    |    %s    |    Page %d"
                          % (DOC_LABEL, date_display, page))
        c.restoreState()
    return draw


def capacity_table(rows, st, primary):
    """Primary-color header bar, two-column table."""
    data = [[Paragraph(TABLE_HDR_ITEM, st["HDRCELL"]),
             Paragraph(TABLE_HDR_VALUE, st["HDRCELL"])]]
    for r in rows:
        data.append([Paragraph(r["label"], st["CELLB"]),
                     Paragraph(r["value"], st["CELL"])])
    t = Table(data, colWidths=[2.6 * inch, 4.4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("BACKGROUND", (0, 1), (0, -1), FILL_LABEL),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def default_signature(company):
    sig = {"name": company.get("pm_name", ""),
           "title": company.get("pm_title"),
           "company": company.get("legal_name")}
    if company.get("pm_phone"):
        sig["phone"] = "Phone: %s" % company["pm_phone"]
    if company.get("pm_email"):
        sig["email"] = company["pm_email"]
    return sig


def build_letter(data, company):
    """Render the letter pages, return PDF bytes."""
    _, primary = brand_colors(company)
    st = make_styles(primary)
    BODY, TIGHT, H1, NOTE = st["BODY"], st["TIGHT"], st["H1"], st["NOTE"]
    L = data["letter"]
    sig = data.get("signature") or default_signature(company)
    s = []
    s.append(Paragraph(L["date_display"], BODY))
    s.append(Spacer(1, 4))
    for ln in L["recipient_lines"]:
        s.append(Paragraph(ln, TIGHT))
    s.append(Spacer(1, 10))
    s.append(Paragraph("<b>RE: %s</b>" % L["re_line"], BODY))
    s.append(Paragraph(L["salutation"], BODY))
    for p in L["opening_paragraphs"]:
        s.append(Paragraph(p, BODY))
    s.append(Paragraph(CAPACITY_HEADING, H1))
    s.append(capacity_table(L["capacity_rows"], st, primary))
    s.append(Spacer(1, 6))
    if L.get("premium_note"):
        s.append(Paragraph(L["premium_note"], NOTE))
    if L.get("surety_lines"):
        s.append(Paragraph(SURETY_HEADING, H1))
        for ln in L["surety_lines"]:
            s.append(Paragraph(ln, TIGHT))
        s.append(Spacer(1, 8))
    for p in L.get("closing_paragraphs", []):
        s.append(Paragraph(p, BODY))
    # closing + signature + enclosures never split across a page break
    tail = [Paragraph(CLOSING, BODY),
            Spacer(1, 24)]                        # room for a wet signature
    tail.append(Paragraph("<b>%s</b>" % sig["name"], TIGHT))
    for key in ("title", "company", "phone", "email"):
        if sig.get(key):
            tail.append(Paragraph(sig[key], TIGHT))
    enc = data.get("enclosures", [])
    if enc:
        tail.append(Spacer(1, 10))
        tail.append(Paragraph("<b>%s</b>" % ENCLOSURES_LABEL, TIGHT))
        for i, e in enumerate(enc, 1):
            tail.append(Paragraph("%d. %s" % (i, e["label"]), TIGHT))
    s.append(KeepTogether(tail))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=1.35 * inch, bottomMargin=0.87 * inch,
                            title=data["meta"]["pdf_title"], invariant=1)
    mh = masthead_factory(L["date_display"], company)
    doc.build(s, onFirstPage=mh, onLaterPages=mh)
    return buf.getvalue()


# ---- deterministic assembly -------------------------------------------------
def meta_dates(data, company):
    created = data["meta"].get("created", "2026-01-01")
    d = "D:%s000000" % created.replace("-", "")
    return {"title": data["meta"]["pdf_title"],
            "author": data["meta"].get("pdf_author")
            or company.get("legal_name") or "",
            "producer": "", "creator": "",
            "creationDate": d, "modDate": d}


def make_deterministic_id(path):
    """MuPDF writes a fresh random /ID on every save; everything else is
    byte-stable (reportlab invariant=1). Replace the trailer /ID with an MD5
    of the file content so identical data gives byte-identical PDFs."""
    with open(path, "rb") as f:
        raw = f.read()
    matches = list(re.finditer(rb"/ID\[<([0-9A-Fa-f]{32})><([0-9A-Fa-f]{32})>\]", raw))
    if not matches:
        return
    m = matches[-1]  # the document trailer is the last one in the file
    zeroed = raw[:m.start(1)] + b"0" * 32 + raw[m.end(1):m.start(2)] + b"0" * 32 + raw[m.end(2):]
    dig = hashlib.md5(zeroed).hexdigest().upper().encode("ascii")
    fixed = raw[:m.start(1)] + dig + raw[m.end(1):m.start(2)] + dig + raw[m.end(2):]
    with open(path, "wb") as f:
        f.write(fixed)


def main():
    ap = argparse.ArgumentParser(description="Build a bonding capacity "
                                             "correspondence packet PDF.")
    ap.add_argument("data", nargs="?",
                    default=os.path.join(HERE, "sample_data.json"),
                    help="letter data JSON (default: sample_data.json here)")
    ap.add_argument("--company", default=DEFAULT_COMPANY,
                    help="company config JSON (default: "
                         "template-library/company.example.json)")
    args = ap.parse_args()

    data_path = args.data
    raw = io.open(data_path, "r", encoding="utf-8").read()
    for ch, name in ((chr(0x2014), "em dash"), (chr(0x2013), "en dash")):
        if ch in raw:
            raise SystemExit("House style violation: %s found in %s. Use commas, "
                             "periods, or hyphens instead." % (name, data_path))
    company = load_company(args.company)
    tokens = {k: v for k, v in company.items()
              if isinstance(v, str) and not k.startswith("_")}
    data = fill_tokens(json.loads(raw), tokens)
    data_dir = os.path.dirname(os.path.abspath(data_path))

    out_dir = data["meta"].get("output_dir") or os.path.join(HERE, "_sample_output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(HERE, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    letter_bytes = build_letter(data, company)

    final = fitz.open()
    src = fitz.open(stream=letter_bytes, filetype="pdf")
    final.insert_pdf(src)
    src.close()
    for e in data.get("enclosures", []):
        p = e.get("path")
        if not p:
            continue                       # listed in the letter, not merged
        if not os.path.isabs(p):
            p = os.path.join(data_dir, p)  # relative to the data file
        if os.path.exists(p):
            src = fitz.open(p)
            final.insert_pdf(src)
            src.close()
        else:
            print("  MISSING enclosure (skipped):", p)

    name = "%s_Bonding_Capacity_Packet_%s.pdf" % (
        data["meta"]["job_slug"], data["meta"]["letter_date_iso"])
    out_path = os.path.join(out_dir, name)
    final.set_metadata(meta_dates(data, company))
    final.save(out_path, garbage=4, deflate=True)
    print("wrote", out_path, "| pages", final.page_count)
    final.close()
    make_deterministic_id(out_path)


if __name__ == "__main__":
    main()
