# -*- coding: utf-8 -*-
"""
PCO (Proposed Change Order) package builder.

One JSON data file in, one merged PDF out: a narrative and sign-off page,
a Scope and Cost Itemization, then any backup attachments (RFIs, engineer
details, subcontractor proposals) merged in order. Every job-specific value
comes from the JSON data file; company fields come from the company config.
This script holds only fixed wording and layout.

Usage:  py -3 build_pco.py [data.json] [--company path/to/company.json]
        data.json defaults to sample_data.json next to this script.
        --company defaults to ../../company.example.json (template-library root).

Company tokens: any string in the data file may contain {{company.KEY}},
for example {{company.legal_name}} or {{company.pm_name}}; it is replaced
with that key from the company config before the build.

Output: <job_slug>_PCO-<pco_number>_<file_slug>.pdf in the output dir
        (default: _sample_output next to this script).

House style: no em or en dashes anywhere (the script refuses data that
contains them). Drawing tags keep native form (RTU-1, L3x3x1/4, W14x22).

Determinism: no datetime.now/random anywhere; reportlab canvases are built
with invariant=1; final PDF metadata dates come from meta.created in the JSON.

Libraries: stdlib + reportlab + PyMuPDF (fitz) only.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ------------------------------------------------------------------ styles
styles = getSampleStyleSheet()
TITLE = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold",
                       fontSize=16, spaceAfter=2, alignment=0)
SUB = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Bold",
                     fontSize=11, textColor=colors.HexColor("#444444"), spaceAfter=8)
H = ParagraphStyle("h", parent=styles["Heading2"], fontName="Helvetica-Bold",
                   fontSize=11, spaceBefore=10, spaceAfter=4,
                   textColor=colors.HexColor("#1a1a1a"))
BODY = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=9.5, leading=13, spaceAfter=4)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=8.5, leading=11,
                      textColor=colors.HexColor("#333333"))
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=14, bulletIndent=2, spaceAfter=3)
CELL = ParagraphStyle("cell", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=9, leading=11.5)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
RIGHT = ParagraphStyle("right", parent=CELL, alignment=2)
RIGHTB = ParagraphStyle("rightb", parent=CELLB, alignment=2)

RULE_LIGHT = colors.HexColor("#dddddd")
RULE_HEAVY = colors.HexColor("#333333")
FILL_HEAD = colors.HexColor("#e9ecef")
FILL_TOTAL = colors.HexColor("#f6f6f6")
FILL_CALLOUT = colors.HexColor("#f3f4f6")
BOX_CALLOUT = colors.HexColor("#9aa0a6")


def money(x):
    return "$%s" % format(x, ",.2f")


def paren(x):
    return "(%s)" % money(x)


def b(txt):
    return Paragraph(txt, BULLET, bulletText=u"•")


# ------------------------------------------------------------------ company config
TOKEN_RE = re.compile(r"\{\{company\.([A-Za-z_]+)\}\}")


def load_company(path):
    if not os.path.exists(path):
        raise SystemExit("Company config not found: %s (use --company)" % path)
    with io.open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def company_short(company):
    return company.get("dba") or company.get("legal_name") or "Contractor"


def build_part(story, pdf_title, lm=0.85, rm=0.85):
    """Render a story to PDF bytes. invariant=1 keeps output byte-stable."""
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=letter, leftMargin=lm * inch, rightMargin=rm * inch,
                      topMargin=0.7 * inch, bottomMargin=0.6 * inch,
                      title=pdf_title, invariant=1).build(story)
    return buf.getvalue()


def hdr_table(rows):
    t = Table([[Paragraph(k, CELLB), Paragraph(v, CELL)] for k, v in rows],
              colWidths=[0.95 * inch, 5.55 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 1),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def callout(rows):
    t = Table([[Paragraph(k, CELLB), Paragraph(v, CELL)] for k, v in rows],
              colWidths=[0.95 * inch, 5.55 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, -1), FILL_CALLOUT),
                           ("BOX", (0, 0), (-1, -1), 0.6, BOX_CALLOUT),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    return t


def sig(party, name_role, extra=None):
    rows = [[Paragraph(party, CELLB), Paragraph("", CELL)],
            [Paragraph("_______________________________________________", CELL),
             Paragraph("Date: ____________________", CELL)]]
    nr = name_role + ("&nbsp;&nbsp;&nbsp;&nbsp;" + extra if extra else "")
    rows.append([Paragraph(nr, CELL), Paragraph("", CELL)])
    tb = Table(rows, colWidths=[4.2 * inch, 2.3 * inch])
    tb.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ("TOPPADDING", (0, 0), (-1, -1), 2),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return tb


def signoffs(story, data):
    story.append(Paragraph(data["narrative"]["signoff_heading"], H))
    parties = data["narrative"]["signoffs"]
    for i, p in enumerate(parties):
        story.append(sig(p["party"], p["name_role"], p.get("extra")))
        if i < len(parties) - 1:
            story.append(Spacer(1, 4))


# ------------------------------------------------------------------ narrative page blocks
def cost_amount(row, rates):
    """A cost row amount: explicit number, or {'foreman','tech','material'} hours
    priced at the rates in the JSON so labor math cannot drift."""
    if "amount" in row and row["amount"] is not None:
        return float(row["amount"])
    h = row.get("hours")
    if h is None:
        return None
    return (h.get("foreman", 0) * rates["foreman_rate"]
            + h.get("tech", 0) * rates["tech_rate"] + h.get("material", 0.0))


def narrative_cost_table(story, block, rates):
    rows = []
    for r in block["rows"]:
        lab = r["label"]
        if r.get("blank"):
            rows.append([Paragraph("<b>%s</b>" % lab, CELLB), Paragraph("", RIGHT)])
            continue
        amt = cost_amount(r, rates)
        bold = bool(r.get("bold"))
        val = paren(amt) if r.get("paren") else money(amt)
        if bold:
            val = "<b>%s</b>" % val
        if r.get("tag"):
            val += "&nbsp;&nbsp;<font size=7>%s</font>" % r["tag"]
        rows.append([Paragraph(("<b>%s</b>" % lab) if bold else lab, CELLB if bold else CELL),
                     Paragraph(val, RIGHTB if bold else RIGHT)])
    cw = block.get("col_widths", [5.5, 1.0])
    pad = block.get("padding", 2.5)
    ct = Table(rows, colWidths=[cw[0] * inch, cw[1] * inch])
    last = len(rows) - 1
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
          ("LINEABOVE", (0, last), (-1, last), 0.8, RULE_HEAVY),
          ("LINEBELOW", (0, last), (-1, last), 0.8, RULE_HEAVY),
          ("BACKGROUND", (0, last), (-1, last), FILL_TOTAL)]
    ct.setStyle(TableStyle(ts))
    story.append(ct)
    story.append(Spacer(1, 4))


def render_section_blocks(story, blocks, rates):
    for blk in blocks:
        t = blk["type"]
        if t == "bullet":
            story.append(b(blk["text"]))
        elif t == "para":
            story.append(Paragraph(blk["text"], BODY))
        elif t == "note":
            story.append(Paragraph(blk["text"], NOTE))
        elif t == "cost_table":
            narrative_cost_table(story, blk, rates)
        elif t == "spacer":
            story.append(Spacer(1, blk.get("height", 4)))
        else:
            raise SystemExit("Unknown narrative block type: %s" % t)


def build_narrative(data):
    n = data["narrative"]
    rates = data["rates"]
    s = []
    s.append(Paragraph("PROPOSED CHANGE ORDER &nbsp;&nbsp;|&nbsp;&nbsp; %s" % n["pco_label"], TITLE))
    s.append(Paragraph(n["subtitle"], SUB))
    s.append(hdr_table([(k, v) for k, v in n["header_rows"]]))
    s.append(Spacer(1, 6))
    if n.get("callout_rows"):
        s.append(callout([(k, v) for k, v in n["callout_rows"]]))
    for sec in n["sections"]:
        if sec.get("signoffs"):
            signoffs(s, data)
            continue
        s.append(Paragraph(sec["heading"], H))
        render_section_blocks(s, sec.get("blocks", []), rates)
    return build_part(s, data["meta"]["pdf_title"], lm=0.85, rm=0.85)


# ------------------------------------------------------------------ itemization page blocks
def three_col(g, header_rows, total_label, total_val):
    rows = [[Paragraph("Line", CELLB), Paragraph("Type", CELLB), Paragraph("Amount", RIGHTB)]]
    for label, kind, amt in header_rows:
        rows.append([Paragraph(label, CELL), Paragraph(kind, CELL), Paragraph(money(amt), RIGHT)])
    rows.append([Paragraph("", CELLB), Paragraph(total_label, CELLB),
                 Paragraph(money(total_val), RIGHTB)])
    tb = Table(rows, colWidths=[4.55 * inch, 1.15 * inch, 1.0 * inch])
    tb.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                            ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                            ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                            ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                            ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(tb)
    g.append(Spacer(1, 8))
    s = round(sum(r[2] for r in header_rows), 2)
    if abs(s - total_val) > 0.005:
        print("  WARNING three_col rows foot to %s but total is %s" % (money(s), money(total_val)))


def labor_table(g, lines, rates, short_name):
    rf, rt = rates["foreman_rate"], rates["tech_rate"]
    rows = [[Paragraph("Item", CELLB), Paragraph("Task", CELLB), Paragraph("Frmn hr", RIGHTB),
             Paragraph("Tech hr", RIGHTB), Paragraph("Labor", RIGHTB), Paragraph("Matl", RIGHTB),
             Paragraph("Total", RIGHTB)]]
    sf = st = sl = sm = stt = 0
    for code, task, fh, th, mat in lines:
        lab = fh * rf + th * rt
        tot = lab + mat
        sf += fh; st += th; sl += lab; sm += mat; stt += tot
        rows.append([Paragraph(code, CELL), Paragraph(task, CELL), Paragraph(str(fh), RIGHT),
                     Paragraph(str(th), RIGHT), Paragraph(money(lab), RIGHT),
                     Paragraph(money(mat), RIGHT), Paragraph(money(tot), RIGHT)])
    rows.append([Paragraph("", CELLB), Paragraph("Subtotal, %s labor" % short_name, CELLB),
                 Paragraph(str(sf), RIGHTB), Paragraph(str(st), RIGHTB), Paragraph(money(sl), RIGHTB),
                 Paragraph(money(sm), RIGHTB), Paragraph(money(stt), RIGHTB)])
    tb = Table(rows, colWidths=[0.4 * inch, 3.35 * inch, 0.62 * inch, 0.6 * inch,
                                0.72 * inch, 0.62 * inch, 0.72 * inch])
    tb.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                            ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                            ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                            ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                            ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(tb)
    g.append(Spacer(1, 8))
    return stt


def welder_detail(g, blk):
    g.append(Paragraph("Welder materials (itemized)", CELLB))
    rows = [[Paragraph("Item", CELLB), Paragraph("Qty", RIGHTB), Paragraph("Unit cost", RIGHTB),
             Paragraph("Total", RIGHTB)]]
    msum = 0
    for item, qty, unit, tot in blk["materials"]:
        msum += tot
        rows.append([Paragraph(item, CELL), Paragraph(qty, RIGHT), Paragraph(money(unit), RIGHT),
                     Paragraph(money(tot), RIGHT)])
    rows.append([Paragraph("Materials subtotal", CELLB), Paragraph("", RIGHT), Paragraph("", RIGHT),
                 Paragraph(money(msum), RIGHTB)])
    t = Table(rows, colWidths=[3.9 * inch, 0.75 * inch, 0.95 * inch, 1.0 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                           ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                           ("LINEABOVE", (0, -1), (-1, -1), 0.6, RULE_HEAVY)]))
    g.append(t)
    g.append(Spacer(1, 5))
    g.append(Paragraph("Welder labor (men times hours times rate)", CELLB))
    rows = [[Paragraph("Crew", CELLB), Paragraph("Men", RIGHTB), Paragraph("Hours", RIGHTB),
             Paragraph("Rate", RIGHTB), Paragraph("Total", RIGHTB)]]
    lsum = 0
    for crew, men, hrs, rate, tot in blk["labor"]:
        lsum += tot
        rows.append([Paragraph(crew, CELL), Paragraph(str(men), RIGHT), Paragraph(str(hrs), RIGHT),
                     Paragraph(money(rate), RIGHT), Paragraph(money(tot), RIGHT)])
    rows.append([Paragraph("Labor subtotal", CELLB), Paragraph("", RIGHT), Paragraph("", RIGHT),
                 Paragraph("", RIGHT), Paragraph(money(lsum), RIGHTB)])
    t = Table(rows, colWidths=[3.35 * inch, 0.7 * inch, 0.7 * inch, 0.85 * inch, 1.0 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                           ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                           ("LINEABOVE", (0, -1), (-1, -1), 0.6, RULE_HEAVY)]))
    g.append(t)
    g.append(Spacer(1, 5))
    trip = blk["trip"]
    total = blk["total"]
    rows = [
        [Paragraph("Materials", CELL), Paragraph(money(msum), RIGHT)],
        [Paragraph("Labor", CELL), Paragraph(money(lsum), RIGHT)],
        [Paragraph("Trip charge", CELL), Paragraph(money(trip), RIGHT)],
        [Paragraph("<b>Welder total (firm lump, subcontractor proposal)</b>", CELLB),
         Paragraph("<b>%s</b>" % money(total), RIGHTB)],
    ]
    t = Table(rows, colWidths=[5.6 * inch, 1.0 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                           ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                           ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(t)
    g.append(Spacer(1, 8))
    if abs(msum + lsum + trip - total) > 0.005:
        print("  WARNING welder_detail parts %s do not foot to total %s"
              % (money(msum + lsum + trip), money(total)))


def roofer_breakout(g, blk):
    g.append(Paragraph(blk["title"], CELLB))
    rows = [[Paragraph("Line", CELLB), Paragraph("Type", CELLB), Paragraph("Amount", RIGHTB)]]
    s = 0
    for label, kind, amt in blk["lines"]:
        s += amt
        rows.append([Paragraph(label, CELL), Paragraph(kind, CELL), Paragraph(money(amt), RIGHT)])
    total_label = blk.get("total_label", "Firm total (roofer cost)")
    rows.append([Paragraph("", CELLB), Paragraph(total_label, CELLB),
                 Paragraph(money(round(s, 2)), RIGHTB)])
    t = Table(rows, colWidths=[4.55 * inch, 1.15 * inch, 1.0 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                           ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                           ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                           ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(t)
    g.append(Spacer(1, 8))
    return round(s, 2)


def crew_grid(g, blk):
    grows = [[Paragraph("Day", CELLB), Paragraph("Phase", CELLB), Paragraph("Frmn hr", RIGHTB),
              Paragraph("Tech hr", RIGHTB), Paragraph("Fire watch hr", RIGHTB),
              Paragraph("Billed hr", RIGHTB)]]
    sup = tech = fw = 0
    for day, phase, f, t, w in blk["rows"]:
        sup += f; tech += t; fw += w
        grows.append([Paragraph(day, CELL), Paragraph(phase, CELL), Paragraph(str(f), RIGHT),
                      Paragraph(str(t), RIGHT), Paragraph(str(w), RIGHT), Paragraph(str(f + t), RIGHT)])
    grows.append([Paragraph("", CELLB), Paragraph("Total", CELLB), Paragraph(str(sup), RIGHTB),
                  Paragraph(str(tech), RIGHTB), Paragraph("%d (base)" % fw, RIGHTB),
                  Paragraph(str(sup + tech), RIGHTB)])
    gt = Table(grows, colWidths=[0.7 * inch, 2.85 * inch, 0.75 * inch, 0.75 * inch,
                                 0.95 * inch, 0.75 * inch])
    gt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                            ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                            ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                            ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                            ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(gt)
    g.append(Spacer(1, 4))


def credit_labor_table(g, blk, short_name):
    rows = [[Paragraph("Item", CELLB), Paragraph("Scope of work (deleted)", CELLB),
             Paragraph("Hours", RIGHTB), Paragraph("Rate", RIGHTB), Paragraph("Credit", RIGHTB)]]
    shrs = 0
    scred = 0.0
    for no, scope, hrs, rate in blk["rows"]:
        cred = hrs * rate
        shrs += hrs
        scred += cred
        rows.append([Paragraph(str(no), CELL), Paragraph(scope, CELL), Paragraph(str(hrs), RIGHT),
                     Paragraph(money(rate), RIGHT), Paragraph(paren(cred), RIGHT)])
    rows.append([Paragraph("", CELLB), Paragraph(blk.get("total_label",
                 "TOTAL %s labor (deduct)" % short_name), CELLB),
                 Paragraph(str(shrs), RIGHTB), Paragraph("", RIGHTB), Paragraph(paren(scred), RIGHTB)])
    t = Table(rows, colWidths=[0.4 * inch, 3.85 * inch, 0.6 * inch, 0.75 * inch, 0.9 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
                           ("BACKGROUND", (0, 0), (-1, 0), FILL_HEAD),
                           ("LINEABOVE", (0, -1), (-1, -1), 0.8, RULE_HEAVY),
                           ("BACKGROUND", (0, -1), (-1, -1), FILL_TOTAL)]))
    g.append(t)
    g.append(Spacer(1, 8))


def build_itemization(data, company):
    it = data["itemization"]
    rates = data["rates"]
    short_name = company_short(company)
    contractor = it.get("contractor_line") or company.get("legal_name", "")
    g = []
    g.append(Paragraph("Scope and Cost Itemization (broken out)", TITLE))
    g.append(Paragraph("Every trade broken out: description, quantity, unit cost, total, "
                       "and labor by hours and rate", SUB))
    intro = "%s | %s | %s." % (it["project_short"], it["pco_label"], contractor)
    if it.get("intro"):
        intro += " " + it["intro"]
    intro += (" Labor rates: %s %s per hour, %s %s per hour."
              % (rates["foreman_name"].lower(), money(rates["foreman_rate"]),
                 rates["tech_name"].lower(), money(rates["tech_rate"])))
    g.append(Paragraph(intro, BODY))
    g.append(Spacer(1, 6))
    for blk in it["blocks"]:
        t = blk["type"]
        if t == "heading":
            g.append(Paragraph(blk["text"], H))
        elif t == "note":
            g.append(Paragraph(blk["text"], NOTE))
        elif t == "para":
            g.append(Paragraph(blk["text"], BODY))
        elif t == "spacer":
            g.append(Spacer(1, blk.get("height", 4)))
        elif t == "welder_detail":
            welder_detail(g, blk)
        elif t == "roofer_breakout":
            tot = roofer_breakout(g, blk)
            print("  roofer breakout foots to", money(tot))
        elif t == "labor_table":
            lines = [tuple(x) for x in blk["lines"]]
            ctot = labor_table(g, lines, rates, short_name)
            print("  labor subtotal computed:", money(ctot))
        elif t == "crew_grid":
            crew_grid(g, blk)
        elif t == "credit_labor_table":
            credit_labor_table(g, blk, short_name)
        elif t == "three_col":
            rows = [tuple(x) for x in blk["rows"]]
            three_col(g, rows, blk["total_label"], blk["total"])
        else:
            raise SystemExit("Unknown itemization block type: %s" % t)
    return build_part(g, data["meta"]["pdf_title"], lm=0.7, rm=0.7)


# ------------------------------------------------------------------ assembly
def meta_dates(data, company):
    created = data["meta"].get("created", "2026-01-01")
    d = "D:%s000000" % created.replace("-", "")
    return {"title": data["meta"]["pdf_title"],
            "author": company.get("legal_name") or "",
            "producer": "", "creator": "",
            "creationDate": d, "modDate": d}


def make_deterministic_id(path):
    """MuPDF writes a fresh random /ID on every save; everything else is
    byte-stable (reportlab invariant=1). Replace the trailer /ID with an MD5
    of the file content so identical data gives byte-identical PDFs."""
    with open(path, "rb") as f:
        raw = f.read()
    matches = list(re.finditer(rb"/ID\[<([0-9A-Fa-f]{32})><([0-9A-Fa-f]{32})>\]", raw))
    if not matches:
        return
    m = matches[-1]  # the document trailer is the last one in the file
    zeroed = raw[:m.start(1)] + b"0" * 32 + raw[m.end(1):m.start(2)] + b"0" * 32 + raw[m.end(2):]
    dig = hashlib.md5(zeroed).hexdigest().upper().encode("ascii")
    fixed = raw[:m.start(1)] + dig + raw[m.end(1):m.start(2)] + dig + raw[m.end(2):]
    with open(path, "wb") as f:
        f.write(fixed)


def save_doc(doc, path, data, company):
    doc.set_metadata(meta_dates(data, company))
    doc.save(path, garbage=4, deflate=True)
    make_deterministic_id(path)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Build a PCO package PDF from a JSON data file.")
    ap.add_argument("data", nargs="?", default=os.path.join(here, "sample_data.json"),
                    help="PCO data file (default: sample_data.json next to this script)")
    ap.add_argument("--company", default=os.path.normpath(
                    os.path.join(here, "..", "..", "company.example.json")),
                    help="company config JSON (default: template-library/company.example.json)")
    args = ap.parse_args()

    data_path = args.data
    raw = io.open(data_path, "r", encoding="utf-8").read()
    for ch, name in ((chr(0x2014), "em dash"), (chr(0x2013), "en dash")):
        if ch in raw:
            raise SystemExit("House style violation: %s found in %s. Use commas, periods, "
                             "or hyphens instead." % (name, data_path))
    company = load_company(args.company)
    data = fill_company_tokens(json.loads(raw), company)
    data_dir = os.path.dirname(os.path.abspath(data_path))

    out_dir = data["meta"].get("output_dir") or os.path.join(here, "_sample_output")
    os.makedirs(out_dir, exist_ok=True)

    print("PCO %s:" % data["meta"]["pco_number"])
    parts = [build_narrative(data)]
    if data.get("itemization", {}).get("enabled", False):
        parts.append(build_itemization(data, company))

    final = fitz.open()
    for pb in parts:
        src = fitz.open(stream=pb, filetype="pdf")
        final.insert_pdf(src)
        src.close()
    for att in data.get("attachments", []):
        att_path = att if os.path.isabs(att) else os.path.join(data_dir, att)
        if os.path.exists(att_path):
            src = fitz.open(att_path)
            final.insert_pdf(src)
            src.close()
        else:
            print("  MISSING attachment (skipped):", att)

    name = "%s_PCO-%s_%s.pdf" % (data["meta"]["job_slug"], data["meta"]["pco_number"],
                                 data["meta"]["file_slug"])
    out_path = os.path.join(out_dir, name)
    save_doc(final, out_path, data, company)
    print("  wrote", out_path, "| pages", final.page_count)
    final.close()


if __name__ == "__main__":
    main()
