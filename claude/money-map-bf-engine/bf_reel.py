import cairo, math, json, os, sys, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
from bf_common import *

DUR = 30.0
BG0 = (0.93, 0.95, 0.97)
SLATE = (0.10, 0.14, 0.22)
GX0, GX1, GY0, GY1 = 140, 960, 440, 900
VMIN, VMAX = 40, 110
_BG = None


def price(m):
    if m < 8.8:
        return 60 + 0.35 * math.sin(m * 7)
    if m < 9.0:
        return 60 + (m - 8.8) / 0.2 * 40
    if m < 10.0:
        return 100 + 0.35 * math.sin(m * 9)
    if m < 10.12:
        return 100 - (m - 10.0) / 0.12 * 50
    if m < 11.9:
        return 50 + 0.25 * math.sin(m * 7)
    if m < 12.0:
        return 50 - (m - 11.9) / 0.1
    return 49


def gx(m):
    return GX0 + (GX1 - GX0) * m / 12.0


def gy(v):
    return GY1 - (v - VMIN) / (VMAX - VMIN) * (GY1 - GY0)


def bg(c):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, 0.95, 0.97, 0.99)
        g.add_color_stop_rgb(1, 0.86, 0.90, 0.94)
        d.set_source(g)
        d.paint()
        d.set_source_rgba(0.1, 0.2, 0.4, 0.07)
        d.set_line_width(2)
        for x in range(0, VW + 1, 60):
            d.move_to(x, 0)
            d.line_to(x, VH)
        for y in range(0, VH + 1, 60):
            d.move_to(0, y)
            d.line_to(VW, y)
        d.stroke()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def axes(c):
    c.set_source_rgba(*SLATE, 0.8)
    c.set_line_width(5)
    c.move_to(GX0, GY0 - 20)
    c.line_to(GX0, GY1)
    c.line_to(GX1 + 20, GY1)
    c.stroke()
    c.set_source_rgba(*SLATE, 0.18)
    c.set_line_width(2)
    for v in (50, 70, 90, 110):
        c.move_to(GX0, gy(v))
        c.line_to(GX1, gy(v))
        c.stroke()
    for v in (50, 100):
        txt(c, "$%d" % v, GX0 - 18, gy(v) + 12, 34, SLATE, M, "r", 0.8)
    for i, l in enumerate("JFMAMJJASOND" + "J"):
        txt(c, l, gx(i), GY1 + 48, 36, SLATE, H, a=0.8)
    txt(c, "PRICE HISTORY", GX0, GY0 - 36, 36, SLATE, B, "l", 0.65)


def curve(c, upto, glow_oct=0.0):
    pts = [(gx(m), gy(price(m))) for m in [i * 0.02 for i in range(int(upto / 0.02) + 1)]]
    if len(pts) < 2:
        return None
    if glow_oct > 0:
        a, b = int(8.8 / 0.02), min(len(pts) - 1, int(10.2 / 0.02))
        if b > a:
            c.set_source_rgba(*RED, 0.25 * glow_oct)
            c.set_line_width(40)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.move_to(*pts[a])
            for p in pts[a + 1:b + 1]:
                c.line_to(*p)
            c.stroke()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgb(*SLATE)
    c.set_line_width(10)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    if glow_oct > 0:
        a, b = int(8.8 / 0.02), min(len(pts) - 1, int(10.2 / 0.02))
        c.set_source_rgba(*RED, glow_oct)
        c.set_line_width(12)
        c.move_to(*pts[a])
        for p in pts[a + 1:b + 1]:
            c.line_to(*p)
        c.stroke()
    return pts[-1]


def dot(c, x, y, v, t):
    for r, a in ((34, 0.18), (22, 0.3)):
        c.arc(x, y, r + 4 * math.sin(t * 10), 0, 2 * math.pi)
        c.set_source_rgba(*RED, a)
        c.fill()
    c.arc(x, y, 12, 0, 2 * math.pi)
    c.set_source_rgb(*RED)
    c.fill()
    lx = clamp(x, GX0 + 70, GX1 - 70)
    ly = y - 70 if y > GY0 + 90 else y + 90
    rrect(c, lx - 80, ly - 40, 160, 68, 34)
    c.set_source_rgb(*SLATE)
    c.fill()
    txt(c, "$%d" % round(v), lx, ly + 12, 46, (1, 1, 1), M)


