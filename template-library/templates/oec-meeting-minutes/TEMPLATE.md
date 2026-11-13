# OEC/OAC Progress Meeting Minutes

## Purpose and when to use

Formal minutes the contractor issues after every Owner, Engineer, Contractor (OEC) or Owner, Architect, Contractor (OAC) progress meeting on a construction job, often a public-entity job. The PM prepares them the same day or the day after the meeting, saves the docx plus a PDF in the job's meetings folder, and emails them to all attendees. They serve as the record of discussion items, directions given, and action items; the closing paragraph starts a five business day correction window after which the minutes stand as the record.

Use this template for weekly or monthly OEC/OAC progress meetings. Do not use it for pre-construction meeting notes (those are better as a looser narrative format, see Known variations).

## Output spec

- Format: .docx (python-docx). A PDF copy is normally issued alongside it, converted from the docx (see How to build).
- Page: letter, 8.5 x 11 in, portrait, single section, one to three pages depending on content. Content flows; no manual page breaks.
- Margins: left 0.90 in, right 0.90 in, top 0.70 in, bottom 0.70 in. Header distance 0.50 in, footer distance 0.50 in. Header and footer are empty.
- Font: Arial throughout (set on the Normal style; runs inherit it). Base Normal size 10.5 pt, space after 4 pt, line spacing 1.15 (the python-docx docDefaults value of 276/240, left untouched).
- Sizes: title 15 pt bold; project subtitle 11 pt bold; masthead lines 10 pt; section headings 11 pt bold; discussion items 10.5 pt; attendance table 9.5 pt; action items table 9 pt; italic notes and closing 9 pt italic.
- Colors (hex): navy #1A264D for the title and every section heading; gray #595959 for the italic attendance note and the closing paragraph; table header row shading #E8EBF2; all other text black.
- Tables: Word built-in style "Table Grid" (thin black borders all around), autofit, columns evenly split across the 6.7 in text width. Attendance table 3 columns (about 2.23 in each); action items table 4 columns (about 1.68 in each). Header row cells shaded #E8EBF2 with bold text.
- Header/footer: none (empty on every page).
- Document properties: author and last modified by are the company DBA from the company config; title is doc_title; created and modified are fixed from doc_date.

## Layout walkthrough

Single flowing document, top to bottom:

1. Title line: the doc_title (for example "OEC PROGRESS MEETING MINUTES"), 15 pt bold, navy #1A264D, space after 2 pt.
2. Project subtitle: one bold 11 pt black line naming the project, optionally followed by "  |  " and a meeting-series descriptor (for example "Sample Elementary School HVAC Replacement  |  Weekly Owner, Engineer, Contractor Meeting"), space after 6 pt.
3. Masthead block: eight single-line paragraphs, each a bold 10 pt label ending in a colon and two spaces, followed by the regular 10 pt value. Order is fixed: Owner, Solicitation, Contractor, Engineer, Meeting Date, Format (or Location), Prepared By, Distribution. Each inherits the Normal 4 pt space after.
4. "Attendance" heading: 11 pt bold navy, space before 9 pt, space after 2 pt.
5. Attendance table: Table Grid, 3 columns (Name, Organization, Role), header row shaded #E8EBF2 with 9.5 pt bold text, one 9.5 pt body row per attendee.
6. Optional attendance note: one 9 pt italic gray #595959 paragraph immediately under the table ("Not in attendance: ..." or "Referenced, not present: ...").
7. Numbered discussion sections, one after another. Each section is:
   - Heading paragraph "N.0   Title" (three spaces between the number and title), 11 pt bold navy, space before 9 pt, space after 2 pt. N starts at 1 and increments.
   - One paragraph per discussion item: bold run "N.M   " (item number, three trailing spaces) then a regular run with the item text, both 10.5 pt, space after 3 pt, left indent 0.35 in. M starts at 1 within each section.
8. Action items: a final numbered heading "N.0   Action Items" where N is one past the last discussion section, same heading style. Below it a Table Grid table with 4 columns (No., Action, Responsible, Target), header row shaded #E8EBF2 with 9 pt bold text, one 9 pt body row per action item; the No. column is 1, 2, 3... in order.
9. Closing paragraph: 9 pt italic gray #595959, space before 10 pt, containing the fixed five business day record statement, optionally followed by one job-specific extra sentence.

## Company config

Company data is never hard coded. The script reads `template-library/company.example.json` by default (two folders up from this script). Copy it, fill in your own company, and pass it with `--company`. Fields used:

| config key | used for |
|---|---|
| legal_name | Contractor masthead line when the data file leaves `contractor` empty; last part of the default Prepared By line |
| dba | docx author and last modified by properties (falls back to legal_name) |
| pm_name, pm_title | default Prepared By line when the data file leaves `prepared_by` empty |

No logo or signature is used by this template.

