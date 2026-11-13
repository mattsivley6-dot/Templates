# -*- coding: utf-8 -*-
"""Build an Open Items / Action Tracker as .docx.

Usage:
    py -3 build_action_items_tracker.py [data.json] [--company company.json]

If no data file is given, sample_data.json next to this script is used.
Company fields (legal name, brand color) come from the company config,
which defaults to ../../company.example.json relative to this script.
All variable content lives in the JSON data file; this script holds only
fixed wording and layout. Deterministic: no clock reads, no randomness.
Every date comes from the data file.
"""
import argparse
import json
import os
import sys
import zipfile
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- constants
DEFAULT_PRIMARY_HEX = '1F3A5F'             # used if the company config has no brand color
GRAY = RGBColor(0x59, 0x59, 0x59)          # info-line gray #595959
RED = RGBColor(0xB0, 0x00, 0x20)           # High-priority red #B00020 (portrait profile)
HEADER_FILL = 'E8EBF2'                     # table header shading
DOC_TITLE = "OPEN ITEMS / ACTION TRACKER"
TABLE_HEADERS = ["#", "Action item", "Owner", "Due", "Pri.", "Status"]
PRIORITIES = ("High", "Med", "Low")
DEFAULT_LEGEND = ("Priority: High / Med / Low.  Owner roles use trade labels for "
                  "subcontractors.  This tracker is a working contractor record; "
                  "financial items (PCOs, credits, pay applications) move through "
                  "the change order and pay-application channels.")

# Two look profiles. "landscape" is the default; "portrait" is a compact
# variant with a rule under the header and red High priority.
PROFILES = {
    "landscape": {
        "page_w_in": 11.0, "page_h_in": 8.5, "landscape": True,
        "margins_in": {"top": 0.6, "bottom": 0.6, "left": 0.6, "right": 0.6},
        "normal_size_pt": 9.5, "normal_space_after_pt": None,
        "title_size_pt": 13,
        "divider": "spacer",               # plain empty paragraph, space after 2 pt
        "col_widths_in": [0.5, 5.9, 1.7, 1.4, 0.6, 1.6],
        "bold_ids": True,                  # A-01 etc. bold in the # column
        "default_legend": DEFAULT_LEGEND,  # italic legend line under the table
        "default_highlight_high": False,   # High priority not color-coded
    },
    "portrait": {
        "page_w_in": 8.5, "page_h_in": 11.0, "landscape": False,
        "margins_in": {"top": 0.7, "bottom": 0.7, "left": 0.8, "right": 0.8},
        "normal_size_pt": 10, "normal_space_after_pt": 4,
        "title_size_pt": 14,
        "divider": "rule",                 # brand-color bottom-border rule paragraph
        "col_widths_in": [0.45, 3.7, 0.95, 0.85, 0.55, 0.85],
        "bold_ids": False,
        "default_legend": "",              # no legend line by default
        "default_highlight_high": True,    # High rendered bold red #B00020
    },
}


# ---------------------------------------------------------------- helpers
def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def check_no_dashes(obj, path="data"):
    """House rule: no em or en dashes anywhere. Fail loudly if found."""
    if isinstance(obj, str):
        if chr(0x2014) in obj or chr(0x2013) in obj:  # em dash, en dash
            fail("em/en dash found at %s: %r" % (path, obj[:80]))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_no_dashes(v, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_no_dashes(v, "%s[%d]" % (path, i))


def load_company(path):
    if not os.path.isfile(path):
        fail("company config not found: %s" % path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def brand_hex(company):
    """Primary brand color from the company config as 6-digit hex, no '#'."""
    raw = ((company.get("brand") or {}).get("primary_color") or DEFAULT_PRIMARY_HEX)
    raw = raw.lstrip("#")
    if len(raw) != 6:
        fail("brand.primary_color must be a 6-digit hex color, got %r" % raw)
    return raw.upper()


def set_cell_bg(cell, hexcolor):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), hexcolor)
    cell._tc.get_or_add_tcPr().append(shd)


def cell_run(cell, text, size_pt, bold=False, color=None):
    """Put a single styled run in the cell's first paragraph."""
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.font.size = Pt(size_pt)
    if bold:
        r.bold = True
    if color is not None:
        r.font.color.rgb = color
    return r


