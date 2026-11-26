import numpy as np, soundfile as sf, sys

SR = 44100
BPM = 66
B = 60 / BPM
BAR = 4 * B
OFF = dict(s0=0, s0b=5, s1=7, s2=25, s3=42, s4=62, s5=90, s6=110, s7=140, s8=160)
TOTAL = 180.0
rng = np.random.RandomState(3)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, dur, vel):
    f = mtof(m)
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > 12000:
            break
        amp = (1.0 / k ** 1.4) * (0.6 if k == 2 else 1.0)
        dec = 1.2 + 0.9 * k + f / 600
        out += amp * np.sin(2 * np.pi * fk * t + k) * np.exp(-t * dec / 2.2)
    rel = np.ones(n)
    r0 = int(dur * SR)
    if r0 < n:
        rel[r0:] = np.exp(-(np.arange(n - r0) / SR) * 7)
    att = np.minimum(1, t / 0.004)
    ham = rng.randn(n) * np.exp(-t * 90) * 0.02
    return (out * rel * att + ham) * vel * 0.22


def strings(m, dur, vel, att=1.6):
    f = mtof(m)
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 1.5)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    out = np.zeros(n)
    for k in range(1, 7):
        out += np.sin(k * ph + k * 0.7) / k ** 1.6
    env = np.minimum(1, t / att) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 2.5))
    return out * env * vel * 0.05


def place(buf, x, at):
    a = int(at * SR)
    if a >= len(buf):
        return
    b = min(len(buf), a + len(x))
    buf[a:b] += x[:b - a]


CH = dict(Am=[45, 57, 60, 64], F=[41, 53, 57, 60], C=[48, 55, 60, 64], G=[43, 55, 59, 62], Em=[40, 55, 59, 64], Fmaj7=[41, 57, 60, 64], Dm=[38, 57, 62, 65])
MEL1 = [(76, 2), (74, 1), (72, 1), (72, 2), (69, 2), (67, 1), (72, 1), (76, 2), (74, 3), (71, 1)]
MEL2 = [(76, 2), (74, 1), (72, 1), (72, 2), (69, 2), (67, 1), (72, 1), (79, 2), (76, 2), (72, 2)]


def arps(pn, start, chords, vel=0.6, pat=(0, 1, 2, 3, 2, 1, 2, 3), bass=True, step=0.5):
    t = start
    for ch in chords:
        notes = CH[ch]
        if bass:
            place(pn, piano(notes[0] - 12 if notes[0] > 40 else notes[0], BAR, vel * 0.9), t)
        for i, p in enumerate(pat):
            place(pn, piano(notes[p] + 12 if p > 0 else notes[p] + 12, B * step * 1.8, vel * (0.75 if i % 2 else 0.9)), t + i * B * step)
        t += BAR
    return t


def melody(pn, start, mel, vel=0.7, oct=0):
    t = start
    for m, beats in mel:
        place(pn, piano(m + oct, beats * B, vel), t)
        t += beats * B
    return t


def pad(st, start, chords, vel=0.6):
    t = start
    for ch in chords:
        for m in CH[ch][1:]:
            place(st, strings(m, BAR, vel), t)
        place(st, strings(CH[ch][0], BAR, vel * 0.8), t)
        t += BAR
    return t


def noise_bed(n, a, lp=40):
    x = rng.randn(n)
    k = np.ones(lp) / lp
    return np.convolve(x, k, mode="same") * a


def reverb(x, secs=2.6, wet=0.28):
    n = int(secs * SR)
    ir = rng.randn(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = np.convolve(ir, np.ones(8) / 8, mode="same")
    ir /= np.abs(ir).sum() / 6
    L = len(x) + n
    nf = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[:len(x)]
    return x + wet * y / max(1e-9, np.abs(y).max()) * np.abs(x).max()


def click(v=0.12, f=3200):
    n = int(0.018 * SR)
    t = np.arange(n) / SR
    return (rng.randn(n) * 0.6 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 400) * v


def typing(fx, start, a, b, nchar, dele=False):
    if b <= a or nchar <= 0:
        return
    k = nchar if not dele else max(4, nchar // 2)
    for i in range(k):
        tt = start + a + (b - a) * i / k + rng.uniform(-0.01, 0.01)
        place(fx, click(0.08 if dele else 0.11, 2400 if dele else 3400), tt)


def thud(v=0.6):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (60 - 20 * t) * t) + 0.3 * rng.randn(n) * np.exp(-t * 40)) * np.exp(-t * 9) * v


def knock():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 180 * t) + 0.5 * rng.randn(n)) * np.exp(-t * 45) * 0.35


def tape(d=1.6):
    n = int(d * SR)
    x = rng.randn(n)
    x = x - np.convolve(x, np.ones(6) / 6, mode="same")
    env = np.minimum(1, np.arange(n) / (0.05 * SR)) * np.exp(-np.arange(n) / SR * 1.2)
    return x * env * 0.09


