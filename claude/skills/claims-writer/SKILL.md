---
name: claims-writer
description: Write change orders and build the record in disputes - PCOs and CORs with sub backup and booked labor hours, notices of concealed conditions, NTE and overrun letters, BuildOps change order entries, chronological timelines and daily logs from the record, and proof packets or one-page summaries of a sub's or customer's non-performance built only from primary evidence (email PDFs, text screenshots, photos). Use when the PM finds a hidden condition, the customer adds work, a PCO gets marked up or rejected, the PM needs to prove what happened, a sub isn't performing, or the user says change order, PCO, notice, claim, timeline, "prove it" or "build the case".
---

# Claims writer

You get the contractor paid for extra work and build an accurate record of what happened.

## Change orders (PCOs)
1. **Price before work.** Stop, price it, get it signed, then work. Concealed condition: photo and written notice the same day.
2. **Read the contract first.** Find the change order clause, notice periods, markup rules, and how labor is allowed (for example, some contracts allow labor at cost only, with no overhead, profit or overtime premium). Cite only sections you've opened and quoted.
3. **Labor:**
   - Booked hours from your job cost system and the timesheets, by person and date. Never move or re-date hours. Flag any request to.
   - Rate: the job's agreed rate. With no contract rule, use loaded cost plus your markup (estimator skill). Under an at-cost clause, use loaded cost and attach a loaded labor rate buildup exhibit that shows how the rate was built.
4. **Subs:** attach each sub's own quote or invoice on their letterhead, newest version only. Their overhead and profit stay inside their number.
5. **Fewest words on the face.** Every extra word is something the other side can argue with. Firm lines say firm. NTE lines say not to exceed. Funding and contingency talk goes in the cover email, not the PCO.
6. **Red team.** Read it as the owner rep and the engineer, using every objection they raised before. Search the job's meeting transcripts and markups.
7. **Build:** the PCO on your own PCO form, plus `template-library/templates/pco-email-cover` and `template-library/templates/notice-of-concealed-condition`. Save each revision in a new dated folder. Never overwrite.
8. **BuildOps (or your system):** enter the COR with the latest numbers (with margin unless the contract says at cost) only with the PM's go. Give the entries field by field.

## Timelines and proof packets
- **Primary evidence only:** real email PDFs, text-message screenshots, photos with date and GPS, call logs, signed documents. Never retype a conversation onto letterhead.
- **Timeline format:** date | who | what | evidence file. Quote exactly. Include the facts that show a pattern, such as requests left unanswered, information given to the owner but not to the PM, and unsafe conditions left behind.
- **One-pager on request:** 5 to 7 items. Cold facts, no stretches, no adjectives.
- **Letters** (certified mail, notice of default, letter to a sub's owner): firm and kind. State the next step only if the PM has decided it. Never threaten a step the PM hasn't chosen.

## Output
- In chat: the PCO or letter text, the price buildup, the evidence list and the open risks. Files go in `14-Change Orders` or `12-Correspondence` (or your own folders) under a dated folder.
- Everything goes through the qa-gate before the PM sees it.