def speaker(c, sticker, t, pulse=0.0):
    cx = VW / 2
    c.set_source_rgba(0, 0, 0, 0.12)
    c.rectangle(0, 1420, VW, 26)
    c.fill()
    c.set_source_rgb(0.80, 0.72, 0.60)
    c.rectangle(0, 1386, VW, 40)
    c.fill()
    g = cairo.LinearGradient(cx - 190, 980, cx + 190, 1390)
    g.add_color_stop_rgb(0, 0.66, 0.69, 0.74)
    g.add_color_stop_rgb(1, 0.46, 0.49, 0.55)
    rrect(c, cx - 190, 980, 380, 406, 34)
    c.set_source(g)
    c.fill()
    c.arc(cx, 1090, 40, 0, 2 * math.pi)
    c.set_source_rgb(0.22, 0.24, 0.29)
    c.fill()
    c.arc(cx, 1250, 112, 0, 2 * math.pi)
    c.set_source_rgb(0.18, 0.2, 0.25)
    c.fill()
    c.arc(cx, 1250, 46, 0, 2 * math.pi)
    c.set_source_rgb(0.35, 0.38, 0.44)
    c.fill()
    if sticker is not None:
        k, label = sticker
        s = max(0.001, k * (1 + 0.12 * pulse))
        c.save()
        c.translate(cx + 165, 1135)
        c.rotate(-0.2)
        c.scale(s, s)
        starburst(c, 0, 0, 125, 100, 16)
        c.set_source_rgba(0, 0, 0, 0.25)
        c.save()
        c.translate(8, 10)
        c.fill_preserve()
        c.restore()
        c.set_source_rgb(*RED)
        c.fill()
        txt(c, label, 0, 17, 52, (1, 1, 1))
        c.restore()


def head(c, lines, y, size=84, col=SLATE, a=1.0):
    n = len(lines)
    for i, ln in enumerate(lines):
        txt(c, ln, VW / 2, y + i * size * 1.15, size, col[i] if isinstance(col, list) else col, a=a)


def card83(c, t):
    a = e(t, 0, 0.35)
    c.set_source_rgba(*SLATE, a)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    txt(c, "WHICH? STUDY, 175 PRODUCTS", VW / 2, 360, 40, (1, 1, 1), B, a=0.7 * a)
    txt(c, "%d%%" % int(83 * e(t, 0.1, 1.2)), VW / 2, 760, 340, GREEN, a=a)
    for i, ln in enumerate(("OF BLACK FRIDAY DEALS WERE", "THE SAME PRICE OR CHEAPER", "ON OTHER DAYS")):
        txt(c, ln, VW / 2, 930 + i * 80, 58, (1, 1, 1), a=a * e(t, 0.8 + i * 0.25, 1.1 + i * 0.25))


def final(c, t):
    a = e(t, 0, 0.35)
    c.set_source_rgba(*SLATE, 1)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    head(c, ["CHECK THE", "PRICE HISTORY."], 500, 100, (1, 1, 1), a)
    head(c, ["THEN DECIDE."], 790, 100, GOLD, e(t, 0.5, 0.9))
    logo(c, VW / 2 - 90, 1010, 3.0, e(t, 1.0, 1.4))
    txt(c, "MONEY MAP", VW / 2, 1290, 70, (1, 1, 1), a=e(t, 1.0, 1.4))
    txt(c, "FOLLOW THE MONEY.", VW / 2, 1370, 50, GOLD, a=e(t, 1.3, 1.7))


