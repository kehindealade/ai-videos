import numpy as np, soundfile as sf, librosa
from scipy.signal import fftconvolve, lfilter

SR = 44100
DUR = 180.0
N = int(DUR * SR)
BPM = 66.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(6)
MUS = (np.zeros(N), np.zeros(N))
FX = (np.zeros(N), np.zeros(N))
VO = (np.zeros(N), np.zeros(N))


def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def put(sig, t0, gain=1.0, pan=0.0, bus=MUS):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    j = min(N, i + len(sig))
    seg = sig[:j - i] * gain
    bus[0][i:j] += seg * np.cos((pan + 1) * np.pi / 4)
    bus[1][i:j] += seg * np.sin((pan + 1) * np.pi / 4)


def tt(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x, fc):
    return x - lp(x, fc)


def rhodes(f, d=2.6, vel=1.0):
    t = tt(d)
    mod = np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.05) * 1.6 * vel
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 1.3)
    s += 0.25 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.6)
    s *= (1 + 0.12 * np.sin(2 * np.pi * 4.5 * t))
    s *= np.minimum(t / 0.004, 1) * np.clip((d - t) / 0.3, 0, 1)
    return s * 0.32


def flute(f, d, amp=1.0):
    t = tt(d)
    fv = f * (1 + 0.006 * np.sin(2 * np.pi * 5.0 * t) * np.minimum(t / 0.5, 1))
    ph = 2 * np.pi * np.cumsum(fv) / SR
    s = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    s += 0.05 * lp(noise(d), 3000)
    env = np.minimum(t / 0.09, 1) * np.clip((d - t) / 0.25, 0, 1)
    return s * env * 0.22 * amp


def bass(f, d=1.2):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.2)
    s *= np.exp(-t / 0.55) * np.minimum(t / 0.006, 1)
    return lp(s, 900) * 0.5


def pad(f, d):
    t = tt(d)
    s = np.zeros_like(t)
    for dt in (0.996, 1.0, 1.004):
        s += np.sin(2 * np.pi * f * dt * t) + 0.25 * np.sin(4 * np.pi * f * dt * t)
    env = np.minimum(t / 1.6, 1) * np.clip((d - t) / 1.6, 0, 1)
    return s * env * 0.09


def brush(t0, g):
    d = 0.18
    t = tt(d)
    put(hp(noise(d), 4000) * np.exp(-t / 0.05), t0, g, 0.3)


CH = {"Cm": (36, (60, 63, 67)), "Ab": (32, (60, 63, 68)), "Eb": (39, (58, 63, 67)), "Bb": (34, (58, 62, 65)),
      "Fm": (41, (60, 65, 68)), "G": (31, (59, 62, 67))}
PROG_MIN = ["Cm", "Ab", "Eb", "Bb", "Cm", "Ab", "Fm", "G"]
PROG_MAJ = ["Eb", "Bb", "Cm", "Ab", "Eb", "Bb", "Ab", "Eb"]
MEL_MIN = [[(67, 0, 1), (72, 1, 1), (75, 2, 1), (74, 3, 1)], [(72, 0, 1), (70, 1, 1), (67, 2, 2)],
           [(68, 0, 1), (72, 1, 1), (75, 2, 1), (79, 3, 1)], [(77, 0, 1), (75, 1, 1), (74, 2, 2)],
           [(75, 0, 2), (74, 2, 1), (72, 3, 1)], [(72, 0, 1), (68, 1, 1), (72, 2, 2)],
           [(68, 0, 1), (72, 1, 1), (77, 2, 1), (75, 3, 1)], [(74, 0, 4)]]
MEL_MAJ = [[(70, 0, 1), (75, 1, 1), (79, 2, 1), (77, 3, 1)], [(75, 0, 1), (74, 1, 1), (70, 2, 2)],
           [(72, 0, 1), (75, 1, 1), (79, 2, 1), (82, 3, 1)], [(80, 0, 1), (79, 1, 1), (77, 2, 2)],
           [(79, 0, 2), (77, 2, 1), (75, 3, 1)], [(74, 0, 1), (70, 1, 1), (74, 2, 2)],
           [(72, 0, 1), (75, 1, 1), (80, 2, 1), (79, 3, 1)], [(75, 0, 4)]]


def bar(tb, k, prog, mel, v):
    rv, fl, bs, pd, br, arp = v
    root, tones = CH[prog[k % 8]]
    if rv > 0:
        for ii, m in enumerate(tones):
            put(rhodes(mf(m), 3.0, 0.8), tb + ii * 0.02, rv, -0.2)
        if arp > 0:
            for bi in range(1, 4):
                put(rhodes(mf(tones[bi % 3] + 12), 1.4, 0.6), tb + bi * BEAT, arp * 0.6, 0.25)
    if bs > 0:
        put(bass(mf(root)), tb, bs)
        put(bass(mf(root + 7)), tb + 2 * BEAT, bs * 0.7)
    if pd > 0:
        for m in tones:
            put(pad(mf(m - 12), BAR * 1.05), tb, pd)
    if br > 0:
        for bi in range(4):
            brush(tb + bi * BEAT + 0.5 * BEAT, br)
    if fl > 0:
        for (m, b0, bd) in mel[k % 8]:
            put(flute(mf(m), bd * BEAT * 0.98), tb + b0 * BEAT, fl, 0.1)


