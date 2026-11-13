# Bonding Capacity Correspondence Packet

## Purpose and when to use
A formal letter on company letterhead stating the company's surety bonding
capacity (aggregate capacity, single project limit, unencumbered capacity,
optional premium note), with the surety broker's written confirmation merged in
behind it as an enclosure. Used when a public-entity solicitation (RFP, RFQ,
CSP, qualification form) asks the bidder to document bonding capacity. Build it
as soon as the surety broker confirms the numbers in writing (usually by email;
print that email to PDF and enclose it), and file the packet with the proposal
or qualification statement. The letter carries your company's voice; the
enclosure carries the broker's proof.

## Output spec
- Format: PDF (single merged packet: letter pages + enclosure pages).
- Page size: letter, 8.5 x 11 in, portrait.
- Margins (letter pages): left 0.75 in, right 0.75 in, top 1.35 in (clears the
  letterhead masthead, whose rule sits 88 pt from the top edge), bottom 0.87 in
  (clears the footer rule at 46 pt and the running line at 55 pt).
- Fonts: Helvetica family (core PDF font, no embedding).
  - Wordmark (company DBA, upper case): Helvetica-Bold 22 pt, shrinks to fit
    long names (minimum 12 pt).
  - Wordmark subline "LICENSE <license>": Helvetica 7 pt, letter-spaced.
  - Masthead address block: Helvetica 7.6 pt, right aligned.
  - Body text: Helvetica 10 pt, leading 13.5, space after 7 pt.
  - Address/signature/enclosure lines: Helvetica 10 pt, leading 13, no space after.
  - Section headings: Helvetica-Bold 12 pt, leading 15, space before 8 / after 5 pt.
  - Premium note: Helvetica 9 pt, leading 11.5, left indent 8 pt.
  - Table cells: Helvetica 10 pt (labels Helvetica-Bold); header row Helvetica-Bold
    10 pt white.
  - Footer company line: Helvetica 6.8 pt centered; running line: Helvetica 7.2 pt
    right aligned.
