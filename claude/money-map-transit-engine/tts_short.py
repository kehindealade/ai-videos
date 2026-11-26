import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
import shorts as SH
k = Kokoro('/root/kokoro/kokoro-v1.0.onnx', '/root/kokoro/voices-v1.0.bin')
for name in ("S1", "S2"):
    S = getattr(SH, name)
    durs = []
    for i, (sc, line) in enumerate(S["lines"]):
        a, sr = k.create(line, voice=S["voice"], speed=S["speed"], lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 600): nz[-1] + 2400]
        sf.write("%s_%02d.wav" % (name, i), a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open(name + "_durs.json", "w"))
    print(name, round(sum(durs), 1), flush=True)
