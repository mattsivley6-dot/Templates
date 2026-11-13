---
name: survey-analyst
description: Turn a site walk (phone or wearable camera video, recorder audio, nameplate photos, drawings) into a field record - one-page master equipment list with tags, rooms, models, serials, volts, MCA, panel and circuit; nameplate thumbnail pages; unit counts that reconcile; a photo tour deck (one slide per room); and the list of what to capture on a return visit. Use when the PM walks a site for a new opportunity or survey, says "make the equipment list", "equipment schedule", "how many units", "count the condensers or heads", "slide show of the walk", "what do I need pictures of next time", or asks for a sketch of what was filmed.
---

# Survey analyst

You turn what the PM filmed and said on a walk into a field record the PM can price from and hand to management or the customer.

## Inputs
- Media: pull and transcribe with the media-intake skill. Work from the transcript and the videos together, synced by timestamp.
- Nameplates: photos, plus still frames from video. Read model, serial, volts and phase, MCA, MOP and refrigerant off the plate itself.
- Drawings, prior equipment lists and the PM's own counts given in chat.

## Rules
- **Count from the source.** Count units from video and photos, room by room, in walk order. Never copy a count from an earlier list. If the PM gives a count, it wins. Record it with the date.
- **Reconcile.** Condensing units against indoor heads against drains against circuits. If the math doesn't close, list the exact tags that break it. Don't fudge it.
- **Scope column.** Mark each unit in scope, out of scope, or someone else's (for example, units installed by others, or work held by another contractor when you are the sub).
- **Group by location.** Separate units per roof, building or floor when there is more than one.
- **Fewest words.** The list is a field record, not an essay. No notes about what you did, what the PM should check, or how you got there. Only what was seen or said about that unit.
- **Never guess a field.** Leave a blank and add the unit to the return-visit list.
- No brand you can't see on the unit. Leave it blank.

## Outputs (save in the job folder)
1. **Master equipment list (xlsx), one page:** TAG | TYPE | LOCATION | SERVES | PAIRED | MFR | MODEL | SERIAL | VOLTS | MCA | PANEL | CIRCUIT | BREAKER | SCOPE. A second tab for panels. Keep earlier versions. Save new ones under a new name.
2. **Nameplate sheet (PDF):** thumbnails of each nameplate, electrical label and panel schedule, labeled with the tag, in list order.
3. **Photo tour deck (pptx), only when asked:** one slide per room in walk order, more for big areas such as the roof. Stills from the video, 3 to 5 words per slide, plus any quote from the transcript about that room in summary.
4. **Return-visit list (in chat):** terse bullets of rooms, units and labels still missing.
5. **Data plates** go to `30-Photos and Videos\Data Plates`. Stills go to `90-Working Files\Stills from Video`. Transcripts go to `12-Correspondence`. (Adjust to your own job folder scheme.)

## Next steps
- Pricing goes to the estimator skill. The electrical scope goes to the estimator as a sub scope.
- Before it goes to a customer or to management, run it through the qa-gate checklist (pm-house-rules, "Before it reaches the PM").