def normalize_zip_times(path, dt):
    """Rewrite the docx zip with fixed entry timestamps taken from the data
    file, so identical data gives a byte-identical file (python-docx stamps
    zip entries with the wall clock at save time)."""
    date_time = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    with zipfile.ZipFile(path, "r") as zin:
        entries = [(item, zin.read(item.filename)) for item in zin.infolist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item, blob in entries:
            zi = zipfile.ZipInfo(item.filename, date_time=date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = item.external_attr
            zout.writestr(zi, blob)


# ---------------------------------------------------------------- build
def build(data, company):
    orientation = data.get("orientation", "landscape")
    if orientation not in PROFILES:
        fail("orientation must be 'landscape' or 'portrait', got %r" % orientation)
    prof = PROFILES[orientation]

    primary_hex = brand_hex(company)
    primary = RGBColor.from_string(primary_hex)
    company_name = (company.get("legal_name") or "[Company Legal Name]").upper()

    items = data.get("items", [])
    if not items:
        fail("items must be a non-empty list")
    for i, it in enumerate(items):
        for key in ("id", "action", "owner", "due", "priority", "status"):
            if not it.get(key):
                fail("items[%d] is missing a non-empty %r" % (i, key))
        if it["priority"] not in PRIORITIES:
            fail("items[%d].priority must be one of %s, got %r"
                 % (i, "/".join(PRIORITIES), it["priority"]))

    doc = Document()

    # base style and page setup (must precede add_table so the table grid
    # is computed from the correct text-column width)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(prof["normal_size_pt"])
    if prof["normal_space_after_pt"] is not None:
        st.paragraph_format.space_after = Pt(prof["normal_space_after_pt"])
    sec = doc.sections[0]
    if prof["landscape"]:
        sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width = Inches(prof["page_w_in"])
    sec.page_height = Inches(prof["page_h_in"])
    m = prof["margins_in"]
    sec.top_margin = Inches(m["top"])
    sec.bottom_margin = Inches(m["bottom"])
    sec.left_margin = Inches(m["left"])
    sec.right_margin = Inches(m["right"])

    # header block: company name, document title, three gray info lines
    p = doc.add_paragraph()
    r = p.add_run(company_name)
    r.bold = True
    r.font.size = Pt(prof["title_size_pt"])
    r.font.color.rgb = primary
    p.paragraph_format.space_after = Pt(0)

    p2 = doc.add_paragraph()
    r2 = p2.add_run(DOC_TITLE)
    r2.bold = True
    r2.font.size = Pt(12)
    p2.paragraph_format.space_after = Pt(2)

    project_line = "Project: %s  |  Owner: %s" % (data["project_name"], data["owner"])
    if data.get("csp_number"):
        project_line += "  |  CSP #%s" % data["csp_number"]
    info_lines = [
        project_line,
        data["source_line"],
        "Prepared by: %s  |  Updated: %s" % (data["prepared_by"], data["updated_date"]),
    ]
    for line in info_lines:
        p3 = doc.add_paragraph()
        r3 = p3.add_run(line)
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = GRAY
        p3.paragraph_format.space_after = Pt(0)

    # divider between header block and table
    pd = doc.add_paragraph()
    if prof["divider"] == "rule":
        # brand-color horizontal rule (portrait look)
        pd.paragraph_format.space_before = Pt(4)
        pd.paragraph_format.space_after = Pt(6)
        pPr = pd._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12')
        bottom.set(qn('w:color'), primary_hex)
        pBdr.append(bottom)
        pPr.append(pBdr)
    else:
        # plain spacer (landscape look)
        pd.paragraph_format.space_after = Pt(2)

    # tracker table
    highlight_high = bool(data.get("highlight_high_priority",
                                   prof["default_highlight_high"]))
    widths = [Inches(w) for w in prof["col_widths_in"]]
    t = doc.add_table(rows=1 + len(items), cols=6)
    t.style = 'Table Grid'
    for ci, htext in enumerate(TABLE_HEADERS):
        c = t.rows[0].cells[ci]
        c.width = widths[ci]
        set_cell_bg(c, HEADER_FILL)
        cell_run(c, htext, 9, bold=True)
    for ri, it in enumerate(items, start=1):
        row = t.rows[ri]
        values = [it["id"], it["action"], it["owner"],
                  it["due"], it["priority"], it["status"]]
        for ci, val in enumerate(values):
            c = row.cells[ci]
            c.width = widths[ci]
            bold = False
            color = None
            if ci == 0 and prof["bold_ids"]:
                bold = True
            if ci == 4 and highlight_high and val == "High":
                bold = True
                color = RED
            cell_run(c, val, 8.5, bold=bold, color=color)

    # legend line under the table
    legend = data.get("legend_text", prof["default_legend"])
    if legend:
        pl = doc.add_paragraph()
        pl.paragraph_format.space_before = Pt(6)
        rl = pl.add_run(legend)
        rl.italic = True
        rl.font.size = Pt(8)
        rl.font.color.rgb = GRAY

    # stable core properties (determinism: author from company config,
    # dates from data file)
    fixed_dt = datetime.strptime(data["doc_created_iso"], "%Y-%m-%dT%H:%M:%S")
    author = company.get("legal_name") or "[Company Legal Name]"
    cp = doc.core_properties
    cp.author = author
    cp.last_modified_by = author
    cp.created = fixed_dt
    cp.modified = fixed_dt
    cp.title = "Open Items / Action Tracker - %s - %s" % (
        data["project_short"], data["file_date_label"])
    cp.subject = ""
    cp.keywords = ""
    cp.comments = ""
    cp.category = ""
    cp.revision = 1

    return doc, fixed_dt


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(script_dir, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build an Open Items / Action Tracker .docx")
    ap.add_argument("data", nargs="?", default=os.path.join(script_dir, "sample_data.json"),
                    help="job data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=default_company,
                    help="company config JSON (default: ../../company.example.json)")
    args = ap.parse_args()

    if not os.path.isfile(args.data):
        fail("data file not found: %s" % args.data)
    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)
    company = load_company(args.company)

    check_no_dashes(data)
    check_no_dashes(company, "company")

    doc, fixed_dt = build(data, company)

    out_dir = data.get("output_dir", "_sample_output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(script_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_name = "%s Action Items - %s.docx" % (data["file_date_label"], data["project_short"])
    out_path = os.path.join(out_dir, out_name)
    doc.save(out_path)
    normalize_zip_times(out_path, fixed_dt)
    print("saved", out_path)


if __name__ == "__main__":
    main()
