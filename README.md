# Submittal Templates

Single source of truth for the three submittal artifacts used on every
project. Styled to match the live Centric / EMA submittal package format.

## Templates

| File | Purpose |
| --- | --- |
| [01_Transmittal.docx](templates/01_Transmittal.docx) | Delivery cover / routing slip. Includes the empty red A/E review stamp at the bottom — filled in by the Engineer on return. |
| [02_Submittal_Cover_Sheet.docx](templates/02_Submittal_Cover_Sheet.docx) | Per-submittal title page — Project / Engineer / Prime Contractor / Sub / Contractor Action stamp. |
| [03_Submittal_Index.docx](templates/03_Submittal_Index.docx) | Itemized contents (Item / Description / Spec Section) plus Contractor's Remarks. |

All three are stripped of project-specific data — `[bracketed]` placeholders
mark fields to fill per project.

## How to use

1. Copy the template you need from `/templates/` into the relevant project folder.
2. Rename it following the project's naming convention.
3. Fill the `[bracketed]` placeholders. Leave the structural fields alone.
4. The red A/E review stamp area on the transmittal is left blank — the
   Architect/Engineer completes that section on return.

## Updating the templates

Templates are generated from `scripts/build_submittal_templates.py` so
formatting stays consistent. To change a template:

1. Edit `scripts/build_submittal_templates.py`.
2. Run `python scripts/build_submittal_templates.py`.
3. Commit the updated `.docx` files and the script in the same commit.

Do **not** hand-edit the `.docx` files in `/templates/` if the change
should apply to future projects — edit the generator and re-run.
