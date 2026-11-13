# PCO (Proposed Change Order) package

## Purpose and when to use

The PCO package is the document the contractor sends the Engineer and Owner to price a change. One PDF holds everything the reviewer needs to sign: a narrative and justification page with the cost summary and sign-off lines, a fully broken out Scope and Cost Itemization (every trade: description, quantity, unit cost, total, labor by hours and rate), and the merged backup attachments (RFIs, engineer details, subcontractor proposals, notices).

Use it whenever you need to propose an add, a not-to-exceed cap, or a credit. One script and one JSON file build any PCO number for any job. Contract clause citations are plain text in the JSON (shown as `[clause]` in the sample), so any contract's numbering drops in cleanly. How you price the change (markup, overhead and profit, overtime, labor rates) follows your own contract and your own pricing method; the template only lays out the numbers you give it.

## Output spec

- Format: PDF (reportlab pages merged with attachment PDFs via PyMuPDF). No docx step, no Word needed.
- Page size: letter (8.5 x 11 in), portrait.
- Margins: top 0.7 in, bottom 0.6 in on every generated page. Left/right 0.85 in on the narrative page(s); left/right 0.7 in on the itemization page(s).
- Fonts (reportlab built-ins, metrically equivalent to Arial):
  - Title: Helvetica-Bold 16 pt, left aligned ("PROPOSED CHANGE ORDER | PCO-NNN").
  - Subtitle: Helvetica-Bold 11 pt, color #444444.
  - Section headings: Helvetica-Bold 11 pt, color #1a1a1a, 10 pt space before, 4 pt after.
  - Body: Helvetica 9.5 pt, 13 pt leading. Bullets same, left indent 14 pt, bullet char U+2022.
  - Notes (fine print): Helvetica 8.5 pt, 11 pt leading, color #333333.
  - Table cells: Helvetica 9 pt, 11.5 pt leading; bold cells Helvetica-Bold; money right aligned.
- Colors (hex): #444444 subtitle, #1a1a1a headings, #333333 note text and heavy table rules (0.8 pt), #dddddd light row rules (0.25 pt), #e9ecef table header row fill, #f6f6f6 total row fill, #f3f4f6 callout box fill, #9aa0a6 callout box border (0.6 pt).
- Header/footer: none. No page numbers. Each PDF part carries the metadata title from `meta.pdf_title`; the merged file gets the author from the company config (`legal_name`) and creation/mod dates from `meta.created`.
- House style: this document family is intentionally grayscale. No logo or brand color bars.
- Determinism: reportlab canvases run with invariant=1 and the script rewrites the PDF trailer /ID with a content hash, so identical JSON gives byte-identical PDFs. No datetime.now anywhere; every date comes from the JSON.

## Company config

Company fields come from `template-library/company.example.json` (or the file you pass with `--company`). Copy it, fill in your own company, and point `--company` at your copy.

Any string in the data file may contain `{{company.KEY}}`; the script replaces it with that key from the company config before building. Keys used by the sample: `{{company.legal_name}}`, `{{company.pm_name}}`, `{{company.pm_title}}`. The script also uses `legal_name` for the PDF author, `legal_name` as the default itemization contractor line, and `dba` (or `legal_name`) in the labor subtotal labels. An unknown token stops the build with an error.

## Layout walkthrough

The generated part of the package is two logical documents merged in order, then the attachments.

