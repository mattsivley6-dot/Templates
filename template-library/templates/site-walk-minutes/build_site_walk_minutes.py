"""Build Site Walk / Field Meeting Minutes (.docx).

Usage:
    py -3 build_site_walk_minutes.py [data.json] [--company company.json]

Defaults to sample_data.json located next to this script. Writes
<output_basename>.docx into output_dir from the data file, or into
_sample_output next to this script when output_dir is not given.
Company fields (legal name, brand color, PM name and title) come from the
company config, which defaults to ../../company.example.json relative to
this script.

Deterministic: no clock or random calls; every date and all variable
content come from the JSON data file. Core properties are fixed from
the data file so identical data gives identical output.
"""

import argparse
import io
import json
import os
import sys
import zipfile
from datetime import datetime, timezone

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ---------------------------------------------------------------- style
DEFAULT_PRIMARY_HEX = "1F3A5F"             # used if the company config has no brand color
GRAY = RGBColor(0x59, 0x59, 0x59)          # italic notes and closing
TABLE_HEADER_FILL = "E8EBF2"               # shaded table header rows
BODY_FONT = "Arial"
BODY_SIZE = Pt(10.5)                       # Normal style base size
TITLE_SIZE = Pt(15)
SUBTITLE_SIZE = Pt(11)
MASTHEAD_SIZE = Pt(10)
HEADING_SIZE = Pt(11)
ATTEND_TABLE_SIZE = Pt(9.5)
ACTION_TABLE_SIZE = Pt(9)
NOTE_SIZE = Pt(9)

MARGIN_LR = Inches(0.90)
MARGIN_TB = Inches(0.70)
HDR_FTR_DIST = Inches(0.50)

# action items table column widths
ACTION_COL_WIDTHS = (Inches(0.4), Inches(4.6), Inches(1.7), Inches(1.3))

# title and section heading color, set from the company config in build()
PRIMARY = RGBColor.from_string(DEFAULT_PRIMARY_HEX)

