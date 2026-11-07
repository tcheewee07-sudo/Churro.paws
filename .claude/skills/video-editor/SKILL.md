---
name: video-editor
description: Edit the user's raw videos into finished posts for Instagram Reels, TikTok or YouTube — cut retakes and pauses with Whisper word timestamps, split multi-video recordings, add on-brand captions and graphics, level mixed AI/real voices, fix low light, and export at top quality. Use whenever the user asks to edit, cut, trim, caption, reformat, clean up or prepare a video for posting.
---

# Video editor

The user is the director. You do the cutting. Follow every rule below, in order, on every edit.

## Setup (once per computer)

Mac: `brew install ffmpeg node` then `pip3 install -U openai-whisper`. Copy this repo's `.claude/skills/*` folders into `~/.claude/skills/` so they work in every project. Whisper downloads its model the first time it runs (base.en is about 140 MB, small about 460 MB).

Tools: FFmpeg, Whisper (`openai-whisper`), Node.js. For animated captions, titles and graphics, use the HyperFrames skills (`hyperframes`, `hyperframes-registry`, `media-use`) when they are installed.

## 1. Ask three questions before every edit

Before touching anything, ask all three in one message:

1. **Where is it going?** Instagram, TikTok, or YouTube (or several)?
2. **What should viewers do at the end?** (follow, comment, click link, visit site, nothing)
3. **Captions and graphics, or just a clean cut?**

Do not start until all three are answered. Answers decide format (rule 6), end card/CTA text, and whether to add captions.

## 2. Never touch the original

- Never modify, move, rename or overwrite the source file.
- Copy it into a work folder **outside iCloud Drive, Dropbox, OneDrive or Google Drive** (large files time out in synced folders). Default: `~/VideoWork/<original-name>-<YYYYMMDD-HHMM>/`. If the source itself is inside a synced folder, still copy out first.
- Do all intermediate work in that folder.
- Save each finished video **next to the original** under a new name: `<original-name>_<platform>_edit.mp4` (e.g. `walk_tiktok_edit.mp4`). If that name exists, add `_v2`, `_v3` — never overwrite.

## 3. Transcribe, remove retakes, tighten pauses

1. Extract audio: `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 audio.wav`
2. Transcribe with word-level timestamps:
   `whisper audio.wav --model small --word_timestamps True --output_format json --output_dir .`
   (use `medium` if accuracy is poor and time allows; set `--language en` if known)
3. Find retakes from the transcript:
   - A sentence that is started and then restarted (same or near-same opening words repeated) → keep only the **last complete, cleanest** take; drop the earlier attempts.
   - Phrases like "let's redo that", "let me start again", "one more time", "cut that", "take two" → drop the failed take before them **and** the phrase itself.
   - If two takes are both complete, keep the one with fewer stumbles/filler words; when unsure, keep the later one and mention it in the handoff.
4. Cut every silence/gap **longer than 0.5 s** down to about 0.15–0.25 s (keep a natural breath, not zero). Use word timestamps for gaps between words; confirm with `ffmpeg -af silencedetect=noise=-35dB:d=0.5`.
5. Build a cut list (keep segments), then render with `ffmpeg` (trim/atrim + concat filter) — re-encode, don't stream-copy, so cuts are frame-accurate. Add ~30 ms audio crossfades at joins to avoid clicks.
6. Show the user a short summary of what was cut (number of retakes removed, total time saved).

## 4. Split multi-video recordings

If one recording clearly contains several separate videos (new intro/greeting, "next video", long pause + topic change, a clap/slate, a different outfit or location), split it into separate files and edit each one as its own video: `<original-name>_part1_<platform>_edit.mp4`, `_part2_…`. Tell the user how many you found and where each starts before editing them.

## 5. Make it look like the user

Order of precedence:
1. A branding skill or brand files (brand guide, `brand.json`, style sheet) if one exists — use its colours, fonts and voice.
2. Otherwise use the **saved brand below**.
3. If nothing is saved and nothing is found, ask **once** for two brand colours and one font, then write them into the "Saved brand" section of this file so you never ask again.

If a folder named **`B-roll kit`** exists (check the source video's folder, its parents, and the home folder), pull the logo, photos and graphics from it for intros, end cards and cutaways.

### Saved brand

Taken from the user's Churro site (`assets/css/style.css`, `index.html`):

| Role | Value |
|---|---|
| Brand colour 1 (primary) | Amber `#ffb37b` |
| Brand colour 2 (accent) | Coral `#ff7a8a` |
| Extra accent | Magenta `#d67bff` (gradient: amber → coral → magenta) |
| Background / dark | Deep purple `#150f26` |
| Light text | `#f7f4ff` |
| Heading / caption font | Plus Jakarta Sans (ExtraBold 800) |
| Body font | Inter |
| Voice | Warm, playful, dog-centred ("Churro — Professional Good Boy") |

Caption style: Plus Jakarta Sans ExtraBold, white `#f7f4ff` text, 4–6 px deep-purple `#150f26` outline, the current/key word highlighted in amber `#ffb37b`. 1–4 words per line, lower-middle of frame (above platform UI on 9:16, about 70% down). Fonts: Google Fonts (OFL). Install them if missing.

Generate captions from the Whisper JSON with `scripts/make_captions.py transcript.json captions.ass --width 1080 --height 1920`, then burn in with `ffmpeg -vf ass=captions.ass`. For animated titles, end cards and graphics, use HyperFrames.

## 6. Formats and quality

| Platform | Aspect | Resolution | fps |
|---|---|---|---|
| Instagram Reels, TikTok | 9:16 vertical | 1080×1920 | source fps (max 60) |
| YouTube | 16:9 wide | 1920×1080 (3840×2160 if source is 4K) | source fps |

- Reframe, don't squash. Never blind centre-crop wide footage to 9:16: check frames and crop to the subject (follow it if it moves), or blur-fill the background if cropping would cut the subject.
- Keep vertical safe zones clear of captions and graphics: top 220 px and bottom 380 px on 1080×1920.
- Always export at the highest quality: `-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -movflags +faststart -c:a aac -b:a 320k -ar 48000`. Never upscale beyond the source unless asked; never re-encode more times than needed (do one final encode from the cut list).

## 7. Mixed voices (AI + real)

If a video has both an AI/synthetic voice and the user's real voice:
- Separate the segments by speaker (transcript timing + voice character; ask the user if unclear).
- Level each group on its own to about **−14 LUFS integrated** (`loudnorm=I=-14:TP=-1.5:LRA=11`, two-pass), and apply gentle compression and EQ to the real voice so it isn't quieter or thinner than the AI voice.
- Check the final mix: the two voices should be within ±1 LU of each other. Music, if any, sits 18–22 dB under speech.

## 8. Low light

If footage is dark or grainy:
- Fix what you can: exposure/gamma lift (`eq`), mild contrast and saturation, denoise (`hqdn3d` or `nlmeans`, light settings so faces don't go waxy).
- Export a before/after still and **tell the user honestly** how it looks.
- If faces are still muddy, noise is heavy, or highlights are crushed, say plainly that a **reshoot with more light** would look noticeably better. Don't oversell the fix.

## 9. Handoff

When finished, tell the user:
- The **full path** of every finished file.
- What you changed (cuts, retakes removed, time saved, captions, format, audio, light fixes) and anything you were unsure about.
- A reminder: **"Watch it once all the way through before you post. You're the director."**
