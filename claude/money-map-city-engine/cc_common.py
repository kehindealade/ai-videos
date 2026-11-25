import cairo, math, random
import ss_common as S
from ss_common import clamp, ease, e, lerp, back, ease_out, rr, fill, box, circle, line, arrow, shadow, logo, coin, stamp

W, H, FPS = 1920, 1080, 30
HEAD = "Inter Black"
BODY = "Inter"
MONO = "DejaVu Sans Mono"

INK = (0.09, 0.12, 0.22)
SOFT = (0.36, 0.41, 0.52)
WHITE = (1, 1, 1)
NAVY = (0.08, 0.13, 0.30)
GOLD = (0.98, 0.72, 0.14)
GOLD_D = (0.72, 0.50, 0.06)
GREEN = (0.10, 0.62, 0.36)
GREEN_L = (0.84, 0.96, 0.88)
RED = (0.86, 0.24, 0.22)
RED_L = (0.99, 0.88, 0.86)
BLUE = (0.22, 0.46, 0.88)
BLUE_L = (0.86, 0.92, 1.0)
VIOLET = (0.45, 0.36, 0.86)
TEAL = (0.10, 0.60, 0.56)
ORANGE = (0.96, 0.52, 0.22)

C_HOME = (0.98, 0.78, 0.60)
C_SHOP = (0.96, 0.52, 0.34)
C_ACQ = (0.38, 0.62, 0.94)
C_NET = (0.50, 0.42, 0.88)
C_ISS = (0.14, 0.64, 0.58)
C_OTH = (0.88, 0.89, 0.92)

TW_, TH_, ZH = 128.0, 64.0, 58.0
CAM = {"cx": 9.5, "cy": 7.0, "z": 0.8, "sy": 520.0}


def eff(size, f):
    return max(size, 34) if f == BODY else size


def T(c, s, x, y, size, col, f=BODY, align="c", a=1.0, stroke=None, sw=8):
    size = eff(size, f)
    return S.txt(c, s, x, y, size, col, f, align, a, bold=(f != HEAD and f != MONO), stroke=stroke, sw=sw)


def tw(c, s, size, f=BODY):
    size = eff(size, f)
    return S.tw(c, s, size, f, bold=(f != HEAD and f != MONO))


def fitsz(c, s, size, maxw, f=BODY):
    while size > 18 and tw(c, s, size, f) > maxw:
        size -= 2
    return size


def P(x, y, h=0.0):
    z = CAM["z"]
    X = 960 + z * TW_ / 2 * ((x - y) - (CAM["cx"] - CAM["cy"]))
    Y = CAM["sy"] + z * TH_ / 2 * ((x + y) - (CAM["cx"] + CAM["cy"])) - z * h * ZH
    return X, Y


def set_cam(cx, cy, z, sy=520.0):
    CAM.update(cx=cx, cy=cy, z=z, sy=sy)


def cam_lerp(a, b, k):
    k = ease(k)
    return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k))


def poly(c, pts, col, a=1.0, line_col=None, lw=2):
    c.new_path()
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgba(*col, a)
    if line_col:
        c.fill_preserve()
        c.set_source_rgba(*line_col, a)
        c.set_line_width(lw)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke()
    else:
        c.fill()


def shade(col, k):
    return tuple(max(0, min(1, v * k)) for v in col)


def tint(col, k):
    return tuple(v + (1 - v) * k for v in col)


def tile(c, x, y, col, a=1.0, h=0.0, w=1.0, d=1.0):
    poly(c, [P(x, y, h), P(x + w, y, h), P(x + w, y + d, h), P(x, y + d, h)], col, a)


def ibox(c, x, y, w, d, h, col, z0=0.0, a=1.0, edge=True, top=None):
    topc = top or tint(col, 0.22)
    lc, rc = shade(col, 0.80), shade(col, 0.64)
    ln = shade(col, 0.45) if edge else None
    h1 = z0 + h
    poly(c, [P(x, y + d, z0), P(x + w, y + d, z0), P(x + w, y + d, h1), P(x, y + d, h1)], lc, a, ln, 1.5)
    poly(c, [P(x + w, y, z0), P(x + w, y + d, z0), P(x + w, y + d, h1), P(x + w, y, h1)], rc, a, ln, 1.5)
    poly(c, [P(x, y, h1), P(x + w, y, h1), P(x + w, y + d, h1), P(x, y + d, h1)], topc, a, ln, 1.5)


