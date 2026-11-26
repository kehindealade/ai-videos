import cairo, math, os, sys, subprocess
import numpy as np, soundfile as sf
from common import *

DUR = 40.0
APR = (0.965, 0.79, 0.61)
BLUSH = (0.91, 0.65, 0.63)
PLUM = (0.23, 0.16, 0.24)
SAGE = (0.56, 0.66, 0.54)
CREAM = (1.0, 0.953, 0.89)
DUSK = (0.23, 0.20, 0.35)
DUSK2 = (0.15, 0.13, 0.26)
LAMP = (1.0, 0.79, 0.47)
SKIN_H = (0.80, 0.56, 0.38)
SKIN_W = (0.47, 0.29, 0.19)
YEL = (0.98, 0.78, 0.25)
BLUE = (0.30, 0.45, 0.62)
RED = (0.88, 0.30, 0.32)
FLOOR = 1500


def lerp(a, b, t):
    return a + (b - a) * t


def gradient(c, top, bot, y0=0, y1=VH):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    c.set_source(g)
    c.rectangle(0, y0, VW, y1 - y0)
    c.fill()


def line_text(c, s, y, a=1.0, size=92, col=CREAM):
    txt(c, s, 540, y, size, col, H, a=a, stroke=PLUM, sw=20)


def face(c, cx, cy, mood, T, r=80):
    blink = 0.1 if (T % 3.4) < 0.1 else 1.0
    c.set_source_rgb(*PLUM)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(8)
    for ex in (-30, 30):
        if mood == "sleep":
            c.move_to(cx + ex - 12, cy)
            c.line_to(cx + ex + 12, cy)
            c.stroke()
        else:
            c.save()
            c.translate(cx + ex, cy)
            c.scale(1, blink)
            rr = 13 if mood == "shock" else 9
            c.arc(0, 0, rr, 0, 2 * math.pi)
            c.fill()
            c.restore()
    if mood in ("smile", "smile2"):
        c.arc(cx, cy + 16, 30, 0.2 * math.pi, 0.8 * math.pi)
        c.stroke()
    elif mood == "sad":
        c.arc(cx, cy + 56, 26, 1.2 * math.pi, 1.8 * math.pi)
        c.stroke()
    elif mood == "shock":
        c.arc(cx, cy + 40, 15, 0, 2 * math.pi)
        c.stroke()
    elif mood == "tired":
        c.move_to(cx - 18, cy + 40)
        c.line_to(cx + 18, cy + 38)
        c.stroke()
        for ex in (-30, 30):
            c.arc(cx + ex, cy + 26, 12, 0.1 * math.pi, 0.9 * math.pi)
            c.stroke()
    else:
        c.move_to(cx - 16, cy + 38)
        c.line_to(cx + 16, cy + 38)
        c.stroke()


