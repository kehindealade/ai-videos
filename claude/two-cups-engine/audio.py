import numpy as np, wave, sys
from timeline import *

SR = 44100
rng = np.random.default_rng(87)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def pluck(m, d=2.6, bright=0.5, decay=0.9965):
    f = hz(m)
    N = int(SR / f)
    frac = SR / f / N
    n = int(d * SR)
    nb = n // N + 2
    buf = rng.uniform(-1, 1, N)
    buf = lowpass(np.concatenate([buf, buf[:8]]), 3)[:N]
    buf = buf - buf.mean()
    out = np.empty(nb * N)
    cur = buf
    for b in range(nb):
        out[b * N:(b + 1) * N] = cur
        nxt = bright * cur + (1 - bright) * np.roll(cur, 1)
        cur = nxt * decay
    tt = np.arange(n) / frac
    y = np.interp(tt, np.arange(len(out)), out)
    y = y[:n]
    env = np.minimum(1, np.arange(n) / (0.002 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.25 * SR))
    body = np.sin(2 * np.pi * f * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 3.0) * 0.12
    return (y * 1.0 + body) * env


def clink():
    d = 1.1
    n = int(d * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f, dec, g in ((3140, 9, 1.0), (4720, 13, 0.7), (6830, 20, 0.5), (8610, 30, 0.35), (2190, 6, 0.5), (1230, 9, 0.3)):
        s += g * np.sin(2 * np.pi * f * t + rng.uniform(0, 1)) * np.exp(-t * dec)
    tick = rng.standard_normal(n)
    tick = tick - lowpass(tick, 8)
    s += 0.5 * tick * np.exp(-t * 400)
    s *= np.minimum(1, t / 0.0005)
    return s


def rain(n):
    out = np.zeros((2, n))
    for ch in range(2):
        w = rng.standard_normal(n)
        a = lowpass(w, 14)
        b = lowpass(w, 90)
        x = (a - b) * 1.0 + 0.5 * b
        mod = 1 + 0.15 * np.sin(2 * np.pi * 0.13 * np.arange(n) / SR + ch)
        out[ch] = x * mod
        k = int(n / SR * 28)
        for _ in range(k):
            i = rng.integers(0, n - 800)
            tt = np.arange(700) / SR
            f = rng.uniform(1800, 4200)
            out[ch, i:i + 700] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 400) * rng.uniform(0.2, 0.9) * 0.35
    return out / np.abs(out).max()




def hiss(d):
    n = int(d * SR)
    w = rng.standard_normal(n)
    h = w - lowpass(w, 5)
    rum = lowpass(rng.standard_normal(n), 200) * 6
    env = np.minimum(1, np.arange(n) / (1.2 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.4 * SR))
    return (h * 0.6 + rum) * env


def pour(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    w = rng.standard_normal(n)
    b = lowpass(w, 6) - lowpass(w, 40)
    gur = 0.6 + 0.4 * np.sin(2 * np.pi * (7 + 3 * np.sin(2 * np.pi * 1.3 * t)) * t)
    s = b * gur * 3
    for _ in range(int(d * 14)):
        i = rng.integers(0, max(1, n - 3000))
        tt = np.arange(2500) / SR
        f = rng.uniform(500, 1400)
        s[i:i + 2500] += np.sin(2 * np.pi * f * tt * (1 + 2 * tt)) * np.exp(-tt * 60) * 0.25
    env = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.25)
    return s * env


def knock():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 110 * t) * np.exp(-t * 28) + 0.6 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 40)
    w = rng.standard_normal(n)
    s += lowpass(w, 20) * np.exp(-t * 90) * 3
    return s * np.minimum(1, t / 0.001)


def tick(f=2600):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 160)
    w = rng.standard_normal(n)
    s += (w - lowpass(w, 4)) * np.exp(-t * 700) * 0.8
    return s


def thud():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 75 * t) * np.exp(-t * 18) + lowpass(rng.standard_normal(n), 30) * np.exp(-t * 60) * 2


def warm_low(m, d=7.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = sum(g * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (0.5 + 0.6 * k)) for k, g in ((1, 1.0), (2, 0.45), (3, 0.2), (4, 0.08)))
    return s * np.minimum(1, t / 0.01)