## Placeholders

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| doc_title | string | yes | OEC PROGRESS MEETING MINUTES | All caps. Use "OAC PROGRESS MEETING MINUTES" for OAC meetings. Also used as the docx Title property. |
| project_line | string | yes | Sample Elementary School HVAC Replacement  \|  Weekly Owner, Engineer, Contractor Meeting | Bold subtitle. The "  \|  descriptor" tail is optional. |
| owner | string | yes | Sample ISD | Masthead value. |
| solicitation | string | yes | CSP 2026-0001 | Masthead value; the bid, CSP or contract number. |
| contractor | string or null | no | Example Mechanical, LLC | Masthead value. Empty or null uses `legal_name` from the company config. |
| engineer | string | yes | Sample Engineering, Inc. | Masthead value. On an OAC job this may be an architect; the label stays "Engineer". |
| meeting_date | string | yes | Wednesday, January 14, 2026, 1:00 PM | Free text; weekday, long date, optional time. |
| location_label | string | no | Format | Label for the sixth masthead line. Defaults to "Format". Use "Location" if you prefer. |
| location | string | yes | Video call plus on site at Sample Elementary School | Value for the Format/Location line. |
| prepared_by | string or null | no | Pat Doe, Project Manager, Example Mechanical, LLC | Masthead value. Empty or null builds "pm_name, pm_title, legal_name" from the company config. |
| distribution | string | yes | All attendees and project file | Masthead value. |
| doc_date | string | yes | 2026-01-14 | YYYY-MM-DD. Sets the docx created/modified core properties (determinism). Use the meeting date. |
| output_basename | string | yes | Sample_ES_OEC_Progress_Meeting_Minutes_2026-01-14 | Output filename without extension. Suggested pattern: `<Job>_<OEC or OAC>_[Progress_]Meeting_Minutes_YYYY-MM-DD`. |
| attendees | array of objects | yes | see sample_data.json | One attendance table row each, in order. |
| attendees[].name | string | yes | Pat Doe | Column 1. |
| attendees[].organization | string | yes | Example Mechanical, LLC | Column 2. |
| attendees[].role | string | yes | Project Manager / Contractor (on site) | Column 3. Often carries "(on site)", "(by phone)", or "(copied)". |
| attendance_note | string | no | Not in attendance: the controls subcontractor (copied). | Italic gray note under the attendance table. Omit or empty string to skip. |
| sections | array of objects | yes | see sample_data.json | Discussion sections in order. Numbering (1.0, 2.0, ...) is generated automatically; do not put numbers in the data. |
| sections[].title | string | yes | RFIs and Change Orders | Heading text after "N.0   ". |
| sections[].items | array of strings | yes | ["RFI-001 (RTU-2 curb adapter) is open. ..."] | One paragraph per item; item numbers (N.1, N.2, ...) are generated automatically. |
| action_items | array of objects | yes | see sample_data.json | Rows of the final table. Row numbers are generated automatically. The Action Items heading number is one past the last section. |
| action_items[].action | string | yes | Respond to RFI-001 (RTU-2 curb adapter) | Column 2. |
| action_items[].responsible | string | yes | Engineer | Column 3. Short party names: Contractor, Engineer, Owner, subs, or combinations with " / ". |
| action_items[].target | string | yes | Next meeting | Column 4. Short: a date, "ASAP", "In progress", "Next meeting", etc. |
| closing_extra | string | no | (empty) | One extra sentence appended after the fixed closing statement, for example to note a related meeting that is not covered. Omit or empty to skip. |

All values in `sample_data.json` are made up.

## Fixed wording

These strings are hard coded in the script and never change between jobs:

- Masthead labels (bold, each followed by a colon and two spaces): `Owner:`, `Solicitation:`, `Contractor:`, `Engineer:`, `Meeting Date:`, `Format:` (or the location_label override), `Prepared By:`, `Distribution:`
- Heading: `Attendance`
- Attendance table header row: `Name` | `Organization` | `Role`
- Heading: `Action Items` (rendered as "N.0   Action Items")
- Action items table header row: `No.` | `Action` | `Responsible` | `Target`
- Closing paragraph (italic, gray): `These minutes reflect the writer's understanding of the items discussed and the conclusions reached. Please direct any corrections or additions to the writer within five (5) business days of receipt; otherwise these minutes will stand as the record of the meeting.`
- Distribution value by convention is `All attendees and project file` (kept as a placeholder).

## How to build

Requires Python 3 and python-docx.

```
python build_oec_meeting_minutes.py [data.json] [--company <path to company.json>] [--out-dir <folder>]
```

- With no data argument the script uses `sample_data.json` from its own folder.
- `--company` defaults to `../../company.example.json` relative to the script (the template-library root).
- `--out-dir` defaults to the current working directory.
- Output: `<output_basename>.docx`, for example `Sample_ES_OEC_Progress_Meeting_Minutes_2026-01-14.docx`. The sample build is in `_sample_output/`.
- The build is deterministic: identical JSON gives byte-identical docx (core properties are fixed from `doc_date` and the company config).
- PDF copy (normally issued alongside the docx): on Windows with Word installed, convert with Word COM from PowerShell:

```powershell
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$d = $w.Documents.Open("<full path>\Sample_ES_OEC_Progress_Meeting_Minutes_2026-01-14.docx")
$d.SaveAs("<full path>\Sample_ES_OEC_Progress_Meeting_Minutes_2026-01-14.pdf", 17)
$d.Close($false)
$w.Quit()
```

## Known variations

- OEC vs OAC: only the title changes ("OEC PROGRESS MEETING MINUTES" vs "OAC PROGRESS MEETING MINUTES") plus whoever fills the Engineer line.
- Masthead line 6 label: "Format" (default) or "Location". Controlled by location_label.
- Project subtitle: either the project name alone, or the project name plus "  |  " and a meeting-series descriptor. Both live in project_line.
- Attendance note: optional. Use "Not in attendance: ..." or "Referenced, not present: ...". Omit the key when there is nothing to note.
- Closing paragraph: the fixed statement, plus an optional job-specific sentence through closing_extra.
- Section count varies freely. A "Next Meeting" section is often the last discussion section before Action Items.
- Pre-construction meetings suit a separate narrative notes format (title, topic headings, no numbered items or action table); do not use this template for those.
