"""
Build clean submittal-flow templates that mirror the real Centric visual style.

Visual style (from the existing Centric submittal package):
  - Left-aligned letterhead (small) at top: company name bold, address /
    phone / URL in 9pt.
  - Transmittal title is centered "TRANSMITTAL" in plain bold, no banner.
  - Field tables use LIGHT BLUE shading (#DAE3F3) on label cells, plain
    white on value cells. Black text everywhere.
  - No horizontal rules. No sub-section headers in the transmittal.
  - Cover Sheet and Index pages each open with a dark-navy BANNER
    (#1F3864, white text) showing the artifact title + Division.
  - Cover Sheet body uses bold all-caps section headings (PROJECT,
    ENGINEER, PRIME CONTRACTOR, etc.) with KV pairs underneath.
  - Index uses two tables: ITEMS SUBMITTED and KNOWN DEVIATIONS, each with
    a light-blue header row.

Outputs (in /templates/submittals/):
  01_Transmittal.docx
  02_Submittal_Cover_Sheet.docx
  03_Submittal_Index.docx
  04_Submittal_Package_Combined.docx
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

# Real Centric palette (matches the rendered PDFs)
BANNER_NAVY = "1F3864"     # cover sheet / index banner fill
LABEL_BLUE = "DAE3F3"      # light-blue label cell fill (Accent 1, Lighter 80%)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HYPER_BLUE = RGBColor(0x05, 0x63, 0xC1)


# -----------------------------------------------------------------------------
# Low-level helpers
# -----------------------------------------------------------------------------

def shd(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear')
    s.set(qn('w:color'), 'auto')
    s.set(qn('w:fill'), fill_hex)
    tcPr.append(s)


def set_run(run, bold=False, size=10, color=BLACK, name="Calibri"):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_para(doc, text, bold=False, size=10, color=BLACK,
             align=None, name="Calibri"):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    set_run(r, bold=bold, size=size, color=color, name=name)
    return p


def set_col_widths(table, widths):
    table.autofit = False
    table.allow_autofit = False
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if idx < len(widths):
                cell.width = Inches(widths[idx])


def add_table_borders(table):
    """Plain single-line borders for every cell."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), '7F7F7F')
        tblBorders.append(b)
    tblPr.append(tblBorders)


def cell_text(cell, text, bold=False, size=10, color=BLACK,
              fill=None, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    set_run(r, bold=bold, size=size, color=color)
    if fill is not None:
        shd(cell, fill)


# -----------------------------------------------------------------------------
# Reusable structure blocks
# -----------------------------------------------------------------------------

def letterhead(doc):
    """Top-of-page company block (left-aligned, small)."""
    add_para(doc, "[Company Name]", bold=True, size=11)
    add_para(doc, "[Street Address]", size=9)
    add_para(doc, "[City, State ZIP]", size=9)
    add_para(doc, "[Phone]", size=9)
    p = doc.add_paragraph()
    r = p.add_run("[Website]")
    set_run(r, size=9, color=HYPER_BLUE)
    r.font.underline = True


def banner(doc, title, subtitle):
    """Dark-navy banner used on Cover Sheet and Index pages."""
    t = doc.add_table(rows=2, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Title row
    c = t.rows[0].cells[0]
    c.text = ""
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(title), bold=True, size=18, color=WHITE)
    shd(c, BANNER_NAVY)
    # Subtitle row
    c2 = t.rows[1].cells[0]
    c2.text = ""
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p2.add_run(subtitle), size=10, color=WHITE)
    shd(c2, BANNER_NAVY)
    set_col_widths(t, [7.1])
    # Remove cell padding by setting tight margins on the table
    return t


def section_header(doc, text):
    """Bold all-caps heading used inside Cover Sheet/Index sections."""
    p = doc.add_paragraph()
    set_run(p.add_run(text.upper()), bold=True, size=11)


