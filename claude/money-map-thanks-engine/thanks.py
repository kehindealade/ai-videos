import cairo, math, os, sys, subprocess, random
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
from common import *

DUR = 35.0
BEAT = DUR / 64.0
CREAM = (0.97, 0.93, 0.82)
KRAFT = (0.91, 0.76, 0.50)
BROWN = (0.20, 0.10, 0.05)
ORANGE = (0.90, 0.42, 0.10)
DEEP = (0.62, 0.20, 0.10)
SAGE = (0.55, 0.64, 0.38)
DROP = 0.30
LOCK = BEAT * 28
PL0 = BEAT * 30
P1, P2, P3, END = BEAT * 36, BEAT * 44, BEAT * 52, BEAT * 58

ROWS = [790, 925, 1060]
COLS = [300, 540, 780]
SC = 0.72
ORANGE_TXT = (0.70, 0.22, 0.03)
CARD_Y = 1255
BOARD_Y = 385
_SPEC = [
    ("stuffing", 0, 0, 3.91, "$3.91"),
    ("sweet", 1, 0, 4.20, "$4.20"),
    ("rolls", 2, 0, 3.81, "$3.81"),
    ("peas", 0, 1, 1.99, "$1.99"),
    ("cran", 1, 1, 2.48, "$2.48"),
    ("veggie", 2, 1, 1.31, "$1.31"),
    ("pie", 0, 2, 9.36, "PIE $9.36"),
    ("milk", 1, 2, 4.05, "$4.05"),
    ("misc", 2, 2, 3.84, "MISC. $3.84"),
]
D = [dict(name="turkey", x=540, y=560, price=23.68, label="TURKEY $23.68", land=DROP, pill=BEAT * 6, ty=660)]
for i, (n, ci, ri, p, lab) in enumerate(_SPEC):
    land = BEAT * (10 + 2 * i)
    D.append(dict(name=n, x=COLS[ci], y=ROWS[ri], price=p, label=lab, land=land, pill=land, ty=ROWS[ri] + 58))
TOTAL = round(sum(d["price"] for d in D), 2)
assert abs(TOTAL - 58.63) < 1e-6, TOTAL
SHADOW = {"turkey": (212, 110), "milk": (50, 60), "veggie": (74, 56), "misc": (84, 56)}
PLATES = []
for k in range(5):
    PLATES.append((95, 520 + 130 * k))
    PLATES.append((985, 520 + 130 * k))
_BG = None
_SP = {}


def leaf(c, x, y, ang, s, col, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s * 0.55, s)
    c.move_to(0, -1)
    c.curve_to(0.9, -0.5, 0.9, 0.5, 0, 1)
    c.curve_to(-0.9, 0.5, -0.9, -0.5, 0, -1)
    c.set_source_rgba(*col, a)
    c.fill()
    c.set_line_width(0.05)
    c.set_source_rgba(0, 0, 0, 0.25 * a)
    c.move_to(0, -1)
    c.line_to(0, 1.15)
    c.stroke()
    c.restore()


LEAVES = [(40, 430, 0.6, 52, (0.85, 0.35, 0.10)), (75, 1560, 2.1, 60, (0.78, 0.18, 0.12)), (1030, 1530, 1.0, 55, (0.93, 0.62, 0.15)),
          (1010, 400, 2.6, 50, (0.72, 0.25, 0.08)), (230, 1610, 0.2, 58, (0.90, 0.50, 0.12)), (880, 1640, 1.7, 52, (0.80, 0.30, 0.10)),
          (540, 1720, 0.9, 62, (0.88, 0.45, 0.10)), (300, 1790, 2.4, 55, (0.70, 0.20, 0.10)), (780, 1800, 0.4, 56, (0.93, 0.62, 0.15)),
          (100, 1740, 1.4, 50, (0.92, 0.55, 0.12)), (985, 1760, 2.9, 54, (0.78, 0.22, 0.10)), (60, 300, 1.9, 46, (0.93, 0.62, 0.15)),
          (1020, 290, 0.3, 48, (0.82, 0.32, 0.10)), (210, 1480, 1.2, 40, (0.85, 0.40, 0.10)), (870, 1470, 2.0, 42, (0.72, 0.22, 0.08))]


def pumpkin(c, x, y, r):
    for k, dx in enumerate((-0.55, 0, 0.55)):
        c.save()
        c.translate(x + dx * r * 0.7, y)
        c.scale(0.62 + 0.0 * k, 1)
        c.arc(0, 0, r, 0, 2 * math.pi)
        c.set_source_rgb(0.92 - 0.04 * abs(dx), 0.50 - 0.05 * abs(dx), 0.10)
        c.fill()
        c.restore()
    c.set_source_rgb(0.30, 0.38, 0.15)
    c.set_line_width(r * 0.18)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x, y - r * 0.9)
    c.curve_to(x + r * 0.1, y - r * 1.2, x + r * 0.3, y - r * 1.25, x + r * 0.35, y - r * 1.15)
    c.stroke()


def plate(d, x0, y0, sc=0.6):
    d.save()
    d.translate(x0, y0)
    d.scale(sc, sc)
    x, y = 0, 0
    d.arc(x + 8, y + 12, 98, 0, 2 * math.pi)
    d.set_source_rgba(0, 0, 0, 0.30)
    d.fill()
    for ang, col in ((0.5, (0.86, 0.42, 0.13)), (1.28, (0.78, 0.34, 0.10))):
        d.save()
        d.translate(x, y)
        d.rotate(ang)
        rrect(d, -88, -88, 176, 176, 10)
        d.set_source_rgb(*col)
        d.fill()
        d.restore()
    g = cairo.RadialGradient(x - 25, y - 25, 10, x, y, 100)
    g.add_color_stop_rgb(0, 1, 1, 0.99)
    g.add_color_stop_rgb(1, 0.88, 0.88, 0.86)
    d.arc(x, y, 96, 0, 2 * math.pi)
    d.set_source(g)
    d.fill()
    d.arc(x, y, 70, 0, 2 * math.pi)
    d.set_source_rgb(0.80, 0.80, 0.78)
    d.set_line_width(3)
    d.stroke()
    d.arc(x, y, 66, 0, 2 * math.pi)
    d.set_source_rgb(0.97, 0.97, 0.95)
    d.fill()
    d.restore()


