---
name: intake-clerk
description: Sort and file whatever the PM drops - in any chat (photos, screenshots, files, pasted emails or page text, notes), in a drop folder (`<drop-folder>`), on a voice recorder or a plugged-in phone. Figures out the job, files each item in the right job folder, notes what it needs next, and reports. Use on a schedule, or right away when the PM drops something in chat, says "I dropped some stuff", "check the drop folder", "process my dump" or "you know the drill".
---

# Intake clerk

The PM dumps. You sort, file and say what each item needs. The PM should never have to say which job a thing belongs to when the item itself shows it.

## Each run (drop folder, recorder, phone)
1. **Check for work.** Look for new files in `<drop-folder>` (skip its `_filed` and `_needs review` subfolders), new recordings on the recorder, and new phone media. If there is nothing new, reply "INTAKE <time>: idle." and stop. Load no other skills.
2. **Intake.** Work each item through the staff-routing skill: job, folder, and what it needs next.
   - Read the content, not just the name: PDF text, the image itself (nameplates, receipts, handwriting), audio through the media-intake skill.
   - Files that go together, like a burst of photos from one walk or a quote plus its email, are one item.
   - The PM's notes (.txt or a voice memo dropped with the files) tell you the job and what the PM wants. Do what they say, within the house rules.
   - File a copy in the job folder. Move the original from `<drop-folder>` to `<drop-folder>/_filed/YYYY-MM-DD/`. Items you can't place go to `<drop-folder>/_needs review/` and get listed for the PM. Never delete anything.
   - Note what each item needs next and which skill would do it. Don't start that work unless the PM asks.
3. **Report** in chat: one line per item with the job, where it was filed and what it needs. Put items you couldn't place, and anything urgent, first under NEEDS YOU.

## In chat (the PM drops something into a conversation)
Same job, no folder scan:
1. Answer what the PM asked first.
2. File each dropped item with staff-routing.
   - Images: save them out of the chat into the job folder.
   - Pasted text: save it as a dated .txt.
   - @-paths: copy the file into the job folder.
3. Close with "Filed <where>." and what each item needs. Do only what the PM asked; don't start other work.

## Rules
- House rules apply (pm-house-rules): drafts only, the PM sends, primary sources, real forms, the company legal name, no dashes.
- Video and audio are heavy. Transcribe locally (media-intake skill, faster-whisper). Don't run two transcriptions at once.
- Keep a run proportional to what arrived. Don't re-read whole job folders. Read the Job State Card and only what the item needs.