def person(c, cx, foot, kind, mood, T, hands=None, run=0.0, seated=False, s=1.45, flip=1, props=()):
    skin = SKIN_H if kind == "h" else SKIN_W
    shirt = BLUE if kind == "h" else YEL
    pants = PLUM if kind == "h" else SKIN_W
    c.save()
    c.translate(cx, foot)
    c.scale(s * flip, s)
    bob = abs(math.sin(run * 6)) * -14 if run else 2 * math.sin(T * 2)
    if not seated:
        for i, sgn in enumerate((-1, 1)):
            sw = math.sin(run * 6 + i * math.pi) * 38 if run else 0
            c.set_source_rgb(*pants)
            c.set_line_width(58 if kind == "h" else 36)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(sgn * 46, -200 + bob)
            c.line_to(sgn * 46 + sw, -20)
            c.stroke()
            rrect(c, sgn * 46 + sw - 36, -34, 72, 34, 14)
            c.set_source_rgb(0.15, 0.12, 0.16)
            c.fill()
    top = -200 - 280 + bob
    if kind == "w":
        c.move_to(-85, top + 200)
        c.line_to(-150, -150 + bob)
        c.line_to(150, -150 + bob)
        c.line_to(85, top + 200)
        c.close_path()
        c.set_source_rgb(*shirt)
        c.fill()
        rrect(c, -90, top, 180, 300, 70)
    else:
        rrect(c, -105, top, 210, 300, 70)
    c.set_source_rgb(*shirt)
    c.fill()
    if kind == "h":
        c.set_source_rgb(*RED)
        c.rectangle(-8, top + 6, 16, 130)
        c.fill()
        rrect(c, -22, top + 130, 44, 56, 6)
        c.set_source_rgb(0.97, 0.97, 0.95)
        c.fill()
    c.rectangle(-24, top - 30, 48, 50)
    c.set_source_rgb(*skin)
    c.fill()
    hy = top - 70
    if kind == "w":
        c.arc(0, hy - 14, 118, 0, 2 * math.pi)
        c.set_source_rgb(0.10, 0.07, 0.07)
        c.fill()
        for sg in (-1, 1):
            rrect(c, sg * 88 - 24, hy, 48, 150, 24)
            c.fill()
    c.arc(0, hy, 82, 0, 2 * math.pi)
    c.set_source_rgb(*skin)
    c.fill()
    if kind == "h":
        c.arc(0, hy - 8, 86, math.pi * 1.03, math.pi * 1.97)
        c.close_path()
        c.set_source_rgb(0.12, 0.09, 0.10)
        c.fill()
    else:
        c.arc(0, hy - 18, 92, math.pi * 1.0, math.pi * 2.0)
        c.close_path()
        c.set_source_rgb(0.10, 0.07, 0.07)
        c.fill()
    face(c, 0, hy + 2, mood, T)
    if kind == "w":
        c.set_source_rgb(*PLUM)
        c.set_line_width(5)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for ex in (-30, 30):
            for dx, dy in ((-14, -14), (0, -18), (14, -14)):
                c.move_to(ex + dx * 0.6, hy - 8)
                c.line_to(ex + dx, hy - 8 + dy)
        c.stroke()
        for sg in (-1, 1):
            c.arc(sg * 82, hy + 40, 13, 0, 2 * math.pi)
            c.set_source_rgb(0.98, 0.80, 0.25)
            c.fill()
        c.arc(0, hy + 42, 14, 0, math.pi)
        c.set_source_rgb(0.85, 0.22, 0.30)
        c.fill()
    arm_col = shirt
    sh = [(-100, top + 60), (100, top + 60)]
    rest = [(-125, top + 250), (125, top + 250)]
    for i in range(2):
        hp = rest[i]
        if hands and hands[i] is not None:
            hp = (hands[i][0] / (s * flip) , hands[i][1] / s) if False else hands[i]
        c.set_line_width(54)
        c.set_source_rgb(*arm_col)
        c.move_to(*sh[i])
        c.line_to(*hp)
        c.stroke()
        c.arc(hp[0], hp[1], 30, 0, 2 * math.pi)
        c.set_source_rgb(*skin)
        c.fill()
    for px, py, k in props:
        if k == 'mug':
            mug(c, px, py)
        elif k == 'mug2':
            mug(c, px, py, (0.98, 0.9, 0.6))
    c.restore()
    return top, hy


def phone(c, cx, cy, w=640, h=1120, glow=0.0, tilt=0.0):
    c.save()
    c.translate(cx, cy)
    c.rotate(tilt)
    if glow > 0:
        c.arc(0, 0, w * 0.9, 0, 2 * math.pi)
        c.set_source_rgba(1, 0.9, 0.6, 0.18 * glow)
        c.fill()
    rrect(c, -w / 2 - 6, -h / 2 + 12, w + 12, h, 80)
    c.set_source_rgba(0, 0, 0, 0.22)
    c.fill()
    rrect(c, -w / 2, -h / 2, w, h, 76)
    c.set_source_rgb(0.12, 0.10, 0.14)
    c.fill()
    rrect(c, -w / 2 + 22, -h / 2 + 22, w - 44, h - 44, 58)
    c.set_source_rgb(*CREAM)
    c.fill()
    c.restore()


