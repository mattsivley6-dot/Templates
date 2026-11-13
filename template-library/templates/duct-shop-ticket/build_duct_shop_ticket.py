#!/usr/bin/env python3
# build_duct_shop_ticket.py
# Duct Transition Shop Ticket builder.
# Usage: py -3 build_duct_shop_ticket.py [data.json] [--company company.json]
#
# Style: schedule page + one parametric isometric per fitting, on a small
# landscape page. Use this for duct shop tickets instead of a large
# title-block drawing sheet.
#
# Fully self-contained: stdlib + reportlab only. All variable content comes
# from the JSON data file; company fields come from the company config
# (default: template-library/company.example.json, two folders up).
# Any data string may hold {{company.KEY}} tokens, e.g. {{company.dba}}.
# Deterministic: Canvas(invariant=1), no clock calls.
#
# Geometry is COMPUTED from each fitting's dimensions: classic isometric,
# width axis 30 deg down-right, depth axis 30 deg down-left with 0.925
# foreshortening, height straight down, auto-scaled so the assembly fills
# the drawing region on every page.

import argparse
import json
import math
import os
import re

from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor

# ---------------------------------------------------------------- page/style
PAGE_W, PAGE_H = 510.0, 358.5          # page size (pt), landscape
MARGIN = 36.0

INK_DARK = HexColor("#2B2A27")         # bold labels, titles
INK_BODY = HexColor("#444441")         # schedule body text
INK_GREY = HexColor("#5F5E5A")         # callout values, footers, spec lines
RULE = HexColor("#D9D7CD")             # horizontal rules, spec box border
LEADER = Color(0.612, 0.604, 0.573)    # dashed leader lines
OUTLINE = Color(0.431, 0.427, 0.408)   # iso shape outlines

F_RING = Color(0.940, 0.930, 0.900)    # flange outer ring
F_PLATE = Color(0.810, 0.780, 0.710)   # flange plate band (tan)
F_TOP = Color(0.753, 0.745, 0.706)     # top opening / flex top face
F_FRONT = Color(0.839, 0.831, 0.792)   # front (width) faces
F_SIDE = Color(0.663, 0.655, 0.616)    # right (depth) faces
F_BOTTOM = Color(0.612, 0.604, 0.573)  # exposed bottom rims
BOX_FILL = Color(0.960, 0.950, 0.930)  # spec box background

FONT = "Helvetica"
FONT_B = "Helvetica-Bold"

# Isometric axes (per inch, before auto-scale):
# width 30 deg down-right, depth 30 deg down-left at 0.925 foreshortening.
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
UX, UY = C30, S30                      # width axis
VX, VY = -C30 * 0.925, S30 * 0.925     # depth axis
HZ = 0.90                              # height pt-per-inch relative factor

# Drawing region on fitting pages (callouts live to the right of it).
DRAW_X0, DRAW_X1 = 80.0, 345.0
DRAW_Y0, DRAW_Y1 = 52.0, 262.0         # top-down page coords (y from top)
CALL_LINE_X = 388.0                    # leaders end here
CALL_TEXT_X = 390.0                    # labels start here
FLANGE_IN = 1.4                        # flange margin, inches
GAP_PT = 18.0                          # exploded gap between pieces, pt


def yy(y_top):
    """Convert top-down layout coordinates to reportlab bottom-up."""
    return PAGE_H - y_top


# ---------------------------------------------------------------- iso engine
class Iso:
    """Projects (x=width in, y=depth in, z=inches BELOW curb top) to page pts."""

    def __init__(self, scale, ox, oy):
        self.s = scale
        self.ox, self.oy = ox, oy      # page position of (0,0,0), top-down

    def pt(self, x, y, z):
        px = self.ox + self.s * (x * UX + y * VX)
        py = self.oy + self.s * (x * UY + y * VY) + self.s * HZ * z
        return px, py

    def poly(self, c, pts3, fill=None, stroke=OUTLINE, width=0.6, dash=None):
        p = c.beginPath()
        first = True
        for (x, y, z) in pts3:
            px, py = self.pt(x, y, z)
            if first:
                p.moveTo(px, yy(py))
                first = False
            else:
                p.lineTo(px, yy(py))
        p.close()
        c.saveState()
        if dash:
            c.setDash(*dash)
        if fill is not None:
            c.setFillColor(fill)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(width)
        c.drawPath(p, fill=1 if fill is not None else 0,
                   stroke=1 if stroke is not None else 0)
        c.restoreState()


