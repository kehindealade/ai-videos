import cairo, math, random, json, os, sys, subprocess
import numpy as np, soundfile as sf
from bf_common import *

VOICE, SPEED = "af_kore", 0.98
LINES = [
    ("hook", "This Black Friday deal isn't the cheapest price of the year."),
    ("track", "A UK consumer group, Which?, tracked Black Friday deals for a whole year."),
    ("pct", "Eighty-three percent were the same price or cheaper on other days."),
    ("how", "So how does the store still win?"),
    ("r1", "One. A few doorbuster deals pull you in."),
    ("r2", "Two. You add full-price extras while you're there."),
    ("r3", "Three. The countdown makes you skip checking."),
    ("receipt", "The deal is the bait. The basket is the profit."),
    ("close", "Same tag. Now you know what it's for."),
]
NIGHT0, NIGHT1 = (0.03, 0.05, 0.13), (0.10, 0.13, 0.28)
random.seed(7)
BOKEH = [(random.uniform(0, VW), random.uniform(250, 1700), random.uniform(18, 70), random.choice([(1, .8, .4), (.5, .7, 1), (1, .4, .5)]), random.uniform(0.05, 0.13)) for _ in range(26)]
_BG = None


def bg(c):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, *NIGHT0)
        g.add_color_stop_rgb(1, *NIGHT1)
        d.set_source(g)
        d.paint()
        for x, y, r, col, a in BOKEH:
            rg = cairo.RadialGradient(x, y, 0, x, y, r)
            rg.add_color_stop_rgba(0, *col, a * 1.6)
            rg.add_color_stop_rgba(0.7, *col, a)
            rg.add_color_stop_rgba(1, *col, 0)
            d.set_source(rg)
            d.paint()
        for x0, w, a in ((-100, 220, 0.045), (260, 90, 0.035), (700, 300, 0.04)):
            d.move_to(x0, 0)
            d.line_to(x0 + w, 0)
            d.line_to(x0 + w - 700, VH)
            d.line_to(x0 - 700, VH)
            d.close_path()
            d.set_source_rgba(1, 1, 1, a)
            d.fill()
        d.set_source_rgba(0.9, 0.2, 0.3, 0.07)
        d.rectangle(0, VH - 220, VW, 220)
        d.fill()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def banner(c, T):
    c.set_source_rgb(*RED)
    c.rectangle(0, 0, VW, 190)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.25)
    c.rectangle(0, 190, VW, 10)
    c.fill()
    for i in range(19):
        x = 28 + i * 56.5
        on = (int(T * 6) + i) % 3 == 0
        for y in (22, 168):
            c.arc(x, y, 8, 0, 2 * math.pi)
            c.set_source_rgba(1, 0.95, 0.6, 1 if on else 0.35)
            c.fill()
    txt(c, "BLACK FRIDAY", VW / 2, 128, 112, (1, 1, 1))


def tag(c, px, py, L, ang, was="$139", now="$119", scale=1.0, circle=0.0, cross=0.0, hole_y=None):
    c.save()
    c.translate(px, py)
    c.rotate(ang)
    c.scale(scale, scale)
    c.set_source_rgba(0.95, 0.9, 0.7, 0.9)
    c.set_line_width(5)
    c.move_to(0, 0)
    c.line_to(0, L)
    c.stroke()
    w, h = 520, 400
    c.save()
    c.translate(-w / 2 + 14, L + 14)
    rrect(c, 0, 0, w, h, 36)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.fill()
    c.restore()
    rrect(c, -w / 2, L, w, h, 36)
    c.set_source_rgb(*CREAM)
    c.fill()
    c.arc(0, L + 42, 17, 0, 2 * math.pi)
    c.set_source_rgb(*NIGHT0)
    c.fill()
    txt(c, "BLACK FRIDAY DEAL", 0, L + 112, 31, (0.35, 0.3, 0.2), B)
    wy = L + 190
    wd = txt(c, "WAS " + was, 0, wy, 62, (0.35, 0.33, 0.3))
    if cross > 0:
        c.set_source_rgba(*RED, 1)
        c.set_line_width(10)
        c.move_to(-wd / 2 - 12, wy - 22)
        c.line_to(-wd / 2 - 12 + (wd + 24) * cross, wy - 22 - 6 * cross)
        c.stroke()
    if circle > 0:
        c.set_source_rgba(*RED, 1)
        c.set_line_width(9)
        c.save()
        c.translate(0, wy - 20)
        c.scale(wd / 2 + 36, 40)
        c.arc(0, 0, 1, -math.pi * 0.6, -math.pi * 0.6 + 2 * math.pi * 1.05 * circle)
        c.restore()
        c.stroke()
    txt(c, "NOW", 0, L + 246, 34, RED)
    txt(c, now, 0, L + 376, 150, RED)
    c.restore()


