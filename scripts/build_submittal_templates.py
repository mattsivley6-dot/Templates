"""
Build clean submittal-flow templates.

Three artifacts, individually and combined:
  01_Transmittal.docx              - delivery cover / routing slip
  02_Submittal_Cover_Sheet.docx    - per-submittal title page (project, parties, action stamp)
  03_Submittal_Index.docx          - itemized list of submittal contents + deviations
  04_Submittal_Package_Combined.docx - all three back-to-back as one deliverable

Structure mirrors PMI/PMBOK communications artifacts adapted to AEC
submittal practice (CSI division, spec section references, A/E action stamp).
All project-specific data is replaced with [bracketed placeholders].
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "templates", "submittals"))
os.makedirs(OUT, exist_ok=True)

PMI_BLUE = RGBColor(0x1F, 0x3A, 0x5F)
PMI_ACCENT = RGBColor(0x2E, 0x75, 0xB6)
HEADER_FILL = "1F3A5F"
SUB_FILL = "D9E2F3"


def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)


def set_run(run, bold=False, size=10, color=None, name="Calibri"):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_title(doc, text, size=18):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_run(r, bold=True, size=size, color=PMI_BLUE)


def add_centered_title(doc, text, size=18):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_run(r, bold=True, size=size, color=PMI_BLUE)


def add_h2(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run(r, bold=True, size=12, color=PMI_BLUE)


def add_h3(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run(r, bold=True, size=10, color=PMI_ACCENT)


def add_para(doc, text, bold=False, size=10, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    set_run(r, bold=bold, size=size)


def set_col_widths(table, widths):
    table.autofit = False
    table.allow_autofit = False
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if idx < len(widths):
                cell.width = Inches(widths[idx])


def add_horizontal_rule(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F3A5F')
    pBdr.append(bottom)
    pPr.append(pBdr)


def set_portrait(doc):
    section = doc.sections[0]
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)


def build_kv_table(doc, rows, key_w=1.4, value_w=5.6, key_fill=HEADER_FILL,
                   key_color=RGBColor(0xFF, 0xFF, 0xFF)):
    t = doc.add_table(rows=len(rows), cols=2)
    t.style = 'Light List Accent 1'
    for i, (k, v) in enumerate(rows):
        c0 = t.rows[i].cells[0]
        c1 = t.rows[i].cells[1]
        c0.text = ""
        c1.text = ""
        r0 = c0.paragraphs[0].add_run(k)
        set_run(r0, bold=True, size=9, color=key_color)
        set_cell_shading(c0, key_fill)
        r1 = c1.paragraphs[0].add_run(v)
        set_run(r1, size=10)
    set_col_widths(t, [key_w, value_w])
    return t


def build_table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Light Grid Accent 1'
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        set_run(r, bold=True, size=9, color=RGBColor(0xFF, 0xFF, 0xFF))
        set_cell_shading(cell, HEADER_FILL)
    for ri, rowdata in enumerate(rows, start=1):
        for ci, val in enumerate(rowdata):
            cell = t.rows[ri].cells[ci]
            cell.text = ""
            r = cell.paragraphs[0].add_run(str(val) if val is not None else "")
            set_run(r, size=9)
    if widths:
        set_col_widths(t, widths)
    return t


# -----------------------------------------------------------------------------
# Section builders (callable in standalone docs or in the combined doc)
# -----------------------------------------------------------------------------

def section_letterhead(doc):
    """Sender block - top of every transmittal."""
    add_para(doc, "[Company Name]", bold=True, size=11)
    add_para(doc, "[Street Address]", size=9)
    add_para(doc, "[City, State ZIP]", size=9)
    add_para(doc, "[Phone]", size=9)
    add_para(doc, "[Website]", size=9)


def section_transmittal(doc):
    """The TRANSMITTAL routing slip."""
    add_centered_title(doc, "TRANSMITTAL", size=16)
    doc.add_paragraph()

    # Date
    build_kv_table(doc, [["DATE:", "[YYYY-MM-DD]"]],
                   key_w=1.0, value_w=6.0)
    doc.add_paragraph()

    # TO / VIA block
    t = doc.add_table(rows=5, cols=4)
    t.style = 'Light Grid Accent 1'
    # Row 0
    t.rows[0].cells[0].text = ""
    r = t.rows[0].cells[0].paragraphs[0].add_run("TO:")
    set_run(r, bold=True, size=9, color=RGBColor(0xFF, 0xFF, 0xFF))
    set_cell_shading(t.rows[0].cells[0], HEADER_FILL)
    t.rows[0].cells[1].text = ""
    set_run(t.rows[0].cells[1].paragraphs[0].add_run("[Recipient Firm]"), size=10)
    t.rows[0].cells[2].text = ""
    r2 = t.rows[0].cells[2].paragraphs[0].add_run("VIA:")
    set_run(r2, bold=True, size=9, color=RGBColor(0xFF, 0xFF, 0xFF))
    set_cell_shading(t.rows[0].cells[2], HEADER_FILL)
    t.rows[0].cells[3].text = ""
    set_run(t.rows[0].cells[3].paragraphs[0].add_run("[ ] U.S. MAIL"), size=9)
    # Row 1
    t.rows[1].cells[0].text = ""
    r = t.rows[1].cells[0].paragraphs[0].add_run("ATTN:")
    set_run(r, bold=True, size=9, color=RGBColor(0xFF, 0xFF, 0xFF))
    set_cell_shading(t.rows[1].cells[0], HEADER_FILL)
    t.rows[1].cells[1].text = ""
    set_run(t.rows[1].cells[1].paragraphs[0].add_run("[Recipient Name]"), size=10)
    t.rows[1].cells[2].text = ""
    t.rows[1].cells[3].text = ""
    set_run(t.rows[1].cells[3].paragraphs[0].add_run("[ ] HAND DELIVERED"), size=9)
    # Row 2
    t.rows[2].cells[0].text = ""
    t.rows[2].cells[1].text = ""
    set_run(t.rows[2].cells[1].paragraphs[0].add_run("[Street Address]"), size=10)
    t.rows[2].cells[2].text = ""
    t.rows[2].cells[3].text = ""
    set_run(t.rows[2].cells[3].paragraphs[0].add_run("[ ] LOCAL DELIVERY"), size=9)
    # Row 3
    t.rows[3].cells[0].text = ""
    t.rows[3].cells[1].text = ""
    set_run(t.rows[3].cells[1].paragraphs[0].add_run("[City, State ZIP]"), size=10)
    t.rows[3].cells[2].text = ""
    t.rows[3].cells[3].text = ""
    set_run(t.rows[3].cells[3].paragraphs[0].add_run("[ ] OVERNIGHT SHIPMENT"), size=9)
    # Row 4
    t.rows[4].cells[0].text = ""
    t.rows[4].cells[1].text = ""
    t.rows[4].cells[2].text = ""
    t.rows[4].cells[3].text = ""
    set_run(t.rows[4].cells[3].paragraphs[0].add_run("[X] EMAIL"), size=9)
    set_col_widths(t, [0.7, 3.0, 0.7, 2.7])
    doc.add_paragraph()

    # PROJECT
    build_kv_table(doc, [
        ["PROJECT:", "[Project Name]"],
        ["PROJECT #:", "[Contract # / A&E Project #]"],
    ], key_w=1.2, value_w=5.8)
    doc.add_paragraph()

    # TRANSMITTED / ITEM
    add_h3(doc, "Transmitted")
    t = doc.add_table(rows=4, cols=4)
    t.style = 'Light Grid Accent 1'
    cells = [
        ["TRANSMITTED:", "[X] HEREWITH",      "",                   "[ ] SEPARATELY"],
        ["ITEM:",        "[ ] ORIGINAL DRAWINGS", "[ ] COPY OF LETTER", "[X] SUBMITTALS"],
        ["",             "[ ] PRINTS",         "[ ] SPECIFICATIONS",  "[ ] SAMPLES"],
        ["",             "[ ] SPECIFICATIONS", "[ ] OTHER",           ""],
    ]
    for ri, row in enumerate(cells):
        for ci, val in enumerate(row):
            tc = t.rows[ri].cells[ci]
            tc.text = ""
            run = tc.paragraphs[0].add_run(val)
            if ci == 0 and val:
                set_run(run, bold=True, size=9, color=RGBColor(0xFF, 0xFF, 0xFF))
                set_cell_shading(tc, HEADER_FILL)
            else:
                set_run(run, size=9)
    set_col_widths(t, [1.2, 1.9, 2.0, 2.0])
    doc.add_paragraph()

    # Description table
    add_h3(doc, "Items Transmitted")
    build_table(doc, ["Quantity", "Dated", "Description"], [
        ["[#]", "[YYYY-MM-DD]", "[Description of the transmitted item / submittal package]"],
        ["", "", ""],
        ["", "", ""],
    ], widths=[1.0, 1.2, 4.8])
    doc.add_paragraph()

    # Remarks
    add_h3(doc, "Remarks")
    add_para(doc, "[One paragraph summarizing what is enclosed, the spec "
                  "section it satisfies, and any context the reviewer needs "
                  "(revision number, scope coverage, related RFIs, requested "
                  "action).]", size=10)
    doc.add_paragraph()

    # Signature
    build_kv_table(doc, [
        ["By:", "[Name, Title]"],
    ], key_w=1.0, value_w=6.0)


def section_submittal_cover_sheet(doc):
    """The SUBMITTAL COVER SHEET - title page for one submittal."""
    add_centered_title(doc, "SUBMITTAL COVER SHEET", size=16)
    add_para(doc, "Division [## ## ##] - [Division Name]",
             bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    add_h3(doc, "Project")
    build_kv_table(doc, [
        ["Project Name:", "[Project Name]"],
        ["Project / CSP Number:", "[Contract # / CSP #]"],
        ["A&E Project No.:", "[Architect/Engineer Project #]"],
        ["Location:", "[Site Address]"],
        ["Date:", "[YYYY-MM-DD]"],
        ["Submittal No.:", "[Spec section - sequential, e.g. 26 00 00-01]"],
        ["Submittal Type:", "[Product Data / Shop Drawings / Samples / Engineering / Mock-up / Other]"],
    ], key_w=1.8, value_w=5.2)
    doc.add_paragraph()

    add_h3(doc, "Architect / Engineer")
    build_kv_table(doc, [
        ["Firm:", "[A/E Firm]"],
        ["Attention:", "[Reviewer Name]"],
        ["Address:", "[Street, City, State ZIP]"],
    ], key_w=1.8, value_w=5.2)
    doc.add_paragraph()

    add_h3(doc, "Prime Contractor / General Contractor")
    build_kv_table(doc, [
        ["Firm:", "[Prime Contractor]"],
        ["Contact:", "[Name, Title]"],
        ["Address:", "[Street, City, State ZIP]"],
        ["Phone:", "[Phone]"],
    ], key_w=1.8, value_w=5.2)
    doc.add_paragraph()

    add_h3(doc, "Subcontractor / Equipment Supplier")
    build_kv_table(doc, [
        ["Firm:", "[Sub or Supplier]"],
        ["Contact:", "[Name]"],
        ["Email:", "[Email]"],
        ["PO Number:", "[PO #]"],
    ], key_w=1.8, value_w=5.2)
    doc.add_paragraph()

    add_h3(doc, "Contractor Action Stamp")
    build_table(doc, ["[ ] APPROVED", "[ ] APPROVED AS NOTED",
                      "[ ] REVISE & RESUBMIT", "[ ] REJECTED"],
                [["", "", "", ""]], widths=[1.75, 1.75, 1.75, 1.75])
    doc.add_paragraph()
    add_para(doc, "Contractor has reviewed submittal data against "
                  "specifications. Forwarded to Architect/Engineer for review "
                  "and comment.", size=10)
    doc.add_paragraph()
    build_kv_table(doc, [
        ["Contractor Signature:", "[Name, Title]"],
        ["Date:", "[YYYY-MM-DD]"],
    ], key_w=1.8, value_w=5.2)
    doc.add_paragraph()

    add_h3(doc, "A/E Review Stamp (For A/E Use)")
    build_table(doc, ["[ ] NO EXCEPTIONS TAKEN", "[ ] MAKE CORRECTIONS NOTED",
                      "[ ] REVISE & RESUBMIT", "[ ] REJECTED"],
                [["", "", "", ""]], widths=[1.75, 1.75, 1.75, 1.75])
    doc.add_paragraph()
    build_kv_table(doc, [
        ["Reviewed By:", ""],
        ["Date:", ""],
        ["Comments:", ""],
    ], key_w=1.8, value_w=5.2)


def section_submittal_index(doc):
    """The SUBMITTAL INDEX - itemized contents + deviations."""
    add_centered_title(doc, "SUBMITTAL INDEX", size=16)
    add_para(doc, "Division [## ## ##] - [Division Name]",
             bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    add_h3(doc, "Items Submitted")
    rows = [
        ["1", "[Product / shop drawing / sample description - manufacturer, "
              "model, rating, application, quantity]", "[## ## ##]"],
    ]
    for n in range(2, 7):
        rows.append([str(n), "", ""])
    build_table(doc, ["Item", "Description", "Spec Section"], rows,
                widths=[0.6, 5.4, 1.0])
    doc.add_paragraph()

    add_h3(doc, "Contractor's Remarks")
    add_para(doc, "Contractor has reviewed submitted product data against "
                  "Division [##] specifications. The following remarks are "
                  "provided for the A/E's consideration.", size=10)
    doc.add_paragraph()
    build_table(doc, ["#", "Remark", "Spec Ref.", "Status"], [
        ["1", "[Note any clarifications, quantity verifications, or "
              "questions the A/E should address]", "[## ## ##]",
         "FOR REVIEW"],
        ["2", "[Note items not included in this submittal but covered "
              "elsewhere or available on request]", "[## ## ##]", "FOR INFO"],
        ["", "", "", ""],
    ], widths=[0.5, 4.5, 1.0, 1.0])
    doc.add_paragraph()

    add_h3(doc, "Known Deviations from Contract Documents")
    add_para(doc, "Per Section [23 00 90 / 01 33 00], the following deviations "
                  "are noted where submittals differ from the contract "
                  "documents. All items are flagged with revision clouds and "
                  "callout notes in the attached markup for A/E review and "
                  "comment.", size=10)
    doc.add_paragraph()
    build_table(doc, ["No.", "Deviation", "Spec Ref.", "Severity"], [
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ], widths=[0.5, 4.5, 1.0, 1.0])
    doc.add_paragraph()

    add_para(doc, "Submittal No.: [## ## ##-##]  |  Date: [YYYY-MM-DD]  |  "
                  "Project / CSP #: [##]  |  A&E Project #: [##]",
             size=9, align=WD_ALIGN_PARAGRAPH.CENTER)


# -----------------------------------------------------------------------------
# Doc builders
# -----------------------------------------------------------------------------

def build_transmittal():
    doc = Document()
    set_portrait(doc)
    section_letterhead(doc)
    add_horizontal_rule(doc)
    section_transmittal(doc)
    out = os.path.join(OUT, "01_Transmittal.docx")
    doc.save(out)
    return out


def build_cover_sheet():
    doc = Document()
    set_portrait(doc)
    section_letterhead(doc)
    add_horizontal_rule(doc)
    section_submittal_cover_sheet(doc)
    out = os.path.join(OUT, "02_Submittal_Cover_Sheet.docx")
    doc.save(out)
    return out


def build_index():
    doc = Document()
    set_portrait(doc)
    section_letterhead(doc)
    add_horizontal_rule(doc)
    section_submittal_index(doc)
    out = os.path.join(OUT, "03_Submittal_Index.docx")
    doc.save(out)
    return out


def build_combined():
    doc = Document()
    set_portrait(doc)
    section_letterhead(doc)
    add_horizontal_rule(doc)
    add_para(doc, "Complete submittal package - bound for transmittal to the "
                  "A/E. Sequence: (1) Transmittal cover, (2) Submittal Cover "
                  "Sheet, (3) Submittal Index, followed by the product "
                  "data / shop drawings / samples themselves.",
             size=9)
    doc.add_paragraph()

    # 1. Transmittal
    section_transmittal(doc)
    doc.add_page_break()

    # 2. Cover Sheet
    section_submittal_cover_sheet(doc)
    doc.add_page_break()

    # 3. Index
    section_submittal_index(doc)

    out = os.path.join(OUT, "04_Submittal_Package_Combined.docx")
    doc.save(out)
    return out


def main():
    for fn in [build_transmittal, build_cover_sheet, build_index, build_combined]:
        path = fn()
        print(f"wrote {os.path.basename(path)}")


if __name__ == '__main__':
    main()
