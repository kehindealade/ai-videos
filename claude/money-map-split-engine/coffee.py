import cairo, math, os, sys, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter
from common import *

DUR = 36.0
T0, T1 = 3.0, 22.0
REVEAL, ENDC = 24.0, 31.2
CAFE_PRICE, HOME_PRICE, MACHINE, DAYS = 5.0, 0.60, 60.0, 250
DISC = 25
STACK_BASE = 1320
DISC_H = 10.5
LX, RX = 450, 630
WALL_L = [(0.99, 0.72, 0.40), (0.96, 0.58, 0.27)]
WALL_R = [(0.40, 0.78, 0.78), (0.20, 0.58, 0.62)]
NAVY = (0.10, 0.14, 0.30)
_BG = None


def day(T):
    return DAYS * clamp((T - T0) / (T1 - T0))


def left_amt(T):
    return CAFE_PRICE * math.floor(day(T))


def right_amt(T):
    return MACHINE + HOME_PRICE * day(T)


def money(v):
    return "${:,.0f}".format(v)


def bg(c):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        for x0, wall, floor in ((0, WALL_L, (0.45, 0.24, 0.12)), (540, WALL_R, (0.10, 0.34, 0.40))):
            g = cairo.LinearGradient(0, 0, 0, STACK_BASE)
            g.add_color_stop_rgb(0, *wall[0])
            g.add_color_stop_rgb(1, *wall[1])
            d.set_source(g)
            d.rectangle(x0, 0, 540, VH)
            d.fill()
            d.set_source_rgb(*floor)
            d.rectangle(x0, 1560, 540, VH - 1560)
            d.fill()
        d.set_source_rgba(0, 0, 0, 0.16)
        d.set_line_width(4)
        for i in range(8):
            d.move_to(0, 1600 + i * 46)
            d.line_to(540, 1600 + i * 46)
            d.stroke()
        d.set_source_rgba(1, 1, 1, 0.10)
        for i in range(12):
            for j in range(8):
                d.rectangle(540 + i * 45 + 2, 1590 + j * 42 + 2, 40, 37)
                d.fill()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def awning(c):
    n = 6
    w = 540 / n
    for i in range(n):
        c.rectangle(i * w, 620, w, 70)
        c.set_source_rgb(*((0.86, 0.17, 0.20) if i % 2 == 0 else (1.0, 0.95, 0.86)))
        c.fill()
        c.arc(i * w + w / 2, 690, w / 2, 0, math.pi)
        c.set_source_rgb(*((0.86, 0.17, 0.20) if i % 2 == 0 else (1.0, 0.95, 0.86)))
        c.fill()
    c.set_source_rgba(0, 0, 0, 0.12)
    c.rectangle(0, 700, 540, 14)
    c.fill()


def menu_board(c):
    rrect(c, 50, 770, 290, 210, 14)
    c.set_source_rgb(0.10, 0.22, 0.17)
    c.fill()
    rrect(c, 50, 770, 290, 210, 14)
    c.set_source_rgb(0.62, 0.40, 0.20)
    c.set_line_width(10)
    c.stroke()
    txt(c, "COFFEE", 195, 850, 50, (0.95, 0.95, 0.9), H)
    txt(c, "$5", 195, 950, 110, GOLD, H)


def window(c):
    rrect(c, 650, 740, 290, 230, 14)
    g = cairo.LinearGradient(0, 740, 0, 970)
    g.add_color_stop_rgb(0, 0.72, 0.92, 1.0)
    g.add_color_stop_rgb(1, 0.92, 0.98, 1.0)
    c.set_source(g)
    c.fill_preserve()
    c.set_source_rgb(0.95, 0.98, 0.98)
    c.set_line_width(12)
    c.stroke()
    c.arc(880, 800, 30, 0, 2 * math.pi)
    c.set_source_rgb(1.0, 0.88, 0.35)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.8)
    c.set_line_width(6)
    c.move_to(795, 740)
    c.line_to(795, 970)
    c.stroke()
    c.save()
    c.translate(720, 870)
    c.rotate(-0.07)
    c.rectangle(-70, -62, 140, 124)
    c.set_source_rgb(1.0, 0.92, 0.45)
    c.fill()
    txt(c, "$0.60", 0, 14, 48, INK, H)
    txt(c, "a cup", 0, 48, 26, INK, B)
    c.restore()


