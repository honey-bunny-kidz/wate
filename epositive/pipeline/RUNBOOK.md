# E Positive daily runbook

Facebook page **E Positive** (Buffer channel `6add9b2c2f1f5ed648c4cd68`, org `6adb2e3a79a82670835a5497`, timezone Asia/Colombo).
Every day: one Sinhala text post at **7:30 AM** and one Sinhala reel at **8:00 PM**.

## Reel & Short rules (user, 2 Nov 2026 — apply to EVERY reel, Short and video)
1. **Mobile 9:16**: 1080×1920. Keep everything important out of the bottom 20% (y ≥ 1536) and the right 15% (x ≥ 918) where the app's buttons and caption sit. `scenes.py` already lays out inside these zones.
2. **Length 15–90 s** (aim 40–60 s). `build.py` warns if outside. Use 6–9 scenes.
3. **Closed captions on every spoken line**: put the exact spoken text in the JSON's `"voice"` (one part per scene, separated by ` ... `) and pass the JSON as the 4th argument to `build.py`. It burns synced captions in (y ≈ 1290–1505) and writes `<name>.srt` next to the MP4. build.py merges a lone trailing word into the previous caption and won't snap a cue so late that the next one flashes for < 0.5 s. Check a few frames: caption matches the words heard, nothing clipped.
   Because captions carry the full sentence, scene headlines stay SHORT: ≤ 2 lines / ~30 Sinhala characters, a keyword or the hook (the script auto-shrinks longer ones, but write them short). Scene-1 hook renders at 104 px: keep it to 2 short lines or it runs into the caption box.
4. **Ask the community to share**: the last spoken line and the endcard ask people to share with a specific person ("O/L ලියන යාළුවෙක්ට share කරන්න", "අම්මට share කරන්න"…); vary the person every day. No giveaways, no "share or else".
5. **Short captions** (Buffer text) for reels, Shorts and videos: 1–2 short lines (≤ ~150 characters) with the hook, then ONE share line ("🔁 <person>ට share කරන්න"), then 3–5 hashtags. No long explanations, no book lists — at most "(Atomic Habits)" in the hook line.

