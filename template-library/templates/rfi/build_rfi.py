# build_rfi.py - RFI (Request for Information) generator.
# All variable content comes from a JSON data file; company header and PDF
# author come from the company config file. This script holds only fixed
# wording and layout.
#
# Usage:  python build_rfi.py [data.json] [--company company.json]
#         data.json defaults to sample_data.json next to this script.
#         --company defaults to template-library/company.example.json
#         (two folders up from this script).
#
# Determinism: no datetime/random calls; every date comes from the JSON. The PDF canvas is
# built with invariant=1 so identical data produces a byte-identical PDF.
#
# Requires: reportlab, Pillow. Verification uses PyMuPDF (fitz) if available.

import argparse
import json
import os
import shutil
from xml.sax.saxutils import escape

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as _canvas
from reportlab.platypus import (HRFlowable, Image as RLImage, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

# ---------------- fixed style constants (do not change between jobs) ----------------
DOC_TITLE = "Request for Information"
SECTION_BACKGROUND = "BACKGROUND"
SECTION_QUESTION = "QUESTION"
SECTION_RESOLUTION = "PROPOSED RESOLUTION"
INFO_LABELS = ["Project", "Owner", "Date", "Response requested by", "To", "From",
               "Subject", "References"]

MARGIN = 58  # points, ~0.81 inch, all four sides
USABLE = letter[0] - 2 * MARGIN
LABEL_COL_W = 1.7 * inch
GRID_LINE = colors.HexColor("#999999")
LABEL_FILL = colors.HexColor("#f3f3f3")
INLINE_CAP_GRAY = colors.HexColor("#555555")

styles = getSampleStyleSheet()
H_COMPANY = ParagraphStyle("company", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=13, leading=15, spaceAfter=2)
H_TITLE = ParagraphStyle("title", parent=styles["Normal"], fontName="Helvetica-Bold",
                         fontSize=17, leading=20)
H_RFI = ParagraphStyle("rfinum", parent=H_TITLE, alignment=TA_RIGHT)
LBL = ParagraphStyle("lbl", parent=styles["Normal"], fontName="Helvetica-Bold",
                     fontSize=10, leading=13)
VAL = ParagraphStyle("val", parent=styles["Normal"], fontName="Helvetica",
                     fontSize=10, leading=13)
SECT = ParagraphStyle("sect", parent=styles["Normal"], fontName="Helvetica-Bold",
                      fontSize=11, leading=13, spaceBefore=9, spaceAfter=3)
BODY = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=10, leading=12.6, spaceAfter=5)
PHEAD = ParagraphStyle("phead", parent=SECT, spaceBefore=0, spaceAfter=8)
INLINE_CAP = ParagraphStyle("inlinecap", parent=styles["Normal"], fontName="Helvetica-Oblique",
                            fontSize=9, leading=12, alignment=TA_CENTER,
                            textColor=INLINE_CAP_GRAY)


class InvariantCanvas(_canvas.Canvas):
    """Canvas with invariant=1 so identical input gives a byte-identical PDF."""
    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        _canvas.Canvas.__init__(self, *args, **kwargs)


def esc(text):
    """JSON text is plain text; escape XML specials for reportlab Paragraph."""
    return escape(str(text))