def draw(c, T):
    T = T % DUR
    bg(c)
    axes(c)
    tt = T
    if T < 3.0:
        head(c, ["STORE SAYS: 50% OFF"], 200, 66)
        head(c, ["PRICE HISTORY SAYS:"], 290, 50, RED)
        txt(c, "?", VW / 2, 760, 330, SLATE, a=0.14 + 0.08 * math.sin(T * 6))
        upto = 0.0
    elif T < 5.6:
        head(c, ["JAN TO SEP: $60"], 230, 80)
        upto = 8.8 * e(T, 3.0, 5.4)
    elif T < 8.0:
        head(c, ["OCTOBER: $100"], 230, 90, RED)
        upto = 8.8 + 1.2 * e(T, 5.6, 7.6)
    elif T < 12.0:
        head(c, ["NOVEMBER: $50"], 230, 90, (0.1, 0.55, 0.3))
        upto = 10.0 + 1.9 * e(T, 8.0, 11.0) if T > 8.0 else 10.0
    elif T < 16.0:
        head(c, ["JANUARY: $49"], 230, 90, SLATE)
        upto = 11.9 + 0.1 * e(T, 12.0, 12.6)
    elif T < 20.0:
        head(c, ["THE $100 “WAS” PRICE", "LASTED 4 WEEKS"], 190, 72, RED)
        upto = 12.0
    else:
        upto = 12.0
    if T >= 3.0 and T < 20.0:
        glow = e(T, 16.0, 16.6) * (0.7 + 0.3 * math.sin(T * 8)) if T >= 16.0 else 0.0
        end = curve(c, max(0.04, upto), glow)
        if end and T < 16.0:
            dot(c, end[0], end[1], price(upto), T)
        if T >= 12.0 and T < 16.0:
            dot(c, gx(12.0), gy(49), 49, T)
        txt(c, "Example product. Pattern based on Which? research.", VW / 2, 990, 30, SLATE, B, a=0.75)
    if T >= 20.0 and T < 25.0:
        pass
    sticker = (1.0, "50% OFF")
    if T < 0.5:
        pulse = 1 - T / 0.5
    elif 8.0 <= T < 9.0:
        pulse = 1 - (T - 8.0)
    else:
        pulse = 0.0
    if T < 20.0:
        c.save()
        c.translate(0, 45)
        speaker(c, sticker, T, pulse)
        c.restore()
    if T < 0.45:
        r = 60 + 500 * T / 0.45
        c.arc(VW / 2 + 165, 1180, r, 0, 2 * math.pi)
        c.set_source_rgba(*RED, 0.5 * (1 - T / 0.45))
        c.set_line_width(14)
        c.stroke()
    if 8.0 <= T < 8.9:
        txt(c, "50% OFF!", gx(10.1) + 40, gy(50) + 120, 70, RED, a=1 - (T - 8.0) / 0.9, stroke=(1, 1, 1), sw=14)
    if 20.0 <= T < 25.0:
        card83(c, T - 20.0)
    if T >= 25.0:
        final(c, T - 25.0)