def counter(c):
    for x0, top, front in ((0, (0.74, 0.46, 0.24), (0.50, 0.28, 0.14)), (540, (0.93, 0.98, 0.98), (0.55, 0.78, 0.80))):
        c.set_source_rgb(*top)
        c.rectangle(x0, STACK_BASE, 540, 42)
        c.fill()
        c.set_source_rgb(*front)
        c.rectangle(x0, STACK_BASE + 42, 540, 198)
        c.fill()
        c.set_source_rgba(0, 0, 0, 0.12)
        c.rectangle(x0, STACK_BASE + 42, 540, 10)
        c.fill()
    c.set_source_rgba(0, 0, 0, 0.14)
    for i in range(1, 4):
        c.move_to(i * 135, STACK_BASE + 52)
        c.line_to(i * 135, 1560)
        c.stroke()


def machine(c, T):
    x, y = 715, STACK_BASE
    rrect(c, x, y - 170, 100, 170, 14)
    c.set_source_rgb(0.18, 0.20, 0.26)
    c.fill()
    rrect(c, x + 10, y - 160, 80, 50, 8)
    c.set_source_rgb(0.30, 0.34, 0.42)
    c.fill()
    c.arc(x + 50, y - 125, 6, 0, 2 * math.pi)
    c.set_source_rgb(0.4, 1.0, 0.6)
    c.fill()
    c.rectangle(x + 38, y - 100, 24, 40)
    c.set_source_rgb(0.1, 0.1, 0.14)
    c.fill()
    rrect(c, x + 28, y - 50, 44, 50, 6)
    c.set_source_rgb(0.98, 0.98, 0.95)
    c.fill()
    for k in range(3):
        ph = (T * 0.8 + k / 3.0) % 1.0
        c.set_source_rgba(1, 1, 1, 0.55 * (1 - ph))
        c.set_line_width(6)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        sx = x + 50 + (k - 1) * 14
        c.move_to(sx, y - 56 - ph * 70)
        c.curve_to(sx + 12, y - 80 - ph * 70, sx - 12, y - 100 - ph * 70, sx, y - 120 - ph * 70)
        c.stroke()