def alarm_row(c, x, y, w, tm, label, on, a=1.0, hl=0.0):
    rrect(c, x, y, w, 150, 34)
    c.set_source_rgba(1, 1, 1, a)
    c.fill()
    if hl > 0:
        rrect(c, x, y, w, 150, 34)
        c.set_source_rgba(1.0, 0.8, 0.3, 0.55 * hl * a)
        c.fill()
    txt(c, tm, x + 30, y + 88, 84, PLUM, H, "l", a)
    if label:
        txt(c, label, x + 30, y + 130, 28, (0.5, 0.4, 0.5), H, "l", a)
    tx = x + w - 150
    rrect(c, tx, y + 48, 110, 56, 28)
    c.set_source_rgba(*((0.35, 0.72, 0.46) if on else (0.75, 0.72, 0.76)), a)
    c.fill()
    c.arc(tx + (82 if on else 28), y + 76, 22, 0, 2 * math.pi)
    c.set_source_rgba(1, 1, 1, a)
    c.fill()


def screen_alarms(c, cx, cy, T, rows, extra=0.0, typed=0):
    x = cx - 270
    y = cy - 440
    txt(c, "Alarms", cx, y + 20, 56, PLUM, H)
    for i, (tm, lb) in enumerate(rows):
        alarm_row(c, x, y + 70 + i * 175, 540, tm, lb, True, 1.0, hl=max(0, 1 - abs(T - i) / 0.35))
    if extra > 0:
        lab = "SAY SORRY. BUY CAKE."[:typed]
        alarm_row(c, x, y + 70 + 3 * 175, 540, "6:30", lab, True, e(extra, 0, 0.5))


def screen_cal(c, cx, cy, T):
    x = cx - 270
    y = cy - 440
    txt(c, "TODAY", cx, y + 30, 60, PLUM, H)
    for i in range(5):
        c.set_source_rgba(0.8, 0.75, 0.8, 0.8)
        c.set_line_width(3)
        c.move_to(x, y + 130 + i * 140)
        c.line_to(x + 540, y + 130 + i * 140)
        c.stroke()
        txt(c, "%d:00" % (7 + i * 3), x + 10, y + 120 + i * 140, 30, (0.6, 0.55, 0.6), M, "l")
    txt(c, "No events", cx, cy + 40, 64, (0.5, 0.42, 0.5), H)
    txt(c, "0", cx + 140, cy + 340, 200, (0.88, 0.30, 0.32), H, a=0.9)


def bed_wall(c):
    gradient(c, APR, BLUSH, 0, 1500)
    c.set_source_rgb(0.45, 0.30, 0.30)
    c.rectangle(0, 1500, VW, 420)
    c.fill()
    rrect(c, 760, 260, 220, 300, 20)
    c.set_source_rgb(1.0, 0.95, 0.80)
    c.fill()
    c.set_source_rgba(1, 0.9, 0.5, 0.4)
    c.arc(870, 410, 70, 0, 2 * math.pi)
    c.fill()


def kitchen(c):
    gradient(c, (0.74, 0.83, 0.71), SAGE, 0, FLOOR)
    c.set_source_rgb(0.62, 0.45, 0.36)
    c.rectangle(0, FLOOR, VW, VH - FLOOR)
    c.fill()
    rrect(c, 70, 380, 300, 380, 16)
    c.set_source_rgb(0.80, 0.93, 1.0)
    c.fill_preserve()
    c.set_source_rgb(1, 1, 1)
    c.set_line_width(14)
    c.stroke()
    c.set_line_width(8)
    c.move_to(220, 380)
    c.line_to(220, 760)
    c.move_to(70, 570)
    c.line_to(370, 570)
    c.stroke()
    c.set_source_rgb(0.95, 0.70, 0.35)
    c.arc(300, 470, 38, 0, 2 * math.pi)
    c.fill()