def fpt(face, x, y, w, d, h, u, v, z0=0.0):
    if face == "L":
        return P(x + u * w, y + d, z0 + v * h)
    return P(x + w, y + u * d, z0 + v * h)


def fquad(c, face, x, y, w, d, h, u0, v0, u1, v1, col, a=1.0, z0=0.0, line_col=None):
    poly(c, [fpt(face, x, y, w, d, h, u0, v0, z0), fpt(face, x, y, w, d, h, u1, v0, z0), fpt(face, x, y, w, d, h, u1, v1, z0), fpt(face, x, y, w, d, h, u0, v1, z0)], col, a, line_col, 1.5)


def windows(c, x, y, w, d, h, cols, rows, col, a=1.0, z0=0.0, lit=0.0, pad=0.12):
    for face in ("L", "R"):
        for i in range(cols):
            for j in range(rows):
                u0 = pad + (1 - 2 * pad) * i / cols + 0.02
                u1 = pad + (1 - 2 * pad) * (i + 1) / cols - 0.02
                v0 = 0.22 + 0.68 * j / rows + 0.02
                v1 = 0.22 + 0.68 * (j + 1) / rows - 0.04
                cc = col if (i * 7 + j * 3 + (1 if face == "R" else 0)) % 5 else tint(col, 0.5)
                fquad(c, face, x, y, w, d, h, u0, v0, u1, v1, cc, a, z0)


def iso_ellipse(c, x, y, h, rx, ry_ratio, col, a=1.0, line_col=None, lw=3):
    X, Y = P(x, y, h)
    z = CAM["z"]
    c.save()
    c.translate(X, Y)
    c.scale(1, ry_ratio)
    c.new_path()
    c.arc(0, 0, rx * z * TW_ / 2, 0, 2 * math.pi)
    c.restore()
    c.set_source_rgba(*col, a)
    if line_col:
        c.fill_preserve()
        c.save()
        c.translate(X, Y)
        c.scale(1, ry_ratio)
        c.set_source_rgba(*line_col, a)
        c.set_line_width(lw / max(ry_ratio, 0.2))
        c.restore()
        c.set_line_width(lw)
        c.set_source_rgba(*line_col, a)
        c.stroke()
    else:
        c.fill()


def ring(c, x, y, h, r, col, a=1.0, lw=4):
    X, Y = P(x, y, h)
    z = CAM["z"]
    c.save()
    c.translate(X, Y)
    c.scale(1, 0.5)
    c.new_path()
    c.arc(0, 0, r * z * TW_ / 2, 0, 2 * math.pi)
    c.restore()
    c.set_source_rgba(*col, a)
    c.set_line_width(lw)
    c.stroke()


# ---------------------------------------------------------------- world layout
GW, GH = 20, 14
ROADS_X = [8, 14]
ROADS_Y = [4, 9]
CONN = []
D_HOME = (4.0, 10.45)
D_SHOP = (4.0, 8.75)
D_ACQ = (4.0, 4.0)
D_NET = (11.05, 3.65)
D_NET2 = (11.05, 3.65)
D_ISS = (15.1, 7.2)
PATHS = {
    "shop_acq": [D_SHOP, (4.0, 9.5), (8.5, 9.5), (8.5, 4.5), (4.0, 4.5), D_ACQ],
    "acq_net": [D_ACQ, (4.0, 4.5), (11.05, 4.5), D_NET],
    "net_iss": [D_NET2, (11.05, 4.5), (14.5, 4.5), (14.5, 7.2), D_ISS],
    "iss_home": [D_ISS, (14.5, 7.2), (14.5, 9.5), (4.0, 9.5), D_HOME],
    "home_shop": [D_HOME, (4.0, 9.5), D_SHOP],
}
BLD = {
    "home": (2.8, 10.9, 2.4, 2.4, 1.5),
    "shop": (2.0, 5.2, 4.0, 3.1, 1.9),
    "acq": (2.0, 0.6, 4.0, 3.1, 2.8),
    "net": (10.0, 1.3, 2.1, 2.1, 5.4),
    "iss": (15.6, 5.6, 3.6, 3.2, 3.0),
}
NAME = {"home": "YOU", "shop": "THE STORE", "acq": "STORE'S BANK", "net": "CARD NETWORK", "iss": "YOUR BANK"}
SUB = {"home": "the cardholder", "shop": "the merchant", "acq": "the acquirer", "net": "runs the roads", "iss": "the issuer"}
COL = {"home": C_HOME, "shop": C_SHOP, "acq": C_ACQ, "net": C_NET, "iss": C_ISS}


