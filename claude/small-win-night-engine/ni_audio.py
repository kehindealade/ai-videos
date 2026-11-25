import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
import night_reel as R

SR = 44100
DUR = R.DUR
N = int(SR * DUR)
T = np.arange(N) / SR
rng = np.random.default_rng(38)
BEAT = R.BEAT


def nf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, sig, t, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[:j - i] * g


def lp(x, f, o=2):
    b, a = butter(o, f / (SR / 2), "low")
    return lfilter(b, a, x)


def hp(x, f, o=2):
    b, a = butter(o, f / (SR / 2), "high")
    return lfilter(b, a, x)


def bp(x, f0, f1):
    b, a = butter(2, [f0 / (SR / 2), f1 / (SR / 2)], "band")
    return lfilter(b, a, x)


def gate(a0, a1, r=0.05):
    return np.clip((T - a0) / r, 0, 1) * np.clip((a1 - T) / r, 0, 1)


def tt(d):
    return np.arange(int(SR * d)) / SR


def kick():
    t = tt(0.3)
    return np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t / 0.035)) / SR) * np.exp(-t / 0.14) * 0.9


def clap():
    t = tt(0.2)
    return bp(rng.standard_normal(len(t)), 900, 3000) * np.exp(-t / 0.06) * 0.5


def hat():
    t = tt(0.06)
    return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t / 0.015) * 0.2


def saw(f, d, cut=1500):
    t = tt(d)
    s = 2 * ((f * t) % 1) - 1 + 2 * ((f * 1.007 * t) % 1) - 1
    return lp(s, cut) * np.minimum(1, t / 0.005) * np.exp(-t / (d * 0.6)) * 0.18


def club():
    out = np.zeros(N)
    prog = [(57, [69, 72, 76]), (53, [69, 72, 77]), (55, [67, 71, 74]), (52, [67, 71, 76])]
    nb = int(14.0 / BEAT)
    for b in range(nb):
        t0 = b * BEAT
        bar = (b // 4) % 4
        root, ch = prog[bar]
        place(out, kick(), t0)
        place(out, hat(), t0 + BEAT / 2)
        if b % 2 == 1:
            place(out, clap(), t0)
        place(out, saw(nf(root - 12), BEAT * 0.45, 400) * 2.2, t0 + BEAT / 2)
        if b % 4 in (1, 3):
            for n in ch:
                place(out, saw(nf(n), BEAT * 0.35, 2500), t0 + BEAT * 0.5)
    return out


def kal(m, vel=1.0):
    t = tt(2.0)
    f = nf(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.06)
    return s * np.minimum(1, t / 0.002) * vel * 0.22


def bell(m, vel=1.0, d=1.6):
    t = tt(d * 2)
    f = nf(m)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.1)
    return s * np.exp(-t / d) * vel * 0.18