def rect_at(w, d, cx, cy):
    """Corner list of a w x d rectangle centered at (cx, cy), CCW from back-left."""
    return [(cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2),
            (cx + w / 2, cy + d / 2), (cx - w / 2, cy + d / 2)]


def bottom_center(fit):
    """Bottom-rect center offset (inches) from the top-rect center, per taper mode."""
    tw, td = fit["top_w"], fit["top_d"]
    bw, bd = fit["bot_w"], fit["bot_d"]
    mode = fit.get("taper", "concentric")
    dx = 0.0
    if mode == "flush_left":
        dx = -(tw - bw) / 2.0
    elif mode == "flush_right":
        dx = (tw - bw) / 2.0
    return dx, 0.0


def assembly_extent(fit):
    """(min_x, max_x, min_y, max_y, total_z) of the whole assembly in inches."""
    fw = FLANGE_IN
    tw, td = fit["top_w"] + 2 * fw, fit["top_d"] + 2 * fw
    bw, bd = fit["bot_w"], fit["bot_d"]
    zs = fit["height_in"]
    xs = [tw / 2, bw / 2]
    ys = [td / 2, bd / 2]
    if fit.get("flex"):
        xs.append(fit["flex"]["w"] / 2)
        ys.append(fit["flex"]["d"] / 2)
        zs += fit["flex"].get("height_in", 16)
    if fit.get("square_to_round"):
        zs += fit["square_to_round"].get("height_in", 12)
    m = max(xs)
    n = max(ys)
    return -m, m, -n, n, zs


def draw_box(iso, c, w, d, z_top, z_bot, cx, cy, hatch=False, s_label=False):
    """Open rectangular box (flex piece): top face, front face, right face."""
    top = rect_at(w, d, cx, cy)
    bl, br, fr, fl = top  # back-left, back-right, front-right, front-left
    # order from rect_at: (bl)(br)(fr)(fl) with y+d/2 = front
    iso.poly(c, [(x, y, z_top) for (x, y) in top], fill=F_TOP)
    front = [(fl[0], fl[1], z_top), (fr[0], fr[1], z_top),
             (fr[0], fr[1], z_bot), (fl[0], fl[1], z_bot)]
    iso.poly(c, front, fill=F_FRONT)
    side = [(br[0], br[1], z_top), (fr[0], fr[1], z_top),
            (fr[0], fr[1], z_bot), (br[0], br[1], z_bot)]
    iso.poly(c, side, fill=F_SIDE)
    if hatch:
        c.saveState()
        c.setStrokeColor(OUTLINE)
        c.setLineWidth(0.35)
        for i in (1, 2, 3):
            z = z_top + (z_bot - z_top) * i / 4.0
            x0, y0 = iso.pt(fl[0], fl[1], z)
            x1, y1 = iso.pt(fr[0], fr[1], z)
            c.line(x0, yy(y0), x1, yy(y1))
        c.restoreState()
    if s_label:
        mx, my = iso.pt((fl[0] + fr[0]) / 2 - w * 0.18, fl[1], (z_top + z_bot) / 2)
        c.setFont(FONT_B, 8.2)
        c.setFillColor(HexColor("#3A3A37"))
        c.drawString(mx, yy(my) - 3, "S")
        dx_, dy_ = iso.pt(fr[0], fr[1] - d * 0.25, (z_top + z_bot) / 2)
        c.drawString(dx_ - 6, yy(dy_) - 8, "drive")