A = [65, 62, 58, 63, 65, 67, 65, 62]
B = [58, 60, 62, 65, 63, 62, 58]
END = [65, 63, 62, 60, 58]
CH = {"Bb": [46, 53, 58, 62], "Eb": [51, 55, 58, 63], "Gm": [43, 55, 58, 62], "F": [41, 53, 57, 60]}


def ab(name, t):
    return START[name] + t


def build():
    total = TOTAL
    n = int(total * SR)
    pad = 6 * SR
    L = np.zeros((2, n + pad))

    def addm(sig, t0, g, pan=0.0):
        i = int(t0 * SR)
        if i >= n + pad or i < 0:
            return
        m = min(len(sig), n + pad - i)
        L[0, i:i + m] += sig[:m] * g * (1 - pan) * 0.5
        L[1, i:i + m] += sig[:m] * g * (1 + pan) * 0.5

    def line(notes, t0, step, g=0.42, d=2.6, bright=0.5, pan=0.15):
        for k, m in enumerate(notes):
            addm(pluck(m, d, bright), t0 + k * step, g, pan)

    def strum(ch, t0, g=0.15, d=3.0):
        for k, m in enumerate(CH[ch]):
            addm(pluck(m, d, 0.5), t0 + k * 0.045, g, -0.25 + 0.15 * k)

    def bass(m, t0, g=0.32, d=3.0):
        addm(pluck(m, d, 0.62, 0.998), t0, g, -0.1)

    rn = rain(n + pad)
    tt = np.arange(n + pad) / SR
    pts = [(0, 0.06), (29.5, 0.06), (30.5, 0.075), (44.5, 0.075), (45.5, 0.06), (79, 0.06), (81, 0.1), (99, 0.1),
           (101, 0.065), (114, 0.065), (116, 0.035), (133.5, 0.035), (135.3, 0.0), (190, 0.0)]
    rg = np.interp(tt, [p[0] for p in pts], [p[1] for p in pts])
    L[0] += rn[0] * rg
    L[1] += rn[1] * rg
    ck = clink()
    addm(ck, 0.0, 0.55, 0.0)
    addm(ck[: int(0.5 * SR)] * 0.5, 0.075, 0.25, 0.1)

    for k, m in enumerate(A):
        addm(pluck(m, 2.6, 0.5), (2 + 1.5 * k) * BEAT, 0.42, 0.15)
    for b, m in ((4, 46), (8, 51), (12, 46)):
        bass(m, b * BEAT, 0.34)
    strum("Bb", 9.5 * BEAT, 0.16)

    line(B, ab("day1", 2.3), 3 * BEAT, 0.36)
    line([65, 62], ab("day1", 2.3 + 21 * BEAT), 3 * BEAT, 0.3)
    addm(hiss(4.2), ab("day1", 0.0), 0.05, 0.2)
    for a, _ in D1_TAKE:
        addm(ck * 0.5, ab("day1", D1[1] + a + 0.15), 0.25, 0.2)
    for a, b in D1_POUR:
        addm(pour(b - a), ab("day1", D1[3] + a), 0.11, 0.0)

    line(A, ab("days", 0.5), 2 * BEAT, 0.3, bright=0.45)
    line([58], ab("days", 12.2), 1, 0.28)
    bass(46, ab("days", 0.5), 0.2)
    bass(51, ab("days", 6.0), 0.2)
    for i in range(6):
        addm(ck * 0.6, ab("days", i * DAYS_STEP + DAYS_DRINK[3]), 0.3, 0.35)

    line(B, ab("day8", 0.5), 2 * BEAT, 0.32)
    bass(46, ab("day8", 0.5), 0.2)
    line(A[:4], ab("day8", D8_B + 2.0), 3 * BEAT, 0.3, bright=0.45)
    addm(pour(D8_POUR[1] - D8_POUR[0]), ab("day8", D8_B + D8_POUR[0]), 0.09, -0.1)

    for k in D14_KNOCK:
        addm(knock(), ab("day14", k), 0.6, 0.45)
    addm(lowpass(rng.standard_normal(int(0.9 * SR)), 60) * np.hanning(int(0.9 * SR)) * 3, ab("day14", D14[1] + D14_DOOR[0]), 0.25, 0.4)
    addm(thud(), ab("day14", D14[1] + D14_SET[1]), 0.35, 0.3)
    line([62, 58, 63, 62], ab("day14", 3.5), 2.5, 0.3)
    addm(pour(D14_POUR[1] - D14_POUR[0]), ab("day14", D14[2] + D14_POUR[0]), 0.08, 0.0)
    t0 = ab("day14", D14[3] - 0.4)
    line(A[:6], t0, 1.25 * BEAT, 0.36)
    line([m - 4 if m in (62, 67) else m - 3 for m in A[:6]], t0 + 0.02, 1.25 * BEAT, 0.22, 3.2, 0.32, -0.3)
    bass(46, t0, 0.24)
    bass(51, t0 + 2.76, 0.22)

    for k in range(20):
        addm(tick(2600 if k % 2 == 0 else 2100), ab("day30", k + 0.0), 0.1, 0.25)

    line([65, 62, 58], ab("day40", 2.0), 3.0, 0.28, 3.2, 0.42)
    addm(ck, ab("day40", D40_SET), 0.4, 0.1)
    addm(ck[: int(0.5 * SR)], ab("day40", D40_SET + 0.06), 0.18, -0.1)
    addm(pour(D40_POUR[1] - D40_POUR[0]), ab("day40", D40_B + D40_POUR[0]), 0.09, -0.1)
    addm(pluck(70, 1.6, 0.5), ab("day40", D40_B + D40_POP), 0.26, 0.3)
    addm(pluck(74, 1.6, 0.5), ab("day40", D40_B + D40_POP + 0.18), 0.24, 0.3)
    line([63, 65], ab("day40", D40_B + D40_POP + 1.2), 1.5 * BEAT, 0.3)

    line(A, ab("day60", 0.5), 1.5 * BEAT, 0.36)
    line(B, ab("day60", 10.0), 1.5 * BEAT, 0.34)
    bass(46, ab("day60", 0.5), 0.22)
    bass(51, ab("day60", 4.6), 0.22)
    strum("Bb", ab("day60", 10.0), 0.11)
    strum("Gm", ab("day60", 14.0), 0.11)

    addm(hiss(4.2), ab("day90", 0.0), 0.05, 0.2)
    for a, _ in D90_TAKE:
        addm(ck * 0.5, ab("day90", D90[1] + a + 0.15), 0.25, 0.2)
    addm(ck, ab("day90", D90[1] + D90_BACK[1]), 0.4, 0.15)
    addm(pour(D90_POUR[1] - D90_POUR[0]), ab("day90", D90[2] + D90_POUR[0]), 0.11, 0.0)
    g0 = ab("day90", 0.5)
    seqm = A + B + A[:6]
    for k, m in enumerate(seqm):
        addm(pluck(m, 2.6, 0.52), g0 + k * 1.5 * BEAT, 0.42, 0.15)
    prog = ["Bb", "Eb", "Gm", "F", "Bb", "Eb", "Bb", "F", "Bb", "Eb"]
    for k, ch in enumerate(prog):
        tb = g0 + k * 4 * BEAT
        if tb > ab("day90", 29.0):
            break
        strum(ch, tb, 0.15)
        bass(CH[ch][0], tb, 0.3)
        strum(ch, tb + 2 * BEAT, 0.08, 2.0)
    line(A[:4], ab("day90", D90[4] + 2.6), 1.5 * BEAT, 0.34)
    addm(warm_low(34, 8.0), ab("day90", D90[4]), 0.5, 0.0)
    addm(warm_low(46, 6.0), ab("day90", D90[4] + 0.02), 0.25, 0.0)

    line(END, ab("close", 0.6), 2 * BEAT, 0.4, 3.0)
    strum("Bb", ab("close", 7.6), 0.2, 6.0)
    bass(46, ab("close", 7.6), 0.3, 6.0)
    addm(pluck(70, 5.0, 0.5), ab("close", 8.4), 0.2, 0.2)

    y = L[:, :n]
    fo = int(1.2 * SR)
    y[:, -fo:] *= np.linspace(1, 0, fo) ** 2
    y = np.tanh(y * 3.0)
    y = y / np.abs(y).max() * 10 ** (-4.0 / 20)
    return y


def write(path, y):
    pcm = (y.T * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    write(sys.argv[1], build())
