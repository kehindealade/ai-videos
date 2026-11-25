import cairo, math, sys, subprocess
from wv_common import *

DUR = 38.0
ARM_UP = 3.0
HEY0, HEY1 = 3.25, 5.4
ARC0, ARC_GROW = 3.6, 8.6
P2_IN, BEND, ARC_DONE, P2_CURB, ARC_OFF = 8.8, 9.0, 9.7, 10.6, 11.2
FREEZE = 10.4
STOP = 11.0
CROSS0, P2_FAR = 10.9, 13.0
HI5 = 13.3
REC = [15.0, 18.0, 21.0]
WALK = 24.0
NODS = [25.6, 26.4]
GLANCE = 28.0
PIG_OFF = 28.6
NOBODY, EVERY, END = 31.0, 33.0, 35.0

FAR_Y = 965
STRANGER_X = 330
P2_FAR_X = 500
FACE_WIN_X = 1100

LOOK_S = dict(shirt=(0.93, 0.42, 0.36), pants=(0.16, 0.20, 0.34), skin=(0.40, 0.26, 0.17), hair=(0.11, 0.08, 0.07), style=0)
LOOK_P2 = dict(shirt=(0.36, 0.76, 0.64), pants=(0.22, 0.22, 0.26), skin=(0.86, 0.66, 0.52), hair=(0.42, 0.20, 0.12), style=2)
LOOK_PB = dict(shirt=(0.42, 0.56, 0.80), pants=(0.30, 0.25, 0.22), skin=(0.62, 0.42, 0.28), hair=(0.14, 0.10, 0.08), style=1)
VSKIN = (0.58, 0.39, 0.27)
SLEEVE = (0.93, 0.64, 0.22)

BUILDINGS = [(-420, 270, 420, (0.86, 0.50, 0.40)), (-150, 300, 330, (0.96, 0.87, 0.72)), (150, 260, 470, (0.58, 0.72, 0.60)),
             (410, 290, 380, (0.47, 0.60, 0.77)), (700, 200, 450, (0.94, 0.74, 0.38)), (900, 290, 360, (0.80, 0.44, 0.38)),
             (1190, 260, 430, (0.95, 0.85, 0.70)), (1450, 300, 390, (0.56, 0.70, 0.58)), (1750, 270, 450, (0.47, 0.60, 0.77))]
TREES = [40, 650, 1330, 1900]


def scroll(t):
    return 380 * e(t, WALK, EVERY)


def walk_amp(t):
    return e(t, WALK, WALK + 0.4) * (1 - e(t, EVERY - 0.4, EVERY))


def bump(t, t0, d=0.5):
    if t < t0 or t > t0 + d:
        return 0.0
    return math.sin(math.pi * (t - t0) / d)


def limb(c, x0, y0, x1, y1, w, col):
    c.set_source_rgb(*col)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x0, y0)
    c.line_to(x1, y1)
    c.stroke()


def arm_pts(side, raise_amt, osc, reach=0.0):
    sx = 42 * side
    de = (sx + side * 10, -182)
    dh = (sx + side * 14, -124)
    ue = (sx + side * 60, -268)
    uh = (ue[0] + math.sin(osc) * 85 * side + reach * side * -40, ue[1] - math.cos(osc) * 85)
    k = raise_amt
    return (sx, -240), lerp2(de, ue, k), lerp2(dh, uh, k)


def person(c, x, y, s, look, facing="front", walk=None, arms=((0, 0, 0), (0, 0, 0)), eyes=0.0, bob=0.0):
    c.save()
    c.translate(x, y - bob)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    sw = 0.38 * math.sin(walk) if walk is not None else 0.0
    for k, sg in ((-1, 1), (1, -1)):
        hx = 18 * k
        ang = sw * sg
        fx, fy = hx + math.sin(ang) * 118, -128 + math.cos(ang) * 118
        limb(c, hx, -128, fx, fy, 38, look["pants"])
        c.set_source_rgb(*INK)
        c.save()
        c.translate(fx + 6 * k, fy + 6)
        c.scale(1.5, 0.8)
        c.arc(0, 0, 16, 0, 2 * math.pi)
        c.fill()
        c.restore()
    if look["style"] == 2 and facing == "back":
        pass
    c.set_source_rgb(*look["shirt"])
    rrect(c, -52, -265, 104, 150, 28)
    c.fill()
    c.set_source_rgb(*look["skin"])
    c.rectangle(-12, -292, 24, 34)
    c.fill()
    hands = []
    for i, side in enumerate((-1, 1)):
        ra, osc, reach = arms[i]
        sh, el, hd = arm_pts(side, ra, osc, reach)
        limb(c, sh[0], sh[1], el[0], el[1], 28, darken(look["shirt"], 0.08))
        limb(c, el[0], el[1], hd[0], hd[1], 24, darken(look["shirt"], 0.08) if ra < 0.5 else look["skin"])
        c.set_source_rgb(*look["skin"])
        c.arc(hd[0], hd[1], 17, 0, 2 * math.pi)
        c.fill()
        hands.append((x + hd[0] * s, y - bob + hd[1] * s))
    hy = -322
    hr = 43
    st = look["style"]
    if facing == "back":
        c.set_source_rgb(*look["skin"])
        c.arc(0, hy, hr, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*look["hair"])
        c.arc(0, hy - 2, hr + 2, 0, 2 * math.pi)
        c.fill()
        if st == 2:
            rrect(c, -46, hy - 10, 92, 120, 30)
            c.fill()
        if st == 1:
            c.arc(0, hy - 48, 19, 0, 2 * math.pi)
            c.fill()
    else:
        c.set_source_rgb(*look["hair"])
        if st == 2:
            for sx in (-1, 1):
                rrect(c, sx * 41 - 13, hy - 20, 26, 92, 13)
                c.fill()
        c.set_source_rgb(*look["skin"])
        c.arc(0, hy, hr, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*look["hair"])
        c.arc(0, hy, hr + 3, math.pi * 1.04, math.pi * 1.96)
        c.close_path()
        c.fill()
        if st == 1:
            c.arc(0, hy - 50, 19, 0, 2 * math.pi)
            c.fill()
        if eyes > 0:
            c.set_source_rgba(*INK, eyes)
            for ex in (-15, 15):
                c.save()
                c.translate(ex, hy + 6)
                c.scale(1, 1.3 * eyes)
                c.arc(0, 0, 6.5, 0, 2 * math.pi)
                c.fill()
                c.restore()
    c.restore()
    return hands


