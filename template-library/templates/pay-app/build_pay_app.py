# -*- coding: utf-8 -*-
"""
Pay Application builder: an Application for Payment face sheet plus a
Schedule of Values continuation sheet.

All job-specific content comes from a JSON data file. Company fields
(legal name, address, PM name, brand color) come from the company config
file (template-library/company.example.json by default). This script holds
only fixed wording and layout.

Usage:
    python build_pay_app.py [data.json] [output_dir] [--company company.json]

data.json    defaults to sample_data.json next to this script.
output_dir   defaults to _sample_output next to this script.
--company    defaults to ../../company.example.json relative to this script.

Company tokens: any string in the data file may contain {legal_name},
{dba}, {address_line1}, {city_state_zip}, {phone}, {email}, {website},
{license}, {pm_name}, {pm_title}, {pm_phone} or {pm_email}; they are filled
from the company config.

Determinism: no datetime/random anywhere; reportlab invariant=1 so identical
data produces byte-identical PDFs. Every date and number comes from the JSON.

Arithmetic: every face-sheet box is recomputed from the SOV lines and the
script asserts internal consistency (totals cross-foot) before writing.
"""

import argparse
import json
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COMPANY = os.path.join(HERE, "..", "..", "company.example.json")

# ---------------------------------------------------------------- constants
DEFAULT_PRIMARY = "#1F3A5F"           # used if the company config has no color
LIGHT = colors.HexColor("#E8EEF5")    # totals-row and AMOUNT DUE fill
GREY = colors.HexColor("#666666")     # small italic notes
BORDER = colors.HexColor("#B8C5D6")   # all table grid lines and the rule
GREEN = colors.HexColor("#E4F0E4")    # stored-material row highlight
RED = colors.HexColor("#B00020")      # banner and changed-cell highlight

CERTIFICATION = (
    "Contractor's statement: By signing below, the contractor confirms, "
    "based on what it knows today, that the amount due shown above is "
    "payable now, that the work billed here matches the contract, and that "
    "money the owner paid on earlier applications has been passed on to the "
    "subcontractors and suppliers who did that work.")

CONTRACTOR_SIGN_LINE = (
    "Signed for the contractor: ______________________________   "
    "Date: ______________ (have the signature notarized if the owner "
    "requires it)")

EPS = 0.005  # half a cent

_TOKEN = re.compile(r"\{([a-z_0-9]+)\}")


# ---------------------------------------------------------------- helpers
def r2(v):
    return round(float(v) + 0.0, 2)


