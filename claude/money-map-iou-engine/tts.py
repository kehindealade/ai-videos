import json, os, sys, hashlib, numpy as np, soundfile as sf
import importlib
C = importlib.import_module(sys.argv[1])
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
k = None
info, files = [], []
for i, ln in enumerate(C.L):
    v = ln.get("voice", C.VOICE); sp = ln.get("speed", C.SPEED)
    p = os.path.join(out, hashlib.md5((v + str(sp) + ln["text"]).encode()).hexdigest()[:12] + ".wav")
    if not os.path.exists(p):
        if k is None:
            from kokoro_onnx import Kokoro
            k = Kokoro('/root/kokoro/kokoro-v1.0.onnx', '/root/kokoro/voices-v1.0.bin')
        a, sr = k.create(ln["text"], voice=v, speed=sp, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 600): nz[-1] + 2400]
        sf.write(p, a, sr)
        print("new", i, round(len(a)/sr,1), flush=True)
    info.append(sf.info(p).duration); files.append(os.path.basename(p))
json.dump(info, open(os.path.join(out, "durs.json"), "w"))
json.dump(files, open(os.path.join(out, "files.json"), "w"))
print("total speech", round(sum(info), 1), "lines", len(info))
