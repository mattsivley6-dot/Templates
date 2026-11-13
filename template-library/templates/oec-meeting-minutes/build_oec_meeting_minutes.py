"""Build OEC/OAC Progress Meeting Minutes (.docx).

Usage:
    python build_oec_meeting_minutes.py [data.json] [--company company.json]
                                        [--out-dir folder]

data.json defaults to sample_data.json next to this script.
--company defaults to template-library/company.example.json (two folders
up from this script). It supplies the contractor name, the default
"Prepared By" line and the docx author property.
--out-dir defaults to the current working directory.
Writes <output_basename>.docx.

Deterministic: no clock or random calls; every date and all variable
content come from the JSON data file. Core properties are fixed from
the data file so identical data gives identical output.
"""

import argparse
import json
import os
from datetime import datetime, timezone

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ---------------------------------------------------------------- style
NAVY = RGBColor(0x1A, 0x26, 0x4D)          # headings and title
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

# ---------------------------------------------------------- fixed wording
CLOSING_TEXT = (
    "These minutes reflect the writer's understanding of the items "
    "discussed and the conclusions reached. Please direct any corrections "
    "or additions to the writer within five (5) business days of receipt; "
    "otherwise these minutes will stand as the record of the meeting."
)
ATTENDANCE_HEADING = "Attendance"
ACTION_ITEMS_HEADING = "Action Items"
ATTEND_COLS = ("Name", "Organization", "Role")
ACTION_COLS = ("No.", "Action", "Responsible", "Target")


def load_company(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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
    run.font.color.rgb = NAVY
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

    # contractor and preparer default to the company config
    contractor = data.get("contractor") or company.get("legal_name", "")
    prepared_by = data.get("prepared_by") or ", ".join(
        v for v in (company.get("pm_name"), company.get("pm_title"),
                    company.get("legal_name")) if v)

    # title
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(data["doc_title"])
    run.font.size = TITLE_SIZE
    run.font.bold = True
    run.font.color.rgb = NAVY

    # project subtitle
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(data["project_line"])
    run.font.size = SUBTITLE_SIZE
    run.font.bold = True

    # masthead block
    add_masthead_line(doc, "Owner", data["owner"])
    add_masthead_line(doc, "Solicitation", data["solicitation"])
    add_masthead_line(doc, "Contractor", contractor)
    add_masthead_line(doc, "Engineer", data["engineer"])
    add_masthead_line(doc, "Meeting Date", data["meeting_date"])
    add_masthead_line(doc, data.get("location_label", "Format"),
                      data["location"])
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
    for ri, act in enumerate(actions, start=1):
        row = table.rows[ri]
        cell_text(row.cells[0], str(ri), ACTION_TABLE_SIZE)
        cell_text(row.cells[1], act["action"], ACTION_TABLE_SIZE)
        cell_text(row.cells[2], act["responsible"], ACTION_TABLE_SIZE)
        cell_text(row.cells[3], act["target"], ACTION_TABLE_SIZE)

    # closing record statement
    closing = CLOSING_TEXT
    if data.get("closing_extra"):
        closing = closing + " " + data["closing_extra"]
    add_gray_note(doc, closing, space_before=Pt(10))

    # deterministic core properties
    cp = doc.core_properties
    cp.author = company.get("dba") or company.get("legal_name", "")
    cp.last_modified_by = cp.author
    cp.title = data["doc_title"]
    cp.description = ""
    fixed = datetime.strptime(data["doc_date"], "%Y-%m-%d").replace(
        tzinfo=timezone.utc)
    cp.created = fixed
    cp.modified = fixed

    return doc


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(script_dir, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build OEC/OAC meeting minutes.")
    ap.add_argument("data", nargs="?",
                    default=os.path.join(script_dir, "sample_data.json"),
                    help="meeting data JSON (default: sample_data.json)")
    ap.add_argument("--company", default=default_company,
                    help="company config JSON (default: %(default)s)")
    ap.add_argument("--out-dir", default=".",
                    help="output folder (default: current directory)")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    company = load_company(args.company)
    doc = build(data, company)
    os.makedirs(args.out_dir, exist_ok=True)
    out_name = os.path.join(args.out_dir, data["output_basename"] + ".docx")
    doc.save(out_name)
    print("wrote " + os.path.abspath(out_name))


if __name__ == "__main__":
    main()