def door(c, openness, shake=0.0):
    x, y, w, h = 760, 600, 280, 900
    c.save()
    c.translate(shake, 0)
    c.rectangle(x - 16, y - 16, w + 32, h + 16)
    c.set_source_rgb(0.95, 0.9, 0.8)
    c.fill()
    c.rectangle(x, y, w, h)
    c.set_source_rgb(0.95, 0.80, 0.55)
    c.fill()
    if openness > 0:
        c.rectangle(x, y, w, h)
        c.set_source_rgb(0.99, 0.93, 0.75)
        c.fill()
        c.move_to(x, y)
        c.line_to(x - 80 * openness, y + 30)
        c.line_to(x - 80 * openness, y + h - 20)
        c.line_to(x, y + h)
        c.close_path()
        c.set_source_rgb(0.80, 0.55, 0.30)
        c.fill()
    else:
        c.arc(x + w - 40, y + 460, 14, 0, 2 * math.pi)
        c.set_source_rgb(0.5, 0.35, 0.2)
        c.fill()
    c.restore()


def mug(c, x, y, col=(0.98, 0.97, 0.94)):
    rrect(c, x - 34, y - 56, 68, 62, 10)
    c.set_source_rgb(*col)
    c.fill()
    c.set_line_width(10)
    c.set_source_rgb(*col)
    c.arc(x + 38, y - 26, 20, -1.2, 1.2)
    c.stroke()


def dining(c, dark):
    gradient(c, DUSK, DUSK2, 0, FLOOR)
    c.set_source_rgb(0.28, 0.20, 0.26)
    c.rectangle(0, FLOOR, VW, VH - FLOOR)
    c.fill()
    c.arc(540, 1000, 520, 0, 2 * math.pi)
    c.set_source_rgba(*LAMP, 0.10 * (1 - dark))
    c.fill()
    c.set_source_rgb(0.60, 0.40, 0.26)
    c.rectangle(0, FLOOR - 10, VW, 14)
    c.fill()


def clock(c, h, m):
    cx, cy = 880, 520
    c.arc(cx, cy, 110, 0, 2 * math.pi)
    c.set_source_rgb(*CREAM)
    c.fill_preserve()
    c.set_source_rgb(*PLUM)
    c.set_line_width(10)
    c.stroke()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(12):
        a = k * math.pi / 6
        c.move_to(cx + 90 * math.sin(a), cy - 90 * math.cos(a))
        c.line_to(cx + 100 * math.sin(a), cy - 100 * math.cos(a))
        c.set_line_width(6)
        c.stroke()
    ah = (h % 12 + m / 60) * math.pi / 6
    am = m * math.pi / 30
    c.set_line_width(12)
    c.move_to(cx, cy)
    c.line_to(cx + 52 * math.sin(ah), cy - 52 * math.cos(ah))
    c.stroke()
    c.set_line_width(8)
    c.move_to(cx, cy)
    c.line_to(cx + 80 * math.sin(am), cy - 80 * math.cos(am))
    c.stroke()


def table(c, top_y=1180):
    rrect(c, 120, top_y, 840, 44, 14)
    c.set_source_rgb(0.72, 0.50, 0.32)
    c.fill()
    c.rectangle(210, top_y + 44, 40, FLOOR - top_y - 44)
    c.rectangle(830, top_y + 44, 40, FLOOR - top_y - 44)
    c.set_source_rgb(0.56, 0.38, 0.24)
    c.fill()