def fail(msg):
    raise SystemExit("DATA/CROSS-FOOT ERROR: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def money(v):
    """Face-sheet style: always dollars, e.g. $0.00, -$12.34."""
    if v < 0:
        return "-$%s" % ("{:,.2f}".format(-v))
    return "${:,.2f}".format(v)


def money_dash(v):
    """Continuation column style: '-' for zero, else dollars."""
    if abs(v) < EPS:
        return "-"
    return money(v)


def pct_cell(g, c):
    if abs(g) < EPS or abs(c) < EPS:
        return "-"
    return "{:.2f}%".format(g / c * 100)


def rate_label(rate_pct):
    """5 -> '5%', 7.5 -> '7.5%'."""
    return ("{:g}".format(float(rate_pct))) + "%"


# ---------------------------------------------------------------- company
def load_company(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def company_tokens(company):
    return {k: v for k, v in company.items() if isinstance(v, str)}


def fill_tokens(obj, tokens):
    """Replace {company_key} tokens in every string of the data."""
    if isinstance(obj, str):
        return _TOKEN.sub(lambda m: tokens.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, list):
        return [fill_tokens(x, tokens) for x in obj]
    if isinstance(obj, dict):
        return {k: fill_tokens(v, tokens) for k, v in obj.items()}
    return obj


# ---------------------------------------------------------------- data load
def load_data(path, company):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data = fill_tokens(data, company_tokens(company))

    # Company-driven defaults, used when the data file leaves them out.
    if not data.get("contractor"):
        data["contractor"] = ", ".join(
            x for x in (company.get("legal_name"), company.get("address_line1"),
                        company.get("city_state_zip")) if x)
    if not data.get("verified_by"):
        data["verified_by"] = ", ".join(
            x for x in (company.get("pm_name"), company.get("pm_title")) if x)

    required = [
        "owner", "contractor", "project", "project_short", "project_slug",
        "via_engineer", "contract_for", "contract_ref", "contract_date",
        "application_no", "application_date", "application_date_iso",
        "period_from", "period_to", "invoice_no", "retainage_pct",
        "previous_certificates", "verified_by", "status_slug", "sov_lines",
    ]
    missing = [k for k in required if k not in data]
    check(not missing, "missing required JSON keys: " + ", ".join(missing))
    check(isinstance(data["sov_lines"], list) and data["sov_lines"],
          "sov_lines must be a non-empty list")
    for i, ln in enumerate(data["sov_lines"], start=1):
        for k in ("item", "description", "scheduled_value",
                  "previous", "this_period", "stored"):
            check(k in ln, "sov_lines[%d] missing key '%s'" % (i, k))
    return data


# ---------------------------------------------------------------- math
def compute(data):
    """Recompute every face-sheet box from the SOV lines and cross-foot."""
    rate = float(data["retainage_pct"]) / 100.0
    lines = []
    for ln in data["sov_lines"]:
        c = r2(ln["scheduled_value"])
        d = r2(ln["previous"])
        e = r2(ln["this_period"])
        f = r2(ln["stored"])
        g = r2(d + e + f)
        lines.append({
            "item": str(ln["item"]), "desc": str(ln["description"]),
            "c": c, "d": d, "e": e, "f": f, "g": g,
            "bal": r2(c - g), "ret": r2(g * rate),
        })

    ct = r2(sum(l["c"] for l in lines))
    dt = r2(sum(l["d"] for l in lines))
    et = r2(sum(l["e"] for l in lines))
    ft = r2(sum(l["f"] for l in lines))
    gt = r2(dt + et + ft)
    bal_t = r2(sum(l["bal"] for l in lines))
    # Grand-total retainage = sum of per-line rounded retainage so the
    # continuation column foots exactly to the face sheet (no 1-cent drift).
    ret_t = r2(sum(l["ret"] for l in lines))

    check(abs(r2(sum(l["g"] for l in lines)) - gt) < EPS,
          "column G does not foot: sum(G) != D+E+F totals")
    check(abs(r2(ct - gt) - bal_t) < 0.02,
          "balance-to-finish column does not foot to C - G")

    # Change order summary (all default to 0.00).
    co = data.get("change_orders", {}) or {}
    pa = r2(co.get("previous_additions", 0))
    pd_ = r2(co.get("previous_deductions", 0))
    ta = r2(co.get("this_month_additions", 0))
    td = r2(co.get("this_month_deductions", 0))
    add_t = r2(pa + ta)
    ded_t = r2(pd_ + td)
    net = r2(add_t - ded_t)

    # Line 3 (contract amount to date) must equal the column C total, because
    # approved change orders live as SOV lines. Line 1 backs the net change out.
    line3 = ct
    line1 = r2(ct - net)
    if "original_contract_sum" in data:
        check(abs(r2(data["original_contract_sum"]) - line1) < EPS,
              "original_contract_sum %s does not equal column C total "
              "minus net change orders %s" %
              (money(r2(data["original_contract_sum"])), money(line1)))
    check(abs(r2(line1 + net) - line3) < EPS, "line 1 + line 2 != line 3")

    # 5a/5b split. Cumulative stored can exceed the current column F because
    # it includes materials stored in previous periods and still on site.
    stored_cum = r2(data.get("materials_stored_cumulative", ft))
    check(-EPS <= stored_cum <= gt + EPS,
          "materials_stored_cumulative must be between 0 and total "
          "completed and stored (G)")
    work_cum = r2(gt - stored_cum)
    ret_5a = r2(work_cum * rate)
    ret_5b = r2(stored_cum * rate)
    delta = r2(ret_t - r2(ret_5a + ret_5b))
    check(abs(delta) <= 0.02,
          "retainage split 5a + 5b differs from per-line footing by more "
          "than 2 cents (%s vs %s)" % (money(r2(ret_5a + ret_5b)),
                                       money(ret_t)))
    ret_5a = r2(ret_5a + delta)  # reconcile so the printed 5a + 5b == 5

    prev = r2(data["previous_certificates"])
    earned = r2(gt - ret_t)
    due = r2(earned - prev)
    bal9 = r2(line3 - earned)

    # Final cross-foot assertions on the printed face-sheet boxes.
    check(abs(r2(ret_5a + ret_5b) - ret_t) < EPS, "5a + 5b != 5")
    check(abs(r2(earned + ret_t) - gt) < EPS, "line 6 + line 5 != line 4")
    check(abs(r2(due + prev) - earned) < EPS, "line 8 + line 7 != line 6")
    check(abs(r2(bal9 + earned) - line3) < EPS, "line 9 + line 6 != line 3")

    return {
        "rate": rate, "lines": lines,
        "ct": ct, "dt": dt, "et": et, "ft": ft, "gt": gt,
        "ret_t": ret_t, "line1": line1, "line2": net, "line3": line3,
        "co": {"pa": pa, "pd": pd_, "ta": ta, "td": td,
               "add_t": add_t, "ded_t": ded_t, "net": net},
        "stored_cum": stored_cum, "work_cum": work_cum,
        "ret_5a": ret_5a, "ret_5b": ret_5b,
        "prev": prev, "earned": earned, "due": due, "bal9": bal9,
    }


# ---------------------------------------------------------------- build
def build(data, calc, out_path, company):
    rp = rate_label(data["retainage_pct"])
    brand = company.get("brand") or {}
    navy = colors.HexColor(brand.get("primary_color") or DEFAULT_PRIMARY)
    author = data.get("pdf_author") or company.get("legal_name") or ""

    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"],
                           fontName="Helvetica-Bold", fontSize=16,
                           textColor=navy, alignment=1, spaceAfter=2)
    body = ParagraphStyle("body", parent=styles["BodyText"],
                          fontName="Helvetica", fontSize=9.5, leading=12,
                          spaceAfter=4)
    small = ParagraphStyle("small", parent=styles["BodyText"],
                           fontName="Helvetica-Oblique", fontSize=8.5,
                           leading=11, textColor=GREY, spaceAfter=3)
    draftnote = ParagraphStyle("draftnote", parent=styles["BodyText"],
                               fontName="Helvetica-Bold", fontSize=11,
                               leading=13, textColor=RED, alignment=1,
                               spaceAfter=4)
    revnote = ParagraphStyle("revnote", parent=styles["BodyText"],
                             fontName="Helvetica-Bold", fontSize=8.5,
                             leading=11, textColor=navy, alignment=1,
                             spaceAfter=6)
    h1 = ParagraphStyle("h1", parent=styles["Heading2"],
                        fontName="Helvetica-Bold", fontSize=11,
                        textColor=navy, spaceBefore=8, spaceAfter=4)
    lab = ParagraphStyle("lab", parent=body, fontName="Helvetica-Bold",
                         fontSize=8, leading=10, textColor=navy, spaceAfter=0)
    val = ParagraphStyle("val", parent=body, fontName="Helvetica",
                         fontSize=8, leading=10, spaceAfter=0)

    doc_title = data.get("doc_title", "%s Application for Payment No. %s" %
                         (data["project_short"], data["application_no"]))
    doc = BaseDocTemplate(out_path, title=doc_title, author=author,
                          invariant=1)
    port = Frame(0.7 * inch, 0.6 * inch, LETTER[0] - 1.4 * inch,
                 LETTER[1] - 1.2 * inch, id="port")
    land = Frame(0.45 * inch, 0.45 * inch, landscape(LETTER)[0] - 0.9 * inch,
                 landscape(LETTER)[1] - 0.9 * inch, id="land")
    doc.addPageTemplates([
        PageTemplate(id="portrait", frames=[port], pagesize=LETTER),
        PageTemplate(id="landscape", frames=[land],
                     pagesize=landscape(LETTER)),
    ])

    story = []

    # ------------- Face sheet, portrait -------------
    if data.get("banner_text"):
        story.append(Paragraph(data["banner_text"], draftnote))
    if data.get("revision_note"):
        story.append(Paragraph(data["revision_note"], revnote))
    story.append(Paragraph("APPLICATION FOR PAYMENT", title))
    story.append(Paragraph("Contractor's progress billing summary", small))
    story.append(HRFlowable(width="100%", thickness=0.75, color=BORDER,
                            spaceAfter=8))

    period_txt = "%s to %s" % (data["period_from"], data["period_to"])
    hdr_rows = [
        [Paragraph("Owner:", lab), Paragraph(data["owner"], val),
         Paragraph("Application No.:", lab),
         Paragraph(str(data["application_no"]), val)],
        [Paragraph("Contractor:", lab),
         Paragraph(data["contractor"], val),
         Paragraph("Application Date:", lab),
         Paragraph(data["application_date"], val)],
        [Paragraph("Project:", lab), Paragraph(data["project"], val),
         Paragraph("Period:", lab), Paragraph(period_txt, val)],
        [Paragraph("Engineer:", lab),
         Paragraph(data["via_engineer"], val),
         Paragraph("Invoice No.:", lab),
         Paragraph(data["invoice_no"], val)],
        [Paragraph("Contract scope:", lab),
         Paragraph(data["contract_for"], val),
         Paragraph("Contract Date:", lab),
         Paragraph(data["contract_date"], val)],
    ]
    t = Table(hdr_rows, colWidths=[1.15 * inch, 3.35 * inch, 1.1 * inch,
                                   1.5 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("PAYMENT SUMMARY", h1))
    prev_note = data.get("previous_certificates_note", "")
    line7_label = "Less amounts from previous applications" + (
        " (%s)" % prev_note if prev_note else "")
    sum_rows = [
        ["1.", "Original contract amount", money(calc["line1"])],
        ["2.", "Net change from approved change orders",
         money(calc["line2"])],
        ["3.", "Contract amount to date (1 + 2)", money(calc["line3"])],
        ["4.", "Work completed and materials stored to date "
         "(column G total)", money(calc["gt"])],
        ["5a.", "Retainage held: %s of completed work (%s)" %
         (rp, money(calc["work_cum"])), money(calc["ret_5a"])],
        ["5b.", "Retainage held: %s of stored materials (%s)" %
         (rp, money(calc["stored_cum"])), money(calc["ret_5b"])],
        ["5.", "Total retainage held", money(calc["ret_t"])],
        ["6.", "Earned to date, less retainage (4 - 5)",
         money(calc["earned"])],
        ["7.", line7_label, money(calc["prev"])],
        ["8.", "AMOUNT DUE THIS APPLICATION", money(calc["due"])],
        ["9.", "Remaining contract balance, including retainage (3 - 6)",
         money(calc["bal9"])],
    ]
    t2 = Table(sum_rows, colWidths=[0.45 * inch, 4.9 * inch, 1.5 * inch])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 7), (-1, 7), "Helvetica-Bold"),
        ("FONTNAME", (0, 9), (-1, 9), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("BACKGROUND", (0, 9), (-1, 9), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))

    co = calc["co"]
    co_rows = [
        ["CHANGE ORDERS", "ADDED", "DEDUCTED"],
        ["Approved in earlier periods", money(co["pa"]), money(co["pd"])],
        ["Approved this period", money(co["ta"]), money(co["td"])],
        ["TOTALS", money(co["add_t"]), money(co["ded_t"])],
        ["Net change from change orders", money(co["net"]), ""],
    ]
    t3 = Table(co_rows, colWidths=[3.85 * inch, 1.5 * inch, 1.5 * inch])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 6))

    if data.get("face_note"):
        story.append(Paragraph(data["face_note"], small))
        story.append(Spacer(1, 6))

    story.append(Paragraph(CERTIFICATION, body))
    story.append(Spacer(1, 14))
    story.append(Paragraph(CONTRACTOR_SIGN_LINE, body))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Checked by: %s   Date: ______________" %
                           data["verified_by"], body))

    # ------------- Schedule of Values continuation, landscape -------------
    story.append(NextPageTemplate("landscape"))
    story.append(PageBreak())
    if data.get("banner_text"):
        story.append(Paragraph(data["banner_text"], draftnote))
    story.append(Paragraph("SCHEDULE OF VALUES CONTINUATION", title))
    sub_parts = [
        "Application No. %s" % data["application_no"],
        "Period %s" % period_txt,
        "%s, %s" % (data["project_short"], data["contract_ref"]),
    ]
    if data.get("revision_tag"):
        sub_parts.append(data["revision_tag"])
    sub_parts.append("Amounts stated to two decimal places")
    story.append(Paragraph("  |  ".join(sub_parts), small))
    story.append(Spacer(1, 4))

    hdr = ["ITEM", "WORK DESCRIPTION", "SCHEDULED\nVALUE (C)",
           "PREVIOUSLY\nBILLED (D)", "THIS\nPERIOD (E)",
           "STORED\nMATERIAL (F)", "COMPLETED +\nSTORED (G)",
           "%\n(G/C)", "LEFT TO\nFINISH (C-G)",
           "RETAINAGE\n(G x %s)" % rp]
    rows = [hdr]
    stored_rows = []
    highlight = set(data.get("highlight_this_period_items", []) or [])
    hi_rows = []
    for i, l in enumerate(calc["lines"], start=1):
        rows.append([
            l["item"], l["desc"], money_dash(l["c"]), money_dash(l["d"]),
            money_dash(l["e"]), money_dash(l["f"]), money_dash(l["g"]),
            pct_cell(l["g"], l["c"]), money_dash(l["bal"]),
            money_dash(l["ret"]),
        ])
        if l["f"] > EPS:
            stored_rows.append(i)
        if l["item"] in highlight:
            hi_rows.append(i)
    rows.append([
        "", "GRAND TOTALS", money(calc["ct"]), money(calc["dt"]),
        money(calc["et"]), money(calc["ft"]), money(calc["gt"]),
        pct_cell(calc["gt"], calc["ct"]),
        money(r2(calc["ct"] - calc["gt"])), money(calc["ret_t"]),
    ])

    colw = [0.62, 1.95, 0.92, 1.08, 0.88, 0.92, 1.12, 0.55, 0.98, 0.88]
    t4 = Table(rows, colWidths=[w * inch for w in colw], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.6),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for r in stored_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), GREEN))
    for r in hi_rows:
        style.append(("TEXTCOLOR", (4, r), (4, r), RED))
        style.append(("FONTNAME", (4, r), (4, r), "Helvetica-Bold"))
    t4.setStyle(TableStyle(style))
    story.append(t4)
    story.append(Spacer(1, 6))

    small_land = ParagraphStyle("small_land", parent=small)
    for n in data.get("continuation_notes", []) or []:
        story.append(Paragraph("* " + n, small_land))

    doc.build(story)


