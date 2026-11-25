import json, os, random, sys, hashlib, warnings
import numpy as np, soundfile as sf
warnings.filterwarnings("ignore")
import ram
OUT = ram.VODIR
os.makedirs(OUT, exist_ok=True)
rnd = random.SystemRandom()
refp = os.path.join(OUT, "ref.wav")
meta = os.path.join(OUT, "voice.json")
if not os.path.exists(refp):
    from kokoro_onnx import Kokoro
    k = Kokoro("/root/kokoro/kokoro-v1.0.onnx", "/root/kokoro/voices-v1.0.bin")
    poor = {"af_nicole", "am_adam", "am_santa"}
    pool = sorted(v for v in k.get_voices() if v not in poor and v[:2] in ("af", "am", "bf", "bm"))
    while True:
        a, b = rnd.sample(pool, 2)
        if {a, b} != {"af_bella", "bf_emma"}:
            break
    w = round(rnd.uniform(0.3, 0.7), 2)
    style = w * k.get_voice_style(a) + (1 - w) * k.get_voice_style(b)
    spd = round(rnd.uniform(0.92, 1.0), 2)
    txt = " ".join(l[1] for l in ram.LINES[1:4])
    audio, sr = k.create(txt, voice=style, speed=spd, lang="en-us")
    audio = audio[: int(11 * sr)]
    sf.write(refp, audio, sr)
    json.dump({"blend": [a, b], "weight_a": w, "ref_speed": spd}, open(meta, "w"))
    print("ref", a, b, w, spd, round(len(audio) / sr, 1), flush=True)
m = None
durs, files = [], []
for i, L in enumerate(ram.LINES):
    p = os.path.join(OUT, "%02d.wav" % i)
    if not os.path.exists(p):
        if m is None:
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            m = ChatterboxTurboTTS.from_pretrained(device="cpu")
        wv = m.generate(L[1], audio_prompt_path=refp).squeeze(0).numpy().astype("float32")
        nz = np.where(np.abs(wv) > 0.01)[0]
        wv = wv[max(0, nz[0] - 600): nz[-1] + 2400]
        if m.sr != 24000:
            import librosa
            wv = librosa.resample(wv, orig_sr=m.sr, target_sr=24000)
        sf.write(p, wv, 24000)
        print("line", i, round(len(wv) / 24000, 2), flush=True)
    durs.append(sf.info(p).duration)
json.dump(durs, open(os.path.join(OUT, "durs.json"), "w"))
print("total speech", round(sum(durs), 1), flush=True)
