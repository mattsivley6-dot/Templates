# Pay Application (Application for Payment with Schedule of Values continuation)

## Purpose and when to use
Monthly progress-billing package a contractor submits to an owner on a lump-sum construction contract. It is an original, plain-language progress billing form, not a copy of any published standard form: a portrait face sheet ("Application for Payment") that summarizes the contract amount, completed and stored work, retainage, previous applications and the amount due now, plus a landscape Schedule of Values continuation sheet that lists every SOV line with columns C through G, percent complete, balance to finish and per-line retainage. Use it whenever a pay app must be produced or revised in-house (your billing system is not available, the engineer wants corrections fast, or you need a draft for internal review before signing). Every dollar figure on the face sheet is recomputed from the SOV lines, and the script refuses to build if anything fails to cross-foot.

If the owner's contract requires a specific standard form, use that form and use this PDF to back-check its numbers.

## Output spec
- Format: PDF (reportlab platypus, BaseDocTemplate with two page templates)
- Page size: US Letter. Face sheet pages portrait (612 x 792 pt); continuation sheet pages landscape (792 x 612 pt)
- Margins: portrait frame 0.7 in left/right, 0.6 in top/bottom; landscape frame 0.45 in all around
- Fonts: Helvetica family only. Title 16 pt Helvetica-Bold; section header 11 pt Helvetica-Bold; body 9.5 pt Helvetica; header-block labels/values 8 pt; small italic notes 8.5 pt Helvetica-Oblique; banner 11 pt Helvetica-Bold; revision note 8.5 pt Helvetica-Bold; continuation table 7.6 pt; change order table 8.5 pt
- Colors: primary color from the company config `brand.primary_color` (titles, labels, table header bars; falls back to #1F3A5F), light blue fill #E8EEF5 (grand totals row and AMOUNT DUE row), grey #666666 (italic notes), border #B8C5D6 (all grid lines and the horizontal rule), green #E4F0E4 (stored-material row highlight), red #B00020 (banner and changed-cell highlight)
- Header/footer: none. The banner line (if any) is the first flowable on the face sheet and repeats at the top of the continuation sheet. No page numbers. No logo.
- Money format: face sheet always shows dollars ($0.00 for zero); continuation cells show "-" for zero. Negative values render as -$1,234.56. Percent cells show "-" when G is zero, else two decimals ("33.33%").
- PDF metadata: title = doc_title (default "{project_short} Application for Payment No. {application_no}"), author = `pdf_author` from the data file, else the company config `legal_name`. invariant=1 so identical data gives byte-identical PDFs.

## Company config
The script reads company fields from `template-library/company.example.json` (two folders up from this one) unless you pass `--company path/to/your_company.json`. Copy the example, fill in your own values and point `--company` at it. Fields used here:

| config key | used for |
|---|---|
| legal_name | default contractor line, default PDF author, `{legal_name}` token |
| address_line1, city_state_zip | default contractor line |
| pm_name, pm_title | default "Checked by" line |
| brand.primary_color | titles, labels, table header bars |

Any string in the data file may also contain company tokens, filled from the config: `{legal_name}`, `{dba}`, `{address_line1}`, `{city_state_zip}`, `{phone}`, `{email}`, `{website}`, `{license}`, `{pm_name}`, `{pm_title}`, `{pm_phone}`, `{pm_email}`. Unknown tokens are left as typed.

## Layout walkthrough
Page 1 (portrait face sheet, top to bottom):
1. Optional banner line, centered, 11 pt bold red: e.g. "DRAFT FOR INTERNAL REVIEW - NOT FOR SUBMISSION" (from banner_text; omitted entirely if key absent).
2. Optional revision note, centered, 8.5 pt bold primary color, one to two lines (from revision_note).
3. Title "APPLICATION FOR PAYMENT", centered, 16 pt bold primary color.
4. Subtitle "Contractor's progress billing summary", 8.5 pt grey italic, left-aligned.
5. Full-width horizontal rule, 0.75 pt, border color #B8C5D6.
6. Header block: borderless 5-row x 4-column table (col widths 1.15 / 3.35 / 1.1 / 1.5 in). Left pair = bold 8 pt label + 8 pt value, right pair same. Rows: Owner / Application No.; Contractor / Application Date; Project / Period ("{period_from} to {period_to}"); Engineer / Invoice No.; Contract scope / Contract Date. Top-aligned, 3 pt bottom padding.
7. Section header "PAYMENT SUMMARY", 11 pt bold.
8. Summary table, 11 rows, 3 columns (0.45 / 4.9 / 1.5 in), full grid 0.4 pt border color, 9.5 pt, amounts right-aligned. Rows numbered 1., 2., 3., 4., 5a., 5b., 5., 6., 7., 8., 9. Row 6 and row 8 in bold; row 8 (AMOUNT DUE THIS APPLICATION) has light blue #E8EEF5 background. 5a/5b labels embed the retainage percent and the completed-work and stored-material bases in parentheses.
9. Change order table, 5 rows, 3 columns (3.85 / 1.5 / 1.5 in), 8.5 pt. Header row "CHANGE ORDERS | ADDED | DEDUCTED" with primary-color background and white bold text; body rows: earlier periods, this period, TOTALS, net change (net amount in ADDED column, DEDUCTED cell blank).
10. Optional face note paragraph, 8.5 pt grey italic (from face_note; e.g. a pending-PCO explanation).
11. Contractor's statement paragraph, 9.5 pt body text (fixed wording below).
12. Contractor signature line with date blank (fixed wording below). If the story overflows, this and the next item flow onto a second portrait page.
13. "Checked by: {verified_by}   Date: ______________", 9.5 pt.

Next page (landscape continuation sheet; page number varies with overflow):
1. Optional banner line repeated (same style as face sheet).
2. Title "SCHEDULE OF VALUES CONTINUATION", centered, 16 pt bold primary color.
3. Subtitle line, 8.5 pt grey italic, segments joined by "  |  ": "Application No. {n}", "Period {from} to {to}", "{project_short}, {contract_ref}", optional "{revision_tag}", "Amounts stated to two decimal places".
4. SOV table, one row per line item plus header plus GRAND TOTALS. Column widths in inches: 0.62, 1.95, 0.92, 1.08, 0.88, 0.92, 1.12, 0.55, 0.98, 0.88. Header row primary-color background, white bold, two-line captions (see Fixed wording). Body 7.6 pt, columns C onward right-aligned, 0.35 pt grid, header repeats if the table breaks across pages. Rows with stored material (F > 0) get the green #E4F0E4 background across the full row. Items listed in highlight_this_period_items get their THIS PERIOD (E) cell in bold red. Grand totals row: bold, light blue background, all six money columns plus overall percent and total retainage.
5. Bulleted notes, 8.5 pt grey italic, each prefixed "* " (from continuation_notes). Overflow flows to another landscape page.

Arithmetic (all recomputed by the script, never typed): per line G = D + E + F, balance = C - G, retainage = round(G x rate, 2). Grand-total retainage is the sum of per-line rounded retainage so the continuation column foots exactly to the face sheet. Face sheet: line 3 = column C total; line 2 = net change orders; line 1 = line 3 - line 2; line 4 = column G total; 5a = rate x (G total - cumulative stored), 5b = rate x cumulative stored, with 5a nudged by at most 2 cents so 5a + 5b equals the per-line footing exactly; line 6 = 4 - 5; line 8 = 6 - 7; line 9 = 3 - 6. The build aborts with a clear message if any check fails.

## Placeholders
All example values are fictional.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| owner | string | yes | "Sample ISD, Anytown, TX 75000" | Owner value, name and address in one string |
| contractor | string | no | "{legal_name}, {address_line1}, {city_state_zip}" | Contractor value; defaults to the company config legal name and address |
| project | string | yes | "Sample Elementary School HVAC Replacement, 200 Example Avenue, Anytown, TX 75001" | Project value with address |
| project_short | string | yes | "Sample Elementary School" | used in continuation subtitle and default PDF title |
| project_slug | string | yes | "Sample_ES" | filename-safe short name for the output file |
| via_engineer | string | yes | "Sample Engineering, Inc. (Alex Poe, PE)" | Engineer value |
| contract_for | string | yes | "HVAC Replacement, Project 2026-0001" | Contract scope value |
| contract_ref | string | yes | "Project 2026-0001" | short contract reference for continuation subtitle |
| contract_date | string | yes | "January 15, 2026" | printed as-is |
| application_no | integer | yes | 2 | zero-padded to 3 digits in the filename |
| application_date | string | yes | "03/31/2026 (set to actual signing date)" | printed as-is; parenthetical optional |
| application_date_iso | string | yes | "2026-03-31" | YYYY-MM-DD, used only in the output filename |
| period_from | string | yes | "03/01/2026" | MM/DD/YYYY |
| period_to | string | yes | "03/31/2026" | MM/DD/YYYY; should match the owner's billing cutoff |
| invoice_no | string | yes | "TBD" | printed as-is; your billing system's invoice number |
| retainage_pct | number | yes | 5 | percent, not fraction; drives 5a/5b labels, the retainage column header and all retainage math. Use the rate in your contract. |
| previous_certificates | number | yes | 28500.00 | face sheet line 7 (amounts from previous applications); 0.0 on Application No. 1 |
| previous_certificates_note | string | no | "Application No. 1" | appended in parentheses to the line 7 label |
| materials_stored_cumulative | number | no | 60000.00 | cumulative stored basis for 5b; defaults to the column F total; can exceed column F when previously stored material is still on site |
| original_contract_sum | number | no | 300000.00 | optional guard; build fails if it does not equal column C total minus net change orders |
| change_orders | object | no | {"previous_additions": 0.0, "previous_deductions": 0.0, "this_month_additions": 0.0, "this_month_deductions": 0.0} | all four keys optional, default 0.0; drives the change order table and face sheet line 2 |
| sov_lines | array of objects | yes | see sample_data.json | one object per SOV line, in print order |
| sov_lines[].item | string | yes | "SOV 0004" | item number column |
| sov_lines[].description | string | yes | "Div 23 - HVAC Equipment" | description column |
| sov_lines[].scheduled_value | number | yes | 100000.00 | column C |
| sov_lines[].previous | number | yes | 0.0 | column D, cumulative through prior application of record |
| sov_lines[].this_period | number | yes | 0.0 | column E |
| sov_lines[].stored | number | yes | 50000.00 | column F, materials presently stored this application |
| highlight_this_period_items | array of strings | no | ["SOV 0006"] | item numbers whose THIS PERIOD cell prints bold red (flag a revised line) |
| banner_text | string | no | "DRAFT FOR INTERNAL REVIEW - NOT FOR SUBMISSION" | red centered banner on both sheets; omit for a clean submission copy |
| revision_note | string | no | "Numbers checked 03/31/2026 against the SOV and sub invoices." | bold note under the banner, face sheet only |
| revision_tag | string | no | "Rev. 03/30/2026" | extra segment in the continuation subtitle |
| face_note | string | no | "Note: PCO-001 is pending owner and engineer signature and is not included in this application." | italic paragraph between the change order table and the contractor's statement |
| continuation_notes | array of strings | no | see sample_data.json | printed under the continuation table, each prefixed "* " |
| verified_by | string | no | "{pm_name}, {pm_title}" | Checked by line; defaults to the company config PM name and title |
| status_slug | string | yes | "DRAFT" | filename token, e.g. DRAFT, FINAL, REVISED |
| output_basename | string | no | "Sample_ES_PA2_custom.pdf" | overrides the whole output filename |
| doc_title | string | no | "Sample ES Application for Payment No. 2" | overrides PDF metadata title |
| pdf_author | string | no | "Example Mechanical, LLC" | overrides PDF metadata author (default: company legal_name) |

## Fixed wording
- Face sheet title: "APPLICATION FOR PAYMENT"
- Face sheet subtitle: "Contractor's progress billing summary"
- Header labels: "Owner:", "Contractor:", "Project:", "Engineer:", "Contract scope:", "Application No.:", "Application Date:", "Period:", "Invoice No.:", "Contract Date:"
- Section header: "PAYMENT SUMMARY"
- Summary row labels: "Original contract amount"; "Net change from approved change orders"; "Contract amount to date (1 + 2)"; "Work completed and materials stored to date (column G total)"; "Retainage held: {rate} of completed work ({amount})"; "Retainage held: {rate} of stored materials ({amount})"; "Total retainage held"; "Earned to date, less retainage (4 - 5)"; "Less amounts from previous applications ({note})"; "AMOUNT DUE THIS APPLICATION"; "Remaining contract balance, including retainage (3 - 6)"
- Change order table: "CHANGE ORDERS", "ADDED", "DEDUCTED", "Approved in earlier periods", "Approved this period", "TOTALS", "Net change from change orders"
- Contractor's statement: "Contractor's statement: By signing below, the contractor confirms, based on what it knows today, that the amount due shown above is payable now, that the work billed here matches the contract, and that money the owner paid on earlier applications has been passed on to the subcontractors and suppliers who did that work." Check this against your contract; if the owner requires specific certification language, put that language in your copy of the script.
- Signature block: "Signed for the contractor: ______________________________   Date: ______________ (have the signature notarized if the owner requires it)" and "Checked by: {verified_by}   Date: ______________"
- Continuation title: "SCHEDULE OF VALUES CONTINUATION"
- Continuation subtitle tail: "Amounts stated to two decimal places"
- Continuation column headers: "ITEM", "WORK DESCRIPTION", "SCHEDULED VALUE (C)", "PREVIOUSLY BILLED (D)", "THIS PERIOD (E)", "STORED MATERIAL (F)", "COMPLETED + STORED (G)", "% (G/C)", "LEFT TO FINISH (C-G)", "RETAINAGE (G x {rate})"
- Totals row label: "GRAND TOTALS"
- No em dashes or en dashes anywhere in this document; use hyphens, commas or periods.

## How to build
    python build_pay_app.py [data.json] [output_dir] [--company company.json]

- data.json defaults to sample_data.json next to the script; output_dir defaults to `_sample_output` next to the script; `--company` defaults to `../../company.example.json`.
- Example with your own files: `python build_pay_app.py my_job/pay_app_03.json my_job/out --company my_company.json`
- Expected output filename: {project_slug}_Pay_Application_{application_no as 3 digits}_{status_slug}_{application_date_iso}.pdf, e.g. Sample_ES_Pay_Application_002_DRAFT_2026-03-31.pdf (override with output_basename).
- The script prints the column totals and face-sheet results (5a, 5b, retainage, earned, due, balance) and exits nonzero with a "DATA/CROSS-FOOT ERROR" message if the data does not foot. Always eyeball the printed amount due against expectations before sending.
- Output is a ready-to-print PDF. Print and sign the face sheet (notarize if the owner requires it), then merge backup exhibits (photos, sub invoices, conditional lien waivers) behind it with PyMuPDF or your PDF editor.
- Requires: Python 3, reportlab.

## Known variations
- DRAFT vs FINAL: usually only banner_text, revision_note and the continuation notes change. A draft might use the banner "DRAFT FOR INTERNAL REVIEW - NOT FOR SUBMISSION"; a final might use "FINAL - PRINT, SIGN, AND NOTARIZE BEFORE SUBMISSION" plus a short numbers-checked revision_note. For a clean submission copy omit banner_text and revision_note entirely.
- The red bold THIS PERIOD highlight (highlight_this_period_items) is for flagging a revised line on a resubmittal; omit the key for a normal build.
- Retainage rates differ by owner and contract; set retainage_pct to your contract's rate (the labels and column header follow it automatically).
- SOV granularity is up to you: a short roll-up (equipment, install, subs, controls, electrical, contingency) or a detailed line-by-line schedule both work, since sov_lines is any length. Use whatever schedule of values the owner approved.
- When change orders exist, add them as SOV lines (so column C foots to the contract amount to date) and fill change_orders; line 1 is derived by subtracting the net change from the column C total.
- Cumulative stored (materials_stored_cumulative) can exceed the current column F when material stored in an earlier period is still on site; on a first application it usually equals the column F total (the default).
- Many engineers require dated photo backup for stored material. Keep a continuation note saying photos are attached, and merge the photo exhibit behind the pay app before submission.
- If your billing system produces the official pay app on a different form, this PDF still carries identical numbers and can back-check it.