def takeaway(c, x, y, tilt=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.move_to(-26, -64)
    c.line_to(26, -64)
    c.line_to(20, 0)
    c.line_to(-20, 0)
    c.close_path()
    c.set_source_rgb(0.98, 0.97, 0.94)
    c.fill()
    c.rectangle(-27, -76, 54, 14)
    c.set_source_rgb(0.30, 0.18, 0.10)
    c.fill()
    c.rectangle(-23, -44, 46, 22)
    c.set_source_rgb(0.86, 0.17, 0.20)
    c.fill()
    c.restore()


def person(c, cx, top, shirt, skin, hair, mood, T, side):
    bob = 4 * math.sin(T * 2.2 + side)
    top += bob
    arm = shirt
    rrect(c, cx - 100, top + 100, 200, 330, 70)
    c.set_source_rgb(*shirt)
    c.fill()
    c.rectangle(cx - 22, top + 55, 44, 70)
    c.set_source_rgb(*skin)
    c.fill()
    c.arc(cx, top, 74, 0, 2 * math.pi)
    c.set_source_rgb(*skin)
    c.fill()
    c.arc(cx, top - 6, 79, math.pi * 1.02, math.pi * 1.98)
    c.close_path()
    c.set_source_rgb(*hair)
    c.fill()
    blink = 1.0 if (T % 3.2) > 0.12 else 0.1
    for ex in (-27, 27):
        c.save()
        c.translate(cx + ex, top - 2)
        c.scale(1, blink)
        c.arc(0, 0, 8.5, 0, 2 * math.pi)
        c.set_source_rgb(*INK)
        c.fill()
        c.restore()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(7)
    c.set_source_rgb(*INK)
    if mood == "happy":
        c.arc(cx, top + 14, 28, 0.25 * math.pi, 0.75 * math.pi)
        c.stroke()
        c.arc(cx - 48, top + 20, 11, 0, 2 * math.pi)
        c.arc(cx + 48, top + 20, 11, 0, 2 * math.pi)
        c.set_source_rgba(1, 0.4, 0.4, 0.35)
        c.fill()
    elif mood == "sad":
        c.arc(cx, top + 52, 26, 1.2 * math.pi, 1.8 * math.pi)
        c.stroke()
        c.move_to(cx - 44, top - 30)
        c.line_to(cx - 14, top - 20)
        c.move_to(cx + 44, top - 30)
        c.line_to(cx + 14, top - 20)
        c.stroke()
        sw = (T * 1.5) % 1.0
        c.arc(cx + 70, top - 40 + sw * 40, 9, 0, 2 * math.pi)
        c.set_source_rgba(0.5, 0.8, 1.0, 0.9 * (1 - sw))
        c.fill()
    else:
        c.move_to(cx - 16, top + 30)
        c.line_to(cx + 16, top + 30)
        c.stroke()
    return top


def arms(c, cx, top, shirt, skin, hx, hy, side):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgb(*shirt)
    c.set_line_width(52)
    c.move_to(cx - 92 * side, top + 150)
    c.line_to(cx - 112 * side, top + 290)
    c.stroke()
    c.move_to(cx + 92 * side, top + 150)
    c.line_to(hx, hy)
    c.stroke()
    c.arc(hx, hy, 26, 0, 2 * math.pi)
    c.set_source_rgb(*skin)
    c.fill()


def coin(c, x, y, r=24, a=1.0):
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(0.99, 0.82, 0.25, a)
    c.fill_preserve()
    c.set_source_rgba(0.75, 0.52, 0.08, a)
    c.set_line_width(5)
    c.stroke()
    txt(c, "$", x, y + r * 0.38, r * 1.15, (0.6, 0.40, 0.05), H, a=a)


def stack(c, cx, n, flying, hand, T, glow=0.0):
    w = 124
    for i in range(n):
        y = STACK_BASE - (i + 1) * DISC_H
        off = ((i * 37) % 7 - 3) * 1.2
        rrect(c, cx - w / 2 + off, y, w, DISC_H + 1.5, 4)
        c.set_source_rgb(*((0.99, 0.80, 0.22) if i % 2 == 0 else (0.94, 0.70, 0.14)))
        c.fill()
    topy = STACK_BASE - n * DISC_H
    if glow > 0:
        c.arc(cx, topy, 90, 0, 2 * math.pi)
        c.set_source_rgba(1, 0.9, 0.4, 0.25 * glow)
        c.fill()
    if flying is not None and 0 < flying < 1:
        p = flying
        sx, sy = hand
        tx, ty = cx, topy - DISC_H
        x = sx + (tx - sx) * p
        y = sy + (ty - sy) * p - 160 * math.sin(math.pi * p)
        coin(c, x, y, 24)
    return topy


def headline(c, T):
    txt(c, "SAME COFFEE. 1 YEAR.", 540, 200, 80, WHITE, H, stroke=NAVY, sw=16)
    hook = 1 - e(T, 3.0, 3.4)
    chip = e(T, 3.0, 3.4) * (1 - e(T, REVEAL - 0.4, REVEAL))
    if hook > 0.01:
        k = 1 + 0.04 * math.sin(T * 7)
        c.save()
        c.translate(540, 305)
        c.scale(k, k)
        rrect(c, -380, -58, 760, 116, 58)
        c.set_source_rgba(1.0, 0.86, 0.20, hook)
        c.fill()
        txt(c, "WHO SPENDS MORE?", 0, 24, 66, INK, H, a=hook)
        c.restore()
    if chip > 0.01:
        d = int(day(T))
        ms = [3.0 + 3.8 * k for k in range(1, 6)]
        pulse = max([max(0.0, 1 - abs(T - m) / 0.35) for m in ms] + [0])
        k = 1 + 0.10 * pulse
        c.save()
        c.translate(540, 305)
        c.scale(k, k)
        rrect(c, -290, -62, 580, 124, 40)
        c.set_source_rgba(*NAVY, 0.92 * chip)
        c.fill()
        txt(c, "DAY %d" % d, -60, 24, 70, WHITE, M, a=chip)
        txt(c, "OF 250", 190, -2, 34, GOLD, H, a=chip)
        txt(c, "WORKDAYS", 190, 38, 28, WHITE, H, a=chip)
        c.restore()


def header(c, T):
    for x, s, col in ((270, "CAFÉ EVERY DAY", (0.86, 0.17, 0.20)), (810, "HOME MACHINE", (0.08, 0.45, 0.50))):
        rrect(c, x - 235, 408, 470, 78, 39)
        c.set_source_rgba(1, 1, 1, 0.92)
        c.fill()
        txt(c, s, x, 463, 44, col, H)


def counters(c, T):
    la, ra = left_amt(T), right_amt(T)
    if T >= REVEAL:
        la, ra = CAFE_PRICE * DAYS, MACHINE + HOME_PRICE * DAYS
    pl = 0.0
    if T < 0.5:
        pl = 1 - T / 0.5
    k = 1 + 0.15 * pl
    c.save()
    c.translate(810, 590)
    c.scale(k, k)
    txt(c, money(ra), 0, 0, 124, WHITE, M, stroke=(0.05, 0.28, 0.33), sw=16)
    c.restore()
    txt(c, money(la), 270, 590, 124, WHITE, M, stroke=(0.55, 0.12, 0.10), sw=16)
    if T < 3.0:
        a = 1.0 - e(T, 2.5, 3.0)
        rrect(c, 640, 1130 - 580 + 460, 0, 0, 0)
        c.save()
        c.translate(810, 650)
        c.rotate(-0.04)
        rrect(c, -210, -28, 420, 56, 28)
        c.set_source_rgba(1.0, 0.86, 0.20, a)
        c.fill()
        txt(c, "MACHINE $60", 0, 15, 36, INK, H, a=a)
        c.restore()


def scene(c, T):
    bg(c)
    awning(c)
    menu_board(c)
    window(c)
    d = day(T)
    la, ra = left_amt(T), right_amt(T)
    if T >= REVEAL:
        la, ra = CAFE_PRICE * DAYS, MACHINE + HOME_PRICE * DAYS
        d = DAYS
    ln, rn = int(la // DISC), int(ra // DISC)
    lf = (la / DISC - ln) if T < REVEAL else 0
    rf = (ra / DISC - rn) if T < REVEAL else 0
    if T < T0:
        lf = 0
        rf = 0
    lf = ((d % 5) / 5.0) if T0 <= T < REVEAL else 0
    rf = ra / DISC - rn if T0 <= T < REVEAL else 0
    sad = "sad" if T >= 3.0 + 3.8 * 3 else "flat"
    lt = person(c, 215, 1020, NAVY, (0.88, 0.68, 0.52), (0.12, 0.10, 0.10), sad, T, 1)
    arms(c, 215, lt, NAVY, (0.88, 0.68, 0.52), 335, lt + 255 + 8 * math.sin(T * 3), -1)
    takeaway(c, 335, lt + 255 + 8 * math.sin(T * 3) + 30)
    rt = person(c, 880, 1020, (0.98, 0.93, 0.80), (0.62, 0.42, 0.30), (0.24, 0.14, 0.10), "happy", T, -1)
    arms(c, 880, rt, (0.98, 0.93, 0.80), (0.62, 0.42, 0.30), 820, rt + 260, -1)
    counter(c)
    machine(c, T)
    glow = e(T, REVEAL, REVEAL + 0.5)
    lt_y = stack(c, LX, ln, lf if lf > 0 else None, (340, lt + 270), T, glow)
    rt_y = stack(c, RX, rn, rf if rf > 0 else None, (830, rt + 270), T, glow)
    return lt_y, rt_y


def reveal(c, T, lt_y, rt_y):
    t = T - REVEAL
    a = e(t, 0, 0.35)
    c.set_source_rgba(1, 1, 1, 0.95 * a)
    c.set_line_width(6)
    c.set_dash([16, 12])
    c.move_to(340, rt_y)
    c.line_to(740, rt_y)
    c.stroke()
    c.set_dash([])
    bx = 350
    c.set_source_rgba(1, 0.9, 0.3, a)
    c.set_line_width(9)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(bx, rt_y)
    c.line_to(bx, lt_y)
    c.stroke()
    for yy, dd in ((rt_y, -1), (lt_y, 1)):
        c.move_to(bx - 22, yy + dd * 30)
        c.line_to(bx, yy)
        c.line_to(bx + 22, yy + dd * 30)
        c.stroke()
    s = back(e(t, 0.1, 0.6))
    c.save()
    c.translate(540, 1450)
    c.scale(max(0.01, s), max(0.01, s))
    rrect(c, -470, -118, 940, 236, 40)
    c.set_source_rgba(*NAVY, 0.97)
    c.fill()
    txt(c, "$1,040", -150, 40, 150, GOLD, H)
    txt(c, "APART.", 250, -2, 62, WHITE, H)
    txt(c, "SAME COFFEE.", 250, 62, 44, WHITE, H)
    c.restore()


def endcard(c, T):
    t = T - ENDC
    s = e(t, 0, 0.6)
    c.save()
    c.rectangle(0, 0, 540 + (1 - s) * 0, VH)
    c.restore()
    for x0, wall in ((0, WALL_L), (540, WALL_R)):
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgba(0, *wall[0], s)
        g.add_color_stop_rgba(1, *wall[1], s)
        c.set_source(g)
        c.rectangle(x0, 0, 540, VH)
        c.fill()
    c.set_source_rgba(1, 1, 1, 0.9 * s)
    c.rectangle(535, 0, 10, VH)
    c.fill()
    a = e(t, 0.2, 0.7)
    txt(c, "SAME MONEY.", 540, 560, 112, WHITE, H, a=a, stroke=NAVY, sw=18)
    txt(c, "TWO CHOICES.", 540, 690, 112, GOLD, H, a=a, stroke=NAVY, sw=18)
    b = e(t, 0.8, 1.3)
    rrect(c, 140, 800, 800, 120, 60)
    c.set_source_rgba(*NAVY, 0.95 * b)
    c.fill()
    txt(c, "EPISODE 1 · COFFEE", 540, 880, 56, WHITE, H, a=b)
    n = e(t, 1.6, 2.1)
    txt(c, "NEXT: A NEW PHONE", 540, 1040, 60, WHITE, H, a=n, stroke=NAVY, sw=12)
    txt(c, "EVERY YEAR?", 540, 1112, 60, WHITE, H, a=n, stroke=NAVY, sw=12)
    f = e(t, 2.4, 2.9)
    logo(c, 540 - 90, 1150, 3.0, f)
    txt(c, "MONEY MAP", 540, 1405, 64, WHITE, H, a=f, stroke=NAVY, sw=12)
    txt(c, "FOLLOW FOR EPISODE 2", 540, 1490, 52, WHITE, H, a=f, stroke=NAVY, sw=12)
    txt(c, "Example prices. Not advice, just maths.", 540, 1545, 32, WHITE, B, a=f * 0.9, stroke=NAVY, sw=8)


def draw(c, T):
    T = T % DUR
    lt_y, rt_y = scene(c, T)
    if T < ENDC:
        header(c, T)
        headline(c, T)
        counters(c, T)
        if T >= REVEAL:
            reveal(c, T, lt_y, rt_y)
        if 3.0 <= T < 3.0 + 0.001:
            pass
    else:
        endcard(c, T)
    if T < 0.45:
        r = 40 + 380 * T / 0.45
        c.arc(810, 600, r, 0, 2 * math.pi)
        c.set_source_rgba(1, 1, 1, 0.6 * (1 - T / 0.45))
        c.set_line_width(14)
        c.stroke()


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(path="coffee_music.wav"):
    sr = 44100
    bpm = 100.0
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int(DUR * sr)
    tail = 4 * sr
    out = np.zeros(n + tail)
    rng = np.random.RandomState(11)

    def put(sig, t0, g=1.0):
        j = int(t0 * sr)
        if j >= len(out):
            return
        k = min(len(sig), len(out) - j)
        out[j:j + k] += sig[:k] * g

    def env(m, d):
        return np.exp(-np.arange(m) / (d * sr))

    def ep(midi, dur, vel):
        m = int((dur + 0.6) * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.sin(2 * np.pi * f * x) + 0.45 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 3) + 0.2 * np.sin(2 * np.pi * 3 * f * x) * np.exp(-x * 7)
        s *= (1 + 0.12 * np.sin(2 * np.pi * 5 * x))
        r = np.minimum(1, x / 0.005) * np.where(x < dur, np.exp(-x * 1.6), np.exp(-dur * 1.6) * np.exp(-(x - dur) * 14))
        return s * r * vel * 0.07

    def bass(midi, dur):
        m = int((dur + 0.2) * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 6)
        return s * np.minimum(1, x / 0.004) * np.exp(-x / (dur * 0.9)) * 0.3

    def marimba(midi, vel):
        m = int(0.7 * sr)
        x = np.arange(m) / sr
        f = mtof(midi)
        s = np.sin(2 * np.pi * f * x) * np.exp(-x * 9) + 0.35 * np.sin(2 * np.pi * 4 * f * x) * np.exp(-x * 28)
        return s * vel * 0.2

    def bell(f, d=0.7, g=0.1):
        m = int(d * sr)
        x = np.arange(m) / sr
        s = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 10) + 0.3 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 20)) * np.exp(-x * 7)
        return s * g

    m = int(0.35 * sr)
    kick = np.sin(2 * np.pi * (48 + 100 * np.exp(-np.arange(m) / (0.03 * sr))) * np.arange(m) / sr) * env(m, 0.1) * 0.55
    bh, ah = butter(2, 6000 / (sr / 2), "high")
    sh = lfilter(bh, ah, rng.randn(int(0.06 * sr))) * env(int(0.06 * sr), 0.018) * 0.10
    bp, ap = butter(2, [1500 / (sr / 2), 3500 / (sr / 2)], "band")
    rim = lfilter(bp, ap, rng.randn(int(0.05 * sr))) * env(int(0.05 * sr), 0.012) * 0.5

    chords = [[60, 64, 67, 71], [57, 60, 64, 67], [57, 60, 62, 65], [55, 59, 62, 65], [60, 64, 67, 71]]
    roots = [36, 33, 38, 31, 36]
    phr = [
        [(0.0, 76), (1.0, 79), (1.5, 81), (2.5, 79), (3.5, 76)],
        [(0.0, 81), (1.5, 79), (2.0, 76), (3.0, 72)],
        [(0.0, 74), (1.0, 77), (1.5, 81), (2.5, 77), (3.5, 74)],
        [(0.0, 79), (0.5, 77), (1.0, 74), (2.0, 71), (3.0, 74)],
        [(0.0, 76), (2.0, 72), (3.0, 79)],
    ]
    for b in range(15):
        sec, i = b // 5, b % 5
        t0 = b * bar
        ch = chords[i]
        for k, tb in enumerate((0.0, 1.5, 2.5)):
            for mi, nn in enumerate(ch):
                put(ep(nn, 0.9, 0.8 if k == 0 else 0.6), t0 + tb * beat + mi * 0.012)
        put(bass(roots[i], 1.4), t0)
        put(bass(roots[i], 0.9), t0 + 2.5 * beat, 0.8)
        if i in (1, 3):
            put(bass(roots[i] + 7, 0.6), t0 + 3.5 * beat, 0.7)
        for q in range(8):
            sw = 0.0 if q % 2 == 0 else 0.14 * beat
            put(sh * (1.0 if q % 2 == 0 else 0.6), t0 + q * 0.5 * beat + sw)
        if sec >= 1:
            for tb in (0, 2):
                put(kick, t0 + tb * beat)
            for tb in (1, 3):
                put(rim, t0 + tb * beat, 0.7)
            for tb, midi in phr[i]:
                put(marimba(midi, 1.0), t0 + tb * beat)
                if sec == 2:
                    put(marimba(midi + 12, 0.45), t0 + tb * beat + 0.01)
    for k in range(1, 51):
        put(bell(2700 + (k % 5) * 90, 0.18, 0.045), T0 + 0.38 * k + 0.0)
    for mi in range(1, 4):
        tl = T0 + (((25 * mi + 0) - 60) / 0.6) / 250.0 * (T1 - T0) if False else None
    rr = 0
    for mm in range(3, 9):
        d = (DISC * mm - MACHINE) / HOME_PRICE
        if 0 < d <= 250:
            put(bell(1700, 0.3, 0.10), T0 + d / 250.0 * (T1 - T0))
    put(bell(1900, 0.4, 0.12), 0.0)
    put(kick * 1.3, 0.0)
    nn = int(2.0 * sr)
    x = np.arange(nn) / sr
    ri = lfilter(*butter(2, [800 / (sr / 2), 6000 / (sr / 2)], "band"), rng.randn(nn)) * (x / 2.0) ** 2 * 0.22
    put(ri, REVEAL - 2.0)
    put(kick * 1.6, REVEAL)
    for f in (1046.5, 1318.5, 1568.0, 2093.0):
        put(bell(f, 1.6, 0.10), REVEAL)
    put(bell(2093.0, 0.6, 0.09), ENDC)
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
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "coffee_v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        draw(c, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    music()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "coffee_v.tmp.mp4", "-i", "coffee_music.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    print("ok")


def stills(times=None):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, T in enumerate(times or (0.0, 1.5, 3.3, 6.0, 9.0, 12.0, 15.0, 19.0, 22.5, 24.6, 26.5, 33.0)):
        draw(c, T)
        surf.write_to_png("cst_%02d.png" % i)


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    scene(c, 0.0)
    counters(c, 0.0)
    txt(c, "SAME COFFEE.", 540, 210, 118, WHITE, H, stroke=NAVY, sw=20)
    c.save()
    c.translate(540, 345)
    c.rotate(-0.02)
    rrect(c, -440, -80, 880, 160, 80)
    c.set_source_rgb(1.0, 0.86, 0.20)
    c.fill()
    txt(c, "WHO SPENDS MORE?", 0, 34, 84, INK, H)
    c.restore()
    surf.write_to_png(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"stills": lambda: stills(), "render": lambda: render(sys.argv[2]), "cover": lambda: cover(sys.argv[2]), "music": lambda: music()}[cmd]()
