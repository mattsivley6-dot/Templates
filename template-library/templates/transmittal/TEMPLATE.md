# Transmittal / Submittal Cover Sheet

## Purpose and when to use
Cover document for every submittal package sent to the engineer of record (product data, engineering drawings, samples). Up to three parts in one docx: (1) the TRANSMITTAL form, (2) the SUBMITTAL COVER SHEET, (3) an optional SUBMITTAL INDEX page with a known-deviations table. Save it in the job's submittals folder next to the package it covers, then convert to PDF and merge it ahead of the submittal contents.

## Output spec
- Format: .docx (python-docx), letter portrait 8.5 x 11 in, one part per page (explicit page breaks)
- Margins: 0.75 in all sides
- Font: Arial. Company name 11 pt bold; page title TRANSMITTAL 14 pt bold centered; section headings 10 pt bold; table text 9 pt; review/deviation statements 8.5 pt
- Colors: navy #1F3864 banner cells and index-table header rows with white bold text; light blue #DEEAF1 fill on the QUANTITY/DATED/DESCRIPTION header row; thin black table grid borders
- Checkboxes are literal "x" marks in the option cell or before the option label
- docx author and last-modified-by are set to the company DBA from the company config

## Layout walkthrough
Page 1, TRANSMITTAL: company letterhead block (company name + address, city/state/zip, phone, website from the company config); centered TRANSMITTAL title; DATE row; a 4-column block with TO/ATTN/address lines on the left and the VIA checklist (U.S. MAIL, HAND DELIVERED, LOCAL DELIVERY, OVERNIGHT SHIPMENT, Email) on the right with one option marked; PROJECT / PROJECT # row; TRANSMITTED checklist (HEREWITH or SEPARATELY marked) with the ITEM checklist under it, two options per row, each listed once (ORIGINAL DRAWINGS, PRINTS, SPECIFICATIONS, COPY OF LETTER, SUBMITTALS, SAMPLES, OTHER); QUANTITY/DATED/DESCRIPTION table (light blue header, minimum 4 body rows, blanks left empty); REMARKS row; By: row.

Page 2, SUBMITTAL COVER SHEET: navy banner with title and division line; PROJECT heading + label/value table (project name, contract number, engineer project number, location, date, submittal number, submittal type); ENGINEER heading + firm/attention/address; contractor heading (varies by trade) + firm/contact/address/phone (from the company config unless the data overrides it); optional third-party heading (subcontractor or supplier) + fields; CONTRACTOR ACTION heading with the APPROVED / APPROVED AS NOTED / REJECTED row (left unmarked when sending, the engineer marks it); the contractor review statement in 8.5 pt; Contractor Signature / name / Date row.

Page 3 (optional), SUBMITTAL INDEX: navy banner; ITEMS SUBMITTED heading + Item/Description/Spec Section table (navy header); KNOWN DEVIATIONS FROM CONTRACT DOCUMENTS heading, the deviations note, and a No./Deviation/Spec Ref./Severity table (navy header, minimum 3 blank rows).

## Company config
Company and letterhead fields come from `template-library/company.example.json` (or the file you pass with `--company`). Copy that file, fill in your own values, and point `--company` at your copy.

| Config key | Used for |
|---|---|
| legal_name (falls back to dba) | letterhead name, contractor Firm |
| dba (falls back to legal_name) | docx author / last modified by |
| address_line1, city_state_zip | letterhead, contractor Address |
| phone, website | letterhead (phone also contractor Phone) |
| pm_name, pm_title | default By: and Contractor Signature name, contractor Contact |

logo_path, signature_path and brand colors are not used by this template.

