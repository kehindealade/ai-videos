import cairo, math, sys, subprocess, os, random
from timeline import DURS, WH, PH_LEN

W, H, FPS = 1920, 1080, 30
FONT = "Rounded Mplus 1c ExtraBold"
GY = 860

INK = (0.18, 0.23, 0.20)
SKY = (0.875, 0.898, 0.824)
FAR = (0.78, 0.82, 0.73)
GROUND = (0.86, 0.73, 0.61)
CLAY = (0.77, 0.47, 0.35)
CLAY_D = (0.68, 0.39, 0.29)
SAGE = (0.50, 0.61, 0.48)
SAGE_D = (0.33, 0.43, 0.34)
CREAM = (0.96, 0.92, 0.86)
WOOD = (0.56, 0.37, 0.25)
WOOD_D = (0.46, 0.29, 0.19)
SKIN = (0.42, 0.26, 0.15)
OCHRE = (0.85, 0.64, 0.25)
RED = (0.78, 0.27, 0.18)
ORANGE = (0.88, 0.54, 0.18)
GREEN = (0.37, 0.54, 0.31)
ROT = (0.40, 0.31, 0.20)
NIGHT = (0.07, 0.09, 0.20)

STY = [
    dict(col=(0.36, 0.50, 0.62), shape="rect", skin=(0.55, 0.36, 0.24), hair="bun"),
    dict(col=(0.80, 0.45, 0.40), shape="round", skin=(0.36, 0.22, 0.14), hair="wrap"),
    dict(col=(0.62, 0.70, 0.55), shape="pear", skin=(0.72, 0.52, 0.38), hair="cap"),
    dict(col=(0.55, 0.42, 0.60), shape="rect", skin=(0.45, 0.28, 0.17), hair="bald"),
    dict(col=(0.90, 0.78, 0.55), shape="round", skin=(0.30, 0.19, 0.12), hair="cap"),
    dict(col=(0.30, 0.42, 0.40), shape="pear", skin=(0.62, 0.42, 0.28), hair="bun"),
    dict(col=(0.72, 0.36, 0.30), shape="rect", skin=(0.38, 0.24, 0.15), hair="cap"),
]

random.seed(4)
RAIN = [(random.random(), random.random(), 0.6 + 0.8 * random.random()) for _ in range(260)]
STARS = [(random.random() * W, random.random() * 560, 1.5 + 2 * random.random()) for _ in range(70)]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(p, q, k):
    return tuple(lerp(p[i], q[i], k) for i in range(3))


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ell(c, cx, cy, rx, ry):
    c.save()
    c.translate(cx, cy)
    c.scale(rx, ry)
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def text(c, s, x, y, size, col, alpha=1.0, align="c"):
    c.select_font_face(FONT)
    c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        x = x - e.width / 2 - e.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, alpha)
    c.show_text(s)
    return e.width


def far_stalls(c):
    c.set_source_rgb(*FAR)
    for x, w, h in ((-420, 280, 230), (40, 300, 250), (1760, 230, 220)):
        rrect(c, x, GY - h, w, h, 10)
        c.fill()
        c.move_to(x - 30, GY - h)
        c.line_to(x + w + 30, GY - h)
        c.line_to(x + w, GY - h - 60)
        c.line_to(x, GY - h - 60)
        c.close_path()
        c.fill()