def kv_underline(doc, rows, label_width=1.6, value_width=5.4):
    """
    Cover Sheet KV style: bold label on left, underlined plain value on right.
    Implemented as a borderless 2-col table with a bottom border on the value cell.
    """
    t = doc.add_table(rows=len(rows), cols=2)
    # Use a plain style and we'll add only bottom borders to value cells
    for i, (k, v) in enumerate(rows):
        c0 = t.rows[i].cells[0]
        c1 = t.rows[i].cells[1]
        cell_text(c0, k, bold=True, size=10)
        cell_text(c1, v, size=10)
        # Bottom border on the value cell to mimic a fill-in line
        tcPr = c1._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:color'), 'A6A6A6')
        tcBorders.append(bottom)
        tcPr.append(tcBorders)
    set_col_widths(t, [label_width, value_width])
    return t


# -----------------------------------------------------------------------------
# TRANSMITTAL section
# -----------------------------------------------------------------------------

def section_transmittal(doc):
    # Centered "TRANSMITTAL" title (no banner, plain black bold)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run("TRANSMITTAL"), bold=True, size=20)
    doc.add_paragraph()

    # DATE row (single-row 2-col table, bordered)
    t = doc.add_table(rows=1, cols=2)
    add_table_borders(t)
    cell_text(t.rows[0].cells[0], "DATE:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "[YYYY-MM-DD]", size=10)
    set_col_widths(t, [1.0, 6.1])
    doc.add_paragraph()

    # TO / VIA / PROJECT combined 6-row x 4-col grid
    t = doc.add_table(rows=6, cols=4)
    add_table_borders(t)
    # Row 0: TO / firm / VIA / U.S. MAIL
    cell_text(t.rows[0].cells[0], "TO:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "[Recipient Firm]", size=10)
    cell_text(t.rows[0].cells[2], "VIA:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[3], "U.S. MAIL", size=10)
    # Row 1: ATTN / name / / HAND DELIVERED
    cell_text(t.rows[1].cells[0], "ATTN:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[1].cells[1], "[Recipient Name]", size=10)
    cell_text(t.rows[1].cells[2], "", size=10)
    cell_text(t.rows[1].cells[3], "HAND DELIVERED", size=10)
    # Row 2: blank / street / / LOCAL DELIVERY
    cell_text(t.rows[2].cells[0], "", size=10)
    cell_text(t.rows[2].cells[1], "[Street Address]", size=10)
    cell_text(t.rows[2].cells[2], "", size=10)
    cell_text(t.rows[2].cells[3], "LOCAL DELIVERY", size=10)
    # Row 3: blank / city / / OVERNIGHT
    cell_text(t.rows[3].cells[0], "", size=10)
    cell_text(t.rows[3].cells[1], "[City, State ZIP]", size=10)
    cell_text(t.rows[3].cells[2], "", size=10)
    cell_text(t.rows[3].cells[3], "OVERNIGHT SHIPMENT", size=10)
    # Row 4: blank / blank / "x" / Email
    cell_text(t.rows[4].cells[0], "", size=10)
    cell_text(t.rows[4].cells[1], "", size=10)
    cell_text(t.rows[4].cells[2], "x", bold=True, size=10,
              align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_text(t.rows[4].cells[3], "Email", size=10)
    # Row 5: PROJECT / name / PROJECT # / #
    cell_text(t.rows[5].cells[0], "PROJECT:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[5].cells[1], "[Project Name]", size=10)
    cell_text(t.rows[5].cells[2], "PROJECT #", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[5].cells[3], "[Project #]", size=10)
    set_col_widths(t, [0.9, 3.0, 1.0, 2.2])
    doc.add_paragraph()

    # TRANSMITTED / ITEM grid (4 rows, 5 cols: label, mark, item, mark, item)
    t = doc.add_table(rows=4, cols=5)
    add_table_borders(t)
    # Row 0
    cell_text(t.rows[0].cells[0], "TRANSMITTED:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "x", bold=True, size=10,
              align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_text(t.rows[0].cells[2], "HEREWITH", size=10)
    cell_text(t.rows[0].cells[3], "", size=10)
    cell_text(t.rows[0].cells[4], "SEPARATELY", size=10)
    # Row 1
    cell_text(t.rows[1].cells[0], "ITEM:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[1].cells[1], "", size=10)
    cell_text(t.rows[1].cells[2], "ORIGINAL DRAWINGS", size=10)
    cell_text(t.rows[1].cells[3], "", size=10)
    cell_text(t.rows[1].cells[4], "COPY OF LETTER", size=10)
    # Row 2
    cell_text(t.rows[2].cells[0], "", size=10)
    cell_text(t.rows[2].cells[1], "", size=10)
    cell_text(t.rows[2].cells[2], "PRINTS", size=10)
    cell_text(t.rows[2].cells[3], "", size=10)
    cell_text(t.rows[2].cells[4], "SPECIFICATIONS", size=10)
    # Row 3 (SUBMITTALS x, SAMPLES)
    cell_text(t.rows[3].cells[0], "", size=10)
    cell_text(t.rows[3].cells[1], "x", bold=True, size=10,
              align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_text(t.rows[3].cells[2], "SUBMITTALS", size=10)
    cell_text(t.rows[3].cells[3], "", size=10)
    cell_text(t.rows[3].cells[4], "SAMPLES", size=10)
    set_col_widths(t, [1.2, 0.4, 2.1, 0.4, 3.0])
    doc.add_paragraph()

    # QUANTITY / DATED / DESCRIPTION table (4 rows, 3 cols)
    t = doc.add_table(rows=5, cols=3)
    add_table_borders(t)
    cell_text(t.rows[0].cells[0], "QUANTITY", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "DATED", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[2], "DESCRIPTION", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[1].cells[0], "[#]", size=10)
    cell_text(t.rows[1].cells[1], "[YYYY-MM-DD]", size=10)
    cell_text(t.rows[1].cells[2], "[Description of the transmitted item / submittal package]", size=10)
    for r in (2, 3, 4):
        for c in range(3):
            cell_text(t.rows[r].cells[c], "", size=10)
    set_col_widths(t, [1.0, 1.2, 4.9])
    doc.add_paragraph()

    # REMARKS (single-row 2-col)
    t = doc.add_table(rows=1, cols=2)
    add_table_borders(t)
    cell_text(t.rows[0].cells[0], "REMARKS:", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1],
              "[One paragraph summarizing what is enclosed, the spec section "
              "it satisfies, and any context the reviewer needs (revision "
              "number, scope coverage, related RFIs, requested action).]",
              size=10)
    set_col_widths(t, [1.2, 5.9])
    doc.add_paragraph()

    # By signature line
    add_para(doc, "By:   [Name, Title]", bold=True, size=10)


# -----------------------------------------------------------------------------
# COVER SHEET section
# -----------------------------------------------------------------------------

def section_cover_sheet(doc):
    banner(doc, "SUBMITTAL COVER SHEET",
           "Division [## ## ##]  -  [Division Name]")
    doc.add_paragraph()

    section_header(doc, "Project")
    kv_underline(doc, [
        ["Project Name:", "[Project Name]"],
        ["Project / CSP Number:", "[Contract # / CSP #]"],
        ["A&E Project No.:", "[Architect/Engineer Project #]"],
        ["Location:", "[Site Address]"],
        ["Date:", "[YYYY-MM-DD]"],
        ["Submittal No.:", "[Spec section - sequential, e.g. 26 00 00-01]"],
        ["Submittal Type:", "[Product Data / Shop Drawings / Samples / Engineering / Mock-up / Other]"],
    ])
    doc.add_paragraph()

    section_header(doc, "Engineer")
    kv_underline(doc, [
        ["Firm:", "[A/E Firm]"],
        ["Attention:", "[Reviewer Name]"],
        ["Address:", "[Street, City, State ZIP]"],
    ])
    doc.add_paragraph()

    section_header(doc, "Prime Contractor / HVAC Contractor")
    kv_underline(doc, [
        ["Firm:", "[Prime Contractor]"],
        ["Contact:", "[Name, Title]"],
        ["Address:", "[Street, City, State ZIP]"],
        ["Phone:", "[Phone]"],
    ])
    doc.add_paragraph()

    section_header(doc, "Subcontractor / Equipment Supplier")
    kv_underline(doc, [
        ["Firm:", "[Sub or Supplier]"],
        ["Contact:", "[Name]"],
        ["Email:", "[Email]"],
        ["PO Number:", "[PO #]"],
    ])
    doc.add_paragraph()

    section_header(doc, "Contractor Action")
    p = doc.add_paragraph()
    set_run(p.add_run("APPROVED          APPROVED AS NOTED          REJECTED"),
            bold=True, size=11)
    doc.add_paragraph()
    add_para(doc,
             "Contractor has reviewed submittal data against specifications. "
             "Forwarded to Engineer for review and comment.",
             size=10)
    doc.add_paragraph()
    kv_underline(doc, [
        ["Contractor Signature:", "[Name, Title]"],
        ["Date:", "[YYYY-MM-DD]"],
    ])


# -----------------------------------------------------------------------------
# INDEX section
# -----------------------------------------------------------------------------

def section_index(doc):
    banner(doc, "SUBMITTAL INDEX",
           "Division [## ## ##]  -  [Division Name]")
    doc.add_paragraph()

    section_header(doc, "Items Submitted")
    t = doc.add_table(rows=4, cols=3)
    add_table_borders(t)
    cell_text(t.rows[0].cells[0], "Item", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "Description", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[2], "Spec Section", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[1].cells[0], "1", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_text(t.rows[1].cells[1],
              "[Product / shop drawing / sample description - manufacturer, "
              "model, rating, application, quantity]", size=10)
    cell_text(t.rows[1].cells[2], "[## ## ##]", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    for r in (2, 3):
        for c in range(3):
            cell_text(t.rows[r].cells[c], "", size=10)
    set_col_widths(t, [0.7, 5.4, 1.0])
    doc.add_paragraph()

    section_header(doc, "Known Deviations from Contract Documents")
    add_para(doc,
             "Per Section [23 00 90 / 01 33 00], the following deviations are "
             "noted where submittals differ from the contract documents. All "
             "items are flagged with revision clouds and callout notes in the "
             "attached markup for the Engineer's review and comment.",
             size=10)
    doc.add_paragraph()
    t = doc.add_table(rows=4, cols=4)
    add_table_borders(t)
    cell_text(t.rows[0].cells[0], "No.", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[1], "Deviation", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[2], "Spec Ref.", bold=True, size=10, fill=LABEL_BLUE)
    cell_text(t.rows[0].cells[3], "Severity", bold=True, size=10, fill=LABEL_BLUE)
    for r in (1, 2, 3):
        for c in range(4):
            cell_text(t.rows[r].cells[c], "", size=10)
    set_col_widths(t, [0.5, 4.6, 1.0, 1.0])


# -----------------------------------------------------------------------------
# Document builders
# -----------------------------------------------------------------------------

def page_setup(doc):
    s = doc.sections[0]
    s.left_margin = Inches(0.7)
    s.right_margin = Inches(0.7)
    s.top_margin = Inches(0.6)
    s.bottom_margin = Inches(0.6)


def build_transmittal():
    doc = Document()
    page_setup(doc)
    letterhead(doc)
    doc.add_paragraph()
    section_transmittal(doc)
    out = os.path.join(OUT, "01_Transmittal.docx")
    doc.save(out)
    return out


def build_cover_sheet():
    doc = Document()
    page_setup(doc)
    letterhead(doc)
    doc.add_paragraph()
    section_cover_sheet(doc)
    out = os.path.join(OUT, "02_Submittal_Cover_Sheet.docx")
    doc.save(out)
    return out


def build_index():
    doc = Document()
    page_setup(doc)
    letterhead(doc)
    doc.add_paragraph()
    section_index(doc)
    out = os.path.join(OUT, "03_Submittal_Index.docx")
    doc.save(out)
    return out


def build_combined():
    doc = Document()
    page_setup(doc)
    letterhead(doc)
    doc.add_paragraph()
    section_transmittal(doc)
    doc.add_page_break()
    section_cover_sheet(doc)
    doc.add_page_break()
    section_index(doc)
    out = os.path.join(OUT, "04_Submittal_Package_Combined.docx")
    doc.save(out)
    return out


def main():
    for fn in [build_transmittal, build_cover_sheet, build_index, build_combined]:
        print(f"wrote {os.path.basename(fn())}")


if __name__ == '__main__':
    main()