def lvl(tb):
    if tb < 5:
        return (0.35, 0, 0.3, 0, 0, 0)
    if tb < 14:
        return (0.45, 0, 0.35, 0.3, 0, 0)
    if tb < 30:
        return (0.45, 0.55, 0.4, 0.4, 0, 0)
    if tb < 64:
        return (0.42, 0.0, 0.55, 0.3, 0.12, 0.45)
    if tb < 110:
        return (0.45, 0.7, 0.5, 0.5, 0.0, 0.25)
    k = (tb - 110) / 22
    return (0.5 + 0.15 * k, 0.75 + 0.25 * k, 0.6, 0.6 + 0.5 * k, 0.0, 0.3 + 0.3 * k)


k = 0
while k * BAR < 132:
    bar(k * BAR, k, PROG_MIN, MEL_MIN, lvl(k * BAR))
    k += 1
put(pad(mf(48), 9.0), 132.0, 0.6)
put(pad(mf(55), 9.0), 132.0, 0.4)
put(rhodes(mf(63), 4.0, 0.5), 136.5, 0.35)
put(rhodes(mf(62), 4.0, 0.5), 140.2, 0.3)
put(rhodes(mf(60), 5.0, 0.5), 143.6, 0.28)
T0 = 151.0
for kk in range(6):
    tb = T0 + kk * BAR
    v = (0.5, 0.0 if kk < 1 else 0.85, 0.5, 0.6, 0.0, 0.45)
    if 162.0 <= tb < 170.5:
        v = (0.4, 0.0, 0.4, 0.6, 0.0, 0.3)
    bar(tb, kk, PROG_MAJ, MEL_MAJ, v)
for i, m in enumerate((63, 67, 70, 75, 79)):
    put(rhodes(mf(m), 6.0, 0.7), 172.6 + i * 0.35, 0.5, 0.2 - 0.1 * i)
for m in (51, 58, 63, 67):
    put(pad(mf(m), 7.4), 172.6, 0.9)
put(flute(mf(75), 4.5), 174.0, 0.6)
put(bass(mf(39), 3.0), 172.6, 0.6)


# ------------------------------------------------------------ effects
def fx(sig, t0, g=1.0, pan=0.0):
    put(sig, t0, g, pan, FX)


def buzz(t0, t1, g=0.35):
    t = t0
    while t < t1:
        d = min(0.55, t1 - t)
        s = tt(d)
        sig = (np.sign(np.sin(2 * np.pi * 150 * s)) * 0.4 + 0.6 * lp(noise(d), 300)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * s)))
        sig *= np.minimum(s / 0.01, 1) * np.clip((d - s) / 0.02, 0, 1)
        fx(lp(sig, 700), t, g, 0.1)
        t += 1.0


def ringback(t0, t1, g=0.06, pan=-0.3):
    t = t0
    while t < t1:
        d = min(1.6, t1 - t)
        s = tt(d)
        sig = (np.sin(2 * np.pi * 440 * s) + np.sin(2 * np.pi * 480 * s)) * np.minimum(s / 0.02, 1) * np.clip((d - s) / 0.02, 0, 1)
        fx(lp(sig, 2500), t, g, pan)
        t += 3.6


def dtmf(t0, n, step=0.24, g=0.07):
    keys = [(697, 1209), (697, 1336), (770, 1209), (852, 1477), (770, 1336), (941, 1336), (697, 1477), (852, 1336), (770, 1477), (941, 1209)]
    for i in range(n):
        a, b = keys[i % len(keys)]
        s = tt(0.12)
        fx((np.sin(2 * np.pi * a * s) + np.sin(2 * np.pi * b * s)) * np.clip((0.12 - s) / 0.01, 0, 1), t0 + i * step, g, -0.2)


def click(t0, g=0.3, f=1400):
    s = tt(0.12)
    fx(np.sin(2 * np.pi * f * s) * np.exp(-s / 0.008) + 0.5 * lp(noise(0.12), 2500) * np.exp(-s / 0.02), t0, g)


def clunk(t0, g=0.5):
    s = tt(0.35)
    fx(np.sin(2 * np.pi * 110 * s) * np.exp(-s / 0.06) + 0.5 * lp(noise(0.35), 900) * np.exp(-s / 0.05), t0, g)


def clink(t0, g=0.18):
    s = tt(0.8)
    fx((np.sin(2 * np.pi * 2650 * s) + 0.6 * np.sin(2 * np.pi * 3720 * s)) * np.exp(-s / 0.18), t0, g, 0.2)