**Pages 1-2, Narrative (the page the three parties sign):**
1. Title line: "PROPOSED CHANGE ORDER  |  PCO-NNN" (Helvetica-Bold 16). Two nbsp on each side of the pipe.
2. Subtitle: one line naming the change, Helvetica-Bold 11 gray (e.g. "RTU-1 curb support repair (concealed roof deck condition)").
3. Header table, two columns (0.95 in bold label / 5.55 in value), no rules, 1 pt vertical padding: Project, Reference, Project #, Owner, Engineer, Contractor, Date. Order and count are data-driven.
4. 6 pt spacer, then the callout box: light gray fill #f3f4f6 with 0.6 pt border, same two-column geometry, 4/6 pt padding. Rows are normally Amount / Schedule / Funding; the Amount value opens with a bold dollar figure.
5. Numbered sections, each a heading plus bullets, paragraphs, notes, or a cost table. Typical add-PCO sequence: 1. WHAT WE FOUND, 2. THE FIX (Engineer directed), 3. COST (broken out), 4. SCHEDULE, 5. NOTES, then sign-offs, then 6. ATTACHED.
6. The narrative cost table: two columns (default 5.5 in label / 1.0 in amount), light 0.25 pt rules under every row, group header rows are bold with an empty amount cell, subtotal/total rows bold, the last row gets 0.8 pt rules above and below plus #f6f6f6 fill. Amounts can carry a small gray tag (7 pt) like "trues down to invoice". Credits render in parentheses.
7. SIGN OFFS block: heading (sample: "SIGN OFFS (all three sign before the changed work is billed)"), then one signature group per party: bold party line, a 47-underscore signature line with "Date: ____________________" to its right (4.2 in / 2.3 in columns), then the name and role line. The Engineer line appends checkbox text "[ ] Approve   [ ] Approve as noted   [ ] Reject". 4 pt spacer between parties.
8. Final "N. ATTACHED" section: one bullet listing every attachment in reading order.