def build(out):
    n = int(TOTAL * SR)
    pn = np.zeros(n + SR * 4)
    st = np.zeros(n + SR * 4)
    fx = np.zeros(n + SR * 4)
    amb = np.zeros(n + SR * 4)
    place(pn, piano(76, 1.5, 0.8), 0.0)
    place(pn, piano(45, 4.5, 0.6), 0.0)
    place(pn, piano(64, 3, 0.5), 0.9)
    place(pn, piano(72, 3, 0.5), 1.8)
    place(pn, piano(69, 3.2, 0.55), 2.9)
    place(pn, piano(33, 2.0, 0.5), 5.0)
    t = arps(pn, 7.0, ["Am", "F", "C", "G", "Am"], 0.45, pat=(0, 2, 3, 2), step=1.0)
    t = arps(pn, 25.0, ["Am", "F", "C", "G"], 0.5, pat=(0, 1, 2, 3, 2, 1, 2, 3))
    melody(pn, 25.0, MEL1, 0.45)
    t = arps(pn, 42.0, ["F", "C", "G", "Am", "F"], 0.5)
    pad(st, 42.0, ["F", "C", "G", "Am", "F"], 0.35)
    t = arps(pn, 62.0, ["Am", "F", "C", "G", "Am", "F", "C", "G"], 0.6)
    pad(st, 66.0, ["F", "C", "G", "Am", "F", "C", "G"], 0.9)
    melody(pn, 69.3, MEL1, 0.7)
    melody(pn, 69.3 + 4 * BAR, MEL2, 0.75)
    melody(st, 69.3 + 4 * BAR, [(m - 12, d) for m, d in MEL2], 0.9) if False else None
    t = arps(pn, 90.0, ["Am", "Em", "F", "C", "Dm"], 0.4, pat=(0, 2, 3, 2), step=1.0)
    place(pn, piano(57, 3.0, 0.45), 110.2)
    place(pn, piano(64, 3.0, 0.4), 111.1)
    place(pn, piano(72, 3.6, 0.4), 112.0)
    place(st, strings(57, 9.0, 0.35, 3.0), 114.0)
    place(st, strings(64, 9.0, 0.30, 3.0), 114.0)
    place(pn, piano(76, 4.0, 0.35), 123.6)
    arps(pn, 125.0, ["F", "C", "G", "C"], 0.45, pat=(0, 2, 3, 2), step=1.0)
    pad(st, 126.0, ["F", "C", "G", "C"], 0.6)
    t = arps(pn, 140.0, ["F", "C", "G", "Am", "F"], 0.42)
    melody(pn, 142.0, [(72, 2), (74, 1), (76, 1), (76, 2), (72, 2), (74, 2), (79, 2), (76, 4)], 0.45)
    arps(pn, 160.0, ["Am", "F", "C", "G", "C"], 0.55)
    pad(st, 160.0, ["Am", "F", "C", "G", "C"], 0.8)
    melody(pn, 160.0, MEL2, 0.6)
    place(pn, piano(60, 6, 0.5), 160 + 4 * BAR)
    place(pn, piano(64, 6, 0.45), 160 + 4 * BAR + 0.4)
    place(pn, piano(67, 6, 0.45), 160 + 4 * BAR + 0.8)
    place(pn, piano(72, 6, 0.5), 160 + 4 * BAR + 1.2)
    o = OFF
    typing(fx, o["s0"], 3.9, 4.6, 11, True)
    place(fx, click(0.12), 0.02)
    typing(fx, o["s1"], 10.0, 12.4, 17)
    typing(fx, o["s1"], 14.0, 15.4, 17, True)
    place(fx, thud(0.7), o["s1"] + 4.4)
    typing(fx, o["s2"], 4.4, 6.0, 12)
    typing(fx, o["s2"], 8.0, 9.2, 12, True)
    for k in range(3):
        place(fx, knock(), o["s3"] + 0.4 + k * 0.28)
    place(fx, thud(0.25), o["s3"] + 7.3)
    place(fx, thud(0.5), o["s3"] + 14.4)
    typing(fx, o["s3"], 15.8, 17.0, 9)
    typing(fx, o["s3"], 18.2, 19.0, 9, True)
    typing(fx, o["s4"], 7.4, 15.0, 70)
    typing(fx, o["s4"], 19.0, 21.4, 60, True)
    place(fx, tape(1.8), o["s5"] + 5.0)
    typing(fx, o["s5"], 9.2, 12.0, 29)
    typing(fx, o["s5"], 15.0, 16.6, 29, True)
    typing(fx, o["s6"], 1.0, 3.2, 11)
    typing(fx, o["s6"], 13.0, 14.4, 11, True)
    place(fx, click(0.2, 1800), o["s6"] + 19.9)
    place(fx, click(0.25, 900), o["s6"] + 26.0)
    place(fx, click(0.25, 900), o["s7"] + 15.5)
    tt = np.arange(len(amb)) / SR
    rain = noise_bed(len(amb), 0.05, 6) * (1 + 0.3 * np.sin(2 * np.pi * 0.2 * tt))
    renv = np.zeros(len(amb))
    def seg(a, b, lvl, fi=0.8, fo=1.5):
        i0, i1 = int(a * SR), int(b * SR)
        e_ = np.ones(i1 - i0) * lvl
        k1, k2 = int(fi * SR), int(fo * SR)
        e_[:k1] *= np.linspace(0, 1, k1)
        e_[-k2:] *= np.linspace(1, 0, k2)
        renv[i0:i1] += e_
    seg(0, 5, 0.5)
    seg(62, 90, 1.0)
    seg(110, 122, 0.9, 0.8, 3.0)
    room = noise_bed(len(amb), 0.006, 200)
    music = reverb(pn + st, 2.8, 0.35)
    mix = music * 0.9 + fx + rain * renv + room
    mix = mix[:n]
    fade = np.ones(n)
    k = int(2.5 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    mix *= fade
    mix /= max(1e-9, np.abs(mix).max()) / 0.9
    stereo = np.stack([mix, np.roll(mix, 220) * 0.97 + mix * 0.03], axis=1)
    sf.write(out, stereo.astype(np.float32), SR)


if __name__ == "__main__":
    build(sys.argv[1])
