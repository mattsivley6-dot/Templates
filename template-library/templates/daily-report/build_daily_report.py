#!/usr/bin/env python3
"""Daily Report (field construction report PDF).

Builds one 1-to-2 page letterhead PDF per entry in the data file. All job
and per-day content comes from the JSON data file. All letterhead content
(company name, address, phone, website, license, logo, accent color) comes
from the company config file.

Usage:
    python build_daily_report.py [data.json] [--company company.json]

data.json defaults to sample_data.json beside this script.
--company defaults to template-library/company.example.json (two folders
up from this script).

Deterministic: no clock or randomness is used. Canvas is created with
invariant=1 so identical data gives byte-identical PDFs.
"""
import argparse
import io
import json
import os
import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image, ImageOps

# ---- style constants --------------------------------------------------------
DEFAULT_ACCENT = "#2E7D32"           # used when the company config has none
GRAY = colors.HexColor("#595959")    # secondary text
LGRAY = colors.HexColor("#BFBFBF")   # hairlines, photo borders
INK = colors.HexColor("#1A1A1A")     # body text
PALE = colors.HexColor("#F2F5EF")    # info grid fill

PW, PH = letter                      # 612 x 792 pt, portrait
LEFT = 0.75 * inch
RIGHT = PW - 0.75 * inch
W = RIGHT - LEFT

# Set from the company config in main() before any page is drawn.
ACCENT = colors.HexColor(DEFAULT_ACCENT)   # wordmark, rules, accents
LETTERHEAD = {"wordmark": "", "tagline": "", "addr": [], "foot": "",
              "logo": None}


def load_company(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_company(company, company_path):
    """Map company config fields onto the letterhead."""
    global ACCENT
    brand = company.get("brand") or {}
    ACCENT = colors.HexColor(brand.get("accent_color") or DEFAULT_ACCENT)
    dba = company.get("dba") or company.get("legal_name", "")
    lic = company.get("license")
    LETTERHEAD["wordmark"] = (company.get("wordmark") or dba).upper()
    LETTERHEAD["tagline"] = (company.get("tagline")
                             or ("LICENSE " + lic if lic else "")).upper()
    LETTERHEAD["addr"] = [v for v in (company.get("address_line1"),
                                      company.get("city_state_zip"),
                                      company.get("phone"),
                                      company.get("website")) if v]
    street = ", ".join(v for v in (company.get("address_line1"),
                                   company.get("city_state_zip")) if v)
    LETTERHEAD["foot"] = "    |    ".join(
        v for v in (company.get("legal_name"), street, company.get("phone"),
                    company.get("website")) if v)
    logo = company.get("logo_path")
    if logo:
        if not os.path.isabs(logo):
            logo = os.path.join(os.path.dirname(os.path.abspath(company_path)),
                                logo)
        LETTERHEAD["logo"] = logo if os.path.exists(logo) else None
    else:
        LETTERHEAD["logo"] = None


def masthead(c, page, report_no, datestr):
    """Letterhead masthead plus footer, drawn on every page."""
    c.saveState()
    if LETTERHEAD["logo"]:
        # logo replaces the text wordmark, fitted in a 160 x 36 pt box
        im = ImageReader(LETTERHEAD["logo"])
        iw, ih = im.getSize()
        s = min(160.0 / iw, 36.0 / ih)
        c.drawImage(im, LEFT, PH - 80, iw * s, ih * s, mask="auto")
    else:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(LEFT, PH - 62, LETTERHEAD["wordmark"])
        if LETTERHEAD["tagline"]:
            c.saveState()
            t = c.beginText(LEFT + 1, PH - 73)
            t.setFont("Helvetica", 7)
            t.setFillColor(GRAY)
            t.setCharSpace(3.2)
            t.textLine(LETTERHEAD["tagline"])
            c.drawText(t)
            c.restoreState()
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.6)
    for i, ln in enumerate(LETTERHEAD["addr"]):
        c.drawRightString(RIGHT, PH - 52 - i * 9, ln)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    c.line(LEFT, PH - 88, RIGHT, PH - 88)
    # footer
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.5)
    c.line(LEFT, 46, RIGHT, 46)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 6.8)
    c.drawCentredString(PW / 2, 36, LETTERHEAD["foot"])
    c.setFont("Helvetica", 7.2)
    c.drawRightString(RIGHT, 55, "Daily Report %s    |    %s    |    Page %d"
                      % (report_no, datestr, page))
    c.restoreState()