## Placeholders (job data JSON)
| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| doc_date | string YYYY-MM-DD | yes | "2026-03-02" | drives docx metadata and zip timestamps (determinism) |
| output_filename | string | yes | "J-0001_Transmittal_SampleSupply_Div23_ProductData.docx" | pattern: {Job}_Transmittal_{Sub or Vendor}_{Div}_{Subject}.docx |
| output_dir | string | no | absolute path | default _sample_output |
| pdf_title | string | no | "Transmittal - Division 23 Product Data Submittal" | docx Title property |
| transmittal.date | string | yes | "3/2/2026" | short date format on the form |
| transmittal.to | string | yes | "Sample Engineering, Inc." | |
| transmittal.attn | string | yes | "Alex Poe" | |
| transmittal.to_address_lines | string[] | no | ["100 Sample Street, Suite 300", "Anytown, TX 75000"] | |
| transmittal.via | string | no | "Email" | must equal one VIA option exactly to get the x |
| transmittal.project | string | yes | "Sample Elementary School HVAC Replacement" | |
| transmittal.project_number | string | yes | "2026-0001 / J-0001" | contract and/or job number |
| transmittal.transmitted | string | no | "HEREWITH" | or "SEPARATELY" |
| transmittal.items | string[] | no | ["SUBMITTALS"] | subset of the ITEM options, exact spelling |
| transmittal.lines | {quantity,dated,description}[] | yes | see sample | one row per package item |
| transmittal.remarks | string | no | see sample | |
| transmittal.by | string | no | "" | blank uses pm_name from the company config |
| cover_sheet.enabled | bool | no | true | false skips page 2 |
| cover_sheet.division_line | string | yes* | "Division 23 00 00  -  Heating, Ventilating and Air Conditioning" | banner subtitle |
| cover_sheet.project_fields | [label, value][] | yes* | 7 rows, see sample | keep the field order |
| cover_sheet.engineer_fields | [label, value][] | yes* | firm/attention/address | |
| cover_sheet.contractor_heading | string | no | "PRIME CONTRACTOR / HVAC CONTRACTOR" | default "PRIME CONTRACTOR / GENERAL CONTRACTOR" |
| cover_sheet.contractor_fields | [label, value][] | no | omit | omit to build firm/contact/address/phone from the company config |
| cover_sheet.third_party_heading | string | no | "HVAC EQUIPMENT SUPPLIER" | e.g. "ELECTRICAL SUBCONTRACTOR" |
| cover_sheet.third_party_fields | [label, value][] | no | firm/contact/email/PO | omit to skip the block |
| cover_sheet.action_marked | string | no | "" | leave empty when sending; the engineer marks it |
| cover_sheet.action_statement | string | yes* | see sample | trade-specific review sentence |
| cover_sheet.signature_name | string | no | "" | blank uses pm_name from the company config |
| cover_sheet.signature_date | string | yes* | "March 2, 2026" | long date format |
| index.enabled | bool | no | true | false/omit skips page 3 |
| index.division_line | string | no | "Division 23 00 00  -  Heating, Ventilating and Air Conditioning" | |
| index.rows | [item, description, spec][] | no | see sample | |
| index.deviations_note | string | yes* | see sample | cite the spec section that governs deviations on your project |
| index.deviations | [no, deviation, ref, severity][] | no | [] | empty leaves 3 blank rows |

(* required when that part is enabled)

## Fixed wording
- Titles: "TRANSMITTAL", "SUBMITTAL COVER SHEET", "SUBMITTAL INDEX"
- Form labels: "DATE:", "TO:", "ATTN:", "VIA:", "PROJECT:", "PROJECT #", "TRANSMITTED:", "ITEM:", "QUANTITY", "DATED", "DESCRIPTION", "REMARKS:", "By:", "Contractor Signature:", "Date:"
- Option lists: VIA (U.S. MAIL, HAND DELIVERED, LOCAL DELIVERY, OVERNIGHT SHIPMENT, Email); ITEM (ORIGINAL DRAWINGS, PRINTS, SPECIFICATIONS, COPY OF LETTER, SUBMITTALS, SAMPLES, OTHER); actions (APPROVED, APPROVED AS NOTED, REJECTED)
- Headings: "PROJECT", "ENGINEER", "CONTRACTOR ACTION", "ITEMS SUBMITTED", "KNOWN DEVIATIONS FROM CONTRACT DOCUMENTS"

## How to build
Requires Python 3 and python-docx.
```
python build_transmittal.py [data.json] [--company path/to/company.json]
```
- `data.json` defaults to `sample_data.json` next to the script.
- `--company` defaults to `../../company.example.json` (the template-library root).

Output: `{output_dir}/{output_filename}` (.docx). The bundled `sample_data.json` uses only fake example data (Sample ISD, Sample Engineering, Example Mechanical) and writes to `_sample_output/`.

To convert to PDF on Windows with Word installed (PowerShell):
```
$w = New-Object -ComObject Word.Application; $d = $w.Documents.Open("<full path>.docx"); $d.SaveAs([ref]"<full path>.pdf", [ref]17); $d.Close(); $w.Quit()
```

## Known variations
- Trade wording changes per submittal: contractor heading, third-party heading, division line, and the contractor review statement. Example for an electrical submittal: "Contractor has reviewed the submitted product data against the Division 26 specifications and forwards it to the Engineer for review."
- The index page usually appears only on engineering-drawing submittals; product-data submittals are often 2 parts (set index.enabled to false).