def tick(t0, t1, g=0.09):
    t = t0
    while t < t1:
        s = tt(0.04)
        fx(hp(noise(0.04), 2000) * np.exp(-s / 0.006), t, g, 0.0)
        t += 1.0


def bed(t0, t1, kind, g):
    d = t1 - t0
    s = tt(d)
    env = np.minimum(s / 0.4, 1) * np.clip((d - s) / 0.4, 0, 1)
    if kind == "office":
        sig = lp(noise(d), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * s)) + 0.2 * hp(lp(noise(d), 3000), 1500) * (np.sin(2 * np.pi * 6 * s) > 0.6)
    elif kind == "train":
        sig = lp(noise(d), 180) * 1.5 + 0.5 * lp(noise(d), 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * s) ** 8)
    elif kind == "city":
        sig = lp(noise(d), 250) * 0.8
    elif kind == "pour":
        sig = hp(lp(noise(d), 3500), 600) * (0.7 + 0.3 * np.sin(2 * np.pi * 13 * s))
    fx(sig * env, t0, g)


def swish(t0, g=0.12):
    d = 0.4
    s = tt(d)
    fx(hp(noise(d), 1500) * np.sin(np.pi * s / d) ** 2, t0, g)


def marker(t0, g=0.08, d=0.6):
    s = tt(d)
    fx(hp(lp(noise(d), 5000), 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * s)) * np.sin(np.pi * s / d), t0, g, 0.3)


buzz(0.0, 5.0, 0.42)
click(0.0, 0.25, 900)
swish(1.75, 0.15)
fx(np.zeros(1), 0)
marker(9.8, 0.10)
tick(7.0, 9.0, 0.08)
dtmf(12.0, 10)
ringback(14.6, 23.0)
buzz(14.6, 20.0, 0.22)
clunk(24.7, 0.45)
clink(27.2)
bed(30.0, 42.0, "office", 0.05)
swish(35.8, 0.12)
bed(42.0, 50.0, "train", 0.10)
bed(50.0, 64.0, "city", 0.05)
tick(64.0, 68.5, 0.08)
clink(65.6)
ringback(69.2, 77.0)
buzz(69.2, 72.0, 0.22)
click(72.0, 0.2, 1800)
clunk(76.8, 0.45)
clink(80.2)
tick(90.0, 93.5, 0.08)
ringback(94.2, 103.4)
buzz(94.2, 99.0, 0.18)
clunk(103.3, 0.45)
tick(104.0, 110.0, 0.06)
tick(110.0, 115.0, 0.09)
clink(115.8)
ringback(119.0, 129.4)
buzz(119.0, 129.0, 0.40)
clunk(129.4, 0.5)
tick(134.0, 149.0, 0.11)
dtmf(146.0, 10, 0.24, 0.08)
buzz(149.0, 150.0, 0.45)
click(150.0, 0.35, 1100)
bed(157.3, 161.3, "pour", 0.07)
clink(161.5)
for t, n in ((25.0, 1), (77.0, 2), (103.5, 3), (129.6, 4)):
    marker(t, 0.09, 0.5)


def vo(path, t0, g=1.0):
    a, sr = sf.read(path)
    if a.ndim > 1:
        a = a.mean(1)
    a = librosa.resample(a, orig_sr=sr, target_sr=SR)
    a = a / (np.abs(a).max() + 1e-9)
    put(a, t0, g, 0.0, VO)
    return len(a) / SR


ds = vo("vo/son.wav", 162.5, 0.55)
dg = vo("vo/gran.wav", 166.6, 0.45)
print("vo", ds, dg)


def reverb(x, dec=0.7):
    ir_t = tt(2.2)
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / dec)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    return fftconvolve(x, ir)[:N]


wl, wr = reverb(MUS[0]), reverb(MUS[1])
duck = np.ones(N)
for a, b in ((162.3, 165.4), (166.4, 168.2)):
    i0, i1 = int(a * SR), int(b * SR)
    duck[i0:i1] = 0.45
duck = lp(duck, 3.0)
ml = (MUS[0] * 0.75 + wl * 0.4) * duck
mr = (MUS[1] * 0.75 + wr * 0.4) * duck
vl = VO[0] + 0.12 * reverb(VO[0], 0.25)
vr = VO[1] + 0.12 * reverb(VO[1], 0.25)
room = lp(rng.standard_normal(N), 400) * 0.0025
outl = ml * 0.85 + FX[0] + vl + room
outr = mr * 0.85 + FX[1] + vr + room
fade = np.clip((DUR - np.arange(N) / SR) / 2.5, 0, 1)
outl *= fade
outr *= fade
pk = max(np.abs(outl).max(), np.abs(outr).max())
st = np.stack([outl, outr], 1) / pk * 0.8
sf.write("sunday_audio.wav", st, SR)
print("ok peak", pk)
