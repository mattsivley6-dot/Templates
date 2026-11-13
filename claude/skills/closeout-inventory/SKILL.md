---
name: closeout-inventory
description: Build or refresh one job's closeout status in a single saved file. It covers what the owner and GC require, what is done, what is missing, who owes it, and what changed since the last check. Use when the PM asks what is missing for closeout, closeout status, O&Ms, warranties, as-builts, record drawings, final pay app, lien releases, or "what do we lack" on a job.
---

# Closeout inventory

Keep one list per job, in one file, updated in place. Never start a new inventory from scratch when the file exists.

## The file
- The file is `<job folder>\_CLOSEOUT STATUS.md`.
- If it exists, read it first and update it.
- The top line records the date of the last check.

## Requirements (build once, then reuse)
Draw the requirements from two sources:
1. **The job's own requirements:**
   - the contract and spec closeout sections: Division 01 closeout, 23 05 93 TAB, and 23 08 00 commissioning if present
   - any closeout list or portal checklist from the owner or GC
2. **Your company project checklist,** its closeout phases.

Merge them into one requirement list, and record where each requirement came from. Reuse that list on every later run. Add to it only when a new requirement appears.

## Evidence (every run)
- **Folders:** the job folder's closeout folder (for example `18-Closeout`).
- **Email:** work email since the last check, from the owner rep, GC, subs and vendors. Use the outlook-read skill and check both the Inbox and Sent Items.
- **Project system:** project status and invoices, read only.

An item counts as done only when a file or an email proves it. Cite that proof.

## Output
1. Update the file with a table: Requirement | Source | Status (Done, Partial, Missing, Waiting) | Proof (file, or email with date) | Owner | Next step.
2. Add a "Changed since <last date>" section.
3. In chat, give the PM only three things: what changed, what is still missing, and who owes each item.

## Rules
- Never invent a document or form. If the owner's form is missing, say so.
- Never send anything. Draft emails in chat for the PM to send.
- Set finished projects to the status your company uses for finished work (for example Work Complete rather than Closed). Ask [Ops Manager] if unsure.