def draw_fitting(c, fit):
    """Isometric assembly. Returns dict of leader anchor points (top-down pts)."""
    fw = FLANGE_IN
    tw, td = fit["top_w"], fit["top_d"]
    bw, bd = fit["bot_w"], fit["bot_d"]
    h = fit["height_in"]
    dx, dy = bottom_center(fit)

    x0, x1, y0, y1, total_z = assembly_extent(fit)
    # Auto-scale: fit projected extent into the drawing region.
    corners = []
    for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        corners.append((x * UX + y * VX, x * UY + y * VY))
    minpx = min(p[0] for p in corners)
    maxpx = max(p[0] for p in corners)
    minpy = min(p[1] for p in corners)
    maxpy = max(p[1] for p in corners) + HZ * total_z
    gaps = GAP_PT * (1 + (1 if fit.get("square_to_round") else 0))
    sx = (DRAW_X1 - DRAW_X0) / (maxpx - minpx)
    sy = (DRAW_Y1 - DRAW_Y0 - gaps) / (maxpy - minpy)
    s = min(sx, sy)
    ox = DRAW_X0 - minpx * s + ((DRAW_X1 - DRAW_X0) - (maxpx - minpx) * s) / 2
    oy = DRAW_Y0 - minpy * s
    iso = Iso(s, ox, oy)
    anchors = {}

    # Flange ring + plate + top opening.
    ring = rect_at(tw + 2 * fw, td + 2 * fw, 0, 0)
    plate = rect_at(tw + 2 * fw * 0.5, td + 2 * fw * 0.5, 0, 0)
    opening = rect_at(tw, td, 0, 0)
    iso.poly(c, [(x, y, 0) for (x, y) in ring], fill=F_RING, width=0.9)
    iso.poly(c, [(x, y, 0) for (x, y) in plate], fill=F_PLATE, width=0.5)
    iso.poly(c, [(x, y, 0) for (x, y) in opening], fill=F_TOP, width=0.5)
    # Screw dots on the plate band midline: front edge, right edge, back edge.
    c.saveState()
    c.setFillColor(Color(0, 0, 0))
    bx, by = tw / 2 + fw * 0.5, td / 2 + fw * 0.5
    dots = [(-tw * 0.25, by), (tw * 0.25, by),            # front edge
            (bx, -td * 0.25), (bx, td * 0.25),            # right edge
            (-tw * 0.25, -by), (tw * 0.25, -by)]          # back edge
    for (dxp, dyp) in dots:
        px, py = iso.pt(dxp, dyp, 0)
        c.circle(px, yy(py), 1.0, fill=1, stroke=0)
    c.restoreState()
    anchors["flange"] = iso.pt(tw / 2 + fw, -td / 2 - fw, 0)
    anchors["top"] = iso.pt(tw / 2, td / 2 * 0.2, 0)

    # Transition body: front + right walls from top opening to bottom rect.
    topr = rect_at(tw, td, 0, 0)
    botr = rect_at(bw, bd, dx, dy)
    tbl, tbr, tfr, tfl = topr
    bbl, bbr, bfr, bfl = botr
    iso.poly(c, [(tfl[0], tfl[1], 0), (tfr[0], tfr[1], 0),
                 (bfr[0], bfr[1], h), (bfl[0], bfl[1], h)], fill=F_FRONT, width=0.9)
    iso.poly(c, [(tbr[0], tbr[1], 0), (tfr[0], tfr[1], 0),
                 (bfr[0], bfr[1], h), (bbr[0], bbr[1], h)], fill=F_SIDE, width=0.6)
    iso.poly(c, [(x, y, h) for (x, y) in botr], fill=F_BOTTOM, width=0.6)
    anchors["liner"] = iso.pt((tfr[0] + bfr[0]) / 2, (tfr[1] + bfr[1]) / 2, h * 0.45)
    anchors["bottom"] = iso.pt(bfr[0], bfr[1], h)

    z = h
    # Separate flex piece (exploded below the drop bottom).
    if fit.get("flex"):
        fx = fit["flex"]
        fh = fx.get("height_in", 16)
        zgap = GAP_PT / (s * HZ)
        z_top = z + zgap
        draw_box(iso, c, fx["w"], fx["d"], z_top, z_top + fh, dx, dy,
                 hatch=True, s_label=True)
        anchors["flex"] = iso.pt(dx + fx["w"] / 2, dy, z_top + fh * 0.5)
        z = z_top + fh

    # Separate square-to-round (exploded below the flex).
    if fit.get("square_to_round"):
        sq = fit["square_to_round"]
        dia = sq["dia"]
        sh = sq.get("height_in", 12)
        zgap = GAP_PT / (s * HZ)
        z_top = z + zgap
        topq = rect_at(fit["bot_w"], fit["bot_d"], dx, dy)
        qbl, qbr, qfr, qfl = topq
        iso.poly(c, [(x, y, z_top) for (x, y) in topq], fill=F_TOP)
        # front + side frustum faces down to the circle footprint.
        r = dia / 2.0
        iso.poly(c, [(qfl[0], qfl[1], z_top), (qfr[0], qfr[1], z_top),
                     (dx + r, dy, z_top + sh), (dx - r, dy, z_top + sh)],
                 fill=F_FRONT, width=0.6)
        iso.poly(c, [(qbr[0], qbr[1], z_top), (qfr[0], qfr[1], z_top),
                     (dx + r, dy, z_top + sh)], fill=F_SIDE, width=0.6)
        # bottom ellipse.
        ex, ey = iso.pt(dx, dy, z_top + sh)
        rw = r * s * (UX - VX) / 1.6
        c.saveState()
        c.setFillColor(F_BOTTOM)
        c.setStrokeColor(OUTLINE)
        c.setLineWidth(0.6)
        c.ellipse(ex - rw, yy(ey) - rw * 0.45, ex + rw, yy(ey) + rw * 0.45,
                  fill=1, stroke=1)
        c.restoreState()
        anchors["sq2r"] = iso.pt(dx + r, dy, z_top + sh * 0.7)
    return anchors