def cake(c, x, y, candle=1.0, flame=1.0, T=0.0, tilt=0.0, bakery=False):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    rrect(c, -130, -110, 260, 110, 20)
    c.set_source_rgb(0.98, 0.86, 0.80)
    c.fill()
    rrect(c, -130, -140, 260, 50, 24)
    c.set_source_rgb(0.99, 0.97, 0.94)
    c.fill()
    if bakery:
        c.set_source_rgb(*RED)
        for k in range(-3, 4):
            c.arc(k * 34, -92, 11, 0, 2 * math.pi)
            c.fill()
        c.save()
        c.translate(-60, -146)
        c.rotate(0.5)
        c.rectangle(0, 0, 70, 28)
        c.set_source_rgb(0.99, 0.97, 0.94)
        c.fill()
        c.restore()
    if candle > 0:
        ch = 80 * candle
        c.rectangle(-8, -140 - ch, 16, ch)
        c.set_source_rgb(0.4, 0.7, 0.9)
        c.fill()
        if flame > 0:
            fl = 1 + 0.12 * math.sin(T * 14)
            c.save()
            c.translate(0, -148 - ch)
            c.scale(flame, flame * fl)
            c.move_to(0, -52)
            c.curve_to(26, -16, 22, 0, 0, 4)
            c.curve_to(-22, 0, -26, -16, 0, -52)
            c.set_source_rgb(1.0, 0.76, 0.25)
            c.fill()
            c.restore()
    c.restore()


def sprout_logo(c, cx, cy, s, a):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.arc(0, 0, 90, math.pi, 2 * math.pi)
    c.set_source_rgba(0.93, 0.70, 0.25, a)
    c.fill()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(10)
    for k in range(7):
        ang = math.pi + (k + 0.5) * math.pi / 7
        c.move_to(110 * math.cos(ang), 110 * math.sin(ang))
        c.line_to(150 * math.cos(ang), 150 * math.sin(ang))
    c.stroke()
    c.set_source_rgba(0.20, 0.55, 0.32, a)
    c.set_line_width(12)
    c.move_to(0, 0)
    c.curve_to(0, -30, 0, -50, 0, -70)
    c.stroke()
    for sg in (-1, 1):
        c.move_to(0, -62)
        c.curve_to(sg * 20, -100, sg * 60, -92, sg * 68, -70)
        c.curve_to(sg * 40, -52, sg * 14, -54, 0, -62)
        c.fill()
    c.restore()


def ping_t():
    return (0.0, 1.0, 2.0)


