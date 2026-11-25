import json, os, subprocess, importlib, numpy as np, soundfile as sf, cairo
from ss_common import *

VW, VH = 1080, 1920
SR = 24000


def timeline(L, durs, lead=0.10, tail=1.4):
    tl = []
    t = lead
    for i, ln in enumerate(L):
        d = durs[i] + ln["gap"]
        if i == len(L) - 1:
            d += tail
        tl.append((t, d))
        t += d
    return tl, t


def cap_chunks(s, mx=30):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > mx and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return [lines[i:i + 2] for i in range(0, len(lines), 2)]


def caps_for(L, tl, durs):
    out = []
    for i, ln in enumerate(L):
        t0 = tl[i][0] + 0.08
        ch = cap_chunks(ln["cap"])
        tot = sum(len(" ".join(c)) for c in ch)
        x = t0
        for c in ch:
            dd = max(1.2, durs[i] * len(" ".join(c)) / tot) if len(ch) > 1 else durs[i] + ln["gap"] * 0.8
            out.append((x, x + dd, c))
            x += dd
    return out


def draw_caption(c, caps, T, fnt=BODY, bg=(0.06, 0.07, 0.12), fg=WHITE, hl=GOLD, y=1150):
    cur = None
    for a, b, ch in caps:
        if a <= T < b:
            cur = (a, b, ch)
    if not cur:
        return
    a, b, ch = cur
    k = e(T, a, a + 0.15)
    size = 54
    ws = [tw(c, s, size, fnt) for s in ch]
    w = max(ws) + 70
    h = 80 * len(ch) + 34
    x = 540 - w / 2
    yy = y + (1 - k) * 14
    box(c, x, yy, w, h, bg, 0.88 * k, 18)
    for j, s in enumerate(ch):
        txt(c, s, 540, yy + 72 + j * 80, size, fg, fnt, "c", k)


def render(drawfn, total, out, w=VW, h=VH):
    n = int(total * FPS)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    c = cairo.Context(surf)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (w, h), "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fr in range(n):
        drawfn(c, fr / FPS)
        surf.flush()
        pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    pr.wait()


def stills(drawfn, times, outdir, prefix="f", w=VW, h=VH):
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    c = cairo.Context(surf)
    for T in times:
        drawfn(c, T)
        surf.write_to_png(os.path.join(outdir, "%s_%05.2f.png" % (prefix, T)))


def tone(f, d, a=0.3, dec=3.0):
    t = np.arange(int(d * SR)) / SR
    env = np.exp(-t * dec) * np.minimum(1, t * 300)
    return a * env * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t))


def noise_hit(seed, d=0.03, dec=0.004, a=0.08, smooth=3):
    r = np.random.RandomState(seed)
    n = int(d * SR)
    x = r.randn(n) * np.exp(-np.arange(n) / (dec * SR))
    return np.convolve(x, np.ones(smooth) / smooth, mode="same") * a


def thump(a=0.5):
    t = np.arange(int(0.4 * SR)) / SR
    return a * np.sin(2 * np.pi * (80 - 40 * t) * t) * np.exp(-t * 12)


def write_audio(vodir, L, tl, total, events, bedfn, outwav, srt_caps=None, srt_path=None):
    files = json.load(open(os.path.join(vodir, "files.json")))
    n = int((total + 0.3) * SR)
    voice = np.zeros(n)
    fx = np.zeros(n)

    def put(buf, x, at, g=1.0):
        a = int(at * SR)
        if a < 0 or a >= n:
            return
        b = min(n, a + len(x))
        buf[a:b] += x[:b - a] * g

    for i, ln in enumerate(L):
        a, _ = sf.read(os.path.join(vodir, files[i]))
        put(voice, a, tl[i][0] + 0.08)
    for x, at, g in events:
        put(fx, x, at, g)
    mix = voice + fx + bedfn(total + 0.3)[:n]
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    sf.write(outwav, mix.astype(np.float32), SR)
    if srt_caps and srt_path:
        def ts(x):
            return ("%02d:%02d:%06.3f" % (int(x // 3600), int(x % 3600 // 60), x % 60)).replace(".", ",")
        with open(srt_path, "w") as f:
            for k, (a, b, ch) in enumerate(srt_caps):
                f.write("%d\n%s --> %s\n%s\n\n" % (k + 1, ts(a), ts(b), "\n".join(ch)))
