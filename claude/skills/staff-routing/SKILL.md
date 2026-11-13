---
name: staff-routing
description: Who on the PM's AI staff owns what. Maps any incoming item (photo, video, audio, PDF, email, note) to the job, the folder it's filed in, the AI employee responsible, and the action that employee takes. Used by the intake-clerk and the inbox-sweep. Load it whenever new material arrives and has to be filed and acted on.
---

# Staff routing

Every new item gets four answers: **which job, which folder, which employee, what action.** Then the employee does the action, drafts only.

## 1. Which job
Try these in order. Stop at the first solid match.
1. A job, project or quote number in the file name, folder, email subject or text. Use your own numbering scheme to tell them apart (for example J-0001 is a job, 2026-0001 is a project, Q-1001 is a quote). Map it to a folder through the job folder names under `<jobs root>\` and your job number index.
2. The PM's own note: a .txt or voice memo dropped with the item, a subfolder name, or the email the PM forwarded it with.
3. Names in the content: customer, property, address, contact, vendor or sub tied to one active job (job state cards, your own job tracker).
4. Photo GPS against job addresses. Geocode the job's public address. Never send the user's photo coordinates anywhere. Compare locally.
5. Equipment: a model or serial that matches one job's submittal, quote or nameplates.

If two jobs fit, or none does, don't guess. Put the item in `<drop folder>\_needs review\` and ask in one line with your best guess.

New site, no job yet: make a pre-booking folder `<jobs root>\<CUSTOMER>-<Scope>` with `30-Photos and Videos\Data Plates` and `12-Correspondence`. Tell the PM.

## 2. Which folder (use the job's existing folder if its name differs)
This is an example job folder layout. Adjust it to your own.

| Item | Folder |
|---|---|
| Site photos and videos | `30-Photos and Videos`, named `YYYY-MM-DD_HHMM_<what>_<original name>` |
| Nameplates and data plates | `30-Photos and Videos\Data Plates` |
| Audio and transcripts, emails, letters | `12-Correspondence` |
| Drawings and specs | `02-Plans and Specs` |
| Vendor and sub quotes, IOMs, product data | `05-Vendor Quotes\<Vendor>` |
| Our proposals | `06-Proposal` |
| Customer PO, signed proposal, contract, bonds, COI | `07-Contract and PO` |
| Submittals | `08-Submittals` |
| Sub paperwork, sub invoices, lien waivers | `10-Subcontractors` |
| Daily and field reports | `13-Field Reports` |
| Receipts, packing lists, bills of lading, tickets | `16-Receipts and Tickets` |
| Closeout, warranty, O&M | `18-Closeout` |
| Anything else useful | `90-Working Files` |

Copy into the job folder. Never overwrite. If a file with that name exists, add `_2`.

## 3. Which employee and what action (drafts only)
| What arrived | Employee | Action |
|---|---|---|
| Walk video, photos or nameplates for a job not yet sold | survey-analyst | Update or start the master equipment list and the return-visit list |
| Install-day photos or video on an active job | doc-controller | Add a dated line to the running notes. On projects, add a daily report line |
| Audio from the recorder or phone | media-clerk | Transcribe, file, give the gist and action items |
| Vendor or sub quote | estimator | Add it to the entry sheet, re-run margin, flag changes against the last version |
| Submittal, order acknowledgment, or equipment arriving | buyer | Match check (model, volts, phase, hand, curb, options) against what was sold and the nameplates |
| Ship notice, tracking, packing list, bill of lading | buyer | Update the ship date on the job state card. Check the delivery against the PO |
| Sub or vendor invoice, lien waiver, card receipt | billing-clerk | Check against the PO and the work. Draft the approve-to-pay or fix-it note for [Billing/AP]. Stamp receipts with the PO number |
| Customer PO, signed proposal, "approved", "go ahead" | the PM | Award steps: job state card, sales-to-operations handoff package, transition checklist. Suggest the tracker update |
| RFP, bid invite, addendum, bid results, new lead | bid-clerk | Day-1 intake, due dates, bid checklist. Sort lead notes into entries for your own CRM |
| Extra work asked, hidden condition, PCO markup or rejection, a sub not performing | claims-writer | Price or log it. Draft the notice. Add to the timeline with the evidence |
| Owner or GC asks for a submittal, RFI, permit or inspection item, or a form | doc-controller | Build it or fill it field by field |
| Closeout list, warranty request, O&M or as-built ask | closeout-clerk | Update `_CLOSEOUT STATUS.md` and gather primary-source documents |
| Schedule change, crew issue, delivery date that moves an install | crew-scheduler | Re-issue the week plan and the foreman text. Draft the note to [Scheduler] if the slip changes the schedule |
| A technical question from the field | tech-advisor | Answer with the manufacturer's source |
| Job cost, hours or margin question | cost-analyst | Margin now and at completion |
| Work finished | billing-clerk | Draft the ready-to-invoice note for [Billing/AP] |
| Anything that needs a reply | correspondent | Draft the whole reply in the PM's voice (email-in-pm-voice) |

- One item can trigger more than one employee. A delivered unit with a damaged crate goes to the buyer and to the correspondent (claim email to the vendor).
- Money, signature, legal and customer-facing drafts get the qa-gate's verdict before they reach the PM (pm-house-rules).
- PO receipts and invoices go to your company's accounts payable inbox, as a draft for the PM to send.

## 4. What never happens without the PM
- Sending, replying, forwarding, uploading or submitting anything.
- Any change in BuildOps (or your job system), an owner portal or the calendar.
- Deleting anything. Editing the job tracker (list suggested tracker changes instead).
- Taking over the screen.

## 5. The report (fewest words)
```
<CLERK> <time>: <n> new
- <Job>: <what arrived> -> <where filed>. To <employee>: <action>.
NEEDS YOU:
1. <decision or approval, one line>
DRAFTS READY: <list. Full text below, each with To, Subject and body>
TRACKER: <suggested updates, one line each>
```
- Nothing new: one line, "<CLERK> <time>: nothing new." No notification.
- Anything under NEEDS YOU or DRAFTS READY: send one notification with a one-line summary.
- Add a dated line to each touched job's `_RUNNING NOTES.txt`, and update its job state card when status, next action or waiting-on changed.