def on_path(name, k):
    pts = PATHS[name]
    segs = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    goal = sum(segs) * clamp(k)
    run = 0
    for i, sl in enumerate(segs):
        if run + sl >= goal or i == len(segs) - 1:
            f = (goal - run) / max(sl, 1e-6)
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
        run += sl
    return pts[-1]


def is_road(x, y):
    return x in ROADS_X or y in ROADS_Y or (x, y) in CONN


# ---------------------------------------------------------------- ground
def ground(c, t=0.0):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.76, 0.89, 0.95)
    g.add_color_stop_rgb(1, 0.90, 0.96, 0.97)
    c.set_source(g)
    c.paint()
    pts = [P(-0.6, -0.6), P(GW + 0.6, -0.6), P(GW + 0.6, GH + 0.6), P(-0.6, GH + 0.6)]
    poly(c, pts, (0.58, 0.72, 0.62), 1.0)
    for x in range(GW):
        for y in range(GH):
            if is_road(x, y):
                col = (0.38, 0.42, 0.50)
            else:
                col = (0.80, 0.91, 0.80) if (x + y) % 2 == 0 else (0.76, 0.88, 0.77)
                bx = x
                if 0 <= x < 8 and 0 <= y < 4 or 0 <= x < 8 and 5 <= y < 9 or 0 <= x < 8 and 10 <= y < 14:
                    col = (0.90, 0.92, 0.93) if (x + y) % 2 == 0 else (0.87, 0.89, 0.91)
                if 9 <= x < 14 and 0 <= y < 4 or 15 <= x < 20 and 5 <= y < 9:
                    col = (0.90, 0.92, 0.93) if (x + y) % 2 == 0 else (0.87, 0.89, 0.91)
            tile(c, x, y, col)
    c.set_source_rgba(1, 1, 1, 0.55)
    c.set_line_width(max(2, 3 * CAM["z"]))
    c.set_dash([14 * CAM["z"], 12 * CAM["z"]])
    for rx in ROADS_X:
        c.move_to(*P(rx + 0.5, 0))
        c.line_to(*P(rx + 0.5, GH))
    for ry in ROADS_Y:
        c.move_to(*P(0, ry + 0.5))
        c.line_to(*P(GW, ry + 0.5))
    c.stroke()
    c.set_dash([])


def tree(c, x, y, s=1.0, a=1.0):
    X, Y = P(x, y)
    z = CAM["z"] * s
    c.set_source_rgba(0.35, 0.25, 0.15, a)
    rr(c, X - 4 * z, Y - 22 * z, 8 * z, 24 * z, 3 * z)
    c.fill()
    circle(c, X, Y - 38 * z, 22 * z, (0.30, 0.66, 0.42), a)
    circle(c, X - 8 * z, Y - 46 * z, 13 * z, (0.40, 0.76, 0.50), a)


def car(c, x, y, horiz=True, col=(0.92, 0.35, 0.30), a=1.0):
    if horiz:
        ibox(c, x - 0.35, y - 0.18, 0.7, 0.36, 0.28, col, a=a)
    else:
        ibox(c, x - 0.18, y - 0.35, 0.36, 0.7, 0.28, col, a=a)


