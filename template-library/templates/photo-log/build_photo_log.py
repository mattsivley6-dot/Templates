# -*- coding: utf-8 -*-
"""Photo Log / Photo Exhibit builder.

Two modes, selected by the "mode" key in the JSON data file:

  "daily"   - Daily Photo Log: letter portrait, 2 photos per page, colored
              section bars, numbered captions, optional trailing Video Index
              page.

  "exhibit" - Stored-material / pay-app photo exhibit: one photo per page
              with an EXIF capture time + GPS metadata line.

Usage:
    python build_photo_log.py [data.json] [--company company.json]

data.json defaults to sample_data.json in this script's folder.
--company defaults to ../../company.example.json (the template-library
company config, two folders up from this script). Company name, the PM
name fallback and the accent color come from that file; nothing about the
company is hard-coded here. All other variable content comes from the
data JSON; this script holds only fixed wording and layout.

Determinism: no datetime.now()/time.time()/random anywhere. PDF metadata
(creation and modification dates) is taken from the JSON "doc_date" key so
identical data gives stable output. Images are re-prepped (EXIF-oriented,
downscaled, recompressed) on every run with fixed Pillow settings.

Libraries: PyMuPDF (fitz) + Pillow only. No em dashes anywhere.
"""
import argparse
import json
import os

import fitz
from PIL import Image, ImageOps, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COMPANY = os.path.normpath(os.path.join(HERE, "..", "..", "company.example.json"))

# ---------------------------------------------------------------- constants
PAGE_W, PAGE_H = 612, 792          # US Letter portrait, points

ACCENT_FALLBACK = "#333333"        # used only if the company config has no primary_color
GRAY_DAILY = (0.45, 0.45, 0.45)    # borders + footer, daily mode
GRAY_EXHIBIT = (0.40, 0.40, 0.40)  # borders + footer, exhibit mode
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
ROW_SHADE = (0.93, 0.95, 0.98)     # video index alternating rows

M_DAILY = 40                       # page margin, daily mode
M_EXHIBIT = 54                     # page margin, exhibit mode

# Base-14 fonts: helv = Helvetica (renders as Arial-class sans),
# hebo = Helvetica-Bold.
F_REG = "helv"
F_BOLD = "hebo"

SLOT_TOPS = [60, 425]              # y of the two photo slots, daily mode
IMG_H_DAILY = 290                  # max photo height per slot, daily mode
IMG_TOP_EXHIBIT = 100              # photo top, exhibit mode
IMG_H_EXHIBIT = 560                # max photo height, exhibit mode

MAXPX_DAILY = 1500                 # Pillow downscale bound, daily mode
MAXPX_EXHIBIT = 1800               # Pillow downscale bound, exhibit mode
JPEG_QUALITY = 82

CREATOR = "Template Library photo-log"


