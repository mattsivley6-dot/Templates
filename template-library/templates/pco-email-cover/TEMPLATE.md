# PCO Email Cover Note

## Purpose and when to use

A short plain-text email body that transmits a Proposed Change Order (PCO) PDF for
signature. Written once per PCO, saved as "Email cover - PCO-0XX.txt" in the job's
change order folder, then pasted into the mail client when the PCO package is sent.
A second variant covers backup-request emails to a subcontractor when the owner
questions a line item on a PCO.

Use the `pco_cover` variant every time a PCO PDF goes out for signature (new,
revised, or resubmitted). Use the `sub_backup_request` variant when a sub must
supply documentation (receipts, hour breakdowns on letterhead) before the owner
will approve a PCO line.

ROUTING, WHO GETS WHICH EMAIL (a common pattern; follow your own project's
change order procedure, usually set at the pre-construction meeting):

1. If a new labor rate is being introduced, send the rate support first as its own
   short email, so the rate is on the record before any PCO that uses it.
2. Send each PCO cover to the engineer and the owner at the same time:
   - TO: [Engineer contact] and the engineer's submittal inbox, if they use one.
   - CC: [Owner contact(s)].
   - One email per PCO, one PCO PDF attached per email, plus any shared backup
     exhibit.
3. Signature order: follow the contract. A typical order is contractor, then
   engineer, then owner, before the work is billed. The engineer may email an
   authorization to proceed on urgent items before full signatures land.
4. After signatures, get the formal change authorization the contract requires;
   only then does the PCO go on a pay application.
5. Subcontractor backup requests (`sub_backup_request` variant) go directly to the
   sub's contact only. Do NOT copy the engineer or the owner; the point is to
   collect clean paper before resubmitting to them.

Subject line pattern: "{project short name} PCO {number} {action} ({plain-language tag})".
Examples (fictional):
- New firm PCO: "Sample ES PCO-002 for signature (RTU-2 disconnect)"
- NTE or anything needing review before signature: "Sample ES PCO-001 for review
  and signature (RTU-1 curb adapter)"
- Resubmittal of a superseded PCO: "Sample ES PCO-003 revised (deduct credit)"

## Output spec

- Format: plain text. `pco_cover` writes a `.txt`; `sub_backup_request` writes a
  `.md` (light Markdown: `#` title, `**bold**` headings, `- ` bullets).
- Encoding: UTF-8, no BOM. Line endings: LF. File ends with a single newline.
- No page geometry: this is an email body, not a paginated document. No page size,
  margins, fonts, or colors; the mail client supplies the rendering. Send as
  plain text.
- Body wrap width: 83 characters for `pco_cover`; 0 (no wrapping, one line per
  paragraph) for `sub_backup_request`.
- Header: a routing block at the top of the file, labels in caps with TWO spaces
  after the colon: `TO:  `, `CC:  `, `SUBJECT:  `, `ATTACH:  `. Multiple
  addresses or attachments are joined with `; `. The `sub_backup_request` variant
  instead uses `To: ` and `Subject: ` (one space) under a `# DRAFT EMAIL - ...`
  title line.
- Footer: none. The email ends with the closing line and the signature block.
- House rule: no em dashes or en dashes anywhere. The build script raises an error
  if one appears in the rendered text.

## Company config

The script reads company fields from `template-library/company.example.json` (two
folders up from this one) unless you pass `--company path/to/your_company.json`.
Copy the example, fill in your own values and point `--company` at it.

- Any string in the data file may contain company tokens, filled from the config:
  `{legal_name}`, `{dba}`, `{address_line1}`, `{city_state_zip}`, `{phone}`,
  `{email}`, `{website}`, `{license}`, `{pm_name}`, `{pm_title}`, `{pm_phone}`,
  `{pm_email}`. Unknown tokens are left as typed.
- If `signature` is left out of the data file, the script builds it from the
  config: `pm_name` / `pm_title` / `legal_name` for `pco_cover`, and `pm_name` /
  `dba` for `sub_backup_request`.

## Layout walkthrough

`pco_cover` variant (top to bottom, single "page"):

1. Routing block, four lines, no blank lines between them:
   - `TO:  <recipient 1>; <recipient 2>` (display name with email in parentheses,
     or a bare address)
   - `CC:  <recipient 1>; <recipient 2>` (line omitted entirely if no CC)
   - `SUBJECT:  <subject line>`
   - `ATTACH:  <exact PDF filename being attached>` (line omitted if none)
2. Blank line.
3. Greeting: first name of the primary recipient followed by a comma, e.g.
   `Alex,`
