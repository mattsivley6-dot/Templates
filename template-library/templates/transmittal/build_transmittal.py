#!/usr/bin/env python3
# build_transmittal.py
# Transmittal / Submittal Cover Sheet builder.
# Usage: python build_transmittal.py [data.json] [--company company.json]
#
# Self-contained: stdlib + python-docx only. Job content comes from the JSON
# data file. Company letterhead fields (name, address, phone, website, PM
# contact) come from the company config, which defaults to
# template-library/company.example.json (two folders up from this script).
# This script holds only fixed wording and layout.
# Deterministic: no clock or random calls; docx core properties and zip entry
# timestamps come from the JSON "doc_date".

import argparse
import io
import json
import os
import zipfile
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- constants
FONT = "Arial"
NAVY_HEX = "1F3864"                      # banner cells + index table header fill
LIGHTBLUE_HEX = "DEEAF1"                 # quantity/dated/description header fill
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
MARGIN_IN = 0.75
CONTENT_W_IN = 8.5 - 2 * MARGIN_IN       # 7.0

VIA_OPTIONS = ["U.S. MAIL", "HAND DELIVERED", "LOCAL DELIVERY", "OVERNIGHT SHIPMENT", "Email"]
ITEM_OPTIONS = ["ORIGINAL DRAWINGS", "PRINTS", "SPECIFICATIONS", "COPY OF LETTER",
                "SUBMITTALS", "SAMPLES", "OTHER"]
ACTION_OPTIONS = ["APPROVED", "APPROVED AS NOTED", "REJECTED"]

TITLE_TRANSMITTAL = "TRANSMITTAL"
TITLE_COVER = "SUBMITTAL COVER SHEET"
TITLE_INDEX = "SUBMITTAL INDEX"
HDG_PROJECT = "PROJECT"
HDG_ENGINEER = "ENGINEER"
HDG_ACTION = "CONTRACTOR ACTION"
HDG_ITEMS = "ITEMS SUBMITTED"
HDG_DEVIATIONS = "KNOWN DEVIATIONS FROM CONTRACT DOCUMENTS"


# ----------------------------------------------------------- company config
def default_company_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "company.example.json"))


def load_company(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def company_display_name(co):
    return co.get("legal_name") or co.get("dba") or ""


def company_address_lines(co):
    lines = [co.get("address_line1"), co.get("city_state_zip"),
             co.get("phone"), co.get("website")]
    return [ln for ln in lines if ln]


def pm_signoff(co):
    name = co.get("pm_name", "")
    return name


def default_contractor_fields(co):
    contact = co.get("pm_name", "")
    if co.get("pm_title"):
        contact = contact + ", " + co["pm_title"] if contact else co["pm_title"]
    addr = ", ".join(x for x in (co.get("address_line1"), co.get("city_state_zip")) if x)
    return [
        ["Firm:", company_display_name(co)],
        ["Contact:", contact],
        ["Address:", addr],
        ["Phone:", co.get("phone", "")],
    ]


# ------------------------------------------------------------------ helpers
def run_in(p, text, size=9, bold=False, color=BLACK):
    r = p.add_run(text)
    r.bold = bold
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.color.rgb = color
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FONT)
    return r


def para(doc, text=None, size=9, bold=False, align=None, before=0, after=2, color=BLACK):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if align is not None:
        p.alignment = align
    if text is not None:
        run_in(p, text, size=size, bold=bold, color=color)
    return p


