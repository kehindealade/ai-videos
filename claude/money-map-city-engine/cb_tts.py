import json, os, sys, hashlib, importlib, numpy as np, soundfile as sf, warnings
warnings.filterwarnings("ignore")
C = importlib.import_module(sys.argv[1]); out = sys.argv[2]; ref = sys.argv[3]
os.makedirs(out, exist_ok=True)
m = None; info, files = [], []
for i, ln in enumerate(C.L):
    txt = ln.get("cb", ln["text"])
    p = os.path.join(out, hashlib.md5(("cb" + ref + txt).encode()).hexdigest()[:12] + ".wav")
    if not os.path.exists(p):
        if m is None:
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            m = ChatterboxTurboTTS.from_pretrained(device="cpu")
        w = m.generate(txt, audio_prompt_path=ref).squeeze(0).numpy().astype("float32")
        nz = np.where(np.abs(w) > 0.01)[0]
        w = w[max(0, nz[0] - 600): nz[-1] + 2400]
        if m.sr != 24000:
            import librosa; w = librosa.resample(w, orig_sr=m.sr, target_sr=24000)
        sf.write(p, w, 24000)
        print("new", i, round(len(w) / 24000, 1), flush=True)
    info.append(sf.info(p).duration); files.append(os.path.basename(p))
json.dump(info, open(os.path.join(out, "durs.json"), "w")); json.dump(files, open(os.path.join(out, "files.json"), "w"))
print("total speech", round(sum(info), 1), "lines", len(info))
