# Photo Log (dated photo exhibit document)

## Purpose and when to use

One script, two photo documents, selected by the `"mode"` key in the JSON data file:

1. **`"daily"` - Daily Photo Log.** A dated, numbered photo record of one day (or a short date range) of field work. Two photos per page, grouped under colored section bars by activity (curb sets, RFIs, excavation, structural steel, and so on). File it with the written daily log and reference it from RFI and PCO correspondence. An optional trailing Video Index page lists the day's video clips by EXIF capture time so a reviewer can pull the right clip.

2. **`"exhibit"` - Stored-Material / Pay-App Photo Exhibit.** One photo per page with a bold metadata line citing the EXIF capture date/time and GPS coordinates embedded in the image. This is the backup for the stored-material column on a pay application: the EXIF timestamp proves WHEN the material photo was taken and the GPS coordinates prove WHERE (on site, at the vendor's ship-to, or at your warehouse). Attach it to the pay app package.

Convention to preserve: whenever a photo is used to verify stored material or delivery, cite the EXIF capture time and GPS in the document, and name the metadata source ("per embedded image metadata (EXIF, phone camera)"). Plain undated photos are weak evidence; do not use them for stored material.

## Company config

Company data is never hard-coded. The script reads it from the template-library company config:

- `--company <path>` selects the file. Default: `template-library/company.example.json` (two folders up from this script). Copy that file, fill in your own values, and pass it with `--company`.
- Fields used:
  - `legal_name`: daily header line 1 (upper-cased), exhibit footer prefix, and PDF author.
  - `pm_name`: daily footer "Prepared by" when the data file has no `prepared_by`.
  - `brand.primary_color`: accent color for the daily company line, header rule, section bars, photo labels and video index header bar. Falls back to neutral dark gray `#333333` if missing.
- `logo_path` and `signature_path` are not used by this template.

## Output spec

- Format: PDF, built natively with PyMuPDF (fitz) + Pillow. No docx stage, no Word needed.
- Page size: US Letter portrait, 612 x 792 pt (8.5 x 11 in), every page.
- Margins:
  - daily mode: 40 pt (0.56 in) on all four sides.
  - exhibit mode: 54 pt (0.75 in) left and right; content starts at y = 54 pt from the top.
- Fonts: PDF base-14 Helvetica (`helv`) and Helvetica-Bold (`hebo`). No embedded fonts.
  - daily: company line 9 pt bold, header line 8 pt, section bar 8 pt bold (auto-shrinks in 0.5 pt steps to fit, floor 6.5 pt), photo label 7.5 pt bold, caption 8 pt (line height 1.15), footer 7 pt; video index intro 8.5 pt, note 8 pt, table 8 pt.
  - exhibit: title 12 pt bold, subtitle lines 9.5 pt, metadata line 9 pt bold, note + caption 8.5 pt (line height 1.25), footer 7.5 pt.
- Colors:
  - Accent: `brand.primary_color` from the company config (company name, section bars, table header bar, header rule, photo number labels).
  - White `#FFFFFF`: text inside accent bars.
  - Black `#000000`: body text.
  - Gray `#737373` (0.45, 0.45, 0.45): daily-mode photo borders, footer, video index note.
  - Gray `#666666` (0.40, 0.40, 0.40): exhibit-mode photo borders and footer.
  - Row shade `#EDF2FA` (0.93, 0.95, 0.98): video index alternating rows.
- Header (daily, every page): accent bold company name, then a black info line `<DOC TYPE>  |  <project>  |  <client>` left and the date label right-aligned, then a 1.2 pt accent rule across the page at y = 48.
- Header (exhibit, every page): black bold title, then 1 or 2 subtitle lines. No rule, no accent color.
- Footer (daily): centered 7 pt gray, `Page N  |  <counts>  |  Prepared by: <name>  |  Captured <date>`.
- Footer (exhibit): left-aligned 7.5 pt gray single line, `<legal_name>   |   <footer>`, baseline 30 pt above the page bottom.
- Determinism: PDF creation/mod dates come from the JSON `doc_date` key (never the clock), author is the company `legal_name`, and the file is saved with `no_new_id=True`, so identical data gives identical PDFs.
- Images: every source image is EXIF-orientation-corrected, downscaled to fit a max pixel bound (1500 px daily, 1800 px exhibit, overridable via `image_max_px`), and recompressed to JPEG quality 82 into `_prepped\` inside the output folder before insertion. This keeps a 13-photo log near 5 MB instead of 50 MB.

## Layout walkthrough

### Daily mode, photo pages

Top to bottom on every page (all coordinates in pt from top-left, margin m = 40):

1. Company line: `[COMPANY LEGAL NAME]` in caps at (40, baseline 30), 9 pt Helvetica-Bold, accent color.
2. Info line at baseline 42, 8 pt: left `DAILY PHOTO LOG  |  <project_label>  |  <client>` in black; right-aligned on the same baseline the `date_label` (e.g. `Date: Tuesday, 03/03/2026`).
3. Accent rule, 1.2 pt, from x=40 to x=572 at y=48.
4. Two photo slots with tops at y = 60 and y = 425. Each slot holds, in order:
   - If this photo starts a new section: an accent filled bar 14 pt tall across the full text width (x 40 to 572), with the section title in white 8 pt Helvetica-Bold caps, inset 6 pt from the left, baseline 10.5 pt into the bar. The title auto-shrinks to fit one line. The photo area then starts 20 pt below the slot top.
   - The photo, scaled to fit within 532 pt wide x 290 pt tall (minus 20 pt if a section bar is present), centered horizontally, with a 0.5 pt gray border on the image edge.
   - 12 pt below the image bottom, the label line in 7.5 pt Helvetica-Bold accent: `Photo NN  |  <display name>` plus `  |  <captured time>` when a per-photo capture time is given. Video stills get ` (video still)` appended to the display name.
   - 4 pt below the label baseline, the caption paragraph in 8 pt black, line height 1.15, wrapping in a box up to 52 pt tall (2 to 4 lines).
5. Footer, centered at baseline 770 (22 pt above bottom), 7 pt gray: `Page N  |  6 exhibits (4 photos + 2 video stills)  |  Prepared by: Pat Doe  |  Captured 03/03/2026`. With no video stills the counts read `6 exhibits (6 photos)`. The counts are computed from the data, not typed.

Photos flow two per page in data order; sections do NOT force a page break, so a section bar can start in the lower slot.

### Daily mode, optional Video Index page (last page)

1. Same company line and accent rule as photo pages, but the info line reads `VIDEO INDEX  |  <project_label>  |  <client>` and there is no right-aligned date.
2. Intro line at baseline 66, 8.5 pt black (from `video_index.intro_line`).
3. Note paragraph starting at y=78, 8 pt gray, line height 1.2, up to 30 pt tall (from `video_index.note`; say that clips are indexed by EXIF capture time and where the originals are kept).
4. Table starting at y=120: accent header bar 16 pt tall with white 8 pt bold column heads `FILE` (x=46), `TIME` (x=170), `ACTIVITY (INDEXED BY TIME)` (x=240). Then one 17 pt row per clip, 8 pt black, alternating rows shaded `#EDF2FA` (second row first). A 0.5 pt gray rectangle frames the whole table.
5. Footer, centered, 7 pt gray: `Video Index  |  <N> clips  |  Prepared by: <name>  |  Captured <captured_label>`.

### Exhibit mode (one photo per page)

1. Title at (54, baseline 54), 12 pt Helvetica-Bold black: `SAMPLE ELEMENTARY SCHOOL - SAMPLE ISD` style, all caps, project then owner.
2. Subtitle lines starting at baseline 70, one per list entry, 14 pt apart, 9.5 pt black. Line 1 names the document and pay app period; line 2 names the material, vendor reference, PO, and value.
3. The photo, top edge at y=100, scaled to fit 504 pt wide x 560 pt tall, centered horizontally, 0.6 pt gray border.
4. 16 pt below the image bottom, the metadata line in 9 pt Helvetica-Bold black: `File: IMG_0001.JPG   |   Captured: March 2, 2026 8:00 AM CST   |   GPS: 0.000100, 0.000100` (GPS segment omitted if the photo has no GPS).
5. 8 pt below that baseline, a paragraph block in 8.5 pt black, line height 1.25, up to 62 pt tall: first the fixed `metadata_note` lines (EXIF source sentence, then the location consistency sentence), then this photo's caption.
6. Footer at baseline 762 (30 pt above bottom), left-aligned, 7.5 pt gray: `Example Mechanical, LLC   |   PA No. 1 Stored-Material Backup   |   On-Site Delivery 03/02/2026`.

## Placeholders

Keys marked mode `daily` or `exhibit` are used only in that mode. Keys must match `sample_data.json` (daily) and `sample_data_exhibit.json` (exhibit). All example values below are invented.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| `mode` | string | yes | `"daily"` | `"daily"` or `"exhibit"`; selects the document type |
| `doc_date` | string | yes | `"2026-03-03"` | ISO date; sets PDF creation/mod metadata only (determinism), never printed |
| `output_filename` | string | yes | `"2026-03-03 Photo Log - Sample Elementary.pdf"` | exact output file name |
| `output_dir` | string | no | `"<job folder>/Daily Logs/Photo logs"` | defaults to `_sample_output` next to the script |
| `image_root` | string | yes | `"sample_photos"` or `"<job folder>/Photos/2026-03-03"` | folder that relative photo `file` names resolve against; a relative `image_root` resolves against the data file's folder; absolute `file` paths ignore it |
| `image_max_px` | number | no | `1500` | Pillow downscale bound; defaults 1500 (daily) / 1800 (exhibit) |
| `company_name` | string | no (daily) | `"EXAMPLE MECHANICAL, LLC"` | optional override for header line 1; omit it to use the company config `legal_name` in caps |
| `doc_type_label` | string | daily | `"DAILY PHOTO LOG"` | header line 2 left segment |
| `project_label` | string | daily | `"Sample Elementary School HVAC Replacement"` | header line 2 middle segment |
| `client` | string | daily | `"Sample ISD"` | header line 2 right segment |
| `date_label` | string | daily | `"Date: Tuesday, 03/03/2026"` | right-aligned header date; see Known variations for formats |
| `captured_label` | string | daily | `"03/03/2026"` | date(s) shown after "Captured" in the footer |
| `prepared_by` | string | no (daily) | `"Pat Doe"` | footer name; defaults to the company config `pm_name` |
| `sections` | array | daily | see sample | ordered activity groups |
| `sections[].title` | string | daily | `"ROOF CURBS SET AND FIELD MEASUREMENT"` | ALL CAPS bar text; add a date suffix like `" - 03/04/2026"` in multi-day logs |
| `sections[].photos` | array | daily | see sample | photos in print order, 2 per page |
| `sections[].photos[].file` | string | daily | `"daily_01.jpg"` | file name under `image_root`, or absolute path |
| `sections[].photos[].caption` | string | daily | `"New roof curb set at RTU-1..."` | 1 to 3 sentence caption; cite RFI/PCO numbers where relevant |
| `sections[].photos[].display` | string | no | `"IMG_0001.JPG"` | label name override; defaults to `file` without extension |
| `sections[].photos[].captured` | string | no | `"03/03/2026 9:15 AM"` | EXIF capture time appended to the label line; use when the photo verifies delivery or stored material |
| `sections[].photos[].video_still` | boolean | no | `true` | appends " (video still)" and counts it as a video still in the footer |
| `video_index` | object | no | see sample | include only when videos were taken that day |
| `video_index.intro_line` | string | with `video_index` | `"Date: Tuesday, 03/03/2026   |   3 video clips, listed by capture time"` | 8.5 pt intro under the header |
| `video_index.note` | string | with `video_index` | `"Clips are indexed by EXIF capture time and correlated to the day's activities. Originals retained in the job photo folder."` | gray explainer paragraph |
| `video_index.videos` | array | with `video_index` | see sample | one row per clip, in time order |
| `video_index.videos[].file` | string | with `video_index` | `"VID_0001.MOV"` | clip file name |
| `video_index.videos[].time` | string | with `video_index` | `"8:05 AM"` | EXIF capture time |
| `video_index.videos[].activity` | string | with `video_index` | `"Roof walk; RTU-1 curb set and dried in."` | short activity description |
| `title` | string | exhibit | `"SAMPLE ELEMENTARY SCHOOL - SAMPLE ISD"` | page title, PROJECT - OWNER, all caps |
| `subtitle_lines` | array of strings | exhibit | `["Stored Material Documentation - Pay Application No. 1 (Period 02/01/2026 to 02/28/2026)", "Div 23 HVAC Material: rooftop unit package, Sample Supply quote Q-1001, PO-1001 ($10,000.00)"]` | usually 2 lines: doc + period, then material + PO + value |
| `metadata_note` | array of strings | exhibit | `["Capture date, time, and GPS coordinates per embedded image metadata (EXIF, phone camera).", "Location: Sample Elementary School campus, 200 Example Avenue, Anytown, TX 75001 (on-site delivery)..."]` | fixed sentences repeated on every page above the caption; line 1 cites the EXIF source, line 2 ties GPS to the site or ship-to address |
| `footer` | string | no (exhibit) | `"PA No. 1 Stored-Material Backup   |   On-Site Delivery 03/02/2026"` | gray page-bottom line; the script puts the company `legal_name` in front |
| `photos` | array | exhibit | see sample | one page per photo |
| `photos[].file` | string | exhibit | `"IMG_0001.jpg"` | file name under `image_root`, or absolute path |
| `photos[].captured` | string | exhibit | `"March 2, 2026 8:00 AM CST"` | EXIF capture date/time with timezone; required in exhibit mode |
| `photos[].gps` | string | no | `"0.000100, 0.000100"` | EXIF GPS decimal degrees; omit only if the image has none |
| `photos[].caption` | string | exhibit | `"Delivery truck staged at the campus drive..."` | what the photo proves; name equipment tags, model/serial when visible |
| `photos[].display` | string | no | `"IMG_0001.JPG"` | file name override in the metadata line; defaults to `file` basename |

## Fixed wording

Hard-coded in the script, never changes between jobs:

- Daily photo label prefix: `Photo NN  |  ` (two-digit number, continuous across sections and pages).
- Video still suffix: ` (video still)` appended to the display name.
- Daily footer: `Page N  |  <T> exhibits (<P> photos + <V> video stills)  |  Prepared by: <name>  |  Captured <date>` and, with no stills, `<T> exhibits (<P> photos)`. Counts are computed.
- Video index header segment: `VIDEO INDEX  |  ` before project and client.
- Video index column heads: `FILE`, `TIME`, `ACTIVITY (INDEXED BY TIME)`.
- Video index footer: `Video Index  |  <N> clips  |  Prepared by: <name>  |  Captured <date>`.
- Exhibit metadata line: `File: <name>   |   Captured: <time>` and `   |   GPS: <lat, lon>` when present.
- Separator style: two spaces, pipe, two spaces (`  |  `) in daily mode; three spaces, pipe, three spaces (`   |   `) in exhibit mode.

Conventional values that live in the JSON but rarely change:

- `DAILY PHOTO LOG` (doc_type_label).
- `Capture date, time, and GPS coordinates per embedded image metadata (EXIF, phone camera).` (metadata_note line 1; name the camera type you actually used).
- No em dashes or en dashes anywhere; captions and labels use commas, periods, or hyphens.

## How to build

```
python build_photo_log.py [data.json] [--company path/to/company.json]
```

- No data argument: builds from `sample_data.json` in the script's folder (daily mode sample).
- Exhibit sample: `python build_photo_log.py sample_data_exhibit.json`
- Your own company: `python build_photo_log.py my_log.json --company ../../my_company.json`
- Output goes to `output_dir` (default `_sample_output\` next to the script) with the exact name in `output_filename`. Suggested naming patterns:
  - daily: `YYYY-MM-DD Photo Log - <Job Short Name>.pdf` (date range: `YYYY-MM-DD to DD Photo Log - <Job>.pdf`)
  - exhibit: `PA<N> Photos - <Subject> <MM-DD-YYYY> (<Job>, EXIF+GPS).pdf`
- The script prints `saved <path> pages: N exhibits: M` and exits 0. Prepped (downscaled) JPEG copies land in `<output_dir>\_prepped\`; they are intermediates and safe to delete.
- Requires: PyMuPDF (`import fitz`) and Pillow only. Source photos must exist at `image_root` + `file`.
- The sample data points at gray placeholder images in `sample_photos\`. Replace them with your own photos.

## Known variations

- **date_label formats:** `Date: Tuesday, 03/03/2026` (single day), `Date: Monday, 03/02/2026  (Delivery Day)` (single day with event tag), `Dates: 03/04 - 03/05/2026` (range). Match `captured_label` to it (e.g. `03/04 - 03/05/2026`).
- **project_label** can change during a job (for example when scope is added). Use whatever the job currently goes by.
- **Per-photo capture times** (`captured` in the label line) belong only on evidence-grade photos (delivery day, stored material); routine progress photos omit them and use descriptive file names instead.
- **Video Index page** belongs only on days with video clips. Omit the `video_index` key entirely on other days.
- **Section titles** carry a date suffix (`... - 03/04/2026`) in multi-day logs; the bar text auto-shrinks to fit.
- **Exhibit style:** raw full-page photos with no text are weak backup. Use the exhibit layout with the metadata line on every page.
- **GPS segment** is omitted per photo when the image has no GPS EXIF (for example a camera with location turned off); the capture time is still required.
- **File size:** daily logs run about 5 to 14 MB depending on photo count with the default 1500 px / quality 82 prep. Raise `image_max_px` only if a close-up needs more detail.
