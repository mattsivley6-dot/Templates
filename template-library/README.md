# Template Library

Repeatable, script-built templates for the documents a commercial HVAC or construction project manager produces on every job. Each template folder holds the full recipe to rebuild one document for any job:

- `TEMPLATE.md`: the spec (layout, colors, fonts, every placeholder, and the fixed wording).
- `build_<key>.py`: a self-contained Python generator.
- `sample_data.json`: made-up example data for a fictional job.
- `_sample_output/`: the document the generator produced from that fake data.

All sample data and sample outputs use fictional names and numbers (Example Mechanical, LLC; Sample ISD; Sample Elementary School HVAC Replacement; job J-0001). Nothing in this library comes from a real job.

## Company settings: `company.example.json`

Every generator reads your company and letterhead fields from one shared file, `company.example.json`, in this folder. No company data is hard-coded in any script.

| Key | Used for |
|---|---|
| `legal_name`, `dba` | Letterhead, signature blocks, legal text |
| `address_line1`, `city_state_zip` | Letterhead address |
| `phone`, `email`, `website` | Letterhead contact line |
| `license` | License line where a document shows one |
| `logo_path` | Logo image, or `null` for no logo |
| `signature_path` | Signature image, or `null` for no signature |
| `pm_name`, `pm_title`, `pm_phone`, `pm_email` | Default signer and contact block |
| `brand.primary_color`, `brand.accent_color`, `brand.font` | Brand color and font (see STYLE.md) |

To use the library for your own company:

1. Copy `company.example.json` to a new file (for example `company.json`) and fill in your values. Keep the keys the same.
2. Leave `logo_path` and `signature_path` as `null` to skip the images, or point them at your own image files.
3. Pass your file to any generator with `--company`. Without the option, each generator uses `company.example.json`, found two folders up from the script (`templates/<key>/` to this folder).

Keep your filled-in config, signature image and real job data out of any public copy of this library.

## How to run a generator

1. Open `templates/<key>/TEMPLATE.md` and read it fully. It defines the output, every placeholder, and the wording that must not change.
2. Copy `sample_data.json` to a working file (for example `data.json`) and edit the values for your job. Do not invent new keys; the placeholder table in TEMPLATE.md is the full list.
3. From the template folder, run:
   ```
   python build_<key>.py data.json --company path/to/company.json
   ```
   On Windows, `py -3` works in place of `python`.
4. Most generators write to `_sample_output/` unless the data file sets an output folder; TEMPLATE.md says where each one writes. Copy the result into your job folder; do not edit the library copy in place.
5. Do not change fixed wording, colors, fonts or layout in the scripts. If a job needs a variation, check "Known variations" in TEMPLATE.md first.

### Rules every generator follows

- No em dashes or en dashes in any document, data file or file name. Use commas, periods or hyphens. Several scripts reject data that contains them.
- Same data in, same document out. Scripts never read the clock and never use random values; every date comes from the data file.

## Catalog (in job lifecycle order)

| Key | Document | Output | When used |
|---|---|---|---|
| capacity-letter | Bonding capacity correspondence packet | Letter-packet PDF | Bid or prequalification: showing bonding capacity to an owner |
| transmittal | Transmittal / submittal cover sheet | docx (2 to 3 parts) | Every submittal package to the engineer |
| duct-shop-ticket | Duct transition shop ticket | PDF, schedule plus isometric per fitting | Releasing duct fabrication to the shop |
| rfi | RFI (Request for Information) | PDF, optional photo exhibit pages | Field questions to the engineer |
| daily-report | Daily report | PDF per day (brand accent color) | Every working day in the field |
| daily-log | Daily log | See TEMPLATE.md | Field log record |
| photo-log | Photo log / exhibit | PDF with photo date and location citations | Dated photo documentation, stored-material proof |
| site-walk-minutes | Site walk / field meeting minutes | docx | After walks with the engineer or owner |
| oec-meeting-minutes | Owner, engineer and contractor (OEC/OAC) meeting minutes | See TEMPLATE.md | Recurring owner meetings |
| action-items-tracker | Open items / action tracker | docx (landscape) | Running job punch and action list |
| notice-of-concealed-condition | Certified-mail notice of concealed condition | PDF per recipient | Hidden condition found: formal notice and claim reservation, pairs with a PCO |
| pco | PCO (Proposed Change Order) package | PDF (grayscale, signature-ready) | Pricing changed or concealed work |
| pco-email-cover | PCO email cover note | Text | Sending a PCO by email |
| pay-app | Pay application with schedule of values | PDF, cross-footed math | Monthly billing |
| project-binder | Project binder (registers and core sections) | PDF set | Job close: submittal, RFI and PCO registers, contacts |
| warranty-matrix | Warranty matrix and binder assembly | PDF | Closeout: equipment warranty summary plus merged manufacturer warranties |
| warranty-closeout | Warranty closeout letter | docx | Final letter to the customer setting the warranty start date |

Ideas for future templates: owner notice letter, bid tabulation, sub or equipment RFQ package, OAC status slide deck. Add them by following the same pattern.

## Requirements

- Python 3 with python-docx, reportlab, PyMuPDF (`import fitz`) and Pillow.
- Optional, for docx to PDF on Windows with Microsoft Word installed (PowerShell):
  ```
  $w = New-Object -ComObject Word.Application; $d = $w.Documents.Open("<full path>.docx"); $d.SaveAs([ref]"<full path>.pdf", [ref]17); $d.Close(); $w.Quit()
  ```
- Determinism built into the scripts: no `datetime.now` or `today`, no random values; reportlab `Canvas(invariant=1)`; docx core properties and zip entry timestamps pinned from the data file's date; PyMuPDF trailer `/ID` rewritten from a content hash where PyMuPDF is used.

## Suggested job folder layout

Generated documents are easiest to find when every job uses the same numbered subfolders, for example:

```
<jobs root>/<year>/<job name>/
  01 Bid and Award
  02 Contract and Bonds
  04 Submittals
  05 RFIs
  06 Change Orders
  08 Pay Apps
  12 Daily Logs
  13 Photos
  14 Project Binder
  15 Daily Reports
```

Save each generated document in the matching subfolder using the file naming patterns in STYLE.md.