# ---------------------------------------------------------------- text bits
def callout(c, y_top, label, value, anchor):
    """Right-column callout with dashed leader from anchor to the text block."""
    ax, ay = anchor
    c.saveState()
    c.setStrokeColor(LEADER)
    c.setLineWidth(0.45)
    c.setDash(3, 2.25)
    c.line(ax, yy(ay), CALL_LINE_X, yy(y_top + 4))
    c.restoreState()
    c.saveState()
    c.setFillColor(LEADER)
    c.circle(ax, yy(ay), 1.4, fill=1, stroke=0)
    c.restoreState()
    c.setFont(FONT_B, 10.5)
    c.setFillColor(INK_DARK)
    c.drawString(CALL_TEXT_X, yy(y_top + 8), label)
    if value:
        c.setFont(FONT, 9)
        c.setFillColor(INK_GREY)
        c.drawString(CALL_TEXT_X, yy(y_top + 20), value)


def spec_box(c, title, lines):
    x0, y0t, x1, y1t = 30, 279, 480, 345
    c.saveState()
    c.setFillColor(BOX_FILL)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.75)
    c.roundRect(x0, yy(y1t), x1 - x0, y1t - y0t, 10, fill=1, stroke=1)
    c.restoreState()
    c.setFont(FONT_B, 10.5)
    c.setFillColor(INK_DARK)
    c.drawString(44, yy(297), title)
    c.setFont(FONT, 9)
    c.setFillColor(INK_GREY)
    for i, line in enumerate(lines[:3]):
        c.drawString(44, yy(312 + 13.5 * i), line)


def fitting_callouts(fit):
    """(label, value, anchor-key) list in drawing order."""
    out = [(fit.get("flange_note", '1" flange (4 sides)'),
            fit.get("flange_sub", "screw to curb"), "flange"),
           ("Top opening", "%d × %d" % (fit["top_w"], fit["top_d"]), "top")]
    if fit.get("liner_note"):
        out.append((fit["liner_note"], fit.get("liner_sub", "internal"), "liner"))
    out.append(("Drop bottom", "%d × %d" % (fit["bot_w"], fit["bot_d"]), "bottom"))
    if fit.get("flex"):
        out.append(("Flex (separate)",
                    "%d × %d" % (fit["flex"]["w"], fit["flex"]["d"]), "flex"))
    if fit.get("square_to_round"):
        out.append(("Square-to-round",
                    fit["square_to_round"].get("note", "separate"), "sq2r"))
    return out


