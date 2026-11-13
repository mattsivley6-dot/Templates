---
name: estimator
description: Price an HVAC or mechanical job - scope in BuildOps quote style, takeoff and hours, line items (labor, equipment, material, rental, subcontractor, truck charge) with your markup ladder, margin check against your margin floor, vendor and sub RFQs, options and phases, and comparisons to past jobs. Use when the user asks for a quote, proposal, scope, line items, "what do I put in BuildOps", pricing, an estimate, a takeoff, an RFQ to a vendor or sub, how a price compares to past jobs, or whether a job is worth bidding.
---

# Estimator

You turn a site walk, drawings or a customer ask into a price the PM can defend, keyed the way BuildOps (or your own quoting system) wants it.

## Sources, in this order
1. **The job.** Walk transcript, photos and nameplates, drawings and specs, the customer's email. Start in the job folder (`_RUNNING NOTES.txt`).
2. **Vendor and sub quotes in writing.** Never estimate equipment cost. If there is no quote, write the RFQ.
3. **Your history.** Similar past jobs and quotes in your quoting system, with their actual hours and cost (read only). Name the job and quote numbers you compare to.
4. **Company numbers.** All of these come from your own files. None are built into this skill.
   - Quote structure, markup ladder, standard clarifications, standard excludes and scope pattern: your own quoting guide.
   - **Labor cost:** the loaded labor rate for the crew's branch or region. Build it from your burden-rate sheet:
     - Wage-based items scale with the wage (retirement match, workers' comp, Medicare, federal and state unemployment). Express them as one percent of wage: [burden %].
     - Per-hour items stay flat no matter the wage (medical, Social Security as your sheet carries it, truck, uniforms, direct office support): [flat $/hr].
     - Loaded cost = wage + (wage x [burden %]) + [flat $/hr]. Check that this math reproduces the sheet's own regular rates before you use it.
     - Overtime cost = (wage x 1.5) + (wage x 1.5 x [burden %]) + [flat $/hr].
     - The loaded rate carries no overhead or profit. The sell price carries those.
     - Don't use averages that mix branches or regions, and don't use old ladder costs or rough calculator multipliers for cost. They understate cost and overstate margin.
   - **Labor sell:** your current customer rate sheet, regular and overtime, by labor class (for example installer or tech, working foreman). Overtime sell = regular sell x [overtime multiplier]. Use the same rate sheet for T&M and service-rate work.
   - Keep a small rate table in your own notes (not in this skill):

     | Line | Unit Cost (key this) | Unit Price (sell) | Margin |
     |---|---|---|---|
     | Installer / tech, regular | [loaded cost] | [sell rate] | [calc] |
     | Working foreman, regular | [loaded cost] | [sell rate] | [calc] |
     | Installer / tech, overtime | [loaded cost] | [sell rate] | [calc] |
     | Working foreman, overtime | [loaded cost] | [sell rate] | [calc] |

   - In BuildOps, key Unit Cost and Unit Price and let Markup calculate. If BuildOps auto-fills a different Unit Cost, override it with the loaded rate.
   - Margin targets: your size-band ladder (for example under [$A] at [x]%, [$A] to [$B] at [y]%, and so on). **Your margin floor is [floor]% gross margin.** Below it, stop and tell the PM.
   - Takeoffs and public bids: copy your takeoff workbook template and fill the copy, never the template.
   - Your own estimating brief (principles, takeoff method, notes for public owners), if you keep one.
5. **Model output.** One past proposal folder you treat as the model: its entry sheet and its paste-ready scope. Copy that structure. Keep the scope short (3 to 6 word bullets).

## Steps
1. **Scope first, in chat.** What we replace, reuse and exclude. Ask only the questions that move the price more than about 5%. Number them, and give the default you'll assume for each.
2. **RFQs.** Bare-bones emails to vendors and subs (email-in-pm-voice).
   - Include exact model, voltage, phase, tonnage, quantity, need-by date and ship-to or pickup.
   - Ask for submittals and lead time.
   - On public bids, just ask the equipment manufacturers' reps to put you on the bid list.
3. **Takeoff and hours.** Show how the hours were built: crew size times days, next to a comparable job's actual hours. Add for after hours, occupied buildings, lifts, cranes and phasing. Say why the hours are what they are.
4. **Entry sheet.** Save it as `06-Proposal\BuildOps entry sheet - <short>.txt` (or your own proposal folder).
   - Header: customer, property, job name, salesperson, prior job.
   - Labor: one line per worker.
   - Items: Material, Equipment, Rental Equipment, Subcontractor, Truck Charge or Other, with the vendor quote number in the description.
   - Cost, markup and sell on every line, then totals and gross margin.
   - Subs never go in the labor table.
5. **Scope text, in the PM's quote format.** Model it on the PM's own recent quotes. It is the description of ONE pricing section named "Scope". Nothing goes in the Scope of Work tab or Issue Description (Internal Notes gets the internal summary in step 6).
   - Plain lines, one step per line, in work order. No dashes, no numbers, no price, no "plus tax" (BuildOps prints the section price and the total including tax).
   - Then "Notes:" lines: equipment model, crane included, hours, warranty worded as the vendor proposal words it, lead time or price validity.
   - Then one "Not included:" paragraph with this job's real risks, ending "Any of these require written approval before work proceeds."
   - If your proposal template already prints standard clarifications and excludes, never type them into the quote.
6. **Keying it in BuildOps. Only on the PM's go, and this checklist every time:**
   - Info tab: Quote Title in the PM's words (on a placeholder customer, lead with the real customer and site). Project manager and Sold by: the PM. Department, Pricebook and Job type: your own install settings. Expiration: [x] days. **Quote Due By = today, the date the quote is made.** Property and Company representatives when the contacts exist. Issue Description stays empty. Internal Notes: one short internal note with the real customer and site, contacts, lead source, each vendor quote number with its price and validity, and the entry sheet path.
   - Pricing tab: rename the default section "Scope" and paste the scope text as its description. Labor: your install labor item, descriptions "Lead Tech" and "Tech", payroll and billing hour types set to regular time, then override Unit Cost and Unit Price to your rate table, Bill Hrs = Hrs. Items from the Item List: "Equipment" (vendor proposal number in the description), "Subcontractor" (for example "Crane"), "Material" ("Misc."), "Truck Charge" (cost type Other, qty = trips, taxed or not per your tax rules). Set the tax rate to your local rate unless the customer is exempt. Read the Profitability box back against the entry sheet before saying it is done.
   - **Forms & Attachments: attach every vendor quote (equipment proposal and submittal, crane, electrician, any sub) as an Internal File.**
   - Leave it in Draft. Never generate or send. Tell the PM the quote number.
7. **Options and phases.** Each one is a separate quote ("Option A" and "Option B", or "Quote 1 of 2"). Priced adders stay off the customer copy unless the PM wants them shown.
8. **Margin check.** Total cost, total sell and gross margin, against the ladder and the floor. Show a lean version, with its floor, only if the PM asks.
9. **Customer note.** A few lines in a friendly PM tone on why this option, through email-in-pm-voice.

## Rules
- Every number has a source: a vendor quote, a past job record, a rate file or the PM. Never assume. Never guess a number.
- Quote pre-tax when the customer or you hold a resale or exemption certificate. Otherwise add your local sales tax on top. Follow your state's rules on whether the truck charge is taxed.
- Stay under the customer's budget cap when the PM gives one.
- Don't key anything into BuildOps without the PM's go. Give the entry field by field in chat.
- Run the qa-gate checklist before you hand it over.

## Output in chat
1. Scope text in the PM's quote format (the "Scope" section description), paste-ready.
2. Line items: labor first, then items, each with cost, markup and sell.
3. Total, margin and the comparable job or jobs.
4. Open questions and RFQs still out.
