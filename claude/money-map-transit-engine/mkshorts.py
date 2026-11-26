import json, sys, numpy as np, soundfile as sf, subprocess
import shorts as SH
name, out = sys.argv[1], sys.argv[2]
S = getattr(SH, name)
d = json.load(open(name + "_durs.json"))
tl, total = SH.render(S, d, name + "_v.mp4")
sr = 24000
mix = np.zeros(int((total + 0.5) * sr))
for i, (t0, dd) in enumerate(tl):
    a, _ = sf.read("%s_%02d.wav" % (name, i))
    j = int((t0 + 0.05) * sr)
    mix[j:j + len(a)] += a
    if i == 0:
        n = int(0.35 * sr); tt = np.arange(n) / sr
        mix[:n] += 0.5 * np.sin(2 * np.pi * (70 - 40 * tt) * tt) * np.exp(-tt * 12)
sf.write(name + "_a.wav", mix.astype(np.float32), sr)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", name + "_v.mp4", "-i", name + "_a.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
print("ok", out, total)