def bg(c):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        rng = random.Random(7)
        for i in range(9):
            x = i * 120
            sh = rng.uniform(-0.04, 0.04)
            d.set_source_rgb(0.37 + sh, 0.21 + sh * 0.6, 0.11 + sh * 0.4)
            d.rectangle(x, 0, 120, VH)
            d.fill()
            for j in range(10):
                gx = x + rng.uniform(8, 112)
                d.set_source_rgba(0, 0, 0, rng.uniform(0.05, 0.13))
                d.set_line_width(rng.uniform(1.5, 3.2))
                d.move_to(gx, 0)
                for y in range(0, VH + 40, 40):
                    d.line_to(gx + math.sin(y * 0.01 + j) * 3 + rng.uniform(-1, 1), y)
                d.stroke()
            d.set_source_rgba(0, 0, 0, 0.5)
            d.rectangle(x, 0, 3, VH)
            d.fill()
        for _ in range(7):
            kx, ky = rng.uniform(0, VW), rng.uniform(0, VH)
            d.save()
            d.translate(kx, ky)
            d.scale(1, 2.2)
            d.arc(0, 0, rng.uniform(10, 20), 0, 2 * math.pi)
            d.set_source_rgba(0.12, 0.06, 0.02, 0.18)
            d.fill()
            d.restore()
        d.set_source_rgba(0, 0, 0, 0.28)
        d.rectangle(188, 0, 12, VH)
        d.fill()
        d.rectangle(880, 0, 12, VH)
        d.fill()
        d.set_source_rgb(*CREAM)
        d.rectangle(200, 0, 680, VH)
        d.fill()
        d.set_line_width(1)
        for x in range(200, 880, 6):
            d.set_source_rgba(0.5, 0.4, 0.25, 0.05)
            d.move_to(x, 0)
            d.line_to(x, VH)
            d.stroke()
        for y in range(0, VH, 6):
            d.set_source_rgba(0.5, 0.4, 0.25, 0.05)
            d.move_to(200, y)
            d.line_to(880, y)
            d.stroke()
        d.set_source_rgb(0.84, 0.38, 0.11)
        d.rectangle(200, 0, 24, VH)
        d.fill()
        d.rectangle(856, 0, 24, VH)
        d.fill()
        d.set_source_rgba(0.35, 0.14, 0.05, 0.6)
        d.set_line_width(3)
        for x in (232, 848):
            d.move_to(x, 0)
            d.line_to(x, VH)
            d.stroke()
        for (x, y) in PLATES:
            plate(d, x, y)
        pumpkin(d, 400, 215, 42)
        pumpkin(d, 700, 235, 36)
        pumpkin(d, 400, 1590, 44)
        pumpkin(d, 690, 1620, 38)
        pumpkin(d, 540, 1775, 40)
        for (lx, ly, la, ls, lc) in LEAVES:
            leaf(d, lx, ly, la, ls, lc)
        g = cairo.RadialGradient(540, 960, 500, 540, 960, 1250)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.38)
        d.set_source(g)
        d.paint()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def new(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s)
    c.translate(w / 2, h / 2)
    return s, c


def bowl(c, r, rim=(0.97, 0.96, 0.93)):
    c.arc(0, 0, r, 0, 2 * math.pi)
    c.set_source_rgb(*rim)
    c.fill_preserve()
    c.set_source_rgb(0.70, 0.70, 0.68)
    c.set_line_width(2)
    c.stroke()
    c.arc(0, 0, r - 9, 0, 2 * math.pi)
    c.set_source_rgb(0.86, 0.84, 0.80)
    c.fill()


def in_circle(rng, R):
    while True:
        x, y = rng.uniform(-R, R), rng.uniform(-R, R)
        if x * x + y * y <= R * R:
            return x, y


def shine(c, R, a=0.14):
    g = cairo.RadialGradient(-R * 0.35, -R * 0.4, 2, 0, 0, R * 1.2)
    g.add_color_stop_rgba(0, 1, 1, 1, a)
    g.add_color_stop_rgba(1, 0, 0, 0, a * 0.8)
    c.arc(0, 0, R, 0, 2 * math.pi)
    c.set_source(g)
    c.fill()


