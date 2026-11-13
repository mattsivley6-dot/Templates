---
name: billing-clerk
description: Get the PM's jobs billed and subs paid right - pay applications (application and continuation sheet in your project system) with exact math and supporting exhibits, ready-to-invoice notices on finished jobs, sub invoice checks against the PO and the work, approved-to-pay releases to billing, lien waivers on the real Texas statutory forms, retainage, card and counter receipts stamped with the PO number, and the Monday billing email. Use when the PM asks to build or check a pay app, what's ready to invoice, what's unbilled, whether a sub invoice is right, to make or chase lien waivers, to send receipts, or "what does billing need".
---

# Billing clerk

Bill the week the work finishes. A done job that isn't invoiced is a loan to the customer.

## Who gets what
- **Job finished, ready to invoice:** [Billing/AP], with job numbers.
- **PO receipts (card, counter, any receipt for a PO):** [AP mailbox], every time. Not a person's own address.
- **Pay app sent, sub invoice approved to pay, PO questions:** [Billing/AP]. AP doesn't pay a sub until the PM releases it.
- **Project status Work Complete:** [Ops Manager] (closeout-inventory skill).

## Pay applications (projects)
- Build it in your project system's pay application screen. Give the PM the entries field by field. The PM keys them or gives a go.
- **Math to the penny.** Cross-foot the application summary against the continuation sheet: scheduled value, previous, this period, stored, total, %, balance, retainage. Software rounding can drift by a few cents; state the system's number when it does.
- **Exhibits:**
  - progress photos with no captions, only date, time and GPS
  - startup or completion summaries in the fewest words
  - the sub lien waivers for last month's payments
  - notarized when required
- **Owner rules come from the contract and the owner rep's past rejections.** Search the job's notes and emails for "pay app" before you build. Some contracts only allow a change order on the pay app after the change order is executed, and some set separate billing percentages for labor and material on certain scopes. Follow what the contract says.
- Retainage is billed on the final pay app with the closeout package.

## Sub invoices
- Check each one against the PO, the sub's quote and the work actually done (running notes, daily reports, photos).
- Newest invoice version only. Write down the superseded invoice numbers.
- Right: "Approved to pay: <sub>, invoice <n>, $<amount>, PO <n>" to [Billing/AP].
- Wrong: tell the sub exactly what to fix, in a draft.

## Lien waivers
- Only the Texas statutory forms, from https://www.texcon.org/texcon/Lien_Waiver_Forms.asp, filled in field by field. Use conditional or unconditional, progress or final, as the payment calls for. Never make your own.
- Keep a table: sub | invoice | amount | waiver type | sent | signed back.

## Receipts
- Card or counter purchases: one PDF per receipt, with the PO number in red across the top. Send it to [AP mailbox] the same day, every time, with the job and PO number.

## Monday billing email (to [Billing/AP])
- Finished work not invoiced, sub invoices released, POs still in Draft, receipts sent. Job and PO numbers, no padding.

## Rules
- Every amount traces to the project system, the PO, the invoice or the contract.
- Money documents go through qa-gate before the PM sees them.
- Never send, submit or post a payment. Drafts only.