def stall(c, t, ox=0, wall=CLAY, wall_d=CLAY_D, awn=(CREAM, SAGE), guitar=True, stock=None, tarp=0.0, brk=0.0):
    stock = stock or [(8, 0)] * 4
    c.save()
    c.translate(ox, 0)
    c.set_source_rgba(*INK, 0.12)
    ell(c, 1220, GY + 6, 540, 14)
    c.fill()
    c.set_source_rgb(*WOOD_D)
    c.rectangle(752, 300, 24, 560)
    c.rectangle(1664, 300, 24, 560)
    c.fill()
    c.set_source_rgb(*wall)
    c.rectangle(776, 350, 888, 350)
    c.fill()
    c.set_source_rgba(*wall_d, 0.55)
    for i in range(1, 6):
        c.rectangle(776 + i * 148 - 3, 350, 6, 350)
    c.fill()
    if guitar:
        c.save()
        c.translate(900, 470)
        c.rotate(-0.12)
        c.set_source_rgb(*WOOD_D)
        rrect(c, -9, -150, 18, 130, 6)
        c.fill()
        c.set_source_rgb(*OCHRE)
        ell(c, 0, 20, 50, 58)
        ell(c, 0, -30, 36, 36)
        c.fill()
        c.set_source_rgb(*INK)
        c.arc(0, 6, 15, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*CREAM)
        rrect(c, -16, -162, 32, 22, 6)
        c.fill()
        c.restore()

    c.set_source_rgb(*WOOD_D)
    c.rectangle(740, 690, 960, 170)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.12)
    for i in range(1, 6):
        c.rectangle(740 + i * 160 - 3, 690, 6, 170)
    c.fill()
    c.set_source_rgb(*WOOD)
    rrect(c, 724, 660, 992, 34, 10)
    c.fill()
    prod = [RED, ORANGE, GREEN, RED]
    for i in range(4):
        n, rot = stock[i]
        if n < 0:
            continue
        x = 800 + i * 220
        c.set_source_rgb(*mix(prod[i], ROT, rot * 0.85))
        for j in range(min(n, 5)):
            c.arc(x + 22 + j * 34, 596 - (10 if j % 2 else 0), 24 - 4 * rot, 0, 2 * math.pi)
        c.fill()
        for j in range(max(0, n - 5)):
            c.arc(x + 56 + j * 34, 566 + 6 * rot, 24 - 4 * rot, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(0.74, 0.56, 0.38)
        rrect(c, x - 10, 596, 200, 66, 8)
        c.fill()
        c.set_source_rgba(*WOOD_D, 0.5)
        c.rectangle(x - 10, 624, 200, 6)
        c.fill()
        if rot > 0.5 and n > 0:
            c.set_source_rgba(*INK, (rot - 0.5) * 2)
            for f in range(3):
                a = t * (3 + f) + i * 2 + f * 2.1
                c.arc(x + 90 + 60 * math.cos(a), 530 + 26 * math.sin(a * 1.7), 4, 0, 2 * math.pi)
                c.fill()
    if tarp > 0:
        c.set_source_rgba(*SAGE_D, 1)
        dx = -1100 * (1 - tarp) ** 2
        c.save()
        c.rectangle(700, 480, 1040, 400)
        c.clip()
        c.move_to(730 + dx, 700)
        c.curve_to(730 + dx, 560, 800 + dx, 530, 900 + dx, 540)
        c.line_to(1560 + dx, 536)
        c.curve_to(1680 + dx, 530, 1712 + dx, 580, 1712 + dx, 700)
        c.close_path()
        c.fill()
        c.set_source_rgba(0, 0, 0, 0.12)
        for i in range(4):
            c.rectangle(900 + i * 200 + dx, 545, 8, 150)
        c.fill()
        c.restore()

    cols = awn
    for half in (0, 1):
        c.save()
        if half == 0 and brk > 0:
            c.translate(1220, 270)
            c.rotate(-brk)
            c.translate(-1220, -270)
        for i in range(5):
            k = i + half * 5
            c.set_source_rgb(*cols[k % 2])
            x = 720 + k * 100
            c.rectangle(x, 270, 100, 60)
            c.fill()
            c.arc(x + 50, 330, 50, 0, math.pi)
            c.fill()
        c.set_source_rgba(*INK, 0.10)
        c.rectangle(720 + half * 500, 270, 500, 10)
        c.fill()
        c.restore()
    c.restore()


def note(c, x, y, s, a):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(*INK, a)
    c.save()
    c.rotate(-0.4)
    ell(c, 0, 0, 13, 9)
    c.restore()
    c.fill()
    c.set_line_width(5)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(11, -3)
    c.line_to(11, -44)
    c.curve_to(22, -40, 30, -32, 28, -20)
    c.stroke()
    c.restore()


def notes(c, t, spans, x0, face=1):
    for a, b in spans:
        k = 0
        s = a
        while s < b:
            age = t - s
            if 0 <= age < 1.5:
                p = age / 1.5
                x = x0 + face * (60 + 90 * p) + 14 * math.sin(age * 5 + k)
                y = 470 - 150 * p
                note(c, x, y, 0.8 + 0.3 * p, math.sin(math.pi * p) ** 0.6)
            s += 0.57
            k += 1


def crate_box(c, n=0, col=ROT):
    c.set_source_rgb(*col)
    for j in range(n):
        c.arc(-60 + j * 34, -40 - (8 if j % 2 else 0), 20, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.74, 0.56, 0.38)
    rrect(c, -100, -36, 200, 66, 8)
    c.fill()
    c.set_source_rgba(*WOOD_D, 0.5)
    c.rectangle(-100, -8, 200, 6)
    c.fill()


def hero(c, t, x=520, mood="ok", whistle=0, busy=0.0, sit=0.0, lean=0.0, face=1, rh=None, lh=None,
         carry=None, tip=0.0, walk=None, lift=0.0, bob=0.0):
    Y = GY - lift
    c.set_source_rgba(*INK, 0.14)
    ell(c, x, GY + 6, 130, 13)
    c.fill()
    if lift > 0:
        c.save()
        c.translate(x, GY - 30)
        crate_box(c, 0)
        c.restore()
    drop = 60 * sit + bob
    if sit > 0.3:
        c.save()
        c.translate(x, GY - 30)
        crate_box(c, 0)
        c.restore()
    c.save()
    c.translate(x, Y)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgb(*INK)
    c.set_line_width(40)
    for sgn in (-1, 1):
        sw = 20 * math.sin(walk) * sgn if walk is not None else 0
        c.move_to(sgn * 34, -130 + drop)
        c.line_to(sgn * (34 + 14 * sit) + sw, -22)
        c.stroke()
        c.set_source_rgb(*CLAY_D)
        rrect(c, sgn * (34 + 14 * sit) + sw - 30, -30, 72, 30, 14)
        c.fill()
        c.set_source_rgb(*INK)
    c.translate(0, -120 + drop)
    c.rotate(lean)

    def body_path(top, bot, y0, y1, r=34):
        c.new_sub_path()
        c.move_to(-top + r, y0)
        c.line_to(top - r, y0)
        c.curve_to(top, y0, top + 6, y0 + 10, top + 12, y0 + 40)
        c.line_to(bot, y1 - r)
        c.curve_to(bot + 4, y1, bot - 10, y1, bot - r, y1)
        c.line_to(-bot + r, y1)
        c.curve_to(-bot + 10, y1, -bot - 4, y1, -bot, y1 - r)
        c.line_to(-top - 12, y0 + 40)
        c.curve_to(-top - 6, y0 + 10, -top, y0, -top + r, y0)
        c.close_path()

    c.set_source_rgb(*OCHRE)
    body_path(62, 104, -200, 20)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.move_to(-44, -130)
    c.line_to(44, -130)
    c.line_to(78, 22)
    c.line_to(-78, 22)
    c.close_path()
    c.fill()
    c.set_line_width(9)
    c.move_to(-40, -128)
    c.line_to(-26, -196)
    c.move_to(40, -128)
    c.line_to(26, -196)
    c.stroke()
    c.set_source_rgba(*SAGE, 0.9)
    rrect(c, -30, -70, 60, 44, 10)
    c.fill()

    bb = 10 * math.sin(t * 5) * busy
    dl = (-104, -18)
    dr = (lerp(100, 196, busy), lerp(-14, -96 + bb, busy))
    if carry == "crate":
        dl, dr = (-78, -92), (78, -92)
    lhp = lh or dl
    rhp = rh or dr

    def arm(sx, hand):
        c.set_source_rgb(*OCHRE)
        c.set_line_width(38)
        c.move_to(sx, -176)
        mx = (sx + hand[0]) / 2 + (26 if sx > 0 else -26)
        c.curve_to(mx, -150, mx, hand[1] - 40 if hand[1] > -176 else hand[1] + 60, hand[0], hand[1])
        c.stroke()
        c.set_source_rgb(*SKIN)
        c.arc(hand[0], hand[1], 20, 0, 2 * math.pi)
        c.fill()

    arm(-66, lhp)
    arm(66, rhp)
    if carry == "crate":
        c.save()
        c.translate(0, -84)
        c.rotate(-tip)
        crate_box(c, 4 if tip < 0.5 else 0)
        c.restore()
        c.set_source_rgb(*SKIN)
        c.arc(lhp[0], lhp[1], 20, 0, 2 * math.pi)
        c.arc(rhp[0], rhp[1], 20, 0, 2 * math.pi)
        c.fill()
    if carry == "orange":
        hp = lhp if face < 0 else rhp
        c.set_source_rgb(*ORANGE)
        c.arc(hp[0] + face * 14, hp[1] - 18, 22, 0, 2 * math.pi)
        c.fill()
    if carry == "hammer":
        c.save()
        c.translate(rhp[0], rhp[1])
        c.rotate(-0.5 + tip)
        c.set_source_rgb(*WOOD_D)
        rrect(c, -7, -90, 14, 100, 6)
        c.fill()
        c.set_source_rgb(*INK)
        rrect(c, -30, -112, 60, 30, 8)
        c.fill()
        c.restore()

    c.translate(0, -262)
    c.rotate(lean * 0.9)
    c.set_source_rgb(*SKIN)
    c.arc(0, 0, 64, 0, 2 * math.pi)
    c.fill()
    c.arc(-62, 6, 12, 0, 2 * math.pi)
    c.arc(62, 6, 12, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    c.arc(0, 0, 66, math.radians(200), math.radians(340))
    c.close_path()
    c.fill()
    rrect(c, -44, -78, 88, 40, 16)
    c.fill()
    ex = 10 * face
    c.set_line_width(7)
    if mood == "tired":
        for dx in (-22, 22):
            c.set_source_rgb(*CREAM)
            ell(c, ex + dx, 2, 11, 9)
            c.fill()
            c.set_source_rgb(*INK)
            c.arc(ex + dx, 6, 5, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*SKIN)
            c.rectangle(ex + dx - 13, -10, 26, 11)
            c.fill()
            c.set_source_rgb(*INK)
            c.move_to(ex + dx - 12, 1)
            c.line_to(ex + dx + 12, 1)
            c.stroke()
        c.arc(ex, 44, 14, 1.15 * math.pi, 1.85 * math.pi)
        c.stroke()
    else:
        big = 1.25 if mood == "shock" else 1.0
        blink = 0.15 if (mood != "shock" and (t % 3.1) < 0.12) else 1.0
        for dx in (-22, 22):
            c.set_source_rgb(*CREAM)
            ell(c, ex + dx, 0, 11 * big, 13 * big * blink)
            c.fill()
            c.set_source_rgb(*INK)
            ell(c, ex + dx + 2 * face, 1, 5.5, 6.5 * blink)
            c.fill()
        c.set_source_rgb(*INK)
        for dx in (-22, 22):
            sgn = 1 if dx > 0 else -1
            if mood == "shock":
                y0 = y1 = -26
            elif mood == "worried":
                y0, y1 = (-17, -25) if sgn > 0 else (-25, -17)
            else:
                y0 = y1 = -20
            c.move_to(ex + dx - 11, y0)
            c.line_to(ex + dx + 11, y1)
            c.stroke()
        if whistle:
            ell(c, ex + 6 * face, 32, 7, 8)
            c.fill()
        elif mood == "shock":
            ell(c, ex, 34, 10, 13)
            c.fill()
        elif mood == "worried":
            c.move_to(ex - 12, 34)
            c.line_to(ex + 12, 34)
            c.stroke()
        elif mood == "happy":
            c.arc(ex, 18, 22, 0.12 * math.pi, 0.88 * math.pi)
            c.stroke()
        else:
            c.arc(ex, 22, 14, 0.2 * math.pi, 0.8 * math.pi)
            c.stroke()
    c.restore()


def figure(c, x, feet, s, st, phase=None, face=1, mute=0.0, carry=False):
    def m(col):
        return mix(col, FAR, mute)
    c.save()
    c.translate(x, feet)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    sw = 26 * math.sin(phase) if phase is not None else 0
    bobv = -6 * abs(math.sin(phase)) if phase is not None else 0
    c.set_source_rgb(*m(INK))
    c.set_line_width(30)
    for sgn in (-1, 1):
        c.move_to(sgn * 20, -110)
        c.line_to(sgn * 20 + sw * sgn, -14)
        c.stroke()
    c.translate(0, bobv)
    col = m(st["col"])
    c.set_source_rgb(*col)
    if st["shape"] == "rect":
        rrect(c, -58, -320, 116, 226, 38)
    elif st["shape"] == "round":
        ell(c, 0, -212, 80, 114)
    else:
        rrect(c, -48, -322, 96, 130, 40)
        ell(c, 0, -178, 86, 88)
    c.fill()
    c.set_line_width(28)
    for sgn in (-1, 1):
        hx, hy = sgn * 70 - sw * 0.5 * sgn, -178
        if carry and sgn == face:
            hx, hy = sgn * 84, -230
        c.set_source_rgb(*mix(col, (0, 0, 0), 0.12))
        c.move_to(sgn * 54, -286)
        c.line_to(hx, hy)
        c.stroke()
        c.set_source_rgb(*m(st["skin"]))
        c.arc(hx, hy, 15, 0, 2 * math.pi)
        c.fill()
        if carry and sgn == face:
            c.set_source_rgb(*m(ORANGE))
            c.arc(hx + sgn * 6, hy - 22, 20, 0, 2 * math.pi)
            c.fill()
    c.set_source_rgb(*m(st["skin"]))
    c.arc(0, -372, 46, 0, 2 * math.pi)
    c.fill()
    hair = st["hair"]
    c.set_source_rgb(*m(INK))
    if hair in ("cap", "bun"):
        c.arc(0, -372, 48, math.radians(195), math.radians(345))
        c.close_path()
        c.fill()
    if hair == "bun":
        c.arc(0, -424, 18, 0, 2 * math.pi)
        c.fill()
    if hair == "wrap":
        c.set_source_rgb(*m(OCHRE))
        ell(c, 0, -398, 52, 30)
        c.fill()
        c.arc(30 * -face, -424, 16, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgb(*m(INK))
    for dx in (-14, 14):
        c.arc(face * 10 + dx, -372, 5, 0, 2 * math.pi)
        c.fill()
    c.set_line_width(5)
    c.arc(face * 10, -362, 12, 0.2 * math.pi, 0.8 * math.pi)
    c.stroke()
    c.restore()


def passers(c, t, sched):
    for t0, si, spd in sched:
        x = -120 + (t - t0) * spd
        if -150 < x < 2100:
            figure(c, x, GY, 0.78, STY[si % len(STY)], phase=(t - t0) * spd / 26, face=1, mute=0.45)


def stream(c, t, arrivals, front=330, spd=260):
    served = 0
    for k, a in enumerate(arrivals):
        st = STY[(k * 3 + 1) % len(STY)]
        d = a + 1.3
        if t < a:
            x = front - (a - t) * spd
            if x > -500:
                figure(c, x, 884, 1.0, st, phase=(t - a) * spd / 26, face=1)
        elif t < d:
            figure(c, front, 884, 1.0, st, face=1, carry=t > a + 0.75)
        else:
            x = front - (t - d) * spd
            if x > -500:
                figure(c, x, 926, 1.06, st, phase=(t - d) * spd / 26, face=-1, carry=True)
        if t >= a + 0.75:
            served += 1
    return served


def meter(c, n, bump=0.0):
    x0, y0 = 1500, 34
    c.set_source_rgba(1, 1, 1, 0.62)
    rrect(c, x0, y0, 380, 206, 28)
    c.fill()
    text(c, "CUSTOMERS TODAY", x0 + 190, y0 + 52, 28, INK, 0.62)
    c.save()
    c.translate(x0 + 190, y0 + 134)
    k = 1 + 0.4 * math.sin(math.pi * bump)
    c.scale(k, k)
    text(c, str(n), 0, 36, 104, CLAY_D if n == 0 else GREEN)
    c.restore()


def tag(c, s, pop=0.0):
    c.select_font_face(FONT)
    c.set_font_size(34)
    wd = c.text_extents(s).width
    c.save()
    c.translate(60, 81)
    k = 1 + 0.25 * math.sin(math.pi * pop)
    c.scale(k, k)
    c.set_source_rgb(*INK)
    rrect(c, 0, -31, wd + 56, 62, 31)
    c.fill()
    text(c, s, 28, 12, 34, CREAM, 1, "l")
    c.restore()


def caption(c, t, s, a, b, dark=False, y0=990, size=70, col=None):
    if t < a or t > b:
        return
    k = ease(seg(t, a, a + 0.35)) * (1 - ease(seg(t, b - 0.3, b)))
    y = y0 + 18 * (1 - ease(seg(t, a, a + 0.35)))
    if dark:
        text(c, s, W / 2, y, size, col or CREAM, k)
    else:
        text(c, s, W / 2 + 3, y + 4, size, CREAM, 0.7 * k)
        text(c, s, W / 2, y, size, col or INK, k)


def world_begin(c, sky=SKY, sun=(300, 230, 1.0), cam=0.0, zoom=1.0, stars=0.0):
    c.set_source_rgb(*sky)
    c.paint()
    if stars > 0:
        for x, y, r in STARS:
            c.set_source_rgba(1, 1, 1, stars)
            c.arc(x, y, r, 0, 2 * math.pi)
            c.fill()
    c.set_source_rgba(1, 0.97, 0.88, 0.9 * sun[2])
    c.arc(sun[0], sun[1], 70, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*GROUND)
    c.rectangle(0, GY, W, 220)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, GY, W, 7)
    c.fill()
    c.save()
    c.translate(W * (1 - zoom), GY * (1 - zoom))
    c.scale(zoom, zoom)
    c.translate(-cam, 0)
    far_stalls(c)


def world_end(c):
    c.restore()


def tint(c, col, a):
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


def rain(c, t, k, slant=0.18, speed=1500, col=(0.85, 0.90, 0.95)):
    if k <= 0:
        return
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(4)
    c.set_source_rgba(*col, 0.55 * k)
    n = int(len(RAIN) * k)
    for rx, ry, rs in RAIN[:n]:
        y = (ry * 1300 + t * speed * rs) % 1300 - 110
        x = (rx * 2300 - y * slant) % 2300 - 190
        ln = 46 * rs
        c.move_to(x, y)
        c.line_to(x - ln * slant * 1.0, y + ln)
    c.stroke()


def flood(c, t, lvl):
    if lvl <= 0:
        return
    top = GY - lvl
    c.set_source_rgba(0.43, 0.56, 0.64, 0.82)
    c.move_to(0, H)
    c.line_to(0, top)
    for x in range(0, W + 41, 40):
        c.line_to(x, top + 7 * math.sin(x * 0.012 + t * 2.4))
    c.line_to(W, H)
    c.close_path()
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.25)
    c.set_line_width(5)
    for i in range(6):
        x = (i * 370 + t * 60) % (W + 200) - 100
        y = top + 40 + (i % 3) * 50
        c.move_to(x, y)
        c.line_to(x + 90, y)
    c.stroke()


def dip(c, t, dur, col=CREAM, din=0.3, dout=0.3):
    a = max(1 - seg(t, 0, din), seg(t, dur - dout, dur))
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


def wspans(name):
    return [(a, a + PH_LEN[k]) for a, k, _ in WH.get(name, [])]


def whistling(t, name):
    return any(a <= t < b for a, b in wspans(name))


EMPTY = [(0, 0)] * 4


def s1(c, t):
    D = 13
    world_begin(c)
    passers(c, t, [(6.6, 0, 190), (8.4, 3, 170), (10.2, 5, 200)])
    stall(c, t)
    busy = 1 - ease(seg(t, 9.5, 10.3)) * 0.0
    wh = whistling(t, "s1")
    hero(c, t, mood="ok", whistle=wh, busy=1.0)
    notes(c, t, wspans("s1"), 520)
    world_end(c)
    meter(c, 0)
    tag(c, "DAY 1", seg(t, 3.9, 4.3))
    caption(c, t, "For 40 days, nobody stopped.", 0.4, 3.7)
    caption(c, t, "Day 1. I opened my stall.", 4.3, 7.6)
    caption(c, t, "People walked past.", 8.4, 12.5)
    dip(c, t, D)


def s2(c, t):
    D = 13
    d20 = t >= 6.5
    world_begin(c, sun=(300 + 40 * t, 230, 1.0))
    passers(c, t, [(-2.0, 1, 180), (0.8, 4, 200), (3.2, 2, 170), (5.4, 6, 190), (7.6, 0, 180), (9.4, 3, 210), (11.0, 5, 175)])
    stall(c, t)
    wh = whistling(t, "s2")
    hero(c, t, mood="ok" if t < 4.5 else "worried", whistle=wh, busy=0.0)
    notes(c, t, wspans("s2"), 520)
    world_end(c)
    tint(c, (0.16, 0.18, 0.32), 0.14 * ease(seg(t, 6.5, 12)))
    meter(c, 0, seg(t, 6.5, 6.9))
    tag(c, "DAY 20" if d20 else "DAY 5", seg(t, 6.5, 6.9) if d20 else seg(t, 0.2, 0.6))
    caption(c, t, "Day 5. Nobody.", 0.8, 5.2)
    caption(c, t, "Day 20. Still nobody.", 7.0, 12.4)
    dip(c, t, D)


def s3(c, t):
    D = 13
    rot = ease(seg(t, 0.5, 4.0))
    taken = t >= 6.0
    stock = [(-1 if (i == 0 and taken) else 8, rot) for i in range(4)]
    world_begin(c, sun=(820, 230, 1.0))
    stall(c, t, stock=stock)
    c.set_source_rgb(*SAGE_D)
    rrect(c, 176, 760, 148, 100, 12)
    c.fill()
    hx = lerp(520, 650, ease(seg(t, 4.8, 5.8)))
    hx = lerp(hx, 400, ease(seg(t, 6.4, 8.4)))
    walking = (4.8 < t < 5.8) or (6.4 < t < 8.4)
    tip = 1.25 * ease(seg(t, 8.7, 9.5))
    for j in range(4):
        ft = t - (9.2 + j * 0.28)
        if 0 < ft < 0.7:
            c.set_source_rgb(*ROT)
            c.arc(hx - 120 - 40 * ft, 690 + 260 * ft * ft + 20 * ft, 20, 0, 2 * math.pi)
            c.fill()
    c.set_source_rgb(*mix(SAGE_D, (0, 0, 0), 0.15))
    rrect(c, 166, 752, 168, 24, 10)
    c.fill()
    c.set_source_rgb(*SAGE_D)
    rrect(c, 176, 772, 148, 88, 12)
    c.fill()
    hero(c, t, x=hx, mood="worried" if t < 5 else "tired", busy=ease(seg(t, 5.5, 5.9)) * (0 if taken else 1),
         carry="crate" if taken else None, tip=tip, face=-1 if t > 6.3 else 1,
         walk=t * 9 if walking else None, lean=-0.08 * ease(seg(t, 8.7, 9.5)) * (1 - ease(seg(t, 11, 12))))
    world_end(c)
    tint(c, (0.16, 0.18, 0.32), 0.10)
    meter(c, 0)
    tag(c, "DAY 21", seg(t, 0.2, 0.6))
    caption(c, t, "The fruit went bad.", 0.8, 5.0)
    caption(c, t, "I threw it away.", 6.6, 12.4)
    dip(c, t, D)


def s4(c, t):
    D = 14
    cam = 1150 * (ease(seg(t, 1.0, 3.6)) - ease(seg(t, 9.2, 11.6)))
    world_begin(c, sun=(820 - cam * 0.2, 230, 1.0), cam=cam)
    stall(c, t, stock=EMPTY)
    stall(c, t, ox=1330, wall=(0.45, 0.56, 0.60), wall_d=(0.36, 0.47, 0.52), awn=(OCHRE, CREAM), guitar=False)
    hero(c, t, mood="worried", face=1 if t > 2 else 1)
    figure(c, 1850, GY, 1.0, STY[1], face=-1)
    q = [(1690, 0), (1545, 2), (1400, 4), (1255, 6)]
    for i, (x, si) in enumerate(q):
        figure(c, x - 6 * math.sin(t * 1.3 + i), 884, 1.0, STY[si], face=1, carry=(i == 0 and int(t * 0.7) % 2 == 0))
    for k in range(8):
        ft = (t - 3.2 - k * 0.75)
        if 0 < ft < 1.0:
            text(c, "+1", 1790, 430 - 90 * ft, 54, GREEN, math.sin(math.pi * ft))
    world_end(c)
    tint(c, (0.16, 0.18, 0.32), 0.10)
    meter(c, 0, seg(t, 11.8, 12.2))
    tag(c, "DAY 21")
    caption(c, t, "Next door was full.", 3.6, 8.8)
    caption(c, t, "Mine was empty.", 10.6, 13.6)
    dip(c, t, D)


def s5(c, t):
    D = 13
    k = ease(seg(t, 0.2, 2.2))
    lvl = 78 * ease(seg(t, 3.0, 10.5))
    world_begin(c, sky=mix(SKY, (0.62, 0.68, 0.72), k), sun=(820, 230, 1 - k))
    stall(c, t, stock=[(2, 1), (0, 0), (1, 1), (0, 0)])
    up = ease(seg(t, 1.2, 2.0))
    hero(c, t, mood="worried", rh=(lerp(100, 58, up), lerp(-14, -348, up)), lh=(lerp(-104, -58, up), lerp(-18, -348, up)),
         bob=0)
    for i, x0 in enumerate((640, 330)):
        dx = -70 * max(0, t - 4 - i) if lvl > 20 else 0
        c.save()
        c.translate(x0 + dx, GY - 30 - max(0, lvl - 20) + 6 * math.sin(t * 2 + i))
        c.rotate(0.08 * math.sin(t * 1.6 + i) * (1 if lvl > 20 else 0))
        crate_box(c, 3, mix(ORANGE if i else RED, ROT, 0.5))
        c.restore()
    world_end(c)
    flood(c, t, lvl)
    tint(c, (0.14, 0.18, 0.30), 0.30 * k)
    rain(c, t, k)
    if 2.0 < t < 2.25 or 7.4 < t < 7.6:
        tint(c, (1, 1, 1), 0.35)
    meter(c, 0)
    tag(c, "DAY 34", seg(t, 0.2, 0.6))
    caption(c, t, "Then the rain came.", 0.8, 5.0, col=CREAM, dark=True)
    caption(c, t, "It took what was left.", 6.2, 12.2, col=CREAM, dark=True)
    dip(c, t, D)


def s6a(c, t):
    D = 8
    c.set_source_rgb(*INK)
    c.paint()
    text(c, "CUSTOMERS TODAY", W / 2, 120, 44, CREAM, 0.6)
    cw, ch = 200, 138
    x0 = (W - 8 * cw) / 2
    for i in range(40):
        a = 0.4 + 3.3 * (i / 39) ** 0.75
        if t < a:
            continue
        p = seg(t, a, a + 0.25)
        cx = x0 + (i % 8) * cw + cw / 2
        cy = 190 + (i // 8) * ch + ch / 2
        c.set_source_rgba(1, 1, 1, 0.06)
        rrect(c, cx - cw / 2 + 8, cy - ch / 2 + 8, cw - 16, ch - 16, 18)
        c.fill()
        text(c, "DAY %d" % (i + 1), cx, cy - 32, 22, CREAM, 0.5)
        c.save()
        c.translate(cx, cy + 14)
        k = 1 + 0.5 * math.sin(math.pi * p)
        c.scale(k, k)
        text(c, "0", 0, 26, 70, CLAY)
        c.restore()
    caption(c, t, "40 days. Not one customer.", 4.2, 7.7, dark=True, y0=1000)
    dip(c, t, D, col=INK, din=0.3, dout=0.4)


def lantern(c, x):
    c.set_source_rgb(*INK)
    rrect(c, x - 22, GY - 86, 44, 12, 5)
    rrect(c, x - 26, GY - 14, 52, 14, 5)
    c.fill()
    c.set_source_rgb(1.0, 0.86, 0.5)
    rrect(c, x - 18, GY - 76, 36, 64, 8)
    c.fill()


def glow(c, x, y, r, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1.0, 0.80, 0.45, a)
    g.add_color_stop_rgba(1, 1.0, 0.80, 0.45, 0)
    c.set_source(g)
    c.paint()


def s6b(c, t):
    D = 13
    world_begin(c, sky=mix(SKY, NIGHT, 0.55), sun=(1500, 190, 0.5), stars=0.9)
    stall(c, t, stock=EMPTY, tarp=1.0)
    lantern(c, 690)
    hero(c, t, mood="tired", sit=1.0, lean=0.16 + 0.012 * math.sin(t * 1.2), rh=(60, -40), lh=(-60, -40))
    world_end(c)
    tint(c, NIGHT, 0.52)
    glow(c, 690, GY - 50, 430, 0.42 + 0.04 * math.sin(t * 7))
    meter(c, 0)
    tag(c, "NIGHT 40")
    caption(c, t, "I stopped whistling.", 1.0, 5.4, dark=True)
    caption(c, t, "I almost gave up.", 6.8, 12.2, dark=True)
    dip(c, t, D, col=INK)


def s7(c, t):
    D = 12
    k = ease(seg(t, 0.3, 6.0))
    sit = 1 - ease(seg(t, 2.2, 3.4))
    tarp = 1 - ease(seg(t, 5.6, 7.4))
    world_begin(c, sky=mix(mix(SKY, NIGHT, 0.55), SKY, k), sun=(300, lerp(700, 230, k), k), stars=0.9 * (1 - k))
    stall(c, t, stock=[(5, 0)] * 4, tarp=tarp)
    lantern(c, 690)
    reach = ease(seg(t, 5.0, 5.6)) * (1 - ease(seg(t, 7.4, 8.2)))
    hero(c, t, mood="tired" if t < 4.5 else "ok", sit=sit, lean=0.16 * sit, busy=max(reach, ease(seg(t, 8.6, 9.4))),
         rh=(60, -40) if sit > 0.9 else None, lh=(-60, -40) if sit > 0.9 else None)
    world_end(c)
    tint(c, NIGHT, 0.52 * (1 - k))
    tint(c, (0.98, 0.62, 0.40), 0.20 * math.sin(math.pi * k))
    if k < 0.7:
        glow(c, 690, GY - 50, 430, 0.42 * (1 - k / 0.7))
    meter(c, 0)
    tag(c, "DAY 41", seg(t, 4.0, 4.4)) if t >= 4.0 else tag(c, "NIGHT 40")
    caption(c, t, "The next morning,", 1.0, 4.6, dark=t < 3.0)
    caption(c, t, "I opened anyway.", 5.6, 11.4)
    dip(c, t, D, col=INK, dout=0.3)


def s8(c, t):
    D = 14
    world_begin(c)
    passers(c, t, [(-3.0, 2, 180), (6.0, 5, 190)])
    stall(c, t, stock=[(5, 0), (5 if t < 5.2 else 4, 0), (5, 0), (5, 0)])
    cx = lerp(-160, 330, seg(t, 0.6, 3.6))
    leaving = t > 9.0
    if leaving:
        cx = 330 - (t - 9.0) * 230
    give = ease(seg(t, 5.2, 6.0)) * (1 - ease(seg(t, 7.0, 7.6)))
    has = 5.2 <= t < 6.5
    face = -1 if 3.0 < t < 10.0 else 1
    mood = "ok"
    if 3.2 <= t < 5.0:
        mood = "shock"
    elif t >= 5.0:
        mood = "happy"
    wh = whistling(t, "s8")
    busy = ease(seg(t, 4.6, 5.1)) * (1 - ease(seg(t, 5.1, 5.4)))
    hero(c, t, mood=mood, face=face, whistle=wh, busy=busy,
         lh=(lerp(-104, -170, give), lerp(-18, -150, give)) if t >= 5.2 else None,
         carry="orange" if has else None)
    figure(c, cx, 884 if not leaving else 926, 1.0 if not leaving else 1.06, STY[0],
           phase=(t * 9) if (t < 3.6 or leaving) else None, face=-1 if leaving else 1, carry=t >= 6.5)
    ft = seg(t, 6.6, 7.2)
    if 0 < ft < 1:
        c.set_source_rgb(*OCHRE)
        c.arc(lerp(400, 500, ft), 660 - 110 * math.sin(math.pi * ft), 16, 0, 2 * math.pi)
        c.fill()
    notes(c, t, wspans("s8"), 520, face)
    world_end(c)
    n = 1 if t >= 7.2 else 0
    meter(c, n, seg(t, 7.2, 7.8))
    tag(c, "DAY 41")
    caption(c, t, "Someone stopped.", 3.4, 6.8)
    caption(c, t, "One customer. One orange.", 7.8, 13.2)
    dip(c, t, D)


def s9(c, t):
    D = 12
    second = t >= 6.0
    world_begin(c)
    passers(c, t, [(1.5, 6, 185), (8.0, 3, 195)])
    stall(c, t, stock=[(5, 0), (4, 0), (5, 0), (4, 0)] if not second else [(8, 0), (6, 0), (7, 0), (8, 0)])
    arr = [1.2, 3.3] if not second else [6.8, 7.7, 8.6, 9.5, 10.4]
    tt = t
    serving = any(a <= tt < a + 1.3 for a in arr)
    give = 0.0
    for a in arr:
        give = max(give, math.sin(math.pi * seg(tt, a + 0.2, a + 1.1)))
    wh = whistling(t, "s9")
    hero(c, t, mood="happy" if not wh else "ok", face=-1, whistle=wh,
         lh=(lerp(-104, -170, give), lerp(-18, -150, give)), carry="orange" if (serving and give > 0.3 and give < 0.99 and False) else None)
    n = stream(c, t, arr)
    notes(c, t, wspans("s9"), 520, -1)
    world_end(c)
    bump = 0
    for a in arr:
        bump = max(bump, math.sin(math.pi * seg(t, a + 0.75, a + 1.15)))
    meter(c, n, bump / 1.0 if bump > 0 else 0)
    tag(c, "DAY 45" if second else "DAY 42", seg(t, 6.0, 6.4) if second else seg(t, 0.2, 0.6))
    caption(c, t, "Then two.", 1.4, 5.4)
    caption(c, t, "Then five.", 7.4, 11.4)
    dip(c, t, D)


def s10(c, t):
    D = 15
    storm = 1 - ease(seg(t, 5.2, 7.0))
    brk = 0.55 * ease(seg(t, 3.0, 3.35)) * (1 - ease(seg(t, 8.6, 11.6)))
    world_begin(c, sky=mix(SKY, (0.40, 0.44, 0.52), storm * ease(seg(t, 0, 0.6))), sun=(300, 230, 1 - storm))
    stall(c, t, stock=[(7, 0), (6, 0), (7, 0), (6, 0)], brk=brk)
    fixing = t >= 7.6
    hx = lerp(520, 660, ease(seg(t, 6.6, 7.6)))
    ex = 1220 - 500 * math.cos(brk) + 30
    ey = 270 + 500 * math.sin(brk) + 40
    tap = 0.0
    if 11.8 < t < 13.6:
        tap = 0.8 * abs(math.sin((t - 11.8) * math.pi / 0.566))
    wh = whistling(t, "s10")
    if not fixing:
        up = ease(seg(t, 0.6, 1.2)) * storm
        hero(c, t, x=hx, mood="shock" if (t < 6.2) else "worried", walk=t * 9 if 6.6 < t < 7.6 else None,
             rh=(lerp(100, 58, up), lerp(-14, -348, up)), lh=(lerp(-104, -58, up), lerp(-18, -348, up)),
             lean=0.03 * math.sin(t * 9) * storm)
    else:
        lift = 66
        tx, ty = ex - hx, ey - (GY - lift - 120)
        if t > 11.8:
            tx, ty = 100, -400
        hero(c, t, x=hx, mood="ok" if t < 12.4 else "happy", lift=lift, rh=(tx, ty), whistle=wh,
             carry="hammer" if t > 11.6 else None, tip=tap)
    notes(c, t, wspans("s10"), hx)
    world_end(c)
    tint(c, (0.10, 0.12, 0.24), 0.42 * storm * ease(seg(t, 0, 0.6)))
    rain(c, t, storm * ease(seg(t, 0, 0.6)), slant=0.75, speed=1900)
    for a in (1.2, 3.0):
        if a < t < a + 0.22:
            tint(c, (1, 1, 1), 0.45)
    meter(c, 0 if t < 7 else 0)
    tag(c, "DAY 60", seg(t, 0.2, 0.6)) if t < 7.0 else tag(c, "DAY 61", seg(t, 7.0, 7.4))
    caption(c, t, "A storm broke my roof.", 1.6, 5.8, dark=True)
    caption(c, t, "I fixed it.", 7.8, 11.0)
    caption(c, t, "I opened again.", 11.6, 14.5)
    dip(c, t, D)


def s11(c, t):
    D = 13
    zoom = lerp(1.0, 0.84, ease(seg(t, 3.0, 8.5)))
    world_begin(c, zoom=zoom)
    passers(c, t, [(0.5, 3, 190), (5.5, 1, 180)])
    stall(c, t, stock=[(8, 0), (7, 0), (8, 0), (6, 0)])
    wh = whistling(t, "s11")
    cyc = (t % 1.6) / 1.6
    give = math.sin(math.pi * seg(cyc, 0.1, 0.8))
    hero(c, t, mood="happy" if not wh else "ok", face=-1, whistle=wh,
         lh=(lerp(-104, -170, give), lerp(-18, -150, give)), carry="orange" if 0.15 < cyc < 0.5 else None)
    for i in range(6):
        figure(c, 330 - i * 150 - 4 * math.sin(t * 1.2 + i), 884, 1.0, STY[(i * 2 + 1) % len(STY)], face=1,
               carry=(i == 0 and cyc > 0.5))
    if 0.5 < cyc < 0.85:
        ft = seg(cyc, 0.5, 0.85)
        c.set_source_rgb(*OCHRE)
        c.arc(lerp(400, 500, ft), 660 - 110 * math.sin(math.pi * ft), 16, 0, 2 * math.pi)
        c.fill()
    notes(c, t, wspans("s11"), 520, -1)
    world_end(c)
    n = 9 + int(t / 1.6)
    meter(c, n, seg(cyc, 0.82, 1.0) if t > 1.4 else 0)
    tag(c, "DAY 90", seg(t, 0.2, 0.6))
    caption(c, t, "Day 90.", 0.8, 4.0)
    caption(c, t, "I still whistle every morning.", 5.2, 12.2)
    dip(c, t, D, dout=0.5)


def s12(c, t):
    D = 9
    c.set_source_rgb(*INK)
    c.paint()
    k = ease(seg(t, 0.3, 1.0))
    c.set_source_rgba(*ORANGE, k)
    c.arc(W / 2, 330, 46, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*GREEN, k)
    ell(c, W / 2 + 26, 280, 22, 10)
    c.fill()
    caption(c, t, "Some seasons, nothing works.", 0.8, 9.5, dark=True, y0=520, size=84)
    caption(c, t, "Open the stall anyway.", 3.6, 9.5, dark=True, y0=660, size=96, col=OCHRE)
    a = max(1 - seg(t, 0, 0.4), seg(t, D - 0.9, D - 0.1))
    tint(c, (0.05, 0.07, 0.06), a) if t > 1 else tint(c, INK, a)


SC = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6a=s6a, s6b=s6b, s7=s7, s8=s8, s9=s9, s10=s10, s11=s11, s12=s12)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]
        for spec in sys.argv[3:]:
            name, ts = spec.split("@")
            SC[name](c, float(ts))
            surf.write_to_png(os.path.join(out, "%s_%s.png" % (name, ts)))
        return
    out = sys.argv[2]
    names = sys.argv[3:] or [n for n, _ in DURS]
    durs = dict(DURS)
    for name in names:
        tmp = os.path.join(out, name + ".part.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0",
                              "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                              "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(int(durs[name] * FPS)):
            SC[name](c, i / FPS)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
        p.stdin.close()
        if p.wait() != 0:
            sys.exit(1)
        os.rename(tmp, os.path.join(out, name + ".mp4"))
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
