import json, sys, os, importlib, numpy as np, soundfile as sf
import iou_engine as E

SR = 24000


def tone(f, d, a=0.3, dec=3.0):
    t = np.arange(int(d * SR)) / SR
    env = np.exp(-t * dec) * np.minimum(1, t * 200)
    return a * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))


def chime():
    a = tone(523.25, 1.4, 0.18, 3)
    b = tone(783.99, 1.8, 0.18, 2.5)
    out = np.zeros(int(2.2 * SR))
    out[:len(a)] += a
    o = int(0.22 * SR)
    out[o:o + len(b)] += b
    return out


def tick(seed=1):
    n = int(0.03 * SR)
    return np.random.RandomState(seed).randn(n) * np.exp(-np.arange(n) / (0.004 * SR)) * 0.10


def thump(a=0.55):
    t = np.arange(int(0.45 * SR)) / SR
    return a * np.sin(2 * np.pi * (70 - 35 * t) * t) * np.exp(-t * 11)


def whoosh(d=1.0, a=0.10):
    n = int(d * SR)
    x = np.random.RandomState(3).randn(n)
    x = np.convolve(x, np.ones(40) / 40, mode="same")
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return x * env * a


def rustle(seed=0):
    n = int(0.22 * SR)
    r = np.random.RandomState(seed)
    x = r.randn(n)
    x = np.convolve(x, np.ones(6) / 6, mode="same")
    env = np.minimum(1, np.arange(n) / (0.01 * SR)) * np.exp(-np.arange(n) / (0.07 * SR))
    return x * env * 0.12


def clink(seed=0):
    r = np.random.RandomState(seed)
    f = r.choice([2093.0, 2637.0, 3136.0])
    a = tone(f, 0.5, 0.10, 9)
    b = tone(f * 1.5, 0.4, 0.04, 12)
    a[:len(b)] += b
    return a


def pad(total):
    n = int(total * SR)
    t = np.arange(n) / SR
    chords = [(98.0, 146.83, 196.0, 246.94), (87.31, 130.81, 174.61, 220.0), (110.0, 164.81, 220.0, 277.18), (98.0, 146.83, 196.0, 233.08)]
    out = np.zeros(n)
    seg = 8.0
    for k, ch in enumerate(chords * int(total / seg / 4 + 2)):
        a = int(k * seg * SR)
        if a >= n:
            break
        b = min(n, int((k + 1) * seg * SR) + int(2 * SR))
        tt = t[a:b] - k * seg
        env = np.minimum(1, tt / 2.0) * np.minimum(1, np.maximum(0, (seg + 2 - tt) / 2.0))
        for fr in ch:
            out[a:b] += env * (np.sin(2 * np.pi * fr * tt) + 0.2 * np.sin(2 * np.pi * 2 * fr * tt + 0.3)) * 0.011
    return out * (0.85 + 0.15 * np.sin(2 * np.pi * t / 13))


def ts(x):
    h = int(x // 3600)
    m = int(x % 3600 // 60)
    s = x % 60
    return ("%02d:%02d:%06.3f" % (h, m, s)).replace(".", ",")


def chunk(s, mx=84):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > mx and cur:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


def main(mod, vodir, outwav, srt):
    C = importlib.import_module(mod)
    durs = json.load(open(os.path.join(vodir, "durs.json")))
    files = json.load(open(os.path.join(vodir, "files.json")))
    tl, total = E.build_timeline(C.L, durs)
    n = int((total + 0.5) * SR)
    voice = np.zeros(n)
    fx = np.zeros(n)

    def put(buf, x, at, g=1.0):
        a = int(at * SR)
        if a < 0 or a >= n:
            return
        b = min(n, a + len(x))
        buf[a:b] += x[:b - a] * g

    subs = []
    rng = np.random.RandomState(11)
    put(fx, thump(0.6), 0.0)
    for k in range(10):
        put(fx, tick(k), 0.05 + k * 0.045)
    for i, ln in enumerate(C.L):
        t0, d = tl[i]
        sc = ln["scene"]
        st = ln["p"]["step"]
        a, sr = sf.read(os.path.join(vodir, files[i]))
        put(voice, a, t0)
        subs.append((t0, t0 + durs[i], ln["cap"]))
        new = i == 0 or C.L[i - 1]["scene"] != sc
        if "ch" in ln["p"] and ln["p"]["ch"] > 0:
            put(fx, whoosh(0.9, 0.12), t0)
            put(fx, chime(), t0 + 0.1, 0.9)
        elif new and i > 0:
            put(fx, rustle(i), t0 + 0.03)
        if sc == "hook":
            put(fx, thump(0.7), 1.1)
        if sc == "wall":
            for j in range(18):
                put(fx, rustle(j), t0 + 0.3 + j * 0.09, 0.7)
        if sc == "tsy":
            for j in range(5):
                put(fx, clink(j), t0 + d * (0.2 + j * 0.03))
            put(fx, rustle(5), t0 + d * 0.3)
            put(fx, clink(9), t0 + d * 0.85)
        if sc == "frames" and st == 0:
            for j, fr in enumerate((0.45, 0.55, 0.64, 0.80)):
                put(fx, tick(j + 3), t0 + d * fr)
        if sc in ("trust", "fed", "foreign", "other") and st == 0:
            put(fx, thump(0.4), t0 + 0.05)
            for j in range(10):
                put(fx, rustle(j + 30), t0 + 0.2 + j * 0.13, 0.5)
        if sc == "trust" and st == 5:
            put(fx, thump(0.6), t0 + 2.3)
        if sc == "trust" and st == 4:
            put(fx, clink(1), t0 + d * 0.5)
            put(fx, clink(2), t0 + d * 0.78)
        if sc == "pay" and st == 3:
            put(fx, thump(0.5), t0 + d * 0.5)
        if sc == "pay" and st == 5:
            for j in range(18):
                put(fx, clink(j), t0 + 0.4 + j * 0.42 + rng.rand() * 0.15, 0.7)
        if sc == "pie" and st == 0:
            for j in range(4):
                put(fx, thump(0.3), t0 + d * (0.16 + j * 0.17))
        if sc == "plain":
            put(fx, thump(0.5), t0 + 0.1)
        if sc == "end":
            put(fx, chime(), t0 + 0.2)
    bed = pad(total + 0.5)[:n]
    mix = voice + fx * 0.9 + bed
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    sf.write(outwav, mix.astype(np.float32), SR)
    with open(srt, "w") as f:
        k = 1
        for a, b, s in subs:
            parts = chunk(s)
            dd = (b - a) / sum(len(p) for p in parts)
            x = a
            for p in parts:
                y = x + dd * len(p)
                f.write("%d\n%s --> %s\n%s\n\n" % (k, ts(x), ts(y), p))
                k += 1
                x = y
    print("total", round(total, 1))
    json.dump([(round(a, 2), ln["p"].get("ch")) for (a, _), ln in zip(tl, C.L) if "ch" in ln["p"]], open("chapters.json", "w"))


if __name__ == "__main__":
    main(*sys.argv[1:5])
