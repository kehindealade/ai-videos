import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
from wave_reel import (DUR, ARM_UP, HEY0, ARC0, ARC_GROW, BEND, ARC_DONE, STOP, HI5, REC, WALK, NODS, GLANCE,
                       NOBODY, EVERY, END, CROSS0, P2_FAR)

SR = 44100
N = int(SR * DUR)
rng = np.random.default_rng(11)
BPM = 17 * 4 * 60 / DUR
BEAT = 60 / BPM
BAR = BEAT * 4
T = np.arange(N) / SR


def nf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, sig, t, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[:j - i] * g


def hp(x, f):
    b, a = butter(2, f / (SR / 2), "high")
    return lfilter(b, a, x)


def lp(x, f):
    b, a = butter(2, f / (SR / 2), "low")
    return lfilter(b, a, x)


def pizz(m, vel=1.0, d=0.22):
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    f = nf(m)
    s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1 / d) * (1 + 0.6 * k)) / k for k in range(1, 7))
    s += hp(rng.standard_normal(n), 2000) * np.exp(-t / 0.004) * 0.3
    return s * np.minimum(1, t / 0.002) * vel * 0.16


def glock(m, vel=1.0, d=0.9):
    n = int(SR * 2.0)
    t = np.arange(n) / SR
    f = nf(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / d) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25) \
        + 0.2 * np.sin(2 * np.pi * f * 5.40 * t) * np.exp(-t / 0.08)
    return s * np.minimum(1, t / 0.001) * vel * 0.11


def shaker(vel=1.0):
    n = int(SR * 0.08)
    t = np.arange(n) / SR
    a = np.minimum(1, t / 0.015) * np.exp(-t / 0.025)
    return hp(rng.standard_normal(n), 5000) * a * 0.07 * vel


def held(m, dur, vel=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = nf(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return s * np.minimum(1, t / 0.05) * np.exp(-t / (dur * 0.5)) * vel * 0.12


def sweep(f0, f1, dur, vol=0.4, noise=0.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    if noise:
        s += lp(rng.standard_normal(n), 3000) * noise
    return s * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.08) * vol


def whoosh(dur=0.45, vol=0.25, up=True):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        k = i / n if up else 1 - i / n
        out[i:i + seg] = lp(x[i:i + seg], 600 + 4000 * k)
    return out * np.sin(np.pi * t / dur) * vol


def tick(vol=0.5):
    n = int(SR * 0.05)
    t = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 1500) * np.exp(-t / 0.006) * 0.5 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01) * 0.4) * vol


def tap(vol=0.3):
    n = int(SR * 0.06)
    t = np.arange(n) / SR
    return lp(rng.standard_normal(n), 1800) * np.exp(-t / 0.012) * vol


def step(vol=0.25):
    n = int(SR * 0.12)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (70 + 60 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.04) + lp(rng.standard_normal(n), 2500) * np.exp(-t / 0.015) * 0.5
    return s * vol


def chirp(vol=0.12):
    out = np.zeros(int(SR * 0.4))
    for k in range(3):
        s = sweep(2600, 3600, 0.07, vol)
        out[int(k * 0.1 * SR):int(k * 0.1 * SR) + len(s)] += s
    return out


def womp(m, dur, vol=0.35):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = nf(m) * (1 - 0.06 * (t / dur) ** 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k for k in range(1, 9))
    s = lp(s, 1400)
    s *= (1 + 0.3 * np.sin(2 * np.pi * 6 * t))
    return s * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06) * vol


CH = [(50, [62, 66, 69]), (47, [59, 62, 66]), (43, [59, 62, 67]), (45, [61, 64, 69])]
MEL = [(0, 78), (1, 81), (2, 86), (3, 81), (4, 83), (5, 81), (6, 78), (7, 76), (8, 79), (9, 83), (10, 86), (11, 83), (12, 81)]


def band(t0, t1, vel_p=1.0, glk=True, shk=True, bass_only=False):
    m = np.zeros(N)
    b0 = int(t0 / BAR)
    for bar in range(b0, int(t1 / BAR) + 1):
        root, notes = CH[bar % 4]
        tb = bar * BAR
        for beat in range(4):
            tt = tb + beat * BEAT
            if not (t0 <= tt < t1):
                continue
            if beat in (0, 2):
                place(m, pizz(root + (7 if beat == 2 else 0), 1.1 * vel_p), tt)
            elif not bass_only:
                for k, nt in enumerate(notes):
                    place(m, pizz(nt, 0.6 * vel_p), tt + k * 0.006)
                place(m, pizz(notes[1] + 12, 0.35 * vel_p), tt + BEAT / 2)
            if shk:
                place(m, shaker(1.0), tt)
                place(m, shaker(0.6), tt + BEAT * 0.55)
        if glk:
            for bi, nt in MEL[(bar % 2) * 8:(bar % 2) * 8 + 8] if bar % 2 == 0 else MEL[8:]:
                tt = tb + (bi % 8) * BEAT / 2
                if t0 <= tt < t1:
                    place(m, glock(nt, 0.9), tt)
    return m


