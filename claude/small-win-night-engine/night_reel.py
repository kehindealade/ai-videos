import cairo, math, sys, subprocess
import numpy as np

VW, VH, FPS, DUR = 1080, 1920, 30, 38.0
FH = "Lilita One"
FB = "Inter"
AY = 820
INK = (0.06, 0.05, 0.12)
WHITE = (1, 1, 1)
AMBER = (1.0, 0.72, 0.30)
MAG = (0.98, 0.28, 0.66)
CYAN = (0.22, 0.86, 0.96)
LIME = (0.70, 0.96, 0.32)
VIOLET = (0.62, 0.44, 1.0)
NEONS = [MAG, CYAN, LIME, VIOLET]
OFF = (0.085, 0.085, 0.165)
HOME = (0.93, 0.83, 0.58)
WALL = (0.19, 0.20, 0.30)
SKIN = [(0.46, 0.30, 0.19), (0.80, 0.60, 0.44), (0.36, 0.23, 0.15), (0.93, 0.76, 0.62), (0.62, 0.42, 0.28)]
BX0, BX1, BTOP, GROUND = 60, 1020, 260, 3300
FLOORS = 8
YOU = (5, 0)
BEAT = 60 / 122.0

KF = [(0.0, 540, 450, 1.35), (3.0, 540, 450, 1.28), (11.0, 540, 3400, 1.0), (11.8, 540, 3400, 1.0),
      (13.0, 540, 1800, 0.52), (14.0, 540, 1800, 0.52), (15.2, 306, 2361, 2.0), (25.9, 306, 2361, 2.0),
      (26.6, 540, 3120, 1.0), (29.4, 540, 3120, 1.0), (30.2, 306, 2361, 2.0), (38.0, 306, 2361, 2.0)]

COUNTS = [3, 3, 4, 2, 3, 4, 3, 3, 2, 4, 3, 3, 4, 3, 2]
TAXI_HONK, CROWD_GO, CAB_GO = 10.9, 11.3, 11.6
BUZZ = [17.4, 18.2, 19.0]
FLIP = 19.8
KNOCK = [20.15, 20.35, 20.55]
DOOR_OPEN, HEAD_IN, BUBBLE0, SPOON0, SPOON1, SHRUG, HEAD_OUT, DOOR_SHUT = 20.6, 21.0, 21.2, 21.8, 22.8, 23.0, 23.4, 23.75
NEIGH_GONE = 24.0
SINK0, SINK1, SLEEP = 24.3, 25.0, 24.9
CLOCK0, CLOCK1 = 25.0, 26.0
STREET2, THUNDER, RAIN0, RAIN1 = 26.6, 26.9, 26.0, 32.0
REGRET = 28.2
BACK_IN = 30.2
CARD_AGAIN = 32.0
END_AT = 35.0


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return x * x * (3 - 2 * x)