# ---------------------------------------------------------------- buildings
def bld_home(c, a=1.0, glow=0.0):
    x, y, w, d, h = BLD["home"]
    ibox(c, x, y, w, d, h, COL["home"], a=a)
    windows(c, x, y, w, d, h, 2, 1, (0.55, 0.78, 0.92), a)
    rh = 1.0
    rc = (0.78, 0.30, 0.26)
    poly(c, [P(x - 0.15, y + d + 0.15, h), P(x + w + 0.15, y + d + 0.15, h), P(x + w + 0.15, y + d / 2, h + rh), P(x - 0.15, y + d / 2, h + rh)], shade(rc, 1.0), a, shade(rc, 0.5), 1.5)
    poly(c, [P(x + w, y - 0.1, h), P(x + w, y + d + 0.1, h), P(x + w, y + d / 2, h + rh)], shade(COL["home"], 0.60), a)
    poly(c, [P(x - 0.15, y - 0.15, h), P(x + w + 0.15, y - 0.15, h), P(x + w + 0.15, y + d / 2, h + rh), P(x - 0.15, y + d / 2, h + rh)], shade(rc, 0.78), a, shade(rc, 0.5), 1.5)
    fquad(c, "L", x, y, w, d, h, 0.40, 0.0, 0.60, 0.62, (0.45, 0.28, 0.18), a)


def bld_shop(c, t=0.0, a=1.0):
    x, y, w, d, h = BLD["shop"]
    ibox(c, x, y, w, d, h, COL["shop"], a=a)
    fquad(c, "L", x, y, w, d, h, 0.08, 0.18, 0.92, 0.62, (0.78, 0.92, 0.98), a)
    fquad(c, "L", x, y, w, d, h, 0.40, 0.0, 0.60, 0.50, (0.35, 0.22, 0.15), a)
    n = 10
    for i in range(n):
        u0, u1 = 0.04 + 0.92 * i / n, 0.04 + 0.92 * (i + 1) / n
        cc = (0.88, 0.22, 0.22) if i % 2 == 0 else (0.98, 0.96, 0.94)
        poly(c, [P(x + u0 * w, y + d, h * 0.66), P(x + u1 * w, y + d, h * 0.66), P(x + u1 * w, y + d + 0.55, h * 0.52), P(x + u0 * w, y + d + 0.55, h * 0.52)], cc, a, None)
    windows(c, x, y, w, d, h * 1.0, 3, 1, (0.90, 0.95, 1.0), a, z0=0.0, pad=0.1) if False else None
    fquad(c, "R", x, y, w, d, h, 0.15, 0.25, 0.85, 0.70, (0.78, 0.92, 0.98), a)


def bld_acq(c, t=0.0, a=1.0):
    x, y, w, d, h = BLD["acq"]
    ibox(c, x, y, w, d, h, COL["acq"], a=a)
    windows(c, x, y, w, d, h, 4, 4, (0.84, 0.93, 1.0), a)
    ibox(c, x + 1.5, y + 1.0, 0.9, 0.7, 0.32, shade(COL["acq"], 0.8), z0=h, a=a)
    X, Y = P(x + 2.0, y + 1.3, h + 0.6)
    c.set_source_rgba(0.9, 0.93, 0.98, a)
    c.arc(X, Y, 22 * CAM["z"], math.pi, 2 * math.pi)
    c.fill()


def bld_net(c, t=0.0, a=1.0, pulse=0.0):
    x, y, w, d, h = BLD["net"]
    ibox(c, x, y, w, d, h, COL["net"], a=a)
    for k in range(5):
        fquad(c, "L", x, y, w, d, h, 0.12, 0.10 + 0.17 * k, 0.88, 0.16 + 0.17 * k, (0.78, 0.94, 1.0), a)
        fquad(c, "R", x, y, w, d, h, 0.12, 0.10 + 0.17 * k, 0.88, 0.16 + 0.17 * k, (0.66, 0.84, 0.98), a)
    cx_, cy_ = x + w / 2, y + d / 2
    X0, Y0 = P(cx_, cy_, h)
    X1, Y1 = P(cx_, cy_, h + 1.6)
    c.set_source_rgba(0.35, 0.30, 0.55, a)
    c.set_line_width(5 * CAM["z"])
    c.move_to(X0, Y0)
    c.line_to(X1, Y1)
    c.stroke()
    circle(c, X1, Y1, (9 + 4 * pulse) * CAM["z"], (0.55, 0.95, 1.0), a)
    for k in range(3):
        ph = (t * 0.7 + k / 3.0) % 1.0
        ring(c, cx_, cy_, h + 1.6, 0.25 + ph * 1.1, (0.55, 0.95, 1.0), a * (1 - ph) * 0.8, 3)