# ------------------------------------------------------------------ helpers
def hex_to_rgb(h):
    h = str(h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def parse_args():
    ap = argparse.ArgumentParser(description="Build a daily photo log or photo exhibit PDF.")
    ap.add_argument("data", nargs="?", default=os.path.join(HERE, "sample_data.json"),
                    help="data JSON (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=DEFAULT_COMPANY,
                    help="company config JSON (default: template-library/company.example.json)")
    return ap.parse_args()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(image_root, fname):
    if os.path.isabs(fname):
        return fname
    return os.path.join(image_root, fname)


def prep_image(src, prep_dir, maxpx):
    """EXIF-orient, downscale, recompress to JPEG. Returns (path, w, h)."""
    base = os.path.splitext(os.path.basename(src))[0] + ".jpg"
    dst = os.path.join(prep_dir, base)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    im.thumbnail((maxpx, maxpx), Image.LANCZOS)
    im = im.convert("RGB")
    im.save(dst, "JPEG", quality=JPEG_QUALITY)
    with Image.open(dst) as im2:
        return dst, im2.width, im2.height


def fit_rect(iw, ih, x_left, y_top, avail_w, avail_h):
    scale = min(avail_w / iw, avail_h / ih)
    dw, dh = iw * scale, ih * scale
    x0 = x_left + (avail_w - dw) / 2
    return fitz.Rect(x0, y_top, x0 + dw, y_top + dh), dh


def shrink_to_fit(text, fontname, size, max_w, min_size=6.5):
    """Reduce font size in 0.5 pt steps until text fits max_w."""
    while size > min_size and fitz.get_text_length(text, fontname=fontname, fontsize=size) > max_w:
        size -= 0.5
    return size


def set_metadata(doc, data, company, title):
    d = str(data.get("doc_date", "2026-01-01")).replace("-", "")
    stamp = "D:%s000000-06'00'" % d
    doc.set_metadata({
        "title": title,
        "author": company.get("legal_name", ""),
        "creator": CREATOR,
        "producer": "PyMuPDF",
        "creationDate": stamp,
        "modDate": stamp,
    })


# --------------------------------------------------------------- daily mode
def build_daily(data, company, accent, out_path, prep_dir):
    m = M_DAILY
    gray = GRAY_DAILY
    image_root = data["_image_root"]
    maxpx = int(data.get("image_max_px", MAXPX_DAILY))
    sections = data["sections"]
    company_line = data.get("company_name") or str(company.get("legal_name", "")).upper()
    prepared_by = data.get("prepared_by") or company.get("pm_name", "")

    # prep all images, count photos vs video stills
    prepped = {}
    nphotos = 0
    nstills = 0
    for sec in sections:
        for ph in sec["photos"]:
            if ph.get("video_still"):
                nstills += 1
            else:
                nphotos += 1
            src = resolve(image_root, ph["file"])
            prepped[ph["file"]] = prep_image(src, prep_dir, maxpx)
    total = nphotos + nstills

    doc = fitz.open()

    def new_page():
        p = doc.new_page(width=PAGE_W, height=PAGE_H)
        p.insert_text((m, 30), company_line, fontsize=9, fontname=F_BOLD, color=accent)
        head = "%s  |  %s  |  %s" % (data["doc_type_label"], data["project_label"], data["client"])
        p.insert_text((m, 42), head, fontsize=8, fontname=F_REG, color=BLACK)
        rdate = data["date_label"]
        w = fitz.get_text_length(rdate, fontname=F_REG, fontsize=8)
        p.insert_text((PAGE_W - m - w, 42), rdate, fontsize=8, fontname=F_REG, color=BLACK)
        p.draw_line(fitz.Point(m, 48), fitz.Point(PAGE_W - m, 48), color=accent, width=1.2)
        return p

    if nstills > 0:
        counts = "%d exhibits (%d photos + %d video stills)" % (total, nphotos, nstills)
    else:
        counts = "%d exhibits (%d photos)" % (total, nphotos)

    def footer(p, num):
        txt = "Page %d  |  %s  |  Prepared by: %s  |  Captured %s" % (
            num, counts, prepared_by, data["captured_label"])
        w = fitz.get_text_length(txt, fontname=F_REG, fontsize=7)
        p.insert_text(((PAGE_W - w) / 2, PAGE_H - 22), txt, fontsize=7, fontname=F_REG, color=gray)

    counter = 0
    page = None
    slot = 0
    pageno = 0

    for sec in sections:
        pending = sec["title"]
        for ph in sec["photos"]:
            counter += 1
            if page is None or slot > 1:
                if page is not None:
                    footer(page, pageno)
                pageno += 1
                page = new_page()
                slot = 0
            top = SLOT_TOPS[slot]
            y = top
            if pending is not None:
                page.draw_rect(fitz.Rect(m, y, PAGE_W - m, y + 14), color=accent, fill=accent)
                fs = shrink_to_fit(pending, F_BOLD, 8, PAGE_W - 2 * m - 12)
                page.insert_text((m + 6, y + 10.5), pending, fontsize=fs, fontname=F_BOLD, color=WHITE)
                pending = None
                y += 20
            path, iw, ih = prepped[ph["file"]]
            avail_h = IMG_H_DAILY - (y - top)
            rect, dh = fit_rect(iw, ih, m, y, PAGE_W - 2 * m, avail_h)
            page.insert_image(rect, filename=path)
            page.draw_rect(rect, color=gray, width=0.5)
            cy = y + dh + 12
            disp = ph.get("display") or os.path.splitext(os.path.basename(ph["file"]))[0]
            if ph.get("video_still"):
                disp += " (video still)"
            label = "Photo %02d  |  %s" % (counter, disp)
            if ph.get("captured"):
                label += "  |  %s" % ph["captured"]
            page.insert_text((m, cy), label, fontsize=7.5, fontname=F_BOLD, color=accent)
            page.insert_textbox(fitz.Rect(m, cy + 4, PAGE_W - m, cy + 56), ph["caption"],
                                fontsize=8, fontname=F_REG, color=BLACK, lineheight=1.15)
            slot += 1

    footer(page, pageno)

    # ---------------- optional VIDEO INDEX page ----------------
    vi = data.get("video_index")
    if vi:
        vp = doc.new_page(width=PAGE_W, height=PAGE_H)
        vp.insert_text((m, 30), company_line, fontsize=9, fontname=F_BOLD, color=accent)
        head = "VIDEO INDEX  |  %s  |  %s" % (data["project_label"], data["client"])
        vp.insert_text((m, 42), head, fontsize=8, fontname=F_REG, color=BLACK)
        vp.draw_line(fitz.Point(m, 48), fitz.Point(PAGE_W - m, 48), color=accent, width=1.2)
        vp.insert_text((m, 66), vi["intro_line"], fontsize=8.5, fontname=F_REG, color=BLACK)
        vp.insert_textbox(fitz.Rect(m, 78, PAGE_W - m, 108), vi["note"],
                          fontsize=8, fontname=F_REG, color=GRAY_DAILY, lineheight=1.2)
        y = 120
        vp.draw_rect(fitz.Rect(m, y, PAGE_W - m, y + 16), color=accent, fill=accent)
        vp.insert_text((m + 6, y + 11), "FILE", fontsize=8, fontname=F_BOLD, color=WHITE)
        vp.insert_text((m + 130, y + 11), "TIME", fontsize=8, fontname=F_BOLD, color=WHITE)
        vp.insert_text((m + 200, y + 11), "ACTIVITY (INDEXED BY TIME)", fontsize=8, fontname=F_BOLD, color=WHITE)
        y += 16
        for i, v in enumerate(vi["videos"]):
            if i % 2 == 1:
                vp.draw_rect(fitz.Rect(m, y, PAGE_W - m, y + 17), color=ROW_SHADE, fill=ROW_SHADE)
            vp.insert_text((m + 6, y + 12), v["file"], fontsize=8, fontname=F_REG, color=BLACK)
            vp.insert_text((m + 130, y + 12), v["time"], fontsize=8, fontname=F_REG, color=BLACK)
            vp.insert_textbox(fitz.Rect(m + 200, y + 3, PAGE_W - m - 4, y + 17), v["activity"],
                              fontsize=8, fontname=F_REG, color=BLACK)
            y += 17
        vp.draw_rect(fitz.Rect(m, 120, PAGE_W - m, y), color=gray, width=0.5)
        ftv = "Video Index  |  %d clips  |  Prepared by: %s  |  Captured %s" % (
            len(vi["videos"]), prepared_by, data["captured_label"])
        w = fitz.get_text_length(ftv, fontname=F_REG, fontsize=7)
        vp.insert_text(((PAGE_W - w) / 2, PAGE_H - 22), ftv, fontsize=7, fontname=F_REG, color=gray)

    set_metadata(doc, data, company, "%s - %s" % (data["doc_type_label"], data["project_label"]))
    doc.save(out_path, deflate=True, garbage=3, no_new_id=True)
    n = doc.page_count
    doc.close()
    return n, counter


# ------------------------------------------------------------- exhibit mode
def build_exhibit(data, company, out_path, prep_dir):
    m = M_EXHIBIT
    gray = GRAY_EXHIBIT
    image_root = data["_image_root"]
    maxpx = int(data.get("image_max_px", MAXPX_EXHIBIT))
    note = "\n".join(data["metadata_note"])
    footer = None
    if data.get("footer"):
        footer = "%s   |   %s" % (company.get("legal_name", ""), data["footer"])

    doc = fitz.open()
    counter = 0
    for ph in data["photos"]:
        counter += 1
        src = resolve(image_root, ph["file"])
        path, iw, ih = prep_image(src, prep_dir, maxpx)
        p = doc.new_page(width=PAGE_W, height=PAGE_H)
        p.insert_text((m, 54), data["title"], fontsize=12, fontname=F_BOLD, color=BLACK)
        sy = 70
        for line in data["subtitle_lines"]:
            p.insert_text((m, sy), line, fontsize=9.5, fontname=F_REG, color=BLACK)
            sy += 14
        rect, dh = fit_rect(iw, ih, m, IMG_TOP_EXHIBIT, PAGE_W - 2 * m, IMG_H_EXHIBIT)
        p.insert_image(rect, filename=path)
        p.draw_rect(rect, color=gray, width=0.6)
        cy = IMG_TOP_EXHIBIT + dh + 16
        disp = ph.get("display") or os.path.basename(ph["file"])
        line1 = "File: %s   |   Captured: %s" % (disp, ph["captured"])
        if ph.get("gps"):
            line1 += "   |   GPS: %s" % ph["gps"]
        p.insert_text((m, cy), line1, fontsize=9, fontname=F_BOLD, color=BLACK)
        p.insert_textbox(fitz.Rect(m, cy + 8, PAGE_W - m, cy + 70),
                         note + "\n" + ph["caption"],
                         fontsize=8.5, fontname=F_REG, color=BLACK, lineheight=1.25)
        if footer:
            p.insert_text((m, PAGE_H - 30), footer, fontsize=7.5, fontname=F_REG, color=gray)

    set_metadata(doc, data, company, data["title"])
    doc.save(out_path, deflate=True, garbage=3, no_new_id=True)
    n = doc.page_count
    doc.close()
    return n, counter


# --------------------------------------------------------------------- main
def main():
    args = parse_args()
    data = load_json(args.data)
    company = load_json(args.company)
    accent = hex_to_rgb((company.get("brand") or {}).get("primary_color") or ACCENT_FALLBACK)

    # a relative image_root resolves against the data file's folder
    json_dir = os.path.dirname(os.path.abspath(args.data))
    image_root = data.get("image_root", "")
    if not os.path.isabs(image_root):
        image_root = os.path.join(json_dir, image_root)
    data["_image_root"] = image_root

    out_dir = data.get("output_dir") or os.path.join(HERE, "_sample_output")
    os.makedirs(out_dir, exist_ok=True)
    prep_dir = os.path.join(out_dir, "_prepped")
    os.makedirs(prep_dir, exist_ok=True)
    out_path = os.path.join(out_dir, data["output_filename"])

    mode = data.get("mode", "daily")
    if mode == "daily":
        pages, items = build_daily(data, company, accent, out_path, prep_dir)
    elif mode == "exhibit":
        pages, items = build_exhibit(data, company, out_path, prep_dir)
    else:
        raise SystemExit("mode must be 'daily' or 'exhibit', got %r" % mode)
    print("saved", out_path, "pages:", pages, "exhibits:", items)


if __name__ == "__main__":
    main()
