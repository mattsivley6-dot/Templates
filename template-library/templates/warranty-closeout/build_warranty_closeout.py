#!/usr/bin/env python3
# build_warranty_closeout.py
# Warranty Close Out Letter builder.
# Usage: python build_warranty_closeout.py [data.json] [--company company.json]
#
# Self-contained: stdlib + python-docx only. Job content comes from the JSON
# data file. Letterhead fields (company name, address, optional logo, license
# number) come from the company config, which defaults to
# template-library/company.example.json (two folders up from this script).
# This script holds only fixed wording and layout.
# Deterministic: no datetime.now()/today()/time()/random anywhere. The docx
# core properties (created/modified) are taken from the JSON "doc_date".

import argparse
import io
import json
import os
import zipfile
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- constants
FONT_NAME = "Times New Roman"
BODY_PT = 10                        # Normal body size
SMALL_PT = 9.5                      # letterhead address, labels, values
CONTACT_PT = 8                      # optional customer mailing block
NAME_PT = 14                        # company name when no logo is set
COLOR_BLACK = RGBColor(0x00, 0x00, 0x00)
COLOR_LABEL_GRAY = RGBColor(0x9A, 0x9A, 0x9A)   # CUSTOMER NAME / AUTHORIZED BY labels
RULE_HEX = "999999"                 # horizontal section divider color
RULE_SZ = 6                         # eighths of a point -> 0.75 pt line

MARGIN_LEFT_IN = 0.33
MARGIN_RIGHT_IN = 0.33
MARGIN_TOP_IN = 0.44
MARGIN_BOTTOM_IN = 0.30
PAGE_W_IN = 8.5
PAGE_H_IN = 11.0
LOGO_WIDTH_IN = 2.0                 # optional logo width in the letterhead
TAB1_IN = 2.62                      # PROPERTY NAME column
TAB2_IN = 4.92                      # PROPERTY ADDRESS column

# Fixed wording.
LBL_CUSTOMER = "CUSTOMER NAME"
LBL_PROPERTY = "PROPERTY NAME"
LBL_ADDRESS = "PROPERTY ADDRESS"
LBL_AUTHORIZED = "AUTHORIZED BY"
HDG_COMPLETION = "PROJECT COMPLETION NOTICE"
HDG_EQUIPMENT = "EQUIPMENT INSTALLED"
HDG_WARRANTY = "WARRANTY COVERAGE"
HDG_REMINDERS = "IMPORTANT REMINDERS"
HDG_ACCEPTANCE = "ACCEPTANCE"
TXT_AUTH_BY = "Authorized By:"
TXT_THANK_YOU = "THANK YOU, WE APPRECIATE YOUR BUSINESS!"
HDG_TERMS = "Terms of Service"
LIC_LABEL = "Contractor License #: "
DEFAULT_ACCEPTANCE = ("The system has been installed to industry and manufacturer "
                      "standards and is operational at close-out.")


# ----------------------------------------------------------- company config
def default_company_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "company.example.json"))


def load_company(path):
    with open(path, "r", encoding="utf-8") as fh:
        co = json.load(fh)
    co["_dir"] = os.path.dirname(os.path.abspath(path))
    return co


def company_name(co):
    return co.get("legal_name") or co.get("dba") or ""


def default_signer(co):
    parts = [co.get("pm_name", ""), co.get("pm_title", "")]
    left = ", ".join(p for p in parts if p)
    dba = co.get("dba") or co.get("legal_name") or ""
    return " - ".join(p for p in (left, dba) if p)


def resolve_logo(co, script_dir):
    """Return the logo path, or None when the config has no logo (skip cleanly)."""
    rel = co.get("logo_path")
    if not rel:
        return None
    for base in ([""] if os.path.isabs(rel) else [co["_dir"], script_dir]):
        cand = os.path.join(base, rel) if base else rel
        if os.path.isfile(cand):
            return cand
    raise FileNotFoundError("Letterhead logo not found: " + rel)


# ------------------------------------------------------------------ helpers
def styled_run(paragraph, text, size=BODY_PT, bold=False, color=COLOR_BLACK):
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONT_NAME)
    return run


def para(doc, before=0.0, after=0.3, align=None, line=1.06):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line is not None:
        pf.line_spacing = line
    if align is not None:
        pf.alignment = align
    return p


def text_para(doc, text, size=BODY_PT, bold=False, color=COLOR_BLACK,
              before=0.0, after=0.3, align=None):
    p = para(doc, before=before, after=after, align=align)
    styled_run(p, text, size=size, bold=bold, color=color)
    return p