def strip(c, y, h, k, sale=True, glow=0.0):
    x0, bw, gap = 72, 14, 4
    for i in range(52):
        x = x0 + i * (bw + gap)
        lit = (i + 1) / 52 <= k
        if i in (45, 46, 47, 48):
            col = RED
        elif i in (8, 9, 20, 21, 22, 33, 41, 42):
            col = AMBER
        else:
            col = GREEN
        a = 0.95 if lit else 0.16
        if i in (45, 46, 47, 48) and lit and glow:
            c.set_source_rgba(*RED, 0.35 * glow)
            c.rectangle(x - 6, y - 14, bw + 12, h + 28)
            c.fill()
        rrect(c, x, y, bw, h, 5)
        c.set_source_rgba(*col, a)
        c.fill()
    txt(c, "JAN", x0, y + h + 44, 30, (1, 1, 1), B, "l", 0.7)
    txt(c, "DEC", x0 + 52 * 18 - gap, y + h + 44, 30, (1, 1, 1), B, "r", 0.7)
    txt(c, "GREEN = SAME OR CHEAPER THAN THE SALE PRICE", VW / 2, y + h + 100, 28, GREEN, B, "c", 0.9 * e(k, 0.2, 0.4))
    if sale and k > 0.92:
        txt(c, "THE SALE", x0 + 47 * 18, y - 22, 30, RED, B, "c", e(k, 0.92, 1.0))


def caption(c, s, a):
    ls = wrap(c, s, 900, 66)
    y0 = 1385 - (len(ls) - 1) * 40
    for i, ln in enumerate(ls):
        txt(c, ln, VW / 2, y0 + i * 80, 66, (1, 1, 1), a=a, stroke=(0, 0, 0), sw=14)


def pill(c, cx, cy, w, h, col, a=1.0):
    rrect(c, cx - w / 2, cy - h / 2, w, h, h / 2)
    c.set_source_rgba(*col, a)
    c.fill()


