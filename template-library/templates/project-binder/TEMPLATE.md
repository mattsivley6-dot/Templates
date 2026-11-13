# Project Binder (registers + core sections)

## Purpose and when to use

A printable project record binder for a mechanical job: letter portrait,
punch friendly left margin, one PDF per tab, merged into a single
bookmarked PDF. This template covers the six core and register tabs of a
full binder (a typical physical binder has about 20 tabs):

- Tab 00, Cover and Contents (cover page, table of contents, how to read)
- Tab 01, Project Summary (fact grid, status bullets, scope table, milestones)
- Tab 02, Directory (contact register plus formal notice addresses)
- Tab 09, RFI Log (register plus one detail page per RFI)
- Tab 10, Submittal Log (register plus notes)
- Tab 11, Change Orders (register, contingency ledger, one page per PCO)

Use it when a job needs a defensible paper record: owner meetings, disputes,
audits, closeout, or simply keeping one live register instead of three
drifting spreadsheets. Any section can be built alone; omit a section's key
from the JSON and that tab is skipped.

Voice rule for all content written into the JSON: terse, plain words, short
sentences, facts first, no filler. Where the record shows a problem, say it
plainly and say what is being done. Never invent a fact; where sources
conflict, keep both with a note saying so.

## Company config

Company data is never hard-coded. The script reads it from the
template-library company config:

- `--company <path>` selects the file. Default:
  `template-library/company.example.json` (two folders up from this
  script). Copy that file, fill in your own values, and pass it with
  `--company`.
- Fields used:
  - `dba`: masthead wordmark line 1, in caps (falls back to `legal_name`).
  - `legal_name`: masthead line 2 (small letterspaced caps, shown only when
    it differs from the DBA), footer left on every page, PDF author.
  - `brand.accent_color`: wordmark and the masthead rule.
  - `brand.primary_color`: h2 headings and register table header fill.
- `logo_path` and `signature_path` are not used; the masthead is a text
  wordmark built from the config.

## Output spec

- Format: PDF (reportlab platypus), one file per tab plus a merged binder
  PDF with one bookmark per tab (PyMuPDF merge).
- Page size: letter portrait, 8.5 x 11 in.
- Margins: left 1.15 in (binder punch side), right 0.70 in, bottom 0.85 in.
  Content top margin 1.35 in on tab pages, 1.00 in on the cover (no tab band).
- Font: Helvetica family (reportlab built in Base 14; Arial metric
  equivalent). Sizes:
  - h1 22/26 bold (RFI and PCO page titles)
  - h2 13/16 bold, primary color (section heads)
  - kicker 9/12 bold gray (small labels above h1)
  - big 12.5/17 (lead sentences), body 10.5/14.5
  - bullet 10.3/14.2 with round bullet, 14 pt left indent
  - cell 9.3/12, cellb bold, cellg gray (table cells)
  - hcell 8.6/11 bold white (register table headers)
  - label 8.4/11 bold gray over value 11.5/15 bold (fact grids)
  - note 8.6/11.6 gray
- Colors:
  - Accent: `brand.accent_color` (wordmark, 1.4 pt masthead rule). Default
    neutral gray `#666666` if the config has none.
  - Primary: `brand.primary_color` (h2 headings, register table header
    background). Default neutral dark gray `#333333` if the config has none.
  - GRAY #595959 (secondary text, footer), LGRAY #BFBFBF (rules)
  - INK #1A1A1A (body text), row stripe #F7F7F5 (alternating register rows)
  - hairline #E3E3E0 (register row separators)
  - reserved status colors RED #B23A2F, AMBER #B07A1E, tint #F2F5EF
- Header (every page): the company DBA in caps, Helvetica Bold 16 in the
  accent color at the left margin, with the legal name under it in
  Helvetica 5.6 gray at 2.6 pt letterspacing (letterspacing is reset after
  drawing; reportlab Tc leaks otherwise). Right side: project name line
  bold 9.2 INK over a gray 7.6 second line. Below: 1.4 pt accent rule
  across the text width at 0.77 in from the top edge. On tab pages a tab
  band follows: "TAB NN" bold 7.8 gray, the tab title in Helvetica Bold 15
  caps, subtitle right aligned gray 8.8.
- Footer (every page): 0.5 pt LGRAY rule at 0.68 in, then at 0.52 in:
  `[Company Legal Name]` left, "Prepared <date>" center,
  "Tab NN  ·  Page X of Y" right (Y is the page count of that tab's PDF;
  pages without a tab use the footer_binder_label instead of "Tab NN").
