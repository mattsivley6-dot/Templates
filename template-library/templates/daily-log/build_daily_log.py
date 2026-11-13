# -*- coding: utf-8 -*-
"""Build a Daily Log (Daily Construction Report, DCR) as .docx.

Usage:
    py -3 build_daily_log.py [data.json] [--company company.json]

If no data file is given, sample_data.json next to this script is used.
Company fields (legal name, brand color, PM name and title) come from the
company config, which defaults to ../../company.example.json relative to
this script. All variable content lives in the JSON data file; this script
holds only fixed wording and layout. Deterministic: no clock reads, no
randomness. Every date comes from the data file.
"""
import argparse
import json
import os
import sys
import zipfile
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- constants
DEFAULT_PRIMARY_HEX = '1F3A5F'             # used if the company config has no brand color
GRAY = RGBColor(0x59, 0x59, 0x59)          # info-line gray #595959
HEADER_FILL = 'E8EBF2'                     # table header shading
DOC_TITLE = "DAILY CONSTRUCTION REPORT"
GENERAL_CONDITIONS_LABEL = "GENERAL CONDITIONS"
DEFAULT_TABLE_WIDTHS_IN = [1.7, 4.6, 0.7]  # trades table column widths
PHOTO_WIDTH_IN = 3.0                       # 2-up photo width

# brand color, set from the company config in build()
PRIMARY = RGBColor.from_string(DEFAULT_PRIMARY_HEX)
PRIMARY_HEX = DEFAULT_PRIMARY_HEX


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


def style_base(doc):
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(10)
    st.paragraph_format.space_after = Pt(4)
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)


def header_block(doc, company_name, title, lines):
    p = doc.add_paragraph()
    r = p.add_run(company_name)
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = PRIMARY
    p.paragraph_format.space_after = Pt(0)
    p2 = doc.add_paragraph()
    r2 = p2.add_run(title)
    r2.bold = True
    r2.font.size = Pt(12)
    p2.paragraph_format.space_after = Pt(2)
    for line in lines:
        p3 = doc.add_paragraph()
        r3 = p3.add_run(line)
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = GRAY
        p3.paragraph_format.space_after = Pt(0)
    # brand-color horizontal rule under the header
    pr = doc.add_paragraph()
    pr.paragraph_format.space_before = Pt(4)
    pr.paragraph_format.space_after = Pt(6)
    pPr = pr._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:color'), PRIMARY_HEX)
    pBdr.append(bottom)
    pPr.append(pBdr)


