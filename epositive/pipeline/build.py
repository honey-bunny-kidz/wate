"""Assemble an E Positive reel: scene PNGs + voice.wav + soft generated music -> 1080x1920 MP4.
Usage: python3 build.py outdir "b1,b2,b3,b4,b5" out.mp4
bN = scene boundary times (s) in voice.wav; last scene runs to the end of the voice + 1.2 s.
"""
import sys, subprocess, wave, numpy as np

out, bounds, dst = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3]
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
na = len(durs)
inputs += ["-i", f"{out}/voice.wav", "-i", f"{out}/music.wav"]
filt.append(f"[{na}:a]aresample=48000,apad=whole_dur={total:.3f},volume=1.6[va];[{na+1}:a]aresample=48000[ma];[va][ma]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5[a]")
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
       "-map", f"[{prev}]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", dst]
subprocess.run(cmd, check=True)
print("ok", round(total, 2), [round(d, 2) for d in durs])
