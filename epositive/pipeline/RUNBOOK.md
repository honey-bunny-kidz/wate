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
     If too few pauses show up, use `n=-32dB:d=0.2`, estimate each boundary from the share of Sinhala letters per scene (letters / total × voice length) and snap to the nearest pause; check the last scene's internal pauses make sense.
     Keep the voiceover ≤ ~420 Sinhala letters to stay under 35 s (29 Oct: ~500 letters → 39.8 s).
   - `python3 scenes.py rYYYYMMDD.json out && python3 build.py out "b1,b2,b3,b4,b5" out/epositive_reel_YYYYMMDD.mp4` then grab frames and LOOK at them (text inside the art, nothing clipped).
   - Push the MP4 to `epositive/` in this repo; Buffer reel URL = `https://raw.githubusercontent.com/honey-bunny-kidz/wate/main/epositive/<file>`; `create_post` with metadata.facebook.type = "reel", assets = [{"video":{"url":…,"metadata":{"title":…}}}], customScheduled 20:00:00+05:30.
4. **Post for tomorrow 7:30 AM** (if not scheduled). EVERY post has an image — never text-only (text-only posts reached 3 people in week 1).
   - Format by weekday: Mon/Wed/Fri = **carousel** (5 slides: cover → 3 tips → CTA; albums get the most shares), Tue/Thu/Sat/Sun = **single quote card**.
   - Write `pYYYYMMDD.json` (see `p20261028.json` carousel, `p20261029.json` single) and run `python3 cards.py pYYYYMMDD.json outP`. 1080×1350 (4:5).
     Themes rotate: teal, sunrise, night, mint, rose (don't repeat yesterday's). Art: drops, sunrise, heart, phone_off, rain_sun, lamp, javelin, jar, books, plant, steps, note_cant, note_yet, endcard; add new SVG art to `cards.py` when the topic needs it.
     Title ≤ 8 words with ONE `<b>` highlight; body ≤ 2 short lines; kicker = book · author.
   - LOOK at every slide (contact sheet) before posting: no clipped or overlapping text.
   - Push JPGs to `epositive/img/ep_YYYYMMDD_N.jpg`; Buffer assets = [{"image":{"url":…,"metadata":{"altText":…}}}, …] in slide order.
   - Caption: line 1 = hook that matches the image (+ "👉 Swipe කරලා බලන්න" on carousels); 2–4 short lines; "✨ අද අභියෝගය:"; "💬" question; "📌 Save කරගන්න · <specific person> කෙනෙක්ට share කරන්න"; (Idea: author, book); hashtags `#EPositive #ධනාත්මකසිතුවිලි #PositiveThinking #SriLanka` + 1–2 topical.
   - metadata.facebook.type = "post".
4b. **Reel growth rules**: scene 1 must be a hook readable in under 2 seconds (a question or a surprising number, big text); keep reels 20–35 s so people watch to the end; caption line 1 repeats the hook and ends with a share prompt aimed at a specific person ("O/L ලියන යාළුවෙක්ට share කරන්න").
4c. **Weekly series** (keeps people coming back): Mon "සඳුදා අභියෝගය" (week challenge), Wed "පොතක් විනාඩියෙන්" (one book idea), Fri "O/L Countdown" until 7 Dec, Sun "ඔබේ කතාව" (ask followers for their small win of the week).
4d. **Sunday review**: get_aggregated_post_metrics for the last 7 days plus per-post numbers (list_posts sent); note which topics/formats got most reach and shares in `epositive/pipeline/metrics.md` (date, post, format, impressions, reactions, comments, shares) and lean the next week toward the winners.
5. Delete reels from `epositive/` once Buffer shows them sent.
6. Buffer free plan: max 10 scheduled posts across ALL pages. If full, schedule the reel first.

## Setup in a fresh session
- Fonts: `git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts gfonts && cd gfonts && git sparse-checkout set ofl/notosanssinhala && mkdir -p ~/.fonts && cp ofl/notosanssinhala/*.ttf ~/.fonts/ && fc-cache -f`
- Playwright + Chromium + ffmpeg are preinstalled.
