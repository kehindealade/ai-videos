import json, sys, os, importlib, numpy as np, soundfile as sf
import engine as E

SR = 24000


def tone(f, d, a=0.3, dec=3.0):
    t = np.arange(int(d * SR)) / SR
    env = np.exp(-t * dec) * np.minimum(1, t * 200)
    return a * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))


def chime():
    a = tone(659.25, 1.2, 0.22, 3)
    b = tone(523.25, 1.6, 0.22, 2.5)
    out = np.zeros(int(2.0 * SR))
    out[:len(a)] += a
    o = int(0.32 * SR)
    out[o:o + len(b)] += b
    return out


def tick():
    n = int(0.03 * SR)
    return np.random.RandomState(1).randn(n) * np.exp(-np.arange(n) / (0.004 * SR)) * 0.08


def thump():
    t = np.arange(int(0.35 * SR)) / SR
    return 0.5 * np.sin(2 * np.pi * (70 - 40 * t) * t) * np.exp(-t * 12)


def whoosh(d=1.2):
    n = int(d * SR)
    x = np.random.RandomState(3).randn(n)
    x = np.convolve(x, np.ones(40) / 40, mode="same")
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return x * env * 0.12


def pad(total):
    n = int(total * SR)
    t = np.arange(n) / SR
    chords = [(110.0, 164.81, 220.0, 261.63), (98.0, 146.83, 196.0, 246.94), (87.31, 130.81, 174.61, 220.0), (98.0, 146.83, 196.0, 233.08)]
    out = np.zeros(n)
    seg = 8.0
    for k, ch in enumerate(chords * int(total / seg / 4 + 2)):
        a = int(k * seg * SR)
        if a >= n:
            break
        b = min(n, int((k + 1) * seg * SR) + int(2 * SR))
        tt = t[a:b] - k * seg
        env = np.minimum(1, tt / 2.0) * np.minimum(1, np.maximum(0, (seg + 2 - tt) / 2.0))
        for f in ch:
            out[a:b] += env * (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt + 0.3)) * 0.012
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * t / 11)
    return out * lfo


def main(mod, vodir, outwav, srt):
    C = importlib.import_module(mod)
    durs = json.load(open(os.path.join(vodir, "durs.json")))
    tl, total = E.build_timeline(C.L, durs)
    n = int((total + 0.5) * SR)
    voice = np.zeros(n)
    fx = np.zeros(n)

    def put(buf, x, at):
        a = int(at * SR)
        b = min(n, a + len(x))
        buf[a:b] += x[:b - a]

    subs = []
    for i, ln in enumerate(C.L):
        t0, d = tl[i]
        sc = ln["scene"]
        st = ln["p"].get("step")
        if ln["text"]:
            a, sr = sf.read(os.path.join(vodir, json.load(open(os.path.join(vodir, "files.json")))[i]))
            put(voice, a, t0)
            subs.append((t0, t0 + durs[i], ln["text"]))
        if sc == "sign":
            put(fx, chime(), t0 + 0.1)
            put(fx, whoosh(0.8), t0)
        elif sc in ("hook", "board", "bignum") and (i == 0 or C.L[i - 1]["scene"] != sc or st is not None):
            for k in range(8):
                put(fx, tick(), t0 + k * 0.05)
        elif sc == "map":
            put(fx, whoosh(1.6), t0 + 0.2)
        if (sc == "lev" and st == 7) or (sc == "hook" and st == 1) or (sc == "drop" and st == 1) or sc == "end":
            put(fx, thump(), t0 + (0.3 if sc == "lev" else 1.5 if sc == "drop" else 0.05))
    bed = pad(total + 0.5)[:n]
    mix = voice + fx * 0.9 + bed
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    sf.write(outwav, mix.astype(np.float32), SR)
    with open(srt, "w") as f:
        k = 1
        for a, b, s in subs:
            parts = chunk(s)
            d = (b - a) / sum(len(p) for p in parts)
            x = a
            for p in parts:
                y = x + d * len(p)
                f.write("%d\n%s --> %s\n%s\n\n" % (k, ts(x), ts(y), p))
                k += 1
                x = y
    print("total", round(total, 1))


def chunk(s, mx=84):
    words = s.split()
    out, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > mx and cur:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


def ts(x):
    h = int(x // 3600)
    m = int(x % 3600 // 60)
    s = x % 60
    return ("%02d:%02d:%06.3f" % (h, m, s)).replace(".", ",")


if __name__ == "__main__":
    main(*sys.argv[1:5])