def cosy(a0, a1, seed):
    out = np.zeros(N)
    r = np.random.default_rng(seed)
    scale = [60, 62, 64, 67, 69, 72, 74, 76]
    t = a0
    k = 0
    while t < a1:
        m = scale[int(r.integers(0, len(scale)))]
        place(out, kal(m, 0.8 + 0.2 * r.random()), t)
        if k % 4 == 0:
            place(out, kal(48 + [0, 5, 7, 3][(k // 4) % 4] , 0.9), t)
        t += 0.42 * (1 + (k % 3 == 2))
        k += 1
    return out


def noise_bed(f0, f1, amp):
    return bp(rng.standard_normal(N), f0, f1) * amp


def click(vol=0.4):
    t = tt(0.04)
    return hp(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.006) * vol


def knock():
    t = tt(0.25)
    return (lp(rng.standard_normal(len(t)), 600) * 1.2 + np.sin(2 * np.pi * 140 * t)) * np.exp(-t / 0.04) * 0.6


def buzz():
    t = tt(0.4)
    return np.sign(np.sin(2 * np.pi * 150 * t)) * lp(np.ones(len(t)), 50) * 0.12 * (np.sin(np.pi * t / 0.4) > 0.2)


def honk():
    t = tt(0.5)
    s = np.sign(np.sin(2 * np.pi * 415 * t)) + np.sign(np.sin(2 * np.pi * 523 * t))
    return lp(s, 2500) * np.minimum(1, t / 0.01) * np.minimum(1, (0.5 - t) / 0.03) * 0.18


def whoosh(d=0.8):
    t = tt(d)
    return bp(rng.standard_normal(len(t)), 300, 3000) * np.sin(np.pi * t / d) ** 2 * 0.35


def record_stop():
    t = tt(0.6)
    f = 220 * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.4) * 0.35 + lp(rng.standard_normal(len(t)), 800) * np.exp(-t / 0.1) * 0.2


def thunder():
    t = tt(3.0)
    return lp(rng.standard_normal(len(t)), 180, 4) * (np.minimum(1, t / 0.05) * np.exp(-t / 1.0)) * 4.0


def squelch():
    t = tt(0.18)
    f = 300 + 400 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05) * 0.12 + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.04) * 0.1


def womp():
    out = np.zeros(int(SR * 1.6))
    for k, m in enumerate([55, 54, 53, 52]):
        t = tt(0.5 if k < 3 else 0.9)
        f = nf(m)
        s = lp(2 * ((f * t) % 1) - 1, 900) * np.minimum(1, t / 0.02) * np.exp(-t / 0.5) * 0.25
        i = int(k * 0.28 * SR)
        out[i:i + len(s)] += s[:len(out) - i]
    return out


def mix():
    c = club()
    c_far = lp(c, 350, 2)
    c_mid = lp(c, 1800, 2)
    w_mid = gate(0, 9.6, 0.4) + gate(11.8, 14.0, 0.05) * 0
    w_full = gate(9.6, 11.8, 0.5)
    w_far = gate(11.8, 13.2, 0.1) * np.clip((13.3 - T) / 1.5, 0, 1)
    music = c_mid * w_mid + c * w_full * 0.9 + c_far * w_far * 1.4
    music += cosy(13.45, 25.0, 3) * (1 - 0.45 * gate(17.3, 24.0, 0.3))
    music += cosy(30.2, 35.0, 5) * 0.7
    for k, m in enumerate([72, 76, 79, 84]):
        place(music, bell(m, 1.0), R.CARD_AGAIN + k * 0.16)
    for k, m in enumerate([60, 64, 67, 72, 76]):
        place(music, bell(m, 1.1, 2.0), R.END_AT + k * 0.07)
    s = np.zeros(N)
    for L in R.LEAVES:
        place(s, click(0.35), L - 0.4)
        place(s, click(0.5), L + 0.05)
    place(s, honk(), R.TAXI_HONK)
    place(s, honk(), R.TAXI_HONK + 0.6)
    place(s, whoosh(1.0), R.CAB_GO)
    place(s, record_stop(), 13.35)
    for b in R.BUZZ:
        place(s, buzz(), b)
    place(s, knock() * 0.6, R.FLIP + 0.2)
    for k in R.KNOCK:
        place(s, knock(), k)
    t = tt(0.5)
    place(s, bp(rng.standard_normal(len(t)), 400, 1200) * np.sin(np.pi * t / 0.5) * 0.12, R.DOOR_OPEN)
    place(s, bell(91, 0.8, 0.5), R.SPOON0 + 0.6)
    place(s, knock() * 0.8, R.DOOR_SHUT)
    place(s, bell(84, 0.4, 0.3), R.NEIGH_GONE)
    for k in range(20):
        place(s, click(0.25), R.CLOCK0 + k * 0.045)
    for k in range(3):
        place(s, bell(69, 0.7, 1.2), 25.95 + k * 0.6 if False else R.CLOCK0 + 0.95 + k * 0.33)
    rain_out = noise_bed(500, 6000, 0.18)
    rain_w = gate(R.RAIN0, 30.2, 0.5) * 1.0 + gate(30.2, R.RAIN1, 0.3) * 0.35
    s += rain_out * rain_w
    place(s, thunder(), R.THUNDER)
    for i in range(16):
        place(s, squelch(), R.STREET2 + 0.1 + i * 0.17 + (i % 2) * 0.03)
    place(s, womp(), R.REGRET)
    room = noise_bed(100, 900, 0.02) * gate(13.4, 35.0, 0.3)
    tv = noise_bed(300, 2500, 0.03) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * T) * np.sin(2 * np.pi * 0.7 * T)) * gate(13.4, 25.0, 0.3)
    out = music + s * 1.0 + room + tv
    out *= np.clip((DUR - T) / 0.25, 0, 1)
    return out


if __name__ == "__main__":
    out = mix()
    out = out / max(1e-6, np.abs(out).max()) * 0.85
    sf.write("mix_raw.wav", out.astype(np.float32), SR)
    print("ok")
