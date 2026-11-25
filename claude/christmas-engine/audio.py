import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, lfilter

SR = 44100
DUR = 180.0
N = int(DUR * SR)
L = np.zeros(N)
R = np.zeros(N)
BPM = 84.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
rng = np.random.default_rng(3)


def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def put(sig, t0, gain=1.0, pan=0.0, bus=None):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    j = min(N, i + len(sig))
    seg = sig[:j - i] * gain
    lg = np.cos((pan + 1) * np.pi / 4)
    rg = np.sin((pan + 1) * np.pi / 4)
    (bus or (L, R))[0][i:j] += seg * lg
    (bus or (L, R))[1][i:j] += seg * rg


MUS = (np.zeros(N), np.zeros(N))
FX = (np.zeros(N), np.zeros(N))


def mp(sig, t0, gain=1.0, pan=0.0):
    put(sig, t0, gain, pan, MUS)


def fp(sig, t0, gain=1.0, pan=0.0):
    put(sig, t0, gain, pan, FX)


def tt(d):
    return np.arange(int(d * SR)) / SR


def musicbox(f, d=2.2):
    t = tt(d)
    s = np.zeros_like(t)
    for m, a, tau in ((1, 1.0, 1.1), (2.0, 0.28, 0.6), (3.0, 0.12, 0.35), (5.4, 0.05, 0.2)):
        s += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau)
    s *= np.minimum(t / 0.003, 1)
    return s * 0.5


def celesta(f, d=1.6):
    t = tt(d)
    s = np.zeros_like(t)
    for m, a, tau in ((1, 1.0, 0.8), (4, 0.22, 0.35), (6, 0.07, 0.2)):
        s += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau)
    s *= np.minimum(t / 0.006, 1)
    return s * 0.4


def pluck(f, d=1.2):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.18)
    s *= np.minimum(t / 0.004, 1)
    return s * 0.35


def cello(f, d, vib=1.0, amp=1.0):
    t = tt(d)
    fv = f * (1 + 0.0045 * vib * np.sin(2 * np.pi * 5.1 * t) * np.minimum(t / 0.7, 1))
    ph = 2 * np.pi * np.cumsum(fv) / SR
    s = np.zeros_like(t)
    for n in range(1, 10):
        s += np.sin(n * ph) / (n ** 1.35)
    env = np.minimum(t / 0.22, 1) * np.clip((d - t) / 0.45, 0, 1)
    return s * env * 0.42 * amp


def pad(f, d):
    t = tt(d)
    s = np.zeros_like(t)
    for dt in (0.9965, 1.0, 1.0035):
        s += np.sin(2 * np.pi * f * dt * t) + 0.3 * np.sin(4 * np.pi * f * dt * t) + 0.12 * np.sin(6 * np.pi * f * dt * t)
    env = np.minimum(t / 1.4, 1) * np.clip((d - t) / 1.4, 0, 1)
    return s * env * 0.12


def noise(d):
    return rng.standard_normal(int(d * SR))


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x, fc):
    return x - lp(x, fc)


# --------------------------------------------------------------- music
CH_MIN = {"Bm": (47, (59, 62, 66)), "G": (43, (55, 59, 62)), "Em": (40, (52, 55, 59))}
CH_MAJ = {"D": (38, (57, 62, 66)), "G": (43, (55, 59, 62)), "A": (45, (57, 61, 64)), "Bm": (47, (59, 62, 66))}
TH_MIN = [[(78, 0, 2), (74, 2, 1)], [(71, 0, 2), (69, 2, 1)], [(71, 0, 1), (74, 1, 1), (78, 2, 1)], [(76, 0, 3)],
          [(74, 0, 2), (73, 2, 1)], [(71, 0, 2), (66, 2, 1)], [(67, 0, 1), (69, 1, 1), (71, 2, 1)], [(71, 0, 3)]]
CHORDS_MIN = ["Bm", "Bm", "G", "Em", "Bm", "Bm", "Em", "Bm"]
TH_MAJ = [[(81, 0, 2), (78, 2, 1)], [(74, 0, 2), (76, 2, 1)], [(78, 0, 1), (81, 1, 1), (83, 2, 1)], [(81, 0, 3)],
          [(78, 0, 2), (76, 2, 1)], [(74, 0, 2), (69, 2, 1)], [(76, 0, 1), (78, 1, 1), (79, 2, 1)], [(78, 0, 3)]]
CHORDS_MAJ = ["D", "D", "G", "A", "D", "Bm", "G", "D"]


