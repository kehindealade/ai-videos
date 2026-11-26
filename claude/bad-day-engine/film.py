import cairo, math, sys, subprocess, os, random
from timeline import DURS

W, H, FPS = 1920, 1080, 30
FONT = "Rounded Mplus 1c ExtraBold"
GY = 860

INK = (0.09, 0.16, 0.20)
SAND = (0.93, 0.88, 0.77)
SAND_D = (0.85, 0.77, 0.61)
TEAL = (0.18, 0.50, 0.53)
TEAL_D = (0.12, 0.35, 0.38)
SEA = (0.74, 0.85, 0.82)
SEA_D = (0.60, 0.75, 0.73)
CORAL = (0.91, 0.38, 0.30)
CORAL_D = (0.74, 0.27, 0.22)
CREAM = (0.98, 0.95, 0.89)
AMBER = (0.96, 0.72, 0.38)
SKIN = (0.56, 0.36, 0.24)
WOOD = (0.66, 0.50, 0.36)
WOOD_D = (0.50, 0.37, 0.27)
STEEL = (0.45, 0.55, 0.62)
STEEL_D = (0.33, 0.42, 0.49)
NIGHT = (0.04, 0.10, 0.16)
FLOOR = (0.80, 0.75, 0.64)
PAVE = (0.84, 0.78, 0.66)

STY = [
    dict(col=(0.86, 0.66, 0.52), shape="round", skin=(0.40, 0.25, 0.16), hair="afro"),
    dict(col=(0.42, 0.52, 0.66), shape="rect", skin=(0.66, 0.46, 0.32), hair="bald"),
    dict(col=(0.93, 0.82, 0.60), shape="rect", skin=(0.33, 0.21, 0.14), hair="short"),
    dict(col=(0.56, 0.44, 0.56), shape="round", skin=(0.50, 0.32, 0.20), hair="puffs"),
    dict(col=(0.50, 0.68, 0.62), shape="rect", skin=(0.72, 0.52, 0.38), hair="afro"),
]
WORK = [
    dict(col=STEEL, shape="rect", skin=(0.38, 0.24, 0.15), hair="short", bib=1),
    dict(col=STEEL, shape="round", skin=(0.68, 0.48, 0.34), hair="afro", bib=1),
    dict(col=STEEL, shape="rect", skin=(0.48, 0.30, 0.19), hair="bald", bib=1),
]
BOSS = dict(col=(0.22, 0.26, 0.36), shape="rect", skin=(0.62, 0.42, 0.30), hair="bald", tie=1, glasses=1)
VENDOR = dict(col=(0.95, 0.90, 0.80), shape="round", skin=(0.36, 0.23, 0.15), hair="puffs")

random.seed(11)
STARS = [(random.random() * W, random.random() * 420, 1.5 + 2 * random.random()) for _ in range(60)]
BCOL = [(0.90, 0.82, 0.68), (0.72, 0.83, 0.80), (0.94, 0.78, 0.70), (0.86, 0.87, 0.78), (0.80, 0.74, 0.62),
        (0.66, 0.78, 0.78)]
BUILD = []
_x = 860
_i = 0
while _x < 6200:
    _w = random.randint(320, 520)
    BUILD.append((_x, _w, random.randint(380, 560), BCOL[_i % len(BCOL)], random.random()))
    _x += _w + random.randint(0, 40)
    _i += 1
FARB = [(i * 260 + random.randint(-30, 30), random.randint(170, 240), random.randint(430, 640)) for i in range(-2, 22)]

UI = {}
DRAW_UI = True


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


def pulse(t, a, d=0.5):
    return math.sin(math.pi * seg(t, a, a + d)) if a <= t <= a + d else 0.0


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
    elif align == "r":
        x = x - e.width - e.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, alpha)
    c.show_text(s)
    return e.width


def tint(c, col, a):
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


def glow(c, x, y, r, a, col=(1.0, 0.80, 0.45)):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g)
    c.paint()


def dip(c, t, dur, col=CREAM, din=0.3, dout=0.3):
    a = max(1 - seg(t, 0, din), seg(t, dur - dout, dur))
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