def music():
    out = band(0.0, STOP)
    stop_env = np.clip((STOP + 0.05 - T) / 0.05, 0, 1)
    out *= np.where(T < STOP, 1, stop_env)
    place(out, sweep(500, 45, 0.5, 0.35, noise=0.15), STOP - 0.05)
    place(out, held(81, 1.8, 1.0), STOP + 0.15)
    for i, t0 in enumerate(REC):
        v = (1.0, 0.6, 0.32)[i]
        root, notes = CH[(0, 2, 3)[i]]
        place(out, pizz(root, 1.2 * v), t0)
        for k, nt in enumerate(notes):
            place(out, pizz(nt, 0.9 * v), t0 + k * 0.01)
        place(out, glock((86, 83, 79)[i], 0.9 * v), t0 + 0.02)
    out += band(REC[0] + BEAT, WALK, vel_p=0.35, glk=False, shk=False, bass_only=True)
    out += band(WALK, EVERY - 0.1, vel_p=0.6, glk=False, shk=True)
    place(out, glock(86, 1.0), NOBODY)
    place(out, glock(90, 1.0), NOBODY + 0.22)
    for k, (m, d) in enumerate(((67, 0.32), (66, 0.32), (65, 0.32), (64, 1.1))):
        place(out, womp(m - 12, d), EVERY + 0.15 + k * 0.34)
    for k, nt in enumerate((74, 78, 81, 86)):
        place(out, glock(nt, 1.0, 1.4), END + 0.1 + k * 0.09)
    place(out, pizz(38, 1.3), END + 0.1)
    place(out, held(62, 2.6, 0.6), END + 0.1)
    out *= np.clip((DUR - T) / 0.3, 0, 1)
    return out


def sfx():
    s = np.zeros(N)
    amb = lp(rng.standard_normal(N), 500) * 0.025 * np.clip((END - T) / 0.3, 0, 1)
    amb *= np.where((T > STOP) & (T < REC[0]), 1.6, 1.0)
    s += amb
    place(s, tap(0.3), 0.0)
    place(s, whoosh(0.35, 0.3), ARM_UP - 0.05)
    place(s, sweep(300, 900, 0.18, 0.18), HEY0)
    k = 0
    tt = ARC0
    while tt < ARC_GROW:
        place(s, glock(98 + (k % 3) * 2, 0.18, 0.2), tt)
        tt += 0.45
        k += 1
    place(s, whoosh(0.5, 0.3, up=False), BEND)
    place(s, glock(93, 0.5, 0.6), ARC_DONE)
    place(s, tick(0.45), 13.6)
    place(s, tap(0.5), HI5)
    place(s, tap(0.3), HI5 + 0.02)
    tt = REC[0] + 0.5
    while tt < REC[1] - 0.4:
        place(s, tap(0.12), tt)
        tt += 1 / 5.2
    place(s, whoosh(0.6, 0.25), REC[1] + 0.3)
    place(s, whoosh(0.6, 0.2, up=False), REC[2] - 0.7)
    for c0 in (REC[1] + 1.0, REC[1] + 1.8):
        place(s, chirp(), c0)
    place(s, sweep(140, 220, 0.9, 0.08, noise=0.05), REC[2] + 0.3)
    for i in range(int((EVERY - WALK) * 1.8)):
        place(s, step(0.22), WALK + i / 1.8)
    for n in NODS:
        place(s, tap(0.08), n)
    place(s, glock(100, 0.15, 0.2), GLANCE)
    place(s, whoosh(0.25, 0.15), NOBODY - 0.05)
    place(s, whoosh(0.25, 0.15), EVERY - 0.05)
    place(s, whoosh(0.35, 0.2), END)
    return s


if __name__ == "__main__":
    out = music() * 0.95 + sfx()
    out = out / max(1e-6, np.abs(out).max()) * 0.8
    sf.write("mix_raw.wav", out.astype(np.float32), SR)
    print("ok bpm", BPM)
