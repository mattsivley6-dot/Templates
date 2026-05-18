# PMI Project Artifact Templates

PMBOK Guide 7th Edition–aligned project artifact templates, kept here as the
single source of truth across projects.

## Templates

| File | PMBOK Artifact | Performance Domain / Process |
| --- | --- | --- |
| [01_Risk_Register.docx](templates/01_Risk_Register.docx) | Risk Register | Uncertainty |
| [02_RFI_Log.docx](templates/02_RFI_Log.docx) | Issue Log (RFI variant) | Stakeholder / Delivery |
| [03_Daily_Status_Report.docx](templates/03_Daily_Status_Report.docx) | Status Report | Project Communications |
| [04_Change_Request_Form.docx](templates/04_Change_Request_Form.docx) | Change Request | Integrated Change Control |
| [05_Project_Closeout_Checklist.docx](templates/05_Project_Closeout_Checklist.docx) | Closeout Checklist | Close Project or Phase |

All templates use PMI-standard field sets (Risk Score, Response Strategy,
Residual Risk, RYG performance indicators, CCB Disposition, etc.) with
bracketed `[Placeholder]` text where project-specific values belong.

## How to use

1. Copy the template you need from `/templates/` into the relevant project folder.
2. Rename it to follow the project's naming convention.
3. Fill the `[bracketed]` placeholders. Leave the PMBOK structural fields alone.
4. Version-bump the **Document Version** in the Document Control header on
   each material revision; keep the **Date Reviewed** column current on
   registers.

## Updating the templates

The templates are generated from `scripts/build_templates.py` so the format
stays consistent. To change a template:

1. Edit `scripts/build_templates.py`.
2. Run `python scripts/build_templates.py`.
3. Commit the updated `.docx` and the script in the same commit.

Do **not** hand-edit the `.docx` files in `/templates/` if the change should
apply to future projects — edit the generator and re-run.

## Conventions

- Template filenames are stable; do not rename without bumping a major
  version and updating downstream references.
- Each artifact contains a **Document Control** header (Project, Document
  Type, Version, Issue Date, Prepared By, Distribution, PMI Reference) — keep
  this on any derived project copy.
- Field changes that depart from PMBOK 7th Edition should be documented in
  this README under a **Deviations** section.

## Reference

- PMBOK Guide, 7th Edition — Project Management Institute
- PMI Standards: <https://www.pmi.org/standards/pmbok>
