import numpy as np, soundfile as sf
SR = 44100
DUR = 40.0
BPM = 72
B = 60 / BPM
BAR = 4 * B
rng = np.random.RandomState(7)


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


def reverb(x, secs=2.4, wet=0.3):
    n = int(secs * SR)
    ir = rng.randn(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = np.convolve(ir, np.ones(8) / 8, mode="same")
    ir /= np.abs(ir).sum() / 6
    L = len(x) + n
    nf = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[:len(x)]
    return x + wet * y / max(1e-9, np.abs(y).max()) * np.abs(x).max()


CH = dict(G=(43, [55, 59, 62, 67]), Em=(40, [55, 59, 64, 67]), C=(36, [52, 55, 60, 64]), D=(38, [54, 57, 62, 66]), Am=(45, [57, 60, 64, 69]))
PROG = ["G", "Em", "C", "D", "Em", "Am", "Am", "C", "D", "G", "C", "D"]
VEL = [0.45, 0.45, 0.5, 0.5, 0.45, 0.55, 0.28, 0.3, 0.42, 0.62, 0.66, 0.5]
MOTIF = [(0, 74), (1, 71), (2, 67), (3, 69), (4, 71), (5, 74), (6, 76), (7, 74), (8, 71), (9, 67)]


def build(path):
    n = int(DUR * SR)
    tail = 4 * SR
    pn = np.zeros(n + tail)
    fx = np.zeros(n + tail)

    def put(buf, x, at):
        a = int(at * SR)
        if a >= len(buf):
            return
        k = min(len(x), len(buf) - a)
        buf[a:a + k] += x[:k]

    for t0 in (0.0, 1.0, 2.0):
        put(pn, piano(91, 0.25, 0.6), t0)
    for b, name in enumerate(PROG):
        root, notes = CH[name]
        t = b * BAR
        v = VEL[b]
        if b in (6, 7):
            put(pn, piano(root, 3.0, v), t)
            put(pn, piano(notes[3] + 12, 1.6, v * 0.8), t + 1.5 * B)
            if b == 6:
                put(pn, piano(notes[1] + 12, 1.6, v * 0.7), t + 2.5 * B)
            continue
        put(pn, piano(root, BAR, v * 0.9), t)
        pat = (0, 1, 2, 3, 2, 1, 2, 3) if b >= 9 else (0, 2, 3, 2)
        step = 0.5 if b >= 9 else 1.0
        for i, p in enumerate(pat):
            put(pn, piano(notes[p] + 12, B * step * 1.8, v * (0.75 if i % 2 else 0.9)), t + i * B * step)
    mel = [(7.0, 74), (8.0, 71), (9.0, 67), (10.0, 69), (11.0, 71), (12.0, 74), (13.0, 71), (14.0, 67)]
    t = 2 * BAR
    for beat, m in [(0, 74), (1, 71), (2, 67), (3, 69), (4, 71), (5, 74), (6, 71), (7, 67)]:
        put(pn, piano(m + 12, B * 1.2, 0.4), t + beat * B)
    t = 9 * BAR
    for beat, m in [(0, 74), (1, 71), (2, 67), (3, 69), (4, 71), (5, 74), (6, 76), (7, 79)]:
        put(pn, piano(m + 12, B * 1.4, 0.6), t + beat * B + 0.0)
    t = 5 * BAR
    for beat, m in [(0, 72), (1, 69), (2, 64), (3, 67)]:
        put(pn, piano(m + 12, B * 1.2, 0.45), t + beat * B)
    put(pn, piano(91, 0.4, 0.55), 28.7)
    put(pn, piano(98, 0.4, 0.5), 29.4)
    n3 = int(0.5 * SR)
    th = np.sin(2 * np.pi * (70 - 25 * np.arange(n3) / SR) * np.arange(n3) / SR) * np.exp(-np.arange(n3) / (0.08 * SR)) * 0.5
    put(fx, th, 8.6)
    bl = rng.randn(int(0.9 * SR))
    bl = np.convolve(bl, np.ones(30) / 30, mode="same") * np.sin(np.pi * np.arange(len(bl)) / len(bl)) * 0.12
    put(fx, bl, 22.4)
    put(fx, th * 0.4, 25.4)
    pn[:tail] += pn[n:n + tail]
    fx[:tail] += fx[n:n + tail]
    pn = pn[:n]
    fx = fx[:n]
    mix = reverb(pn, 2.4, 0.3) * 0.9 + fx
    mix /= np.abs(mix).max() / 0.9
    st = np.stack([mix, np.roll(mix, 200) * 0.97 + mix * 0.03], axis=1)
    sf.write(path, st.astype(np.float32), SR)


if __name__ == "__main__":
    build("alarms_music.wav")
