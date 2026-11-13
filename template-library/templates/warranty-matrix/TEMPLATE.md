# Warranty Matrix + Warranty Binder

## Purpose and when to use

Two closeout deliverables for a mechanical job, built at substantial
completion / system startup and filed with the job's startup and warranty
records:

1. **Warranty Summary Matrix**: a one page (usually) landscape table that
   lists every warranted item or system on the job, who stands behind it,
   the warranty type, term, start and end dates, and where to make a claim.
   The start date is the system startup date; every end date is start plus
   term. Hand it to the owner so they never have to dig through
   manufacturer paperwork to know who to call.
2. **Warranty Binder**: a single merged PDF that packages the actual
   manufacturer warranty documents behind a generated cover page with
   project contacts, the start-up date, and a clickable Table of Contents.
   Every merged page gets a blue "Back to Table of Contents" link at the
   bottom left.

Build the matrix for every job. Build the binder when the owner wants the
backing paper in one navigable file (chiller replacements, plant upgrades,
any job with 3+ manufacturers). The matrix and binder should agree: every
matrix row that cites a manufacturer limited warranty should have its
warranty document as a binder section, and the terms on the matrix must
match the terms in the TOC section titles.

Note on sharing: a finished binder contains the manufacturers' own warranty
documents. Give it to the owner; do not publish it.

## Company config

Company data is never hard-coded. The script reads it from the
template-library company config:

- `--company <path>` selects the file. Default:
  `template-library/company.example.json` (two folders up from this
  script). Copy that file, fill in your own values, and pass it with
  `--company`.
- Fields used:
  - `legal_name`: PDF author on both outputs (unless `meta.author` is set)
    and the matrix "Mechanical Contractor" line (unless `matrix.contractor`
    is set).
- `logo_path`, `signature_path` and brand colors are not used; the matrix is
  gray and black, and the binder accent comes from `binder.accent_hex`.

## Output spec

**Warranty Matrix.pdf** (reportlab, native PDF, no Word needed)

- Page size: letter LANDSCAPE, 11 x 8.5 in (792 x 612 pt).
- Margins: title block starts 42 pt (0.58 in) from the left edge, title
  baseline 56 pt (0.78 in) from the top. The table itself bleeds almost to
  the page edges, x = 1 pt to x = 791 pt. Table bottom limit 571 pt from
  top (41 pt bottom margin).
- Fonts (Helvetica family, Arial metric equivalent):
  - Title "WARRANTY SUMMARY MATRIX": Helvetica-Bold 14
  - Three meta lines under the title: Helvetica 9, baselines 79/91/103 pt
  - Column header row: Helvetica-Bold 8
  - Body cells: Helvetica 8, 11 pt line height
- Colors (hex): header row fill #D3D3D3, all grid lines #808080 at 0.5 pt,
  all text #000000.
- Header/footer: none. No page numbers.

**Warranty Binder.pdf** (reportlab cover + PyMuPDF merge, native PDF)

- Cover and TOC pages: letter PORTRAIT, 8.5 x 11 in (612 x 792 pt),
  1 in margins (left margin 72 pt, bottom limit 720 pt).
- Fonts: Helvetica family. Title 16 bold, section headings ("Start-Up
  Date", "Table of Contents") 14 bold, everything else 12.
- Colors: accent #4F81BD by default (title, 14 pt headings, startup date
  line, TOC entry titles), all other text #000000, back links #0000FF
  Helvetica 8.
- Merged manufacturer pages keep their own page sizes (letter, A4 and
  legal all work); the back link is placed relative to each page's own
  bottom edge.
- Determinism: both PDFs are identical run to run. reportlab
  Canvas(..., invariant=1); PyMuPDF save with no_new_id=True; binder
  creationDate/modDate come from meta.pdf_date; no clock reads anywhere.

## Layout walkthrough

**Matrix, page 1** (all y values measured from the TOP of the page):

1. Title "WARRANTY SUMMARY MATRIX", Helvetica-Bold 14 black, baseline at
   y=56, x=42.
2. Three meta lines, Helvetica 9 black, x=42, baselines y=79, 91, 103:
   - "Project: " + matrix.project
   - "Warranty Commencement Date (System Startup): " + matrix.commencement
   - "Mechanical Contractor: " + matrix.contractor (default: company
     `legal_name`)