def draw(c, T):
    T = T % DUR
    if T < 3.0:
        bed_wall(c)
        phone(c, 540, 1000, tilt=0.02 * math.sin(T * 25) * (1 if T % 1 < 0.3 else 0.2), glow=1)
        screen_alarms(c, 540, 1000, T, [("6:00", "Work"), ("6:10", "Work"), ("6:20", "Work")])
        line_text(c, "He set", 250, e(T, 0, 0.2))
        line_text(c, "3 alarms for work.", 360, e(T, 0.2, 0.5), 88)
    elif T < 6.0:
        t = T - 3.0
        bed_wall(c)
        phone(c, 540, 1000)
        screen_cal(c, 540, 1000, t)
        line_text(c, "0 for", 250, e(t, 0, 0.2))
        line_text(c, "her birthday.", 360, e(t, 0.2, 0.5), 96)
    elif T < 11.0:
        t = T - 6.0
        kitchen(c)
        shake = 0.0
        slam = t > 2.6
        op = 0.0 if slam else 1.0
        if 2.6 <= t < 3.0:
            shake = 12 * math.sin(t * 90)
        door(c, op, shake)
        hx = lerp(520, 880, e(t, 0.0, 2.6))
        if t < 2.6:
            person(c, hx, FLOOR + 30, "h", "tired", T, hands=[None, (150, -300)], run=t, props=[(150, -270, 'mug')])
        wx = 250
        person(c, wx, FLOOR + 30, "w", "sad" if t > 2.8 else "smile", T, hands=[(-90, -350), (90, -350)], props=[(-90, -330, 'mug'), (90, -330, 'mug2')])
        if t > 2.9:
            c.set_source_rgba(1, 1, 1, 0.8 * (1 - e(t, 2.9, 3.6)))
            c.set_line_width(10)
            for k in range(5):
                a = -0.9 + k * 0.45
                c.move_to(820 + 190 * math.cos(a), 900 + 260 * math.sin(a))
                c.line_to(820 + 270 * math.cos(a), 900 + 360 * math.sin(a))
            c.stroke()
    elif T < 25.0:
        t = T - 11.0
        dark = e(T, 22.8, 25.0)
        dining(c, dark)
        hh = 8 if T < 13.4 else (9 if T < 15.7 else 10)
        mm = 0 if t < 2.3 else 0
        clock(c, 8 + min(2, int(t / 2.35)) if T < 18 else 10, 0)
        candle = 1 - 0.18 * min(t, 7) / 7
        flame = 1.0 if T < 22.8 else max(0.0, 1 - (T - 22.6) / 0.25)
        wife_x = 430
        if T < 23.4:
            person(c, wife_x, FLOOR + 40, "w", "sad" if T > 14.5 else "smile", T, hands=[(-100, -250), (100, -250)], seated=True)
        else:
            u = e(T, 23.4, 25.0)
            person(c, lerp(wife_x, 1300, u), FLOOR + 40, "w", "sad", T, run=T if u < 1 else 0, seated=False)
        if T < 23.4:
            pass
        table(c)
        rrect(c, 580, 1130, 120, 56, 10)
        c.set_source_rgba(0.85, 0.9, 1, 0.85)
        c.fill()
        cake(c, 790, 1180, candle, flame, T)
        if 22.8 <= T < 23.6:
            sm = (T - 22.8) / 0.8
            c.set_source_rgba(0.9, 0.9, 0.95, 0.5 * (1 - sm))
            c.set_line_width(8)
            c.move_to(790, 1000 - sm * 100)
            c.curve_to(810, 960 - sm * 100, 770, 940 - sm * 100, 790, 900 - sm * 100)
            c.stroke()
        if T >= 18.0:
            hx = lerp(-250, 150, e(T, 18.0, 19.9))
            mood = "tired" if T < 19.9 else "shock"
            person(c, hx, FLOOR + 30, "h", mood, T, run=(T - 18) if T < 19.9 else 0, hands=[None, (150, -150)] if False else None)
            if T >= 20.0 and T < 22.6:
                txt(c, "!", hx + 130, 700, 160, YEL, H, stroke=PLUM, sw=16)
        if T < 18:
            for i, k in enumerate((0, 1, 2)):
                t0 = 11.0 + 2.35 * i
                a = e(T, t0, t0 + 0.2) * (1 - e(T, t0 + 2.1, t0 + 2.35))
                line_text(c, ("8 pm.", "9 pm.", "10 pm.")[i], 300, a, 140)
        c.set_source_rgba(0.05, 0.04, 0.12, 0.35 * dark)
        c.rectangle(0, 0, VW, VH)
        c.fill()
    elif T < 28.0:
        t = T - 25.0
        dining(c, 1.0)
        c.set_source_rgba(0.05, 0.04, 0.12, 0.35)
        c.rectangle(0, 0, VW, VH)
        c.fill()
        clock(c, 10, 0)
        person(c, 540, FLOOR + 40, "h", "sad", T, hands=[(-100, -250), (60, -480 + 200 * (1 - e(t, 1.0, 2.0)))] if False else None, seated=True)
        table(c)
        g = e(t, 1.2, 2.2)
        rrect(c, 520, 1130, 120, 56, 10)
        c.set_source_rgba(0.9, 0.95, 1, 0.6 + 0.4 * g)
        c.fill()
        c.arc(540, 1050, 260, 0, 2 * math.pi)
        c.set_source_rgba(0.7, 0.85, 1, 0.15 * g)
        c.fill()
        c.set_source_rgba(0, 0, 0, 0)
    elif T < 32.0:
        t = T - 28.0
        gradient(c, DUSK2, (0.08, 0.07, 0.16))
        phone(c, 540, 1000, glow=1)
        typed = int(clamp((t - 0.7) / 2.0) * 20)
        screen_alarms(c, 540, 1000, 9, [("6:00", "Work"), ("6:10", "Work"), ("6:20", "Work")], extra=t - 0.2, typed=typed)
        line_text(c, "4 alarms.", 250, e(t, 1.6, 2.0), 120)
    elif T < 37.0:
        t = T - 32.0
        bed_wall(c)
        rrect(c, 300, 1050, 760, 480, 40)
        c.set_source_rgb(0.98, 0.93, 0.85)
        c.fill()
        rrect(c, 300, 1230, 760, 300, 30)
        c.set_source_rgb(0.52, 0.62, 0.75)
        c.fill()
        person(c, 720, 1360, "w", "smile2" if t > 1.4 else "tired", T, seated=True, s=1.3)
        c.rectangle(0, 300, 330, 1220)
        c.set_source_rgb(0.99, 0.94, 0.78)
        c.fill()
        c.rectangle(330, 300, 26, 1220)
        c.set_source_rgb(0.78, 0.55, 0.32)
        c.fill()
        hx = lerp(-200, 170, e(t, 0.0, 1.2))
        person(c, hx, FLOOR + 30, "h", "smile2", T, hands=[None, (170, -230)])
        cake(c, hx + 250, FLOOR - 335, 0, 0, T, tilt=-0.18, bakery=True)
        line_text(c, "Late.", 240, e(t, 1.2, 1.5), 120)
        line_text(c, "But he showed up.", 370, e(t, 1.8, 2.2), 84)
    else:
        t = T - 37.0
        gradient(c, CREAM, (0.98, 0.86, 0.66))
        sprout_logo(c, 540, 760, 2.6, e(t, 0, 0.4))
        txt(c, "SMALL WIN FILMS", 540, 980, 84, PLUM, H, a=e(t, 0.2, 0.6))
        txt(c, "NUMBERS THAT SAY EVERYTHING", 540, 1120, 46, PLUM, H, a=e(t, 0.4, 0.8))
        txt(c, "EPISODE 1 · 3 ALARMS", 540, 1190, 40, (0.55, 0.38, 0.30), H, a=e(t, 0.4, 0.8))
        rrect(c, 190, 1290, 700, 110, 55)
        c.set_source_rgba(*PLUM, e(t, 0.8, 1.2))
        c.fill()
        txt(c, "FOLLOW FOR EPISODE 2", 540, 1362, 46, CREAM, H, a=e(t, 0.8, 1.2))
    return T


