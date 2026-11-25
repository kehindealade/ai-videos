import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
from chat_reel import PING_T, TYPING, CAL0, CAL1, BACK_AT, S2_AT, STAMP_AT, END_AT, DUR

SR = 44100
N = int(SR * DUR)
rng = np.random.default_rng(24)
BPM = 16 * 4 * 60 / DUR
BEAT = 60 / BPM
BAR = BEAT * 4


def nf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, sig, t, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[:j - i] * g


def env(n, a=0.005, d=0.4):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def hp(x, f):
    b, a = butter(2, f / (SR / 2), "high")
    return lfilter(b, a, x)


def lp(x, f):
    b, a = butter(2, f / (SR / 2), "low")
    return lfilter(b, a, x)


def epiano(midi, dur, vel=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = nf(midi)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.25) \
        + 0.12 * np.sin(2 * np.pi * 3 * f * t + 0.5) * np.exp(-t / 0.12) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t)
    s *= (1 + 0.12 * np.sin(2 * np.pi * 4.5 * t))
    e_ = np.minimum(1, t / 0.006) * np.exp(-t / 0.9) * np.minimum(1, (dur - t) / 0.06)
    return s * e_ * vel * 0.12


def bass(midi, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = nf(midi)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t / 0.5) * np.minimum(1, (dur - t) / 0.05) * 0.3


def kick():
    n = int(SR * 0.25)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11) * 0.7


def snare():
    n = int(SR * 0.2)
    t = np.arange(n) / SR
    nz = hp(rng.standard_normal(n), 1500) * np.exp(-t / 0.07)
    return (nz * 0.28 + np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05) * 0.2)


def hat(open_=False):
    n = int(SR * (0.12 if open_ else 0.04))
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t / (0.05 if open_ else 0.012)) * 0.12


def ping(f, vol=0.5, d=0.35):
    n = int(SR * 1.0)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.1) + 0.2 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.05)
    return s * np.minimum(1, t / 0.003) * np.exp(-t / d) * vol


def tick(vol=0.5):
    n = int(SR * 0.05)
    t = np.arange(n) / SR
    s = lp(hp(rng.standard_normal(n), 900), 5000) * np.exp(-t / 0.008) * 0.6 + np.sin(2 * np.pi * 1400 * t) * np.exp(-t / 0.01) * 0.3
    return s * vol


def thump(vol=0.8):
    n = int(SR * 0.5)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (48 + 60 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.18)
    s += lp(rng.standard_normal(n), 1500) * np.exp(-t / 0.02) * 0.4
    return s * vol


CH = [(65, [65, 69, 72, 76]), (64, [64, 67, 71, 74]), (62, [62, 65, 69, 72]), (60, [60, 64, 67, 71])]


def music():
    m = np.zeros(N)
    d = np.zeros(N)
    for bar in range(16):
        root, notes = CH[bar % 4]
        t0 = bar * BAR
        for hit_t, ln, vel in ((0, 1.4, 1.0), (1.5, 0.7, 0.7), (2.5, 0.8, 0.8), (3.25, 0.6, 0.55)):
            for k, nt in enumerate(notes):
                place(m, epiano(nt + 12 if k else nt, ln * BEAT * 1.3, vel), t0 + hit_t * BEAT + k * 0.008)
        for ht, ln in ((0, 1.4), (2.5, 0.9)):
            place(m, bass(root - 24, ln * BEAT), t0 + ht * BEAT)
        place(d, kick(), t0)
        place(d, kick(), t0 + 2 * BEAT)
        place(d, kick(), t0 + 2.75 * BEAT, 0.6)
        place(d, snare(), t0 + 1 * BEAT)
        place(d, snare(), t0 + 3 * BEAT)
        for h in range(8):
            place(d, hat(h == 7), t0 + h * BEAT / 2 + (0.03 * BEAT if h % 2 else 0), 0.8 if h % 2 else 1.0)
    t = np.arange(N) / SR

    def gate(a0, a1, r=0.03):
        return np.clip((t - a0) / r, 0, 1) * np.clip((a1 - t) / r, 0, 1)

    dg = gate(0.0, 9.0) * 0.9 + gate(S2_AT, STAMP_AT) * 1.0
    mg = gate(0, 16.0) + gate(CAL0, BACK_AT) * 0.0 + gate(S2_AT, STAMP_AT)
    mg = np.clip(mg, 0, 1)
    mg = mg * (1 - 0.55 * gate(9.0, 16.0))
    pad = np.zeros(N)
    for k, nt in enumerate([53, 60, 64, 67]):
        pad += 0.05 * np.sin(2 * np.pi * nf(nt) * t) * (1 + 0.2 * np.sin(2 * np.pi * 0.3 * t + k))
    pad *= gate(CAL0, BACK_AT, 0.4)
    out = m * mg + d * dg + pad
    end = np.zeros(N)
    for nt, off in ((60, 0), (64, 0.05), (67, 0.1), (71, 0.15), (72, 0.3)):
        place(end, epiano(nt, 3.5, 1.2) * 1.6, END_AT + off)
    place(end, bass(36, 3.4), END_AT)
    out += end
    out *= np.clip((DUR - t) / 0.25, 0, 1)
    return out


def sfx():
    s = np.zeros(N)
    pent = [659, 784, 880, 1047, 1175, 1319, 1568]
    place(s, ping(523, 0.5), 0.0)
    for i, (t0, snd, tx) in enumerate(__import__("chat_reel").S1[1:8]):
        place(s, ping(pent[i], 0.45), t0)
    place(s, ping(440, 0.55, 0.5), 9.0)
    for k, (a0, a1, snd) in enumerate(TYPING):
        place(s, ping(330 - k * 25, 0.18 - k * 0.04, 0.12), a0)
        place(s, ping(260 - k * 25, 0.22 - k * 0.05, 0.25), a1)
    nflip = int((CAL1 - CAL0) / 0.4)
    for k in range(nflip + 1):
        place(s, tick(0.55), CAL0 + k * 0.4 + 0.28)
    place(s, ping(300, 0.2, 0.3), BACK_AT)
    S2 = __import__("chat_reel").S2
    place(s, tick(0.6), S2_AT)
    place(s, ping(523, 0.5), S2[1][0])
    for i, (t0, snd, tx) in enumerate(S2[2:7]):
        place(s, ping(pent[i], 0.42), t0)
    place(s, ping(pent[5], 0.42), S2[7][0])
    for i in range(3):
        place(s, thump(0.9), STAMP_AT + 0.3 + i * 0.85)
    place(s, ping(1047, 0.35, 0.6), END_AT)
    return s


if __name__ == "__main__":
    out = music() * 0.9 + sfx() * 0.95
    out = out / max(1e-6, np.abs(out).max()) * 0.8
    sf.write("mix_raw.wav", out.astype(np.float32), SR)
    print("ok", BPM, BEAT)