def bar(tb, k, th, chords, tbl, vol):
    mel, bass, chord, padv, cmel, cel = vol
    ch = chords[k % 8]
    root, tones = tbl[ch]
    if bass > 0:
        mp(cello(mf(root), BAR * 0.98, 0.6), tb, bass * 0.9, -0.2)
    if chord > 0:
        for bi in (1, 2):
            for ii, m in enumerate(tones):
                mp(pluck(mf(m), 1.0), tb + bi * BEAT + ii * 0.035, chord * 0.55, 0.15)
    if padv > 0 and k % 2 == 0:
        for m in tones:
            mp(pad(mf(m - 12), BAR * 2.05), tb, padv * 0.8, 0.0)
    for (m, b0, bd) in th[k % 8]:
        if mel > 0:
            mp(musicbox(mf(m), 2.4), tb + b0 * BEAT, mel, 0.25)
        if cel > 0:
            mp(celesta(mf(m + 12), 1.8), tb + b0 * BEAT, cel, -0.25)
        if cmel > 0:
            mp(cello(mf(m - 12), bd * BEAT * 0.97, 1.0), tb + b0 * BEAT, cmel, -0.1)


def lvl_min(tb):
    if tb < 4.3:
        return (0.55, 0.30, 0, 0, 0, 0)
    if tb < 43:
        return (0.42, 0.50, 0.30, 0, 0, 0)
    if tb < 65:
        return (0.46, 0.55, 0.32, 0.30, 0, 0)
    if tb < 74:
        k = (tb - 65) / 9
        return (0.55 + 0.1 * k, 0.6, 0.38, 0.45 + 0.2 * k, 0.3 + 0.3 * k, 0.15)
    if tb < 84:
        return (0.7, 0.65, 0.42, 0.7, 0.62, 0.22)
    if tb < 92:
        k = (tb - 84) / 8
        return (0.55, 0.55 - 0.1 * k, 0.32, 0.4, 0.3 * (1 - k), 0.0)
    return (0.40, 0.45, 0.25, 0.25, 0, 0)


k = 0
while k * BAR < 102:
    tb = k * BAR
    bar(tb, k, TH_MIN, CHORDS_MIN, CH_MIN, lvl_min(tb))
    k += 1
    if tb < 4.3 and k >= 2:
        pass
mp(cello(mf(47), 15.8, 0.5, 0.8), 102.0, 0.5, -0.1)
for tm, m in ((104.6, 78), (109.4, 74), (113.5, 71)):
    mp(musicbox(mf(m), 3.0), tm, 0.28, 0.2)
mp(musicbox(mf(66), 3.0), 117.0, 0.12, 0.2)

T0 = 125.0
for k in range(21):
    tb = T0 + k * BAR
    if k < 4:
        vol = (0.55, 0.55, 0.35, 0.45, 0.0, 0.0)
    elif k < 8:
        vol = (0.55, 0.6, 0.38, 0.55, 0.0, 0.18)
    else:
        vol = (0.62, 0.62, 0.40, 0.6, 0.5, 0.28)
    bar(tb, k, TH_MAJ, CHORDS_MAJ, CH_MAJ, vol)
tb = 170.0
for i, m in enumerate((62, 66, 69, 74, 78)):
    mp(musicbox(mf(m), 5.0), tb + i * 0.42, 0.5, 0.2)
    mp(celesta(mf(m + 12), 4.0), tb + i * 0.42 + 0.01, 0.25, -0.2)
for m in (50, 57, 62, 66):
    mp(pad(mf(m), 10.0), 170.0, 0.9)
mp(cello(mf(38), 8.0, 0.8), 170.0, 0.6)

# --------------------------------------------------------------- effects
def bell(t0, f=880, g=0.3):
    t = tt(1.6)
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t / 0.5)
    fp(s, t0, g)