def resolve_photo(entry, photo_dir):
    """Resolve a photo entry to a real file path.

    Accepts an absolute path, a filename inside photo_dir, or (fallback) a
    filename whose stem matches a file in photo_dir with a different extension
    or case (picks lists often say .jpg while the camera file is .JPG). When
    several extensions share a stem the last one in sorted order wins.
    """
    f = entry["file"]
    if os.path.isabs(f):
        if os.path.exists(f):
            return f
        raise SystemExit("photo not found: " + f)
    p = os.path.join(photo_dir, f)
    if os.path.exists(p):
        return p
    stem = f.rsplit(".", 1)[0]
    hit = None
    for g in sorted(os.listdir(photo_dir)):
        if g.rsplit(".", 1)[0] == stem:
            hit = os.path.join(photo_dir, g)
    if hit:
        return hit
    raise SystemExit("photo not found: %s (searched %s)" % (f, photo_dir))


def crop_draw(c, path, x, y, w, h, rotate=0):
    """Center-crop image to the target box aspect and draw with a hairline border."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if rotate:
        # manual rotation for video stills with no EXIF orientation
        # (degrees, PIL counterclockwise convention, e.g. -90)
        im = im.rotate(rotate, expand=True)
    if im.mode != "RGB":
        im = im.convert("RGB")
    iw, ih = im.size
    target = w / h
    if iw / ih > target:
        nw = int(ih * target)
        im = im.crop(((iw - nw) // 2, 0, (iw + nw) // 2, ih))
    else:
        nh = int(iw / target)
        im = im.crop((0, (ih - nh) // 2, iw, (ih + nh) // 2))
    im.thumbnail((1400, 1400))
    bio = io.BytesIO()
    im.save(bio, "JPEG", quality=80)
    bio.seek(0)
    c.drawImage(ImageReader(bio), x, y, w, h)
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h)


def wrap(c, text, font, size, maxw):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if c.stringWidth(trial, font, size) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def section(c, y, title, items, bullet=True):
    """Draw an accent section header with trailing hairline plus items, return new y."""
    if not items:
        return y
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8.6)
    c.drawString(LEFT, y, title)
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.5)
    tw = c.stringWidth(title, "Helvetica-Bold", 8.6)
    c.line(LEFT + tw + 8, y + 2.6, RIGHT, y + 2.6)
    y -= 15
    c.setFillColor(INK)
    for it in items:
        pre = u"•  " if bullet else ""
        lines = wrap(c, it, "Helvetica", 10, W - 14)
        for j, ln in enumerate(lines):
            c.setFont("Helvetica", 10)
            if j == 0 and bullet:
                c.drawString(LEFT + 2, y, pre)
                c.drawString(LEFT + 14, y, ln)
            else:
                c.drawString(LEFT + 14, y, ln)
            y -= 13.2
        y -= 1.5
    return y - 9


def photos_header(c, yy):
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8.6)
    c.drawString(LEFT, yy, "PHOTOS")
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.5)
    tw = c.stringWidth("PHOTOS", "Helvetica-Bold", 8.6)
    c.line(LEFT + tw + 8, yy + 2.6, RIGHT, yy + 2.6)


def build_report(rep, proj, out_dir, author):
    datestr = rep["date"]
    report_no = int(rep["report_no"])
    dt = datetime.date.fromisoformat(datestr)
    dayname = dt.strftime("%A")
    nice = dt.strftime("%B %d, %Y").replace(" 0", " ")
    work = rep.get("work", [])
    no_work = rep.get("no_work",
                      bool(work) and work[0].startswith("No work"))

    fname = "%s Daily Report %02d - %s.pdf" % (datestr, report_no,
                                               proj["job_short"])
    path = os.path.join(out_dir, fname)
    c = canvas.Canvas(path, pagesize=letter, invariant=1)
    c.setTitle("Daily Construction Report %02d - %s"
               % (report_no, proj["pdf_title_project"]))
    c.setAuthor(author)
    c.setSubject("Daily Construction Report")
    c.setCreator(author)

    masthead(c, 1, "%02d" % report_no, dt.strftime("%m/%d/%Y"))

    # Title row
    y = PH - 112
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(LEFT, y, "DAILY CONSTRUCTION REPORT")
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(ACCENT)
    c.drawRightString(RIGHT, y, "No. %02d" % report_no)

    # Info grid
    y -= 14
    gh = 48
    c.setFillColor(PALE)
    c.rect(LEFT, y - gh, W, gh, stroke=0, fill=1)
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.6)
    c.rect(LEFT, y - gh, W, gh, stroke=1, fill=0)
    cols = [
        ("PROJECT", proj["project_line"]),
        ("OWNER", proj["owner"]),
        ("DATE", "%s, %s" % (dayname, nice)),
        ("WEATHER", rep.get("weather", "")),
    ]
    cw = [W * 0.34, W * 0.24, W * 0.22, W * 0.20]
    x = LEFT
    for i, (k, v) in enumerate(cols):
        c.setFillColor(GRAY)
        c.setFont("Helvetica-Bold", 6.6)
        c.drawString(x + 7, y - 13, k)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.6)
        for j, ln in enumerate(wrap(c, v, "Helvetica", 8.6, cw[i] - 12)[:3]):
            c.drawString(x + 7, y - 24 - j * 10, ln)
        x += cw[i]
        if i < 3:
            c.setStrokeColor(LGRAY)
            c.line(x, y - gh, x, y)
    y -= gh + 22

    # Sections
    y = section(c, y, "WORK PERFORMED", work)

    crews = rep.get("crews", [])
    if crews:
        parts = []
        for cr in crews:
            n = cr.get("count")
            parts.append("%s (%d)" % (cr["trade"], n) if n else cr["trade"])
        y = section(c, y, "CREWS ON SITE", ["  |  ".join(parts)], bullet=False)

    if rep.get("equipment"):
        y = section(c, y, "EQUIPMENT", rep["equipment"])
    if rep.get("deliveries"):
        y = section(c, y, "DELIVERIES", rep["deliveries"])
    safety = list(rep.get("safety", []))
    if not no_work:
        safety = ["No accidents or injuries."] + safety
    if safety:
        y = section(c, y, "SAFETY", safety)
    if rep.get("visitors"):
        y = section(c, y, "MEETINGS AND VISITORS", rep["visitors"])
    if rep.get("remarks"):
        y = section(c, y, "REMARKS", rep["remarks"])

    # signature line (bottom of page 1)
    def sig(cv):
        cv.setFillColor(GRAY)
        cv.setFont("Helvetica", 8.4)
        cv.drawString(LEFT, 66, "Prepared by " + proj["prepared_by"])

    # Photos (max 4, suppressed on no-work days)
    photo_dir = proj.get("photo_dir", "")
    photos = []
    if not no_work:
        for p in rep.get("photos", [])[:4]:
            photos.append((resolve_photo(p, photo_dir), p.get("rotate", 0)))

    GAP = 10
    if photos and not no_work:
        colw = (W - GAP) / 2
        tile_h = colw * 0.72
        need = tile_h if len(photos) <= 2 else tile_h * 2 + GAP
        if y - need >= 80 and len(photos) <= 2:
            # photos fit on page 1
            yy = y - 4
            photos_header(c, yy)
            yy -= 12
            avail = yy - 80
            th = min(tile_h, avail)
            if len(photos) == 1:
                crop_draw(c, photos[0][0], LEFT, yy - th, W, th,
                          photos[0][1])
            else:
                crop_draw(c, photos[0][0], LEFT, yy - th, colw, th,
                          photos[0][1])
                crop_draw(c, photos[1][0], LEFT + colw + GAP, yy - th,
                          colw, th, photos[1][1])
            sig(c)
        else:
            # photos go to page 2
            sig(c)
            c.showPage()
            masthead(c, 2, "%02d" % report_no, dt.strftime("%m/%d/%Y"))
            yy = PH - 116
            photos_header(c, yy)
            yy -= 14
            avail_h = yy - 70
            rows = 1 if len(photos) <= 2 else 2
            th = min(colw * 0.75, (avail_h - (rows - 1) * GAP) / rows)
            if len(photos) == 1:
                crop_draw(c, photos[0][0], LEFT, yy - th, W,
                          min(th * 1.6, avail_h), photos[0][1])
            else:
                for i, (ph, rot) in enumerate(photos):
                    r, col = divmod(i, 2)
                    px = LEFT + col * (colw + GAP)
                    py = yy - th - r * (th + GAP)
                    if len(photos) == 3 and i == 2:
                        crop_draw(c, ph, LEFT, py, W, th, rot)
                    else:
                        crop_draw(c, ph, px, py, colw, th, rot)
    else:
        sig(c)

    c.save()
    return path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_company = os.path.normpath(
        os.path.join(here, "..", "..", "company.example.json"))
    ap = argparse.ArgumentParser(description="Build daily report PDFs.")
    ap.add_argument("data", nargs="?",
                    default=os.path.join(here, "sample_data.json"),
                    help="report data JSON (default: sample_data.json)")
    ap.add_argument("--company", default=default_company,
                    help="company config JSON (default: %(default)s)")
    args = ap.parse_args()

    data_file = args.data
    data_dir = os.path.dirname(os.path.abspath(data_file))
    with open(data_file, encoding="utf8") as f:
        data = json.load(f)
    company = load_company(args.company)
    apply_company(company, args.company)
    author = company.get("legal_name") or company.get("dba", "")

    proj = dict(data["project"])
    if not proj.get("prepared_by"):
        proj["prepared_by"] = ", ".join(
            v for v in (company.get("pm_name"), company.get("pm_title")) if v)
    # relative photo_dir resolves against the data file's folder
    pdir = proj.get("photo_dir") or ""
    if pdir and not os.path.isabs(pdir):
        proj["photo_dir"] = os.path.join(data_dir, pdir)

    out_dir = data.get("output_dir", ".")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(data_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    for rep in data["reports"]:
        p = build_report(rep, proj, out_dir, author)
        print("wrote", os.path.basename(p))
    print("done,", len(data["reports"]), "reports")


if __name__ == "__main__":
    main()