## Each daily run
1. `list_posts` for the channel (status scheduled + sent, last/next 3 days). Skip anything already scheduled.
2. Pick today's theme from `trends.md` (rotate; check the date hooks first), paired with one idea from a positive thinking book. Retell ideas in our own words; never quote books at length.
3. **Reel for today 8:00 PM** (if not already scheduled):
   - Write 6–9 scenes in `rYYYYMMDD.json` (see `r20261102.json`): `"voice"` (spoken text, one part per scene separated by ` ... `), and per scene: art name, SHORT Sinhala headline (`<b>` = amber highlight), optional kicker. Last scene = `endcard` with the share ask.
     Art available in `scenes.py`: books, note_cant, note_yet, plant, steps, endcard, rain_cloud, paddy, glasses, bulb, rain_sun, frog, trophy, hourglass, phone_off, heart, tea, five, rocks_jar, ice, ice_melt, alarm, battery_low, battery_full, lamp_one (one lit + one unlit clay lamp), lamps_two, lamps_row (Deepavali / Poya / kindness), circles / circles_big (worry vs what you can do; small inner circle → grown inner circle), coconut / coconut_hits / coconut_crack (stonecutter: every hit counts). Add new SVG art in `ART` when the theme needs it (keep the teal #0F5257 / amber #F4A623 / cream style).
   - Voice: Google AI Studio → https://aistudio.google.com/generate-speech in the user's Chrome (already signed in). Create new dialog, paste the full voiceover (scenes separated by ` ... `), Style: "Warm, calm and encouraging native Sri Lankan Sinhala speaker, like a kind older sibling. Clear pronunciation, gentle pace, short pause between sentences." On the landing page the cards jump down once the page finishes loading — take a screenshot before clicking "Create new dialog". Run, then click the player's Download button (the user approved this daily). File lands in `/Users/thilanmj/Downloads/Generated Audio <date> - <time>.wav`; stage it with device_stage_files and copy to `out/voice.wav`.
   - `ffmpeg -i out/voice.wav -af silencedetect=n=-38dB:d=0.35 -f null -` → pick the 5 scene boundaries at the middle of the pauses between scenes.
     Better: list the speech segments (`silencedetect=n=-35dB:d=0.25`, start/end pairs) and match them sentence by sentence (≈ 11–12 letters/s, short blips are breaths); the TTS does NOT always pause longer at ` ... `, so don't assume the longest pauses are the scene breaks (3 Nov: the first long pause was mid-scene 3).
    If too few pauses show up, use `n=-32dB:d=0.2`, estimate each boundary from the share of Sinhala letters per scene (letters / total × voice length) and snap to the nearest pause; check the last scene's internal pauses make sense.
     Voice speed ≈ 10–12 Sinhala letters per second (29 Oct: ~500 letters → 39.8 s; 31 Oct: 247 → 27.4 s; 2 Nov: 256 → 28.3 s; 3 Nov: 463 Sinhala + ~70 Latin letters → 49.0 s; 7 Nov: 467 → 50.2 s; 9 Nov: 433 → 48.0 s (scene breaks matched phrase-by-phrase, a lone "නෑ." showed as a 0.2 s blip), every sentence/comma phrase showed as its own -35dB segment, so matching letters per phrase worked first time). For a 40–60 s reel write ~450–650 letters; never more than ~950 (90 s cap); at least ~150 (15 s).
   - `python3 scenes.py rYYYYMMDD.json out && python3 build.py out "b1,…,bN-1" out/epositive_reel_YYYYMMDD.mp4 rYYYYMMDD.json` (one boundary per scene change) then grab frames and LOOK at them (headline and captions inside the safe zones, captions match the voice, nothing clipped). Push the `.srt` with the MP4 (for YouTube Shorts uploads later).
   - Push the MP4 to `epositive/` in this repo; Buffer reel URL = `https://raw.githubusercontent.com/honey-bunny-kidz/wate/main/epositive/<file>`; `create_post` with metadata.facebook.type = "reel", assets = [{"video":{"url":…,"metadata":{"title":…}}}], customScheduled 20:00:00+05:30.
4. **Post for tomorrow 7:30 AM** (if not scheduled). EVERY post has an image — never text-only (text-only posts reached 3 people in week 1).
   - Format by weekday: Mon/Wed/Fri = **carousel** (5 slides: cover → 3 tips → CTA; albums get the most shares), Tue/Thu/Sat/Sun = **single quote card**.
   - Write `pYYYYMMDD.json` (see `p20261028.json` carousel, `p20261029.json` single) and run `python3 cards.py pYYYYMMDD.json outP`. 1080×1350 (4:5).
     Themes rotate: teal, sunrise, night, mint, rose (don't repeat yesterday's). Art: drops, sunrise, heart, phone_off, rain_sun, lamp, javelin, jar, books, plant, steps, note_cant, note_yet, endcard; add new SVG art to `cards.py` when the topic needs it.
     Title ≤ 8 words with ONE `<b>` highlight; body ≤ 2 short lines; kicker = book · author.
   - LOOK at every slide (contact sheet) before posting: no clipped or overlapping text.
   - Push JPGs to `epositive/img/ep_YYYYMMDD_N.jpg`; Buffer assets = [{"image":{"url":…,"metadata":{"altText":…}}}, …] in slide order.
   - Caption (short): line 1 = hook that matches the image (+ "👉 Swipe" on carousels); optional "✨ අද අභියෝගය:" one line; "🔁 <specific person>ට share කරන්න"; 3–5 hashtags `#EPositive #ධනාත්මකසිතුවිලි #SriLanka` + 1–2 topical. Keep it under ~250 characters before the hashtags.
   - metadata.facebook.type = "post".
4b. **Reel growth rules**: scene 1 must be a hook readable in under 2 seconds (a question or a surprising number, big text); 15–90 s (aim 40–60 s) with a reason to keep watching to the end (a reveal, a number, a step-by-step); caption follows the short-caption rule above.
4c. **Weekly series** (keeps people coming back): Mon "සඳුදා අභියෝගය" (week challenge), Wed "පොතක් විනාඩියෙන්" (one book idea), Fri "O/L Countdown" until 7 Dec, Sun "ඔබේ කතාව" (ask followers for their small win of the week).
4e. **Comments**: week 1 had 0 comments on every post. End captions and endcards with a one-tap reply ask (a single word, emoji or A/B choice) rather than an open question.
4d. **Sunday review**: get_aggregated_post_metrics for the last 7 days plus per-post numbers (list_posts sent); note which topics/formats got most reach and shares in `epositive/pipeline/metrics.md` (date, post, format, impressions, reactions, comments, shares) and lean the next week toward the winners.
5. Delete reels from `epositive/` once Buffer shows them sent.
6. Buffer free plan: max 10 scheduled posts across ALL pages. If full, schedule the reel first.

- build.py takes ~3 min for a 48 s reel: run it in the background (`nohup … > out/build.log &`) and poll with `ps aux | grep -c "[b]uild.py"` — `pgrep -f "build.py out"` inside the same bash command matches itself and loops forever.
- AI Studio: the first click on Run right after closing the Style menu may only close the menu; check for the player bar (≈0:4x duration at the bottom) and click Run again if it's missing.
- If the device bridge is offline after the voice download, the WAV is also in the AI Studio page as an `<audio>` data URL; retry staging later rather than regenerating.

## Setup in a fresh session
- Fonts: `git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts gfonts && cd gfonts && git sparse-checkout set ofl/notosanssinhala && mkdir -p ~/.fonts && cp ofl/notosanssinhala/*.ttf ~/.fonts/ && fc-cache -f`
- Playwright + Chromium + ffmpeg are preinstalled.