4. Blank line, then the body: 3 to 5 short paragraphs separated by blank lines,
   each wrapped at 83 characters. Typical order:
   - Paragraph 1, one sentence: what is attached ("Attached is PCO-001 for the
     curb adapter at RTU-1.").
   - Paragraph 2: the money sentence first ("It is $X,XXX.XX, firm." or "It is
     not to exceed $X,XXX.XX."), then one or two sentences of context (what
     changed since the last version, why the work is needed).
   - Optional numbered list block: an intro line ending in a colon ("Three parts,
     each broken out:") followed immediately (no blank line) by `1. ` `2. ` `3. `
     items, continuation lines indented 3 spaces to hang under the text.
   - Closing paragraph: what is attached as backup and the ask ("Please sign and
     forward to the owner.").
5. Blank line, then closing `Thank you,` and directly beneath it (no blank line)
   the signature lines: `[PM Name]` / `[PM Title]` / `[Company Legal Name]`.

`sub_backup_request` variant:

1. Title line: `# DRAFT EMAIL - <short internal description>`
2. `To: <name, company (email)>` and `Subject: <subject>` on the next two lines.
3. Blank line, greeting (`Jordan,`), blank line.
4. Body paragraphs, unwrapped (one long line each), separated by blank lines.
   Numbered asks are rendered as a `**bold**` heading line with its explanation
   paragraph on the very next line (same block, no blank line between). Bullet
   lists are their own block, `- ` prefix, one line per bullet.
5. Closing `Thanks,` then a two-line signature: `[PM Name]` / `[Company DBA]`.

## Placeholders

All example values are fictional.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| variant | string | no | "pco_cover" | "pco_cover" (default) or "sub_backup_request"; selects template file and default wrap |
| output_filename | string | yes | "Email cover - PCO-001.txt" | exact output name; convention "Email cover - PCO-0XX.txt" |
| wrap_width | integer | no | 83 | body wrap column; 0 disables wrapping; defaults 83 for pco_cover, 0 for sub_backup_request |
| to | array of strings | yes | ["Alex Poe (alex.poe@example.com)"] | joined with "; " on the TO line |
| cc | array of strings | no | ["Sam Roe (sam.roe@example.com)"] | joined with "; "; CC line dropped if empty or absent |
| subject | string | yes | "Sample ES PCO-001 for review and signature (RTU-1 curb adapter)" | see subject pattern above |
| attach | array of strings | no | ["Sample_ES_PCO-001_RTU-1_Curb_Adapter.pdf"] | exact filenames of the attachments; line dropped if empty |
| greeting | string | yes | "Alex" | first name only; script adds the comma |
| body | array | yes | see sample_data.json | items are strings (paragraphs) or objects, shapes below |
| body[] item: string | string | - | "Attached is PCO-001 for the curb adapter at RTU-1." | one unwrapped paragraph; script wraps it |
| body[] item: intro + numbered | object | - | {"intro": "Three parts, each broken out:", "numbered": ["Curb adapter...", "Roofing sub...", "Our crew..."]} | intro optional; renders 1. 2. 3. with 3-space hanging indent |
| body[] item: intro + bullets | object | - | {"bullets": ["Site visit and layout at RTU-1"]} | renders "- " items, 2-space hanging indent |
| body[] item: heading + text | object | - | {"heading": "**1. Receipt for the permit fee.**", "text": "The owner wants proof..."} | heading line then paragraph in the same block (sub variant) |
| closing | string | yes | "Thank you," | "Thanks," in the sub variant |
| signature | array of strings | no | ["{pm_name}", "{pm_title}", "{legal_name}"] | one line each, directly under the closing; defaults from the company config |
| draft_title | string | sub variant only | "Sample Electric backup needed for PCO-001" | text after "# DRAFT EMAIL - "; ignored by pco_cover |

## Fixed wording

Never changes between jobs (pco_cover variant):

- Header labels, exactly: `TO:  ` / `CC:  ` / `SUBJECT:  ` / `ATTACH:  ` (two
  spaces after each colon).
- Closing line: `Thank you,`
- Signature block: PM name, PM title and company legal name, from the company
  config.

Useful stock sentences (keep the voice short and plain; swap only the numbers and
unit names):

- "Attached is PCO-0XX, updated." / "Attached is PCO-0XX for the <unit/location>."
- "It is $X,XXX.XX, firm." / "It is not to exceed $X,XXX.XX."
- "Backup for each part is attached."
- "Please sign and forward to the owner." / "Please sign and forward to the owner
  for the change authorization."
- "Nothing starts until all parties sign, or your email to proceed." (NTE /
  proceed-authorization situations)

Sub variant fixed wording: closing `Thanks,` and a two-line signature (PM name and
company DBA).

## How to build

    python build_pco_email_cover.py [data.json] [out_dir] [--company company.json]

- `data.json` defaults to `sample_data.json` in this folder;
  `sample_data_sub_variant.json` demonstrates the sub_backup_request variant.
- `out_dir` defaults to `_sample_output` in this folder. For a real job, point it
  at the job's change order send folder.
- `--company` defaults to `../../company.example.json`.
- Output filename: exactly the JSON `output_filename`, conventionally
  `Email cover - PCO-0XX.txt`.
- The script is deterministic (no clock, no randomness), stdlib only, and errors
  out if an em dash or en dash appears anywhere in the rendered email.

## Known variations

- Subject action varies by situation: "for signature" (firm, straightforward),
  "for review and signature" (NTE amounts or anything the engineer should read
  before signing), "revised" (superseding an already-signed PCO; say what changed
  in the body and note new signatures are needed).
- Body length varies from 3 short paragraphs (a simple firm PCO) to 4 with a
  numbered list (a multi-part NTE) or 4 denser paragraphs (a credit that needs
  explaining). Credits state the credit amount in parentheses: ($X,XXX.XX).
- The numbered-list block only appears when a PCO has distinct parts with
  different pricing bases (firm vs NTE vs estimate); otherwise list the trades
  inline in one sentence.
- Recipients are job-specific. Pull the engineer and owner contacts from the
  job's own change order procedure and keep the TO-engineer / CC-owner split
  unless the contract says otherwise.
- The sub_backup_request variant is an internal DRAFT saved as .md with a
  "# DRAFT EMAIL" title; it uses Markdown bold headings and bullets and a shorter
  signature. Strip the title line when actually pasting into the mail client.
