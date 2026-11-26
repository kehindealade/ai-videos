import numpy as np, wave, sys
from timeline import START as S, TOTAL, BEAT

SR = 44100
E = BEAT / 2
N = int(SR * TOTAL)
out = np.zeros(N + 6 * SR)
rng = np.random.default_rng(72)


def add(sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i < 0:
        return
    out[i:i + len(sig)] += sig * gain


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def tv(d):
    return np.arange(int(d * SR)) / SR


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def bass(m, d=1.6, dec=2.2):
    t = tv(d)
    f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
            + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 10)) * np.exp(-t * dec) * np.minimum(1, t * 150)


def conga(f=220, d=0.45, dec=11):
    t = tv(d)
    fr = f * (1 + 0.5 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    return (np.sin(ph) + 0.25 * np.sin(2.1 * ph) * np.exp(-t * 30)) * np.exp(-t * dec) * np.minimum(1, t * 400) \
        + 0.25 * lp(rng.standard_normal(len(t)), 6) * np.exp(-t * 90)


def slap(d=0.14):
    t = tv(d)
    x = rng.standard_normal(len(t))
    x = x - lp(x, 10)
    return x * np.exp(-t * 60) * 0.6 + np.sin(2 * np.pi * 620 * t) * np.exp(-t * 70) * 0.5


def shaker(g=1.0):
    k = int(0.06 * SR)
    x = rng.standard_normal(k)
    x = x - lp(x, 8)
    return x * np.exp(-np.arange(k) / (0.014 * SR)) * g


def log(m, d=1.8, dec=3.4):
    t = tv(d)
    f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * 2.0 * f * t) * np.exp(-t * 9)
            + 0.10 * np.sin(2 * np.pi * 3.9 * f * t) * np.exp(-t * 25)) * np.exp(-t * dec) * np.minimum(1, t * 300)


def pad(ms, t0, d, g):
    t = tv(d)
    s = sum(np.sin(2 * np.pi * hz(m) * t * (1 + 0.002 * np.sin(2 * np.pi * 0.5 * t + k))) for k, m in enumerate(ms)) / len(ms)
    add(s * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.8), t0, g)


def thunk(t0, g=1.0, f0=90):
    t = tv(0.3)
    add(np.sin(2 * np.pi * f0 * t) * np.exp(-t * 18) + 0.3 * lp(rng.standard_normal(len(t)), 12) * np.exp(-t * 55), t0, 0.4 * g)


def step(t0, g=1.0):
    t = tv(0.12)
    add(lp(rng.standard_normal(len(t)), 30) * 3 * np.exp(-t * 50) + 0.5 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 60), t0, 0.10 * g)


def clang(t0, g=1.0):
    t = tv(0.9)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((1730, 7), (2610, 9), (4150, 14), (640, 20)))
    add(s * np.minimum(1, t * 800), t0, 0.07 * g)
    add(s * np.minimum(1, t * 800) * 0.5, t0 + 0.16, 0.05 * g)


def click(t0, g=1.0, f=2400):
    t = tv(0.03)
    add(np.sin(2 * np.pi * f * t) * np.exp(-t * 160), t0, 0.14 * g)


def ding(t0, g=1.0):
    add(log(81, 1.2, 5), t0, 0.12 * g)
    add(log(86, 1.2, 5), t0 + 0.09, 0.10 * g)


def wah(t0, d, g=1.0, base=150):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = np.zeros(n)
    env = np.zeros(n)
    i = 0
    while i < n:
        k = int(rng.uniform(0.13, 0.26) * SR)
        gap = int(rng.uniform(0.02, 0.07) * SR)
        k = min(k, n - i)
        f0 = base * rng.uniform(0.85, 1.45)
        tt = np.arange(k) / SR
        f[i:i + k] = f0 * (1 + 0.25 * np.sin(np.pi * tt / (k / SR)))
        env[i:i + k] = np.sin(np.pi * tt / (k / SR)) ** 0.6
        i += k + gap
    ph = 2 * np.pi * np.cumsum(np.maximum(f, 1)) / SR
    saw = sum(np.sin(h * ph) / h for h in range(1, 9))
    vib = 0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)
    x = lp(saw * env, 14) + 0.5 * lp(saw * env * vib, 40)
    add(x, t0, 0.16 * g)