def section_head(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = PRIMARY


def bullets(doc, items, indent=0.25):
    for it in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.left_indent = Inches(indent)
        p.paragraph_format.space_after = Pt(2)
        p.add_run(it)


def para(doc, runs):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    for text, bold in runs:
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(10)
    return p


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


def style_cell(cell, size_pt, bold=False):
    for pp in cell.paragraphs:
        for rr in pp.runs:
            rr.font.size = Pt(size_pt)
            if bold:
                rr.bold = True


# ---------------------------------------------------------------- build
def build(data, base_dir, company):
    global PRIMARY, PRIMARY_HEX
    PRIMARY_HEX = brand_hex(company)
    PRIMARY = RGBColor.from_string(PRIMARY_HEX)
    legal_name = company.get("legal_name") or "[Company Legal Name]"

    # prepared-by and signature default from the company config when the
    # data file leaves them out
    pm_line = ", ".join(x for x in (company.get("pm_name"), company.get("pm_title")) if x)
    prepared_by = data.get("prepared_by") or pm_line or "[PM Name], [PM Title]"
    signature_name_block = (data.get("signature_name_block")
                            or "%s\n%s" % (prepared_by, legal_name))

    doc = Document()
    style_base(doc)

    # header info lines (fixed prefixes, variable values)
    lines = [
        "Project: %s  |  Owner: %s" % (data["project_name"], data["owner"]),
        "Report No.: %s  |  %s: %s" % (data["report_no"],
                                       data.get("report_date_word", "Date"),
                                       data["report_date_text"]),
    ]
    contract_text = data.get("contract_text", "")
    completion_target = data.get("completion_target", "")
    if contract_text:
        line = "Contract: %s" % contract_text
        if completion_target:
            line += "  |  Substantial completion target: %s" % completion_target
        lines.append(line)
    lines.append("Prepared by: %s" % prepared_by)
    header_block(doc, legal_name.upper(), DOC_TITLE, lines)

    # weather table (4 columns, header row shaded)
    wh = data["weather_headers"]
    wv = data["weather_values"]
    if len(wh) != 4 or len(wv) != 4:
        fail("weather_headers and weather_values must each have exactly 4 entries")
    t = doc.add_table(rows=2, cols=4)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (h, v) in enumerate(zip(wh, wv)):
        c = t.rows[0].cells[i]
        c.text = h
        style_cell(c, 9, bold=True)
        set_cell_bg(c, HEADER_FILL)
        c2 = t.rows[1].cells[i]
        c2.text = v
        style_cell(c2, 9.5)

    # GENERAL CONDITIONS narrative
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run(GENERAL_CONDITIONS_LABEL)
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = PRIMARY
    para(doc, [(data["general_conditions"], False)])

    # numbered sections
    for idx, sec in enumerate(data["sections"], start=1):
        section_head(doc, "%d. %s" % (idx, sec["title"]))
        stype = sec.get("type", "bullets")

        if stype == "bullets":
            bullets(doc, sec["items"])

        elif stype == "table":
            headers = sec["headers"]
            rows = [headers] + [list(r) for r in sec["rows"]]
            ncols = len(headers)
            widths_in = sec.get("col_widths_in", DEFAULT_TABLE_WIDTHS_IN[:ncols])
            widths = [Inches(w) for w in widths_in]
            t2 = doc.add_table(rows=len(rows), cols=ncols)
            t2.style = 'Table Grid'
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    c = t2.rows[ri].cells[ci]
                    c.text = val
                    c.width = widths[ci]
                    style_cell(c, 9.5, bold=(ri == 0))
                if ri == 0:
                    for ci in range(ncols):
                        set_cell_bg(t2.rows[0].cells[ci], HEADER_FILL)

        elif stype == "photos":
            photo_dir = sec.get("photo_dir", "")
            for pair in sec["pairs"]:
                tb = doc.add_table(rows=2, cols=2)
                tb.style = 'Table Grid'
                for ci, item in enumerate(pair):
                    fname = item["file"]
                    path = fname
                    if photo_dir:
                        path = os.path.join(photo_dir, fname)
                    if not os.path.isabs(path):
                        path = os.path.join(base_dir, path)
                    if not os.path.isfile(path):
                        fail("photo not found: %s" % path)
                    cell = tb.rows[0].cells[ci]
                    cp = cell.paragraphs[0]
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = cp.add_run()
                    run.add_picture(path, width=Inches(PHOTO_WIDTH_IN))
                    capc = tb.rows[1].cells[ci]
                    capc.text = item["caption"]
                    for rr in capc.paragraphs[0].runs:
                        rr.font.size = Pt(8)
                        rr.font.color.rgb = GRAY
                doc.add_paragraph().paragraph_format.space_after = Pt(2)

        else:
            fail("unknown section type %r in section %d" % (stype, idx))

    # signature block
    doc.add_paragraph()
    sig = doc.add_table(rows=2, cols=2)
    sig.style = 'Table Grid'
    sig.rows[0].cells[0].text = "Prepared by:"
    sig.rows[0].cells[1].text = "Date:"
    sig.rows[1].cells[0].text = signature_name_block
    sig.rows[1].cells[1].text = data["signature_date"]
    for row in sig.rows:
        for c in row.cells:
            style_cell(c, 9.5)
    for ci in range(2):
        set_cell_bg(sig.rows[0].cells[ci], HEADER_FILL)
        sig.rows[0].cells[ci].paragraphs[0].runs[0].bold = True

    # stable core properties (determinism: author from company config,
    # dates from data file)
    fixed_dt = datetime.strptime(data["doc_created_iso"], "%Y-%m-%dT%H:%M:%S")
    cp = doc.core_properties
    cp.author = legal_name
    cp.last_modified_by = legal_name
    cp.created = fixed_dt
    cp.modified = fixed_dt
    cp.title = "%s %s" % (DOC_TITLE.title(), data["report_no"])
    cp.subject = ""
    cp.keywords = ""
    cp.comments = ""
    cp.category = ""
    cp.revision = 1

    return doc


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(script_dir, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build a Daily Log (DCR) .docx")
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

    base_dir = os.path.dirname(os.path.abspath(args.data))
    doc = build(data, base_dir, company)

    out_dir = data.get("output_dir", "_sample_output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(script_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_name = "%s Daily Log - %s.docx" % (data["file_date_label"], data["project_short"])
    out_path = os.path.join(out_dir, out_name)
    doc.save(out_path)
    fixed_dt = datetime.strptime(data["doc_created_iso"], "%Y-%m-%dT%H:%M:%S")
    normalize_zip_times(out_path, fixed_dt)
    print("saved", out_path)


if __name__ == "__main__":
    main()
