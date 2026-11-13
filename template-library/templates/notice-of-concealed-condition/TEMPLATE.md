# Notice of Concealed Condition (Certified-Mail Claim Letter)

## Purpose and when to use
One-page formal certified-mail letter giving written notice of a concealed or hidden condition under the contract's concealed-condition, claims, and notice sections. It reserves rights, serves as the Notice of Claim, and asks the recipient to execute the related PCO as a Change Order. Usually issued in paired variants per event: the same body to the Owner and to the Engineer, each with its own address block, salutation, and cc list. One run emits one PDF per recipient. File the PDFs in the job's change order folder with the certified-mail receipts.

## Output spec
- Format: PDF (reportlab invariant=1 + PyMuPDF metadata pass; byte-deterministic including the trailer /ID)
- Page: letter portrait, 1 in side margins
- Letterhead (generic, built from the company config): company DBA in the brand primary color on the left (or the logo, if `logo_path` is set), legal name under it when it differs, gray 8.5 pt contact block on the right (address, city/state/zip, phone, website), accent-color rule under the masthead; light gray footer rule with a centered gray one-line company footer
- Font: Helvetica. Body 10.5 pt; certified-mail banner 9 pt bold gray; cc block 8.5 pt gray
- Numbered body paragraphs get a hanging indent; the gap is tighter between consecutive numbered items
- Optional signature image above the typed signature block; with none, the gap stays for a wet signature
- PDF author is the company DBA from the config

## Layout walkthrough
Masthead; date line; bold gray "SENT BY CERTIFIED MAIL, RETURN RECEIPT REQUESTED"; recipient address block; bold wrapped Re: line; salutation; body paragraphs (opening notice sentence citing the contract sections, then numbered facts: what was found and when, work stopped + RFI sent, engineer direction, schedule position, reservation of rights, request to execute the PCO); "Respectfully,"; optional signature image; typed signature block (name, title, company, direct phone | email); gray cc block.

## Company config
Company and letterhead fields come from `template-library/company.example.json` (or the file you pass with `--company`). Copy that file, fill in your own values, and point `--company` at your copy.

| Config key | Used for |
|---|---|
| dba (falls back to legal_name) | masthead name, PDF author |
| legal_name | line under the masthead name (when different), footer, signature block company line |
| address_line1, city_state_zip, phone, website | masthead contact block and footer |
| brand.primary_color | masthead name color |
| brand.accent_color | masthead rule color |
| logo_path | optional logo in place of the masthead name; null skips it |
| signature_path | optional signature image; null leaves a wet-signature gap |
| pm_name, pm_title, pm_phone, pm_email | default typed signature block |

Relative `logo_path` and `signature_path` values resolve against the config file's folder.

## Placeholders (letter data JSON)
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| meta.pdf_title | string | yes | "Notice of Concealed Condition and Reservation of Rights - Corridor Ceiling" | PDF metadata |
| meta.created | string YYYY-MM-DD | no | "2026-03-12" | drives PDF dates (determinism) |
| meta.file_ref | string | no | "PCO-001" | goes into the output filename |
| meta.job_slug | string | yes | "J-0001" | filename prefix |
| meta.output_dir | string | no | absolute path | default _sample_output |
| letter.date_display | string | yes | "March 12, 2026" | long date |
| letter.re_text | string | yes | see sample | include the leading "Re: "; cite PCO, condition, location, project, contract or solicitation number |
| letter.body_paragraphs | string[] | yes | see sample | start numbered items with "N. "; they get the hanging indent |
| letter.signature_lines | string[] | no | [] | empty uses pm_name, pm_title, legal_name and "Direct pm_phone  \|  pm_email" from the config |
| letter.signature_image | string or null | no | null | overrides the config signature_path; path absolute or relative to the data file's folder |
| recipients[].tag | string | yes | "Owner", "Engineer" | filename suffix |
| recipients[].address_lines | string[] | yes | see sample | |
| recipients[].salutation | string | yes | "Mr. Roe:" | |
| recipients[].cc_lines | string[] | no | see sample | first line gets the "cc:  " prefix |

## Fixed wording
- "SENT BY CERTIFIED MAIL, RETURN RECEIPT REQUESTED"
- "Respectfully,"
- "cc:  " prefix
- Standard opening sentence pattern: "Formal written notice under Contract Sections [A], [B], and [C]. This reserves our rights and serves as our Notice of Claim, sent by certified mail as Section [C] requires." Fill in the concealed-condition, claims, and notice section numbers from your own contract.

## How to build
Requires Python 3, reportlab and PyMuPDF.
```
python build_notice_of_concealed_condition.py [data.json] [--company path/to/company.json]
```
- `data.json` defaults to `sample_data.json` next to the script.
- `--company` defaults to `../../company.example.json` (the template-library root).

Output per recipient: `{job_slug}_{file_ref}_Notice_of_Concealed_Condition_{tag}.pdf`. The bundled `sample_data.json` uses only fake example data and writes two letters (Owner and Engineer) to `_sample_output/`. The script REFUSES data containing em or en dashes, and stops if the letter runs past one page.

## Known variations
- Owner and Engineer variants differ only in address block, salutation, and cc list. A separate event gets its own body and its own pair of letters.
- Contract section numbers follow the specific contract. Cite the concealed-condition, change, claims, and notice sections, and the section that governs change order execution.
- If you are working under a written go-ahead, say so and give its date and any limits it sets.