def tv(c, t):
    cx, cy = VW / 2, 640
    rrect(c, cx - 330, cy - 200, 660, 400, 26)
    c.set_source_rgb(0.05, 0.06, 0.09)
    c.fill_preserve()
    c.set_source_rgb(0.5, 0.52, 0.58)
    c.set_line_width(10)
    c.stroke()
    g = cairo.LinearGradient(cx - 300, cy - 180, cx + 300, cy + 180)
    g.add_color_stop_rgb(0, 0.18, 0.32, 0.62)
    g.add_color_stop_rgb(1, 0.05, 0.10, 0.28)
    rrect(c, cx - 310, cy - 180, 620, 360, 14)
    c.set_source(g)
    c.fill()
    c.move_to(cx - 310, cy + 40)
    c.line_to(cx - 60, cy - 180)
    c.line_to(cx + 40, cy - 180)
    c.line_to(cx - 210, cy + 180)
    c.close_path()
    c.set_source_rgba(1, 1, 1, 0.06)
    c.fill()
    c.set_source_rgb(0.5, 0.52, 0.58)
    c.rectangle(cx - 20, cy + 200, 40, 50)
    c.fill()
    rrect(c, cx - 140, cy + 246, 280, 18, 9)
    c.fill()
    txt(c, "-$40", cx, cy + 30, 150, (1, 1, 1), a=e(t, 0.1, 0.5))
    sc = back(e(t, 0.0, 0.5))
    c.save()
    c.translate(cx + 290, cy - 210)
    c.rotate(0.22)
    c.scale(max(sc, 0.001), max(sc, 0.001))
    starburst(c, 0, 0, 120, 92, 14)
    c.set_source_rgb(*RED)
    c.fill()
    txt(c, "DOOR", 0, -8, 40, (1, 1, 1))
    txt(c, "BUSTER", 0, 34, 40, (1, 1, 1))
    c.restore()
    n = 20 - int(e(t, 0.8, 2.2) * 3)
    pill(c, cx, 1010, 660, 96, RED, e(t, 0.4, 0.8))
    txt(c, "ONLY %d IN STOCK" % n, cx, 1042, 58, (1, 1, 1), a=e(t, 0.4, 0.8))


def cart(c, t):
    cx, cy = VW / 2, 700
    items = [("HDMI", "$29", (0.35, 0.65, 0.95), -150, 0.3), ("MOUNT", "$35", (0.95, 0.65, 0.3), 0, 0.8), ("CASE", "$19", (0.6, 0.9, 0.6), 150, 1.3)]
    for lab, pr, col, dx, t0 in items:
        k = e(t, t0, t0 + 0.5)
        y = cy - 330 + 330 * k - 30 * math.sin(k * math.pi)
        a = e(t, t0, t0 + 0.15)
        c.save()
        c.translate(cx + dx, y)
        c.rotate((1 - k) * 0.4 * (1 if dx >= 0 else -1))
        rrect(c, -62, -50, 124, 100, 12)
        c.set_source_rgba(*col, a)
        c.fill()
        txt(c, pr, 0, 12, 40, INK, a=a)
        c.restore()
    pill(c, cx, cy - 300, 560, 80, RED, e(t, 0.3, 0.7))
    txt(c, "FULL-PRICE EXTRAS", cx, cy - 273, 44, (1, 1, 1), a=e(t, 0.3, 0.7))
    c.set_source_rgb(0.85, 0.87, 0.92)
    c.set_line_width(14)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(cx - 400, cy - 160)
    c.line_to(cx - 330, cy - 160)
    c.line_to(cx - 260, cy + 120)
    c.line_to(cx + 280, cy + 120)
    c.line_to(cx + 350, cy - 100)
    c.line_to(cx - 330, cy - 100)
    c.stroke()
    for wx in (cx - 200, cx + 200):
        c.arc(wx, cy + 190, 32, 0, 2 * math.pi)
        c.fill()
    total = int(29 * e(t, 0.5, 0.9) + 35 * e(t, 1.0, 1.4) + 19 * e(t, 1.5, 1.9))
    pill(c, cx, 1010, 500, 100, (0.12, 0.16, 0.30), 1)
    txt(c, "EXTRAS: +$%d" % total, cx, 1045, 58, AMBER)


