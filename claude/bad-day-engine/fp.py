import cairo, math, random

W, H = 1920, 1080
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
NSKY = (0.07, 0.16, 0.24)

WORK = [
    dict(col=STEEL, shape="rect", skin=(0.38, 0.24, 0.15), hair="short", bib=1),
    dict(col=STEEL, shape="round", skin=(0.68, 0.48, 0.34), hair="afro", bib=1),
    dict(col=STEEL, shape="rect", skin=(0.48, 0.30, 0.19), hair="bald", bib=1),
]
BOSS = dict(col=(0.22, 0.26, 0.36), shape="rect", skin=(0.62, 0.42, 0.30), hair="bald", tie=1, glasses=1)

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


def head(c, mood="ok", face=1, cap=True, look=0.0):
    c.set_source_rgb(*SKIN)
    c.arc(0, 0, 62, 0, 2 * math.pi)
    c.fill()
    c.arc(-60, 8, 12, 0, 2 * math.pi)
    c.arc(60, 8, 12, 0, 2 * math.pi)
    c.fill()
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
        c.set_source_rgb(*INK)
        c.arc(0, -4, 64, math.radians(188), math.radians(352))
        c.close_path()
        c.fill()
    ex = 10 * face
    ey = 10
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    big = 1.25 if mood == "shock" else 1.0
    dy = 4 * look + (4 if mood in ("hurt", "tired") else 0)
    for dx in (-22, 22):
        c.set_source_rgb(*CREAM)
        ell(c, ex + dx, ey, 11 * big, 13 * big)
        c.fill()
        c.set_source_rgb(*INK)
        ell(c, ex + dx + 2 * face, ey + 1 + dy, 5.5, 6.5)
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


def hero(c, x=860, mood="ok", face=1, lean=0.0, rh=None, lh=None, walk=None, cap=True, hold=None, hang=0.0,
         look=0.0, y=GY, shadow=True):
    if shadow:
        c.set_source_rgba(*INK, 0.14)
        ell(c, x, y + 6, 125, 12)
        c.fill()
    drop = 5 * abs(math.sin(walk)) if walk is not None else 0
    c.save()
    c.translate(x, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    for sgn in (-1, 1):
        sw = 24 * math.sin(walk) * sgn if walk is not None else 0
        fx = sgn * 36 + sw
        c.set_source_rgb(*TEAL_D)
        c.set_line_width(42)
        c.move_to(sgn * 36, -128 + drop)
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
    arm(-54, lhp)
    arm(54, rhp)
    if hold == "wrench":
        wrench(c, front[0] + 6 * face, front[1] + 4, 0.9 * face)
        c.set_source_rgb(*SKIN)
        c.arc(front[0], front[1], 19, 0, 2 * math.pi)
        c.fill()
    c.translate(0, -262)
    c.rotate(lean * face * 1.3 + 0.10 * look * face)
    head(c, mood, face, cap, look)
    c.restore()


def figure(c, x, feet, s, st, face=1, mouth="smile", point=None, lean=0.0, look=0.0):
    c.save()
    c.translate(x, feet)
    c.set_source_rgba(*INK, 0.12)
    ell(c, 0, 5, 80 * s, 9 * s)
    c.fill()
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    col = st["col"]
    c.set_source_rgb(*(mix(col, INK, 0.25) if st.get("bib") else mix(INK, col, 0.18)))
    c.set_line_width(30)
    for sgn in (-1, 1):
        c.move_to(sgn * 20, -110)
        c.line_to(sgn * 20, -14)
        c.stroke()
    c.translate(0, -100)
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
        hx, hy = sgn * 70, -178
        if point is not None and sgn == face:
            hx, hy = point
        c.set_source_rgb(*mix(col, (0, 0, 0), 0.12))
        c.move_to(sgn * 54, -286)
        c.line_to(hx, hy)
        c.stroke()
        c.set_source_rgb(*st["skin"])
        c.arc(hx, hy, 15, 0, 2 * math.pi)
        c.fill()
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


def workshop(c, hour=8.0, sky=(0.95, 0.90, 0.78)):
    c.set_source_rgb(*SEA)
    c.paint()
    c.set_source_rgb(*sky)
    c.rectangle(0, 240, 320, 620)
    c.fill()
    c.set_source_rgba(1, 0.97, 0.86, 0.9)
    c.arc(150, 520, 54, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*mix(sky, TEAL_D, 0.22))
    for x, w, h in ((-40, 150, 250), (120, 120, 180), (240, 100, 300)):
        c.rectangle(x, GY - h, min(w, 320 - x), h)
        c.fill()
    c.set_source_rgb(*TEAL_D)
    c.rectangle(320, 210, 26, 650)
    c.rectangle(0, 210, 346, 34)
    c.fill()
    c.set_source_rgb(*SEA_D)
    c.rectangle(346, 650, W, 210)
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
    car(c)
    tyres(c, 470, 2)


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


def street(c, cam=0.0, sky=SAND, dark=0.0, lit=0.0):
    c.set_source_rgb(*sky)
    c.paint()
    if dark > 0.5:
        for x, y, r in STARS:
            c.set_source_rgba(1, 1, 1, 0.9)
            c.arc(x, y, r, 0, 2 * math.pi)
            c.fill()
    c.set_source_rgb(*mix(sky, TEAL_D, 0.20 + 0.25 * dark))
    for x, w, h in FARB:
        c.rectangle(x - cam * 0.35, GY - h, w, h)
        c.fill()
    c.set_source_rgb(*PAVE)
    c.rectangle(0, GY, W, 220)
    c.fill()
    c.save()
    c.translate(-cam, 0)
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
    c.restore()


def ball(c, x, y, rot=0.0, r=28):
    c.set_source_rgb(*CREAM)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    for i in range(3):
        a = rot + i * 2.09
        c.arc(x + r / 2 * math.cos(a), y + r / 2 * math.sin(a), r / 4, 0, 2 * math.pi)
        c.fill()
