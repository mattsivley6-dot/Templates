---
name: media-intake
description: The PM's end-of-day media drill. Pull today's photos, videos and audio from a plugged-in iPhone, an iPhone backup, a wearable camera's synced media or a USB voice recorder, transcribe, file into job folders, update running notes, and report job status and to-dos. Use when the PM says "you know the drill", "pull my media", "transcribe the recorder", "camera videos", or anything about phone, camera or recorder media.
---

# Media intake and transcription drill

Scope is TODAY's media unless the PM says otherwise.

## 1. Start the slow things first, in parallel
- Launch classic Outlook (see the outlook-read skill) so mail syncs while you work.
- Start the media pull.

## 2. Get the media (fastest path first)

**Plugged-in, unlocked iPhone.** Use Shell COM: `Shell.Application`, Namespace(17), then `Apple iPhone\Internal Storage\YYYYMM_a`.
- `CopyHere` runs at 20 to 30 MB/s.
- An empty Internal Storage means the phone is locked.

**Which phone.** If more than one phone is in use, know which one holds which media (for example, a wearable camera usually syncs to one phone only).

**Timestamps.**
- WPD file times are UTC. Convert to local time, and mind daylight saving changes.
- Some wearable cameras give files random names. Identify the device by the EXIF Make field.
- GPS is in the photo EXIF and in the MP4 location tag.
- The MP4 creation_time is the import time. The file date is the capture start.

**No phone plugged in.** Use the newest unencrypted backup under `<backup folder>\<UDID>` (the folder where your iTunes or Apple Devices app saves backups).
- Manifest.db maps the files.
- CameraRollDomain holds DCIM.
- Text messages and contacts are also in the backup. Read them only when the PM asks for a specific thread.

**USB voice recorder (`<recorder drive>`).**
- The recorder clock may drift. Work out the offset once (device date against real date) and note it.
- A voice-activated recorder's timestamps are elapsed position, not wall clock.
- Take real times from phone photo EXIF.

**Locations.** Verify job locations by forward-geocoding the job's public address and comparing it to the photo GPS locally. Never send the PM's coordinates out.

## 3. Transcribe

**Before you start.** Check whether a transcript already exists, in the Transcripts folder or 12-Correspondence. Never transcribe the same recording twice.

**Short camera clips.** Use faster-whisper large-v3, int8. It runs at about 1x realtime with 8 threads.

**Long recorder WAVs.** Use faster-whisper medium.en, int8, with VAD off.
- ffmpeg-slice the file first: `ffmpeg -ss S -t D -i in.wav slice.wav`.
- Transcribe the slices in parallel, each with a timestamp offset.
- Never pass clip_timestamps on the full file. That causes 1 GB allocations and MemoryError deaths.

**Resource limits.**
- Each whisper process uses about 1.3 GB of RAM. Cap parallel processes to fit the machine (about 4 on a 16 GB machine).
- Do not run transcription alongside heavy browser work.

**Keep it safe.**
- Flush every segment to disk as it is written.
- Watch log-file growth. A process with no growth and low CPU is wedged: kill it and re-slice.

**Transcribe the tails.** The dictation after a site visit often holds the ordering summary.

**Tell the PM about long waits.** If local transcription will take more than about 15 minutes, say so. The PM may prefer a cloud transcription service, which can be much faster on a long file.

## 4. File it
Never move or overwrite the PM's existing files. In the job folder:
- **`_RUNNING NOTES.txt` at the root.** Keep the JOB STATE block on top current. Then add today's dated block, newest on top, with facts, quotes with mm:ss, and open items.
- **Whole videos and photos** go in `30-Photos and Videos`, named `YYYY-MM-DD_HHMM_<what>_<original id>`.
- **Data plates** go in `30-Photos and Videos\Data Plates`.
- **Picked stills** go in `90-Working Files\Stills from Video`.
- **Transcripts** go in `12-Correspondence`.
- **Vendor submittals from email** go in `05-Vendor Quotes\<vendor>`.
- **Pre-booking jobs** (no job number yet) use a simple set of folders: Data Plates, Photos and Videos, Transcripts, Stills from Video.
- **Otherwise** follow your own standard job folder scheme.

## 5. Report in chat
- For each job: what was captured, its status, and a short to-do list.
- The to-do source is your own job tracker.
- Do not edit the tracker unless the PM asks.