def build(name):
    rng = random.Random(hash(name) % 1000 + 5 if False else sum(map(ord, name)))
    if name == "turkey":
        s, c = new(480, 300)
        c.save()
        c.scale(1, 112 / 212)
        c.arc(0, 0, 212, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgb(0.99, 0.99, 0.97)
        c.fill()
        for rx, ry, col, lw in ((200, 103, (0.85, 0.70, 0.35), 3), (190, 94, (0.80, 0.80, 0.78), 2)):
            c.save()
            c.scale(1, ry / rx)
            c.arc(0, 0, rx, 0, 2 * math.pi)
            c.restore()
            c.set_source_rgb(*col)
            c.set_line_width(lw)
            c.stroke()
        c.save()
        c.scale(1, 94 / 190)
        c.arc(0, 0, 188, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgb(0.96, 0.95, 0.92)
        c.fill()
        for i in range(18):
            a = i / 18 * 2 * math.pi
            leaf(c, 168 * math.cos(a), 78 * math.sin(a), a + 1.2, 16, (0.25 + 0.1 * (i % 3), 0.50 + 0.05 * (i % 2), 0.18))
        for (bx, by) in ((-150, -30), (150, -30), (-120, 62), (125, 60)):
            for k in range(4):
                c.arc(bx + rng.uniform(-14, 14), by + rng.uniform(-9, 9), 8, 0, 2 * math.pi)
                c.set_source_rgb(0.75, 0.08, 0.16)
                c.fill()
        for (ox, oy) in ((-30, -88), (60, 84), (-70, 80)):
            c.arc(ox, oy, 15, 0, 2 * math.pi)
            c.set_source_rgb(0.98, 0.62, 0.10)
            c.fill_preserve()
            c.set_source_rgb(1.0, 0.86, 0.45)
            c.set_line_width(3)
            c.stroke()
        for (ang, sx) in ((-0.6, -80), (0.6, 80)):
            c.save()
            c.translate(sx, 50)
            c.rotate(ang)
            c.save()
            c.scale(1, 22 / 42)
            c.arc(0, 0, 42, 0, 2 * math.pi)
            c.restore()
            g = cairo.RadialGradient(-8, -6, 3, 0, 0, 42)
            g.add_color_stop_rgb(0, 0.88, 0.52, 0.18)
            g.add_color_stop_rgb(1, 0.55, 0.26, 0.07)
            c.set_source(g)
            c.fill()
            c.arc(0, 40 if sx > 0 else 40, 0, 0, 0)
            c.restore()
            c.save()
            c.translate(sx + (-1 if sx < 0 else 1) * 38 * math.cos(abs(ang)) * 0.5, 50 + 34 * math.sin(abs(ang)) * 0.6)
            c.arc(-5, 0, 9, 0, 2 * math.pi)
            c.arc(5, 0, 9, 0, 2 * math.pi)
            c.set_source_rgb(0.99, 0.97, 0.90)
            c.fill()
            c.restore()
        c.save()
        c.translate(0, -8)
        c.save()
        c.scale(1, 66 / 128)
        c.arc(0, 0, 128, 0, 2 * math.pi)
        c.restore()
        g = cairo.RadialGradient(-30, -22, 8, 0, 0, 130)
        g.add_color_stop_rgb(0, 0.93, 0.62, 0.25)
        g.add_color_stop_rgb(0.7, 0.74, 0.40, 0.12)
        g.add_color_stop_rgb(1, 0.54, 0.26, 0.07)
        c.set_source(g)
        c.fill_preserve()
        c.set_source_rgb(0.42, 0.19, 0.05)
        c.set_line_width(3)
        c.stroke()
        c.set_source_rgba(0.35, 0.15, 0.03, 0.35)
        c.set_line_width(3)
        c.move_to(0, -62)
        c.curve_to(10, -20, -10, 20, 0, 62)
        c.stroke()
        for (hx, hy, hw) in ((-60, -28, 50), (45, -34, 60), (-10, 10, 40), (70, 14, 34)):
            c.save()
            c.translate(hx, hy)
            c.scale(1, 0.38)
            c.arc(0, 0, hw * 0.5, 0, 2 * math.pi)
            c.restore()
            c.set_source_rgba(1, 0.85, 0.5, 0.30)
            c.fill()
        c.restore()
        return s
    if name in ("stuffing", "sweet", "peas", "cran"):
        s, c = new(180, 180)
        if name == "cran":
            c.arc(0, 0, 66, 0, 2 * math.pi)
            c.set_source_rgba(0.80, 0.90, 0.92, 0.95)
            c.fill_preserve()
            c.set_source_rgb(0.55, 0.70, 0.74)
            c.set_line_width(3)
            c.stroke()
            c.arc(0, 0, 56, 0, 2 * math.pi)
            c.set_source_rgb(0.50, 0.04, 0.12)
            c.fill()
        else:
            bowl(c, 66)
        c.arc(0, 0, 56, 0, 2 * math.pi)
        c.clip()
        if name == "stuffing":
            c.set_source_rgb(0.72, 0.50, 0.26)
            c.paint()
            for _ in range(95):
                x, y = in_circle(rng, 56)
                c.save()
                c.translate(x, y)
                c.rotate(rng.uniform(0, 3))
                sz = rng.uniform(9, 14)
                c.rectangle(-sz / 2, -sz / 2, sz, sz)
                c.set_source_rgb(*rng.choice([(0.88, 0.68, 0.40), (0.80, 0.57, 0.30), (0.70, 0.46, 0.22), (0.93, 0.78, 0.52)]))
                c.fill()
                c.restore()
            for _ in range(22):
                x, y = in_circle(rng, 52)
                c.arc(x, y, 2.6, 0, 2 * math.pi)
                c.set_source_rgb(0.30, 0.55, 0.20)
                c.fill()
            for _ in range(9):
                x, y = in_circle(rng, 52)
                c.arc(x, y, 3.2, 0, 2 * math.pi)
                c.set_source_rgb(0.92, 0.52, 0.14)
                c.fill()
        elif name == "sweet":
            c.set_source_rgb(0.80, 0.40, 0.10)
            c.paint()
            for k in range(16):
                a = k * 2.4
                rr = 8 + 36 * math.sqrt(k / 16.0)
                x, y = rr * math.cos(a), rr * math.sin(a)
                c.save()
                c.translate(x, y)
                c.rotate(a)
                rrect(c, -16, -14, 32, 28, 9)
                c.set_source_rgb(0.95, 0.55, 0.15)
                c.fill_preserve()
                c.set_source_rgb(0.68, 0.30, 0.06)
                c.set_line_width(2.5)
                c.stroke()
                c.arc(-4, -5, 4, 0, 2 * math.pi)
                c.set_source_rgba(1, 0.9, 0.7, 0.45)
                c.fill()
                c.restore()
            for _ in range(24):
                x, y = in_circle(rng, 50)
                c.arc(x, y, 1.8, 0, 2 * math.pi)
                c.set_source_rgb(0.45, 0.2, 0.05)
                c.fill()
        elif name == "peas":
            c.set_source_rgb(0.32, 0.55, 0.16)
            c.paint()
            for _ in range(150):
                x, y = in_circle(rng, 54)
                c.arc(x, y, 6.2, 0, 2 * math.pi)
                c.set_source_rgb(rng.uniform(0.35, 0.55), rng.uniform(0.66, 0.82), rng.uniform(0.18, 0.30))
                c.fill()
                c.arc(x - 1.8, y - 2, 1.6, 0, 2 * math.pi)
                c.set_source_rgba(1, 1, 0.9, 0.5)
                c.fill()
        else:
            for _ in range(70):
                x, y = in_circle(rng, 52)
                r = rng.uniform(8, 11)
                c.arc(x, y, r, 0, 2 * math.pi)
                c.set_source_rgb(rng.uniform(0.60, 0.80), rng.uniform(0.04, 0.10), rng.uniform(0.10, 0.20))
                c.fill()
                c.arc(x - 3, y - 3, 2.6, 0, 2 * math.pi)
                c.set_source_rgba(1, 0.75, 0.75, 0.55)
                c.fill()
        c.reset_clip()
        shine(c, 56, 0.12)
        return s
    if name == "rolls":
        s, c = new(180, 180)
        c.arc(0, 0, 66, 0, 2 * math.pi)
        c.set_source_rgb(0.60, 0.40, 0.20)
        c.fill()
        for r, al in ((22, 0.55), (36, 0.55), (50, 0.55), (62, 0.55)):
            c.arc(0, 0, r, 0, 2 * math.pi)
            c.set_source_rgba(0.40, 0.24, 0.10, al)
            c.set_line_width(4)
            c.stroke()
        for k in range(18):
            a = k / 18 * 2 * math.pi
            c.move_to(10 * math.cos(a), 10 * math.sin(a))
            c.line_to(64 * math.cos(a), 64 * math.sin(a))
            c.set_source_rgba(0.35, 0.2, 0.08, 0.28)
            c.set_line_width(2)
            c.stroke()
        c.arc(0, 0, 54, 0, 2 * math.pi)
        c.set_source_rgb(0.96, 0.92, 0.84)
        c.fill()
        pos = [(0, 0)] + [(28 * math.cos(k * math.pi / 3 + 0.4), 28 * math.sin(k * math.pi / 3 + 0.4)) for k in range(6)]
        for (x, y) in pos:
            g = cairo.RadialGradient(x - 5, y - 6, 2, x, y, 20)
            g.add_color_stop_rgb(0, 0.98, 0.80, 0.46)
            g.add_color_stop_rgb(1, 0.76, 0.48, 0.18)
            c.arc(x, y, 19, 0, 2 * math.pi)
            c.set_source(g)
            c.fill()
            c.move_to(x - 9, y - 4)
            c.curve_to(x - 3, y + 4, x + 4, y + 4, x + 10, y - 4)
            c.set_source_rgba(0.5, 0.28, 0.08, 0.4)
            c.set_line_width(2)
            c.stroke()
        return s
    if name == "veggie":
        s, c = new(180, 180)
        rrect(c, -74, -56, 148, 112, 16)
        c.set_source_rgb(0.97, 0.97, 0.95)
        c.fill_preserve()
        c.set_source_rgb(0.70, 0.70, 0.68)
        c.set_line_width(2)
        c.stroke()
        rrect(c, -64, -46, 128, 92, 10)
        c.set_source_rgb(0.90, 0.92, 0.90)
        c.fill()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(6):
            y = -36 + k * 13
            c.move_to(-50, y + 6)
            c.line_to(8, y - 4)
            c.set_source_rgb(0.70, 0.32, 0.05)
            c.set_line_width(13)
            c.stroke_preserve()
            c.set_source_rgb(0.96, 0.56, 0.12)
            c.set_line_width(9)
            c.stroke()
        for k in range(5):
            y = -30 + k * 14
            c.move_to(-50, y + 14)
            c.line_to(2, y + 6)
            c.set_source_rgb(0.45, 0.62, 0.25)
            c.set_line_width(13)
            c.stroke_preserve()
            c.set_source_rgb(0.68, 0.84, 0.46)
            c.set_line_width(9)
            c.stroke()
        c.arc(40, 8, 21, 0, 2 * math.pi)
        c.set_source_rgb(0.80, 0.80, 0.78)
        c.fill()
        c.arc(40, 8, 17, 0, 2 * math.pi)
        c.set_source_rgb(0.98, 0.97, 0.90)
        c.fill()
        return s
    if name == "pie":
        s, c = new(180, 180)
        c.arc(0, 0, 66, 0, 2 * math.pi)
        c.set_source_rgb(0.80, 0.80, 0.78)
        c.fill()
        c.arc(0, 0, 64, 0, 2 * math.pi)
        c.set_source_rgb(0.90, 0.65, 0.30)
        c.fill()
        for k in range(28):
            a = k / 28 * 2 * math.pi
            c.arc(62 * math.cos(a), 62 * math.sin(a), 7.5, 0, 2 * math.pi)
            c.set_source_rgb(0.86, 0.58, 0.24)
            c.fill_preserve()
            c.set_source_rgba(0.5, 0.28, 0.08, 0.5)
            c.set_line_width(1.5)
            c.stroke()
        g = cairo.RadialGradient(-10, -12, 4, 0, 0, 52)
        g.add_color_stop_rgb(0, 0.92, 0.55, 0.16)
        g.add_color_stop_rgb(1, 0.76, 0.36, 0.07)
        c.arc(0, 0, 52, 0, 2 * math.pi)
        c.set_source(g)
        c.fill()
        for _ in range(30):
            x, y = in_circle(rng, 46)
            c.arc(x, y, 1.6, 0, 2 * math.pi)
            c.set_source_rgba(0.40, 0.18, 0.05, 0.6)
            c.fill()
        for r, ox, oy in ((26, 0, 0), (19, 0, -4), (11, 0, -8)):
            c.arc(ox, oy, r, 0, 2 * math.pi)
            c.set_source_rgb(0.99, 0.99, 0.97)
            c.fill_preserve()
            c.set_source_rgba(0.6, 0.6, 0.58, 0.55)
            c.set_line_width(2)
            c.stroke()
        c.move_to(0, -12)
        c.curve_to(6, -20, 12, -14, 4, -8)
        c.set_source_rgba(0.55, 0.55, 0.52, 0.5)
        c.set_line_width(2)
        c.stroke()
        return s
    if name == "milk":
        s, c = new(180, 180)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(40, -34)
        c.curve_to(82, -34, 82, 38, 40, 38)
        c.set_source_rgb(0.62, 0.72, 0.86)
        c.set_line_width(14)
        c.stroke_preserve()
        c.set_source_rgb(0.94, 0.97, 1.0)
        c.set_line_width(9)
        c.stroke()
        rrect(c, -46, -56, 92, 112, 16)
        c.set_source_rgb(0.97, 0.98, 1.0)
        c.fill_preserve()
        c.set_source_rgb(0.62, 0.72, 0.86)
        c.set_line_width(3)
        c.stroke()
        rrect(c, -36, -4, 72, 40, 8)
        c.set_source_rgb(0.30, 0.52, 0.90)
        c.fill()
        txt(c, "MILK", 0, 25, 26, WHITE, H)
        c.arc(-16, -36, 17, 0, 2 * math.pi)
        c.set_source_rgb(0.20, 0.42, 0.85)
        c.fill_preserve()
        c.set_source_rgb(0.12, 0.30, 0.65)
        c.set_line_width(2.5)
        c.stroke()
        c.arc(-16, -36, 9, 0, 2 * math.pi)
        c.set_source_rgba(1, 1, 1, 0.3)
        c.fill()
        return s
    if name == "misc":
        s, c = new(200, 140)
        for (x, y, r, col, cap) in ((-62, 0, 24, (0.98, 0.98, 0.96), (0.78, 0.80, 0.84)), (0, -8, 24, (0.30, 0.26, 0.24), (0.78, 0.80, 0.84)),
                                    (62, 12, 28, (0.36, 0.58, 0.22), (0.95, 0.76, 0.20))):
            c.arc(x + 3, y + 5, r, 0, 2 * math.pi)
            c.set_source_rgba(0, 0, 0, 0.22)
            c.fill()
            c.arc(x, y, r, 0, 2 * math.pi)
            c.set_source_rgb(*col)
            c.fill_preserve()
            c.set_source_rgba(0, 0, 0, 0.35)
            c.set_line_width(2)
            c.stroke()
            c.arc(x, y, r * 0.58, 0, 2 * math.pi)
            c.set_source_rgb(*cap)
            c.fill()
            if r < 26:
                for k in range(5):
                    a = k * 1.256
                    c.arc(x + 5 * math.cos(a), y + 5 * math.sin(a), 1.6, 0, 2 * math.pi)
                    c.set_source_rgba(0.1, 0.1, 0.1, 0.7)
                    c.fill()
            c.arc(x - r * 0.3, y - r * 0.35, r * 0.18, 0, 2 * math.pi)
            c.set_source_rgba(1, 1, 1, 0.5)
            c.fill()
        return s


def sprite(name):
    if name not in _SP:
        _SP[name] = build(name)
    return _SP[name]


def blit(c, name, x, y, s=1.0, a=1.0):
    sp = sprite(name)
    w, h = sp.get_width(), sp.get_height()
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_surface(sp, -w / 2, -h / 2)
    c.paint_with_alpha(a)
    c.restore()


def tagw(c, s, size=32):
    font(c, M, True)
    c.set_font_size(size)
    return c.text_extents(s).width


def tag(c, x, y, s, k=1.0, a=1.0, size=32):
    if k <= 0.01:
        return
    w = tagw(c, s, size) + 62
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    rrect(c, -w / 2 + 3, -27 + 6, w, 54, 14)
    c.set_source_rgba(0, 0, 0, 0.3 * a)
    c.fill()
    rrect(c, -w / 2, -27, w, 54, 14)
    c.set_source_rgba(*KRAFT, a)
    c.fill_preserve()
    c.set_source_rgba(*BROWN, a)
    c.set_line_width(3)
    c.stroke()
    c.arc(-w / 2 + 20, 0, 6.5, 0, 2 * math.pi)
    c.set_source_rgba(0.30, 0.16, 0.08, a)
    c.fill()
    txt(c, s, 12, 11, size, BROWN, M, a=a)
    c.restore()


def ring(c, x, y, t, r0=50, r1=170, a0=0.5, w=8, col=(1, 1, 1)):
    if 0 <= t < 0.5:
        p = e(t, 0, 0.5)
        c.arc(x, y, r0 + (r1 - r0) * p, 0, 2 * math.pi)
        c.set_source_rgba(*col, a0 * (1 - p))
        c.set_line_width(w)
        c.stroke()


def dish(c, d, T):
    n = d["name"]
    land = d["land"]
    t = T - (land - DROP)
    if t < 0:
        return
    p = clamp(t / DROP)
    k = e(p, 0, 1)
    sc = 1 + 0.35 * (1 - k)
    a = min(1.0, 0.6 + 0.4 * p) if n == "turkey" else e(p, 0, 0.5)
    if p >= 1:
        tt = T - land
        sc = 1 + 0.04 * math.sin(tt * 22) * math.exp(-tt * 9)
    rx, ry = SHADOW.get(n, (68, 68))
    rx, ry = rx * SC, ry * SC
    off = 10 + 46 * (1 - k)
    c.save()
    c.translate(d["x"] + off, d["y"] + off * 1.3)
    c.scale(1, ry / rx)
    c.arc(0, 0, rx * sc * 0.97, 0, 2 * math.pi)
    c.restore()
    c.set_source_rgba(0, 0, 0, 0.30 * a * (0.55 + 0.45 * k))
    c.fill()
    blit(c, n, d["x"], d["y"], sc * SC, a)
    ring(c, d["x"], d["y"], T - land, 36 if n != "turkey" else 80, 110 if n != "turkey" else 230)


def total_at(T):
    return sum(d["price"] * e(T, d["pill"], d["pill"] + 0.45) for d in D)


def scramble(T):
    r = random.Random(int(T * 14) * 7919 + 3)
    return "$%.2f" % r.uniform(18, 98)


CARDS = [
    (0.0, ("THANKSGIVING FOR 10:", "WHAT'S THE BILL?")),
    (D[0]["pill"], ("TURKEY = 40% OF IT.", "NOW WATCH THE REST")),
    (BEAT * 9.5, ("SIDES, ROLLS, PIE...", "WATCH IT CLIMB")),
    (LOCK, ("THAT'S THE WHOLE", "DINNER FOR 10")),
    (PL0 + 0.0, ("THAT'S $5.86", "FOR EACH PERSON")),
]


def card(c, T, a=1.0, custom=None, sz=(62, 72)):
    lines, ts = None, 0
    for (t0, ln) in CARDS:
        if T >= t0:
            lines, ts = ln, t0
    if custom:
        lines, ts = custom, -9
    s = 0.90 + 0.10 * back(e(T - ts, 0, 0.3))
    c.save()
    c.translate(540, CARD_Y)
    c.scale(s, s)
    rrect(c, -444, -75, 900, 170, 26)
    c.set_source_rgba(0, 0, 0, 0.35 * a)
    c.fill()
    rrect(c, -450, -85, 900, 170, 26)
    c.set_source_rgba(*CREAM, a)
    c.fill()
    c.save()
    rrect(c, -450, -85, 900, 170, 26)
    c.clip()
    c.set_source_rgba(0, 0, 0, 0.07 * a)
    c.rectangle(-450, 52, 900, 40)
    c.fill()
    c.restore()
    rrect(c, -440, -75, 880, 150, 20)
    c.set_source_rgba(*ORANGE, a)
    c.set_line_width(5)
    c.stroke()
    txt(c, lines[0], 0, -8, sz[0], BROWN, H, a=a)
    txt(c, lines[1], 0, 60, sz[1], ORANGE_TXT, H, a=a)
    c.restore()


def board(c, T, text, a=1.0, label="THE BILL"):
    pulse = max(0.0, 1 - abs(T - LOCK - 0.15) / 0.3) if LOCK - 0.15 < T < LOCK + 0.6 else 0.0
    pp = max(0.0, 1 - (T - PL0) / 0.3) if PL0 <= T < PL0 + 0.3 else 0.0
    k = 1 + 0.08 * pulse + 0.08 * pp
    c.save()
    c.translate(540, BOARD_Y)
    c.scale(k, k)
    rrect(c, -356, -59, 720, 130, 28)
    c.set_source_rgba(0, 0, 0, 0.3 * a)
    c.fill()
    rrect(c, -360, -65, 720, 130, 28)
    c.set_source_rgba(*BROWN, 0.97 * a)
    c.fill_preserve()
    c.set_source_rgba(*GOLD, a)
    c.set_line_width(5 + 5 * pulse)
    c.stroke()
    txt(c, label, -332, -30, 26, GOLD, H, align="l", a=a)
    txt(c, "AFBF SURVEY · NOV 2026", 332, -30, 22, GOLD, B, align="r", a=0.85 * a)
    txt(c, text, 0, 48, 100, CREAM if T >= LOCK else (0.95, 0.88, 0.7), M, a=a)
    c.restore()
    ring(c, 540, BOARD_Y, T - LOCK, 120, 520, 0.55, 8, GOLD)


def wordmark(c, a):
    logo(c, 395, 34, 0.5, a)
    txt(c, "MONEY MAP", 560, 66, 34, GOLD, H, a=a, stroke=BROWN, sw=7)


def scene(c, T, cover=False):
    bg(c)
    for d in D:
        if cover:
            dd = dict(d)
            dd["land"] = -5
            dish(c, dd, 5.0)
        else:
            dish(c, d, T)
    if not cover and not (P1 + 0.3 <= T < END):
        for d in D:
            k = back(e(T, d["pill"], d["pill"] + 0.3))
            tag(c, d["x"], d["ty"], d["label"], k, 1.0, 30 if d["name"] in ("pie", "misc") else 32)
        for i, (x, y) in enumerate(PLATES):
            t0 = PL0 + i * BEAT * 0.5
            k = back(e(T, t0, t0 + 0.28))
            if k > 0.01:
                ring(c, x, y, T - t0, 30, 100, 0.6, 5, GOLD)
                c.save()
                c.translate(x, y)
                c.scale(k, k)
                c.arc(0, 0, 46, 0, 2 * math.pi)
                c.set_source_rgb(*KRAFT)
                c.fill_preserve()
                c.set_source_rgb(*BROWN)
                c.set_line_width(4)
                c.stroke()
                txt(c, "$5.86", 0, 10, 27, BROWN, M)
                c.restore()


def leaves_big(c, a):
    for (lx, ly, la, ls, lc) in LEAVES:
        leaf(c, lx, ly, la, ls * 2.4, lc, 0.35 * a)


def panel1(c, t):
    txt(c, "VS. LAST YEAR", 540, 420, 78, GOLD, H, stroke=BROWN, sw=14, a=e(t, 0, 0.25))
    unit = 780 / TOTAL
    for (yy, lab, val, col, t0, t1) in ((540, "2025", 55.18, SAGE, 0.35, 1.1), (720, "2026", TOTAL, ORANGE, 0.9, 1.7)):
        g = e(t, t0, t1)
        if g <= 0:
            continue
        w = val * unit * g
        rrect(c, 110, yy + 6, w, 130, 18)
        c.set_source_rgba(0, 0, 0, 0.35)
        c.fill()
        rrect(c, 110, yy, w, 130, 18)
        c.set_source_rgb(*col)
        c.fill()
        if g > 0.5:
            ta = e(g, 0.5, 0.9)
            txt(c, lab, 140, yy + 88, 54, BROWN if lab == "2025" else WHITE, H, align="l", a=ta)
            txt(c, "$%.2f" % val, 110 + w - 24, yy + 88, 54, BROWN if lab == "2025" else WHITE, M, align="r", a=ta)
    b = back(e(t, 2.0, 2.4))
    if b > 0.01:
        c.save()
        c.translate(540, 1030)
        c.scale(b, b)
        rrect(c, -270, -110, 540, 220, 60)
        c.set_source_rgb(*GOLD)
        c.fill()
        txt(c, "+6%", 0, 60, 170, BROWN, H)
        c.restore()
        ring(c, 540, 1030, t - 2.0, 120, 340, 0.5, 8, GOLD)
    txt(c, "FIRST RISE SINCE 2022", 540, 1235, 42, CREAM, H, a=e(t, 2.5, 2.9), stroke=BROWN, sw=8)


def panel2(c, t):
    txt(c, "THE TURKEY", 540, 415, 80, GOLD, H, stroke=BROWN, sw=14, a=e(t, 0, 0.25))
    txt(c, "16-LB FROZEN BIRD", 540, 480, 48, CREAM, H, a=e(t, 0.1, 0.4), stroke=BROWN, sw=8)
    k = back(e(t, 0.2, 0.6))
    if k > 0.01:
        c.save()
        c.translate(540, 700)
        c.scale(k, k)
        c.translate(-540, -700)
        blit(c, "turkey", 540, 700, 1.0, 1.0)
        c.restore()
    tag(c, 300, 925, "2025 $21.50", back(e(t, 0.8, 1.15)) * 1.35, 1.0, 32)
    ar = e(t, 1.3, 1.7)
    if ar > 0:
        c.set_source_rgba(*GOLD, ar)
        c.set_line_width(14)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.move_to(500, 925)
        c.line_to(580, 925)
        c.move_to(555, 897)
        c.line_to(582, 925)
        c.line_to(555, 953)
        c.stroke()
    tag(c, 780, 925, "2026 $23.68", back(e(t, 1.5, 1.85)) * 1.35, 1.0, 32)
    b = back(e(t, 2.2, 2.6))
    if b > 0.01:
        c.save()
        c.translate(540, 1105)
        c.scale(b, b)
        rrect(c, -290, -105, 580, 210, 60)
        c.set_source_rgb(*GOLD)
        c.fill()
        txt(c, "+10%", 0, 60, 170, BROWN, H)
        c.restore()
        ring(c, 540, 1105, t - 2.2, 120, 340, 0.5, 8, GOLD)
    txt(c, "NOW $1.48 A POUND", 540, 1280, 48, CREAM, H, a=e(t, 2.7, 3.1), stroke=BROWN, sw=8)


def panel3(c, t):
    txt(c, "BUT STILL BELOW", 540, 395, 68, CREAM, H, stroke=BROWN, sw=12, a=e(t, 0, 0.25))
    txt(c, "THE 2022 RECORD", 540, 478, 68, GOLD, H, stroke=BROWN, sw=12, a=e(t, 0.1, 0.35))
    base = 1150
    u = 7.2
    for (cx, lab, val, col, t0, t1) in ((360, "2022", 64.05, DEEP, 0.3, 1.1), (720, "2026", TOTAL, ORANGE, 0.8, 1.5)):
        g = e(t, t0, t1)
        h = val * u * g
        if h > 1:
            rrect(c, cx - 115 + 6, base - h + 6, 230, h, 16)
            c.set_source_rgba(0, 0, 0, 0.35)
            c.fill()
            rrect(c, cx - 115, base - h, 230, h, 16)
            c.set_source_rgb(*col)
            c.fill()
            if g > 0.6:
                txt(c, "$%.2f" % val, cx, base - h + 78, 52, WHITE, M, a=e(g, 0.6, 1.0))
        txt(c, lab, cx, base + 64, 56, CREAM, H, a=e(t, t0, t0 + 0.3))
    da = e(t, 1.3, 1.7)
    if da > 0:
        yy = base - 64.05 * u
        c.set_source_rgba(*CREAM, 0.9 * da)
        c.set_line_width(5)
        c.set_dash([16, 12])
        c.move_to(250, yy)
        c.line_to(840, yy)
        c.stroke()
        c.set_dash([])
    b = back(e(t, 2.0, 2.4))
    if b > 0.01:
        c.save()
        c.translate(540, 1290)
        c.scale(b, b)
        rrect(c, -390, -48, 780, 96, 48)
        c.set_source_rgb(*GOLD)
        c.fill()
        txt(c, "8.5% BELOW THE RECORD", 0, 17, 48, BROWN, H)
        c.restore()


def endcard(c, T):
    t = T - END
    s = e(t, 0, 0.5)
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgba(0, 0.93, 0.52, 0.14, s)
    g.add_color_stop_rgba(1, 0.42, 0.14, 0.06, s)
    c.set_source(g)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    leaves_big(c, s)
    a = e(t, 0.2, 0.7)
    logo(c, 540 - 96, 380, 3.2, a)
    txt(c, "MONEY MAP", 540, 760, 100, CREAM, H, a=a, stroke=BROWN, sw=16)
    txt(c, "FOLLOW THE MONEY.", 540, 850, 52, GOLD, H, a=e(t, 0.5, 1.0), stroke=BROWN, sw=10)
    b = e(t, 1.0, 1.5)
    rrect(c, 140, 940, 800, 120, 60)
    c.set_source_rgba(*BROWN, 0.95 * b)
    c.fill()
    txt(c, "FOLLOW FOR MORE", 540, 1018, 56, CREAM, H, a=b)
    n = e(t, 1.6, 2.1)
    txt(c, "WHAT'S ON YOUR TABLE?", 540, 1160, 54, CREAM, H, a=n, stroke=BROWN, sw=10)


def draw(c, T):
    T = T % DUR
    scene(c, T)
    dim = 0.90 * e(T, P1 - 0.05, P1 + 0.3) * (1 - e(T, END - 0.05, END + 0.1))
    topa = 1 - e(T, P1 - 0.35, P1 - 0.05)
    if T < END:
        if topa > 0.01:
            wordmark(c, topa)
            if T < D[0]["pill"]:
                board(c, T, scramble(T), topa)
            elif T >= PL0:
                board(c, T, "$5.86", topa, "PER PERSON")
            else:
                board(c, T, "$%.2f" % total_at(T), topa)
            card(c, T, topa)
        if dim > 0:
            c.set_source_rgba(0.06, 0.03, 0.01, dim)
            c.rectangle(0, 0, VW, VH)
            c.fill()
        if P1 <= T < P2:
            panel1(c, T - P1)
        elif P2 <= T < P3:
            panel2(c, T - P2)
        elif P3 <= T < END:
            panel3(c, T - P3)
    else:
        endcard(c, T)
    if T < 0.4:
        ring(c, 540, 560, T, 50, 330, 0.55, 12)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(path="thanks_music.wav"):
    sr = 44100
    n = int(DUR * sr)
    tail = 4 * sr
    out = np.zeros(n + tail)
    rng = np.random.RandomState(23)
    bar = 4 * BEAT

    def put(sig, t0, g=1.0):
        j = int(t0 * sr)
        if j < 0 or j >= len(out):
            return
        k = min(len(sig), len(out) - j)
        out[j:j + k] += sig[:k] * g

    def env(m, dd):
        return np.exp(-np.arange(m) / (dd * sr))

    def pluck(midi, vel):
        m = int(1.3 * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.zeros(m)
        for k in range(1, 7):
            s += (1.0 / k ** 1.15) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * x) * np.exp(-x * (3.2 + 2.4 * k))
        s += 0.08 * rng.randn(m) * np.exp(-x * 90)
        return s * np.minimum(1, x / 0.002) * vel * 0.09

    def bassn(midi, dd):
        m = int((dd + 0.2) * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.sin(2 * np.pi * f * x) + 0.45 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 7)
        return s * np.minimum(1, x / 0.004) * np.exp(-x / (dd * 0.8)) * 0.30

    def marimba(midi, vel):
        m = int(0.8 * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.sin(2 * np.pi * f * x) * np.exp(-x * 8) + 0.3 * np.sin(2 * np.pi * 4 * f * x) * np.exp(-x * 26)
        return s * vel * 0.22

    def bell(f, dd=0.7, g=0.1):
        m = int(dd * sr)
        x = np.arange(m) / sr
        s = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 10) + 0.3 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 20)) * np.exp(-x * 7)
        return s * g

    m = int(0.35 * sr)
    stomp = np.sin(2 * np.pi * (46 + 90 * np.exp(-np.arange(m) / (0.035 * sr))) * np.arange(m) / sr) * env(m, 0.11) * 0.62
    bh, ah = butter(2, 6500 / (sr / 2), "high")
    shake = lfilter(bh, ah, rng.randn(int(0.07 * sr))) * env(int(0.07 * sr), 0.02) * 0.09
    bp, ap = butter(2, [1100 / (sr / 2), 3600 / (sr / 2)], "band")
    clap = lfilter(bp, ap, rng.randn(int(0.09 * sr))) * env(int(0.09 * sr), 0.025) * 0.55
    thud = np.sin(2 * np.pi * 150 * np.arange(int(0.2 * sr)) / sr) * env(int(0.2 * sr), 0.05) * 0.35

    chords = [[55, 59, 62, 67], [50, 57, 62, 66], [52, 55, 59, 64], [48, 55, 60, 64]]
    roots = [43, 38, 40, 36]
    arp = [0, 1, 2, 3, 2, 1, 2, 3]
    mel = [[(0, 83), (1.5, 86), (2, 88), (3, 86)], [(0, 86), (1, 83), (2, 81), (3.5, 83)],
           [(0, 88), (1.5, 86), (2.5, 83), (3, 81)], [(0, 79), (1, 83), (2, 86), (3, 83)]]
    for b in range(16):
        i = b % 4
        t0 = b * bar
        ch = chords[i]
        for q in range(8):
            put(pluck(ch[arp[q]] + (12 if q in (3, 7) else 0), 1.0 if q % 4 == 0 else 0.7), t0 + q * 0.5 * BEAT)
            put(shake * (1.0 if q % 2 == 0 else 0.55), t0 + q * 0.5 * BEAT + (0.0 if q % 2 == 0 else 0.1 * BEAT))
        put(bassn(roots[i], 1.5 * BEAT), t0)
        put(bassn(roots[i], 0.9 * BEAT), t0 + 2.5 * BEAT, 0.8)
        if b >= 2:
            for tb in (0, 2):
                put(stomp, t0 + tb * BEAT)
        if b >= 4:
            for tb in (1, 3):
                put(clap, t0 + tb * BEAT, 0.8)
            for tb, midi in mel[i]:
                put(marimba(midi, 1.0), t0 + tb * BEAT)
                if b >= 12:
                    put(marimba(midi + 12, 0.4), t0 + tb * BEAT + 0.01)
    put(stomp * 1.5, 0.0)
    put(bell(1900, 0.4, 0.12), 0.0)
    for i, d in enumerate(D):
        put(thud, d["land"], 0.9)
        put(bell(2300 + (i * 173) % 700, 0.25, 0.10), d["land"] + 0.01)
        put(bell(1500 + 110 * i, 0.2, 0.08), d["pill"] + 0.02)
    nn = int(2.0 * sr)
    x = np.arange(nn) / sr
    ri = lfilter(*butter(2, [800 / (sr / 2), 6000 / (sr / 2)], "band"), rng.randn(nn)) * (x / 2.0) ** 2 * 0.22
    put(ri, LOCK - 2.0)
    put(stomp * 1.7, LOCK)
    for f in (784.0, 987.8, 1174.7, 1568.0):
        put(bell(f, 1.6, 0.10), LOCK)
    pn = [79, 81, 83, 86, 88, 91, 88, 86, 83, 81]
    for i, mi in enumerate(pn):
        put(marimba(mi, 1.1), PL0 + i * BEAT * 0.5)

    def whoosh(t0, dd=0.55, g=0.20):
        m2 = int(dd * sr)
        xx = np.arange(m2) / sr
        w = lfilter(*butter(2, [500 / (sr / 2), 5000 / (sr / 2)], "band"), rng.randn(m2)) * np.sin(np.pi * xx / dd) ** 2 * g
        put(w, t0)

    for tp in (P1, P2, P3, END):
        whoosh(tp - 0.1)
    for tb in (P1 + 2.0, P2 + 2.2, P3 + 2.0):
        put(stomp * 1.2, tb)
        put(bell(1568.0, 0.6, 0.10), tb)
    put(bell(2093.0, 0.6, 0.09), END + 1.0)
    out[:tail] += out[n:n + tail]
    out = out[:n]
    b2, a2 = butter(2, 9000 / (sr / 2), "low")
    out = lfilter(b2, a2, out)
    out /= np.abs(out).max() / 0.9
    sf.write(path, out.astype(np.float32), sr)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "thanks_v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        draw(c, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    music()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "thanks_v.tmp.mp4", "-i", "thanks_music.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    print("ok")


