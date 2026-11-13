# Templates

Field-tested templates, checklists, SOPs, tools and Claude Code skills for HVAC and mechanical construction project management. Everything here is generic. Fill in the `[bracketed]` placeholders, or point a generator at your own company file.

## What's here

| Folder | What it is |
|---|---|
| `templates/` and `scripts/` | Submittal set: transmittal, submittal cover sheet and submittal index (.docx), built by `scripts/build_submittal_templates.py`. |
| `template-library/` | 17 document generators in Python: action items tracker, capacity letter, daily log, daily report, duct shop ticket, notice of concealed condition, OEC (owner, engineer, contractor) meeting minutes, pay application, PCO package, PCO email cover, photo log, project binder, RFI, site walk minutes, transmittal, warranty closeout letter and warranty matrix. Each folder has a spec (`TEMPLATE.md`), the generator, fake sample data and a sample output. |
| `pm-packet/` | A project manager's operating packet: rules, job lifecycle, selling, running, billing and closing a job, a daily and weekly routine, the job folder layout and a job state card. `pm-packet/forms/` holds blank forms: acceptance, owner training record, prefunctional checklist, punch list, startup checklist, communications plan, RACI and lessons register. |
| `checklists/` | Project checklist start to finish, customer meeting checklist, Texas public-entity bid DQ prevention checklist, RTU install workflow, project life cycle, job folder structure guide and a new vendor setup note. `checklists/planning/` has an RFI log, a daily report and a pre-task plan. |
| `claude/skills/` and `claude/agents/` | Claude Code skills and agent definitions for PM work: bids, estimating, buying, billing, cost analysis, claims, closeout, crew scheduling, document control, a pre-send QA gate, field tech answers, site surveys, email drafting, and AutoCAD and Fusion automation. Copy them into `~/.claude/skills/` and `~/.claude/agents/`. |
| `tools/` | `spec_bot` sorts a project manual into must-read, scan and boilerplate, and checks an estimate against it for missed scope. `bid_agent` reads a bid folder and drafts scope, RFQ, submittal, schedule and risk lists with the Claude API. |
| `prompts/` | An MEP estimator system prompt. |
| `autocad-kb/` | AutoCAD MEP 2027 knowledge base (sections 00 to 15) adapted from Autodesk help under CC BY-NC-SA 3.0, plus original test notes and scripts. See `autocad-kb/LICENSE.md`. |

## Using the generators

```
pip install python-docx reportlab pymupdf pillow openpyxl
```

1. Copy `template-library/company.example.json` to your own file and fill in your company details. Logo and signature paths are optional.
2. Copy a template's `sample_data.json` and replace the fake values with your job's data.
3. Run the generator, for example:

```
python template-library/templates/daily-report/build_daily_report.py my_data.json --company my_company.json
```

Each `TEMPLATE.md` lists the data keys and options for that generator.

## Notes

- Sample data and sample outputs use made-up names: Example Mechanical, Sample ISD, Pat Doe, and 555 phone numbers.
- For Texas lien waivers, use the statutory forms in Texas Property Code section 53.284.
- Nothing here is legal advice. Check your own contracts and local rules.