def cell_text(cell, text, size=9, bold=False, color=BLACK, align=None):
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    if align is not None:
        p.alignment = align
    for line_i, line in enumerate(str(text).split("\n")):
        if line_i:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            if align is not None:
                p.alignment = align
        run_in(p, line, size=size, bold=bold, color=color)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def shade(cell, hex_fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
    tcpr.append(shd)


def grid_borders(table, sz=4, color="000000"):
    tbl = table._tbl
    tblpr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblpr.append(borders)


def make_table(doc, rows, cols, widths_in, bordered=True):
    t = doc.add_table(rows=rows, cols=cols)
    t.autofit = False
    if bordered:
        grid_borders(t)
    for ci, w in enumerate(widths_in):
        t.columns[ci].width = Inches(w)
        for row in t.rows:
            row.cells[ci].width = Inches(w)
    return t


def banner(doc, title, subtitle):
    t = make_table(doc, 1, 1, [CONTENT_W_IN])
    c = t.rows[0].cells[0]
    shade(c, NAVY_HEX)
    cell_text(c, title + ("\n" + subtitle if subtitle else ""), size=12, bold=True,
              color=WHITE, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, after=4)


def label_value_rows(doc, fields, label_w=1.6):
    t = make_table(doc, len(fields), 2, [label_w, CONTENT_W_IN - label_w])
    for ri, (label, value) in enumerate(fields):
        cell_text(t.rows[ri].cells[0], label, bold=True)
        cell_text(t.rows[ri].cells[1], value)
    return t


def page_break(doc):
    p = doc.add_paragraph()
    r = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r._element.append(br)


def company_header(doc, co):
    para(doc, company_display_name(co), size=11, bold=True, after=0)
    for line in company_address_lines(co):
        para(doc, line, size=9, after=0)


# -------------------------------------------------------------------- parts
def part_transmittal(doc, co, tr):
    company_header(doc, co)
    para(doc, TITLE_TRANSMITTAL, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         before=4, after=6)

    t = make_table(doc, 1, 2, [1.0, 6.0])
    cell_text(t.rows[0].cells[0], "DATE:", bold=True)
    cell_text(t.rows[0].cells[1], tr["date"])
    para(doc, after=2)

    # TO / ATTN / address on the left, VIA checklist on the right.
    to_lines = [("TO:", tr["to"]), ("ATTN:", tr["attn"])] + \
               [("", line) for line in tr.get("to_address_lines", [])]
    n = max(len(to_lines), len(VIA_OPTIONS))
    t = make_table(doc, n, 4, [0.8, 3.6, 0.5, 2.1])
    for ri in range(n):
        if ri < len(to_lines):
            cell_text(t.rows[ri].cells[0], to_lines[ri][0], bold=True)
            cell_text(t.rows[ri].cells[1], to_lines[ri][1])
        if ri == 0:
            cell_text(t.rows[ri].cells[2], "VIA:", bold=True)
        if ri < len(VIA_OPTIONS):
            opt = VIA_OPTIONS[ri]
            mark = "x  " if opt == tr.get("via") else "     "
            cell_text(t.rows[ri].cells[3], mark + opt)
    para(doc, after=2)

    t = make_table(doc, 1, 4, [1.0, 3.6, 1.0, 1.4])
    cell_text(t.rows[0].cells[0], "PROJECT:", bold=True)
    cell_text(t.rows[0].cells[1], tr["project"])
    cell_text(t.rows[0].cells[2], "PROJECT #", bold=True)
    cell_text(t.rows[0].cells[3], tr["project_number"])
    para(doc, after=2)

    # TRANSMITTED (HEREWITH/SEPARATELY) + ITEM checklist, two options per
    # row, laid out from ITEM_OPTIONS so each option appears exactly once.
    rows = [("TRANSMITTED:", "HEREWITH", "SEPARATELY")]
    for i in range(0, len(ITEM_OPTIONS), 2):
        pair = ITEM_OPTIONS[i:i + 2] + [""]
        rows.append(("ITEM:" if i == 0 else "", pair[0], pair[1]))
    items = set(tr.get("items", []))
    t = make_table(doc, len(rows), 5, [1.3, 0.4, 2.4, 0.4, 2.5])
    for ri, (label, left_opt, right_opt) in enumerate(rows):
        cell_text(t.rows[ri].cells[0], label, bold=True)
        if ri == 0:
            lmark = "x" if tr.get("transmitted", "HEREWITH") == "HEREWITH" else ""
            rmark = "x" if tr.get("transmitted") == "SEPARATELY" else ""
        else:
            lmark = "x" if left_opt in items else ""
            rmark = "x" if right_opt in items else ""
        cell_text(t.rows[ri].cells[1], lmark, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_text(t.rows[ri].cells[2], left_opt)
        cell_text(t.rows[ri].cells[3], rmark, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_text(t.rows[ri].cells[4], right_opt)
    para(doc, after=2)

    # QUANTITY / DATED / DESCRIPTION (minimum 5 rows including the header).
    lines = tr.get("lines", [])
    nrows = max(5, len(lines) + 1)
    t = make_table(doc, nrows, 3, [1.1, 1.1, 4.8])
    for ci, h in enumerate(["QUANTITY", "DATED", "DESCRIPTION"]):
        shade(t.rows[0].cells[ci], LIGHTBLUE_HEX)
        cell_text(t.rows[0].cells[ci], h, bold=True)
    for ri, line in enumerate(lines, start=1):
        cell_text(t.rows[ri].cells[0], line.get("quantity", ""))
        cell_text(t.rows[ri].cells[1], line.get("dated", ""))
        cell_text(t.rows[ri].cells[2], line.get("description", ""))
    para(doc, after=2)

    t = make_table(doc, 1, 2, [1.2, 5.8])
    cell_text(t.rows[0].cells[0], "REMARKS:", bold=True)
    cell_text(t.rows[0].cells[1], tr.get("remarks", ""))
    para(doc, after=2)

    t = make_table(doc, 1, 2, [1.2, 5.8])
    cell_text(t.rows[0].cells[0], "By:", bold=True)
    cell_text(t.rows[0].cells[1], tr.get("by") or pm_signoff(co))


def part_cover_sheet(doc, co, cs):
    page_break(doc)
    banner(doc, TITLE_COVER, cs.get("division_line", ""))

    para(doc, HDG_PROJECT, size=10, bold=True, before=4, after=2)
    label_value_rows(doc, cs["project_fields"])
    para(doc, HDG_ENGINEER, size=10, bold=True, before=8, after=2)
    label_value_rows(doc, cs["engineer_fields"])
    para(doc, cs.get("contractor_heading", "PRIME CONTRACTOR / GENERAL CONTRACTOR"),
         size=10, bold=True, before=8, after=2)
    label_value_rows(doc, cs.get("contractor_fields") or default_contractor_fields(co))
    if cs.get("third_party_fields"):
        para(doc, cs.get("third_party_heading", "SUBCONTRACTOR / SUPPLIER"),
             size=10, bold=True, before=8, after=2)
        label_value_rows(doc, cs["third_party_fields"])

    para(doc, HDG_ACTION, size=10, bold=True, before=10, after=2)
    marked = cs.get("action_marked", "")
    t = make_table(doc, 1, 3, [7.0 / 3] * 3)
    for ci, opt in enumerate(ACTION_OPTIONS):
        mark = "x  " if opt == marked else ""
        cell_text(t.rows[0].cells[ci], mark + opt, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, cs["action_statement"], size=8.5, before=3, after=8)

    t = make_table(doc, 1, 3, [2.0, 3.0, 2.0])
    cell_text(t.rows[0].cells[0], "Contractor Signature:", bold=True)
    cell_text(t.rows[0].cells[1], cs.get("signature_name") or pm_signoff(co))
    cell_text(t.rows[0].cells[2], "Date:  " + cs.get("signature_date", ""))


def part_index(doc, ix):
    page_break(doc)
    banner(doc, TITLE_INDEX, ix.get("division_line", ""))

    para(doc, HDG_ITEMS, size=10, bold=True, before=4, after=2)
    rows = ix.get("rows", [])
    t = make_table(doc, len(rows) + 1, 3, [0.7, 4.8, 1.5])
    for ci, h in enumerate(["Item", "Description", "Spec Section"]):
        shade(t.rows[0].cells[ci], NAVY_HEX)
        cell_text(t.rows[0].cells[ci], h, bold=True, color=WHITE)
    for ri, row in enumerate(rows, start=1):
        for ci in range(3):
            cell_text(t.rows[ri].cells[ci], row[ci] if ci < len(row) else "")

    para(doc, HDG_DEVIATIONS, size=10, bold=True, before=10, after=2)
    para(doc, ix["deviations_note"], size=8.5, after=4)
    devs = ix.get("deviations", [])
    nrows = max(4, len(devs) + 1)
    t = make_table(doc, nrows, 4, [0.6, 4.0, 1.2, 1.2])
    for ci, h in enumerate(["No.", "Deviation", "Spec Ref.", "Severity"]):
        shade(t.rows[0].cells[ci], NAVY_HEX)
        cell_text(t.rows[0].cells[ci], h, bold=True, color=WHITE)
    for ri, row in enumerate(devs, start=1):
        for ci in range(4):
            cell_text(t.rows[ri].cells[ci], row[ci] if ci < len(row) else "")


# -------------------------------------------------------------------- build
def build(data, co):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Inches(MARGIN_IN))

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(2)

    doc_date = datetime.strptime(data["doc_date"], "%Y-%m-%d")
    cp = doc.core_properties
    author = co.get("dba") or co.get("legal_name") or ""
    cp.author = author
    cp.last_modified_by = author
    cp.title = data.get("pdf_title", "Transmittal")
    cp.comments = ""
    cp.created = doc_date
    cp.modified = doc_date

    part_transmittal(doc, co, data["transmittal"])
    if data.get("cover_sheet", {}).get("enabled", True) and data.get("cover_sheet"):
        part_cover_sheet(doc, co, data["cover_sheet"])
    if data.get("index", {}).get("enabled") and data.get("index"):
        part_index(doc, data["index"])
    return doc, doc_date


def save_deterministic(doc, out_path, doc_date):
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
    ap = argparse.ArgumentParser(description="Build a transmittal / submittal cover sheet (.docx).")
    ap.add_argument("data", nargs="?", default=os.path.join(script_dir, "sample_data.json"),
                    help="job data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=default_company_path(),
                    help="company config JSON (default: ../../company.example.json)")
    args = ap.parse_args()

    with open(args.data, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    co = load_company(args.company)
    doc, doc_date = build(data, co)
    out_dir = data.get("output_dir") or os.path.join(script_dir, "_sample_output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, data["output_filename"])
    save_deterministic(doc, out_path, doc_date)
    print("Wrote " + out_path)


if __name__ == "__main__":
    main()
