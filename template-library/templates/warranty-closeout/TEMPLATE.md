# Warranty Close Out Letter

## Purpose and when to use
Formal letter (one page in the chiller style; the RTU style with terms and license block may run to a second page) issued to the customer at project closeout. It states that the work is complete, sets the workmanship warranty start date, lists the installed equipment (model, serials, electrical, refrigerant), summarizes warranty coverage and exclusions, and gives maintenance reminders. Issue it once per job, save it in the job's closeout folder, and usually convert it to PDF for sending.

## Output spec
- Format: .docx (python-docx), letter portrait 8.5 x 11 in
- Margins: left 0.33 in, right 0.33 in, top 0.44 in, bottom 0.30 in
- Font: Times New Roman throughout. Body 10 pt, letterhead address and label rows 9.5 pt, optional customer mailing block 8 pt
- Colors: black text; section labels (CUSTOMER NAME, PROPERTY NAME, PROPERTY ADDRESS, AUTHORIZED BY) in gray #9A9A9A bold; section dividers are 0.75 pt horizontal rules in #999999
- Header: none (letterhead is in the body). Footer: none
- Letterhead: [logo] top left at 2.0 in wide when the company config sets `logo_path`; otherwise the company DBA in 14 pt bold. Company address top right.
- docx author and last-modified-by are set to the company DBA from the company config

## Layout walkthrough
1. Letterhead row (borderless 2-column table): logo or company name left, right-aligned company address (2 lines) right.
2. Optional customer mailing block (8 pt, first line bold) and optional bold project title line.
3. Three-column label row in gray bold text: CUSTOMER NAME, PROPERTY NAME, PROPERTY ADDRESS at tab stops 2.62 in and 4.92 in, followed by the value row(s). Extra address lines wrap under the third column.
4. AUTHORIZED BY gray label, then the authorizing person line.
5. Horizontal rule, then bold heading PROJECT COMPLETION NOTICE and one paragraph stating what was installed, the completion date, and that this sets the start of the one year workmanship warranty.
6. Rule, bold heading EQUIPMENT INSTALLED, then one "Label: value" line per item (label bold).
7. Rule, bold heading WARRANTY COVERAGE, then "Label: value" lines (empty label prints a plain line).
8. Rule, bold heading IMPORTANT REMINDERS, then plain paragraphs (maintenance requirement + how to request warranty service, citing the job or project number).
9. Rule, bold heading ACCEPTANCE: acceptance statement paragraph, "Authorized By:" line, a blank line reserved for signature, then signer line(s).
10. Optional Terms of Service block.
11. Closing line: THANK YOU, WE APPRECIATE YOUR BUSINESS! plus an optional license block (see Known variations).

## Company config
Company and letterhead fields come from `template-library/company.example.json` (or the file you pass with `--company`). Copy that file, fill in your own values, and point `--company` at your copy.

| Config key | Used for |
|---|---|
| dba (falls back to legal_name) | letterhead name when there is no logo, docx author, default signer line |
| address_line1, city_state_zip | letterhead address block |
| logo_path | optional letterhead logo; null skips it and prints the company name instead. Relative paths resolve against the config file's folder |
| license | "Contractor License #:" line in the license block |
| pm_name, pm_title | default Authorized By and signer line when the data leaves them blank |

## Placeholders (job data JSON)
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| doc_date | string YYYY-MM-DD | yes | "2026-08-14" | drives docx created/modified metadata, keeps output deterministic |
| output_filename | string | no | "Warranty Close Out Letter - Sample Elementary School.docx" | default: "Warranty Close Out Letter - {property_name}.docx" |
| output_dir | string | no | absolute path | default: _sample_output next to the script |
| customer_contact_lines | string[] | no | ["Sam Roe", "Sample ISD", "200 Example Avenue", "Anytown, TX 75001"] | optional mailing block, first line bold |
| project_title | string | no | "Sample Elementary School HVAC Replacement" | optional bold title line |
| customer_name | string | yes | "Sample ISD" | column 1 |
| property_name | string | yes | "Sample Elementary School" | column 2, also used in the default filename |
| property_address_lines | string[] | yes | ["200 Example Avenue", "Anytown, TX 75001"] | column 3, extra lines wrap |
| authorized_by | string | no | "Sam Roe, Owner Representative" | blank uses pm_name from the config |
| completion_notice | string | yes | see sample | one paragraph; include scope, completion date, warranty start language |
| equipment | {label, value}[] | yes | see sample | label bold + ": value"; empty label prints a plain line |
| warranty_heading_suffix | string | no | "" | appended to the WARRANTY COVERAGE heading |
| warranty_lines | {label, value}[] | yes | see sample | same rendering as equipment |
| reminders | string[] | yes | see sample | plain paragraphs |
| acceptance_statement | string | no | default fixed sentence | override rarely |
| signers | string[] | no | [] | lines under the signature gap; empty uses "pm_name, pm_title - dba" from the config |
| payment_terms | string | no | "Net 30" | non-empty adds the Terms of Service block |
| include_license_block | bool | no | true | true adds the license line from the config plus license_extra_lines |
| license_extra_lines | string[] | no | ["[Regulatory notice required by your state licensing agency, if any]"] | other license numbers or a state-required regulatory notice |

## Fixed wording
- Labels: "CUSTOMER NAME", "PROPERTY NAME", "PROPERTY ADDRESS", "AUTHORIZED BY"
- Headings: "PROJECT COMPLETION NOTICE", "EQUIPMENT INSTALLED", "WARRANTY COVERAGE", "IMPORTANT REMINDERS", "ACCEPTANCE", "Terms of Service"
- "Authorized By:"
- Default acceptance: "The system has been installed to industry and manufacturer standards and is operational at close-out."
- "THANK YOU, WE APPRECIATE YOUR BUSINESS!"
- License block (when enabled): "Contractor License #: [license from config]" followed by any license_extra_lines.

## How to build
Requires Python 3 and python-docx.
```
python build_warranty_closeout.py [data.json] [--company path/to/company.json]
```
- `data.json` defaults to `sample_data.json` next to the script.
- `--company` defaults to `../../company.example.json` (the template-library root).

Output: `{output_dir}/{output_filename}` (.docx). The bundled `sample_data.json` uses only fake example data and writes to `_sample_output/`.

To convert to PDF on Windows with Word installed (PowerShell):
```
$w = New-Object -ComObject Word.Application; $d = $w.Documents.Open("<full path>.docx"); $d.SaveAs([ref]"<full path>.pdf", [ref]17); $d.Close(); $w.Quit()
```

## Known variations
- Chiller style: no customer mailing block, no terms, no license block. Leave customer_contact_lines, project_title and payment_terms empty and set include_license_block to false.
- RTU style: adds the 8 pt customer mailing block, a bold project title line, a Terms of Service block (payment_terms), and the license block (include_license_block true). The bundled sample uses this style.
- The equipment section repeats per unit on multi-unit jobs; add more {label, value} rows.
- Warranty lines vary by manufacturer (compressor vs parts vs labor splits); keep "Parts: N year (expires MM/DD/YYYY)" as the first line.
