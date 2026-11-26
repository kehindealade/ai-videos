import soundfile as sf, numpy as np, sys, json
from kokoro_onnx import Kokoro
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")
LINES = ["Every morning, I still make her tea.", "She's been gone forty days."]
voice = sys.argv[1] if len(sys.argv) > 1 else "bm_george"
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.92
out, meta, t = [], [], 0.25
sr = 24000
out.append(np.zeros(int(0.25 * sr)))
for i, s in enumerate(LINES):
    a, sr = k.create(s, voice=voice, speed=speed, lang="en-us")
    meta.append((s, t, t + len(a) / sr))
    out.append(a)
    t += len(a) / sr
    gap = 0.3 if i < len(LINES) - 1 else 0.0
    out.append(np.zeros(int(gap * sr)))
    t += gap
y = np.concatenate(out)
sf.write("vo.wav", y, sr)
json.dump(meta, open("vo.json", "w"))
print(json.dumps(meta), len(y) / sr)