3. Table, top edge y=122. Column x edges (7 columns):
   1 | 166 | 306 | 441 | 511 | 586 | 661 | 791.
   Cell text is inset 6 pt from the column's left edge; usable text width
   per column is column width minus 12.
   - Header row: 23 pt tall, fill #D3D3D3, Helvetica-Bold 8 black,
     baseline 14 pt below the row top. Labels: ITEM / SYSTEM,
     MANUFACTURER / PROVIDER, WARRANTY TYPE, TERM, START DATE, END DATE,
     CLAIM CONTACT.
   - Data rows: Helvetica 8 black. First baseline 14 pt below row top,
     11 pt per additional line. Row height = 11 x (max wrapped line count
     across the 7 cells) + 12. The ITEM / SYSTEM cell renders `item`
     word wrapped, then `item_detail` (the parenthetical model or tag
     list) starting on its own line. Claim contact supports embedded \n.
     Words longer than the cell (long URLs) break mid word.
   - Grid: every row boundary and every column edge stroked #808080 at
     0.5 pt, drawn over the header fill.
4. If rows overflow past y=571, the table continues on a new page with the
   gray header row repeated at y=41. About ten rows fit on one page.

**Binder** (assembly order and cover flow):

1. Cover page 1, generated: project title (Helvetica-Bold 16, accent
   color) baseline y=111, x=72. Then "Project Contacts" (bold 12 black),
   then one block per contact group: heading (bold 12) followed by four
   lines "Company Name: ...", "Contact Person: ...", "Phone Number: ...",
   "Email Address: ..." at 13.8 pt line steps, 9.1 pt extra between
   groups. Then "Start-Up Date" (bold 14 accent, 27.8 pt gap before it),
   the startup date line (12 accent, clickable), then "Table of Contents"
   (bold 14 accent) and the numbered entries: number at x=84 (black),
   title at x=108 (12 accent, clickable, wraps at x=540), sub items as
   bullet lines (bullet at x=120, text at x=144, black). TOC lines step
   15.6 pt with 13.8 pt extra between entries. Content past y=720 flows
   onto continuation pages starting at y=83.
2. Merge order (PyMuPDF): generated cover pages first, then every
   `front_attachments` PDF in listed order (startup or claim field reports
   that are not TOC numbered), then every `sections` PDF in listed order.
3. Links added after the merge:
   - each TOC title rect -> GOTO first page of its merged section
   - the startup date rect -> GOTO first front attachment (or first
     section when there are no front attachments)
   - every merged content page gets "Back to Table of Contents" in
     Helvetica 8 blue at x=72, baseline 31 pt above that page's bottom
     edge, with a GOTO link back to page 1.
4. Metadata (title, author, subject, creationDate, modDate) set from the
   JSON and the company config, then saved with garbage=4, deflate=True,
   no_new_id=True.

## Placeholders

All example values are invented (see `sample_data.json`).

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| meta.author | string | no | Example Mechanical, LLC | PDF Author on both outputs; defaults to the company config `legal_name` |
| meta.pdf_date | string | no | D:20260701120000-06'00' | binder creationDate/modDate; matrix date is fixed by invariant=1 |
| matrix.output_name | string | no | Warranty Matrix.pdf | output filename, default shown |
| matrix.project | string | yes | Sample Elementary School HVAC Replacement - Sample ISD | meta line 1 and PDF title/subject |
| matrix.commencement | string | yes | June 30, 2026 | prose startup date, meta line 2 |
| matrix.contractor | string | no | Example Mechanical, LLC | meta line 3; defaults to the company config `legal_name` |
| matrix.rows | array | yes | see sample | one table row each, top to bottom; your own workmanship row first by convention |
| matrix.rows[].item | string | yes | HVAC System - Overall Installation | ITEM / SYSTEM cell, word wraps |
| matrix.rows[].item_detail | string | no | (P-1, P-2) | parenthetical model or tag list, starts on its own line under item |
| matrix.rows[].manufacturer | string | yes | Sample Pump Co. | MANUFACTURER / PROVIDER cell |
| matrix.rows[].warranty_type | string | yes | Manufacturer Limited Warranty | your own row uses "Contractor Workmanship Warranty" |
| matrix.rows[].term | string | yes | 24 Months | free text: "1 Year", "5 Years", "24 Months" all work |
| matrix.rows[].start_date | string | yes | 06/30/2026 | mm/dd/yyyy, usually the same startup date on every row |
| matrix.rows[].end_date | string | yes | 06/30/2028 | start plus term, computed by the author, not the script |
| matrix.rows[].claim_contact | string | yes | Example Mechanical\n(555) 010-0100 | URL, phone, or phrase; \n forces a line break |
| binder | object | no | see sample | omit entirely to build the matrix only |
| binder.output_name | string | no | Warranty Binder.pdf | output filename, default shown |
| binder.title | string | yes | Sample Elementary School HVAC Replacement | cover title and PDF title/subject |
| binder.accent_hex | string | no | 4F81BD | heading/TOC accent color, default shown |
| binder.contacts | array | no | see sample | contact groups on the cover |
| binder.contacts[].heading | string | yes | Mechanical Contractor | bold group heading |
| binder.contacts[].company | string | yes | Example Mechanical, LLC | rendered as "Company Name: ..." |
| binder.contacts[].contact | string | yes | Pat Doe | rendered as "Contact Person: ..." |
| binder.contacts[].phone | string | yes | (555) 010-0100 (Office); (555) 010-0101 (Mobile) | rendered as "Phone Number: ..." |
| binder.contacts[].email | string | yes | pat.doe@example.com | rendered as "Email Address: ..." |
| binder.startup_date | string | no | June 30, 2026 | prose date under "Start-Up Date"; links to the first front attachment |
| binder.front_attachments | array | no | see sample | startup or claim field reports merged after the cover, before section 1, NOT in the TOC |
| binder.front_attachments[].label | string | no | Equipment startup report | for the human reading the JSON; not rendered |
| binder.front_attachments[].path | string | yes | sample_docs/startup_report_rtu.pdf | absolute path, or relative to the JSON file |
| binder.sections | array | yes | see sample | numbered TOC entries, merged in listed order |
| binder.sections[].number | string | yes | 2 | rendered as "2." in the TOC |
| binder.sections[].title | string | yes | Sample Pump Co. 24-Month Limited Warranty | clickable TOC title; put the term in the title |
| binder.sections[].subitems | array of strings | yes | ["Chilled Water Pump (P-1)"] | bullet lines under the title; use [] for none |
| binder.sections[].path | string | yes | sample_docs/pump_warranty.pdf | the manufacturer warranty PDF to merge; absolute or relative to the JSON file |

