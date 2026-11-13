# Daily Log (Daily Construction Report, DCR)

## Purpose and when to use
The Daily Log is a long-form written field log, titled "DAILY CONSTRUCTION REPORT" and numbered `DCR-YYYY-MMDD`. The PM files one per site day (or one covering two consecutive days) in the job folder. It records weather, a narrative of general conditions, a day-at-a-glance summary, trades on site, topical sections for each work front (roofing, structural, RFIs, PCOs, meetings, pay application, safety), a look ahead, key field photos with captions, attachments and a signature block. It is the contemporaneous record used to back up change orders, concealed-condition notices and schedule claims.

This template builds the long-form docx log only. A short one-to-two page daily report on full letterhead, if you use one, is a separate document.

## Output spec
- Format: .docx (python-docx). Usually filed as both .docx and .pdf; make the PDF from the docx afterward (see How to build).
- Page: US Letter, 8.5 x 11 in, portrait (python-docx default section).
- Margins: top 0.7 in, bottom 0.7 in, left 0.8 in, right 0.8 in.
- Base font: Arial 10 pt (Normal style), paragraph space-after 4 pt.
- Type sizes and colors:
  - Company name line: Arial 14 pt bold, brand primary color from the company config.
  - Document title line: Arial 12 pt bold, black.
  - Header info lines: Arial 9.5 pt, gray #595959.
  - Header rule: bottom paragraph border, single, size 12 (1.5 pt), brand primary color.
  - Section headings: Arial 10.5 pt bold, brand primary color, space before 8 pt / after 3 pt.
  - Narrative paragraphs: Arial 10 pt.
  - Bullets: built-in "List Bullet" style, left indent 0.25 in, space after 2 pt.
  - Tables: "Table Grid" style. Header row 9 pt bold on shading #E8EBF2; body cells 9.5 pt. Weather table centered.
  - Photo captions: Arial 8 pt, gray #595959.
- Header/footer: none (no running page header or footer). The letterhead-style block is body text at the top of page 1 only.
- Photos: 2-up in 2x2 "Table Grid" tables (image row + caption row), each image 3.0 in wide, centered.
- Core properties: author and last_modified_by set from the company config legal_name; created and modified set from `doc_created_iso` in the data file (deterministic, no clock reads).
- Determinism: after saving, the script rewrites the docx zip with entry timestamps fixed from `doc_created_iso`, so identical data gives a byte-identical file.
- House rule: no em dashes and no en dashes anywhere. The build script scans every string in the data and company files and exits 1 if it finds one.

## Layout walkthrough
Single continuous flow; content typically runs 3 to 6 pages depending on the day. Top to bottom:

1. Header block (page 1 top, body paragraphs, no page header):
   - Company legal name in upper case (14 pt bold, brand color, space after 0).
   - "DAILY CONSTRUCTION REPORT" (12 pt bold black, space after 2 pt).
   - Three or four gray 9.5 pt info lines, each space after 0, values joined with two spaces, pipe, two spaces:
     - `Project: <project_name>  |  Owner: <owner>`
     - `Report No.: <report_no>  |  <Date or Dates>: <report_date_text>`
     - `Contract: <contract_text>  |  Substantial completion target: <completion_target>` (line omitted when contract_text is empty; the completion-target half omitted when empty)
     - `Prepared by: <prepared_by>`
   - Empty paragraph carrying a brand-color bottom border (the horizontal rule), space before 4 pt / after 6 pt.