def page_schedule(c, data):
    x = MARGIN
    c.setFont(FONT_B, 16)
    c.setFillColor(INK_DARK)
    c.drawString(x, yy(58), data["schedule_title"])
    c.setFont(FONT, 9.4)
    c.setFillColor(INK_GREY)
    c.drawString(x, yy(74), data["schedule_subtitle"])
    c.saveState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.75)
    c.line(x, yy(84), PAGE_W - MARGIN, yy(84))
    c.restoreState()

    c.setFont(FONT_B, 9.8)
    c.setFillColor(INK_DARK)
    c.drawString(x + 4, yy(104), "Fittings (one per page following):")
    y = 126
    for fit in data["fittings"]:
        c.setFont(FONT_B, 9.8)
        c.setFillColor(INK_DARK)
        c.drawString(x + 22, yy(y), fit["tag"])
        c.setFont(FONT, 9.4)
        c.setFillColor(INK_BODY)
        c.drawString(x + 78, yy(y), fit["schedule_line"])
        y += 21.5

    fy = PAGE_H - 46
    c.saveState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.75)
    c.line(x, yy(fy - 12), PAGE_W - MARGIN, yy(fy - 12))
    c.restoreState()
    c.setFont(FONT, 9)
    c.setFillColor(INK_GREY)
    for i, note in enumerate(data.get("footer_notes", [])[:2]):
        c.drawString(x, yy(fy + 13 * i), note)


def page_fitting(c, fit):
    anchors = draw_fitting(c, fit)
    calls = fitting_callouts(fit)
    n = len(calls)
    top0, span = 56.0, 200.0
    step = span / max(n - 1, 1)
    for i, (label, value, key) in enumerate(calls):
        if key in anchors:
            callout(c, top0 + step * i, label, value, anchors[key])
    parts = [p for p in (fit["tag"], fit.get("service", ""), fit["piece"]) if p]
    title = " · ".join(parts) + " · Qty %s" % fit.get("qty", 1)
    spec_box(c, title, fit["spec_lines"])


# ---------------------------------------------------------------- company
TOKEN_RE = re.compile(r"\{\{company\.([A-Za-z_]+)\}\}")


def load_company(path):
    if not os.path.exists(path):
        raise SystemExit("Company config not found: %s (use --company)" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def fill_company_tokens(obj, company):
    """Replace {{company.KEY}} tokens in every string of the data file."""
    if isinstance(obj, str):
        def rep(m):
            key = m.group(1)
            if key not in company:
                raise SystemExit("Unknown company token {{company.%s}}" % key)
            val = company[key]
            return "" if val is None else str(val)
        return TOKEN_RE.sub(rep, obj)
    if isinstance(obj, list):
        return [fill_company_tokens(x, company) for x in obj]
    if isinstance(obj, dict):
        return {k: fill_company_tokens(v, company) for k, v in obj.items()}
    return obj


# -------------------------------------------------------------------- build
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Build a duct transition shop ticket PDF.")
    ap.add_argument("data", nargs="?", default=os.path.join(script_dir, "sample_data.json"),
                    help="fitting data file (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=os.path.normpath(
                    os.path.join(script_dir, "..", "..", "company.example.json")),
                    help="company config JSON (default: template-library/company.example.json)")
    args = ap.parse_args()

    company = load_company(args.company)
    with open(args.data, "r", encoding="utf-8") as fh:
        data = fill_company_tokens(json.load(fh), company)

    for fit in data["fittings"]:
        for k in ("tag", "service", "piece", "top_w", "top_d", "bot_w", "bot_d",
                  "height_in", "schedule_line", "spec_lines"):
            if k not in fit:
                raise KeyError("fitting %r missing %r" % (fit.get("tag", "?"), k))

    out_dir = data.get("output_dir") or os.path.join(script_dir, "_sample_output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, data["output_filename"])
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H), invariant=1)
    c.setTitle(data.get("pdf_title", "Duct Transition Shop Ticket"))
    c.setAuthor(company.get("legal_name") or "")

    page_schedule(c, data)
    c.showPage()
    for fit in data["fittings"]:
        page_fitting(c, fit)
        c.showPage()
    c.save()
    print("Wrote " + out_path)


if __name__ == "__main__":
    main()