def laugh(t0, g=1.0, base=330, n=5):
    for i in range(n):
        d = 0.13
        t = tv(d)
        f = base * (1 - 0.05 * i) * (1 + 0.15 * np.sin(np.pi * t / d))
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = sum(np.sin(h * ph) / h for h in range(1, 5)) * np.sin(np.pi * t / d)
        add(lp(s, 10), t0 + i * 0.19, 0.05 * g)


def cheer(t0, d, g=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = lp(x - lp(x, 60), 12)
    env = np.minimum(1, t / 0.3) * np.clip((d - t) / 2.5, 0, 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.7 * t) ** 2)
    add(x * env, t0, 0.35 * g)


def crickets(t0, d, g=1.0):
    t = t0
    while t < t0 + d:
        for j in range(3):
            c = tv(0.03)
            add(np.sin(2 * np.pi * 4300 * c) * np.sin(np.pi * c / 0.03), t + j * 0.06, 0.010 * g)
        t += 0.8 + 0.4 * rng.random()


def tick(t0, d, g=1.0):
    k = 0
    t = t0
    while t < t0 + d:
        click(t, 0.12 * g, 1500 if k % 2 == 0 else 1250)
        t += 1.0
        k += 1


ROOTS = [38, 41, 34, 33]
BASSP = [[(0, 0), (2, 7), (3, 12)], [(0, 0), (2, 7)], [(0, 0), (2, 7), (3, 12)], [(0, 0), (2, 7), (3, 12)]]
MEL = [[(0, 69), (1, 65), (2, 62), (3, 64)], [(0, 65), (2, 69)], [(0, 67), (1, 65), (2, 62)], [(0, 64)]]


def groove(t0, t1, level, g=1.0, bar0=0):
    bar = bar0
    t = t0
    while t < t1 - 0.05:
        r = ROOTS[bar % 4]
        for b, iv in BASSP[bar % 4]:
            tt = t + b * BEAT
            if tt >= t1 - 0.05:
                continue
            if level in ("thin", "bare") and b != 0:
                continue
            if level == "bare" and bar % 2 == 1:
                continue
            add(bass(r + iv, 2.2 if level in ("thin", "bare") else 1.4, 1.4 if level in ("thin", "bare") else 2.4), tt,
                (0.34 if level == "full" else 0.28) * g)
        for b, m in MEL[bar % 4]:
            tt = t + b * BEAT
            if tt >= t1 - 0.05:
                continue
            if level == "full" or (level == "half" and b in (0, 2)) or (level == "thin" and b == 0 and bar % 2 == 0):
                add(log(m), tt, (0.16 if level == "full" else 0.11) * g)
        if level in ("full", "half"):
            for e in range(8):
                tt = t + e * E
                if tt >= t1 - 0.05:
                    break
                if level == "full":
                    add(shaker(1.0 if e % 2 == 0 else 0.6), tt, 0.035 * g)
                    if e in (0, 3, 6):
                        add(conga(190), tt, 0.20 * g)
                    if e in (2, 5):
                        add(conga(285), tt, 0.16 * g)
                    if e in (4, 7):
                        add(slap(), tt, 0.12 * g)
                else:
                    if e in (0, 6):
                        add(conga(190), tt, 0.13 * g)
                    if e == 3:
                        add(conga(285), tt, 0.09 * g)
        t += 4 * BEAT
        bar += 1


def fail(t0, g=1.0):
    add(log(65, 2.2, 2.4), t0, 0.15 * g)
    add(log(62, 2.8, 2.0), t0 + 0.55, 0.15 * g)
    add(bass(38, 3.0, 1.2), t0 + 0.55, 0.26 * g)