def stills(times):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, T in enumerate(times):
        draw(c, T)
        surf.write_to_png("ast_%02d.png" % i)


def _sheet():
    from PIL import Image
    ts = [0.3, 2.2, 4.5, 7.0, 8.9, 10.2, 12.0, 14.0, 16.5, 19.0, 20.8, 23.0, 24.5, 26.5, 29.5, 31.0, 33.5, 35.5, 38.0, 39.5]
    stills(ts)
    ims = [Image.open("ast_%02d.png" % i).resize((216, 384)) for i in range(len(ts))]
    W = Image.new("RGB", (216 * 10, 384 * 2))
    for i, im in enumerate(ims):
        W.paste(im, ((i % 10) * 216, (i // 10) * 384))
    W.save("asheet.png")


def render(out):
    import piano_loop
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "alarms_v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        draw(c, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    piano_loop.build("alarms_music.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "alarms_v.tmp.mp4", "-i", "alarms_music.wav", "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    bed_wall(c)
    phone(c, 540, 1050, glow=1)
    screen_alarms(c, 540, 1050, 9, [("6:00", "Work"), ("6:10", "Work"), ("6:20", "Work")])
    txt(c, "3 ALARMS.", 540, 250, 150, CREAM, H, stroke=PLUM, sw=26)
    txt(c, "NOT ONE FOR HER.", 540, 400, 92, YEL, H, stroke=PLUM, sw=20)
    surf.write_to_png(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2])
    elif cmd == "cover":
        cover(sys.argv[2])
    else:
        _sheet()
