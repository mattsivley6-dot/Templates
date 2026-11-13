# Bid Agent

A small Python script that reads every file in a bid job folder (specs, drawings text, addenda, bid forms, RFI logs, vendor quotes) and asks a Claude model to produce 10 bid deliverables in one text file:

1. Scope of work (internal, foreman-level)
2. Vendor RFQ list grouped by rep or category
3. Submittal log
4. Preliminary milestone schedule
5. Equipment schedule / key numbers table
6. Pre-bid RFI log
7. Risk flag list
8. GC / mechanical coordination notes
9. Contract milestone checklist
10. Subcontractor RFQ summary

The output is saved in the job folder as `BID_AGENT_<project>_<timestamp>.txt`. Treat it as a first draft. Check every quantity and date against the documents before you price or send anything.

## Important: your documents go to a third-party API

The script extracts the text of the job files and sends it to the Anthropic API. Only run it on documents you are allowed to share with that service under your contracts, NDAs and company policy.

## Files

| File | What it does |
|---|---|
| `bid_agent.py` | The agent. Reads the folder, calls the API, saves the output. |
| `company_profile.example.json` | Fake company profile. Copy it to `company_profile.json` and fill in your own details. |
| `run_bid_agent.bat` | Windows launcher. Drag a job folder onto it. |
| `SETUP_FIRST_RUN.bat` | Installs the Python packages, creates `company_profile.json` from the example, and can save your API key. |

## Setup

1. Install Python 3.9 or later.
2. Install packages:
   ```
   pip install --upgrade anthropic PyPDF2 python-docx openpyxl
   ```
3. Copy `company_profile.example.json` to `company_profile.json` and edit it. Keep `company_profile.json` out of version control.
4. Set your API key as an environment variable. The script reads it from `ANTHROPIC_API_KEY` only; never put a key in the code or the profile.
   - Windows: `setx ANTHROPIC_API_KEY "<your key>"` then open a new window. Note that `setx` stores the key in plain text in your user environment.
   - macOS/Linux: `export ANTHROPIC_API_KEY="<your key>"`

On Windows, `SETUP_FIRST_RUN.bat` does steps 2 to 4 for you.

## Company profile

| Key | Example (fake) | Used for |
|---|---|---|
| `company_legal_name` | Example Mechanical, LLC | System prompt |
| `company_dba` | Example Mechanical | Prompt, console, output footer |
| `company_type` | commercial MEP subcontractor | Prompt |
| `location` | Anytown, TX | Prompt |
| `self_perform` | ["HVAC", "plumbing"] | Scope splits |
| `subcontracted` | ["electrical"] | Scope splits |
| `market_focus` | K-12 school district and commercial projects | Prompt |
| `bonding_capacity` | null | Optional. Left out of the prompt when null. |
| `pm_software` | [PM Software] | Optional. Left out when null or empty. |
| `pm_name`, `pm_title`, `pm_phone`, `pm_email` | Pat Doe, Project Manager, (555) 010-0101, pat.doe@example.com | RFQ contact line and output footer |

The profile is found in this order: `--profile`, the `BID_AGENT_PROFILE` environment variable, `company_profile.json` beside the script, then `company_profile.example.json`.

## Run

```
python bid_agent.py "C:\Jobs\Sample-Elementary"
python bid_agent.py "C:\Jobs\Sample-Elementary" --project "Sample Elementary School HVAC Replacement"
```

Or drag the job folder onto `run_bid_agent.bat`.

Options:

| Option | Default | Notes |
|---|---|---|
| `--project` | folder name | Name used in the output header and file name |
| `--profile` | see above | Company profile JSON |
| `--model` | `BID_AGENT_MODEL` env var, else `claude-opus-5-5` | Any current Claude model id. Check the Anthropic model list if a call fails with a model error. |
| `--max-tokens` | 64000 | Output cap. The request is streamed, so large values do not time out. |
| `--effort` | high | `low`, `medium`, `high`, `xhigh`, `max`, or `none` to leave it out. Needs a current `anthropic` package. |

## Limits

- Text only. Scanned or image-only PDFs come through as a note, not text. OCR them first.
- Old binary `.doc` and `.xls` files are not readable by python-docx or openpyxl. Save them as `.docx` / `.xlsx`.
- Each file is cut at 80,000 characters and the whole folder at 180,000 characters. Large spec books get cut off. Point the agent at a folder with the sections that matter.
- Earlier `BID_AGENT_*` outputs in the folder are skipped so they are not re-read.
- Each run is billed by the API provider. Check token use on large folders.
