# Site Walk / Field Meeting Minutes

## Purpose and when to use
Formal minutes for a site walk or field meeting (for example, a structural walk with the engineer). Records attendees, discussion by numbered section, and an action-items table with responsibilities and targets. File it with the job's field records, send it to the distribution list, and usually convert it to PDF.

## Output spec
- Format: .docx (python-docx), US Letter portrait. Margins 0.9 in left/right, 0.7 in top/bottom.
- Font: Arial. Title 15 pt bold in the brand primary color; project subtitle 11 pt bold; masthead lines 10 pt (bold labels); section headings 11 pt bold in the brand primary color; body 10.5 pt; attendee table 9.5 pt; action table 9 pt; notes and closing 9 pt italic gray #595959.
- Table header rows shaded #E8EBF2.
- Deterministic: docx created/modified dates and zip entry timestamps come from doc_date.
- Document author and last-modified-by are set from the company config legal_name.

## Layout walkthrough
1. Title (doc_title, default "SITE WALK / FIELD MEETING MINUTES") in brand color, bold.
2. Project subtitle line (project_line), bold.
3. Masthead lines, each "Label:  value": Owner, Solicitation, Contractor, Engineer, Walk Date, Location, Prepared By, Distribution.
4. "Attendance" heading, then the attendees table (Name / Organization / Role, shaded header), then an optional italic gray attendance note.
5. Discussion sections numbered "1.0", "2.0", ... with items numbered "1.1", "1.2", ... (bold number, indented 0.35 in).
6. "Action Items" heading numbered as the last section, then a 4-column table (No. / Action / Responsible / Target, widths 0.4 / 4.6 / 1.7 / 1.3 in). Rows are numbered automatically.
7. Closing record statement in italic gray (fixed wording, plus optional closing_extra).

## Company config
Company fields come from `template-library/company.example.json` (or your own copy passed with `--company`):

| Config key | Used for |
|---|---|
| legal_name | Default for `contractor`; default company in `prepared_by`; docx author and last-modified-by |
| brand.primary_color | Title and section heading color |
| pm_name, pm_title | Default for `prepared_by` when the data file leaves it out |

logo_path and signature_path are not used by this template.

## Placeholders
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| doc_title | string | no | "SITE WALK / FIELD MEETING MINUTES" | default shown |
| project_line | string | yes | "Sample Elementary School HVAC Replacement  \|  RTU-1 Deck Condition" | project name and walk subject |
| owner | string | yes | "Sample ISD" | |
| solicitation | string | yes | "Project 2026-0001" | contract, solicitation or project number |
| contractor | string | no | "Example Mechanical, LLC" | defaults to company legal_name |
| engineer | string | yes | "Sample Engineering, Inc." | |
| walk_date | string | yes | "Wednesday, March 11, 2026, approximately 8:00 AM" | |
| location | string | yes | "Sample Elementary School, 200 Example Avenue, Anytown, TX 75001, rooftop at RTU-1" | |
| prepared_by | string | no | "Pat Doe, Project Manager, Example Mechanical, LLC" | [PM Name], [PM Title], [Company Legal Name]; defaults from the company config |
| distribution | string | yes | "All attendees and project file" | |
| doc_date | string YYYY-MM-DD | yes | "2026-03-11" | determinism anchor |
| output_basename | string | yes | "Sample_ES_Site_Walk_Minutes_2026-03-11" | ".docx" is appended |
| output_dir | string | no | "_sample_output" | relative paths resolve against the script folder; default _sample_output |
| attendees[] | {name, organization, role} | yes | {"name": "Alex Poe", "organization": "Sample Engineering, Inc.", "role": "Engineer of Record"} | |
| attendance_note | string | no | "Also on site: the roofing crew." | italic note under the table |
| sections[] | {title, items[]} | yes | {"title": "Purpose", "items": ["Walk the roof at RTU-1..."]} | discussion sections |
| action_items[] | {action, responsible, target} | yes | {"action": "Price the repair and submit PCO-001", "responsible": "Contractor", "target": "After detail"} | numbered automatically |
| closing_extra | string | no | | appended to the closing statement |

## Fixed wording
- Headings "Attendance" and "Action Items".
- Table headers: Name / Organization / Role; No. / Action / Responsible / Target.
- Masthead labels: Owner, Solicitation, Contractor, Engineer, Walk Date, Location, Prepared By, Distribution.
- Closing statement: "These minutes reflect the writer's understanding of the items discussed and the conclusions reached on the site walk. Please direct any corrections or additions to the writer within five (5) business days of receipt; otherwise, these minutes will stand as the record of the walk."

Everything else is data or company config.

## How to build
```
py -3 build_site_walk_minutes.py [data.json] [--company path\to\company.json]
```
- No data argument: uses `sample_data.json` in this folder.
- No `--company`: uses `../../company.example.json` (relative to this script). Point it at your own company file for real use.
- Output: `{output_dir}/{output_basename}.docx`, for example `_sample_output/Sample_ES_Site_Walk_Minutes_2026-03-11.docx`.
- For PDF, open the docx in Word and Save As PDF (or script it with Word COM, as shown in the daily-log TEMPLATE.md).

## Known variations
- Section count and titles vary per walk. An empty action_items list renders the heading and the table header row only.