- Determinism: reportlab invariant=1, PyMuPDF save with no_new_id=True,
  no datetime.now()/random anywhere; identical JSON gives identical PDFs.
  Merged PDF metadata dates come from meta.pdf_date.

## Layout walkthrough

House text rule enforced in code on every string (the clean() pipeline): no
em dash, no en dash, no hyphens inside words or numbers in rendered output.
Em dashes become commas, en dashes become " to ", ISO dates (2026-03-02)
render as 03/02/2026, digit ranges "24-25" become "24 to 25", hyphenated
words are joined ("start-up" to "startup") or spaced ("tie-in" to "tie in"),
" - " becomes ", ". Formal identifiers listed in meta.allowed_dash_tokens
keep their dashes (project numbers, permit numbers). "PCO-004" style refs
normalize to "PCO 004" with zeros preserved. Ampersands are XML escaped.
A post build sweep reads the rendered PDFs and fails the build if any dash
survives.

**Tab 00, Cover and Contents (3 pages).**
Page 1: 1.1 in spacer, kicker "PROJECT RECORD BINDER" (gray bold 9), 6 pt
gap, then the project title lines in h1 22 bold (usually two lines, for
example "Sample Elementary School" / "HVAC Replacement Project"), 14 pt
gap, then a 2 column fact grid (8 facts: Owner, Project No., Engineer,
Site, Contractor, Contract Sum, Project Manager, Substantial Completion;
labels in 8.4 bold gray caps over values in 11.5 bold), 22 pt gap, a light
rule, then the record period sentence in big 12.5 and the sources sentence
in body. Footer label reads the binder label (e.g. "Sample Elementary
Binder"), not a tab.
Page 2: h2 "What is in this binder", then a full width register table
(Tab | Section | What it holds; columns 0.75 / 2.0 / rest in) listing every
tab of the physical binder ("Tab 01" ... "Tab 20"), colored header, striped
rows. Page 3: h2 "How to read this binder", big lead line, then the bullets.

**Tab 01, Project Summary (3 to 5 pages).**
Page 1: h2 "The job in one page", the scope headline in big, a 2 column
fact grid (6 contract facts), a rule, h2 status heading ("Where the job
stands, <date>"), then the status bullets. Page 2: h2 "Scope of work",
register table (Trade | What we are delivering; 1.35 in / rest).
Page 3+ (only if milestones present): h2 "Milestones to date", register
table (Date | Event; 1.1 in / rest); the header row repeats when the table
breaks across pages. Every tab page carries the tab band under the masthead.

**Tab 02, Directory (1 to 2 pages).**
h2 "Who is who", register table (Organization | Name | Role | Phone |
Email; columns 1.25 / 1.15 / 1.7 / 0.95 / rest). Phone hyphens render as
periods ((555) 010.0101). Then 10 pt gap, h2 with the notice heading
(for example "Formal notice addresses (per the contract notice clause,
certified mail)"), and a 2 column table (Party | Address; 2.6 in / rest).

**Tab 09, RFI Log (1 register page + 1 page per RFI).**
Page 1: h2 "RFI register", register table (RFI | Subject | Sent | Answered |
Status | PCO; columns 0.5 / rest / 0.75 / 0.85 / 0.8 / 1.0). Table dates in
mm/dd/yy. Optional gray note under the register (for example to explain a
skipped RFI number). Then one page per RFI: kicker "RFI NNN", the title
in h1 (shortened to 160 chars), 2 column fact grid (Sent [or "Not sent"] /
To / Answered [or "Open"] / Status, prose dates "March 3, 2026"), a rule,
then optional h2 blocks: "The answer" (body), "Cost path" ("This RFI became
PCO NNN. See Tab 11."), "Record note" (body).

**Tab 10, Submittal Log (1 to 2 pages).**
h2 "Submittal register", register table (Item | Spec | Sent | Returned |
Action; item column gets all width left of 3.6 in of fixed columns). The
Action cell falls back to the submittal's status when no reviewer action
exists. Then h2 "Notes" with up to 12 bullets of "item: note" (item
shortened to 46, note to 110).

**Tab 11, Change Orders (1 register page + 1 page per PCO).**
Page 1: h2 "Change order register", register table (No. | Scope | Amount |
Type | Status; 0.65 / rest / 0.95 / 1.25 / 1.5). Gray note with the labor
rate basis. Then h2 "Contingency ledger", table (Item | Amount | Running
balance; running balance computed by the script, credits in parentheses,
exact cents), and a gray note "Remaining with every PCO at full value:
<amount>. <note>". Then one page per PCO: kicker "PCO NNN", title in h1,
fact grid (Amount / Type / Where it came from / Funding), rule, h2 "Status"
with body text, then optional blocks: "How it moved" (bullets from
key_dates), "Price history" (body), "Note" (gray note style).

**Merged binder.** The tab PDFs are concatenated in tab order into
"<output_prefix> Project Binder.pdf" with one level 1 bookmark per tab
("00 - Cover and Contents", "01 - Project Summary", ...), and title /
author / subject / creationDate / modDate metadata set from the JSON and
the company config.

## Placeholders

All example values are invented (see `sample_data.json`).

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| meta.binder_title | string | yes | Sample Elementary Project Record Binder | PDF metadata title and cover doc title |
| meta.output_prefix | string | yes | Sample Elementary | merged file becomes "<prefix> Project Binder.pdf" |
| meta.prepared_line | string | yes | Prepared March 31, 2026 | footer center, every page |
| meta.header_project_line1 | string | yes | SAMPLE ELEMENTARY SCHOOL | masthead right line 1, give it in caps |
| meta.header_project_line2 | string | yes | Sample ISD, Project 2026-0001 | masthead right line 2, gray |
| meta.footer_binder_label | string | no | Sample Elementary Binder | footer right label on pages without a tab (cover) |
| meta.pdf_subject | string | no | Sample Elementary School HVAC Replacement, Sample ISD, Project 2026-0001 | PDF metadata subject on every file |
| meta.pdf_date | string | no | D:20260331120000-06'00' | creation and mod date of the merged PDF |
| meta.allowed_dash_tokens | array of regex strings | no | ["2026-0001", "J-0001"] | identifiers whose dashes survive clean(); no capture groups |
| meta.ref_fixes | array of [regex, replacement] | no | [["\\bEF-(\\d+)\\b", "EF \\1"]] | job specific token fixes applied before the generic dash pass |
| meta.word_joins | object (string to string) | no | {"pre-heat": "preheat"} | extra hyphenated words to join instead of spacing out |
| cover | object | no | see sample | omit to skip Tab 00 |
| cover.tab_no | string | yes | 00 | used in the output filename and bookmark |
| cover.section_name | string | yes | Cover and Contents | filename and bookmark label |
| cover.kicker | string | yes | PROJECT RECORD BINDER | small gray label above the title |
| cover.title_lines | array of strings | yes | ["Sample Elementary School", "HVAC Replacement Project"] | h1 lines, usually two |
| cover.facts | array of [label, value] | yes | [["Owner", "Sample ISD"], ...] | 2 column fact grid, 8 entries in the sample |
| cover.record_period | string | yes | Record period: January 5, 2026 through March 31, 2026. | big line under the rule |
| cover.record_intro | string | yes | Built from the project mailbox, ... | body line under record_period |
| cover.toc | array of [tab, section, description] | yes | [["01", "Project Summary", "The job on one page. Scope. Milestones."], ...] | list every tab of the PHYSICAL binder, not just the generated ones |
| cover.how_to_read_lead | string | yes | Each tab stands alone. Each page stands alone. | big lead on the how to read page |
| cover.how_to_read | array of strings | yes | ["Pages are short on purpose. Facts first. No filler.", ...] | bullets |
| summary | object | no | see sample | omit to skip Tab 01 |
| summary.tab_no | string | yes | 01 | tab band, filename, bookmark |
| summary.tab_title | string | yes | Project Summary | tab band title (renders in caps) |
| summary.subtitle | string | yes | The job on one page | right side of the tab band |
| summary.headline | string | yes | Replace 2 rooftop HVAC units and curbs. ... | scope in one big sentence group |
| summary.facts | array of [label, value] | yes | [["Contract Sum", "$100,000.00"], ...] | 6 contract facts in the sample |
| summary.status_heading | string | yes | Where the job stands, March 31, 2026 | carries the as of date |
| summary.status_bullets | array of strings | yes | ["Both new curbs are set and dried in.", ...] | plain statements of where things stand |
| summary.scope_rows | array of [trade, description] | yes | [["HVAC units", "Remove 2 rooftop units. ..."], ...] | scope of work table |
| summary.milestones | array of {date, event, note} | no | [{"date": "2026-01-05", "event": "Notice to proceed issued."}] | ISO dates; `note` is optional and not rendered; omit or empty to drop the milestones page |
| directory | object | no | see sample | omit to skip Tab 02 |
| directory.tab_no / tab_title / subtitle | strings | yes | 02 / Directory / Every party on the job | tab band |
| directory.contacts | array of {org, name, title, phone, email} | yes | {"org": "Sample ISD", "name": "Sam Roe", ...} | phone hyphens auto convert to periods |
| directory.notice_heading | string | yes | Formal notice addresses (per the contract notice clause, certified mail) | cite your contract's notice clause numbers |
| directory.notice_addresses | array of [party, address] | yes | [["Owner: Sample ISD", "Attn: Sam Roe, 200 Example Avenue, Anytown, TX 75001"]] | certified mail addresses |
| rfi_log | object | no | see sample | omit to skip Tab 09 |
| rfi_log.tab_no / tab_title / subtitle | strings | yes | 09 / RFI Log / Register plus one page per RFI | tab band |
| rfi_log.register_note | string | no | RFI numbers run in the order sent. ... | gray note under the register |
| rfi_log.rfis | array | yes | see below | one register row and one detail page each |
| rfi_log.rfis[].number | string | yes | 001 | zero padded |
| rfi_log.rfis[].title | string | yes | RTU-2 curb out of level at the existing roof opening | |
| rfi_log.rfis[].date_sent | string ISO date | no | 2026-03-03 | empty renders "Not sent" on the detail page |
| rfi_log.rfis[].sent_to | string | no | Alex Poe, Sample Engineering, Inc. | |
| rfi_log.rfis[].date_answered | string ISO date | no | 2026-03-10 | empty renders "Open" on the detail page |
| rfi_log.rfis[].answer | string | no | Level the curb with treated wood blocking ... | "The answer" block |
| rfi_log.rfis[].status | string | yes | Closed | |
| rfi_log.rfis[].linked_pco | string | no | PCO-001 | renders the "Cost path" block, normalized to "PCO 001" |
| rfi_log.rfis[].note | string | no | Photos of the out of level curb are in ... | "Record note" block; keep source conflicts here |
| submittal_log | object | no | see sample | omit to skip Tab 10 |
| submittal_log.tab_no / tab_title / subtitle | strings | yes | 10 / Submittal Log / What was submitted and the action | tab band |
| submittal_log.submittals | array | yes | see below | |
| submittal_log.submittals[].item | string | yes | Rooftop units RTU-1 and RTU-2: product data | |
| submittal_log.submittals[].spec | string | no | 23 74 13 | "N/A" renders blank |
| submittal_log.submittals[].date_submitted | string ISO date | no | 2026-01-20 | |
| submittal_log.submittals[].date_returned | string ISO date | no | 2026-02-03 | |
| submittal_log.submittals[].action | string | no | Approved as noted | falls back to status when empty |
| submittal_log.submittals[].status | string | no | Superseded by resubmittal | |
| submittal_log.submittals[].note | string | no | Engineer asked for the economizer option ... | first 12 noted items bullet under "Notes" |
| change_orders | object | no | see sample | omit to skip Tab 11 |
| change_orders.tab_no / tab_title / subtitle | strings | yes | 11 / Change Orders / Register, ledger, one page per PCO | tab band; tab_no also feeds the RFI "See Tab NN" cross reference |
| change_orders.labor_rate_basis | string | no | All PCOs are priced at the contract labor rates with the contract markup. ... | gray note under the register; describe the basis, do not publish your rates |
| change_orders.funding_default | string | no | Owner contingency | Funding fact on every PCO page unless overridden |
| change_orders.pcos | array | yes | see below | |
| change_orders.pcos[].number | string | yes | 001 | zero padded |
| change_orders.pcos[].title | string | yes | Level RTU-2 curb with wood blocking (RFI 001) | |
| change_orders.pcos[].origin | string | yes | RFI-001 / existing roof opening out of level | "Where it came from" fact |
| change_orders.pcos[].amount | string | yes | $1,000.00 | string, exact cents; credits like ($500.00) |
| change_orders.pcos[].amount_type | string | yes | Firm | Firm / NTE / Credit plus detail |
| change_orders.pcos[].status | string | yes | Approved by the owner 03/24/2026. | register cell and detail Status block |
| change_orders.pcos[].history | string | no | V1 03/05 $3,000.00; V2 03/12 $2,500.00 ... | "Price history" block |
| change_orders.pcos[].key_dates | array of strings | no | ["2026-03-10 RFI 001 answered with the blocking detail.", ...] | "How it moved" bullets |
| change_orders.pcos[].note | string | no | Roofer tie in is included. | gray "Note" block |
| change_orders.pcos[].funding | string | no | Credit back to owner contingency | overrides funding_default for one PCO |
| change_orders.contingency | array of {item, amount} | no | {"item": "Owner contingency (contract allowance)", "amount": 10000.00} | amount is a NUMBER; negatives are draws; running balance is computed; omit to skip the ledger |
| change_orders.contingency_remaining | string | no | +$7,000.00 | quoted in the ledger note |
| change_orders.contingency_note | string | no | Balance per the owner's contingency log as of 03/31/2026. | shortened to 220 chars in the ledger note |

## Fixed wording

Baked into the script, identical on every job:

- Masthead: the company DBA and legal name from the company config.
- Footer: the company legal name from the company config, and
  "Tab NN  ·  Page X of Y".
- Cover page 2 heading: "What is in this binder"; TOC headers
  "Tab | Section | What it holds"; row prefix "Tab NN".
- Cover page 3 heading: "How to read this binder".
- Summary headings: "The job in one page", "Scope of work",
  "Milestones to date"; table headers "Trade | What we are delivering"
  and "Date | Event".
- Directory heading: "Who is who"; table headers
  "Organization | Name | Role | Phone | Email" and "Party | Address".
- RFI headings: "RFI register"; table headers
  "RFI | Subject | Sent | Answered | Status | PCO"; kicker "RFI NNN";
  fact labels "Sent / To / Answered / Status"; empty date fallbacks
  "Not sent" and "Open"; block heads "The answer", "Cost path",
  "Record note"; sentence "This RFI became PCO NNN. See Tab NN."
- Submittal headings: "Submittal register"; table headers
  "Item | Spec | Sent | Returned | Action"; "Notes".
- Change order headings: "Change order register"; table headers
  "No. | Scope | Amount | Type | Status"; "Contingency ledger";
  "Item | Amount | Running balance"; note lead "Remaining with every PCO
  at full value: "; kicker "PCO NNN"; fact labels "Amount / Type /
  Where it came from / Funding"; block heads "Status", "How it moved",
  "Price history", "Note".

## How to build

```
python build_project_binder.py [data.json] [out_dir] [--company path/to/company.json]
```

All arguments optional: data.json defaults to sample_data.json next to the
script, out_dir defaults to _sample_output next to the script, --company
defaults to `../../company.example.json`. For a real job:
`python build_project_binder.py "<job folder>/binder_data.json" "<job folder>/Project Binder" --company "<path>/my_company.json"`.

Expected output files in out_dir:

- "<tab_no> <tab_title>.pdf" per section present in the JSON (sample:
  "00 Cover and Contents.pdf", "01 Project Summary.pdf", "02 Directory.pdf",
  "09 RFI Log.pdf", "10 Submittal Log.pdf", "11 Change Orders.pdf")
- "<meta.output_prefix> Project Binder.pdf" (merged, bookmarked; sample:
  "Sample Elementary Project Binder.pdf", 16 pages)

The script exits nonzero if any dash character survives in the rendered
text (the house rule quality gate). Requires reportlab and PyMuPDF; output
is native PDF, no Word needed. Output is deterministic: same JSON, same
bytes.

## Known variations

- A full binder usually has about 20 tabs. This template generates the six
  core and register tabs. Other tabs (Contract, Schedule, Weather, Daily
  Reports, Manpower, Pay Apps and Cost, Risk Register, Safety, Quality,
  Meetings and Notices, Procurement, Photo Log, Closeout, Lessons Learned)
  are job authored and are not JSON driven here. The cover TOC should still
  list every tab of the physical binder.
- The binder has its own look (text wordmark, accent rule, colored register
  headers). Brand colors come from the company config, so the binder
  matches your other documents once the config is set.
- Every optional block earns its keep: milestones page, register_note,
  labor_rate_basis, contingency ledger, and the per RFI/PCO detail blocks
  (answer, cost path, record note, key dates, history, note) all disappear
  cleanly when their keys are empty or absent. Whole sections skip when
  their top level key is omitted.
- The clean() pipeline is aggressive by design: it will rewrite ISO dates
  inside prose, split hyphenated words, and turn "23 81 19-01" into
  "23 81 19 to 01". Protect any identifier that must keep its dash by
  adding a regex to meta.allowed_dash_tokens (no capture groups), and add
  job specific token repairs (for example an equipment tag like "EF-1") to
  meta.ref_fixes.
- Email addresses or URLs containing hyphens would get mangled by clean().
  Add them to meta.allowed_dash_tokens if a job has them.
- Between jobs, expect these to change: tab numbering if the binder gets
  more or fewer tabs, the notice_heading contract citations, the
  funding_default (only contingency funded jobs say "Owner contingency"),
  and the how_to_read bullets which reference specific tab numbers.
- If a fact in the binder was ever wrong once, add your own check for it
  (a "fact lock") next to the dash sweep so it cannot come back.