def thump(t0, g=0.5, f=60):
    t = tt(0.7)
    s = np.sin(2 * np.pi * f * (1 + 0.6 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.18)
    fp(s, t0, g)


thump(0.0, 0.8, 55)
bell(0.0, 987, 0.22)


def engine(t0, t1, g=0.11, fade=0.8):
    d = t1 - t0
    t = tt(d)
    base = 0
    s = np.zeros_like(t)
    for h, a in ((1, 1.0), (2, 0.6), (3, 0.4), (4, 0.25)):
        s += a * np.sin(2 * np.pi * 31 * h * t + 0.6 * np.sin(2 * np.pi * 0.7 * t)) * (1 + 0.5 * np.sin(2 * np.pi * 15.5 * h * t))
    s += 0.25 * lp(noise(d), 160)
    s *= np.minimum(t / fade, 1) * np.clip((d - t) / fade, 0, 1)
    fp(lp(s, 400), t0, g)


for a, b in ((0, 4), (17, 24), (31, 38), (38, 43), (47, 56), (65, 74), (74, 84), (84, 88), (97, 102), (102, 110)):
    engine(a, b, 0.10 if a not in (38, 65) else 0.05)


def wiper(t0):
    d = 0.5
    t = tt(d)
    s = lp(noise(d), 1800) * np.sin(np.pi * t / d) ** 2
    fp(s, t0, 0.18)


t = 65.0
while t < 69.0:
    wiper(t)
    t += 1.11

for tw in (50.0, 50.5):
    d = 0.22
    t = tt(d)
    s = np.sin(2 * np.pi * (320 - 120 * t / d) * t) * np.exp(-t / 0.07)
    s += 0.6 * np.sin(2 * np.pi * 640 * t) * np.exp(-t / 0.05)
    s += 0.35 * lp(noise(d), 2400) * np.exp(-t / 0.08)
    fp(s, tw, 0.22)


def crunch(t0, g=0.28):
    d = 0.16
    t = tt(d)
    s = hp(lp(noise(d), 4200), 500) * np.exp(-t / 0.05) + 0.5 * lp(noise(d), 700) * np.exp(-t / 0.08)
    fp(s, t0, g, rng.uniform(-0.2, 0.2))


def thud(t0, g=0.25):
    t = tt(0.25)
    s = np.sin(2 * np.pi * 85 * t) * np.exp(-t / 0.05) + 0.4 * lp(noise(0.25), 500) * np.exp(-t / 0.04)
    fp(s, t0, g)


st = 110.9
while st < 116.8:
    crunch(st)
    st += 0.571
for ts in np.arange(150.5, 156.5, 0.571):
    crunch(ts, 0.18)
for ts in (123.2, 123.85, 124.45):
    thud(ts, 0.22)
t = tt(0.6)
fp((np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.08) + 0.6 * lp(noise(0.6), 900) * np.exp(-t / 0.1)) * 0.9, 110.0, 0.5)

for kt in (118.5, 119.4, 120.3):
    t = tt(0.5)
    s = (np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.07) + 0.5 * np.sin(2 * np.pi * 310 * t) * np.exp(-t / 0.04) + 0.5 * lp(noise(0.5), 1500) * np.exp(-t / 0.03))
    fp(s, kt, 0.8)
    bell(kt + 0.02, 523, 0.04)

t = tt(1.4)
creak = lp(noise(1.4), 700) * (0.4 + 0.6 * np.sin(2 * np.pi * 6 * t)) * np.sin(np.pi * t / 1.4)
fp(creak * 0.25, 125.2, 1.0)
t = tt(0.2)
fp(np.sin(2 * np.pi * 1200 * t) * np.exp(-t / 0.01) * 0.5 + lp(noise(0.2), 3000) * np.exp(-t / 0.02) * 0.3, 125.15, 0.5)


def blip(t0, f=880, g=0.14, n=1):
    for i in range(n):
        t = tt(0.07)
        s = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 * np.exp(-t / 0.05)
        fp(s, t0 + i * 0.11, g)


for ty in (17.0, 38.0, 65.0, 92.0):
    blip(ty + 0.1, 880, 0.14, 2)
blip(121.0, 1175, 0.2, 3)

t = tt(0.9)
vb = np.zeros(int(0.9 * SR))
for i in range(2):
    a = int((0.05 + i * 0.4) * SR)
    d = int(0.3 * SR)
    seg = tt(0.3)
    vb[a:a + d] = np.sin(2 * np.pi * 170 * seg) * 0.6 + 0.4 * lp(noise(0.3), 400)
for ts in (12.0, 13.2):
    fp(vb, ts, 0.2)
t = tt(0.05)
fp(np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01), 15.4, 0.3)

d = 5.0
t = tt(d)
murm = lp(noise(d), 600) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t)) * np.minimum(t / 0.8, 1) * np.clip((d - t) / 0.8, 0, 1)
fp(murm, 7.0, 0.10)

t = tt(1.0)
kj = hp(noise(1.0), 3500) * (np.abs(np.sin(2 * np.pi * 11 * t)) ** 3) * np.exp(-t / 0.35)
fp(kj, 133.9, 0.22)


def reverb(x):
    ir_t = tt(1.9)
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55)
    ir = lp(ir, 5200)
    ir /= np.sqrt((ir ** 2).sum())
    return fftconvolve(x, ir)[:N]


wL, wR = reverb(MUS[0]), reverb(MUS[1])
mL = MUS[0] * 0.8 + wL * 0.35
mR = MUS[1] * 0.8 + wR * 0.35
outL = mL * 0.9 + FX[0]
outR = mR * 0.9 + FX[1]
fade = np.clip((DUR - np.arange(N) / SR) / 3.0, 0, 1)
outL *= fade
outR *= fade
pk = max(np.abs(outL).max(), np.abs(outR).max())
print("peak", pk)
st = np.stack([outL, outR], 1) / max(pk, 1e-6) * 0.7
sf.write("xmas_audio.wav", st, SR)
print("ok")
