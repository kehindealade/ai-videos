import json, sys, os, importlib, numpy as np, soundfile as sf
import cc_engine as E

SR = 24000


def tone(f, d, a=0.3, dec=3.0):
    t = np.arange(int(d * SR)) / SR
    env = np.exp(-t * dec) * np.minimum(1, t * 300)
    return a * env * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t))


def key(seed):
    r = np.random.RandomState(seed)
    n = int(0.025 * SR)
    x = r.randn(n) * np.exp(-np.arange(n) / (0.003 * SR))
    x = np.convolve(x, np.ones(3) / 3, mode="same")
    return x * 0.05


def pop(seed=0):
    r = np.random.RandomState(seed)
    f = r.choice([880.0, 988.0, 1175.0])
    return tone(f, 0.18, 0.07, 22)


def chime():
    out = np.zeros(int(1.8 * SR))
    for k, f in enumerate((659.25, 880.0, 1318.5)):
        a = tone(f, 1.2, 0.09, 3.5)
        o = int(k * 0.09 * SR)
        out[o:o + len(a)] += a
    return out


def thump(a=0.5):
    t = np.arange(int(0.4 * SR)) / SR
    return a * np.sin(2 * np.pi * (80 - 40 * t) * t) * np.exp(-t * 12)


def whoosh(d=0.7, a=0.08, seed=3):
    n = int(d * SR)
    x = np.random.RandomState(seed).randn(n)
    x = np.convolve(x, np.ones(30) / 30, mode="same")
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return x * env * a


def bed(total):
    n = int(total * SR)
    out = np.zeros(n)
    bpm = 84.0
    beat = 60.0 / bpm
    prog = [(146.83, 185.0, 220.0, 277.18), (123.47, 146.83, 185.0, 246.94), (98.0, 146.83, 196.0, 246.94), (110.0, 138.59, 164.81, 220.0)]
    t = 0.0
    k = 0
    while t < total:
        ch = prog[(k // 8) % 4]
        f = ch[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] * 2
        p = tone(f, beat * 1.6, 0.012, 4.5)
        a = int(t * SR)
        b = min(n, a + len(p))
        out[a:b] += p[:b - a]
        if k % 8 == 0:
            q = tone(ch[0] / 2, beat * 7, 0.010, 0.6)
            b = min(n, a + len(q))
            out[a:b] += q[:b - a]
        t += beat / 2
        k += 1
    room = np.random.RandomState(9).randn(n)
    room = np.convolve(room, np.ones(60) / 60, mode="same") * 0.004
    return out + room


STAMPS = {("split", 6): 0.4, ("other", 0): 0.5, ("pts", 2): 0.5}


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
    put(fx, thump(0.5), 0.0)
    put(fx, pop(1), 0.15)
    put(fx, pop(2), 0.5)
    put(fx, thump(0.45), 1.05)
    for i, ln in enumerate(C.L):
        t0, d = tl[i]
        sc, st = ln["scene"], ln["p"]["step"]
        a, sr = sf.read(os.path.join(vodir, files[i]))
        put(voice, a, t0 + 0.12)
        subs.append((t0 + 0.12, t0 + 0.12 + durs[i], ln["cap"]))
        for j in range(3):
            put(fx, key(i * 13 + j), t0 + 0.05 + j * 0.05)
        if i > 0:
            put(fx, whoosh(0.5, 0.05, i), t0 - 0.1)
            put(fx, pop(i), t0 + 0.2)
        if "ch" in ln["p"]:
            put(fx, chime(), t0 + 0.05)
        if (sc, st) in STAMPS:
            put(fx, thump(0.5), t0 + d * STAMPS[(sc, st)] + 0.05)
        if sc == "end":
            put(fx, chime(), t0 + 0.3)
    mix = voice + fx * 0.9 + bed(total + 0.5)[:n]
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