def bld_iss(c, t=0.0, a=1.0):
    x, y, w, d, h = BLD["iss"]
    ibox(c, x, y, w, d, h, COL["iss"], a=a)
    ibox(c, x - 0.2, y - 0.2, w + 0.4, d + 0.4, 0.28, (0.96, 0.92, 0.80), z0=h, a=a)
    n = 5
    for i in range(n):
        u = 0.12 + 0.76 * i / (n - 1)
        fquad(c, "L", x, y, w, d, h, u - 0.035, 0.0, u + 0.035, 0.88, (0.96, 0.94, 0.86), a)
    fquad(c, "R", x, y, w, d, h, 0.1, 0.2, 0.9, 0.75, (0.80, 0.94, 0.92), a)
    X, Y = P(x + w / 2, y + d / 2, h + 0.28)
    z = CAM["z"]
    poly(c, [(X - 70 * z, Y), (X + 70 * z, Y), (X, Y - 44 * z)], (0.96, 0.92, 0.80), a)
    circle(c, X, Y - 18 * z, 14 * z, GOLD, a)


def person_b(c, x, y, col, s=1.0, a=1.0, h=0.0, card=False, cash=False, wave=0.0):
    X, Y = P(x, y, h)
    z = CAM["z"] * s
    c.set_source_rgba(0, 0, 0, 0.18 * a)
    c.save()
    c.translate(X, Y)
    c.scale(1, 0.5)
    c.arc(0, 0, 22 * z, 0, 2 * math.pi)
    c.restore()
    c.fill()
    c.set_source_rgba(*shade(col, 0.7), a)
    rr(c, X - 14 * z, Y - 22 * z, 12 * z, 26 * z, 5 * z)
    c.fill()
    rr(c, X + 2 * z, Y - 22 * z, 12 * z, 26 * z, 5 * z)
    c.fill()
    c.set_source_rgba(*col, a)
    rr(c, X - 20 * z, Y - 74 * z, 40 * z, 56 * z, 16 * z)
    c.fill()
    circle(c, X, Y - 94 * z, 16 * z, (0.96, 0.80, 0.66), a)
    if card:
        c.save()
        c.translate(X + 26 * z, Y - 62 * z - wave * 6 * z)
        c.rotate(-0.25)
        rr(c, -16 * z, -10 * z, 32 * z, 20 * z, 4 * z)
        c.set_source_rgba(0.12, 0.2, 0.5, a)
        c.fill()
        c.set_source_rgba(1, 0.85, 0.3, a)
        c.rectangle(-12 * z, -3 * z, 10 * z, 7 * z)
        c.fill()
        c.restore()
    if cash:
        c.save()
        c.translate(X + 26 * z, Y - 62 * z)
        c.rotate(-0.2)
        rr(c, -18 * z, -9 * z, 36 * z, 18 * z, 3 * z)
        c.set_source_rgba(0.55, 0.80, 0.55, a)
        c.fill()
        circle(c, 0, 0, 6 * z, (0.80, 0.94, 0.78), a)
        c.restore()


def pill(c, x, y, s, size=34, fg=WHITE, bg=NAVY, a=1.0, f=BODY, padx=26, h=None, line_col=None):
    w = tw(c, s, size, f) + padx * 2
    hh = h or size * 1.7
    box(c, x - w / 2, y - hh / 2, w, hh, bg, a, hh / 2, line_col, 3)
    T(c, s, x, y + size * 0.35, size, fg, f, "c", a)
    return w