def music(path="reel_music.wav"):
    sr = 44100
    bpm = 96.0
    beat = 60.0 / bpm
    n = int(DUR * sr)
    tail = 3 * sr
    out = np.zeros(n + tail)
    rng = np.random.RandomState(5)

    def put(sig, t0):
        j = int(t0 * sr)
        out[j:j + len(sig)] += sig[:len(out) - j]

    def env(m, d):
        return np.exp(-np.arange(m) / (d * sr))

    m = int(0.35 * sr)
    kick = np.sin(2 * np.pi * (50 + 110 * np.exp(-np.arange(m) / (0.03 * sr))) * np.arange(m) / sr) * env(m, 0.12) * 0.9
    m2 = int(0.2 * sr)
    snare = (rng.randn(m2) * 0.5 + np.sin(2 * np.pi * 190 * np.arange(m2) / sr) * 0.4) * env(m2, 0.06) * 0.5
    b, a = butter(2, 5000 / (sr / 2), "high")
    m3 = int(0.05 * sr)
    hat = lfilter(b, a, rng.randn(m3)) * env(m3, 0.012) * 0.22
    chords = [(220.0, [220.0, 261.6, 329.6, 392.0]), (174.6, [174.6, 220.0, 261.6, 329.6]), (146.8, [146.8, 174.6, 220.0, 261.6]), (164.8, [164.8, 207.7, 246.9, 293.7])]
    bars = int(round(DUR / (4 * beat)))
    for bar in range(bars):
        root, notes = chords[(bar // 2) % 4]
        t0 = bar * 4 * beat
        for bt in range(4):
            tb = t0 + bt * beat
            if bt in (0, 2):
                put(kick, tb)
            if bt == 2 and bar % 2 == 1:
                put(kick, tb + 0.5 * beat)
            if bt in (1, 3):
                put(snare, tb)
            for h in range(2):
                sw = 0.0 if h == 0 else 0.62 * beat
                put(hat * (1.0 if h == 0 else 0.7), tb + sw)
        for tb, dur in ((t0, 1.5 * beat), (t0 + 2 * beat, 0.9 * beat), (t0 + 3 * beat, 0.9 * beat)):
            mm = int(dur * sr * 1.4)
            x = np.arange(mm) / sr
            bass = np.sin(2 * np.pi * (root / 2) * x) * env(mm, dur * 0.6) * 0.45
            put(bass, tb)
        for tb in (t0, t0 + 1.5 * beat + 0.0, t0 + 2.5 * beat):
            mm = int(1.6 * sr)
            x = np.arange(mm) / sr
            ch = sum(np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 6) for f in notes) * env(mm, 0.7) * 0.05
            put(ch, tb + (0.015 if tb > t0 else 0))
        mel = [notes[3], notes[2], notes[3], notes[1]]
        for k, tb in enumerate((t0 + 1 * beat, t0 + 1.5 * beat, t0 + 3 * beat, t0 + 3.5 * beat)):
            mm = int(0.6 * sr)
            x = np.arange(mm) / sr
            put(np.sin(2 * np.pi * mel[k] * 2 * x) * env(mm, 0.18) * 0.06, tb)
    out[:tail] += out[n:n + tail]
    out = out[:n]
    b, a = butter(2, 7000 / (sr / 2), "low")
    out = lfilter(b, a, out)
    out += rng.randn(n) * 0.002
    t_s = np.arange(int(0.25 * sr))
    out[:len(t_s)] += np.sin(2 * np.pi * 70 * t_s / sr) * np.exp(-t_s / (0.05 * sr)) * 0.5
    j = int(8.0 * sr)
    d_ = np.arange(int(0.6 * sr))
    out[j:j + len(d_)] += (np.sin(2 * np.pi * 988 * d_ / sr) + np.sin(2 * np.pi * 1318 * d_ / sr)) * np.exp(-d_ / (0.18 * sr)) * 0.12
    j = int(20.0 * sr)
    d_ = np.arange(int(0.5 * sr))
    wh = lfilter(*butter(2, [1200 / (sr / 2), 5000 / (sr / 2)], "band"), rng.randn(len(d_))) * np.sin(np.pi * d_ / len(d_)) * 0.18
    out[j:j + len(d_)] += wh
    out /= np.abs(out).max() / 0.9
    sf.write(path, out.astype(np.float32), sr)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "reel_v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        draw(c, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    music()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "reel_v.tmp.mp4", "-i", "reel_music.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    print("ok")


def stills():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, T in enumerate((0.0, 1.5, 4.5, 7.0, 8.3, 10.0, 13.0, 18.0, 22.0, 26.5, 27.5, 29.9)):
        draw(c, T)
        surf.write_to_png("rst_%02d.png" % i)


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    bg(c)
    txt(c, "50% OFF", VW / 2, 420, 190, RED, stroke=(1, 1, 1), sw=18)
    txt(c, "OF WHAT?", VW / 2, 590, 150, SLATE, stroke=(1, 1, 1), sw=18)
    c.save()
    c.translate(0, -60)
    speaker(c, (1.0, "50% OFF"), 0, 0)
    c.restore()
    surf.write_to_png(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"stills": lambda: stills(), "render": lambda: render(sys.argv[2]), "cover": lambda: cover(sys.argv[2]), "music": lambda: music()}[cmd]()
