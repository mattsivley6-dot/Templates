# Daily Report (field construction report)

## Purpose and when to use
The Daily Report is a short 1-to-2 page letterhead field construction report PDF, one per calendar day of the job from mobilization to completion, filed in the job's daily reports folder. Each report carries the company letterhead, an info grid (project, owner, date, weather), terse bulleted sections (work performed, crews, equipment, deliveries, safety, meetings and visitors, remarks), a "Prepared by" line, and up to four uncaptioned photos. Reports are numbered sequentially from mobilization day and include no-work days (weekends, holidays), which get a minimal one-page report.

This is not the same document as a long-form docx daily log. Both may use the on-page title "DAILY CONSTRUCTION REPORT", but this template builds the short letterhead PDF only.

## Output spec
- Format: PDF, generated directly with reportlab (no docx step, no Word needed).
- Page size: US Letter, 8.5 x 11 in (612 x 792 pt), portrait. 1 page, or 2 pages when photos do not fit on page 1.
- Margins: 0.75 in left and right. Vertical structure is drawn at fixed coordinates (masthead top edge at 62 pt from top, footer rule at 46 pt from bottom), equivalent to roughly 0.5 in top and bottom working area.
- Fonts: Helvetica and Helvetica-Bold (reportlab built-ins). Sizes: wordmark 22 pt bold, tagline 7 pt (letterspaced 3.2 pt), address block 7.6 pt, title 15 pt bold, info grid labels 6.6 pt bold, info grid values 8.6 pt, section headers 8.6 pt bold, body bullets 10 pt, signature 8.4 pt, footer 6.8 pt, footer-right report line 7.2 pt.
- Colors (hex): accent color from the company config `brand.accent_color` (wordmark, rules, "No. NN", section headers; default #2E7D32 when the config has none), gray #595959 (secondary text, labels, footer, signature), light gray #BFBFBF (hairlines, grid border, photo borders), ink #1A1A1A (body text), pale gray-green #F2F5EF (info grid fill).
- Header (every page): wordmark top left (or the company logo, if the config has one) with a gray letterspaced tagline beneath; right-aligned gray address block; 1.4 pt accent horizontal rule across the page under both.
- Footer (every page): 0.5 pt light gray rule at y=46 pt; centered gray company line beneath it; right-aligned "Daily Report NN    |    MM/DD/YYYY    |    Page N" just above the rule (y=55 pt).
- PDF metadata: Title "Daily Construction Report NN - {pdf_title_project}", Author and Creator from the company config `legal_name`, Subject "Daily Construction Report".

## Company config

Company data is never hard coded. The script reads `template-library/company.example.json` by default (two folders up from this script). Copy it, fill in your own company, and pass it with `--company`. Fields used:

| config key | used for |
|---|---|
| legal_name | footer company line; PDF Author and Creator |
| dba | text wordmark, upper case (falls back to legal_name) |
| license | tagline under the wordmark, rendered "LICENSE <number>"; skipped when empty |
| address_line1, city_state_zip, phone, website | right-aligned address block and footer line; empty fields are skipped |
| logo_path | optional image drawn in place of the text wordmark (fitted to 160 x 36 pt); relative paths resolve against the config file; null skips it and the text wordmark is used |
| brand.accent_color | accent color |
| pm_name, pm_title | default "Prepared by" line when `project.prepared_by` is empty |

Optional extra keys the script also honors if you add them to your own config: `wordmark` (overrides the DBA text) and `tagline` (overrides the license line).

## Layout walkthrough
Page 1, top to bottom (origin bottom-left, page height 792 pt, LEFT=54 pt, RIGHT=558 pt, content width W=504 pt):

1. Masthead: wordmark (Helvetica-Bold 22, accent) at (LEFT, 730). Tagline (Helvetica 7, gray, char spacing 3.2) starting at (LEFT+1, 719). Address block right-aligned to RIGHT, Helvetica 7.6 gray, up to four lines at y = 740, 731, 722, 713: street / city, state ZIP / phone / website. Accent rule (1.4 pt) from LEFT to RIGHT at y=704.
2. Footer (drawn with the masthead on every page): light gray 0.5 pt rule LEFT to RIGHT at y=46; centered company line (Helvetica 6.8, gray) at y=36; right-aligned report line (Helvetica 7.2, gray) at y=55.
3. Title row at y=680: "DAILY CONSTRUCTION REPORT" (Helvetica-Bold 15, ink) left; "No. NN" (Helvetica-Bold 15, accent, zero-padded 2 digits) right-aligned.
4. Info grid: a 48 pt tall box starting 14 pt below the title row, filled pale #F2F5EF with 0.6 pt light gray border, divided into 4 columns of widths 34% / 24% / 22% / 20% of W with light gray vertical separators. Each cell: label (Helvetica-Bold 6.6, gray, 7 pt in from cell left, 13 pt down from box top) then value (Helvetica 8.6, ink, wrapped to max 3 lines, 10 pt line pitch, starting 24 pt down). Labels: PROJECT, OWNER, DATE, WEATHER. DATE renders as "Dayname, Month D, YYYY" (no zero-padded day).
5. Sections, starting 22 pt below the grid. Each section: title (Helvetica-Bold 8.6, accent, all caps) with a 0.5 pt light gray hairline from 8 pt after the title text to RIGHT, raised 2.6 pt; then 15 pt down, items in Helvetica 10 ink. Bulleted items use a bullet glyph at LEFT+2 and text at LEFT+14, wrapped to W-14, 13.2 pt line pitch, 1.5 pt extra after each item, 9 pt extra after the section. Sections in order, each skipped when empty: WORK PERFORMED (bullets), CREWS ON SITE (single unbulleted line: trades joined by "  |  ", each optionally suffixed " (N)" with headcount), EQUIPMENT (bullets), DELIVERIES (bullets), SAFETY (bullets; on any day with work, the fixed line "No accidents or injuries." is automatically prepended), MEETINGS AND VISITORS (bullets), REMARKS (bullets).
6. Signature line: "Prepared by {prepared_by}" (Helvetica 8.4, gray) at (LEFT, 66) on page 1 always.
7. PHOTOS section, up to 4 photos, suppressed entirely on no-work days. Two-column grid: column width colw=(W-10)/2, gap 10 pt, tile aspect 0.72 (page 1) or 0.75 (page 2). If there are 1-2 photos and they fit above y=80 on page 1: PHOTOS header drawn 4 pt below the last section, then the photo row (one photo spans full W, two photos side by side). Otherwise a second page is added: masthead and footer repeat, PHOTOS header at y=676, then a 2x2 grid (1 row if 2 or fewer photos). With exactly 3 photos the third spans the full width beneath the first row. A single photo on page 2 spans full W at up to 1.6x tile height. Every photo is EXIF-transposed, optionally rotated (video stills), center-cropped to the tile aspect, downsampled to max 1400 px, JPEG quality 80, and drawn with a 0.6 pt light gray border.

Page 2 (only when photos overflow): masthead, footer with "Page 2", PHOTOS section as described in 7. Nothing else.

## Placeholders
All keys live in the data JSON. Top level: `project` (object), `output_dir` (optional string), `reports` (array of report objects).

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| project.project_line | string | yes | "Sample Elementary School HVAC Replacement, 200 Example Avenue, Anytown, TX 75001" | PROJECT cell of the info grid, wraps to 3 lines max |
| project.owner | string | yes | "Sample ISD" | OWNER cell |
| project.job_short | string | yes | "Sample ES" | short job name used in the output filename |
| project.pdf_title_project | string | yes | "Sample Elementary School HVAC Replacement" | full project name for the PDF Title metadata |
| project.prepared_by | string | no | "Pat Doe, Project Manager" | rendered after the fixed text "Prepared by "; empty uses pm_name and pm_title from the company config |
| project.photo_dir | string | yes if any photos | "sample_photos" | folder where relative photo filenames are resolved; relative paths resolve against the data file's folder; extension and case mismatches fall back to filename-stem matching |
| output_dir | string | no | "_sample_output" | where PDFs are written; relative paths resolve against the data file's folder; defaults to the data file's folder |
| reports[].report_no | integer | yes | 3 | sequential from mobilization day, rendered zero-padded to 2 digits |
| reports[].date | string | yes | "2026-01-14" | ISO date; script derives the weekday name and long date, no clock is used |
| reports[].weather | string | yes | "Clear, cool, dry. No time lost." | free text; for days without an on-site observation a pattern like "High 60. Low 41." from a weather archive works |
| reports[].work | array of string | yes | ["Crane set new RTU-1 on the curb adapter."] | WORK PERFORMED bullets; a no-work day is a single bullet starting with "No work" |
| reports[].crews | array of object | no | [{"trade": "HVAC", "count": 4}] | CREWS ON SITE line; `count` optional, omit when headcount is unknown |
| reports[].crews[].trade | string | yes (per crew) | "Electrical" | trade label |
| reports[].crews[].count | integer | no | 4 | rendered as " (4)" after the trade |
| reports[].equipment | array of string | no | ["Crane", "Flatbed truck"] | EQUIPMENT bullets |
| reports[].deliveries | array of string | no | ["RTU-1 and curb adapter from Sample Supply"] | DELIVERIES bullets |
| reports[].safety | array of string | no | ["Crane pick zone barricaded during the lift."] | SAFETY bullets; "No accidents or injuries." is auto-prepended on work days |
| reports[].visitors | array of string | no | ["Owner Engineer Contractor meeting held."] | MEETINGS AND VISITORS bullets |
| reports[].remarks | array of string | no | ["RTU-2 set planned for next week, weather permitting."] | REMARKS bullets |
| reports[].photos | array of object | no | [{"file": "photo_01.jpg"}] | up to 4 used; ignored on no-work days |
| reports[].photos[].file | string | yes (per photo) | "photo_01.jpg" | filename in photo_dir, or an absolute path |
| reports[].photos[].rotate | integer | no | -90 | extra rotation in degrees (PIL counterclockwise) for video stills lacking EXIF orientation |
| reports[].no_work | boolean | no | true | override; when absent it is derived from work[0] starting with "No work" |

All values in `sample_data.json` are made up. The images in `sample_photos/` are gray placeholders.

## Fixed wording
Never changes between jobs (verbatim):
- Footer-right pattern: "Daily Report NN    |    MM/DD/YYYY    |    Page N"
- Title: "DAILY CONSTRUCTION REPORT" and "No. NN"
- Info grid labels: "PROJECT", "OWNER", "DATE", "WEATHER"
- Section headers: "WORK PERFORMED", "CREWS ON SITE", "EQUIPMENT", "DELIVERIES", "SAFETY", "MEETINGS AND VISITORS", "REMARKS", "PHOTOS"
- Auto safety line on every work day: "No accidents or injuries."
- Signature prefix: "Prepared by "
- No-work day work bullet convention: "No work performed." (with optional reason appended, e.g. "No work performed. Weekend.")
- PDF metadata: Subject "Daily Construction Report", Title pattern "Daily Construction Report NN - {pdf_title_project}"

Letterhead text (wordmark, tagline, address block, footer company line) comes from the company config, not from the script.

## How to build
Requires Python 3, reportlab and Pillow.

```
python build_daily_report.py [data.json] [--company <path to company.json>]
```
- With no data argument it uses `sample_data.json` beside the script.
- `--company` defaults to `../../company.example.json` relative to the script (the template-library root).
- Writes one PDF per entry in `reports` to `output_dir`, filename pattern: `YYYY-MM-DD Daily Report NN - {job_short}.pdf` (e.g. `2026-01-14 Daily Report 03 - Sample ES.pdf`). The sample build is in `_sample_output/`.
- Deterministic: Canvas invariant=1, no clock or randomness; identical data plus identical photo and config files give byte-identical PDFs.
- Photos must exist on disk; the script exits with an error naming any missing file.

## Known variations
- Most variation is day to day, not job to job.
- No-work days (weekends, holidays, access failures): single "No work performed." bullet, no crews, no photos, no auto safety line; renders as a minimal one-pager. Issue and number reports for those days anyway to keep an unbroken daily record.
- Photo count 0 to 4. 1-2 photos may fit on page 1 (the script decides by remaining space); 3-4 photos always go to page 2.
- Weather text can come from on-site observations ("Hot, sunny, clear. Dry.") or from a weather archive such as Open-Meteo rendered as "High NN. Low NN." plus " Showers in the area." when precipitation is 0.25 in or more. This template takes the final string per day; either style is fine.
- Crew headcounts appear only when known; most crew entries can be trade name only.
- Some photos are stills pulled from videos and need a manual rotate value.
- EQUIPMENT and DELIVERIES sections appear only on days with entries (crane day, delivery days). MEETINGS AND VISITORS commonly contains a line like "Owner Engineer Contractor meeting held."
- The script builds exactly the entries listed in `reports`, so single-day rebuilds are possible.