- Colors: accent color from the company config `brand.accent_color` (wordmark,
  masthead rule; falls back to #2E7D32), primary color from `brand.primary_color`
  (section headings and table header bar; falls back to #1F3A5F), gray #595959
  (secondary text, masthead address, footer), light gray #BFBFBF (footer
  hairline), ink #1A1A1A (body text), label fill #eef2f7, grid #cccccc, note gray
  #555555, header text white.
- Header (every letter page): the company logo top left if the config has a
  `logo_path`, otherwise the company DBA as a text wordmark with the license
  number under it; right-aligned gray address block (address line, city/state/zip,
  phone, website from the config); 1.4 pt accent-color rule across the page 88 pt
  from the top.
- Footer (every letter page): 0.5 pt light-gray hairline at y=46 pt; centered
  company line (legal name | address | phone | website) at y=36 pt; right-aligned
  running line at y=55 pt reading
  "Bonding Capacity Correspondence    |    <date_display>    |    Page N".
- Enclosure pages keep their own native formatting (no header/footer is stamped
  on them).
- PDF metadata: title = meta.pdf_title, author = meta.pdf_author if given, else
  the company config `legal_name`; creation and modification dates from
  meta.created. Deterministic: identical JSON gives byte-identical PDFs
  (reportlab invariant=1 plus a content-hash trailer /ID).

## Company config
The script reads company fields from `template-library/company.example.json`
(two folders up from this one) unless you pass `--company path/to/your_company.json`.
Copy the example, fill in your own values and point `--company` at it.

| config key | used for |
|---|---|
| dba | text wordmark (when there is no logo) |
| legal_name | footer company line, default PDF author, default signature company |
| address_line1, city_state_zip, phone, website | masthead address block and footer |
| license | wordmark subline |
| logo_path | optional logo image, drawn top left in place of the text wordmark; null = text wordmark; a relative path resolves against the config file's folder |
| pm_name, pm_title, pm_phone, pm_email | default signature block |
| brand.accent_color, brand.primary_color | letterhead and heading colors |

Any string in the data file may also contain company tokens, filled from the
config: `{legal_name}`, `{dba}`, `{address_line1}`, `{city_state_zip}`,
`{phone}`, `{email}`, `{website}`, `{license}`, `{pm_name}`, `{pm_title}`,
`{pm_phone}`, `{pm_email}`. Unknown tokens are left as typed.

## Layout walkthrough
Page 1 (the letter, top to bottom):
1. Letterhead masthead (see Output spec header). Everything below sits inside the
   0.75 in side margins.
2. Date line, body style (e.g. "March 2, 2026"), then 4 pt gap.
3. Recipient block: one tight line per entry in letter.recipient_lines (entity
   name, office, city/state). 10 pt gap after.
4. RE line, bold: "RE: " followed by letter.re_line (project name and
   solicitation number, pipe-separated).
5. Salutation (e.g. "To Whom It May Concern:").
6. Opening paragraph(s): one body paragraph per entry in
   letter.opening_paragraphs. States what is being submitted, for which
   solicitation, and that the broker's written confirmation is enclosed.
7. Section heading "Bonding Capacity Summary".
8. Two-column table, 2.6 in + 4.4 in (full 7.0 in text width). Header row:
   primary-color bar, white bold "Item" / "Confirmed Capacity". One row per
   letter.capacity_rows entry: bold label on #eef2f7 fill, plain value at right.
   0.4 pt #cccccc grid, 6 pt side padding, 4 pt vertical padding, top-aligned.
   6 pt gap after.
9. Premium note (optional): small gray indented paragraph. State it the way your
   broker confirmed it in writing, in your own words.
10. Section heading "Confirmed by Surety Broker of Record" (only if
    letter.surety_lines present), then one tight line per entry: broker contact
    name and title, license number, legal entity, address, phone/email/web.
    8 pt gap after.
11. Closing paragraph(s) from letter.closing_paragraphs (offer to provide more
    documentation).
12. Signature block, kept together on one page as a unit: "Sincerely," then a
    24 pt blank gap for a wet signature, then bold signer name, then title,
    company, phone, email lines.
13. Enclosures block (if any): bold "Enclosures:" then numbered lines
    "1. <label>" per enclosure.
14. Footer (see Output spec).

Pages 2+: each enclosure PDF's pages, merged in listed order, unmodified.

## Placeholders
All example values are fictional. Capacity figures in the sample are round
placeholders; always use the figures your broker confirmed in writing.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| meta.job_slug | string | yes | "Sample_ES_HVAC" | Filename prefix; underscores, no spaces |
| meta.letter_date_iso | string | yes | "2026-03-02" | YYYY-MM-DD, used in output filename |
| meta.created | string | yes | "2026-03-02" | PDF metadata creation/mod date, keeps output deterministic |
| meta.pdf_title | string | yes | "Bonding Capacity Correspondence - Sample Elementary School HVAC Replacement (Project 2026-0001)" | PDF /Title metadata |
| meta.pdf_author | string | no | "Example Mechanical, LLC" | PDF /Author; defaults to the company config legal_name |
| meta.output_dir | string or null | no | null | null or absent = _sample_output next to the script; relative paths resolve against the script folder |
| letter.date_display | string | yes | "March 2, 2026" | Printed date line, also in the running footer |
| letter.recipient_lines | array of string | yes | ["Sample ISD", "Purchasing Department", "Anytown, Texas"] | One line each; pull from the solicitation contact block |
| letter.re_line | string | yes | "Bonding Capacity Information - Sample Elementary School HVAC Replacement \| Project 2026-0001" | Rendered after the fixed bold "RE: " |
| letter.salutation | string | yes | "To Whom It May Concern:" | Include the colon |
| letter.opening_paragraphs | array of string | yes | ["{legal_name} submits the following bonding capacity information in support of our proposal for ..."] | reportlab mini-HTML allowed (b, i) |
| letter.capacity_rows | array of object | yes | {"label": "Bonding Capacity", "value": "Aggregate Capacity of $10,000,000.00"} | One table row per object; keep the broker's exact figures |
| letter.capacity_rows[].label | string | yes | "Limit per project" | Left column, bold on light fill |
| letter.capacity_rows[].value | string | yes | "Single Limit of $5,000,000.00" | Right column |
| letter.premium_note | string | no | "Premium rate: [rate per $1,000 of contract value, as quoted by your surety]. ..." | Omit or empty to skip the note |
| letter.surety_lines | array of string | no | ["[Broker Contact Name], [Title]", "[Broker License No.]", "[Surety Broker Firm Name]", "[Broker Street Address, City, State ZIP]", "Phone: (555) 010-0102 \| broker@example.com"] | Omit to skip the whole surety section and its heading |
| letter.closing_paragraphs | array of string | no | ["Please contact me directly with any questions or if additional documentation from our surety is required."] | Body paragraphs before "Sincerely," |
| signature | object | no | see below | Omit the whole object to build it from the company config |
| signature.name | string | yes | "{pm_name}" | Bold line under the wet-signature gap |
| signature.title | string | no | "{pm_title}" | Line 2 |
| signature.company | string | no | "{legal_name}" | Line 3 |
| signature.phone | string | no | "Office: {pm_phone}" | Line 4 |
| signature.email | string | no | "{pm_email}" | Line 5 |
| enclosures | array of object | no | see below | Listed in the letter and merged behind it in order |
| enclosures[].label | string | yes | "Surety broker written confirmation of bonding capacity, March 2, 2026" | Printed in the numbered Enclosures list |
| enclosures[].path | string or null | no | "enclosures/broker_confirmation.pdf" | PDF to merge; a relative path resolves against the data file's folder; null/absent = listed but not merged; a missing file prints a warning and is skipped |

## Fixed wording
These strings are hard-coded in the script and never change between jobs:
- Running line document label: "Bonding Capacity Correspondence".
- RE prefix: "RE: ".
- Section heading: "Bonding Capacity Summary".
- Table column headers: "Item" and "Confirmed Capacity".
- Section heading: "Confirmed by Surety Broker of Record".
- Closing: "Sincerely,".
- Enclosures label: "Enclosures:".

Letterhead text (wordmark, license line, address block, footer) comes from the
company config, never from the script.

## How to build
    python build_capacity_letter.py [data.json] [--company company.json]

- data.json defaults to sample_data.json in this folder; `--company` defaults to
  `../../company.example.json`.
- Example with your own files:
  `python build_capacity_letter.py my_bid/capacity.json --company my_company.json`
- Output filename pattern:
  `<meta.job_slug>_Bonding_Capacity_Packet_<meta.letter_date_iso>.pdf`
  written to meta.output_dir (default `_sample_output/` in this folder).
  Sample: `Sample_ES_HVAC_Bonding_Capacity_Packet_2026-03-02.pdf` (1 page; the
  sample lists an enclosure but has no file to merge).
- The script refuses any data file containing an em dash or en dash (house style).
- Requires only stdlib + reportlab + PyMuPDF (fitz). Fully deterministic: running
  twice on the same JSON produces byte-identical PDFs.

## Known variations
- If you only have the broker's email, this template turns it into a letter +
  enclosure packet that drops straight into a qualification form. The letter
  body, recipient and RE line are fully JSON-driven; the letterhead and signature
  block layout are fixed.
- Capacity figures, premium rate and broker identity change whenever the surety
  program is renewed; always restate them from the broker's latest written
  confirmation and re-enclose that correspondence. Treat these figures as
  confidential; share them only where a solicitation requires them.
- letter.premium_note is optional; many qualification forms only want the three
  capacity numbers (bonding capacity, limit per project, unencumbered bonding
  capacity). Keep the rows in the order the form asks for them.
- letter.surety_lines is optional; omit it when the enclosure alone identifies
  the broker.
- Enclosures may be any number of PDFs (broker letter, surety's own letter, agent
  license). Entries with no path are listed in the letter but not merged.
- The signature phone can be the signer's direct line while the letterhead shows
  the company main number; both come from the company config.
- If a signed (wet-ink) letter is required, print page 1, sign in the 24 pt gap
  above the name line, scan, and re-merge with the enclosure pages.