def back(x):
    x = clamp(x)
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def mix(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def dk(c0, k):
    return tuple(v * (1 - k) for v in c0)


def cam(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(KF, KF[1:]):
        if t0 <= t <= t1:
            k = e(t, t0, t1)
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, math.exp(math.log(z0) + (math.log(z1) - math.log(z0)) * k)
    return KF[-1][1:]


def flat_rect(f, s):
    yk = BTOP + f * 380
    x0 = 84 if s == 0 else 552
    return x0, yk + 22, 444, 358


FLATS = []
_ci = 0
for f in range(FLOORS):
    for s in range(2):
        if (f, s) == YOU:
            continue
        x0, y0, w, h = flat_rect(f, s)
        cy = y0 + h / 2
        tp = 3.0
        for i in range(800):
            tt = 3.0 + i * 0.01
            if cam(tt)[1] >= cy:
                tp = tt
                break
        L = min(10.6, tp + (0.35 if s == 0 else 0.75))
        if f == 0:
            L = 3.4 + 0.4 * s
        FLATS.append(dict(f=f, s=s, n=COUNTS[_ci], L=L, neon=NEONS[(f * 2 + s) % 4], H=27.2 + (15 - _ci) * 0.13, seed=_ci))
        _ci += 1
LEAVES = sorted(fl["L"] for fl in FLATS)


def going(t):
    n = sum(fl["n"] for fl in FLATS if t >= fl["L"])
    if t >= NEIGH_GONE:
        n += 1
    return n


def font(c, name):
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if name == FB else cairo.FONT_WEIGHT_NORMAL)


def tw(c, s, size, f=FH):
    font(c, f)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def txt(c, s, x, y, size, col, f=FH, a=1.0):
    font(c, f)
    c.set_font_size(size)
    ex = c.text_extents(s)
    c.move_to(x - ex.x_advance / 2, y)
    c.set_source_rgba(*col, a)
    c.show_text(s)
    c.new_path()


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def ell(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def sprout(c, x, y, s, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0.95, 0.65, 0.20, a)
    c.arc(0, 0, 70, math.pi, 2 * math.pi)
    c.fill()
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(-3, 4):
        ang = math.pi * 1.5 + k * 0.38
        c.move_to(math.cos(ang) * 88, math.sin(ang) * 88)
        c.line_to(math.cos(ang) * 112, math.sin(ang) * 112)
        c.stroke()
    c.set_source_rgba(0.96, 0.92, 0.80, a)
    c.set_line_width(12)
    c.move_to(-130, 0)
    c.line_to(130, 0)
    c.stroke()
    c.set_source_rgba(0.18, 0.62, 0.38, a)
    c.move_to(0, 0)
    c.curve_to(0, -30, 2, -50, 0, -70)
    c.stroke()
    for sx in (-1, 1):
        c.move_to(0, -52)
        c.curve_to(sx * 20, -90, sx * 55, -90, sx * 62, -70)
        c.curve_to(sx * 40, -45, sx * 15, -46, 0, -52)
        c.fill()
    c.restore()


def fig(c, x, yf, h, col, arms=0.0, hunch=0.0, a=1.0, accent=None):
    hr = h * 0.15
    bw, bh = h * 0.36, h * 0.58
    c.save()
    c.translate(x, yf)
    c.rotate(hunch * 0.25)
    c.set_source_rgba(*col, a)
    rrect(c, -bw / 2, -bh - h * 0.1, bw, bh, bw * 0.45)
    c.fill()
    c.rectangle(-bw * 0.38, -h * 0.14, bw * 0.28, h * 0.14)
    c.rectangle(bw * 0.10, -h * 0.14, bw * 0.28, h * 0.14)
    c.fill()
    c.arc(hunch * hr * 0.8, -bh - h * 0.1 - hr * 0.9 + hunch * hr * 0.6, hr, 0, 2 * math.pi)
    c.fill()
    c.set_line_width(h * 0.07)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    sy = -bh - h * 0.02
    for sx in (-1, 1):
        phi = 0.15 + arms * 2.6
        c.move_to(sx * bw * 0.42, sy)
        c.line_to(sx * (bw * 0.42 + math.sin(phi) * h * 0.30), sy + math.cos(phi) * h * 0.32)
        c.stroke()
    if accent:
        c.set_source_rgba(*accent, a * 0.9)
        rrect(c, -bw / 2, -bh * 0.75 - h * 0.1, bw, bh * 0.16, 4)
        c.fill()
    c.restore()


def party_room(c, fl, t):
    x0, y0, w, h = flat_rect(fl["f"], fl["s"])
    L = fl["L"]
    neon = fl["neon"]
    home = t >= fl["H"]
    lit = t < L + 0.12 or home
    flick = L + 0.02 < t < L + 0.12 and int(t * 60) % 2 == 0
    c.save()
    c.rectangle(x0, y0, w, h)
    c.clip()
    if home:
        k = e(t, fl["H"], fl["H"] + 0.15)
        c.set_source_rgb(*mix(OFF, dk(HOME, 0.35), k))
        c.paint()
        c.set_source_rgba(*dk(HOME, 0.15), 0.6 * k)
        ell(c, x0 + w / 2, y0 + 30, 120, 60)
        c.fill()
        fig(c, x0 + w * 0.45, y0 + h - 4, 150, (0.12, 0.14, 0.24), arms=0.0, hunch=0.6, a=k)
        c.set_source_rgba(0.55, 0.70, 0.95, 0.6 * k)
        ell(c, x0 + w * 0.45, y0 + h - 4, 40, 6)
        c.fill()
    elif lit and not flick:
        c.set_source_rgb(*dk(neon, 0.62))
        c.paint()
        g = cairo.RadialGradient(x0 + w / 2, y0 + 10, 10, x0 + w / 2, y0 + 10, w * 0.8)
        g.add_color_stop_rgba(0, *neon, 0.55)
        g.add_color_stop_rgba(1, *neon, 0.0)
        c.set_source(g)
        c.paint()
        if fl["f"] == 0:
            bx, by = x0 + w / 2, y0 + 60
            for k in range(7):
                ang = t * 1.6 + k * 0.9 + fl["s"]
                c.set_source_rgba(1, 1, 1, 0.10)
                c.move_to(bx, by)
                c.line_to(bx + math.cos(ang) * 500 - 40, by + abs(math.sin(ang)) * 400)
                c.line_to(bx + math.cos(ang) * 500 + 40, by + abs(math.sin(ang)) * 400)
                c.close_path()
                c.fill()
            c.set_source_rgb(0.85, 0.88, 0.95)
            c.arc(bx, by, 22, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgba(0.4, 0.45, 0.6, 1)
            c.set_line_width(2)
            for k in range(-2, 3):
                c.move_to(bx - 22, by + k * 8)
                c.line_to(bx + 22, by + k * 8)
            c.stroke()
            c.move_to(bx, y0)
            c.line_to(bx, by - 22)
            c.stroke()
        else:
            for k in range(9):
                lx = x0 + 20 + k * (w - 40) / 8
                ly = y0 + 26 + 10 * math.sin(k * 0.9)
                on = (int(t * 4) + k) % 3 != 0
                c.set_source_rgba(*(mix(neon, WHITE, 0.5) if on else dk(neon, 0.3)), 1)
                c.arc(lx, ly, 6, 0, 2 * math.pi)
                c.fill()
        c.set_source_rgba(0, 0, 0, 0.25)
        c.rectangle(x0, y0 + h - 28, w, 28)
        c.fill()
        dx, dw = x0 + w - 78, 62
        door_open = e(t, L - 0.6, L - 0.4) * (1 - e(t, L, L + 0.1))
        c.set_source_rgb(*dk(neon, 0.8))
        c.rectangle(dx, y0 + h - 170, dw, 170)
        c.fill()
        if door_open > 0:
            c.set_source_rgba(1.0, 0.92, 0.65, door_open)
            c.rectangle(dx, y0 + h - 170, dw, 170)
            c.fill()
        n = fl["n"]
        for i in range(n):
            px = x0 + 50 + (i + 0.5) * (w - 160) / n
            beat = (t / BEAT + i * 0.37 + fl["seed"] * 0.21) % 1
            bob = abs(math.sin(beat * math.pi)) * 10
            arms = 0.55 + 0.35 * math.sin(t / BEAT * math.pi + i)
            go = e(t, L - 0.55 + i * 0.05, L - 0.05)
            px = px + (dx + dw / 2 - px) * go
            a = 1 - e(t, L - 0.15, L)
            if t > L - 1.5:
                arms *= 1 - e(t, L - 1.5, L - 1.1)
            fig(c, px, y0 + h - 6 - bob * (1 - go), 150 + (i % 3) * 14, (0.07, 0.05, 0.13), arms=arms, a=a,
                accent=NEONS[(i + fl["seed"]) % 4] if t > L - 1.5 else None)
        r0 = L - 1.5
        if r0 < t < L - 0.5:
            for k in range(3):
                p = (t - r0 - k * 0.2) / 0.8
                if 0 < p < 1:
                    cx = x0 + 80 + k * 120 + p * 60
                    cyy = y0 + h - 120 - math.sin(p * math.pi) * 140
                    c.save()
                    c.translate(cx, cyy)
                    c.rotate(p * 6)
                    c.set_source_rgb(*NEONS[(k + 1 + fl["seed"]) % 4])
                    c.move_to(-26, -18)
                    c.line_to(26, -18)
                    c.line_to(34, -4)
                    c.line_to(20, 0)
                    c.line_to(20, 24)
                    c.line_to(-20, 24)
                    c.line_to(-20, 0)
                    c.line_to(-34, -4)
                    c.close_path()
                    c.fill()
                    c.restore()
    else:
        c.set_source_rgb(*OFF)
        c.paint()
        c.set_source_rgb(*dk(OFF, 0.35))
        c.rectangle(x0 + w - 78, y0 + h - 170, 62, 170)
        c.fill()
    c.restore()


def you_room(c, t):
    x0, y0, w, h = flat_rect(*YOU)
    fy = y0 + h
    c.save()
    c.rectangle(x0, y0, w, h)
    c.clip()
    c.set_source_rgb(0.36, 0.25, 0.19)
    c.paint()
    g = cairo.RadialGradient(190, fy - 200, 10, 190, fy - 200, 420)
    g.add_color_stop_rgba(0, 1.0, 0.78, 0.45, 0.75)
    g.add_color_stop_rgba(1, 1.0, 0.60, 0.30, 0.0)
    c.set_source(g)
    c.paint()
    tvk = 0.5 + 0.5 * math.sin(t * 7.3) * math.sin(t * 2.1)
    g2 = cairo.RadialGradient(480, fy - 95, 5, 480, fy - 95, 200)
    g2.add_color_stop_rgba(0, 0.45, 0.65, 1.0, 0.25 + 0.12 * tvk)
    g2.add_color_stop_rgba(1, 0.45, 0.65, 1.0, 0)
    c.set_source(g2)
    c.paint()
    c.set_source_rgb(0.27, 0.17, 0.12)
    c.rectangle(x0, fy - 26, w, 26)
    c.fill()
    c.set_source_rgba(0.75, 0.35, 0.30, 0.8)
    ell(c, 320, fy - 14, 150, 12)
    c.fill()
    dw = 70 * (1 - 0.7 * e(t, DOOR_OPEN, DOOR_OPEN + 0.35) * (1 - e(t, HEAD_OUT + 0.1, DOOR_SHUT)))
    c.set_source_rgb(0.98, 0.88, 0.60)
    c.rectangle(96, fy - 176, 70, 176)
    c.fill()
    if HEAD_IN - 0.05 < t < HEAD_OUT + 0.35:
        k = e(t, HEAD_IN, HEAD_IN + 0.3) * (1 - e(t, HEAD_OUT, HEAD_OUT + 0.3))
        sh = e(t, SHRUG, SHRUG + 0.15) * (1 - e(t, SHRUG + 0.3, SHRUG + 0.45))
        hx = 96 + 70 - 40 * k
        c.save()
        c.rectangle(96, fy - 176, 70, 176)
        c.clip()
        c.set_source_rgb(0.95, 0.74, 0.18)
        rrect(c, hx - 34, fy - 112 - sh * 8, 68, 120, 26)
        c.fill()
        for k2 in range(6):
            c.set_source_rgba(1, 1, 0.85, 0.5 + 0.5 * math.sin(t * 9 + k2))
            c.arc(hx - 20 + (k2 % 3) * 20, fy - 90 + (k2 // 3) * 26, 3, 0, 2 * math.pi)
            c.fill()
        c.set_source_rgb(*SKIN[4])
        c.arc(hx, fy - 132 - sh * 10, 24, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(0.10, 0.07, 0.06)
        c.arc(hx, fy - 140 - sh * 10, 26, math.pi * 0.95, math.pi * 2.05)
        c.fill()
        c.set_source_rgb(0.10, 0.07, 0.06)
        for sx in (-1, 1):
            c.arc(hx + sx * 9 + 6, fy - 132 - sh * 10, 3, 0, 2 * math.pi)
            c.fill()
            c.set_line_width(3)
            c.arc(hx + sx * 9 + 6, fy - 146 - sh * 10, 6, math.pi * 1.15, math.pi * 1.85)
            c.stroke()
        c.set_source_rgb(1.0, 0.85, 0.2)
        c.arc(hx - 22, fy - 122 - sh * 10, 4, 0, 2 * math.pi)
        c.fill()
        c.restore()
    c.set_source_rgb(0.42, 0.26, 0.18)
    c.rectangle(96, fy - 176, dw, 176)
    c.fill()
    c.set_source_rgb(0.85, 0.70, 0.35)
    c.arc(96 + dw - 10, fy - 88, 4, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.20, 0.13, 0.10)
    c.set_line_width(5)
    c.rectangle(94, fy - 178, 74, 178)
    c.stroke()
    c.set_source_rgb(0.25, 0.20, 0.18)
    c.rectangle(198, fy - 210, 5, 210)
    c.fill()
    c.set_source_rgb(1.0, 0.85, 0.55)
    c.move_to(176, fy - 210)
    c.line_to(186, fy - 250)
    c.line_to(216, fy - 250)
    c.line_to(226, fy - 210)
    c.close_path()
    c.fill()
    c.set_source_rgb(0.92, 0.88, 0.80)
    c.arc(480, 2235, 22, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.2, 0.15, 0.12)
    c.set_line_width(3)
    c.arc(480, 2235, 22, 0, 2 * math.pi)
    c.stroke()
    hrs = 11 + 4 * e(t, CLOCK0, CLOCK1) if t < CLOCK1 + 1 else 15
    if t >= CLOCK1:
        hrs = 15
    if t > 30:
        hrs = 15.2
    for ang, ln, lw in ((hrs / 12 * 2 * math.pi, 12, 4), (hrs * 2 * math.pi, 17, 2.5)):
        c.set_line_width(lw)
        c.move_to(480, 2235)
        c.line_to(480 + math.sin(ang) * ln, 2235 - math.cos(ang) * ln)
        c.stroke()
    c.set_source_rgb(0.22, 0.15, 0.12)
    rrect(c, 440, fy - 60, 84, 34, 4)
    c.fill()
    c.set_source_rgb(0.08, 0.08, 0.10)
    rrect(c, 444, fy - 140, 78, 76, 5)
    c.fill()
    c.set_source_rgb(*mix((0.30, 0.50, 0.85), (0.55, 0.80, 0.95), tvk))
    rrect(c, 449, fy - 135, 68, 66, 3)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.5)
    c.arc(470 + 10 * math.sin(t * 1.3), fy - 108, 10, 0, 2 * math.pi)
    c.fill()
    SOFA = (0.20, 0.36, 0.40)
    c.set_source_rgb(*dk(SOFA, 0.15))
    rrect(c, 228, fy - 132, 180, 70, 18)
    c.fill()
    c.set_source_rgb(*SOFA)
    rrect(c, 222, fy - 78, 196, 52, 14)
    c.fill()
    rrect(c, 210, fy - 104, 30, 78, 12)
    rrect(c, 400, fy - 104, 30, 78, 12)
    c.fill()
    sink = 14 * e(t, SINK0, SINK1)
    asleep = t >= SLEEP
    bx, by = 312, fy - 104 + sink * 0.3
    c.set_source_rgb(0.62, 0.58, 0.86)
    ell(c, bx, by, 66, 58)
    c.fill()
    c.move_to(bx - 64, by - 10)
    c.curve_to(bx - 60, by - 70 - sink * 0.0, bx + 60, by - 70, bx + 64, by - 10)
    c.fill()
    hx, hy = bx + 2, by - 66 + sink
    c.set_source_rgb(*SKIN[0])
    c.arc(hx, hy, 27, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.10, 0.07, 0.06)
    c.arc(hx, hy - 6, 28, math.pi * 1.05, math.pi * 1.95)
    c.close_path()
    c.fill()
    c.set_source_rgb(0.62, 0.58, 0.86)
    c.move_to(hx - 40, hy + 2)
    c.curve_to(hx - 34, hy - 46, hx + 34, hy - 46, hx + 40, hy + 2)
    c.curve_to(hx + 30, hy - 30, hx - 30, hy - 30, hx - 40, hy + 2)
    c.fill()
    c.set_source_rgb(0.50, 0.46, 0.74)
    c.move_to(hx - 46, hy + 14)
    c.curve_to(hx - 20, hy + 26, hx + 20, hy + 26, hx + 46, hy + 14)
    c.line_to(hx + 46, hy + 26)
    c.curve_to(hx + 20, hy + 36, hx - 20, hy + 36, hx - 46, hy + 26)
    c.close_path()
    c.fill()
    look = 0
    if BUZZ[0] - 0.1 < t < FLIP + 0.4:
        look = 1
    if HEAD_IN < t < DOOR_SHUT:
        look = -1
    c.set_source_rgb(0.08, 0.06, 0.05)
    c.set_line_width(3)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        ex_, ey_ = hx + sx * 9 + look * 5 + (4 if look == 0 else 0), hy + 4
        if asleep:
            c.arc(ex_, ey_, 5, math.pi * 0.1, math.pi * 0.9)
            c.stroke()
        else:
            c.arc(ex_, ey_, 3.5, 0, 2 * math.pi)
            c.fill()
    c.arc(hx + 3, hy + 11, 7, math.pi * 0.15, math.pi * 0.85)
    c.stroke()
    c.set_source_rgb(0.95, 0.95, 0.95)
    for k in range(2):
        sxk = bx + 56 + k * 16
        ell(c, sxk, fy - 66, 9, 13)
        c.fill()
    c.set_source_rgb(0.95, 0.45, 0.40)
    for k in range(2):
        c.rectangle(bx + 48 + k * 16, fy - 70, 17, 4)
        c.fill()
    raise_ = e(t, SPOON0, SPOON0 + 0.9) * (1 - e(t, SPOON1 + 0.8, SPOON1 + 1.3))
    if not asleep:
        c.set_source_rgb(0.96, 0.93, 0.85)
        c.move_to(bx - 4, by - 18)
        c.curve_to(bx - 2, by + 6, bx + 34, by + 6, bx + 36, by - 18)
        c.close_path()
        c.fill()
        c.set_source_rgb(0.95, 0.75, 0.35)
        for k in range(4):
            c.arc(bx + 4 + k * 8, by - 20, 4, 0, 2 * math.pi)
            c.fill()
        ax0, ay0 = bx + 20, by - 30
        ax1, ay1 = ax0 + (-18 - 10 * raise_), ay0 - 6 - 60 * raise_
        c.set_source_rgb(*SKIN[0])
        c.arc(ax1, ay1, 8, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(0.80, 0.82, 0.86)
        c.set_line_width(4)
        c.move_to(ax1, ay1)
        c.line_to(ax1 + 4 - 6 * raise_, ay1 - 26)
        c.stroke()
        ell(c, ax1 + 4 - 6 * raise_, ay1 - 30, 5, 7)
        c.fill()
    else:
        for k in range(3):
            p = ((t - SLEEP) * 0.6 + k / 3) % 1
            c.set_source_rgba(1, 1, 1, 0.8 * math.sin(p * math.pi))
            font(c, FH)
            c.set_font_size(18 + 10 * p)
            c.move_to(hx + 30 + p * 40, hy - 30 - p * 60)
            c.show_text("z")
            c.new_path()
    jig = 0
    lit_phone = False
    for b in BUZZ:
        if b < t < b + 0.45:
            jig = math.sin((t - b) * 90) * 3
            lit_phone = True
    flip = e(t, FLIP, FLIP + 0.25)
    px, py = 415 + jig, fy - 110
    c.save()
    c.translate(px, py)
    c.scale(1, 1 - 2 * flip if flip < 0.5 else 2 * flip - 1)
    c.set_source_rgb(0.10, 0.10, 0.14)
    rrect(c, -14, -5, 28, 10, 2)
    c.fill()
    c.restore()
    if lit_phone and flip < 0.5:
        c.set_source_rgba(0.55, 0.85, 1.0, 0.9)
        rrect(c, px - 12, py - 6, 24, 4, 1)
        c.fill()
        c.set_source_rgba(1, 1, 1, 0.8)
        c.set_line_width(2.5)
        for sx in (-1, 1):
            for k in range(2):
                c.arc(px, py, 20 + k * 9, math.pi * (1.5 + sx * 0.25) - 0.35, math.pi * (1.5 + sx * 0.25) + 0.35)
                c.stroke()
    if BUBBLE0 < t < HEAD_OUT + 0.2:
        k = back(clamp((t - BUBBLE0) / 0.25)) * (1 - e(t, HEAD_OUT, HEAD_OUT + 0.2))
        c.save()
        c.translate(168, fy - 214)
        c.scale(k, k)
        c.set_source_rgb(1, 1, 1)
        rrect(c, -12, -36, 176, 52, 18)
        c.fill()
        c.move_to(4, 12)
        c.line_to(-8, 30)
        c.line_to(22, 14)
        c.fill()
        c.set_source_rgb(*INK)
        font(c, FH)
        c.set_font_size(30)
        c.move_to(2, 2)
        c.show_text("COMING??")
        c.new_path()
        c.restore()
    if t >= CLOCK0:
        c.set_source_rgba(0.02, 0.02, 0.08, 0.22 * e(t, CLOCK0, CLOCK1))
        c.paint()
    c.restore()


def taxi(c, x, y, a=1.0):
    c.set_source_rgba(0.98, 0.78, 0.18, a)
    rrect(c, x - 110, y - 56, 220, 50, 16)
    c.fill()
    c.move_to(x - 66, y - 54)
    c.line_to(x - 40, y - 96)
    c.line_to(x + 46, y - 96)
    c.line_to(x + 76, y - 54)
    c.close_path()
    c.fill()
    c.set_source_rgba(0.55, 0.75, 0.90, a)
    c.move_to(x - 54, y - 58)
    c.line_to(x - 34, y - 88)
    c.line_to(x + 2, y - 88)
    c.line_to(x + 2, y - 58)
    c.close_path()
    c.move_to(x + 10, y - 58)
    c.line_to(x + 10, y - 88)
    c.line_to(x + 42, y - 88)
    c.line_to(x + 64, y - 58)
    c.close_path()
    c.fill()
    c.set_source_rgba(0.1, 0.1, 0.12, a)
    rrect(c, x - 26, y - 116, 52, 20, 5)
    c.fill()
    font(c, FB)
    c.set_font_size(14)
    c.set_source_rgba(0.98, 0.85, 0.3, a)
    c.move_to(x - 19, y - 101)
    c.show_text("TAXI")
    c.new_path()
    c.set_source_rgba(0.08, 0.08, 0.1, a)
    for wx in (-62, 62):
        c.arc(x + wx, y - 6, 22, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(1, 0.95, 0.7, a)
    ell(c, x + 106, y - 38, 6, 8)
    c.fill()


def street(c, t):
    c.set_source_rgb(0.30, 0.31, 0.40)
    c.rectangle(-2000, GROUND, 5000, 70)
    c.fill()
    c.set_source_rgb(0.12, 0.12, 0.17)
    c.rectangle(-2000, GROUND + 70, 5000, 2000)
    c.fill()
    c.set_source_rgb(0.85, 0.80, 0.55)
    for k in range(-6, 14):
        c.rectangle(k * 220 - (0 if t < CAB_GO else 0), GROUND + 300, 110, 12)
    c.fill()
    for lx in (120, 960):
        c.set_source_rgb(0.15, 0.16, 0.22)
        c.rectangle(lx, GROUND - 260, 10, 260)
        c.fill()
        c.rectangle(lx, GROUND - 260, 50, 10)
        c.fill()
        g = cairo.RadialGradient(lx + 45, GROUND - 245, 2, lx + 45, GROUND - 245, 120)
        g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.6)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        c.set_source(g)
        c.arc(lx + 45, GROUND - 245, 120, 0, 2 * math.pi)
        c.fill()
    if t < 13.5:
        dx = 0 if t < CAB_GO else (t - CAB_GO) ** 2 * 700
        taxi(c, 330 + dx, GROUND + 200)
        taxi(c, 760 + dx * 1.2, GROUND + 200)
        if 8.5 < t < CROWD_GO + 0.5:
            a = e(t, 8.6, 9.2) * (1 - e(t, CROWD_GO, CROWD_GO + 0.4))
            for i in range(10):
                fx = 180 + i * 75 + (math.sin(i * 3.1) * 20)
                bob = abs(math.sin((t / BEAT + i * 0.3) * math.pi)) * 8
                fig(c, fx, GROUND + 52 - bob, 130 + (i % 3) * 12, (0.07, 0.05, 0.13), arms=0.5 + 0.3 * math.sin(t * 6 + i), a=a, accent=NEONS[i % 4])
    if STREET2 - 0.3 < t < 30.5:
        for i in range(7):
            st = STREET2 - 0.2 + i * 0.25
            xx = 1150 - (t - st) * 260
            if xx > 1300 or xx < -200:
                continue
            yy = GROUND + 52
            hop = abs(math.sin((t - st) * 7)) * 18 if i == 2 else abs(math.sin((t - st) * 3.5)) * 3
            fig(c, xx, yy - hop, 140 + (i % 3) * 10, (0.14, 0.17, 0.30), arms=0.05, hunch=0.5, accent=dk(NEONS[i % 4], 0.35))
            if i == 0:
                c.set_source_rgb(*MAG)
                for k in range(2):
                    rrect(c, xx - 34 - k * 10, yy - 64 + k * 6, 22, 10, 3)
                    c.fill()
            if i == 1:
                c.save()
                c.translate(xx + 12, yy - 160)
                c.set_source_rgb(0.18, 0.18, 0.24)
                c.set_line_width(4)
                c.move_to(0, 0)
                c.line_to(0, 70)
                c.stroke()
                c.move_to(-46, 10)
                c.curve_to(-20, -24, 20, -30, 52, -4)
                c.line_to(10, -8)
                c.close_path()
                c.set_source_rgb(0.32, 0.30, 0.55)
                c.fill()
                c.set_source_rgb(0.18, 0.18, 0.24)
                c.set_line_width(3)
                for sx in (-40, -16, 22, 46):
                    c.move_to(0, 0)
                    c.line_to(sx, -16 - abs(sx) * 0.2)
                    c.stroke()
                c.restore()
            for k in range(3):
                p = ((t - st) * 1.8 + k / 3) % 1
                c.set_source_rgba(0.6, 0.8, 1, 0.8)
                ell(c, xx - 16 + k * 16, yy - 90 + p * 90, 3, 5)
                c.fill()


def building(c, t):
    for k in range(-4, 9):
        hh = 900 + (k * 377 % 700)
        bx = -700 + k * 260
        if BX0 - 40 < bx + 200 and bx < BX1 + 40:
            continue
        c.set_source_rgb(0.11, 0.11, 0.21)
        c.rectangle(bx, GROUND - hh, 220, hh)
        c.fill()
        for r in range(int(hh / 90)):
            for q in range(3):
                on = (k * 7 + r * 3 + q) % 5 == 0
                if t > 12 and t < 27.2:
                    on = on and (k + r + q) % 3 == 0
                c.set_source_rgba(1, 0.85, 0.5, 0.55 if on else 0.08)
                c.rectangle(bx + 30 + q * 62, GROUND - hh + 40 + r * 90, 30, 40)
                c.fill()
    c.set_source_rgb(*WALL)
    c.rectangle(BX0, BTOP, BX1 - BX0, GROUND - BTOP)
    c.fill()
    c.set_source_rgb(0.24, 0.25, 0.36)
    c.rectangle(BX0 - 14, BTOP - 18, BX1 - BX0 + 28, 26)
    c.fill()
    c.set_source_rgb(0.16, 0.17, 0.26)
    rrect(c, 760, BTOP - 150, 120, 132, 10)
    c.fill()
    for lx in (790, 850):
        c.rectangle(lx, BTOP - 30, 8, 14)
    c.rectangle(240, BTOP - 220, 6, 200)
    c.fill()
    c.set_source_rgba(1, 0.3, 0.3, 0.6 + 0.4 * math.sin(t * 4))
    c.arc(243, BTOP - 222, 6, 0, 2 * math.pi)
    c.fill()
    for fl in FLATS:
        party_room(c, fl, t)
    you_room(c, t)
    c.set_source_rgb(0.26, 0.27, 0.38)
    for f in range(FLOORS + 1):
        c.rectangle(BX0, BTOP + f * 380, BX1 - BX0, 22)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.06)
    for f in range(FLOORS + 1):
        c.rectangle(BX0, BTOP + f * 380, BX1 - BX0, 4)
    c.fill()


def sky(c, t):
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.04, 0.04, 0.12)
    g.add_color_stop_rgb(1, 0.14, 0.10, 0.28)
    c.set_source(g)
    c.paint()
    for k in range(60):
        x = (k * 397) % VW
        y = (k * 811) % VH
        c.set_source_rgba(1, 1, 1, 0.25 + 0.25 * math.sin(t * 2 + k))
        c.arc(x, y, 1.6 + (k % 3) * 0.6, 0, 2 * math.pi)
        c.fill()


def rain(c, t, a):
    c.save()
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    c.rectangle(-3000, -3000, 8000, 10000)
    c.rectangle(BX0 - 14, BTOP - 18, BX1 - BX0 + 28, GROUND - BTOP + 18)
    c.clip()
    c.set_source_rgba(0.70, 0.80, 1.0, 0.45 * a)
    c.set_line_width(3)
    rng = np.random.default_rng(7)
    xs = rng.uniform(-900, 2000, 500)
    ys = rng.uniform(-800, 4800, 500)
    for x, y in zip(xs, ys):
        yy = (y + t * 2600) % 5600 - 800
        c.move_to(x - yy * 0.12, yy)
        c.line_to(x - yy * 0.12 - 8, yy + 48)
    c.stroke()
    c.restore()


def neon_card(c, lines, size, cy, col, a=1.0, sc=1.0):
    if a <= 0:
        return
    lh = size * 1.18
    wmax = max(tw(c, s, size) for s in lines)
    w = wmax + 90
    h = lh * len(lines) + 50
    c.save()
    c.translate(VW / 2, cy)
    c.scale(sc, sc)
    for lw_, al in ((26, 0.10), (14, 0.22), (5, 1.0)):
        c.set_source_rgba(*col, al * a)
        c.set_line_width(lw_)
        rrect(c, -w / 2, -h / 2, w, h, 30)
        c.stroke()
    c.set_source_rgba(*INK, 0.93 * a)
    rrect(c, -w / 2, -h / 2, w, h, 30)
    c.fill()
    y0 = -h / 2 + 25 + size * 0.98
    for i, s in enumerate(lines):
        txt(c, s, 0, y0 + i * lh, size, mix(col, WHITE, 0.25), a=0.35 * a) if False else None
        txt(c, s, 0, y0 + i * lh, size, WHITE, a=a)
    c.restore()


def pill(c, t):
    if t >= END_AT:
        return
    n = going(t)
    flipk = e(t, REGRET - 0.15, REGRET + 0.15)
    label = "REGRETTING IT: 47" if t >= REGRET else "GOING OUT TONIGHT: %d" % n
    col = MAG if t >= REGRET else CYAN
    pop = 0
    for L in LEAVES + [NEIGH_GONE]:
        if L <= t < L + 0.3:
            pop = max(pop, 1 - (t - L) / 0.3)
    sy = abs(1 - 2 * flipk) if REGRET - 0.15 < t < REGRET + 0.15 else 1
    size = 50
    w = tw(c, label, size) + 80
    h = 96
    c.save()
    c.translate(VW / 2, 366)
    c.scale(1 + 0.08 * pop, (1 + 0.08 * pop) * max(0.05, sy))
    for lw_, al in ((18, 0.14), (9, 0.3), (4, 1.0)):
        c.set_source_rgba(*col, al)
        c.set_line_width(lw_)
        rrect(c, -w / 2, -h / 2, w, h, h / 2)
        c.stroke()
    c.set_source_rgba(*INK, 0.94)
    rrect(c, -w / 2, -h / 2, w, h, h / 2)
    c.fill()
    txt(c, label, 0, 18, size, WHITE)
    c.restore()


def end_card(c, t):
    a = e(t, END_AT, END_AT + 0.4)
    c.save()
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.05, 0.04, 0.14)
    g.add_color_stop_rgb(1, 0.18, 0.11, 0.30)
    c.set_source(g)
    c.paint_with_alpha(a)
    for k in range(50):
        c.set_source_rgba(1, 1, 1, 0.4 * a)
        c.arc((k * 397) % VW, (k * 613) % 1100, 1.8, 0, 2 * math.pi)
        c.fill()
    for k in range(7):
        hh = 260 + (k * 173 % 300)
        c.set_source_rgba(0.09, 0.08, 0.18, a)
        c.rectangle(k * 160 - 20, VH - hh, 150, hh)
        c.fill()
    c.set_source_rgba(0.12, 0.11, 0.22, a)
    c.rectangle(380, 1220, 320, 700)
    c.fill()
    c.set_source_rgba(*AMBER, a)
    c.rectangle(500, 1430, 80, 64)
    c.fill()
    g2 = cairo.RadialGradient(540, 1462, 5, 540, 1462, 200)
    g2.add_color_stop_rgba(0, *AMBER, 0.45 * a)
    g2.add_color_stop_rgba(1, *AMBER, 0)
    c.set_source(g2)
    c.arc(540, 1462, 200, 0, 2 * math.pi)
    c.fill()
    sprout(c, VW / 2, 600, 1.0, a)
    txt(c, "IT'S NOT JUST ME", VW / 2, 820, 104, WHITE, a=a)
    txt(c, "EPISODE 3 · THE NIGHT IN", VW / 2, 905, 50, AMBER, f=FB, a=a)
    lab = "FOLLOW FOR EPISODE 4"
    w = tw(c, lab, 50) + 90
    c.set_source_rgba(*LIME, a)
    rrect(c, VW / 2 - w / 2, 985, w, 100, 50)
    c.fill()
    txt(c, lab, VW / 2, 1053, 50, INK, a=a)
    c.restore()


def frame(c, t, cover=False):
    sky(c, t)
    cx, cy, z = cam(t)
    c.save()
    c.translate(VW / 2, AY)
    c.scale(z, z)
    c.translate(-cx, -cy)
    building(c, t)
    street(c, t)
    ra = e(t, RAIN0, RAIN0 + 0.6) * (1 - e(t, RAIN1 - 0.5, RAIN1))
    if ra > 0:
        rain(c, t, ra)
    c.restore()
    if THUNDER < t < THUNDER + 0.35:
        k = 1 - (t - THUNDER) / 0.35
        c.set_source_rgba(0.85, 0.9, 1.0, 0.7 * k * (1 if int(t * 30) % 3 else 0.4))
        c.paint()
    if cover:
        return
    pill(c, t)
    a1 = 1 - e(t, 2.9, 3.2)
    neon_card(c, ["IN THIS TOWN, EVERYBODY", "GOES OUT PARTYING..."], 66, 1200, MAG, a1, 1.0)
    a2 = e(t, 13.4, 13.6) * (1 - e(t, 16.8, 17.1))
    neon_card(c, ["...EXCEPT ME."], 96, 1210, AMBER, a2, 0.85 + 0.15 * back(clamp((t - 13.4) / 0.3)))
    a3 = e(t, CLOCK0, CLOCK0 + 0.15) * (1 - e(t, 26.0, 26.3))
    neon_card(c, ["3:00 AM."], 90, 1210, CYAN, a3, 0.85 + 0.15 * back(clamp((t - CLOCK0) / 0.3)))
    a4 = e(t, CARD_AGAIN, CARD_AGAIN + 0.15) * (1 - e(t, END_AT, END_AT + 0.3))
    neon_card(c, ["AND I'D DO IT AGAIN."], 82, 1210, AMBER, a4, 0.85 + 0.15 * back(clamp((t - CARD_AGAIN) / 0.3)))
    if t >= END_AT:
        end_card(c, t)


def cover(out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    t = 2.0
    sky(c, t)
    z = 0.50
    cx, cy = 540, 1880
    c.save()
    c.translate(VW / 2, 1020)
    c.scale(z, z)
    c.translate(-cx, -cy)
    building(c, t)
    street(c, 9.5)
    c.restore()
    for fl in FLATS:
        pass
    n = "GOING OUT TONIGHT: 47/48"
    w = tw(c, n, 50) + 80
    c.save()
    c.translate(VW / 2, 366)
    for lw_, al in ((18, 0.14), (9, 0.3), (4, 1.0)):
        c.set_source_rgba(*CYAN, al)
        c.set_line_width(lw_)
        rrect(c, -w / 2, -48, w, 96, 48)
        c.stroke()
    c.set_source_rgba(*INK, 0.94)
    rrect(c, -w / 2, -48, w, 96, 48)
    c.fill()
    txt(c, n, 0, 18, 50, WHITE)
    c.restore()
    neon_card(c, ["WHO STAYED", "HOME?"], 110, 640, AMBER, 1.0)
    x0, y0, w_, h_ = flat_rect(*YOU)
    sx = VW / 2 + (x0 + w_ / 2 - cx) * z
    sy = 1020 + (y0 + h_ / 2 - cy) * z
    for lw_, al in ((16, 0.15), (8, 0.35), (4, 1.0)):
        c.set_source_rgba(*AMBER, al)
        c.set_line_width(lw_)
        rrect(c, sx - w_ * z / 2 - 10, sy - h_ * z / 2 - 10, w_ * z + 20, h_ * z + 20, 14)
        c.stroke()
    s.write_to_png(out)


def still(t, out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    frame(c, t)
    s.write_to_png(out)


def render(out, a=0, b=None):
    nf = int(DUR * FPS)
    b = nf if b is None else b
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "%dx%d" % (VW, VH),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(s)
    for i in range(a, b):
        c.save()
        frame(c, i / FPS)
        c.restore()
        s.flush()
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        for tt in sys.argv[2:]:
            still(float(tt), "st_%s.png" % tt)
    elif cmd == "cover":
        cover(sys.argv[2])
    elif cmd == "render":
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else None
        render(sys.argv[2], a, b)
