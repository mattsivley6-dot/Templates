# Templates

Paths below are relative to this `pm-packet` folder.

## Job folder (make these on Day 1)
Use this scheme for every job folder. More detail: `../checklists/Job Folder Structure Guide.docx`.
```
<NUMBER>-<CUSTOMER>-<Scope>
  _RUNNING NOTES.txt          (Job State Card on top)
  02-Plans and Specs
  03-Site Survey
  05-Vendor Quotes
  06-Proposal
  07-Contract and PO
  08-Submittals
  10-Subcontractors
  12-Correspondence           (emails, transcripts)
  13-Field Reports
  16-Receipts and Tickets
  18-Closeout
  20-Submission Packets       (<NUMBER>_<Short>_Booking Package: 01-Equipment, 02-Proposal, 03-Submittals, 04-Estimate, 05-Transition)
  30-Photos and Videos        (Data Plates inside)
  90-Working Files
```
Pre-booking jobs (no number yet): `<CUSTOMER>-<Scope>` with Photos and Videos, Data Plates, Transcripts. Rename and add the numbered folders on award.

## Checklists (in `../checklists`)
| Need | File |
|---|---|
| Project checklist, 10 phases | `../checklists/Project Checklist - Start to Finish.docx` |
| Project life cycle | `../checklists/Project Life Cycle.docx` |
| Customer meeting checklist | `../checklists/Customer Meeting Checklist.xlsx` |
| RTU install workflow | `../checklists/RTU Install Workflow.docx` |
| Job folder guide | `../checklists/Job Folder Structure Guide.docx` |
| New vendor setup | `../checklists/New Vendor Setup Note.docx` |
| Public bid checklist (Texas) | `../checklists/TX Public-Entity Bid - DQ Prevention Checklist.md` |
| RFI log, daily report, pre-task plan | `../checklists/planning/` |

## Document generators (in `../template-library/templates`)
| Need | Folder |
|---|---|
| Daily report, daily log | `daily-report`, `daily-log` |
| RFI | `rfi` |
| PCO and its cover email | `pco`, `pco-email-cover` |
| Pay app | `pay-app` |
| Transmittal | `transmittal` |
| Photo log | `photo-log` |
| Notice of concealed condition | `notice-of-concealed-condition` |
| Meeting minutes, site walk minutes, action items | `oec-meeting-minutes`, `site-walk-minutes`, `action-items-tracker` |
| Warranty matrix, warranty closeout letter | `warranty-matrix`, `warranty-closeout` |
| Project binder | `project-binder` |
| Duct shop ticket | `duct-shop-ticket` |
| Capacity letter | `capacity-letter` |

Each generator reads your company details from `../template-library/company.example.json`. See each folder's `TEMPLATE.md`.

## Not in this repo
Use your company's own handoff form (transition package), estimator, labor rate sheet, vendor setup and tax exempt forms, bonding forms and contact list. For lien waivers, use the statutory forms your state requires.

## Packet forms (in `forms`)
| Need | File | When |
|---|---|---|
| Prefunctional checklist | `forms/Prefunctional Checklist.docx` | Before startup, one per unit |
| Startup checklist with readings | `forms/Startup Checklist.docx` | At startup, one per unit |
| Owner training record | `forms/Owner Training Record.docx` | At training, everyone signs |
| Punch list | `forms/Punch List.docx` | At the completion walk |
| Acceptance form | `forms/Acceptance Form.docx` | Private jobs. Public owners use their own |
| Lessons register | `forms/Lessons Register.xlsx` | Every closeout, 3 lines minimum |
| RACI | `forms/RACI.xlsx` | Who does what. Fill in your roles and confirm with your managers |
| Communications plan | `forms/Communications Plan.xlsx` | Who tells whom what, and when |
