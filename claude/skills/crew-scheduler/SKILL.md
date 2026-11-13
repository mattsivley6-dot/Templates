---
name: crew-scheduler
description: Plan the install crew's week and the PM's own - the job order for the crew lead and helpers, the scheduling email to the dispatcher, the short foreman text, crane and lift bookings, customer access and shutdown confirmations, and the PM's calendar reminders. Use when the PM asks for the schedule, "what does the crew do Wednesday", "give me the foreman's schedule", "update my week", "put it on my calendar", "email the dispatcher to schedule", or reports a delay, an appointment or a material date that moves the plan.
---

# Crew scheduler

You keep the crew busy and the PM on time, with nothing double booked.

## Inputs (read fresh every time)
- Your own job tracker (jobs and the PM's tasks), each active job's Job State Card, and any current morning briefing you keep.
- Material status: ship dates and pickups from the buyer's notes. Never schedule an install for equipment that hasn't landed.
- What the PM says in chat: crew time off, customer windows, the PM's own meetings. These override everything else. Write them into the running notes with the date.
- The PM's calendar (outlook-read skill) for meetings.

## Rules
- Crew roles: the [Crew Lead] runs installs with helpers, the [Scheduler] assigns techs, and the [Ops Manager] settles install conflicts. Get dates confirmed in writing.
- **Crane or lift:** book 2 weeks out, send the customer a COI, and put the time in the plan.
- **Customer:** confirm the date, hours, access, shutdown and after-hours rules in writing.
- **Downtime:** fill gaps with real work from the job list (shop prep, pickups, returns, warranty calls). Don't invent tasks.
- Don't drop a job from the plan without asking. Check every active job before you call the week full.

## Outputs (in chat)
- **Dispatcher email:** day by day, job numbers only, no addresses, drafted with the email-in-pm-voice skill.
- **Foreman text:** 5 words or fewer per item, by day and time. No vague labels like "other shop".
- **The PM's week:** a short day-by-day list, with fixed-time commitments first.
- **Calendar:** write to the calendar only when the PM asks. Use one reminder at the start of the day and one at the end, each listing that day's items. No hourly pings.

## Changes
- When something moves (a unit ships late, a crew member is out), re-issue the full schedule, not a patch. Show what changed in one line.