2. Weather table: 2 rows x 4 columns, Table Grid, centered. Row 1 = headers (9 pt bold, #E8EBF2 fill), row 2 = values (9.5 pt). Headers and values both come from the data file.
3. "GENERAL CONDITIONS" heading (10.5 pt bold, brand color, space before 6 pt) followed by one narrative paragraph (10 pt) summarizing the day(s).
4. Numbered sections, in data-file order, auto-numbered `1.`, `2.`, ... Each starts with a brand-color section heading `<n>. <TITLE>` (titles are ALL CAPS). Three section body types:
   - bullets: List Bullet items, 0.25 in indent.
   - table: Table Grid with shaded bold header row; used for the trades table (3 columns, widths 1.7 / 4.6 / 0.7 in: Trade / Party, Activity, Crew or Day).
   - photos: successive 2x2 Table Grid tables. Top row = two photos 3.0 in wide, centered; bottom row = 8 pt gray captions ending with the date, e.g. "... 03/10/2026." A small spacer paragraph (space after 2 pt) follows each pair.
   Customary section order: SUMMARY (DAY(S) AT A GLANCE); TRADES / PARTIES ON SITE OR ENGAGED; then day-specific topical sections (work fronts, meetings, RFIs/PCOs, pay application, start up); SCHEDULE; SAFETY; LOOK AHEAD; FIELD PHOTOS (KEY); ATTACHMENTS.
5. Signature block: one empty paragraph, then a 2x2 Table Grid. Row 1 (shaded #E8EBF2, bold): "Prepared by:" | "Date:". Row 2: name block ("[PM Name], [PM Title]" newline "[Company Legal Name]") | date written out ("March 11, 2026"). All cells 9.5 pt.

## Company config
Company fields come from `template-library/company.example.json` (or your own copy passed with `--company`):

| Config key | Used for |
|---|---|
| legal_name | Company name line at the top (upper case); default company line in the signature block; docx author and last-modified-by |
| brand.primary_color | Company name line, section headings and header rule |
| pm_name, pm_title | Default for `prepared_by` (and the signature block) when the data file leaves it out |

logo_path and signature_path are not used by this template.

## Placeholders
All job keys live in the JSON data file. `sections` is an ordered array; the script prepends the section numbers.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| file_date_label | string | yes | "2026-03-10 to 11" | Date part of the output filename. ISO date, or ISO range for a two-day log. |
| project_short | string | yes | "Sample ES" | Short name for the output filename. |
| project_name | string | yes | "Sample Elementary School HVAC Replacement" | Full project title in the header. |
| owner | string | yes | "Sample ISD" | Owner name in the header. |
| report_no | string | yes | "DCR-2026-0310" | Pattern DCR-YYYY-MMDD (first covered date for multi-day logs). |
| report_date_word | string | no | "Dates" | "Date" (default) for one day, "Dates" for a multi-day log. |
| report_date_text | string | yes | "Tuesday, March 10 and Wednesday, March 11, 2026" | Weekday(s) and date(s) written out. |
| contract_text | string | no | "Project 2026-0001, Job J-0001" | Empty or omitted = whole contract line dropped. |
| completion_target | string | no | "May 29, 2026" | Second half of the contract line; dropped when empty. |
| prepared_by | string | no | "Pat Doe, Project Manager" | [PM Name], [PM Title]. Defaults to pm_name, pm_title from the company config. |
| weather_headers | array[4] of string | yes | ["Weather", "Temperature", "Precipitation", "Weather Delay"] | Exactly 4. Single-day logs often use ["Weather (AM)", "Weather (PM)", "Precipitation", "Weather Delay"]. |
| weather_values | array[4] of string | yes | ["Clear both days", "Mild", "None", "None"] | Exactly 4, aligned with headers. |
| general_conditions | string | yes | "Two productive field days. On March 10 the crew opened the curbs..." | One narrative paragraph. |
| sections | array of object | yes | see sample_data.json | Ordered; numbered 1..n automatically. |
| sections[].title | string | yes | "SUMMARY (DAYS AT A GLANCE)" | ALL CAPS, without the number. |
| sections[].type | string | no | "bullets" | "bullets" (default), "table", or "photos". |
| sections[].items | array of string | for bullets | ["March 10: curbs opened at RTU-1 and RTU-2..."] | Bullet texts. |
| sections[].headers | array of string | for table | ["Trade / Party", "Activity", "Day"] | Header row cells. |
| sections[].rows | array of array | for table | [["HVAC (Contractor)", "PM both days: ...", "3/10, 3/11"]] | Body rows, same width as headers. |
| sections[].col_widths_in | array of number | no | [1.7, 4.6, 0.7] | Column widths in inches; default 1.7/4.6/0.7 for 3 columns. |
| sections[].photo_dir | string | for photos | "sample_photos" | Folder holding the photo files; relative paths resolve against the data file's folder. |
| sections[].pairs | array of pair | for photos | [[{"file": "photo_01_curb_opening.jpg", "caption": "RTU-1 curb opening... 03/10/2026."}, {...}]] | Each pair = two {file, caption} objects rendered side by side. |
| signature_name_block | string | no | "Pat Doe, Project Manager\nExample Mechanical, LLC" | \n becomes a line break in the cell. Defaults to prepared_by plus the company legal_name. |
| signature_date | string | yes | "March 11, 2026" | Date the report is signed, written out. |
| doc_created_iso | string | yes | "2026-03-11T08:00:00" | Fixed docx created/modified timestamp (determinism). Format YYYY-MM-DDTHH:MM:SS. |
| output_dir | string | no | "_sample_output" | Output folder; relative paths resolve against the script folder. Default "_sample_output". On a live job point it at your job's daily log folder. |

The sample photos in `sample_photos/` are gray placeholder images.

## Fixed wording
These strings never change between jobs (verbatim, including punctuation):
- "DAILY CONSTRUCTION REPORT"
- "GENERAL CONDITIONS"
- Header line prefixes and separators: "Project: ", "  |  Owner: ", "Report No.: ", "Contract: ", "  |  Substantial completion target: ", "Prepared by: " (separator is space space pipe space space).
- The word before the report date is "Date: " or "Dates: " (single vs multi-day).
- Signature table labels: "Prepared by:" and "Date:".
- Recurring section titles (supplied through JSON but constant in practice): "SUMMARY (DAY AT A GLANCE)" / "SUMMARY (DAYS AT A GLANCE)", "TRADES / PARTIES ON SITE OR ENGAGED THIS DATE" (multi-day drops "THIS DATE"), "SAFETY", "SCHEDULE", "LOOK AHEAD", "FIELD PHOTOS (KEY)", "ATTACHMENTS".
- Recurring safety bullet: "No incidents, injuries, or near misses reported this date." (multi-day: "... reported either day.")
- Weather delay value when none: "None" (or "None today").
- Report numbering pattern: "DCR-" + year + "-" + MMDD.
- Output filename pattern: "<file_date_label> Daily Log - <project_short>.docx".

The company name line and the company line in the signature block come from the company config, not from fixed wording.

## How to build
```
cd template-library/templates/daily-log
py -3 build_daily_log.py [data.json] [--company path\to\company.json]
```
- No data argument: uses `sample_data.json` in this folder.
- No `--company`: uses `../../company.example.json` (relative to this script). Point it at your own company file for real use.
- Expected output: `<output_dir>\<file_date_label> Daily Log - <project_short>.docx`, e.g. `_sample_output\2026-03-10 to 11 Daily Log - Sample ES.docx`. Exit code 0 on success, prints `saved <path>`.
- The script fails (exit 1) if any string in the data or company file contains an em or en dash, if a photo file is missing, or if the weather arrays are not length 4.
- Requires: python-docx only (plus stdlib). No clock reads, no randomness; identical data gives a byte-identical .docx (zip entry timestamps are normalized from doc_created_iso).

PDF conversion: open the docx in Word and Save As PDF, or script it with Word COM from PowerShell:
```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("<full path>\2026-03-10 to 11 Daily Log - Sample ES.docx")
$doc.SaveAs("<full path>\2026-03-10 to 11 Daily Log - Sample ES.pdf", 17)  # 17 = wdFormatPDF
$doc.Close()
$word.Quit()
```

## Known variations
- Single-day vs multi-day: one log may cover two consecutive days. Multi-day logs use report_date_word "Dates", weather headers ["Weather", "Temperature", "Precipitation", "Weather Delay"], trades table third column "Day", section 1 titled "SUMMARY (DAYS AT A GLANCE)", and the safety bullet "either day". Single-day logs use "Date", weather headers ["Weather (AM)", "Weather (PM)", "Precipitation", "Weather Delay"], trades column "Crew", "SUMMARY (DAY AT A GLANCE)", "this date".
- A leaner variant is possible: three header info lines (no contract line), an empty general_conditions string (the heading still prints), no photos section (photos referenced as an attachment instead), and a trades table headed "Trade | Activity | Crew" under the title "TRADES ACTIVE THIS DATE". Prefer the full layout for new logs.
- Section count and topical titles change every day with the work (8 to 16 sections is typical). SUMMARY, TRADES, SAFETY, LOOK AHEAD and ATTACHMENTS recur in every log; SCHEDULE and FIELD PHOTOS (KEY) usually do.
- The FIELD PHOTOS section is optional (omit the section object entirely when there are no photos); 2 to 4 pairs per log is typical.
- Crew counts in the trades table can be left as "(enter)" pending headcounts, with a note to enter subcontractor headcounts before filing.
- Trades table row set varies with who was on site; typical parties: HVAC (Contractor), Roofing, Steel / Welding, Site / Excavation, Electrical, Controls, Plumbing, Engineer, Owner.