def radio(t0, d, g=1.0):
    b = 0.25
    tune = [77, 81, 84, 81, 82, 81, 79, 77, 76, 79, 84, 79, 77, 81, 77, None]
    n = int(d * SR)
    x = np.zeros(n + SR)
    k = 0
    t = 0.0
    while t < d - 0.1:
        m = tune[k % len(tune)]
        if m is not None:
            tt = tv(0.22)
            s = np.sign(np.sin(2 * np.pi * hz(m) * tt)) * np.exp(-tt * 9) + 0.5 * np.sin(2 * np.pi * hz(m - 12) * tt) * np.exp(-tt * 7)
            i = int(t * SR)
            x[i:i + len(s)] += s
        if k % 2 == 0:
            tt = tv(0.05)
            i = int(t * SR)
            x[i:i + len(tt)] += 0.5 * rng.standard_normal(len(tt)) * np.exp(-tt * 80)
        t += b
        k += 1
    x = x[:n]
    x = x - lp(x, 40)
    x = lp(x, 5)
    x += 0.03 * rng.standard_normal(n)
    env = np.minimum(1, np.arange(n) / (0.05 * SR))
    env[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    add(x * env, t0, 0.12 * g)


s = S["s1"]
groove(s + 0.2, s + 4.15, "full")
for lt in np.arange(2.1, 4.0, 0.36):
    thunk(s + lt, 0.25, 110)
thunk(s + 4.2, 1.6, 70)
wah(s + 4.25, 3.9, 1.0)
wah(s + 8.5, 3.8, 0.9)
for a in (5.6, 7.0, 8.4, 9.8, 11.2):
    thunk(s + a, 0.7, 80)
clang(s + 7.0, 1.0)
pad([38, 45], s + 4.4, 12.6, 0.07)
for lt in np.arange(12.9, 15.2, 0.36):
    thunk(s + lt, 0.22 * max(0.2, 1 - (lt - 12.9) / 2.6), 110)
add(bass(38, 3.0, 1.0), s + 13.2, 0.30)
add(bass(33, 3.0, 1.0), s + 15.6, 0.26)

s = S["s2"]
groove(s + 0.6, s + 12.6, "thin")
for lt in np.arange(0.9, 4.5, 0.5):
    click(s + lt, 0.25, 1900)
    click(s + lt + 0.08, 0.2, 2100)
for a in (1.4, 2.6, 3.8):
    i0 = int((s + a) * SR)
    before = out[i0:i0 + SR].copy()
    wah(s + a, 0.7, 0.32)
clang(s + 6.2, 0.9)

s = S["s3"]
groove(s + 0.6, s + 13.4, "thin", bar0=2)
for a, n in ((1.0, 5), (2.2, 4), (3.6, 5), (6.4, 5), (7.8, 4), (9.0, 5)):
    laugh(s + a, 0.7, 300 + 60 * rng.random(), n)
    laugh(s + a + 0.1, 0.5, 240 + 40 * rng.random(), n)

s = S["s4"]
for lt in np.arange(0.5, 5.0, 0.42):
    step(s + lt)
add(bass(38, 3.0, 1.0), s + 0.6, 0.26)
add(bass(41, 3.0, 1.0), s + 3.9, 0.24)
ding(s + 7.6, 1.0)
groove(s + 7.9, s + 12.9, "half")
for lt in np.arange(8.3, 12.6, 0.42):
    step(s + lt, 0.8)

s = S["s5"]
groove(s + 0.2, s + 9.5, "half", 1.05)
for e in range(int(9.2 / E)):
    add(shaker(0.8 if e % 2 == 0 else 0.5), s + 0.2 + e * E, 0.028)
ding(s + 3.6, 1.0)
for a in (7.9, 9.2):
    click(s + a, 0.5, 3100)
fail(s + 10.3)
pad([38, 45], s + 10.0, 5.6, 0.045)

s = S["s6"]
groove(s + 0.2, s + 6.9, "full", 1.05)
ding(s + 2.2, 1.0)
thunk(s + 2.6, 0.5, 150)
thunk(s + 3.6, 0.7, 140)
thunk(s + 5.2, 0.9, 130)
cheer(s + 6.0, 5.8, 0.55)
for a in (6.2, 7.3, 8.0, 9.1, 10.0):
    laugh(s + a, 0.75, 320 + 70 * rng.random(), 5)
groove(s + 6.9, s + 14.6, "thin", 0.9, bar0=2)
fail(s + 12.5)
for lt in np.arange(15.0, 17.6, 0.42):
    step(s + lt, max(0.2, 1 - (lt - 15) / 2.8))

s = S["s7"]
for lt in np.arange(0.3, 2.0, 0.42):
    step(s + lt)
click(s + 2.6, 1.0)
ding(s + 2.75, 0.8)
radio(s + 2.8, 7.9)
for lt in np.arange(3.5, 5.2, 0.42):
    step(s + lt, 0.7)
for lt in np.arange(9.1, 10.4, 0.42):
    step(s + lt, 0.7)
click(s + 10.7, 1.2, 1700)
fail(s + 11.3, 0.9)
crickets(s + 11.0, 4.8, 0.7)

s = S["s8"]
crickets(s + 0.2, 16.5, 1.0)
lt = 0.2
while lt < 13.6:
    step(s + lt, 1.0)
    lt += np.pi / 6.0
ding(s + 1.0, 0.8)
for lt, m in ((1.2, 38), (5.4, 41), (9.6, 34), (13.8, 33)):
    add(bass(m, 4.0, 0.8), s + lt, 0.22)
for lt, m in ((3.3, 69), (7.5, 65), (11.7, 62), (14.6, 64)):
    add(log(m, 3.0, 1.8), s + lt, 0.13)

s = S["s9"]
for i in range(4):
    click(s + 0.5 + i * 0.8, 0.8, 1300)
    add(log(74 - i * 2, 0.8, 6), s + 0.5 + i * 0.8, 0.08)
for i, m in enumerate((50, 48, 46, 45)):
    thunk(s + 4.0 + i * 0.6, 0.9, 95 - i * 5)
    add(bass(m, 1.4, 2.6), s + 4.0 + i * 0.6, 0.26)
add(bass(38, 4.0, 0.8), s + 6.4, 0.34)
add(log(62, 3.0, 1.6), s + 6.4, 0.10)

s = S["s10"]
tick(s + 0.4, 14.4, 1.0)
pad([38, 45], s + 0.5, 14.0, 0.05)
add(log(62, 3.0, 1.6), s + 1.0, 0.10)
add(log(65, 3.0, 1.6), s + 7.4, 0.11)
add(log(62, 3.5, 1.4), s + 8.2, 0.11)

s = S["s11"]
tick(s + 0.2, 4.0, 1.0)
for lt in np.arange(2.5, 3.6, 0.42):
    step(s + lt, 0.7)
click(s + 4.4, 1.6, 900)
for lt in np.arange(5.1, 6.2, 0.42):
    step(s + lt, 0.6)
t = tv(0.7)
f = 150 - 50 * t
add(np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) * np.sin(np.pi * t / 0.7), s + 7.0, 0.035)
crickets(s + 4.8, 11.5, 0.6)
add(bass(38, 4.5, 0.7), s + 4.9, 0.30)
add(log(69, 3.0, 1.6), s + 7.6, 0.10)
add(bass(33, 4.5, 0.7), s + 10.6, 0.28)
add(log(64, 3.5, 1.4), s + 13.4, 0.09)

