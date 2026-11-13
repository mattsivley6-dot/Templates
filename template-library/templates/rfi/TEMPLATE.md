# RFI (Request for Information)

## Purpose and when to use
Formal question from the contractor to the Engineer of Record (or architect or owner rep) when field conditions, drawings, or specs need direction before work can proceed. Use it on any job where a condition differs from the contract documents (curb does not fit, unit lands on no steel, spec conflict, utility conflict). The RFI states the condition, asks a specific question, and proposes a resolution, flagging whether added scope will be priced as a change order. Send it as a PDF attachment by email; responses usually come back as email answers or stamped engineer details, so the document itself has no response or signature block.

## Output spec
- Format: PDF, generated with reportlab platypus (SimpleDocTemplate).
- Page size: letter (8.5 x 11 in), portrait.
- Margins: 58 pt (0.806 in) on all four sides. Usable width 496 pt.
- Fonts (reportlab built-ins, Helvetica):
  - Company header: Helvetica-Bold 13 pt, leading 15.
  - Document title "Request for Information": Helvetica-Bold 17 pt, leading 20. RFI number same style, right aligned.
  - Info table labels: Helvetica-Bold 10 pt; values Helvetica 10 pt, leading 13.
  - Section headers (BACKGROUND etc.): Helvetica-Bold 11 pt, leading 13, spaceBefore 9, spaceAfter 3.
  - Body paragraphs: Helvetica 10 pt, leading 12.6, spaceAfter 5.
  - Photo grid captions: Helvetica-Bold, centered, black; 12 pt suits 4 photos, 11 pt suits 2 photos.
  - Inline photo caption (single-photo variant): Helvetica-Oblique 9 pt, centered, gray #555555.
- Colors: all text black #000000. Info table grid lines 0.5 pt #999999; label column fill #f3f3f3. Horizontal rule under company name 1.1 pt black. This is a plain black and gray letter format with no colored section bars.
- Header/footer: none. No page numbers.
- PDF metadata: author from the company config `legal_name`, title from JSON pdf_title. Canvas built with invariant=1, so identical data yields a byte-identical PDF.

## Company config

Company data is never hard coded. The script reads `template-library/company.example.json` by default (two folders up from this script). Copy it, fill in your own company, and pass it with `--company`. Fields used:

| config key | used for |
|---|---|
| legal_name | company header line (upper case) and PDF author |
| pm_name | default From line ("pm_name, legal_name") when the data file leaves `from` empty |

No logo or signature is used by this template.

## Layout walkthrough
Page 1, top to bottom:
1. Company legal name, upper case, in Helvetica-Bold 13 pt at the top left.
2. Full-width horizontal rule, 1.1 pt black, 2 pt below the company name, 8 pt space after.
3. Title row: a 2-column borderless table (60% / 40% of usable width, zero side padding, bottom-aligned). Left cell "Request for Information" Helvetica-Bold 17 pt; right cell the RFI number (e.g. "RFI-001") same style, right aligned.
4. 7 pt spacer.
5. Info table: two columns, label column 1.7 in wide with #f3f3f3 fill, value column fills the rest. Full 0.5 pt #999999 grid, top-aligned cells, 6 pt side padding, 3 pt top/bottom padding. Rows in order: Project, Owner, Date, Response requested by (omitted when not supplied), To, From, Subject, References. Subject and References wrap to multiple lines.
6. 2 pt spacer.
7. "BACKGROUND" section header, then one body paragraph per JSON array entry.
8. "QUESTION" section header, then body paragraphs. Numbered options are written literally inside the paragraph text ("1.  Use a factory curb adapter...", two spaces after the number).
9. "PROPOSED RESOLUTION" section header, then body paragraphs. Long content overflows naturally to page 2.

Optional inline photo (single-photo variant), flowing directly after the resolution text (no page break): 18 pt spacer, one centered photo 3.4 in wide (height proportional, capped 8.0 in), 8 pt spacer, italic gray caption 9 pt centered.

Optional photo exhibit page (grid variant), on its own page after a PageBreak:
1. Heading in Helvetica-Bold 11 pt (e.g. "FIELD PHOTOGRAPHS (ONE PER UNIT)" or "FIELD PHOTOGRAPHS - RTU-2"), 8 pt space after.
2. Photo grid: 2 columns, each cell half the usable width. Photos are EXIF-rotated, downscaled to max 1500 px, recompressed JPEG quality 88. Each image scaled to a max display height (3.35 in when 3-4 photos in a 2x2 grid, 3.9 in when 1-2 photos in a single row) and max width cell minus 14 pt, centered. Bold black caption centered under each photo, 10 pt bottom padding. An odd photo count leaves the last cell empty.

