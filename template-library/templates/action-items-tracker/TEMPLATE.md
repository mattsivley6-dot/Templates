# Open Items / Action Tracker

## Purpose and when to use
Running action-item tracker for an active job: numbered items with owner, due date, priority and status. Reissue it as items change (file date in the name) and attach it to OAC or field meeting agendas as needed.

## Output spec
- Format: .docx (python-docx). Orientation from JSON: "landscape" (default) or "portrait".
- Font: Arial. Company name line in the brand primary color from the company config; info lines gray #595959; table header shaded #E8EBF2; High priority red #B00020 (portrait profile).
- Deterministic: docx dates and zip timestamps come from doc_created_iso.
- Document author and last-modified-by are set from the company config legal_name.

## Layout walkthrough
Company name line (company config legal_name, upper case, brand color); title "OPEN ITEMS / ACTION TRACKER"; three gray info lines (project and owner with optional CSP number, source line, prepared by and updated date); a spacer (landscape) or brand-color rule (portrait); items table with a shaded header row (# / Action item / Owner / Due / Pri. / Status), one row per item; italic legend line under the table.

## Company config
Company fields come from `template-library/company.example.json` (or your own copy passed with `--company`):

| Config key | Used for |
|---|---|
| legal_name | Company name line at the top (upper case); docx author and last-modified-by |
| brand.primary_color | Company name line color and the portrait header rule |

logo_path and signature_path are not used by this template.

## Placeholders
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| file_date_label | string | yes | "2026-03-10" | goes in the filename |
| project_short | string | yes | "Sample ES" | goes in the filename |
| orientation | string | no | "landscape" | or "portrait"; default landscape |
| project_name | string | yes | "Sample Elementary School HVAC Replacement" | |
| owner | string | yes | "Sample ISD" | |
| csp_number | string | no | "2026-0001" | rendered as "CSP #2026-0001"; omit or leave empty to drop |
| source_line | string | yes | "Snapshot from the Daily Construction Report DCR-2026-0310 and the OAC Meeting (03/10)" | where the items came from |
| prepared_by | string | yes | "Pat Doe, Project Manager" | [PM Name], [PM Title] |
| updated_date | string | yes | "March 10, 2026" | display date |
| legend_text | string | no | priority / status legend | omit for the profile default |
| highlight_high_priority | bool | no | true | overrides the profile default |
| doc_created_iso | string YYYY-MM-DDTHH:MM:SS | yes | "2026-03-10T17:00:00" | determinism anchor |
| output_dir | string | no | "_sample_output" | relative paths resolve against the script folder |
| items[] | {id, action, owner, due, priority, status} | yes | see sample_data.json | priority is High, Med or Low |

## Fixed wording
Title "OPEN ITEMS / ACTION TRACKER", the info-line prefixes ("Project: ", "Owner: ", "CSP #", "Prepared by: ", "Updated: ") and the table header row (# / Action item / Owner / Due / Pri. / Status). Everything else is data or company config.

## How to build
```
py -3 build_action_items_tracker.py [data.json] [--company path\to\company.json]
```
- No data argument: uses `sample_data.json` in this folder.
- No `--company`: uses `../../company.example.json` (relative to this script). Point it at your own company file for real use.
- Output: `{output_dir}/{file_date_label} Action Items - {project_short}.docx`, for example `_sample_output/2026-03-10 Action Items - Sample ES.docx`.
- Fails (exit 1) on an em or en dash in the data, an empty items list, a missing item field, or a priority other than High, Med or Low.

## Known variations
- The orientation switch changes margins, column widths and the header divider; the portrait profile shows High priority in bold red and has no default legend.