# ---------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description="Build a pay application PDF.")
    ap.add_argument("data", nargs="?",
                    default=os.path.join(HERE, "sample_data.json"),
                    help="job data JSON (default: sample_data.json here)")
    ap.add_argument("output_dir", nargs="?",
                    default=os.path.join(HERE, "_sample_output"),
                    help="output folder (default: _sample_output here)")
    ap.add_argument("--company", default=DEFAULT_COMPANY,
                    help="company config JSON (default: "
                         "template-library/company.example.json)")
    args = ap.parse_args(argv[1:])

    company = load_company(args.company)
    data = load_data(args.data, company)
    out_dir = args.output_dir

    calc = compute(data)

    basename = data.get("output_basename") or (
        "%s_Pay_Application_%03d_%s_%s.pdf" % (
            data["project_slug"], int(data["application_no"]),
            data["status_slug"], data["application_date_iso"]))
    out_path = os.path.join(out_dir, basename)
    os.makedirs(out_dir, exist_ok=True)

    build(data, calc, out_path, company)

    print("Wrote", out_path)
    print("C=%s  D=%s  E=%s  F=%s  G=%s" % (
        money(calc["ct"]), money(calc["dt"]), money(calc["et"]),
        money(calc["ft"]), money(calc["gt"])))
    print("5a=%s  5b=%s  ret=%s  earned=%s  due=%s  bal9=%s" % (
        money(calc["ret_5a"]), money(calc["ret_5b"]), money(calc["ret_t"]),
        money(calc["earned"]), money(calc["due"]), money(calc["bal9"])))
    print("All cross-foot checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