def building(c, x, w, top, col):
    c.set_source_rgb(*col)
    c.rectangle(x, top, w, FAR_Y - top)
    c.fill()
    c.set_source_rgb(*darken(col, 0.18))
    c.rectangle(x - 6, top, w + 12, 20)
    c.fill()
    glass = (0.30, 0.40, 0.52)
    n = max(2, int(w / 95))
    gap = w / n
    y = top + 55
    while y + 80 < 790:
        for i in range(n):
            wx = x + gap * i + gap / 2 - 28
            c.set_source_rgb(*darken(col, 0.25))
            rrect(c, wx - 5, y - 5, 66, 90, 8)
            c.fill()
            c.set_source_rgb(*glass)
            rrect(c, wx, y, 56, 80, 6)
            c.fill()
            c.set_source_rgba(1, 1, 1, 0.22)
            c.move_to(wx + 10, y + 60)
            c.line_to(wx + 34, y + 12)
            c.set_line_width(6)
            c.stroke()
        y += 120
    aw = (0.95, 0.95, 0.92)
    ac = darken(col, 0.35)
    c.set_source_rgb(*darken(col, 0.1))
    c.rectangle(x, 805, w, FAR_Y - 805)
    c.fill()
    c.set_source_rgb(*(0.62, 0.74, 0.80))
    c.rectangle(x + 20, 850, w * 0.55, 100)
    c.fill()
    c.set_source_rgb(*darken(col, 0.4))
    c.rectangle(x + w * 0.70, 855, w * 0.18, 110)
    c.fill()
    stripes = 8
    sw_ = (w * 0.62) / stripes
    for i in range(stripes):
        c.set_source_rgb(*(aw if i % 2 == 0 else ac))
        c.move_to(x + 12 + i * sw_, 810)
        c.line_to(x + 12 + (i + 1) * sw_, 810)
        c.line_to(x + 12 + (i + 1) * sw_, 842)
        c.arc(x + 12 + (i + 0.5) * sw_, 842, sw_ / 2, 0, math.pi)
        c.close_path()
        c.fill()


def face_window(c, x, t):
    y = 520
    c.set_source_rgb(0.55, 0.30, 0.27)
    rrect(c, x - 70, y - 10, 140, 170, 10)
    c.fill()
    c.set_source_rgb(0.24, 0.30, 0.40)
    rrect(c, x - 60, y, 120, 150, 6)
    c.fill()
    k = e(t, EVERY - 0.1, EVERY + 0.25)
    if k > 0:
        c.save()
        rrect(c, x - 60, y, 120, 150, 6)
        c.clip()
        person(c, x, y + 300, 0.62, LOOK_PB | dict(shirt=(0.85, 0.55, 0.65), style=3, hair=(0.25, 0.16, 0.10)), eyes=k)
        c.restore()
    cw = 60 * (1 - 0.75 * k)
    c.set_source_rgb(0.98, 0.86, 0.62)
    for sgn in (-1, 1):
        x0 = x - 60 if sgn < 0 else x + 60 - cw
        c.rectangle(x0, y, cw, 150)
        c.fill()
    c.set_source_rgb(0.55, 0.30, 0.27)
    c.rectangle(x - 74, y + 150, 148, 14)
    c.fill()