def load_company(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def grid_caption_style(font_size):
    return ParagraphStyle("cap%s" % font_size, parent=styles["Normal"],
                          fontName="Helvetica-Bold", fontSize=font_size,
                          leading=font_size + 3, alignment=TA_CENTER,
                          textColor=colors.black)


def prep_image(src, tmp_dir):
    """Normalize a field photo: honor EXIF orientation, cap at 1500 px,
    recompress JPEG quality 88."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im.thumbnail((1500, 1500))
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = os.path.join(tmp_dir, "grid_" + base + ".jpg")
    im.save(tmp, quality=88)
    return tmp, im.size


def make_photo_cell(src, caption, cell_w, max_img_h, cap_style, tmp_dir):
    tmp, (w, h) = prep_image(src, tmp_dir)
    max_img_w = cell_w - 14
    disp_h = max_img_h
    disp_w = disp_h * w / h
    if disp_w > max_img_w:
        disp_w = max_img_w
        disp_h = disp_w * h / w
    img = RLImage(tmp, width=disp_w, height=disp_h, hAlign="CENTER")
    inner = Table([[img], [Paragraph("<b>%s</b>" % esc(caption), cap_style)]],
                  colWidths=[cell_w - 8])
    inner.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
    ]))
    return inner


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(script_dir, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build an RFI PDF.")
    ap.add_argument("data", nargs="?",
                    default=os.path.join(script_dir, "sample_data.json"),
                    help="RFI data JSON (default: sample_data.json)")
    ap.add_argument("--company", default=default_company,
                    help="company config JSON (default: %(default)s)")
    args = ap.parse_args()

    data_path = os.path.abspath(args.data)
    data_dir = os.path.dirname(data_path)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    company = load_company(args.company)
    company_name = (company.get("legal_name") or "").upper()
    author = company.get("legal_name") or ""

    # "from" defaults to the PM and company in the company config
    if not data.get("from"):
        data["from"] = ", ".join(v for v in (company.get("pm_name"),
                                             company.get("legal_name")) if v)

    required = ["rfi_number", "output_filename", "project", "owner", "date", "to", "from",
                "subject", "references", "background", "question", "proposed_resolution"]
    missing = [k for k in required if k not in data or data[k] in (None, "", [])]
    if missing:
        raise SystemExit("data file is missing required keys: %s" % ", ".join(missing))

    out_dir = data.get("output_dir") or os.path.join(script_dir, "_sample_output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(data_dir, out_dir)
    tmp_dir = os.path.join(out_dir, "_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    out_path = os.path.join(out_dir, data["output_filename"])

    # ---------------- info table ----------------
    rows = [
        ("Project", data["project"]),
        ("Owner", data["owner"]),
        ("Date", data["date"]),
    ]
    if data.get("response_requested_by"):
        rows.append(("Response requested by", data["response_requested_by"]))
    rows += [
        ("To", data["to"]),
        ("From", data["from"]),
        ("Subject", data["subject"]),
        ("References", data["references"]),
    ]
    tbl_data = [[Paragraph(esc(l), LBL), Paragraph(esc(v), VAL)] for l, v in rows]
    info = Table(tbl_data, colWidths=[LABEL_COL_W, USABLE - LABEL_COL_W])
    info.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GRID_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (0, -1), LABEL_FILL),
    ]))

    # ---------------- page 1 story ----------------
    story = []
    story.append(Paragraph(esc(company_name), H_COMPANY))
    story.append(HRFlowable(width="100%", thickness=1.1, color=colors.black,
                            spaceBefore=2, spaceAfter=8))
    ttl = Table([[Paragraph(DOC_TITLE, H_TITLE), Paragraph(esc(data["rfi_number"]), H_RFI)]],
                colWidths=[USABLE * 0.6, USABLE * 0.4])
    ttl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                             ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    story.append(ttl)
    story.append(Spacer(1, 7))
    story.append(info)
    story.append(Spacer(1, 2))

    for heading, key in ((SECTION_BACKGROUND, "background"),
                         (SECTION_QUESTION, "question"),
                         (SECTION_RESOLUTION, "proposed_resolution")):
        story.append(Paragraph(heading, SECT))
        for t in data[key]:
            story.append(Paragraph(esc(t), BODY))

    # ---------------- optional inline photo (single-photo variant) ----------------
    inline = data.get("inline_photo")
    if inline:
        src = inline["file"]
        if not os.path.isabs(src):
            src = os.path.join(data_dir, src)
        tmp, (pw, ph) = prep_image(src, tmp_dir)
        disp_w = float(inline.get("width_in", 3.4)) * inch
        disp_h = disp_w * ph / pw
        maxh = 8.0 * inch
        if disp_h > maxh:
            disp_h = maxh
            disp_w = disp_h * pw / ph
        story.append(Spacer(1, 18))
        story.append(RLImage(tmp, width=disp_w, height=disp_h, hAlign="CENTER"))
        story.append(Spacer(1, 8))
        story.append(Paragraph(esc(inline.get("caption", "")), INLINE_CAP))

    # ---------------- optional photo exhibit page (grid variant) ----------------
    page = data.get("photo_page")
    if page and page.get("photos"):
        photos = page["photos"]
        cell_w = USABLE / 2.0
        default_h = 3.9 if len(photos) <= 2 else 3.35
        max_img_h = float(page.get("max_image_height_in", default_h)) * inch
        cap_style = grid_caption_style(float(page.get("caption_font_size", 11)))
        cells = []
        for p in photos:
            src = p["file"]
            if not os.path.isabs(src):
                src = os.path.join(data_dir, src)
            cells.append(make_photo_cell(src, p.get("caption", ""), cell_w,
                                         max_img_h, cap_style, tmp_dir))
        grid_rows = []
        for i in range(0, len(cells), 2):
            row = cells[i:i + 2]
            if len(row) == 1:
                row.append("")
            grid_rows.append(row)
        grid = Table(grid_rows, colWidths=[cell_w, cell_w])
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(PageBreak())
        story.append(Paragraph(esc(page.get("heading", "FIELD PHOTOGRAPHS")), PHEAD))
        story.append(grid)

    # ---------------- build ----------------
    doc = SimpleDocTemplate(out_path, pagesize=letter,
                            topMargin=MARGIN, bottomMargin=MARGIN,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            title=data.get("pdf_title", data["rfi_number"]),
                            author=author)
    doc.build(story, canvasmaker=InvariantCanvas)
    # recompressed photo copies are only needed during the build
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("SAVED", out_path)

    # verification: page count > 0
    try:
        import fitz
        d = fitz.open(out_path)
        print("pages:", len(d))
        d.close()
    except ImportError:
        pass


if __name__ == "__main__":
    main()