def clock(c, t):
    cx, cy = VW / 2, 680
    rrect(c, cx - 360, cy - 170, 720, 340, 40)
    c.set_source_rgb(0.04, 0.05, 0.08)
    c.fill_preserve()
    c.set_source_rgba(*RED, 0.6 + 0.4 * math.sin(t * 8))
    c.set_line_width(10)
    c.stroke()
    secs = int(10800 - e(t, 0, 2.4) * 10600 - 60)
    s = "%02d:%02d:%02d" % (secs // 3600, secs // 60 % 60, secs % 60)
    txt(c, s, cx, cy + 50, 140, RED, M, a=0.95)
    txt(c, "SALE ENDS IN", cx, cy - 100, 40, (1, 1, 1), B, a=0.85)
    pill(c, cx, 1010, 700, 96, AMBER, e(t, 1.0, 1.4))
    txt(c, "HURRY. DON'T COMPARE.", cx, 1042, 52, INK, a=e(t, 1.0, 1.4))


def receipt(c, t):
    x, y, w = 180, 270, 720
    h = 760
    c.move_to(x, y)
    c.line_to(x + w, y)
    n = 24
    c.line_to(x + w, y + h)
    for i in range(n):
        c.line_to(x + w - (i + 0.5) * w / n, y + h + 20)
        c.line_to(x + w - (i + 1) * w / n, y + h)
    c.close_path()
    c.set_source_rgba(0, 0, 0, 0.3)
    c.save()
    c.translate(12, 14)
    c.fill_preserve()
    c.restore()
    c.set_source_rgb(0.99, 0.98, 0.94)
    c.fill()
    txt(c, "EXAMPLE BASKET", x + w / 2, y + 80, 52, INK)
    c.set_source_rgba(0.1, 0.1, 0.15, 0.5)
    c.set_dash([14, 10])
    c.set_line_width(4)
    c.move_to(x + 40, y + 120)
    c.line_to(x + w - 40, y + 120)
    c.stroke()
    c.set_dash([])
    rows = [("TV DEAL SAVING", "-$40", (0.1, 0.55, 0.3)), ("HDMI CABLE", "+$29", INK), ("WALL MOUNT", "+$35", INK), ("WARRANTY", "+$49", INK)]
    for i, (a, b, col) in enumerate(rows):
        k = e(t, 0.15 + i * 0.35, 0.35 + i * 0.35)
        yy = y + 200 + i * 92
        txt(c, a, x + 50, yy, 40, col, M, "l", k)
        txt(c, b, x + w - 50, yy, 48, col, M, "r", k)
    k = e(t, 1.7, 2.0)
    c.set_source_rgba(0.1, 0.1, 0.15, 0.7 * k)
    c.set_line_width(5)
    c.move_to(x + 40, y + 560)
    c.line_to(x + w - 40, y + 560)
    c.stroke()
    pul = 0.5 + 0.5 * math.sin(t * 9)
    if k > 0:
        rrect(c, x + 30, y + 590, w - 60, 130, 20)
        c.set_source_rgba(*AMBER, k * (0.85 + 0.15 * pul))
        c.fill()
        txt(c, "NET: +$73 SPENT", x + w / 2, y + 678, 62, INK, a=k)


def endcard(c, t):
    a = e(t, 0, 0.4)
    c.set_source_rgba(0.03, 0.05, 0.13, 0.985 * a)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    logo(c, VW / 2 - 150, 560, 5.0, a)
    txt(c, "MONEY MAP", VW / 2, 1010, 110, (1, 1, 1), a=a)
    txt(c, "FOLLOW THE MONEY.", VW / 2, 1110, 62, GOLD, a=e(t, 0.3, 0.7))
    pill(c, VW / 2, 1240, 640, 100, GOLD, e(t, 0.5, 0.9))
    txt(c, "FOLLOW FOR MORE", VW / 2, 1273, 54, INK, a=e(t, 0.5, 0.9))


def draw(c, tl, T, cap=True):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0, T - t0)
    sc, line = LINES[i]
    bg(c)
    banner(c, T)
    ang = 0.2 * math.exp(-0.9 * T) * math.cos(2 * math.pi * 0.85 * T)
    if sc == "hook":
        tag(c, VW / 2, 200, 300, ang, scale=1.12)
        txt(c, "CHEAPER ON", VW / 2, 1070, 84, (1, 0.9, 0.4), stroke=(0, 0, 0), sw=12)
        txt(c, "OTHER DAYS?", VW / 2, 1160, 84, (1, 0.9, 0.4), stroke=(0, 0, 0), sw=12)
    elif sc == "track":
        k = e(t, 0.3, 3.6)
        day = int(365 * k)
        txt(c, "1 YEAR OF PRICES", VW / 2, 330, 76, (1, 1, 1))
        rrect(c, VW / 2 - 300, 400, 600, 300, 36)
        c.set_source_rgba(0.04, 0.05, 0.1, 0.8)
        c.fill()
        txt(c, "DAY", VW / 2, 480, 44, (1, 1, 1), B, a=0.7)
        txt(c, str(max(1, day)), VW / 2, 640, 190, GREEN, M)
        txt(c, "CHECKED DAILY", VW / 2, 790, 46, (1, 1, 1), B, a=0.8)
        strip(c, 940, 150, k, True, e(t, 3.4, 3.9))
    elif sc in ("pct",):
        strip(c, 940, 150, 1.0, True, 1.0)
        v = int(83 * e(t, 0, 1.5))
        txt(c, "%d%%" % v, VW / 2, 560, 330, GREEN, stroke=(0, 0, 0), sw=14)
        txt(c, "SAME OR CHEAPER AT", VW / 2, 700, 58, (1, 1, 1), a=e(t, 0.8, 1.2))
        txt(c, "LEAST ONCE OUTSIDE", VW / 2, 775, 58, (1, 1, 1), a=e(t, 0.8, 1.2))
        txt(c, "THE SALE", VW / 2, 850, 58, (1, 1, 1), a=e(t, 0.8, 1.2))
    elif sc == "how":
        tag(c, VW / 2, 200, 300, ang * 0.3, scale=1.12, circle=e(t, 0.15, 0.7), cross=e(t, 0.8, 1.2))
        txt(c, "HOW DOES THE", VW / 2, 1090, 78, (1, 0.9, 0.4), stroke=(0, 0, 0), sw=12)
        txt(c, "STORE STILL WIN?", VW / 2, 1180, 78, (1, 0.9, 0.4), stroke=(0, 0, 0), sw=12)
    elif sc in ("r1", "r2", "r3"):
        n = int(sc[1])
        sh = back(e(t, 0, 0.35))
        c.save()
        c.translate(VW / 2, 295)
        c.scale(max(sh, 0.001), max(sh, 0.001))
        c.arc(0, 0, 56, 0, 2 * math.pi)
        c.set_source_rgb(*GOLD)
        c.fill()
        txt(c, str(n), 0, 26, 76, INK)
        c.restore()
        {"r1": tv, "r2": cart, "r3": clock}[sc](c, t)
    elif sc == "receipt":
        receipt(c, t)
    elif sc == "close":
        tag(c, VW / 2, 200, 300, ang * 0.5, scale=1.12)
        k = e(t, 0.2, 0.55)
        c.save()
        c.translate(VW / 2 + 190, 1010)
        c.rotate(-0.1)
        c.scale(max(k, 0.001), max(k, 0.001))
        c.set_source_rgba(0, 0, 0, 0.3)
        c.rectangle(-258, -98, 520, 200)
        c.fill()
        c.set_source_rgb(1, 0.92, 0.35)
        c.rectangle(-270, -110, 520, 200)
        c.fill()
        txt(c, "CHECK THE", -10, -22, 60, INK)
        txt(c, "PRICE HISTORY", -10, 50, 60, INK)
        c.restore()
        if t > d - 2.0:
            endcard(c, t - (d - 2.0))
    if sc != "close" or t < d - 2.0:
        caption(c, line, 1.0 if i == 0 else e(t, 0, 0.15))