def tree(c, x):
    c.set_source_rgb(0.42, 0.30, 0.22)
    c.rectangle(x - 10, 790, 20, FAR_Y - 790)
    c.fill()
    c.set_source_rgb(0.32, 0.58, 0.40)
    for dx, dy, r in ((-40, 780, 62), (35, 772, 66), (0, 725, 72), (-10, 795, 58)):
        c.arc(x + dx, dy, r, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(1, 1, 1, 0.10)
    c.arc(x - 18, 708, 30, 0, 2 * math.pi)
    c.fill()


def stranger_state(t):
    osc = 0.45 * math.sin(2 * math.pi * 1.6 * t)
    ra = 1.0 - e(t, 10.6, 11.2)
    ra = max(ra, bump(t, HI5 - 0.35, 0.9) ** 0.6)
    reach = bump(t, HI5 - 0.35, 0.9)
    if t > HI5 - 0.35 and t < HI5 + 0.55:
        osc = -0.6 * reach
    if t >= EVERY:
        ra, osc = 0.0, 0.0
    eyes = e(t, EVERY, EVERY + 0.15)
    bob = 4 * abs(math.sin(2 * math.pi * 1.2 * t)) if HI5 + 0.6 < t < EVERY else 0
    return dict(arms=((0, 0, 0), (ra, osc, 0)), eyes=eyes, bob=bob)


def p2_state(t):
    if t < P2_IN:
        return None
    a = (-280, 2520, 3.0)
    b = (300, 1405, 1.35)
    f = (P2_FAR_X, FAR_Y + 3, 1.0)
    if t < P2_CURB:
        k = 1 - (1 - clamp((t - P2_IN) / (P2_CURB - P2_IN))) ** 2
        p = tuple(lerp(a[i], b[i], k) for i in range(3))
        walk = 2 * math.pi * 1.9 * t
    elif t < CROSS0:
        p = b
        walk = None
    elif t < P2_FAR:
        k = e(t, CROSS0, P2_FAR)
        p = tuple(lerp(b[i], f[i], k) for i in range(3))
        walk = 2 * math.pi * 1.9 * t if k < 0.98 else None
    else:
        p = f
        walk = None
    osc = 0.5 * math.sin(2 * math.pi * 1.7 * t + 1.0)
    wave = 1.0 - e(t, CROSS0 - 0.2, CROSS0 + 0.3)
    reach = bump(t, HI5 - 0.35, 0.9)
    left = (reach ** 0.6, 0.6 * reach, 0) if reach > 0 else (0, 0, 0)
    facing = "back" if t < EVERY else "front"
    eyes = e(t, EVERY, EVERY + 0.15)
    bob = 4 * abs(math.sin(2 * math.pi * 1.2 * t + 0.7)) if HI5 + 0.6 < t < EVERY else 0
    arms = (left, (wave, osc, 0)) if t < EVERY else ((0, 0, 0), (0, 0, 0))
    return dict(x=p[0], y=p[1], s=p[2], walk=walk, arms=arms, facing=facing, eyes=eyes, bob=bob)


def passer_state(t):
    if t < 24.8:
        return None
    x = 1150 - 55 * (min(t, EVERY) - 24.8)
    glance = e(t, GLANCE, GLANCE + 0.12) * (1 - e(t, GLANCE + 0.8, GLANCE + 0.95))
    eyes = max(glance, e(t, EVERY, EVERY + 0.15))
    walk = 2 * math.pi * 1.8 * t if t < EVERY else None
    return dict(x=x, eyes=eyes, walk=walk)


def bird(c, x, y, t):
    c.set_source_rgb(*INK)
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    f = 18 * math.sin(2 * math.pi * 3 * t)
    c.move_to(x - 40, y - f)
    c.curve_to(x - 20, y - 18, x - 8, y - 6, x, y)
    c.curve_to(x + 8, y - 6, x + 20, y - 18, x + 40, y - f)
    c.stroke()


def cloud(c, x, y, s):
    c.set_source_rgb(1.0, 0.97, 0.92)
    for dx, dy, r in ((-60, 10, 45), (0, -15, 60), (60, 8, 48), (20, 20, 45), (-25, 22, 40)):
        c.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
        c.fill()


def pigeon(c, x, y, t, peck=True, stare=0.0, s=1.0, walk=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pk = 0.0
    if peck and stare == 0:
        ph = (t * 0.8) % 1.0
        pk = bump(ph, 0.6, 0.25)
    hop = 6 * abs(math.sin(2 * math.pi * 3 * t)) if walk else 0
    c.translate(0, -hop)
    c.set_source_rgb(0.95, 0.55, 0.40)
    c.set_line_width(5)
    for lx in (-8, 8):
        c.move_to(lx, -10)
        c.line_to(lx, 18)
        c.stroke()
    c.set_source_rgb(0.55, 0.57, 0.64)
    c.save()
    c.scale(1.35, 0.85)
    c.arc(0, -30, 38, 0, 2 * math.pi)
    c.fill()
    c.restore()
    c.set_source_rgb(0.40, 0.42, 0.50)
    c.move_to(30, -40)
    c.line_to(80, -55)
    c.line_to(70, -25)
    c.close_path()
    c.fill()
    hx, hy = -40, -62 + 40 * pk
    c.set_source_rgb(0.42, 0.60, 0.58)
    c.arc(-30, -48 + 20 * pk, 20, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.55, 0.57, 0.64)
    c.arc(hx, hy, 20, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(0.95, 0.70, 0.30)
    c.move_to(hx - 18, hy - 3)
    c.line_to(hx - 36, hy + 3)
    c.line_to(hx - 18, hy + 7)
    c.close_path()
    c.fill()
    c.set_source_rgb(1, 1, 1)
    c.arc(hx - 4 + 4 * stare, hy - 4, 7 + 2 * stare, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    c.arc(hx - 4 + 6 * stare, hy - 4, 3.5 + 1.5 * stare, 0, 2 * math.pi)
    c.fill()
    c.restore()


def bez(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])


def dotted_arc(c, p0, p1, p2, grow, t, alpha=1.0, head=True, qmark=False):
    pts = [bez(p0, p1, p2, i / 300) for i in range(301)]
    L = [0.0]
    for i in range(1, 301):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    tot = L[-1]
    lim = tot * grow
    sp = 40
    off = (t * 90) % sp
    d = off
    j = 0
    while d < lim - 18:
        while j < 300 and L[j + 1] < d:
            j += 1
        f = d / tot
        x, y = pts[j]
        r = 6 + 12 * f
        c.set_source_rgba(*INK, alpha)
        c.arc(x, y, r + 4, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*CREAM, alpha)
        c.arc(x, y, r, 0, 2 * math.pi)
        c.fill()
        d += sp
    if head and grow > 0.02:
        jj = next((i for i in range(301) if L[i] >= lim), 300)
        x, y = pts[jj]
        r = 18 + 16 * grow
        if qmark:
            r = 70
        c.set_source_rgba(*INK, alpha)
        c.arc(x + 6, y + 6, r + 6, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*CORAL, alpha)
        c.arc(x, y, r, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*INK, alpha)
        c.set_line_width(6)
        c.arc(x, y, r, 0, 2 * math.pi)
        c.stroke()
        if qmark:
            txt(c, "?", x, y + 36, 104, CREAM, a=alpha)
        return (x, y)
    return None


def hand(c, x, y, ang, side=1, s=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(side * s, s)
    out = darken(VSKIN, 0.45)
    for stroke in (True, False):
        c.set_source_rgb(*(out if stroke else VSKIN))
        grow = 7 if stroke else 0
        c.save()
        c.translate(-48, -62)
        c.rotate(-0.95)
        rrect(c, -18 - grow, -78 - grow, 36 + 2 * grow, 92 + 2 * grow, 18 + grow)
        c.fill()
        c.restore()
        for fx, ln in ((-42, 82), (-14, 102), (14, 96), (42, 76)):
            rrect(c, fx - 15 - grow, -112 - ln - grow, 30 + 2 * grow, ln + 40 + 2 * grow, 15 + grow)
            c.fill()
        rrect(c, -62 - grow, -128 - grow, 124 + 2 * grow, 140 + 2 * grow, 42 + grow)
        c.fill()
    c.set_source_rgba(*darken(VSKIN, 0.25), 0.8)
    c.set_line_width(4)
    for fx in (-42, -14, 14, 42):
        c.move_to(fx - 7, -112)
        c.line_to(fx + 7, -112)
        c.stroke()
    c.restore()


def viewer_arm(c, sh, el, wr, ang, side=1):
    dx, dy = wr[0] - el[0], wr[1] - el[1]
    dl = math.hypot(dx, dy) or 1
    ux, uy = dx / dl, dy / dl
    cuff0 = (wr[0] - ux * 70, wr[1] - uy * 70)
    out = darken(SLEEVE, 0.45)
    limb(c, sh[0], sh[1], el[0], el[1], 214, out)
    limb(c, el[0], el[1], cuff0[0], cuff0[1], 166, out)
    limb(c, wr[0] - ux * 40, wr[1] - uy * 40, wr[0], wr[1], 104, darken(VSKIN, 0.45))
    limb(c, wr[0] - ux * 40, wr[1] - uy * 40, wr[0], wr[1], 94, VSKIN)
    limb(c, sh[0], sh[1], el[0], el[1], 202, SLEEVE)
    limb(c, el[0], el[1], cuff0[0], cuff0[1], 154, SLEEVE)
    c.set_source_rgba(*lighten(SLEEVE, 0.3), 0.7)
    c.set_line_width(18)
    c.move_to(el[0] - uy * 45, el[1] + ux * 45)
    c.line_to(cuff0[0] - uy * 40, cuff0[1] + ux * 40)
    c.stroke()
    limb(c, cuff0[0] - ux * 10, cuff0[1] - uy * 10, cuff0[0] + ux * 26, cuff0[1] + uy * 26, 174, out)
    limb(c, cuff0[0] - ux * 6, cuff0[1] - uy * 6, cuff0[0] + ux * 22, cuff0[1] + uy * 22, 162, darken(SLEEVE, 0.18))
    hand(c, wr[0], wr[1], ang, side)


POSES_R = {
    "down": ((1120, 2260), (1090, 2200), (980, 2380), 0.0),
    "wave": ((1120, 2260), (960, 1560), (810, 960), -0.12),
    "hair": ((1120, 2260), (990, 1150), (760, 330), -0.55),
    "visor": ((1120, 2260), (930, 1180), (700, 330), -1.62),
    "stretch": ((1120, 2260), (990, 1050), (880, 300), 0.12),
}
POSES_L = {
    "down": ((-40, 2260), (-10, 2200), (100, 2380), 0.0),
    "stretch": ((-40, 2260), (90, 1050), (200, 300), -0.12),
}
KEYS_R = [(0, "down"), (ARM_UP, "down"), (ARM_UP + 0.35, "wave"), (REC[0], "wave"), (REC[0] + 0.5, "hair"), (REC[1] - 0.4, "hair"),
          (REC[1] + 0.1, "visor"), (REC[2] - 0.4, "visor"), (REC[2] + 0.2, "stretch"), (REC[2] + 2.4, "stretch"), (REC[2] + 2.95, "down")]
KEYS_L = [(0, "down"), (REC[2] - 0.2, "down"), (REC[2] + 0.3, "stretch"), (REC[2] + 2.4, "stretch"), (REC[2] + 2.95, "down")]


def pose_at(keys, poses, t):
    if t <= keys[0][0]:
        return poses[keys[0][1]]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            if t1 - t0 < 1e-6 or a == b:
                return poses[b]
            k = clamp((t - t0) / (t1 - t0))
            k = back(k) if (a == "down" and b == "wave") else k * k * (3 - 2 * k)
            pa, pb = poses[a], poses[b]
            return tuple(lerp2(pa[i], pb[i], k) for i in range(3)) + (lerp(pa[3], pb[3], k),)
    return poses[keys[-1][1]]


def rot_about(p, o, a):
    dx, dy = p[0] - o[0], p[1] - o[1]
    ca, sa = math.cos(a), math.sin(a)
    return (o[0] + dx * ca - dy * sa, o[1] + dx * sa + dy * ca)


def draw_viewer(c, t):
    sh, el, wr, ang = pose_at(KEYS_R, POSES_R, t)
    if ARM_UP <= t < REC[0] + 0.5:
        if t < FREEZE:
            a = 0.30 * math.sin(2 * math.pi * 2.3 * (t - ARM_UP))
        else:
            a0 = 0.30 * math.sin(2 * math.pi * 2.3 * (FREEZE - ARM_UP))
            a = lerp(a0, 0.10, e(t, FREEZE, FREEZE + 0.25))
            if t > STOP:
                a += 0.012 * math.sin(2 * math.pi * 9 * t)
        k = 1 - e(t, REC[0], REC[0] + 0.5)
        a *= k
        wr = rot_about(wr, el, a)
        ang += a
    if REC[0] + 0.5 <= t < REC[1] - 0.4:
        p = 40 * math.sin(2 * math.pi * 2.6 * (t - REC[0]))
        wr = (wr[0] + p, wr[1] + abs(p) * 0.2)
        ang += p * 0.004
    if REC[2] + 0.2 <= t < REC[2] + 2.4:
        w = 18 * math.sin(2 * math.pi * 1.2 * (t - REC[2]))
        wr = (wr[0] + w, wr[1] - abs(w))
    if wr[1] < VH + 300:
        viewer_arm(c, sh, el, wr, ang, 1)
    if t > REC[2] - 0.3 and t < REC[2] + 3.0:
        sh, el, wr, ang = pose_at(KEYS_L, POSES_L, t)
        if REC[2] + 0.3 <= t < REC[2] + 2.4:
            w = 18 * math.sin(2 * math.pi * 1.2 * (t - REC[2]))
            wr = (wr[0] - w, wr[1] - abs(w))
        viewer_arm(c, sh, el, wr, ang, -1)


def fringe(c, t):
    k = e(t, REC[0] + 0.2, REC[0] + 0.6) * (1 - e(t, REC[1] - 0.5, REC[1] - 0.1))
    if k <= 0:
        return
    dy = -150 + 150 * k
    c.save()
    c.translate(0, dy)
    c.set_source_rgb(0.14, 0.10, 0.09)
    c.move_to(-20, -20)
    for i in range(12):
        x0 = -20 + i * 95
        sway = 10 * math.sin(2 * math.pi * 2.6 * t + i)
        c.curve_to(x0 + 20, 120 + sway, x0 + 60, 150 + sway, x0 + 95, 70 + (i % 3) * 25)
    c.line_to(1100, -20)
    c.close_path()
    c.fill()
    c.restore()


def burst(c, x, y, r, col, a=1.0, n=14):
    c.new_path()
    for i in range(n * 2):
        ang = math.pi * i / n - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.72
        px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr
        if i == 0:
            c.move_to(px, py)
        else:
            c.line_to(px, py)
    c.close_path()


def hey(c, t):
    if t < HEY0 or t > HEY1:
        return
    k = back(clamp((t - HEY0) / 0.25))
    a = 1 - e(t, HEY1 - 0.25, HEY1)
    wob = 0.04 * math.sin(2 * math.pi * 4 * t)
    c.save()
    c.translate(800, 470)
    c.rotate(0.08 + wob)
    c.scale(0.4 + 0.6 * k, 0.4 + 0.6 * k)
    burst(c, 10, 10, 175, INK)
    c.set_source_rgba(*INK, a)
    c.fill()
    burst(c, 0, 0, 175, INK)
    c.set_source_rgba(1.0, 0.84, 0.30, a)
    c.fill_preserve()
    c.set_source_rgba(*INK, a)
    c.set_line_width(7)
    c.stroke()
    txt(c, "HEY!!", 0, 38, 104, CORAL, a=a)
    c.restore()


def card(c, lines, cy, t, t0, t1, size=100, rot=-0.03, tag=None):
    if t < t0 or t > t1:
        return
    kin = 1.0 if t0 <= 0.01 else back(clamp((t - t0) / 0.28))
    kout = 1 - e(t, t1 - 0.2, t1)
    if t0 <= 0.01:
        kin = 0.94 + 0.06 * e(t, 0, 0.3)
    sc = (0.55 + 0.45 * kin) * (1 - 0.12 * (1 - kout))
    a = kout
    w = max(tw(c, s, size) for s, _ in lines) + 110
    lh = size * 1.02
    h = lh * len(lines) + 64
    c.save()
    c.translate(540, cy)
    c.rotate(rot)
    c.scale(sc, sc)
    c.set_source_rgba(*INK, a)
    rrect(c, -w / 2 + 14, -h / 2 + 14, w, h, 26)
    c.fill()
    c.set_source_rgba(*CREAM, a)
    rrect(c, -w / 2, -h / 2, w, h, 26)
    c.fill_preserve()
    c.set_source_rgba(*INK, a)
    c.set_line_width(8)
    c.stroke()
    for i, (s, col) in enumerate(lines):
        txt(c, s, 0, -h / 2 + 32 + lh * i + size * 0.86, size, col, a=a)
    if tag:
        tw_ = tw(c, tag, 54) + 60
        ty = -h / 2 - 40
        c.set_source_rgba(*INK, a)
        rrect(c, -tw_ / 2 + 7, ty - 38 + 7, tw_, 82, 41)
        c.fill()
        c.set_source_rgba(*CORAL, a)
        rrect(c, -tw_ / 2, ty - 38, tw_, 82, 41)
        c.fill()
        txt(c, tag, 0, ty + 22, 54, WHITE, a=a)
    c.restore()


def camera(t):
    z, cx, cy = 1.0 + 0.03 * e(t, 0, 9), 540, 760
    zf = 0.07 * e(t, STOP, REC[0] - 0.5) * (1 - e(t, REC[0], REC[0] + 0.5))
    z += zf
    if zf > 0:
        cx, cy = lerp(540, 430, zf / 0.07), lerp(760, 700, zf / 0.07)
    zl = 0.06 * e(t, NOBODY, EVERY + 0.6)
    if zl > 0:
        z = 1.0 + zl
        cx, cy = 420, 760
    dy = 420 * e(t, REC[1] + 0.3, REC[1] + 0.9) * (1 - e(t, REC[2] - 0.7, REC[2] - 0.1))
    dy -= 45 * (bump(t, NODS[0], 0.45) + bump(t, NODS[1], 0.45))
    dy += 10 * abs(math.sin(math.pi * 1.8 * (t - WALK))) * walk_amp(t)
    return z, cx, cy, dy


def world(c, t, z, cx, cy, dy, cover=False):
    S = scroll(t)
    far, mid, near = -0.45 * S, -0.7 * S, -1.0 * S
    c.save()
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy + dy)
    g = cairo.LinearGradient(0, -700, 0, FAR_Y)
    g.add_color_stop_rgb(0, 0.97, 0.62, 0.52)
    g.add_color_stop_rgb(0.55, 0.99, 0.80, 0.66)
    g.add_color_stop_rgb(1, 1.0, 0.91, 0.78)
    c.set_source(g)
    c.rectangle(-400, -800, 1900, FAR_Y + 820)
    c.fill()
    rg = cairo.RadialGradient(250 + far * 0.2, 200, 40, 250 + far * 0.2, 200, 260)
    rg.add_color_stop_rgba(0, 1, 0.97, 0.80, 0.9)
    rg.add_color_stop_rgba(1, 1, 0.97, 0.80, 0)
    c.set_source(rg)
    c.arc(250 + far * 0.2, 200, 260, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(1.0, 0.95, 0.72)
    c.arc(250 + far * 0.2, 200, 88, 0, 2 * math.pi)
    c.fill()
    cloud(c, 820 + far * 0.3 + 6 * t, 170, 1.0)
    cloud(c, 330 + far * 0.3 + 4 * t, -230, 1.2)
    cloud(c, 760 + far * 0.3 + 5 * t, -430, 0.9)
    if REC[1] + 0.4 < t < REC[2]:
        bx = lerp(-80, 1160, clamp((t - REC[1] - 0.4) / 2.4))
        bird(c, bx, -170 + 30 * math.sin(t * 2), t)
        bird(c, bx - 130, -120 + 30 * math.sin(t * 2 + 1), t + 0.2)
    c.save()
    c.translate(far, 0)
    for (x, w, top, col) in BUILDINGS:
        building(c, x, w, top, col)
    face_window(c, FACE_WIN_X, t)
    for x in TREES:
        tree(c, x)
    c.restore()
    c.set_source_rgb(0.88, 0.82, 0.74)
    c.rectangle(-400, FAR_Y, 1900, 30)
    c.fill()
    c.set_source_rgb(0.74, 0.68, 0.62)
    c.rectangle(-400, FAR_Y + 30, 1900, 12)
    c.fill()
    hands = {}
    st = stranger_state(t)
    hs = person(c, STRANGER_X + far, FAR_Y, 1.0, LOOK_S, "front", None, st["arms"], st["eyes"], st["bob"])
    hands["s"] = hs[1]
    pb = passer_state(t)
    if pb:
        person(c, pb["x"] + far, FAR_Y + 2, 0.96, LOOK_PB, "front", pb["walk"], ((0, 0, 0), (0, 0, 0)), pb["eyes"])
    p2 = p2_state(t)
    if p2 and p2["s"] <= 1.05:
        hands["p2"] = person(c, p2["x"] + far, p2["y"], p2["s"], LOOK_P2, p2["facing"], p2["walk"], p2["arms"], p2["eyes"], p2["bob"])[1]
    c.set_source_rgb(0.17, 0.43, 0.47)
    c.rectangle(-400, FAR_Y + 42, 1900, 1340 - FAR_Y - 42)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.05)
    c.rectangle(-400, FAR_Y + 42, 1900, 40)
    c.fill()
    c.set_source_rgb(0.98, 0.90, 0.70)
    d0 = (mid % 170) - 340
    x = d0
    while x < 1500:
        rrect(c, x, 1170, 95, 16, 8)
        c.fill()
        x += 170
    c.set_source_rgb(0.80, 0.74, 0.66)
    c.rectangle(-400, 1340, 1900, 26)
    c.fill()
    c.set_source_rgb(0.66, 0.60, 0.54)
    c.rectangle(-400, 1366, 1900, 10)
    c.fill()
    c.set_source_rgb(0.94, 0.85, 0.71)
    c.rectangle(-400, 1376, 1900, 900)
    c.fill()
    c.set_source_rgba(0.72, 0.62, 0.50, 0.55)
    c.set_line_width(5)
    for yy in (1440, 1540, 1680, 1880):
        c.move_to(-400, yy)
        c.line_to(1500, yy)
        c.stroke()
    for i in range(-6, 12):
        xt = 540 + (i * 150 + (mid % 150)) - 540 * 0
        xb = 540 + (xt - 540) * 3.2 + (near - mid) * 0
        c.move_to(xt, 1376)
        c.line_to(xb, 2300)
        c.stroke()
    if p2 and p2["s"] > 1.05:
        hands["p2"] = person(c, p2["x"], p2["y"], p2["s"], LOOK_P2, p2["facing"], p2["walk"], p2["arms"], p2["eyes"], p2["bob"])[1]
    if not cover:
        draw_pigeon(c, t, near)
    arc_draw(c, t, hands, cover)
    if p2 and HI5 - 0.05 < t < HI5 + 0.6:
        k = clamp((t - HI5 + 0.05) / 0.6)
        mx = (STRANGER_X + P2_FAR_X) / 2 + far
        c.save()
        burst(c, mx, 640, 40 + 70 * k, INK, n=10)
        c.set_source_rgba(1.0, 0.84, 0.30, 1 - k)
        c.fill()
        c.restore()
    c.restore()
    return hands


def draw_pigeon(c, t, near):
    if t < PIG_OFF:
        pigeon(c, 260 + near * 0.0, 1650, t)
        return
    if t < EVERY - 0.2:
        x = 260 - 260 * clamp((t - PIG_OFF) / 1.6)
        if x > -120:
            pigeon(c, x, 1650, t, peck=False, walk=True)
        return
    k = e(t, EVERY - 0.1, EVERY + 0.3)
    pigeon(c, lerp(-130, 40, k), 1650, t, peck=False, stare=k)


ARC_END0 = (650, 1560)


def arc_draw(c, t, hands, cover):
    if cover:
        s = hands["s"]
        dotted_arc(c, s, (s[0] + 330, 560), (560, 1290), 1.0, 0.3, qmark=True)
        return
    if t < ARC0 or t > ARC_OFF:
        return
    s = hands["s"]
    c0 = (s[0] + 380, 300)
    if t < BEND:
        g = 0.85 * (1 - (1 - clamp((t - ARC0) / (ARC_GROW - ARC0))) ** 1.6)
        dotted_arc(c, s, c0, ARC_END0, g, t)
        return
    k = e(t, BEND, ARC_DONE)
    tgt = hands.get("p2", ARC_END0)
    end = lerp2(ARC_END0, tgt, k)
    ctl = lerp2(c0, ((s[0] + tgt[0]) / 2 - 80, min(s[1], tgt[1]) - 380), k)
    g = lerp(0.85, 1.0, k)
    a = 1 - e(t, ARC_OFF - 0.4, ARC_OFF)
    hp = dotted_arc(c, s, ctl, end, g, t, alpha=a)
    if t > ARC_DONE and hp:
        kk = clamp((t - ARC_DONE) / 0.6)
        c.set_source_rgba(*CORAL, 1 - kk)
        c.set_line_width(10)
        c.arc(tgt[0], tgt[1], 30 + 120 * kk, 0, 2 * math.pi)
        c.stroke()


def endcard(c, t):
    if t < END:
        return
    a = e(t, END, END + 0.25)
    c.set_source_rgba(0.09, 0.27, 0.31, a)
    c.paint()
    k = back(clamp((t - END - 0.1) / 0.4))
    c.save()
    c.set_source_rgba(1, 1, 1, 0.0)
    pts_a = (120, 520)
    pts_b = (960, 520)
    c.restore()
    for i in range(12):
        f = i / 11
        x = lerp(140, 940, f)
        y = 470 - 120 * math.sin(math.pi * f)
        if f <= k:
            c.set_source_rgba(*CREAM, a * 0.85)
            c.arc(x, y, 7 + 6 * f, 0, 2 * math.pi)
            c.fill()
    sprout(c, 540, 700, 0.95 * (0.6 + 0.4 * k), a)
    txt(c, "IT'S NOT JUST ME", 540, 900, 104, CREAM, a=a)
    txt(c, "EPISODE 2 · THE WRONG WAVE", 540, 985, 52, MINT, f=B, a=a)
    pw = tw(c, "FOLLOW FOR EPISODE 3", 56) + 90
    py = 1060
    c.set_source_rgba(*INK, a)
    rrect(c, 540 - pw / 2 + 8, py + 8, pw, 96, 48)
    c.fill()
    c.set_source_rgba(1.0, 0.84, 0.30, a)
    rrect(c, 540 - pw / 2, py, pw, 96, 48)
    c.fill()
    txt(c, "FOLLOW FOR EPISODE 3", 540, py + 68, 56, INK, a=a)


def frame(c, t):
    z, cx, cy, dy = camera(t)
    world(c, t, z, cx, cy, dy)
    draw_viewer(c, t)
    fringe(c, t)
    hey(c, t)
    card(c, [("WAS THAT WAVE", INK), ("FOR YOU?", CORAL)], 1200, t, 0.0, 3.0)
    card(c, [("FIX THE HAIR", INK)], 1210, t, REC[0], REC[1] - 0.15, size=104, rot=0.025, tag="RECOVERY 1")
    card(c, [("CHECK THE SKY", INK)], 1210, t, REC[1], REC[2] - 0.15, size=104, rot=-0.025, tag="RECOVERY 2")
    card(c, [("BIG STRETCH", INK)], 1210, t, REC[2], WALK - 0.15, size=104, rot=0.025, tag="RECOVERY 3")
    card(c, [("NOBODY", INK), ("SAW THAT.", INK)], 1200, t, NOBODY, EVERY - 0.05, size=110, rot=-0.02)
    card(c, [("EVERYBODY", CORAL), ("SAW THAT.", INK)], 1200, t, EVERY, END, size=110, rot=0.03)
    endcard(c, t)


def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    return s, cairo.Context(s)


def still(t, out):
    s, c = surface()
    frame(c, t)
    s.write_to_png(out)


def cover(out):
    s, c = surface()
    t = 6.2
    world(c, t, 1.0, 540, 760, 170, cover=True)
    sh, el, wr, ang = POSES_R["wave"]
    viewer_arm(c, sh, (el[0] + 40, el[1] + 220), (wr[0] + 60, wr[1] + 300), ang + 0.15)
    card(c, [("WAS THAT WAVE", INK), ("FOR YOU?", CORAL)], 560, 1.0, 0.0, 9.0, size=112)
    s.write_to_png(out)


def render(f0, f1, out):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{VW}x{VH}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    s, c = surface()
    for i in range(f0, f1):
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame(c, i / FPS)
        s.flush()
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        still(float(sys.argv[2]), sys.argv[3])
    elif cmd == "cover":
        cover(sys.argv[2])
    elif cmd == "part":
        render(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
