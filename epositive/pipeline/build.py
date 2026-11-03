"""Assemble an E Positive reel: scene PNGs + voice.wav + soft generated music -> 1080x1920 (9:16) MP4,
with closed captions burned in (synced to the voice) and a matching .srt file next to the MP4.
Usage: python3 build.py outdir "b1,b2,b3,b4,b5" out.mp4 rYYYYMMDD.json
bN = scene boundary times (s) in voice.wav; last scene runs to the end of the voice + 1.2 s.
The script JSON's "voice" holds the spoken text, one part per scene separated by " ... ".
"""
import sys, os, re, json, subprocess, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

out, bounds, dst = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3]
script = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
FPS, XF, TAIL = 30, 0.35, 1.2

w = wave.open(f"{out}/voice.wav"); vdur = w.getnframes() / w.getframerate()
total = vdur + TAIL
cuts = [0.0] + bounds + [total]
durs = [cuts[i + 1] - cuts[i] for i in range(len(cuts) - 1)]

# soft ambient pad (C - Am - F - G), 48 kHz stereo
SR = 48000
t = np.arange(int(total * SR)) / SR
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
pad = np.zeros_like(t)
seg = 4.0
for k in range(int(total // seg) + 1):
    s0, s1 = int(k * seg * SR), int(min((k + 1) * seg + 1.0, total) * SR)
    if s0 >= len(t):
        break
    tt = t[s0:s1] - k * seg
    env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (seg + 1.0 - tt) / 1.2))
    for f in chords[k % 4]:
        pad[s0:s1] += env * (np.sin(2 * np.pi * f / 2 * tt) + 0.3 * np.sin(2 * np.pi * f * tt) + 0.1 * np.sin(2 * np.pi * f * 2 * tt))
# gentle bell on each scene change
for c in cuts[1:-1]:
    i0 = int(c * SR); n = int(1.5 * SR)
    tt = np.arange(n) / SR
    bell = np.sin(2 * np.pi * 784 * tt) * np.exp(-tt * 3) * 0.6
    pad[i0:i0 + n] += bell[: len(pad) - i0]
pad /= np.abs(pad).max()
fade = np.minimum(1, np.minimum(t / 1.0, (total - t) / 1.5))
pad = (pad * fade * 0.11 * 32767).astype(np.int16)
with wave.open(f"{out}/music.wav", "wb") as m:
    m.setnchannels(1); m.setsampwidth(2); m.setframerate(SR); m.writeframes(pad.tobytes())


# ---------- closed captions (burned in + .srt) ----------
FONT = os.path.expanduser("~/.fonts/NotoSansSinhala[wdth,wght].ttf")
CC_W, CC_FS, CC_MAXCH = 760, 52, 46      # box text width (px), font size, chars per caption card


def pauses(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return [(a + b) / 2 for a, b in zip(st, en)]


def chunks(text):
    out_, cur = [], ""
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        for w in sent.split():
            if cur and len(cur) + 1 + len(w) > CC_MAXCH:
                out_.append(cur); cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur and len(cur) > CC_MAXCH * 0.45:
            out_.append(cur); cur = ""
    if cur:
        out_.append(cur)
    # don't leave a lone short word (e.g. "කරන්න.") as its own flash cue: merge it back
    if len(out_) > 1 and len(out_[-1]) < 12 and len(out_[-2]) + 1 + len(out_[-1]) <= CC_MAXCH * 1.3:
        last = out_.pop(); out_[-1] = out_[-1] + " " + last
    return out_


def cc_png(text, path, font):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if cur and font.getlength(t) > CC_W:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    lh = int(CC_FS * 1.5); h = lh * len(lines) + 36
    bw = int(max(font.getlength(l) for l in lines)) + 64
    cx = 110 + 400  # centre of the safe column (x 110-910)
    y1 = 1505 - h   # box sits above the bottom 20% (y 1536+)
    d.rounded_rectangle([cx - bw // 2, y1, cx + bw // 2, y1 + h], 24, fill=(0, 0, 0, 170))
    for k, l in enumerate(lines):
        d.text((cx, y1 + 18 + k * lh + lh // 2), l, font=font, fill=(255, 255, 255, 255), anchor="mm",
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(path)


def srt_time(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s_:02},{ms:03}"


cues = []
if script and script.get("voice"):
    parts = [x.strip() for x in script["voice"].split("...") if x.strip()]
    if len(parts) == len(durs):
        spans = [(cuts[i], min(cuts[i + 1], vdur)) for i in range(len(parts))]
    else:  # parts don't line up with scenes: spread the whole text over the voice
        parts, spans = [" ".join(parts)], [(0.0, vdur)]
    pz = pauses(f"{out}/voice.wav")
    for text, (a, b) in zip(parts, spans):
        ch = chunks(text); tot = sum(len(c) for c in ch); t = a
        for k, c in enumerate(ch):
            end = b if k == len(ch) - 1 else t + (b - a) * len(c) / tot
            rest = (b - a) * sum(len(x) for x in ch[k + 1:]) / tot  # time the remaining chunks need
            near = [p for p in pz if abs(p - end) < 0.6 and t + 0.6 < p < b - max(0.4, 0.7 * rest)]
            if k < len(ch) - 1 and near:
                end = min(near, key=lambda p: abs(p - end))
            cues.append((t, end, c)); t = end
    font = ImageFont.truetype(FONT, CC_FS, layout_engine=ImageFont.Layout.RAQM)
    try:
        font.set_variation_by_axes([700, 100])
    except Exception:
        pass
    for k, (a, b, c) in enumerate(cues):
        cc_png(c, f"{out}/cc{k}.png", font)
    with open(os.path.splitext(dst)[0] + ".srt", "w") as f:
        for k, (a, b, c) in enumerate(cues, 1):
            f.write(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n\n")

# video: each scene a slow zoom, joined with short crossfades
inputs, filt = [], []
for i, d in enumerate(durs):
    dd = d + (XF if i < len(durs) - 1 else 0)
    n = int(dd * FPS) + 1
    inputs += ["-loop", "1", "-t", f"{dd:.3f}", "-i", f"{out}/s{i+1}.png"]
    z = "1+0.0006*on" if i % 2 == 0 else "1.06-0.0006*on"
    filt.append(f"[{i}:v]scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps={FPS},trim=duration={dd:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
prev, off = "v0", 0.0
for i in range(1, len(durs)):
    off += durs[i - 1]
    filt.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off - 0:.3f}[x{i}]")
    prev = f"x{i}"
for k, (a, b, c) in enumerate(cues):
    inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", f"{out}/cc{k}.png"]
    j = len(durs) + k
    filt.append(f"[{prev}][{j}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[c{k}]")
    prev = f"c{k}"
na = len(durs) + len(cues)
inputs += ["-i", f"{out}/voice.wav", "-i", f"{out}/music.wav"]
filt.append(f"[{na}:a]aresample=48000,apad=whole_dur={total:.3f},volume=1.6[va];[{na+1}:a]aresample=48000[ma];[va][ma]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5[a]")
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
       "-map", f"[{prev}]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", dst]
subprocess.run(cmd, check=True)
print("ok", round(total, 2), [round(d, 2) for d in durs], f"{len(cues)} captions")
if not 15 <= total <= 90:
    print(f"WARNING: reel is {total:.1f} s; reels and Shorts must be 15-90 s")