def build(durs, gap=0.4):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + gap + (2.1 if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def tts(out="vo_short"):
    from kokoro_onnx import Kokoro
    k = Kokoro('/root/kokoro/kokoro-v1.0.onnx', '/root/kokoro/voices-v1.0.bin')
    os.makedirs(out, exist_ok=True)
    durs = []
    for i, (_, line) in enumerate(LINES):
        a, sr = k.create(line, voice=VOICE, speed=SPEED, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 300): nz[-1] + 2000]
        sf.write(os.path.join(out, "%02d.wav" % i), a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open(os.path.join(out, "durs.json"), "w"))
    print(durs, sum(durs))


def srt(path):
    durs = json.load(open("vo_short/durs.json"))
    tl, total = build(durs)
    f = lambda s: "%02d:%02d:%02d,%03d" % (s // 3600, s // 60 % 60, int(s) % 60, int((s % 1) * 1000))
    with open(path, "w") as o:
        for i, ((t0, d), (_, line)) in enumerate(zip(tl, LINES)):
            o.write("%d\n%s --> %s\n%s\n\n" % (i + 1, f(t0 + 0.05), f(t0 + d - 0.05), line))


def render(out):
    durs = json.load(open("vo_short/durs.json"))
    tl, total = build(durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "short_v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        draw(c, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    sr = 24000
    n = int((total + 0.3) * sr)
    mix = np.zeros(n)
    rng = np.random.RandomState(11)
    tt = np.arange(n) / sr
    for fr, amp in ((98.0, 1), (146.8, 0.6), (196.0, 0.4)):
        mix += 0.012 * amp * np.sin(2 * np.pi * fr * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * tt / 5))
    for i, (t0, dd) in enumerate(tl):
        a, _ = sf.read("vo_short/%02d.wav" % i)
        j = int((t0 + 0.02) * sr)
        mix[j:j + len(a)] += a[:n - j]
        m = int(0.3 * sr)
        sc = rng.randn(m) * np.exp(-np.arange(m) / (0.08 * sr)) * 0.03
        sc = sc - np.convolve(sc, np.ones(5) / 5, mode="same")
        mix[j:j + m] += sc[:n - j]
    t_rec = tl[7][0]
    for k_ in range(4):
        j = int((t_rec + 0.15 + k_ * 0.35) * sr)
        m = int(0.08 * sr)
        tk = np.sin(2 * np.pi * 1800 * np.arange(m) / sr) * np.exp(-np.arange(m) / (0.02 * sr)) * 0.06
        mix[j:j + m] += tk[:n - j]
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    sf.write("short_a.wav", mix.astype(np.float32), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "short_v.tmp.mp4", "-i", "short_a.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    print("ok", total)


def stills():
    durs = json.load(open("vo_short/durs.json"))
    tl, total = build(durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, (t0, d) in enumerate(tl):
        for k, off in enumerate((0.02, min(2.2, d - 0.3))):
            draw(c, tl, t0 + off)
            surf.write_to_png("sst_%02d_%d.png" % (i, k))
    draw(c, tl, total - 0.5)
    surf.write_to_png("sst_end.png")


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    bg(c)
    banner(c, 0.1)
    txt(c, "IS THIS THE", VW / 2, 360, 104, (1, 1, 1), stroke=(0, 0, 0), sw=14)
    txt(c, "LOWEST PRICE", VW / 2, 480, 104, (1, 0.9, 0.4), stroke=(0, 0, 0), sw=14)
    txt(c, "OF THE YEAR?", VW / 2, 600, 104, (1, 1, 1), stroke=(0, 0, 0), sw=14)
    c.arc(VW / 2, 700, 14, 0, 2 * math.pi)
    c.set_source_rgb(0.8, 0.8, 0.85)
    c.fill()
    tag(c, VW / 2, 700, 110, -0.06, scale=1.05)
    strip(c, 1250, 120, 0.0, False)
    for i in range(52):
        if i in (45, 46, 47, 48):
            rrect(c, 72 + i * 18, 1250, 14, 120, 5)
            c.set_source_rgb(*RED)
            c.fill()
    txt(c, "?", VW / 2, 1220, 70, (1, 1, 1), a=0.0)
    surf.write_to_png(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"tts": lambda: tts(), "stills": lambda: stills(), "render": lambda: render(sys.argv[2]), "cover": lambda: cover(sys.argv[2]), "srt": lambda: srt(sys.argv[2])}[cmd]()