def stills(times=None):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, T in enumerate(times or (0.0, 0.2, 3.4, 5.6, 9.0, 14.5, 15.6, 17.5, 21.8, 26.5, 30.6, 33.5)):
        draw(c, T)
        surf.write_to_png("tst_%02d.png" % i)


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    scene(c, 0.0, cover=True)
    wordmark(c, 1.0)
    board(c, 0.0, "$??.??")
    card(c, 0.0, 1.0, custom=("10 PEOPLE. ONE DINNER.", "HOW MUCH?"), sz=(60, 84))
    surf.write_to_png(path)


def zones(png, out):
    from PIL import Image, ImageDraw
    im = Image.open(png).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, VW, 270], fill=(255, 0, 0, 90))
    d.rectangle([0, 1536, VW, VH], fill=(255, 0, 0, 90))
    d.rectangle([0, 1344, VW, 1536], fill=(255, 140, 0, 70))
    d.rectangle([VW - 65, 270, VW, 1536], fill=(255, 0, 0, 70))
    d.rectangle([0, 270, 65, 1536], fill=(255, 0, 0, 70))
    d.rectangle([960, 1000, VW - 65, 1344], fill=(255, 140, 0, 60))
    Image.alpha_composite(im, ov).convert("RGB").save(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"stills": lambda: stills(), "render": lambda: render(sys.argv[2]), "cover": lambda: cover(sys.argv[2]), "music": lambda: music()}[cmd]()
