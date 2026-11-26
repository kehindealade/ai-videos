import soundfile as sf, numpy as np, sys, json
from kokoro_onnx import Kokoro
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")
LINES = ["My boss ruined my day at 8 am.", "So I tried four things to fix it.", "Keep count."]
voice = sys.argv[1] if len(sys.argv) > 1 else "am_onyx"
out, meta, t = [], [], 0.25
sr = 24000
out.append(np.zeros(int(0.25 * sr)))
for i, s in enumerate(LINES):
    a, sr = k.create(s, voice=voice, speed=1.0, lang="en-us")
    meta.append((s, t, t + len(a) / sr))
    out.append(a)
    t += len(a) / sr
    gap = 0.2 if i < len(LINES) - 1 else 0.0
    out.append(np.zeros(int(gap * sr)))
    t += gap
y = np.concatenate(out)
sf.write("vo.wav", y, sr)
json.dump(meta, open("vo.json", "w"))
print(json.dumps(meta), len(y) / sr)