def plate(c, name, x, y, hgt, k, sub=None, col=NAVY, num=None, dx=0, dy=0):
    if k <= 0:
        return
    X, Y = P(x, y, hgt)
    X += dx
    Y += dy
    Y -= 12 * k + (1 - k) * 20
    s1 = 40
    w = max(tw(c, name, s1, HEAD) + 56, (tw(c, sub, 26, BODY) + 40) if sub else 0)
    hh = 100 if sub else 62
    c.save()
    c.translate(X, Y)
    sc = 0.7 + 0.3 * back(k)
    c.scale(sc, sc)
    shadow(c, -w / 2, -hh, w, hh, 14, 0.22 * k, 6)
    box(c, -w / 2, -hh, w, hh, col, min(1, k * 1.5), 14)
    T(c, name, 0, -hh + 46, s1, WHITE, HEAD, "c", min(1, k * 1.5))
    if sub:
        T(c, sub, 0, -20, 26, (0.80, 0.86, 0.98), BODY, "c", min(1, k * 1.5))
    poly(c, [(-10, 0), (10, 0), (0, 14)], col, min(1, k * 1.5))
    if num:
        circle(c, -w / 2 + 6, -hh + 6, 22, GOLD, min(1, k * 1.5), WHITE, 4)
        T(c, str(num), -w / 2 + 6, -hh + 17, 30, INK, HEAD, "c", min(1, k * 1.5))
    c.restore()


def coin_at(c, x, y, h, r=26, a=1.0, label=None, tilt=0.0):
    X, Y = P(x, y, h)
    z = CAM["z"]
    rr_ = r * z * 1.0
    c.save()
    c.translate(X, Y)
    c.scale(1, 0.75)
    circle(c, 0, 5 * z * 1.2, rr_, GOLD_D, a)
    circle(c, 0, 0, rr_, GOLD, a, (0.72, 0.5, 0.06), 3)
    c.restore()
    if label:
        T(c, label, X, Y + 5 * z, max(14, 22 * z * r / 26), (0.45, 0.30, 0.02), HEAD, "c", a)


def packet(c, x, y, h, label, col=GOLD, a=1.0, s=1.0, tc=INK):
    X, Y = P(x, y, h)
    z = CAM["z"] * s
    w = tw(c, label, 34 * s, HEAD) + 36
    hh = 54
    c.save()
    c.translate(X, Y - 20 * z)
    c.scale(max(0.5, z / 0.9), max(0.5, z / 0.9))
    shadow(c, -w / 2, -hh / 2, w, hh, 12, 0.25 * a, 8)
    box(c, -w / 2, -hh / 2, w, hh, col, a, 12, (0.72, 0.5, 0.06), 3)
    T(c, label, 0, 12 * s, 34 * s, tc, HEAD, "c", a)
    c.restore()


def label_at(c, x, y, h, s, size=30, fg=WHITE, bg=NAVY, a=1.0, f=BODY, dy=0):
    X, Y = P(x, y, h)
    pill(c, X, Y + dy, s, size, fg, bg, a, f)


def sign(c, n, title, t):
    k = e(t, 0, 0.45) * (1 - e(t, 3.2, 3.8))
    if k <= 0:
        return
    s = "STOP %d  ·  %s" % (n, title)
    w = tw(c, s, 44, HEAD) + 90
    x = 36 + (k - 1) * (w + 80)
    y = 142
    shadow(c, x, y, w, 88, 16, 0.3 * k, 8)
    box(c, x, y, w, 88, (0.08, 0.50, 0.30), 1, 16, WHITE, 5)
    T(c, s, x + w / 2, y + 60, 44, WHITE, HEAD, "c", 1)


def veil(c, a=0.62, col=(0.95, 0.97, 1.0)):
    c.set_source_rgba(*col, a)
    c.rectangle(0, 0, W, H)
    c.fill()


def card(c, x, y, w, h, a=1.0, col=WHITE, r=26):
    shadow(c, x, y, w, h, r, 0.28 * a, 12)
    box(c, x, y, w, h, col, a, r)


def hud(c, t_global=0.0):
    box(c, 36, 28, 300, 64, NAVY, 0.92, 32)
    logo(c, 50, 38, 0.46)
    T(c, "MONEY MAP", 112, 72, 28, WHITE, HEAD, "l")


def cnt(v0, v1, k, cents=False, pre="$"):
    return S.cnt(v0, v1, k, cents, pre)