## Placeholders
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| rfi_number | string | yes | "RFI-001" | Shown right of the title. "RFI-001" or "RFI 001" both work; pick one style per job. |
| output_filename | string | yes | "Sample_ES_RFI-001_RTU-2_Curb_Adapter.pdf" | Suggested pattern: `<Job>_RFI-###_<Short_Subject>.pdf` with underscores. |
| pdf_title | string | no | "Sample ES RFI-001 RTU-2 Curb Adapter" | PDF metadata title; defaults to rfi_number. |
| output_dir | string or null | no | null | null or absent = `_sample_output` next to the script. Relative paths resolve against the JSON file. For a real job point at the job's RFI folder. |
| project | string | yes | "Sample Elementary School HVAC Replacement, Sample ISD  \|  Project 2026-0001" | Keep the two-space pipe separator. |
| owner | string | yes | "Sample ISD" | |
| date | string | yes | "January 14, 2026" | Written date, spelled month. Never generated by the script. |
| response_requested_by | string | no | "January 17, 2026" | Often date + 3 calendar days. Omit or empty to drop the row. |
| to | string | yes | "Alex Poe, Sample Engineering, Inc. (Engineer of Record)" | Name, firm, role. Plain text; & is escaped automatically. |
| from | string | no | "Pat Doe, Example Mechanical, LLC" | Empty uses "pm_name, legal_name" from the company config. |
| subject | string | yes | "The new RTU-2 does not fit the existing curb. ..." | 1-3 plain sentences: condition + what is requested. |
| references | string | yes | "Drawing M-101 (Roof Plan). Spec section 23 74 13 (Packaged Rooftop Units). Related: PCO-001." | Spec sections, drawing sheets, related RFIs/PCOs. |
| background | array of strings | yes | ["We are replacing RTU-1 and RTU-2.", "..."] | One entry per paragraph. Short plain sentences. |
| question | array of strings | yes | ["How do you want us to set RTU-2? Please pick one:", "1.  Use a factory curb adapter..."] | Numbered options are literal text with two spaces after "1.". |
| proposed_resolution | array of strings | yes | ["We recommend option 1. ..."] | State what the contractor can do now vs what becomes a change order. |
| photo_page | object or null | no | see sample_data.json | Omit/null for no exhibit page. |
| photo_page.heading | string | yes (if photo_page) | "FIELD PHOTOGRAPHS (ONE PER UNIT)" | ALL CAPS. Use a hyphen, never a long dash. |
| photo_page.caption_font_size | number | no | 11 | Default 11. 12 suits a 4-photo grid. |
| photo_page.max_image_height_in | number | no | 3.9 | Default: 3.9 if 2 or fewer photos, else 3.35. |
| photo_page.photos | array of objects | yes (if photo_page) | [{"file": "sample_photos/RTU-1.jpg", "caption": "RTU-1"}] | file is absolute or relative to the JSON file. Caption renders bold. |
| inline_photo | object or null | no | null | Single-photo variant, flows after the resolution text. |
| inline_photo.file | string | yes (if inline_photo) | "sample_photos/RTU-2.jpg" | Absolute or relative to the JSON file. |
| inline_photo.caption | string | yes (if inline_photo) | "Field photograph: existing curb at RTU-2, looking north." | Long descriptive sentence, renders italic gray 9 pt. |
| inline_photo.width_in | number | no | 3.4 | Default 3.4 in. |

All JSON text is treated as plain text (XML special characters are escaped); inline markup tags are not supported. All values in `sample_data.json` are made up, and the images in `sample_photos/` are gray placeholders.

## Fixed wording
These strings live in the script and never change between jobs:
- "Request for Information" (document title)
- Info table labels, exact: "Project", "Owner", "Date", "Response requested by", "To", "From", "Subject", "References"
- Section headers, exact caps: "BACKGROUND", "QUESTION", "PROPOSED RESOLUTION"

The company header and PDF author come from the company config.

Writing voice for the variable text: short declarative sentences and plain words. Describe the condition as found, not who caused it. Always state what the contractor will do now versus what gets priced as a change order, and close the question with an ask for "a drawing or a written answer" or a stamped detail. Never use long dashes; use commas, periods, or hyphens.

## How to build
Requires Python 3, reportlab and Pillow (PyMuPDF optional, used only for the page-count check).

```
python build_rfi.py [data.json] [--company <path to company.json>]
```
- data.json defaults to sample_data.json in this folder.
- `--company` defaults to `../../company.example.json` relative to the script (the template-library root).
- Output: `<output_dir>/<output_filename>` (default `_sample_output/Sample_ES_RFI-001_RTU-2_Curb_Adapter.pdf`). The script prints "SAVED <path>" and the page count. Recompressed photo copies go to `<output_dir>/_tmp/` during the build and are removed afterward.

## Known variations
- RFI number style: "RFI-001" (hyphen) or "RFI 001" (space). Pass whichever via rfi_number and keep it consistent on a job.
- Project line: keep one wording for the whole job, for example "<Project>, <Owner>  |  <contract or bid number>".
- "Response requested by" row is optional; leave it out to get a 7-row table.
- Photo handling has three modes: none (one page of text), a single inline photo after the resolution with an italic gray caption, or a dedicated exhibit page with a 2-column grid of bold-captioned photos.
- Grid caption size and image height vary with photo count: 4 photos = 12 pt captions, 3.35 in images; 2 photos = 11 pt captions, 3.9 in images. The script defaults accordingly; both are overridable.
- A marked-up drawing (revision clouds on the engineer's sheet) is a different kind of RFI and is not built by this template.
- There is no engineer response block, signature line, or cost/schedule impact checkbox. Cost and schedule consequences are stated in prose inside PROPOSED RESOLUTION ("we will price it as a change order").