## Fixed wording

Baked into the script, identical on every job:

- Matrix title: "WARRANTY SUMMARY MATRIX"
- Matrix meta line prefixes: "Project: ",
  "Warranty Commencement Date (System Startup): ",
  "Mechanical Contractor: "
- Matrix column headers: "ITEM / SYSTEM", "MANUFACTURER / PROVIDER",
  "WARRANTY TYPE", "TERM", "START DATE", "END DATE", "CLAIM CONTACT"
- Binder cover: "Project Contacts", "Start-Up Date", "Table of Contents"
- Binder contact line labels: "Company Name: ", "Contact Person: ",
  "Phone Number: ", "Email Address: "
- Binder back link text: "Back to Table of Contents"

## How to build

```
python build_warranty_matrix.py [data.json] [out_dir] [--company path/to/company.json]
```

All arguments optional: data.json defaults to sample_data.json next to the
script, out_dir defaults to _sample_output next to the script, --company
defaults to `../../company.example.json`. For a real job:

```
python build_warranty_matrix.py "<job folder>/warranty_data.json" "<job folder>/Startup and Warranty" --company "<path>/my_company.json"
```

Expected output files in out_dir:

- "Warranty Matrix.pdf" (or matrix.output_name), always
- "Warranty Binder.pdf" (or binder.output_name), only when the JSON has a
  binder section; the script fails loudly listing any binder source PDF
  it cannot find

The sample binder merges gray placeholder PDFs from `sample_docs\`. Replace
them with the real manufacturer warranty documents for your job.

The script needs reportlab and PyMuPDF (import fitz) only; output is
native PDF, Word is never involved. It exits nonzero on em/en dashes in
the JSON (house rule), missing required keys, or missing source PDFs.
Rebuilding with the same JSON gives identical files.

## Known variations

- The matrix header row is LIGHT GRAY (#D3D3D3) with black text on
  purpose, so it prints clean on any office printer. It does not use the
  company brand colors.
- The table bleeds to x=1..791 while the title block sits at a normal
  margin. This is deliberate; keep it.
- Term strings are free text on purpose: one table can mix "1 Year",
  "5 Years", and "24 Months".
- Always render final TOC titles directly in the JSON. Do not patch titles
  on the finished PDF.
- TOC links always land on each section's true first page; the startup
  date links to the first front attachment.
- front_attachments is how un-numbered startup and claim reports are
  modeled: merged before section 1 but absent from the TOC. Omit it on
  jobs with no field reports.
- A source PDF filename may contain curly quotes or other odd characters;
  keep them in the path (the filesystem name is what it is) but use plain
  straight quotes in the TOC title.
- Multi page matrix behavior repeats the header row at 41 pt from the top
  of continuation pages. About ten rows fit on one page.