**Pages 3-4, Scope and Cost Itemization (0.7 in side margins):**
1. Title "Scope and Cost Itemization (broken out)" + fixed subtitle + intro paragraph: "{project} | {PCO label} | {contractor}. {optional intro text} Labor rates: {foreman, lowercase} $NN.NN per hour, {tech, lowercase} $NN.NN per hour." Then 6 pt spacer.
2. A sequence of blocks, one per cost section, each usually heading + fine-print note + table:
   - Welder detail: three stacked tables. Materials (Item/Qty/Unit cost/Total, 3.9/0.75/0.95/1.0 in), labor (Crew/Men/Hours/Rate/Total, 3.35/0.7/0.7/0.85/1.0 in), then a summary (Materials/Labor/Trip charge/bold welder total, 5.6/1.0 in). Subtotals computed by the script.
   - Roofer breakout: Line/Type/Amount table (4.55/1.15/1.0 in), types are material/equipment/labor/markup, total row computed from the lines (must foot to the roofer's firm price).
   - Labor table (your own crew): Item/Task/Frmn hr/Tech hr/Labor/Matl/Total (0.4/3.35/0.62/0.6/0.72/0.62/0.72 in). Labor dollars are COMPUTED from hours x the rates in the JSON; subtotal row computed.
   - Crew loading grid (NTE PCOs): Day/Phase/Frmn hr/Tech hr/Fire watch hr/Billed hr (0.7/2.85/0.75/0.75/0.95/0.75 in); totals computed, fire watch total renders "NN (base)".
   - Credit labor table (deduct PCOs): Item/Scope of work (deleted)/Hours/Rate/Credit (0.4/3.85/0.6/0.75/0.9 in); credits computed as hours x rate and shown in parentheses.
   - Totals: a final Line/Type/Amount table titled "Totals" summarizing A/B/C lines with the grand total row.
   All tables share the look: #e9ecef header row, 0.25 pt #dddddd row rules, 0.8 pt #333333 rule above the total row, #f6f6f6 total fill.
3. Every table's header row and total-row labels are fixed wording (below); the line items are data.

**Pages 5+, Attachments:** the PDFs listed in `attachments`, merged as-is in order (engineer detail, RFI, sub proposals, notices, estimates). Missing files are skipped with a console warning.

## Placeholders

Keys are dotted paths into sample_data.json. "Blocks" arrays are ordered and render top to bottom. All example values are fake.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| meta.job_slug | string | yes | "Sample_Elementary" | Output filename prefix. |
| meta.pco_number | string | yes | "001" | Zero-padded three digits in filenames. |
| meta.file_slug | string | yes | "RTU-1" | Output filename suffix; keep native drawing-tag form. |
| meta.pdf_title | string | yes | "Sample Elementary PCO" | PDF metadata title. |
| meta.created | string | yes | "2026-03-02" | YYYY-MM-DD; becomes the PDF creation/mod date. Never use today's date automatically; use the PCO date. |
| meta.output_dir | string or null | no | null | null = _sample_output next to the script. |
| rates.foreman_name | string | yes | "Working Foreman" | Title case; the script lowercases it for prose. |
| rates.tech_name | string | yes | "Working Tech" | Same. |
| rates.foreman_rate | number | yes | [foreman rate], sample 100.00 | $/hr. Drives all computed labor. Use your own rate. |
| rates.tech_rate | number | yes | [tech rate], sample 75.00 | $/hr. Use your own rate. |
| narrative.pco_label | string | yes | "PCO-001" | Goes after the pipe in the title. |
| narrative.subtitle | string | yes | "RTU-1 curb support repair (concealed roof deck condition)" | One line. |
| narrative.header_rows | array of [label, value] | yes | [["Project:", "Sample Elementary School HVAC Replacement (Sample ISD)"], ...] | Rendered in order. Labels end with a colon. |
| narrative.callout_rows | array of [label, value] | no | [["Amount:", "<b>$10,000.00, firm.</b> ..."], ...] | Gray callout box. Values may use <b> and &nbsp; markup. |
| narrative.sections | array | yes | see sample | Each entry is {heading, blocks} or {"signoffs": true} to place the sign-off block. |
| narrative.sections[].heading | string | yes | "1. WHAT WE FOUND" | Numbered, ALL CAPS key phrase. |
| narrative.sections[].blocks[].type | string | yes | "bullet" | One of: bullet, para, note, spacer, cost_table. |
| narrative.sections[].blocks[].text | string | for text types | "We opened the roof at RTU-1 and found..." | Reportlab mini-HTML allowed (<b>, <font>). |
| ...blocks[].height | number | for spacer | 4 | Points. |
| ...cost_table.col_widths | [number, number] | no | [5.5, 1.0] | Inches. Widen the amount column (e.g. [5.05, 1.45]) to fit tags. |
| ...cost_table.padding | number | no | 2.5 | Row top/bottom padding pts. |
| ...cost_table.rows[].label | string | yes | "A1. Steel angle and new metal deck (welder subcontractor), itemized in the attachment" | |
| ...cost_table.rows[].amount | number | one of amount/hours/blank | 2500.00 | Explicit dollars. |
| ...cost_table.rows[].hours | object | one of amount/hours/blank | {"foreman": 10, "tech": 10, "material": 0.0} | Script computes foreman*rate + tech*rate + material so labor math cannot drift. |
| ...cost_table.rows[].blank | bool | no | true | Bold group-header row with empty amount cell. |
| ...cost_table.rows[].bold | bool | no | true | Subtotal/total rows. Last row automatically gets the total-row rules and fill. |
| ...cost_table.rows[].tag | string | no | "trues down to invoice" | Small 7 pt gray tag after the amount (NTE PCOs). |
| ...cost_table.rows[].paren | bool | no | true | Render the amount in parentheses (credits). |
| narrative.signoff_heading | string | yes | "SIGN OFFS (all three sign before the changed work is billed)" | |
| narrative.signoffs[].party | string | yes | "Contractor: {{company.legal_name}}" | Bold line above the signature rule. |
| narrative.signoffs[].name_role | string | yes | "{{company.pm_name}}, {{company.pm_title}}" | Under the rule. |
| narrative.signoffs[].extra | string | no | "[ ] Approve&nbsp;&nbsp; [ ] Approve as noted&nbsp;&nbsp; [ ] Reject" | Appended after the name (Engineer row). |
| itemization.enabled | bool | yes | true | false skips the itemization pages entirely. |
| itemization.project_short | string | yes | "Sample Elementary School" | First segment of the intro line. |
| itemization.pco_label | string | yes | "PCO-001 (RTU-1)" | Second segment. |
| itemization.contractor_line | string | no | "{{company.legal_name}}" | Third segment. Defaults to the company legal name. |
| itemization.intro | string | no | "Subcontractor and vendor lines are each firm's own price." | Optional sentence(s) after the first segment line. |
| itemization.blocks[].type | string | yes | "welder_detail" | One of: heading, note, para, spacer, welder_detail, roofer_breakout, labor_table, crew_grid, credit_labor_table, three_col. |
| ...heading/note/para .text | string | yes | "Section A1. Welder subcontractor: firm $2,500.00" | Headings carry the dollar figure formatted like $2,500.00. |
| ...welder_detail.materials | array of [item, qty, unit_cost, total] | yes | ["Steel angle, L3x3x1/4", "10 LF", 20.00, 200.00] | Qty is a string with the unit. |
| ...welder_detail.labor | array of [crew, men, hours, rate, total] | yes | ["Welders: cut and weld...", 2, 8.0, 100.00, 1600.00] | |
| ...welder_detail.trip | number | yes | 100.00 | Trip charge line. |
| ...welder_detail.total | number | yes | 2500.00 | Firm lump; script warns if materials+labor+trip do not foot. |
| ...roofer_breakout.title | string | yes | "Roofer cost, itemized (roofer proposal)" | |
| ...roofer_breakout.total_label | string | no | "Firm total (roofer cost)" | Default shown. |
| ...roofer_breakout.lines | array of [label, type, amount] | yes | ["Kettle and equipment", "equipment", 500.00] | type in {material, equipment, labor, markup}. Lines MUST sum to the roofer's firm price; the total row is computed. |
| ...labor_table.lines | array of [code, task, foreman_hr, tech_hr, material] | yes | ["C1", "Working Foreman: rig and assist...", 10, 0, 0.0] | Labor dollars computed from rates. Use integers for whole hours. |
| ...crew_grid.rows | array of [day, phase, foreman_hr, tech_hr, firewatch_hr] | yes | ["Day 1", "Protect and stage", 4, 8, 0] | Totals computed; billed = foreman + tech. |
| ...credit_labor_table.rows | array of [item_no, scope, hours, rate] | yes | ["1", "Set the meter: ...", 8, 75.00] | Credit computed = hours x rate, shown in parentheses. |
| ...credit_labor_table.total_label | string | no | "TOTAL {dba} labor (deduct)" | Default uses the company DBA. |
| ...three_col.rows | array of [label, type, amount] | yes | ["A1. Welder subcontractor, firm", "subcontract", 2500.00] | type is free text, e.g. subcontract, vendor, labor, material, equipment, engineering. |
| ...three_col.total_label | string | yes | "TOTAL (firm)" | Also "NOT TO EXCEED TOTAL". |
| ...three_col.total | number | yes | 10000.00 | Explicit; the script warns if the rows do not foot to it. |
| attachments | array of strings | no | ["backup/RFI-001.pdf"] | Paths absolute or relative to the data file, merged in order after the itemization. Missing files skipped with a warning, build still exits 0. |

HARD RULE: no em dashes or en dashes anywhere in the JSON; the script refuses to build if it finds one. Use commas, periods, or hyphens. Drawing tags keep native form (RTU-1, L3x3x1/4, W14x22). Pick one style for PCO and RFI numbers (PCO-001, RFI-001) and use it everywhere.

## Fixed wording

Baked into the script, never changes between jobs:

- Title prefix: "PROPOSED CHANGE ORDER  |  " (two nbsp each side of the pipe).
- Itemization title: "Scope and Cost Itemization (broken out)".
- Itemization subtitle: "Every trade broken out: description, quantity, unit cost, total, and labor by hours and rate".
- Itemization intro skeleton: "{project} | {PCO label} | {contractor}. {intro} Labor rates: {foreman, lowercase} {$rate} per hour, {tech, lowercase} {$rate} per hour."
- Table headers: "Line", "Type", "Amount", "Item", "Task", "Frmn hr", "Tech hr", "Labor", "Matl", "Total", "Qty", "Unit cost", "Crew", "Men", "Hours", "Rate", "Day", "Phase", "Fire watch hr", "Billed hr", "Scope of work (deleted)", "Credit".
- Welder tables: "Welder materials (itemized)", "Welder labor (men times hours times rate)", "Materials subtotal", "Labor subtotal", "Materials", "Labor", "Trip charge", "Welder total (firm lump, subcontractor proposal)".
- Labor table subtotal row: "Subtotal, {dba} labor".
- Crew grid total row: "Total" with fire watch shown as "NN (base)".
- Signature block: 47 underscores, "Date: ____________________".

Standard wording that lives in the JSON and can be reused on new jobs: the sign-off heading "SIGN OFFS (all three sign before the changed work is billed)"; the Engineer checkbox line "[ ] Approve   [ ] Approve as noted   [ ] Reject"; the callout Funding line naming the funding source and the contract clause; the cost table "TOTAL (firm)" row; the roofer total label "Firm total (roofer cost)".

## How to build

```
cd template-library/templates/pco
py -3 build_pco.py                                   (sample_data.json + company.example.json)
py -3 build_pco.py mydata.json                       (any data file)
py -3 build_pco.py mydata.json --company my_company.json
```

Output: `<meta.output_dir or _sample_output>/<job_slug>_PCO-<pco_number>_<file_slug>.pdf` (e.g. `Sample_Elementary_PCO-001_RTU-1.pdf`). Exit code 0 on success. The console prints computed footing checks (roofer total, labor subtotal) and warnings for missing attachments or numbers that do not foot; read them.

Requires: Python 3 with reportlab and PyMuPDF (fitz). No Word, no docx step.

## Known variations

- **PCO type changes the framing, not the layout.** Firm add: callout says "firm", totals row "TOTAL (firm)". Not-to-exceed: callout says "Not to exceed $X", cost table uses tags like "trues down to invoice" and "NN billed hrs", wider amount column [5.05, 1.45], totals row "NOT TO EXCEED TOTAL", and the itemization adds the crew loading grid. Credit: amounts in parentheses via "paren": true, sections become 1. WHAT CHANGED / 2. CREDIT / 3. NOTES, the Funding callout states the effect on the Contract Sum, and the itemization uses credit_labor_table only.
- **Section count and names vary.** Example add PCO: WHAT WE FOUND / THE FIX / COST / SCHEDULE / NOTES / ATTACHED. Example NTE PCO: WHY / COST / TIME / NOT INCLUDED (extra cost, only if it happens) / ATTACHED, with a fine-print note right before the sign-offs saying all parties sign (or approve by email) before work proceeds. Keep the pattern: numbered ALL-CAPS headings, bullets inside, sign-offs before the final ATTACHED section.
- **Callout rows:** usually 3 rows (Amount/Schedule/Funding); 2 rows (Amount/Schedule) is fine when funding is not in question.
- **Cost table padding:** 2.5 pt default; 3 pt is visually near-identical.
- **Itemization blocks are a la carte.** Firm add with two subs: welder_detail + roofer_breakout + crane note + labor_table + three_col totals. NTE: three_col allocation + roofer_breakout + labor_table + crew_grid + totals. Credit: credit_labor_table only.
- **Roofer note wording:** when a sub's summary leaves a line out, say so in the note and show the breakout that reconciles to their firm total.
- **Attachments differ per PCO**: engineer details, RFIs, sub proposals, certified-mail notices, equipment estimates. The final ATTACHED bullet in the narrative must list them in merge order.
- Optional: the itemization can be disabled ("enabled": false) for a minimal one-page narrative PCO.
