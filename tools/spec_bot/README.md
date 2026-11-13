# Spec Bot

Reads a project manual (spec book) PDF and sorts every paragraph into three
piles: **project specific** (read this), **ambiguous** (scan this) and
**boilerplate** (skip). It can also match a priced estimate against the spec
to find scope the estimate may have missed.

It learns from your past bids:

- Paragraphs with capacities (CFM, MBH, GPM, tons, HP, volts) or equipment
  tags (RTU-1, AHU-2, CH-1) are always project specific.
- Paragraphs that repeat nearly word for word across other bids are
  boilerplate.
- Bids where you match a finished estimate to the spec give "gold" labels
  that override the rest.

## Requirements

- Python 3.10 or newer
- `pip install pymupdf openpyxl python-docx`
- For estimate matching only: `pip install sentence-transformers numpy`
  (the first run downloads a small embedding model)

PyMuPDF is offered under the AGPL or a commercial license. Check that this
fits how you use it.

## Folders

All working files go in `data/` next to this README, and Excel checklists go
in `outputs/`. Both are created on first run. Set the `SPEC_BOT_DATA` and
`SPEC_BOT_OUTPUTS` environment variables (or pass `--data-dir` / `--out-dir`
to `run_bot.py`) to keep them somewhere else. Do not commit `data/` or
`outputs/`: they hold your bids.

`config/title_ignore_words.txt` lists words (owner, engineer, project name)
that appear in your spec books' page headers and footers, so they are not
mistaken for section titles.

## Quick run: one spec book to an Excel checklist

Windows: drag the PDF onto `Spec Bot.bat`, type a bid name (for example
`Sample Elementary`) and wait. The checklist opens in Excel.

Any system:

```
python run_bot.py "path/to/project manual.pdf" "Sample Elementary"
python run_bot.py "path/to/project manual.pdf" "Sample Elementary" --divisions 01,22,23,26
```

This runs `extract_spec.py`, `build_library.py` and `to_excel.py`. The
workbook has a Summary tab, a Project-Specific tab, an Ambiguous tab, and
hidden Boilerplate and All tabs.

## Build a library from past bids

Point the inventory at the folders that hold your job folders. It expects
each job folder to have subfolders such as `01-Bid Docs`, `02-Addendums`,
`05-Proposals` and `10-Scopes`; edit the name lists at the top of
`inventory.py` and `extract_proposals.py` to match your layout.

```
python scripts/inventory.py --jobs-dir "path/to/JOBS"
python scripts/batch_extract_specs.py
python scripts/build_library.py
```

Optional: `python scripts/extract_proposals.py --all` pulls CSI citations,
equipment tags, quantities and capacities out of sub and vendor proposals,
and `python scripts/inspect_proposals.py <bid_slug>` prints a quality check.

## Find missed scope: match an estimate to the spec

Inputs: the spec book PDF and the priced estimate workbook (.xlsx) for the
same bid. Use the same bid name in every step.

```
python scripts/extract_spec.py "path/to/project manual.pdf" --bid "Sample Elementary"
python scripts/inventory_estimates.py          # optional: lists candidate estimate workbooks per bid
python scripts/extract_estimate.py --bid "Sample Elementary" --workbook "path/to/estimate.xlsx"
python scripts/match_lineitems_to_spec.py --bid "Sample Elementary"
python scripts/format_matches_xlsx.py --csv data/estimates/sample_elementary__matches.csv
```

Open the review workbook, put `Y` in **Accept** for each correct match and
save. Then:

```
python scripts/apply_estimate_labels.py --bid "Sample Elementary" --reviewed-csv data/estimates/sample_elementary__matches.xlsx
python scripts/find_missed_scope.py --bid "Sample Elementary"
python scripts/build_library.py
```

`find_missed_scope.py` writes `data/missed_scope/<bid>__possible_misses.csv`:
spec paragraphs with no matching line item that still carry scope signals
(capacities, equipment tags, quantities, "as scheduled"). Review the `high`
rows first.

If you already know which spec sections each line item covers, skip the
review and write a decisions file instead (see
`examples/decisions.example.json`):

```
python scripts/apply_proposed_labels.py --bid "Sample Elementary" --decisions examples/decisions.example.json
```

## Scripts

| Script | What it does |
|---|---|
| `run_bot.py` | One spec PDF to an Excel checklist (extract, rebuild library, export) |
| `Spec Bot.bat` | Windows drag-and-drop launcher for `run_bot.py` |
| `scripts/inventory.py` | Classifies job folders by whether they have a spec book and proposals |
| `scripts/batch_extract_specs.py` | Extracts every spec book found by the inventory |
| `scripts/extract_spec.py` | Splits one spec PDF into paragraph records by CSI section |
| `scripts/build_library.py` | Scores and labels every paragraph into `data/library.sqlite` |
| `scripts/to_excel.py` | Writes the takeoff checklist workbook for one bid |
| `scripts/extract_proposals.py` | Pulls scope signals out of sub and vendor proposals |
| `scripts/inspect_proposals.py` | Prints a quality check of extracted proposals |
| `scripts/inventory_estimates.py` | Lists candidate estimate workbooks per bid |
| `scripts/extract_estimate.py` | Reads line items from an estimate workbook |
| `scripts/match_lineitems_to_spec.py` | Finds the closest spec paragraphs for each line item |
| `scripts/format_matches_xlsx.py` | Turns the matches CSV into a review workbook with Y/N dropdowns |
| `scripts/apply_estimate_labels.py` | Turns reviewed matches into gold labels |
| `scripts/apply_proposed_labels.py` | Turns a hand-written decisions file into gold labels |
| `scripts/find_missed_scope.py` | Lists spec paragraphs that look like scope but have no line item |

The bot is a reading aid. It does not replace reading the spec.