# ---------------------------------------------------------- fixed wording
DEFAULT_TITLE = "SITE WALK / FIELD MEETING MINUTES"
CLOSING_TEXT = (
    "These minutes reflect the writer's understanding of the items "
    "discussed and the conclusions reached on the site walk. Please "
    "direct any corrections or additions to the writer within five (5) "
    "business days of receipt; otherwise, these minutes will stand as "
    "the record of the walk."
)
ATTENDANCE_HEADING = "Attendance"
ACTION_ITEMS_HEADING = "Action Items"
ATTEND_COLS = ("Name", "Organization", "Role")
ACTION_COLS = ("No.", "Action", "Responsible", "Target")


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def load_company(path):
    if not os.path.isfile(path):
        fail("company config not found: %s" % path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def brand_hex(company):
    """Primary brand color from the company config as 6-digit hex, no '#'."""
    raw = ((company.get("brand") or {}).get("primary_color") or DEFAULT_PRIMARY_HEX)
    raw = raw.lstrip("#")
    if len(raw) != 6:
        fail("brand.primary_color must be a 6-digit hex color, got %r" % raw)
    return raw.upper()


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def cell_text(cell, text, size, bold=False):
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.size = size
    if bold:
        run.font.bold = True


def add_masthead_line(doc, label, value):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run(label + ":  ")
    r1.font.size = MASTHEAD_SIZE
    r1.font.bold = True
    r2 = p.add_run(value)
    r2.font.size = MASTHEAD_SIZE


def add_section_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.size = HEADING_SIZE
    run.font.bold = True
    run.font.color.rgb = PRIMARY
    return p


def add_item(doc, number, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.35)
    r1 = p.add_run(number + "   ")
    r1.font.size = BODY_SIZE
    r1.font.bold = True
    r2 = p.add_run(text)
    r2.font.size = BODY_SIZE


def add_gray_note(doc, text, space_before=None):
    p = doc.add_paragraph()
    if space_before is not None:
        p.paragraph_format.space_before = space_before
    run = p.add_run(text)
    run.font.size = NOTE_SIZE
    run.font.italic = True
    run.font.color.rgb = GRAY
    return p


def build(data, company):
    global PRIMARY
    PRIMARY = RGBColor.from_string(brand_hex(company))
    legal_name = company.get("legal_name") or "[Company Legal Name]"
    pm_line = ", ".join(x for x in (company.get("pm_name"), company.get("pm_title")) if x)

    doc = Document()

    # base Normal style: Arial 10.5pt, 4pt space after
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = BODY_SIZE
    normal.paragraph_format.space_after = Pt(4)

    sec = doc.sections[0]
    sec.left_margin = MARGIN_LR
    sec.right_margin = MARGIN_LR
    sec.top_margin = MARGIN_TB
    sec.bottom_margin = MARGIN_TB
    sec.header_distance = HDR_FTR_DIST
    sec.footer_distance = HDR_FTR_DIST

    title_text = data.get("doc_title", DEFAULT_TITLE)

    # title
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(title_text)
    run.font.size = TITLE_SIZE
    run.font.bold = True
    run.font.color.rgb = PRIMARY

    # project subtitle (project name  |  walk subject)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(data["project_line"])
    run.font.size = SUBTITLE_SIZE
    run.font.bold = True

    # masthead block (contractor and prepared-by default from the company config)
    contractor = data.get("contractor") or legal_name
    prepared_by = data.get("prepared_by") or ", ".join(
        x for x in (pm_line, legal_name) if x)
    add_masthead_line(doc, "Owner", data["owner"])
    add_masthead_line(doc, "Solicitation", data["solicitation"])
    add_masthead_line(doc, "Contractor", contractor)
    add_masthead_line(doc, "Engineer", data["engineer"])
    add_masthead_line(doc, "Walk Date", data["walk_date"])
    add_masthead_line(doc, "Location", data["location"])
    add_masthead_line(doc, "Prepared By", prepared_by)
    add_masthead_line(doc, "Distribution", data["distribution"])

    # attendance
    add_section_heading(doc, ATTENDANCE_HEADING)
    attendees = data["attendees"]
    table = doc.add_table(rows=1 + len(attendees), cols=3)
    table.style = "Table Grid"
    for ci, head in enumerate(ATTEND_COLS):
        cell = table.rows[0].cells[ci]
        cell_text(cell, head, ATTEND_TABLE_SIZE, bold=True)
        shade_cell(cell, TABLE_HEADER_FILL)
    for ri, att in enumerate(attendees, start=1):
        row = table.rows[ri]
        cell_text(row.cells[0], att["name"], ATTEND_TABLE_SIZE)
        cell_text(row.cells[1], att["organization"], ATTEND_TABLE_SIZE)
        cell_text(row.cells[2], att["role"], ATTEND_TABLE_SIZE)

    if data.get("attendance_note"):
        add_gray_note(doc, data["attendance_note"])

    # numbered discussion sections
    sections = data["sections"]
    for si, section in enumerate(sections, start=1):
        add_section_heading(doc, "%d.0   %s" % (si, section["title"]))
        for ii, item in enumerate(section["items"], start=1):
            add_item(doc, "%d.%d" % (si, ii), item)

    # action items table (numbered as the last section)
    action_no = len(sections) + 1
    add_section_heading(doc, "%d.0   %s" % (action_no, ACTION_ITEMS_HEADING))
    actions = data["action_items"]
    table = doc.add_table(rows=1 + len(actions), cols=4)
    table.style = "Table Grid"
    for ci, head in enumerate(ACTION_COLS):
        cell = table.rows[0].cells[ci]
        cell_text(cell, head, ACTION_TABLE_SIZE, bold=True)
        shade_cell(cell, TABLE_HEADER_FILL)
        cell.width = ACTION_COL_WIDTHS[ci]
    for ri, act in enumerate(actions, start=1):
        row = table.rows[ri]
        values = (str(ri), act["action"], act["responsible"], act["target"])
        for ci, val in enumerate(values):
            cell_text(row.cells[ci], val, ACTION_TABLE_SIZE)
            row.cells[ci].width = ACTION_COL_WIDTHS[ci]

    # closing record statement
    closing = CLOSING_TEXT
    if data.get("closing_extra"):
        closing = closing + " " + data["closing_extra"]
    add_gray_note(doc, closing, space_before=Pt(10))

    # deterministic core properties (author from the company config)
    cp = doc.core_properties
    cp.author = legal_name
    cp.last_modified_by = legal_name
    cp.title = title_text
    cp.subject = ""
    cp.keywords = ""
    cp.comments = ""
    cp.category = ""
    fixed = datetime.strptime(data["doc_date"], "%Y-%m-%d").replace(
        tzinfo=timezone.utc)
    cp.created = fixed
    cp.modified = fixed

    return doc


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(script_dir, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build Site Walk / Field Meeting Minutes .docx")
    ap.add_argument("data", nargs="?", default=os.path.join(script_dir, "sample_data.json"),
                    help="meeting data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=default_company,
                    help="company config JSON (default: ../../company.example.json)")
    args = ap.parse_args()

    if not os.path.isfile(args.data):
        fail("data file not found: %s" % args.data)
    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    company = load_company(args.company)
    doc = build(data, company)
    out_dir = data.get("output_dir") or "_sample_output"
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(script_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, data["output_basename"] + ".docx")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    src_zip = zipfile.ZipFile(buf)
    d0 = datetime.strptime(data["doc_date"], "%Y-%m-%d")
    dt = (d0.year, d0.month, d0.day, 0, 0, 0)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for name in sorted(src_zip.namelist()):
            zi = zipfile.ZipInfo(name, date_time=dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            out.writestr(zi, src_zip.read(name))
    print("wrote " + out_path)


if __name__ == "__main__":
    main()
