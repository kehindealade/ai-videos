import json, os, random, warnings
import numpy as np, soundfile as sf
warnings.filterwarnings("ignore")
OUT = "vo"
os.makedirs(OUT, exist_ok=True)
rnd = random.SystemRandom()
USED_BLENDS = [{"af_bella", "bf_emma"}]
REF_TXT = "Okay, so I finally sat down this evening. The kettle was on, the window was getting dark, and I thought about everyone I keep meaning to call."
LINES = [("son", "Hi, Grandma... Sorry I'm late."), ("gran", "[laugh] [chuckle]")]
k = None
meta = {}
for who, prefix in (("son", ("am", "bm")), ("gran", ("af", "bf"))):
    refp = os.path.join(OUT, "ref_%s.wav" % who)
    if os.path.exists(refp):
        continue
    if k is None:
        from kokoro_onnx import Kokoro
        k = Kokoro("/root/kokoro/kokoro-v1.0.onnx", "/root/kokoro/voices-v1.0.bin")
    poor = {"af_nicole", "am_adam", "am_santa"}
    pool = sorted(v for v in k.get_voices() if v not in poor and v[:2] in prefix)
    while True:
        a, b = rnd.sample(pool, 2)
        if {a, b} not in USED_BLENDS:
            break
    w = round(rnd.uniform(0.3, 0.7), 2)
    style = w * k.get_voice_style(a) + (1 - w) * k.get_voice_style(b)
    spd = round(rnd.uniform(0.90, 0.97), 2)
    audio, sr = k.create(REF_TXT, voice=style, speed=spd, lang="en-us")
    audio = audio[: int(10.5 * sr)]
    sf.write(refp, audio, sr)
    meta[who] = {"blend": [a, b], "weight_a": w, "ref_speed": spd}
    print("ref", who, a, b, w, spd, flush=True)
if meta:
    old = json.load(open(os.path.join(OUT, "voice.json"))) if os.path.exists(os.path.join(OUT, "voice.json")) else {}
    old.update(meta)
    json.dump(old, open(os.path.join(OUT, "voice.json"), "w"))
m = None
for i, (who, txt) in enumerate(LINES):
    p = os.path.join(OUT, "%s.wav" % who)
    if os.path.exists(p):
        continue
    if m is None:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        m = ChatterboxTurboTTS.from_pretrained(device="cpu")
    wv = m.generate(txt, audio_prompt_path=os.path.join(OUT, "ref_%s.wav" % who)).squeeze(0).numpy().astype("float32")
    nz = np.where(np.abs(wv) > 0.01)[0]
    if len(nz):
        wv = wv[max(0, nz[0] - 600): nz[-1] + 2400]
    sf.write(p, wv, m.sr)
    print("line", who, round(len(wv) / m.sr, 2), m.sr, flush=True)