def label_value_para(doc, label, value, size=BODY_PT, before=0.0, after=0.3):
    """Bold 'Label' + non-bold ': value'. Empty label -> plain line."""
    p = para(doc, before=before, after=after)
    if label:
        styled_run(p, label, size=size, bold=True)
        styled_run(p, ": " + value, size=size, bold=False)
    else:
        styled_run(p, value, size=size, bold=False)
    return p


def rule(doc, before=12.0, after=12.0):
    """Thin gray horizontal divider across the content width."""
    p = para(doc, before=before, after=after, line=None)
    ppr = p._element.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(RULE_SZ))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), RULE_HEX)
    pbdr.append(bottom)
    ppr.append(pbdr)
    return p


def section_heading(doc, text, before=0.0, after=0.5):
    return text_para(doc, text, size=BODY_PT, bold=True, before=before, after=after)


def tab_stops(p, *positions_in):
    pf = p.paragraph_format
    for pos in positions_in:
        pf.tab_stops.add_tab_stop(Inches(pos), WD_TAB_ALIGNMENT.LEFT)
    return p


# -------------------------------------------------------------------- build
def build(data, co, script_dir):
    doc = Document()

    # Page setup: letter portrait, tight margins.
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width = Inches(PAGE_W_IN)
    sec.page_height = Inches(PAGE_H_IN)
    sec.left_margin = Inches(MARGIN_LEFT_IN)
    sec.right_margin = Inches(MARGIN_RIGHT_IN)
    sec.top_margin = Inches(MARGIN_TOP_IN)
    sec.bottom_margin = Inches(MARGIN_BOTTOM_IN)

    # Normal style baseline (Times New Roman 10, tight spacing).
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = Pt(BODY_PT)
    normal.font.color.rgb = COLOR_BLACK
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONT_NAME)
    normal.paragraph_format.space_after = Pt(0.3)
    normal.paragraph_format.line_spacing = 1.06

    # Deterministic core properties (dates from JSON, never from the clock).
    doc_date = datetime.strptime(data["doc_date"], "%Y-%m-%d")
    cp = doc.core_properties
    author = co.get("dba") or co.get("legal_name") or ""
    cp.author = author
    cp.last_modified_by = author
    cp.title = "Warranty Close Out Letter"
    cp.comments = ""
    cp.created = doc_date
    cp.modified = doc_date

    # ---- Letterhead: logo (or company name) left, company address right.
    logo_path = resolve_logo(co, script_dir)

    hdr = doc.add_table(rows=1, cols=2)
    hdr.autofit = False
    hdr.columns[0].width = Inches(4.20)
    hdr.columns[1].width = Inches(3.64)
    left_cell, right_cell = hdr.rows[0].cells
    left_cell.width = Inches(4.20)
    right_cell.width = Inches(3.64)
    lp = left_cell.paragraphs[0]
    lp.paragraph_format.space_after = Pt(0)
    if logo_path:
        lp.add_run().add_picture(logo_path, width=Inches(LOGO_WIDTH_IN))
    else:
        styled_run(lp, co.get("dba") or company_name(co), size=NAME_PT, bold=True)
    addr_lines = [ln for ln in (co.get("address_line1"), co.get("city_state_zip")) if ln]
    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rp.paragraph_format.space_after = Pt(0)
    styled_run(rp, addr_lines[0] if addr_lines else "", size=SMALL_PT)
    for line in addr_lines[1:]:
        p = right_cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_after = Pt(0)
        styled_run(p, line, size=SMALL_PT)

    para(doc, after=6.0)  # spacer under letterhead

    # ---- Optional customer mailing block + project title (RTU style).
    contact_lines = data.get("customer_contact_lines") or []
    if contact_lines:
        text_para(doc, contact_lines[0], size=CONTACT_PT, bold=True, after=0.5)
        for line in contact_lines[1:]:
            text_para(doc, line, size=CONTACT_PT, after=0.5)
        para(doc, after=4.0)
    if data.get("project_title"):
        text_para(doc, data["project_title"], size=SMALL_PT, bold=True, after=8.0)

    # ---- Three-column label row: customer / property / address.
    p = para(doc, before=6.0, after=2.5)
    tab_stops(p, TAB1_IN, TAB2_IN)
    styled_run(p, LBL_CUSTOMER, size=SMALL_PT, bold=True, color=COLOR_LABEL_GRAY)
    styled_run(p, "\t" + LBL_PROPERTY, size=SMALL_PT, bold=True, color=COLOR_LABEL_GRAY)
    styled_run(p, "\t" + LBL_ADDRESS, size=SMALL_PT, bold=True, color=COLOR_LABEL_GRAY)

    addr = list(data["property_address_lines"])
    p = para(doc, after=1.0)
    tab_stops(p, TAB1_IN, TAB2_IN)
    styled_run(p, data["customer_name"], size=SMALL_PT)
    styled_run(p, "\t" + data["property_name"], size=SMALL_PT)
    styled_run(p, "\t" + (addr[0] if addr else ""), size=SMALL_PT)
    for line in addr[1:]:
        p = para(doc, after=1.0)
        tab_stops(p, TAB1_IN, TAB2_IN)
        styled_run(p, "\t\t" + line, size=SMALL_PT)

    # ---- AUTHORIZED BY.
    text_para(doc, LBL_AUTHORIZED, size=SMALL_PT, bold=True,
              color=COLOR_LABEL_GRAY, before=8.0, after=2.5)
    text_para(doc, data.get("authorized_by") or co.get("pm_name", ""),
              size=SMALL_PT, after=8.4)

    # ---- PROJECT COMPLETION NOTICE.
    rule(doc)
    section_heading(doc, HDG_COMPLETION)
    text_para(doc, data["completion_notice"], after=8.0)

    # ---- EQUIPMENT INSTALLED.
    rule(doc)
    section_heading(doc, HDG_EQUIPMENT)
    for item in data["equipment"]:
        label_value_para(doc, item.get("label", ""), item["value"])

    # ---- WARRANTY COVERAGE.
    rule(doc)
    section_heading(doc, HDG_WARRANTY + data.get("warranty_heading_suffix", ""))
    for item in data["warranty_lines"]:
        label_value_para(doc, item.get("label", ""), item["value"])

    # ---- IMPORTANT REMINDERS.
    rule(doc)
    section_heading(doc, HDG_REMINDERS)
    for line in data["reminders"]:
        text_para(doc, line)

    # ---- ACCEPTANCE.
    rule(doc)
    section_heading(doc, HDG_ACCEPTANCE)
    text_para(doc, data.get("acceptance_statement") or DEFAULT_ACCEPTANCE, after=8.0)
    text_para(doc, TXT_AUTH_BY)
    para(doc, after=10.0)  # blank line reserved for wet/PDF signature
    for signer in (data.get("signers") or [default_signer(co)]):
        text_para(doc, signer)

    # ---- Optional Terms of Service block.
    if data.get("payment_terms"):
        rule(doc)
        text_para(doc, HDG_TERMS, size=SMALL_PT, bold=True, after=2.0)
        text_para(doc, "Terms: " + data["payment_terms"], after=8.0)

    # ---- Thank you + optional license block.
    text_para(doc, TXT_THANK_YOU, before=8.0)
    if data.get("include_license_block"):
        if co.get("license"):
            text_para(doc, LIC_LABEL + co["license"])
        for i, line in enumerate(data.get("license_extra_lines") or []):
            text_para(doc, line, before=8.0 if i == 0 else 0.0)

    return doc


def save_deterministic(doc, out_path, doc_date):
    """python-docx stamps zip entries with the current clock, which breaks
    byte-determinism. Save to memory, then rewrite the zip with every entry
    timestamped from doc_date and entries in sorted order."""
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    src = zipfile.ZipFile(buf)
    dt = (doc_date.year, doc_date.month, doc_date.day, 0, 0, 0)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for name in sorted(src.namelist()):
            zi = zipfile.ZipInfo(name, date_time=dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            out.writestr(zi, src.read(name))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Build a warranty close out letter (.docx).")
    ap.add_argument("data", nargs="?", default=os.path.join(script_dir, "sample_data.json"),
                    help="job data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=default_company_path(),
                    help="company config JSON (default: ../../company.example.json)")
    args = ap.parse_args()

    with open(args.data, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    co = load_company(args.company)

    doc = build(data, co, script_dir)

    out_name = data.get("output_filename") or (
        "Warranty Close Out Letter - " + data["property_name"] + ".docx")
    out_dir = data.get("output_dir") or os.path.join(script_dir, "_sample_output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)
    save_deterministic(doc, out_path, datetime.strptime(data["doc_date"], "%Y-%m-%d"))
    print("Wrote " + out_path)


if __name__ == "__main__":
    main()