s = S["s12"]
for j, m in enumerate((69, 65, 62)):
    add(log(m, 3.5, 1.3), s + 0.8 + j * BEAT, 0.16)
add(bass(38, 5.0, 0.6), s + 0.8 + 2 * BEAT, 0.30)
for j, m in enumerate((62, 65, 69, 74)):
    add(log(m, 4.5, 1.0), s + 4.4 + j * BEAT, 0.16)
add(bass(38, 6.0, 0.5), s + 4.4, 0.32)
add(conga(190, 0.6, 8), s + 4.4 + 4 * BEAT, 0.14)
add(conga(190, 0.6, 8), s + 4.4 + 4.5 * BEAT, 0.08)
pad([50, 57, 62], s + 4.4, 8.2, 0.05)

s = S["s0"]
thunk(s + 0.0, 1.1, 70)
add(bass(38, 4.0, 0.8), s + 0.0, 0.32)
tick(s + 0.6, 5.2, 1.0)
add(log(62, 3.0, 1.6), s + 2.4, 0.12)
crickets(s + 0.3, 5.5, 0.6)
s = S["s0b"]
add(log(69, 1.6, 2.6), s + 0.1, 0.10)

d = int(0.24 * SR)
wet = np.zeros_like(out)
wet[d:] = out[:-d] * 0.20
wet[2 * d:] += out[:-2 * d] * 0.08
out = (out + wet)[:N]
fade = int(1.5 * SR)
out[-fade:] *= np.linspace(1, 0, fade)
out = np.tanh(out * 1.8) / 1.8
out = out / np.max(np.abs(out)) * 0.85
st = (np.stack([out, out], 1) * 32767).astype(np.int16)
w = wave.open(sys.argv[1], "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(st.tobytes()); w.close()
rms = np.sqrt(np.mean(out ** 2))
print("audio ok", TOTAL, "rms dB", 20 * np.log10(rms))
for name, t0 in S.items():
    seg = out[int(t0 * SR):int((t0 + 10) * SR)]
    print(name, round(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9), 1), round(float(np.max(np.abs(seg))), 2))