def head(c, t, mood="ok", face=1, cap=True, look=0.0):
    c.set_source_rgb(*SKIN)
    c.arc(0, 0, 62, 0, 2 * math.pi)
    c.fill()
    c.arc(-60, 8, 12, 0, 2 * math.pi)
    c.arc(60, 8, 12, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    if cap:
        c.set_source_rgb(*CORAL)
        c.arc(0, -8, 65, math.pi, 2 * math.pi)
        c.close_path()
        c.fill()
        rrect(c, 20 if face > 0 else -104, -22, 84, 18, 9)
        c.fill()
        c.set_source_rgb(*CORAL_D)
        c.rectangle(-65, -20, 130, 12)
        c.fill()
        c.set_source_rgb(*CREAM)
        c.arc(0, -70, 7, 0, 2 * math.pi)
        c.fill()
    else:
        c.arc(0, -4, 64, math.radians(188), math.radians(352))
        c.close_path()
        c.fill()
    ex = 10 * face
    ey = 10
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if mood == "sleep":
        c.set_source_rgb(*INK)
        for dx in (-22, 22):
            c.arc(ex + dx, ey - 2, 10, 0.1 * math.pi, 0.9 * math.pi)
            c.stroke()
        c.move_to(ex - 9, 42)
        c.line_to(ex + 9, 42)
        c.stroke()
        return
    big = 1.25 if mood == "shock" else 1.0
    blink = 0.15 if (mood != "shock" and (t % 3.3) < 0.12) else 1.0
    dy = 4 * look + (4 if mood in ("hurt", "tired") else 0)
    for dx in (-22, 22):
        c.set_source_rgb(*CREAM)
        ell(c, ex + dx, ey, 11 * big, 13 * big * blink)
        c.fill()
        c.set_source_rgb(*INK)
        ell(c, ex + dx + 2 * face, ey + 1 + dy * blink, 5.5, 6.5 * blink)
        c.fill()
        if mood == "tired":
            c.set_source_rgb(*SKIN)
            c.rectangle(ex + dx - 14, ey - 16, 28, 14)
            c.fill()
            c.set_source_rgb(*INK)
            c.move_to(ex + dx - 12, ey - 2)
            c.line_to(ex + dx + 12, ey - 2)
            c.stroke()
    c.set_source_rgb(*INK)
    for dx in (-22, 22):
        inner = -1 if dx > 0 else 1
        if mood == "shock":
            a = b = -20
        elif mood in ("hurt", "try", "tired"):
            k = 9 if mood != "try" else 6
            a, b = (-10, -10 - k) if inner > 0 else (-10 - k, -10)
        elif mood == "angry":
            a, b = (-17, -7) if inner > 0 else (-7, -17)
        else:
            a = b = -12
        if cap and mood != "shock":
            a, b = a + 6, b + 6
        c.move_to(ex + dx - 11, ey + a)
        c.line_to(ex + dx + 11, ey + b)
        c.stroke()
    if mood == "shock":
        ell(c, ex, 42, 9, 12)
        c.fill()
    elif mood in ("hurt", "tired"):
        c.arc(ex, 52, 13, 1.2 * math.pi, 1.8 * math.pi)
        c.stroke()
    elif mood == "angry":
        c.move_to(ex - 13, 42)
        c.line_to(ex + 13, 42)
        c.stroke()
    elif mood == "try":
        c.move_to(ex - 13, 40)
        c.curve_to(ex - 4, 44, ex + 6, 44, ex + 13, 38)
        c.stroke()
    elif mood == "eat":
        ell(c, ex + 4 * face, 42, 8, 7)
        c.fill()
    else:
        c.arc(ex, 30, 14, 0.2 * math.pi, 0.8 * math.pi)
        c.stroke()


def wrench(c, x, y, ang, s=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.set_source_rgb(*STEEL_D)
    rrect(c, -7, -84, 14, 96, 6)
    c.fill()
    c.arc(0, -90, 20, 0, 2 * math.pi)
    c.fill()
    c.set_operator(cairo.OPERATOR_OVER)
    c.set_source_rgb(*mix(STEEL_D, CREAM, 0.75))
    c.rectangle(-7, -112, 14, 22)
    c.fill()
    c.restore()


def plate(c, x, y, full=1.0):
    c.set_source_rgb(*AMBER)
    if full > 0:
        ell(c, x, y - 8, 34 * (0.6 + 0.4 * full), 18 * full)
        c.fill()
    c.set_source_rgb(*CREAM)
    ell(c, x, y, 52, 12)
    c.fill()
    c.set_source_rgba(*INK, 0.15)
    ell(c, x, y + 3, 40, 6)
    c.fill()


def hero(c, t, x=860, mood="ok", face=1, sit=0.0, lean=0.0, rh=None, lh=None, walk=None, cap=True,
         hold=None, hang=0.0, look=0.0, y=GY, jit=0.0, shadow=True, food=1.0):
    if shadow:
        c.set_source_rgba(*INK, 0.14)
        ell(c, x, y + 6, 125, 12)
        c.fill()
    drop = 62 * sit + (5 * abs(math.sin(walk)) if walk is not None else 0)
    c.save()
    c.translate(x + jit, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    for sgn in (-1, 1):
        sw = 24 * math.sin(walk) * sgn if walk is not None else 0
        fx = sgn * 36 + sw + face * 86 * sit
        c.set_source_rgb(*TEAL_D)
        c.set_line_width(42)
        c.move_to(sgn * 36, -128 + drop)
        if sit > 0.05:
            c.line_to(sgn * 36 + face * 80 * sit, -122 + drop)
        c.line_to(fx, -24)
        c.stroke()
        c.set_source_rgb(*INK)
        rrect(c, fx - 30 + (8 * face), -30, 68, 30, 14)
        c.fill()
    c.translate(0, -120 + drop)
    c.rotate(lean * face)

    def shape():
        rrect(c, -52, -216, 104, 150, 46)
        ell(c, 0, -72, 112, 96)

    c.set_source_rgb(*CREAM)
    shape()
    c.fill()
    c.save()
    shape()
    c.clip()
    c.set_source_rgb(*TEAL)
    c.rectangle(-130, -112, 260, 160)
    c.fill()
    c.restore()
    c.set_source_rgb(*TEAL)
    rrect(c, -44, -172, 88, 80, 12)
    c.fill()
    c.set_line_width(14)
    for sgn in (-1, 1):
        c.move_to(sgn * 34, -168)
        c.line_to(sgn * 40, -212)
        c.stroke()
    c.set_source_rgb(*TEAL_D)
    rrect(c, -24, -146, 48, 36, 8)
    c.fill()
    c.set_source_rgb(*CREAM)
    for sgn in (-1, 1):
        c.arc(sgn * 34, -160, 5, 0, 2 * math.pi)
        c.fill()

    dl = (-112 + 16 * hang, -30 + 14 * hang)
    dr = (112 - 16 * hang, -30 + 14 * hang)
    if sit > 0.5 and rh is None and lh is None:
        dl, dr = (-50 + face * 40, -52), (50 + face * 40, -52)
    lhp = lh or dl
    rhp = rh or dr

    def arm(sx, hand):
        c.set_source_rgb(*CREAM)
        c.set_line_width(36)
        c.move_to(sx, -178)
        mx = (sx + hand[0]) / 2 + (24 if sx > 0 else -24)
        c.curve_to(mx, -150, mx, hand[1] - 40 if hand[1] > -176 else hand[1] + 60, hand[0], hand[1])
        c.stroke()
        c.set_source_rgb(*SKIN)
        c.arc(hand[0], hand[1], 19, 0, 2 * math.pi)
        c.fill()

    front = rhp if face > 0 else lhp
    back = lhp if face > 0 else rhp
    arm(-54, lhp)
    arm(54, rhp)
    if hold == "wrench":
        wrench(c, front[0] + 6 * face, front[1] + 4, 0.9 * face)
        c.set_source_rgb(*SKIN)
        c.arc(front[0], front[1], 19, 0, 2 * math.pi)
        c.fill()
    if hold in ("plate", "tin"):
        px_, py_ = back[0] + face * 26, back[1] - 8
        if hold == "plate":
            plate(c, px_, py_, food)
        else:
            c.set_source_rgb(*STEEL)
            rrect(c, px_ - 40, py_ - 22, 80, 34, 8)
            c.fill()
            c.set_source_rgb(*AMBER)
            rrect(c, px_ - 34, py_ - 26, 68, 10, 5)
            c.fill()
        c.set_source_rgb(*mix(STEEL_D, CREAM, 0.6))
        c.set_line_width(7)
        c.move_to(front[0], front[1])
        c.line_to(front[0] - face * 4, front[1] - 34)
        c.stroke()
        ell(c, front[0] - face * 4, front[1] - 40, 8, 11)
        c.fill()
    if hold == "cap":
        mx, my = (lhp[0] + rhp[0]) / 2, (lhp[1] + rhp[1]) / 2 + 6
        c.set_source_rgb(*CORAL)
        c.arc(mx, my, 44, math.pi, 2 * math.pi)
        c.close_path()
        c.fill()
        rrect(c, mx + (10 if face > 0 else -80), my - 10, 70, 14, 7)
        c.fill()
    c.translate(0, -262)
    c.rotate(lean * face * 1.3 + 0.10 * look * face)
    head(c, t, mood, face, cap, look)
    c.restore()


def figure(c, x, feet, s, st, phase=None, face=1, jump=0.0, arms=0.0, mouth="smile", point=None, lean=0.0,
           look=0.0, hold=None):
    c.save()
    c.translate(x, feet)
    c.set_source_rgba(*INK, 0.12)
    ell(c, 0, 5, 80 * s, 9 * s)
    c.fill()
    c.translate(0, -jump)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    sw = 26 * math.sin(phase) if phase is not None else 0
    bobv = -6 * abs(math.sin(phase)) if phase is not None else 0
    col = st["col"]
    c.set_source_rgb(*(mix(col, INK, 0.25) if st.get("bib") else mix(INK, col, 0.18)))
    c.set_line_width(30)
    for sgn in (-1, 1):
        c.move_to(sgn * 20, -110)
        c.line_to(sgn * 20 + sw * sgn, -14)
        c.stroke()
    c.translate(0, bobv - 100)
    c.rotate(lean * face)
    c.translate(0, 100)
    c.set_source_rgb(*col)
    if st["shape"] == "rect":
        rrect(c, -58, -320, 116, 226, 38)
    else:
        ell(c, 0, -212, 80, 114)
    c.fill()
    if st.get("bib"):
        c.set_source_rgb(*mix(col, INK, 0.25))
        rrect(c, -34, -270, 68, 120, 10)
        c.fill()
    if st.get("tie"):
        c.set_source_rgb(*CREAM)
        c.move_to(-26, -318)
        c.line_to(26, -318)
        c.line_to(0, -270)
        c.close_path()
        c.fill()
        c.set_source_rgb(*CORAL_D)
        c.move_to(-9, -306)
        c.line_to(9, -306)
        c.line_to(12, -224)
        c.line_to(0, -206)
        c.line_to(-12, -224)
        c.close_path()
        c.fill()
    c.set_line_width(28)
    for sgn in (-1, 1):
        hx, hy = sgn * 70 - sw * 0.5 * sgn, -178
        if arms > 0:
            hx, hy = lerp(hx, sgn * 96, arms), lerp(hy, -420, arms)
        if point is not None and sgn == face:
            hx, hy = point
        if hold and sgn == face:
            hx, hy = sgn * 86, -236
        c.set_source_rgb(*mix(col, (0, 0, 0), 0.12))
        c.move_to(sgn * 54, -286)
        c.line_to(hx, hy)
        c.stroke()
        c.set_source_rgb(*st["skin"])
        c.arc(hx, hy, 15, 0, 2 * math.pi)
        c.fill()
        if hold == "plate" and sgn == face:
            plate(c, hx + sgn * 30, hy - 14)
    c.set_source_rgb(*st["skin"])
    c.arc(0, -372, 46, 0, 2 * math.pi)
    c.fill()
    hair = st["hair"]
    c.set_source_rgb(*INK)
    if hair == "afro":
        c.arc(0, -392, 54, math.radians(170), math.radians(370))
        c.close_path()
        c.fill()
    elif hair == "short":
        c.arc(0, -372, 48, math.radians(195), math.radians(345))
        c.close_path()
        c.fill()
    elif hair == "puffs":
        c.arc(0, -372, 48, math.radians(195), math.radians(345))
        c.close_path()
        c.fill()
        c.arc(-44, -410, 22, 0, 2 * math.pi)
        c.arc(44, -410, 22, 0, 2 * math.pi)
        c.fill()
    fx = face * 10
    for dx in (-14, 14):
        c.arc(fx + dx, -374 + 3 * look, 5, 0, 2 * math.pi)
        c.fill()
    if st.get("glasses"):
        c.set_line_width(4)
        for dx in (-14, 14):
            c.arc(fx + dx, -374, 12, 0, 2 * math.pi)
            c.stroke()
    c.set_line_width(5)
    if mouth == "open":
        ell(c, fx, -348, 13, 15)
        c.fill()
        c.set_line_width(6)
        for dx in (-14, 14):
            sg = 1 if dx > 0 else -1
            c.move_to(fx + dx - 10, -392 - 4 * sg * face * -1)
            c.line_to(fx + dx + 10, -392 + 4 * sg * face * -1)
            c.stroke()
    elif mouth == "laugh":
        c.arc(fx, -360, 14, 0, math.pi)
        c.close_path()
        c.fill()
    elif mouth == "flat":
        c.move_to(fx - 10, -352)
        c.line_to(fx + 10, -352)
        c.stroke()
    else:
        c.arc(fx, -362, 12, 0.2 * math.pi, 0.8 * math.pi)
        c.stroke()
    c.restore()


def burst(c, x, y, r, a=1.0, n=10, col=CORAL):
    c.save()
    c.translate(x, y)
    c.set_source_rgba(*col, a)
    for i in range(n * 2):
        ang = i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.62
        (c.move_to if i == 0 else c.line_to)(rr * math.cos(ang), rr * math.sin(ang))
    c.close_path()
    c.fill()
    c.set_source_rgba(*CREAM, a)
    rrect(c, -r * 0.09, -r * 0.36, r * 0.18, r * 0.42, r * 0.08)
    c.fill()
    c.arc(0, r * 0.26, r * 0.11, 0, 2 * math.pi)
    c.fill()
    c.restore()


def ha(c, t, x, y, t0, n=4, gap=0.45, col=INK):
    for i in range(n):
        ft = seg(t, t0 + i * gap, t0 + i * gap + 0.9)
        if 0 < ft < 1:
            text(c, "HA", x + (i % 2) * 70 - 35, y - 70 * ft - (i % 2) * 24, 40, col, math.sin(math.pi * ft))


def note(c, x, y, s, a, col=INK):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(*col, a)
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


def tyres(c, x, n=3, y=GY):
    for i in range(n):
        c.set_source_rgb(*INK)
        rrect(c, x - 80, y - 46 * (i + 1), 160, 44, 20)
        c.fill()
        c.set_source_rgba(1, 1, 1, 0.10)
        rrect(c, x - 60, y - 46 * (i + 1) + 8, 120, 8, 4)
        c.fill()


def clock(c, x, y, hour):
    c.set_source_rgb(*INK)
    c.arc(x, y, 56, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.arc(x, y, 46, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for ang, ln, lw in (((hour % 12) / 12 * 2 * math.pi, 24, 8), ((hour % 1) * 2 * math.pi, 36, 6)):
        c.set_line_width(lw)
        c.move_to(x, y)
        c.line_to(x + ln * math.sin(ang), y - ln * math.cos(ang))
        c.stroke()


def car(c):
    c.set_source_rgba(*INK, 0.14)
    ell(c, 1390, GY + 6, 420, 14)
    c.fill()
    c.set_source_rgb(*STEEL)
    c.move_to(1200, 610)
    c.line_to(1270, 470)
    c.line_to(1580, 470)
    c.line_to(1670, 610)
    c.close_path()
    c.fill()
    rrect(c, 1010, 596, 780, 200, 46)
    c.fill()
    c.set_source_rgb(*SEA)
    c.move_to(1238, 600)
    c.line_to(1290, 496)
    c.line_to(1410, 496)
    c.line_to(1410, 600)
    c.close_path()
    c.fill()
    c.move_to(1434, 600)
    c.line_to(1434, 496)
    c.line_to(1564, 496)
    c.line_to(1630, 600)
    c.close_path()
    c.fill()
    c.set_source_rgb(*STEEL_D)
    c.rectangle(1010, 740, 780, 14)
    c.fill()
    c.save()
    c.translate(1200, 606)
    c.rotate(-0.95)
    c.set_source_rgb(*STEEL_D)
    rrect(c, -190, -14, 196, 24, 12)
    c.fill()
    c.restore()
    c.set_source_rgb(*INK)
    rrect(c, 1020, 600, 150, 40, 10)
    c.fill()
    c.set_source_rgb(*AMBER)
    ell(c, 1024, 680, 12, 22)
    c.fill()
    for wx in (1170, 1630):
        c.set_source_rgb(*INK)
        c.arc(wx, 790, 74, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*mix(STEEL, CREAM, 0.5))
        c.arc(wx, 790, 34, 0, 2 * math.pi)
        c.fill()


def workshop(c, t, hour=8.0, sky=(0.95, 0.90, 0.78), bench=False):
    c.set_source_rgb(*SEA)
    c.paint()
    c.set_source_rgb(*sky)
    c.rectangle(0, 240, 320, 620)
    c.fill()
    c.set_source_rgba(1, 0.97, 0.86, 0.9)
    c.arc(150, lerp(520, 330, clamp((hour - 7) / 6)), 54, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*mix(sky, TEAL_D, 0.22))
    for x, w, h in ((-40, 150, 250), (120, 120, 180), (240, 100, 300)):
        c.rectangle(x, GY - h, min(w, 320 - x), h)
        c.fill()
    c.set_source_rgb(*PAVE)
    c.rectangle(0, 800, 320, 60)
    c.fill()
    c.set_source_rgb(*TEAL_D)
    c.rectangle(320, 210, 26, 650)
    c.rectangle(0, 210, 346, 34)
    c.fill()
    c.set_source_rgb(*SEA_D)
    c.rectangle(346, 650, W, 210)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(346, 650, W, 8)
    c.fill()
    c.set_source_rgb(*SAND_D)
    rrect(c, 430, 290, 360, 260, 16)
    c.fill()
    c.set_source_rgb(*INK)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i, x in enumerate((480, 550, 620, 690, 750)):
        c.set_line_width(12)
        c.move_to(x, 340)
        c.line_to(x, 440 + (i % 3) * 30)
        c.stroke()
        if i % 2 == 0:
            c.arc(x, 334, 16, 0, 2 * math.pi)
            c.fill()
        else:
            rrect(c, x - 22, 322, 44, 22, 6)
            c.fill()
    clock(c, 940, 330, hour)
    for x in (700, 1300):
        c.set_source_rgb(*INK)
        c.rectangle(x - 3, 0, 6, 110)
        c.fill()
        c.move_to(x - 60, 150)
        c.line_to(x - 26, 104)
        c.line_to(x + 26, 104)
        c.line_to(x + 60, 150)
        c.close_path()
        c.fill()
        c.set_source_rgb(*AMBER)
        ell(c, x, 152, 40, 10)
        c.fill()
    c.set_source_rgb(*FLOOR)
    c.rectangle(0, GY, W, 220)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, GY, W, 7)
    c.fill()
    car(c)
    tyres(c, 470, 2)
    if bench:
        c.set_source_rgb(*WOOD_D)
        c.rectangle(1160, 720, 26, 150)
        c.rectangle(1764, 720, 26, 150)
        c.fill()
        c.set_source_rgb(*WOOD)
        rrect(c, 1120, 690, 710, 40, 12)
        c.fill()


def lamp_post(c, x, on):
    c.set_source_rgb(*INK)
    c.rectangle(x - 7, 330, 14, 530)
    c.fill()
    rrect(c, x - 16, 820, 32, 40, 8)
    c.fill()
    rrect(c, x - 60, 316, 120, 22, 10)
    c.fill()
    c.set_source_rgb(*(AMBER if on else CREAM))
    rrect(c, x - 44, 338, 88, 26, 10)
    c.fill()


def street(c, t, cam=0.0, sky=SAND, dark=0.0, sun=None, stand_open=True, lit=0.0, door_open=True):
    c.set_source_rgb(*sky)
    c.paint()
    if dark > 0.5:
        for x, y, r in STARS:
            c.set_source_rgba(1, 1, 1, 0.9)
            c.arc(x, y, r, 0, 2 * math.pi)
            c.fill()
    if sun:
        c.set_source_rgba(1, 0.95, 0.82, 0.95)
        c.arc(sun[0], sun[1], 70, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgb(*mix(sky, TEAL_D, 0.20 + 0.25 * dark))
    for x, w, h in FARB:
        xx = x - cam * 0.35
        c.rectangle(xx, GY - h, w, h)
        c.fill()
    c.set_source_rgb(*PAVE)
    c.rectangle(0, GY, W, 220)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, GY, W, 7)
    c.fill()
    c.save()
    c.translate(-cam, 0)
    c.set_source_rgb(*SEA)
    c.rectangle(80, 330, 720, 530)
    c.fill()
    c.set_source_rgb(*TEAL_D)
    c.rectangle(60, 310, 760, 30)
    c.fill()
    c.set_source_rgb(*(INK if door_open else STEEL))
    c.rectangle(170, 480, 440, 380)
    c.fill()
    if not door_open:
        c.set_source_rgba(*INK, 0.25)
        for i in range(9):
            c.rectangle(170, 500 + i * 40, 440, 6)
        c.fill()
    c.set_source_rgb(*CREAM)
    rrect(c, 190, 372, 400, 84, 14)
    c.fill()
    text(c, "AUTO REPAIR", 390, 432, 46, TEAL_D)
    tyres(c, 700, 2)
    for bx, bw, bh, col, r in BUILD:
        if bx + bw < cam - 50 or bx > cam + W + 50:
            continue
        c.set_source_rgb(*col)
        c.rectangle(bx, GY - bh, bw, bh)
        c.fill()
        c.set_source_rgb(*mix(col, INK, 0.35))
        c.rectangle(bx - 10, GY - bh - 18, bw + 20, 22)
        c.fill()
        c.set_source_rgb(*mix(col, INK, 0.45))
        rrect(c, bx + bw * 0.5 - 45, GY - 190, 90, 190, 10)
        c.fill()
        nw = 3 if bw > 400 else 2
        for i in range(nw):
            wx = bx + bw * (i + 0.5) / nw - 45
            on = lit > 0 and ((i + int(r * 10)) % 3 != 0)
            for wy in ((GY - bh + 60,) if bh < 460 else (GY - bh + 60, GY - bh + 210)):
                c.set_source_rgb(*(AMBER if on else mix(col, TEAL_D, 0.45)))
                rrect(c, wx, wy, 90, 100, 8)
                c.fill()
    for lx in (1060, 2360, 3700, 5000):
        lamp_post(c, lx, lit > 0)
    c.set_source_rgb(*WOOD_D)
    c.rectangle(1140, 790, 18, 70)
    c.rectangle(1360, 790, 18, 70)
    c.fill()
    c.set_source_rgb(*WOOD)
    rrect(c, 1110, 770, 300, 26, 10)
    c.fill()
    sx = 1780
    c.set_source_rgb(*INK)
    c.rectangle(sx - 5, 350, 10, 400)
    c.fill()
    if stand_open:
        for i in range(6):
            c.set_source_rgb(*(CORAL if i % 2 == 0 else CREAM))
            c.move_to(sx, 330)
            c.line_to(sx - 240 + i * 80, 470)
            c.line_to(sx - 160 + i * 80, 470)
            c.close_path()
            c.fill()
            c.arc(sx - 200 + i * 80, 470, 40, 0, math.pi)
            c.fill()
    else:
        c.set_source_rgb(*CORAL)
        c.move_to(sx, 330)
        c.line_to(sx - 34, 640)
        c.line_to(sx + 34, 640)
        c.close_path()
        c.fill()
    c.restore()


def stand_front(c, t, cam, steam=True):
    c.save()
    c.translate(-cam, 0)
    sx = 1780
    c.set_source_rgb(*INK)
    for wx in (sx - 120, sx + 120):
        c.arc(wx, 826, 36, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgb(*TEAL_D)
    rrect(c, sx - 190, 660, 380, 150, 16)
    c.fill()
    c.set_source_rgb(*CREAM)
    rrect(c, sx - 206, 640, 412, 30, 12)
    c.fill()
    if steam:
        c.set_source_rgb(*STEEL_D)
        rrect(c, sx + 40, 580, 120, 62, 14)
        c.fill()
        c.set_source_rgb(*STEEL)
        rrect(c, sx + 30, 570, 140, 18, 9)
        c.fill()
        c.set_line_width(7)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(3):
            ph = (t * 0.5 + i / 3) % 1
            c.set_source_rgba(1, 1, 1, 0.7 * math.sin(math.pi * ph))
            x0 = sx + 70 + i * 30
            y0 = 560 - 90 * ph
            c.move_to(x0, y0)
            c.curve_to(x0 + 14, y0 - 14, x0 - 14, y0 - 28, x0, y0 - 42)
            c.stroke()
    c.restore()


def goal(c, cam):
    c.save()
    c.translate(-cam, 0)
    gx = 3560
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(*CREAM, 0.55)
    c.set_line_width(4)
    for i in range(1, 7):
        c.move_to(gx + i * 26, 600 + i * 6)
        c.line_to(gx + i * 26, GY)
    for j in range(1, 6):
        c.move_to(gx, 590 + j * 45)
        c.line_to(gx + 180, 626 + j * 39)
    c.stroke()
    c.set_source_rgb(*CREAM)
    c.set_line_width(16)
    c.move_to(gx, GY)
    c.line_to(gx, 590)
    c.line_to(gx + 180, 626)
    c.line_to(gx + 180, GY)
    c.stroke()
    c.restore()


def ball(c, x, y, rot=0.0):
    c.set_source_rgba(*INK, 0.14)
    ell(c, x, GY + 6, 30, 6)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.arc(x, y, 28, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    for i in range(3):
        a = rot + i * 2.09
        c.arc(x + 14 * math.cos(a), y + 14 * math.sin(a), 7, 0, 2 * math.pi)
        c.fill()


def room(c, t, sky=NIGHT, lamp=1.0, radio_on=False, bed="made", moon=True):
    c.set_source_rgb(*SAND)
    c.paint()
    c.set_source_rgb(*SAND_D)
    c.rectangle(0, 700, W, 160)
    c.fill()
    c.set_source_rgb(*TEAL_D)
    rrect(c, 90, 360, 210, 500, 8)
    c.fill()
    c.set_source_rgb(*AMBER)
    c.arc(268, 620, 11, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*CREAM)
    rrect(c, 690, 230, 320, 310, 14)
    c.fill()
    c.set_source_rgb(*sky)
    c.rectangle(710, 250, 280, 270)
    c.fill()
    if moon:
        c.set_source_rgb(0.97, 0.95, 0.85)
        c.arc(900, 330, 34, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*sky)
        c.arc(916, 320, 30, 0, 2 * math.pi)
        c.fill()
        for sx, sy in ((760, 300), (820, 420), (950, 460), (740, 470)):
            c.set_source_rgba(1, 1, 1, 0.8)
            c.arc(sx, sy, 3, 0, 2 * math.pi)
            c.fill()
    c.set_source_rgb(*CREAM)
    c.rectangle(844, 250, 12, 270)
    c.rectangle(710, 378, 280, 12)
    c.fill()
    c.set_source_rgb(*INK)
    c.rectangle(1098, 0, 4, 150)
    c.fill()
    c.set_source_rgb(*TEAL)
    c.move_to(1040, 220)
    c.line_to(1070, 150)
    c.line_to(1130, 150)
    c.line_to(1160, 220)
    c.close_path()
    c.fill()
    c.set_source_rgb(*(AMBER if lamp > 0.5 else mix(CREAM, INK, 0.5)))
    ell(c, 1100, 222, 34, 14)
    c.fill()
    c.set_source_rgb(*INK)
    c.rectangle(1158, 220, 3, 150)
    c.fill()
    c.arc(1159, 376, 8, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*(0.52, 0.66, 0.65))
    c.rectangle(0, GY, W, 220)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, GY, W, 7)
    c.fill()
    c.set_source_rgb(*mix(CORAL, SAND, 0.45))
    ell(c, 900, 902, 430, 26)
    c.fill()
    c.set_source_rgb(*WOOD_D)
    c.rectangle(420, 720, 16, 140)
    c.rectangle(604, 720, 16, 140)
    c.fill()
    c.set_source_rgb(*WOOD)
    rrect(c, 396, 700, 248, 26, 8)
    c.fill()
    c.set_source_rgb(*INK)
    c.set_line_width(5)
    c.move_to(590, 610)
    c.line_to(626, 500)
    c.stroke()
    c.set_source_rgb(*CORAL)
    rrect(c, 430, 604, 180, 98, 16)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.arc(480, 654, 30, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    for i in range(3):
        c.arc(480, 654, 8 + i * 9, 0, 2 * math.pi)
        c.set_line_width(3)
        c.stroke()
    c.set_source_rgb(*(AMBER if radio_on else CORAL_D))
    c.arc(566, 634, 10, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*CREAM)
    rrect(c, 540, 664, 50, 12, 6)
    c.fill()
    c.set_source_rgb(*WOOD_D)
    rrect(c, 1750, 560, 40, 300, 10)
    c.fill()
    c.rectangle(1110, 800, 24, 60)
    c.fill()
    c.set_source_rgb(*WOOD)
    rrect(c, 1090, 780, 690, 36, 10)
    c.fill()
    c.set_source_rgb(*CREAM)
    rrect(c, 1100, 724, 660, 64, 22)
    c.fill()
    if bed == "made":
        c.set_source_rgb(*CREAM)
        rrect(c, 1590, 690, 150, 52, 24)
        c.fill()
        c.set_source_rgba(*INK, 0.08)
        rrect(c, 1590, 728, 150, 14, 7)
        c.fill()
        c.set_source_rgb(*TEAL)
        rrect(c, 1100, 736, 420, 60, 18)
        c.fill()


def meter(c, mode, n=0, val="NO", bump=0.0, shake=0.0, t=0.0):
    UI["meter"] = (mode, n, val, bump, shake, t)
    if DRAW_UI:
        meter_draw(c, 1470, 34, 1.0, *UI["meter"])


def meter_draw(c, x0, y0, k, mode, n, val, bump, shake, t):
    c.save()
    c.translate(x0, y0)
    c.scale(k, k)
    c.set_source_rgba(1, 1, 1, 0.80)
    rrect(c, 0, 0, 410, 200, 28)
    c.fill()
    if mode == "day":
        text(c, "MY DAY", 205, 52, 28, INK, 0.62)
        c.save()
        c.translate(205, 128)
        s = 1 + 0.35 * math.sin(math.pi * bump)
        c.scale(s, s)
        text(c, val, 0, 30, 78, TEAL if val == "FINE" else CORAL)
        c.restore()
    else:
        text(c, "I TRIED", 105, 48, 26, INK, 0.62)
        text(c, "BETTER?", 300, 48, 26, INK, 0.62)
        c.set_source_rgba(*INK, 0.12)
        c.rectangle(203, 26, 4, 148)
        c.fill()
        c.save()
        c.translate(105, 124)
        s = 1 + 0.4 * math.sin(math.pi * bump)
        c.scale(s, s)
        text(c, str(n), 0, 34, 100, TEAL)
        c.restore()
        c.save()
        c.translate(300 + 10 * math.sin(t * 40) * shake, 124)
        s = 1 + 0.25 * shake
        c.scale(s, s)
        text(c, val, 0, 30, 78, CORAL)
        c.restore()
    c.restore()


def tag(c, s, pop=0.0, dark=False):
    UI["tag"] = (s, pop, dark)
    if DRAW_UI:
        tag_draw(c, 60, 81, 34, s, pop, dark)


def tag_draw(c, x, y, size, s, pop, dark=False):
    c.select_font_face(FONT)
    c.set_font_size(size)
    wd = c.text_extents(s).width
    c.save()
    c.translate(x, y)
    k = 1 + 0.25 * math.sin(math.pi * pop)
    c.scale(k, k)
    c.set_source_rgb(*(CREAM if dark else INK))
    rrect(c, 0, -size * 0.92, wd + size * 1.65, size * 1.84, size * 0.92)
    c.fill()
    text(c, s, size * 0.82, size * 0.36, size, INK if dark else CREAM, 1, "l")
    c.restore()


def caption(c, t, s, a, b, dark=False, y0=990, size=70, col=None):
    if t < a or t > b:
        return
    k = ease(seg(t, a, a + 0.35)) * (1 - ease(seg(t, b - 0.3, b)))
    UI.setdefault("caps", []).append((s, k, dark))
    if not DRAW_UI:
        return
    y = y0 + 18 * (1 - ease(seg(t, a, a + 0.35)))
    if dark:
        text(c, s, W / 2, y, size, col or CREAM, k)
    else:
        text(c, s, W / 2 + 3, y + 4, size, CREAM, 0.7 * k)
        text(c, s, W / 2, y, size, col or INK, k)


def try_meter(c, t, n, at=None, fail=None):
    bump = seg(t, at, at + 0.5) if at is not None and t >= at else 0.0
    shake = pulse(t, fail, 0.9) if fail is not None else 0.0
    meter(c, "try", n if (at is None or t >= at) else n - 1, "NO", bump if bump < 1 else 0, shake, t)


def s1(c, t):
    D = 18
    sh = 0.0
    for a in (4.2, 5.6, 7.0, 8.4, 9.8, 11.2):
        sh = max(sh, pulse(t, a, 0.5))
    c.save()
    c.translate(6 * sh * math.sin(t * 60), 4 * sh * math.cos(t * 47))
    workshop(c, t, 8.0)
    watch = [seg(t, 5.2 + i * 0.45, 5.5 + i * 0.45) * (1 - seg(t, 15.2 + i * 0.3, 15.5 + i * 0.3)) for i in range(3)]
    for i, (x, fy) in enumerate(((1400, 896), (1640, 912), (1840, 880))):
        figure(c, x, fy, 0.9, WORK[i], face=-1 if watch[i] > 0.5 else 1, mouth="flat" if watch[i] > 0.5 else "smile")
    shout = 4.2 <= t < 12.4
    bx = lerp(-140, 560, seg(t, 2.0, 4.0))
    if t > 12.8:
        bx = 560 - (t - 12.8) * 300
    talk = shout and (int(t * 5) % 2 == 0)
    if bx > -200:
        figure(c, bx, 884, 1.18, BOSS, phase=t * 9 if (t < 4.0 or t > 12.8) else None, face=-1 if t > 12.8 else 1,
               mouth="open" if talk else "flat", point=(112, -300 + 10 * math.sin(t * 14)) if shout else None,
               lean=0.10 if shout else 0)
    if shout:
        k = 0.75 + 0.25 * abs(math.sin(t * 9))
        burst(c, 706, 356 + 10 * math.sin(t * 7), 78 * k)
        c.set_source_rgb(*CORAL)
        c.set_line_width(9)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(3):
            ph = (t * 1.6 + i / 3) % 1
            xx = 650 + 150 * ph
            c.set_source_rgba(*CORAL, 1 - ph)
            c.move_to(xx, 470 + i * 26)
            c.line_to(xx + 46, 470 + i * 26)
            c.stroke()
    turned = t >= 4.1
    mood = "ok" if t < 4.1 else ("shock" if t < 6.6 else "hurt")
    down = ease(seg(t, 6.6, 9.0))
    busy = 1 - ease(seg(t, 3.9, 4.3))
    if not turned:
        hero(c, t, x=880, mood=mood, face=1, rh=(128, -120 + 12 * math.sin(t * 6)), hold="wrench")
    else:
        hero(c, t, x=880, mood=mood, face=-1, lean=0.07 * down, hang=down, look=down,
             jit=3 * sh * math.sin(t * 50), hold="wrench" if t < 6.6 else None, lh=(-112, -30) if t < 6.6 else None)
    if t >= 6.6:
        ft = seg(t, 6.6, 7.0)
        wrench(c, 770, lerp(700, GY - 6, ft * ft), lerp(-0.9, -1.57, ft))
    c.restore()
    meter(c, "day", 0, "FINE" if t < 4.3 else "RUINED", seg(t, 4.3, 4.9) if 4.3 <= t < 4.9 else 0)
    tag(c, "8:00 AM", seg(t, 0.2, 0.6))
    caption(c, t, "At 8 am, my day was ruined.", 0.4, 4.3)
    caption(c, t, "My boss shouted at me.", 5.0, 9.4)
    caption(c, t, "Everyone watched.", 10.4, 15.0)
    dip(c, t, D)


def s2(c, t):
    D = 13
    workshop(c, t, 10.0)
    glance = seg(t, 6.2, 6.5) * (1 - seg(t, 7.6, 7.9))
    for i, (x, fy) in enumerate(((1400, 896), (1640, 912), (1840, 880))):
        figure(c, x, fy, 0.9, WORK[i], face=-1 if (glance > 0.5 and i < 2) else 1, mouth="flat")
    stop = ease(seg(t, 4.6, 5.4))
    dropped = t >= 5.8
    hero(c, t, x=880, mood="hurt", face=1, rh=(lerp(128, 100, stop), lerp(-120 + 8 * math.sin(t * 3) * (1 - stop), -40, stop)),
         hold=None if dropped else "wrench", look=stop, lean=0.05 * stop, hang=stop * 0.5)
    if dropped:
        ft = seg(t, 5.8, 6.2)
        wrench(c, 1000, lerp(700, GY - 6, ft * ft), lerp(0.9, 1.57, ft))
    for a in (1.4, 2.6, 3.8):
        p = pulse(t, a, 0.9)
        if p > 0:
            burst(c, 770, 395, 50 * (0.7 + 0.3 * p), 0.6 * p, col=CORAL)
    meter(c, "day", 0, "RUINED")
    tag(c, "10:00 AM", seg(t, 0.2, 0.6))
    caption(c, t, "I kept hearing it in my head.", 0.8, 5.2)
    caption(c, t, "Nobody said anything.", 7.2, 12.2)
    dip(c, t, D)


def s3(c, t):
    D = 14
    workshop(c, t, 13.0, bench=False)
    for i, x in enumerate((1260, 1470, 1680)):
        lg = 8 * abs(math.sin(t * 6 + i * 1.3))
        figure(c, x, 880, 0.95, WORK[i], face=(1, -1, -1)[i], jump=lg, mouth="laugh")
    c.set_source_rgb(*WOOD_D)
    c.rectangle(1160, 720, 26, 150)
    c.rectangle(1764, 720, 26, 150)
    c.fill()
    c.set_source_rgb(*WOOD)
    rrect(c, 1120, 690, 710, 40, 12)
    c.fill()
    for x in (1260, 1470, 1680):
        c.set_source_rgb(*STEEL)
        rrect(c, x - 40, 664, 80, 30, 8)
        c.fill()
        c.set_source_rgb(*AMBER)
        rrect(c, x - 34, 658, 68, 10, 5)
        c.fill()
    ha(c, t, 1370, 440, 1.0, n=5, gap=0.5)
    ha(c, t, 1600, 430, 6.4, n=5, gap=0.5)
    lk = ease(seg(t, 2.0, 2.8)) * (1 - ease(seg(t, 5.0, 6.0)))
    hero(c, t, x=470, y=GY - 14, mood="hurt", face=1, sit=1.0, hold="tin", look=1 - lk, lean=0.06 * (1 - lk),
         rh=(96, -66), lh=(40, -58), shadow=False)
    meter(c, "day", 0, "RUINED")
    tag(c, "1:00 PM", seg(t, 0.2, 0.6))
    caption(c, t, "At lunch, I sat alone.", 0.8, 5.6)
    caption(c, t, "I felt it all day.", 7.2, 13.0)
    dip(c, t, D)


EVE = (0.96, 0.84, 0.64)
SUNSET = (0.95, 0.72, 0.56)
DUSK = (0.58, 0.56, 0.66)
NSKY = (0.07, 0.16, 0.24)


def s4(c, t):
    D = 13
    cam = 260 * ease(seg(t, 7.6, 12.6))
    street(c, t, cam, EVE, 0.0, sun=(1500 - cam * 0.2, 300))
    stand_front(c, t, cam)
    x = lerp(400, 1000, seg(t, 0.4, 5.0))
    x = lerp(x, 1560, ease(seg(t, 8.2, 12.8)))
    walking = (0.4 < t < 5.0) or (8.2 < t < 12.6)
    sigh = pulse(t, 5.4, 1.6)
    mood = "hurt" if t < 7.4 else "try"
    hero(c, t, x=x - cam, mood=mood, face=1, walk=t * 7.5 if walking else None, hang=1 - seg(t, 7.2, 7.8) * 0.6,
         look=1 - ease(seg(t, 7.0, 7.6)), lean=0.05 * (1 - seg(t, 7.0, 7.6)) + 0.03 * sigh)
    tint(c, (0.98, 0.62, 0.35), 0.08)
    if t < 7.6:
        meter(c, "day", 0, "RUINED")
    else:
        meter(c, "try", 0, "NO", seg(t, 7.6, 8.1) if t < 8.1 else 0, 0, t)
    tag(c, "5:30 PM", seg(t, 0.2, 0.6))
    caption(c, t, "At 5:30, work was over.", 0.8, 4.8)
    caption(c, t, "After work, I tried to fix it.", 6.2, 12.2)
    dip(c, t, D)


def s5(c, t):
    D = 16
    cam = 700
    street(c, t, cam, SUNSET, 0.10, sun=(1560, 520))
    figure(c, 1900 - cam, 870, 0.95, VENDOR, face=-1, hold="plate" if 2.4 < t < 3.6 else None, mouth="smile")
    stand_front(c, t, cam)
    x = lerp(-140, 880, seg(t, 0.2, 2.6))
    x = lerp(x, 560, ease(seg(t, 4.4, 6.0)))
    sit = ease(seg(t, 6.0, 6.8))
    has = t >= 3.6
    bite = max(pulse(t, 7.4, 1.0), pulse(t, 8.7, 1.0))
    put = ease(seg(t, 10.2, 11.0))
    walking = (0.2 < t < 2.6) or (4.4 < t < 6.0)
    face = -1 if 4.4 < t < 6.0 else 1
    mood = "try" if t < 9.4 else "hurt"
    if bite > 0.6:
        mood = "eat"
    food = 1.0 - 0.15 * seg(t, 7.9, 8.0) - 0.15 * seg(t, 9.2, 9.3)
    onbench = put > 0.95
    rh = lh = None
    if has and not onbench:
        if sit > 0.5:
            lh = (lerp(20, -70, put), lerp(-70, -30, put))
            rh = (lerp(84, 40, bite), lerp(-70, -196, bite))
        else:
            lh = (-70 * face * -1 if face > 0 else 70, -80)
            lh = (-60, -80) if face > 0 else (-90, -80)
            rh = (90, -80) if face > 0 else (60, -80)
    hero(c, t, x=x, mood=mood, face=face, sit=sit, walk=t * 7.5 if walking else None, rh=rh, lh=lh,
         hold="plate" if (has and not onbench) else None, look=ease(seg(t, 9.6, 10.4)), lean=0.07 * ease(seg(t, 11.0, 12.0)),
         hang=0.4, food=food, y=GY - 12 * sit)
    if onbench:
        plate(c, 430, 764, food)
    tint(c, (0.98, 0.50, 0.30), 0.10)
    try_meter(c, t, 1, 3.6, 10.6)
    tag(c, "6:00 PM", seg(t, 0.2, 0.6))
    caption(c, t, "I bought my favourite food.", 1.0, 5.8)
    caption(c, t, "It tasted like nothing.", 9.6, 15.2)
    dip(c, t, D)


def s6(c, t):
    D = 18
    cam = 2100
    street(c, t, cam, DUSK, 0.30, lit=1.0, stand_open=False)
    goal(c, cam)
    cheer = seg(t, 6.0, 6.3) * (1 - seg(t, 11.6, 12.2))
    look = seg(t, 12.4, 12.8)
    fr = ((930, 884, 0), (1190, 900, 3), (760, 872, 4))
    for i, (x, fy, si) in enumerate(fr):
        jp = 46 * abs(math.sin(t * 7 + i)) * cheer
        runx = 0
        if i == 1:
            runx = 60 * pulse(t, 4.6, 1.0)
        figure(c, x + runx, fy, 0.95, STY[si], face=-1 if (look > 0.5 or (i == 0 and t < 3.6)) else 1, jump=jp, arms=cheer,
               mouth="laugh" if cheer > 0.5 else ("flat" if look > 0.5 else "smile"))
    if cheer > 0.5:
        ha(c, t, 960, 380, 6.2, n=6, gap=0.55, col=CREAM)
        ha(c, t, 1200, 400, 8.0, n=5, gap=0.55, col=CREAM)
    hx = lerp(-140, 520, seg(t, 0.2, 2.2))
    if t > 15.0:
        hx = 520 - (t - 15.0) * 190
    kick = pulse(t, 3.5, 0.5)
    mood = "try" if t < 6.6 else "hurt"
    hero(c, t, x=hx + 30 * kick, mood=mood, face=-1 if t > 15.0 else 1,
         walk=t * 7.5 if (t < 2.2 or t > 15.0) else None, hang=ease(seg(t, 6.6, 8.0)), look=ease(seg(t, 7.0, 8.4)),
         lean=0.05 * ease(seg(t, 7.0, 8.4)))
    by = GY - 30
    if t < 2.6:
        bx, bz = 900, 0
    elif t < 3.6:
        bx, bz = lerp(900, 610, seg(t, 2.6, 3.6)), 0
    elif t < 4.8:
        k = seg(t, 3.6, 4.8)
        bx, bz = lerp(610, 1180, k), 120 * math.sin(math.pi * k)
    elif t < 5.2:
        bx, bz = 1200, 0
    elif t < 6.0:
        k = seg(t, 5.2, 6.0)
        bx, bz = lerp(1220, 1530, k), 90 * math.sin(math.pi * k)
    elif t < 9.6:
        bx, bz = 1530, 0
    else:
        k = seg(t, 9.6, 14.2)
        bx, bz = lerp(1530, 420, 1 - (1 - k) ** 2), 0
    ball(c, bx, by - bz, bx / 28.0)
    tint(c, NIGHT, 0.30)
    for lx in (2360, 3700):
        glow(c, lx - cam, 360, 420, 0.40)
    try_meter(c, t, 2, 2.2, 12.6)
    tag(c, "7:00 PM", seg(t, 0.2, 0.6), True)
    caption(c, t, "I played football with my friends.", 0.8, 5.6)
    caption(c, t, "They laughed. I could not.", 8.2, 14.6)
    dip(c, t, D)


def s7(c, t):
    D = 16
    on = 2.6 <= t < 10.8
    room(c, t, sky=NSKY, radio_on=on)
    x = lerp(190, 700, seg(t, 0.2, 2.0))
    x = lerp(x, 1260, ease(seg(t, 3.4, 5.2)))
    x = lerp(x, 720, ease(seg(t, 9.0, 10.4)))
    sit = ease(seg(t, 5.2, 6.0)) * (1 - ease(seg(t, 8.4, 9.0)))
    walking = (0.2 < t < 2.0) or (3.4 < t < 5.2) or (9.0 < t < 10.4)
    reach = max(pulse(t, 2.1, 1.0), ease(seg(t, 10.3, 10.7)) * (1 - ease(seg(t, 12.2, 13.0))))
    face = -1
    if t < 2.0 or 3.4 < t < 5.2:
        face = 1
    if 2.0 <= t < 3.4:
        face = -1
    nod = 0.05 * math.sin(t * 2 * math.pi * 1.2) * seg(t, 6.0, 6.4) * (1 - seg(t, 7.6, 8.0))
    mood = "try" if t < 7.8 else "hurt"
    lh = (lerp(-112, -150, reach), lerp(-30, -100, reach)) if reach > 0 else None
    hero(c, t, x=x, mood=mood, face=face, sit=sit, walk=t * 7.5 if walking else None, lh=lh, lean=nod + 0.06 * seg(t, 11.0, 12.0),
         look=ease(seg(t, 7.8, 8.6)), hang=0.4, y=GY - 12 * sit)
    if on:
        for k in range(14):
            s0 = 2.8 + k * 0.6
            age = t - s0
            if 0 <= age < 1.6 and s0 < 10.6:
                p = age / 1.6
                note(c, 560 + 90 * p + 14 * math.sin(age * 5 + k), 580 - 170 * p, 0.8 + 0.3 * p, math.sin(math.pi * p) ** 0.6)
    tint(c, (0.98, 0.70, 0.35), 0.10)
    glow(c, 1100, 240, 900, 0.30)
    try_meter(c, t, 3, 2.6, 10.9)
    tag(c, "8:30 PM", seg(t, 0.2, 0.6))
    caption(c, t, "I played my favourite song.", 2.6, 7.4)
    caption(c, t, "I turned it off.", 10.9, 15.2)
    dip(c, t, D)


def s8(c, t):
    D = 17
    k = seg(t, 0.0, 13.6)
    cam = 700 + 1900 * (k - 0.12 * k * k * k)
    walking = t < 13.6
    street(c, t, cam, NSKY, 1.0, lit=1.0, stand_open=False, door_open=False)
    stand_front(c, t, cam, steam=False)
    goal(c, cam)
    ball(c, 2520 - cam, GY - 30, 1.0)
    up = ease(seg(t, 14.0, 14.8)) * (1 - ease(seg(t, 15.6, 16.4)))
    hero(c, t, x=820, mood="hurt", face=1, walk=t * 6.0 if walking else None, hang=1.0, look=1 - 2.2 * up, lean=0.06 * (1 - up))
    tint(c, NIGHT, 0.52)
    c.set_source_rgb(0.97, 0.95, 0.85)
    c.arc(1180, 170, 56, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*mix(NSKY, NIGHT, 0.52))
    c.arc(1206, 154, 50, 0, 2 * math.pi)
    c.fill()
    for lx in (1060, 2360, 3700, 5000):
        if -500 < lx - cam < W + 500:
            glow(c, lx - cam, 360, 460, 0.50)
            g = cairo.RadialGradient(lx - cam, GY + 30, 0, lx - cam, GY + 30, 330)
            g.add_color_stop_rgba(0, 1.0, 0.80, 0.45, 0.22)
            g.add_color_stop_rgba(1, 1.0, 0.80, 0.45, 0)
            c.save()
            c.rectangle(0, GY, W, 220)
            c.clip()
            c.set_source(g)
            c.paint()
            c.restore()
    try_meter(c, t, 4, 1.0, 9.8)
    tag(c, "9:30 PM", seg(t, 0.2, 0.6), True)
    caption(c, t, "I took a long walk.", 1.0, 6.0, dark=True)
    caption(c, t, "I still felt the same.", 9.5, 15.6, dark=True)
    dip(c, t, D, col=INK)


TRIES = ["My favourite food", "Football with friends", "My favourite song", "A long walk"]


def s9(c, t):
    D = 10
    c.set_source_rgb(*INK)
    c.paint()
    text(c, "THINGS I TRIED", W / 2, 170, 54, CREAM, 0.6)
    for i, s in enumerate(TRIES):
        a = 0.5 + i * 0.8
        if t < a:
            continue
        k = ease(seg(t, a, a + 0.3))
        y = 320 + i * 138
        c.set_source_rgba(1, 1, 1, 0.06 * k)
        rrect(c, 380, y - 82, 1160, 116, 26)
        c.fill()
        text(c, str(i + 1), 450, y, 70, AMBER, k)
        xa = 4.0 + i * 0.6
        done = seg(t, xa, xa + 0.25)
        wd = text(c, s, 540, y, 70, CREAM, k * (1 - 0.45 * done), "l")
        if done > 0:
            c.set_source_rgb(*CORAL)
            c.set_line_width(7)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(530, y - 24)
            c.line_to(530 + (wd + 20) * done, y - 24)
            c.stroke()
            c.save()
            c.translate(1450, y - 24)
            s2_ = 1 + 0.5 * math.sin(math.pi * done)
            c.scale(s2_, s2_)
            c.set_line_width(16)
            c.move_to(-26, -26)
            c.line_to(26, 26)
            c.move_to(26, -26)
            c.line_to(-26, 26)
            c.stroke()
            c.restore()
    caption(c, t, "Four things. Nothing worked.", 6.4, 9.7, dark=True, y0=960)
    dip(c, t, D, col=INK, din=0.3, dout=0.4)


def s10(c, t):
    D = 15
    room(c, t, sky=NSKY)
    off = t >= 3.0
    k = ease(seg(t, 2.2, 3.0))
    mood = "angry" if t < 6.6 else "hurt"
    tense = 0.012 * math.sin(t * 22) * (1 - seg(t, 5.6, 6.6))
    hero(c, t, x=1260, y=GY - 12, mood=mood, face=-1, sit=1.0, cap=not off, hold="cap" if off else None,
         lean=0.10 + 0.06 * ease(seg(t, 6.6, 9.0)) + tense, look=ease(seg(t, 6.6, 8.0)),
         rh=(lerp(-10, -40, k), lerp(-250, -60, k)) if t >= 1.6 and not off else ((-40, -60) if off else None),
         lh=(-110, -60) if off else None)
    tint(c, (0.98, 0.70, 0.35), 0.10)
    glow(c, 1100, 240, 900, 0.30)
    meter(c, "try", 4, "NO", 0, 0, t)
    tag(c, "10:30 PM", seg(t, 0.2, 0.6))
    caption(c, t, "I was still angry.", 1.0, 6.0)
    caption(c, t, "Still sad.", 7.4, 13.0)
    dip(c, t, D)


def s11(c, t):
    D = 17
    lit = t < 4.4
    lying = ease(seg(t, 7.0, 7.8))
    room(c, t, sky=NSKY, lamp=1.0 if lit else 0.0, bed="made" if lying < 0.5 else "in")
    sit = (1 - ease(seg(t, 1.6, 2.4))) + ease(seg(t, 6.2, 7.0))
    x = lerp(1260, 1150, ease(seg(t, 2.4, 3.6)))
    x = lerp(x, 1300, ease(seg(t, 5.0, 6.2)))
    reach = ease(seg(t, 3.6, 4.2)) * (1 - ease(seg(t, 4.6, 5.0)))
    walking = (2.4 < t < 3.6) or (5.0 < t < 6.2)
    if lying < 1:
        c.push_group()
        hero(c, t, x=x, y=GY - 12 * sit, mood="hurt", face=1 if 2.4 < t < 5.0 else -1, sit=clamp(sit), cap=False,
             walk=t * 7.5 if walking else None, hang=0.6, look=0.6,
             rh=(lerp(112, 20, reach), lerp(-30, -330, reach)) if reach > 0 else None)
        c.pop_group_to_source()
        c.paint_with_alpha(1 - lying)
    if lying > 0:
        c.push_group()
        c.set_source_rgb(*CREAM)
        rrect(c, 1610, 684, 150, 56, 26)
        c.fill()
        c.save()
        c.translate(1664, 668)
        c.rotate(1.35)
        closed = t >= 13.4
        head(c, t, "sleep" if closed else "tired", face=-1, cap=False)
        c.restore()
        br = 4 * math.sin(t * 1.6)
        c.set_source_rgb(*TEAL)
        c.move_to(1110, 790)
        c.curve_to(1110, 690 - br, 1250, 660 - br, 1420, 672 - br)
        c.curve_to(1520, 676 - br, 1590, 690, 1600, 730)
        c.line_to(1600, 790)
        c.close_path()
        c.fill()
        c.set_source_rgb(*TEAL_D)
        rrect(c, 1560, 716, 44, 74, 14)
        c.fill()
        c.pop_group_to_source()
        c.paint_with_alpha(lying)
    c.set_source_rgb(*CORAL)
    c.arc(520, 604, 40, math.pi, 2 * math.pi)
    c.close_path()
    c.fill()
    if lit:
        tint(c, (0.98, 0.70, 0.35), 0.10)
        glow(c, 1100, 240, 900, 0.30)
    else:
        tint(c, NIGHT, 0.74)
        c.set_source_rgba(0.75, 0.85, 0.95, 0.10)
        c.move_to(710, 250)
        c.line_to(990, 250)
        c.line_to(1500, GY + 220)
        c.line_to(900, GY + 220)
        c.close_path()
        c.fill()
        if 4.4 <= t < 4.5:
            tint(c, NIGHT, 0.3)
        if lying > 0:
            glow(c, 1650, 670, 230, 0.30 * lying, col=(0.78, 0.86, 0.95))
    meter(c, "try", 4, "NO", 0, 0, t)
    tag(c, "11:00 PM", seg(t, 0.2, 0.6), not lit)
    caption(c, t, "So I stopped trying.", 4.9, 9.4, dark=True)
    caption(c, t, "I went to bed.", 10.6, 15.4, dark=True)
    a = seg(t, D - 1.4, D - 0.2)
    tint(c, INK, a)
    if t < 0.3:
        tint(c, CREAM, 1 - seg(t, 0, 0.3))


def sprout(c, cx, cy, r, a=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(r / 100.0, r / 100.0)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(0.85, 0.64, 0.25, a)
    c.set_line_width(8)
    for ang in (-150, -120, -90, -60, -30):
        g = math.radians(ang)
        c.move_to(52 * math.cos(g), 44 + 52 * math.sin(g))
        c.line_to(70 * math.cos(g), 44 + 70 * math.sin(g))
        c.stroke()
    c.arc(0, 44, 40, math.pi, 2 * math.pi)
    c.close_path()
    c.fill()
    c.set_source_rgba(*CREAM, a)
    rrect(c, -92, 40, 184, 14, 7)
    c.fill()
    c.set_source_rgba(0.37, 0.54, 0.31, a)
    c.set_line_width(10)
    c.move_to(0, 42)
    c.curve_to(2, 10, -4, -30, 0, -58)
    c.stroke()
    for sgn, ang, ln, y in ((-1, -0.45, 40, -50), (1, 0.45, 46, -62)):
        c.save()
        c.translate(0, y)
        c.rotate(ang)
        c.translate(sgn * ln * 0.55, 0)
        c.move_to(-ln * 0.6, 0)
        c.curve_to(-ln * 0.3, -ln * 0.42, ln * 0.3, -ln * 0.42, ln * 0.6, 0)
        c.curve_to(ln * 0.3, ln * 0.42, -ln * 0.3, ln * 0.42, -ln * 0.6, 0)
        c.close_path()
        c.set_source_rgba(0.47, 0.70, 0.40, a)
        c.fill()
        c.restore()
    c.restore()


def s12(c, t):
    D = 13
    c.set_source_rgb(*INK)
    c.paint()
    sprout(c, W / 2, 300, 70, ease(seg(t, 0.3, 1.0)))
    caption(c, t, "Not every day can be saved.", 0.8, 13.5, dark=True, y0=540, size=84)
    caption(c, t, "Some you just finish.", 4.4, 13.5, dark=True, y0=680, size=96, col=AMBER)
    text(c, "Small Win Films", W / 2, 900, 40, CREAM, 0.55 * ease(seg(t, 7.4, 8.2)))
    tint(c, (0.03, 0.06, 0.08), max(1 - seg(t, 0, 0.4), seg(t, D - 1.2, D - 0.1)))


SC = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6, s7=s7, s8=s8, s9=s9, s10=s10, s11=s11, s12=s12)


def frame(c, name, t):
    UI.clear()
    SC[name](c, t)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    mode = sys.argv[1]
    out = sys.argv[2]
    if mode == "stills":
        for spec in sys.argv[3:]:
            name, ts = spec.split("@")
            frame(c, name, float(ts))
            surf.write_to_png(os.path.join(out, "%s_%s.png" % (name, ts)))
        return
    names = sys.argv[3:] or [n for n, _ in DURS]
    durs = dict(DURS)
    for name in names:
        tmp = os.path.join(out, name + ".part.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0",
                              "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                              "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(int(durs[name] * FPS)):
            frame(c, name, i / FPS)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
        p.stdin.close()
        if p.wait() != 0:
            sys.exit(1)
        os.rename(tmp, os.path.join(out, name + ".mp4"))
        print("done", name, flush=True)



_COLD = None


def s0(c, t):
    global _COLD, DRAW_UI
    D = 6
    if _COLD is None:
        _COLD = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    sc = cairo.Context(_COLD)
    saved = DRAW_UI
    DRAW_UI = False
    UI.clear()
    tt = 9.0 + 0.4 * t
    room(sc, tt, sky=NSKY)
    hero(sc, tt, x=1260, y=GY - 12, mood="hurt", face=-1, sit=1.0, cap=False, hold="cap",
         lean=0.16 + 0.01 * math.sin(t * 1.3), look=1.0, lh=(-110, -60), rh=(-40, -60))
    tint(sc, (0.98, 0.70, 0.35), 0.10)
    glow(sc, 1100, 240, 900, 0.30)
    DRAW_UI = saved
    UI.clear()
    z = 2.05 - 0.10 * ease(seg(t, 0, D))
    cx, cy = 1235, 560
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)
    c.set_source_surface(_COLD, 0, 0)
    c.paint()
    c.restore()
    k = ease(seg(t, 2.4, 3.2))
    if k < 1:
        c.save()
        x = lerp(1060, 1470, k)
        y = lerp(330, 34, k)
        s = lerp(1.9, 1.0, k)
        meter_draw(c, x, y, s, "try", 4, "NO", 0, 0, t)
        c.restore()
    else:
        meter(c, "try", 4, "NO", 0, 0, t)
    tag(c, "10:30 PM", 0)
    caption(c, t, "I tried four things. Nothing worked.", 0.3, 5.8)


def s0b(c, t):
    D = 2
    c.set_source_rgb(*NIGHT)
    c.paint()
    text(c, "That morning.", W / 2, H / 2 + 20, 76, CREAM, ease(seg(t, 0.05, 0.4)))
    dip(c, t, D, col=NIGHT, din=0.05, dout=0.25)


SC["s0"] = s0
SC["s0b"] = s0b


if __name__ == "__main__":
    main()
