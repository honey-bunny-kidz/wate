# E Positive daily runbook

Facebook page **E Positive** (Buffer channel `6add9b2c2f1f5ed648c4cd68`, org `6adb2e3a79a82670835a5497`, timezone Asia/Colombo).
Every day: one Sinhala text post at **7:30 AM** and one Sinhala reel at **8:00 PM**.

## Each daily run
1. `list_posts` for the channel (status scheduled + sent, last/next 3 days). Skip anything already scheduled.
2. Pick today's theme from `trends.md` (rotate; check the date hooks first), paired with one idea from a positive thinking book. Retell ideas in our own words; never quote books at length.
3. **Reel for today 8:00 PM** (if not already scheduled):
   - Write 6 scenes in `rYYYYMMDD.json` (see `r20261027.json`): art name, Sinhala caption (`<b>` = amber highlight), optional kicker. Scene 6 = `endcard`.
     Art available in `scenes.py`: books, note_cant, note_yet, plant, steps, endcard. Add new SVG art in `ART` when the theme needs it (keep the teal #0F5257 / amber #F4A623 / cream style).
   - Voice: Google AI Studio → https://aistudio.google.com/generate-speech in the user's Chrome (already signed in). Create new dialog, paste the full voiceover (scenes separated by ` ... `), Style: "Warm, calm and encouraging native Sri Lankan Sinhala speaker, like a kind older sibling. Clear pronunciation, gentle pace, short pause between sentences." Run, then click the player's Download button (the user approved this daily). File lands in `/Users/thilanmj/Downloads/Generated Audio <date> - <time>.wav`; stage it with device_stage_files and copy to `out/voice.wav`.
   - `ffmpeg -i out/voice.wav -af silencedetect=n=-38dB:d=0.35 -f null -` → pick the 5 scene boundaries at the middle of the pauses between scenes.
   - `python3 scenes.py rYYYYMMDD.json out && python3 build.py out "b1,b2,b3,b4,b5" out/epositive_reel_YYYYMMDD.mp4` then grab frames and LOOK at them (text inside the art, nothing clipped).
   - Push the MP4 to `epositive/` in this repo; Buffer reel URL = `https://raw.githubusercontent.com/honey-bunny-kidz/wate/main/epositive/<file>`; `create_post` with metadata.facebook.type = "reel", assets = [{"video":{"url":…,"metadata":{"title":…}}}], customScheduled 20:00:00+05:30.
4. **Post for tomorrow 7:30 AM** (if not scheduled): Sinhala text, emoji header, idea in 2–3 short lines, "✨ අද අභියෝගය:" daily challenge, "💬" question, hashtags `#EPositive #ධනාත්මකසිතුවිලි #PositiveThinking #SriLanka` + 1–2 topical ones. metadata.facebook.type = "post".
5. Delete reels from `epositive/` once Buffer shows them sent.
6. Buffer free plan: max 10 scheduled posts across ALL pages. If full, schedule the reel first.

## Setup in a fresh session
- Fonts: `git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts gfonts && cd gfonts && git sparse-checkout set ofl/notosanssinhala && mkdir -p ~/.fonts && cp ofl/notosanssinhala/*.ttf ~/.fonts/ && fc-cache -f`
- Playwright + Chromium + ffmpeg are preinstalled.
