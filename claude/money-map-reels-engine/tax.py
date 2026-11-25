import sys, math, cairo
from common import *

H = "Montserrat"
B = "Roboto"
DUR = 38.4
BEAT = DUR / 64
BASE = 1075
TX, TW = 170, 380
S = 9 / 1000.0
ROW = 4000
INK = (0.10, 0.12, 0.18)
PLATE = (0.15, 0.50, 0.27)
CREAM = (0.97, 0.95, 0.88)
YEL = (0.98, 0.78, 0.10)
BLU = (0.13, 0.42, 0.88)
RED = (0.88, 0.16, 0.14)
GRN = (0.10, 0.62, 0.30)
DED = 16600
L10 = DED + 12800
L12 = DED + 52025
PAY0 = 68000
RAISE = 5000
PAY1 = PAY0 + RAISE
TAX0 = 0.10 * 12800 + 0.12 * (PAY0 - DED - 12800)
TAX1 = 0.10 * 12800 + 0.12 * 39225 + 0.22 * (PAY1 - L12)
assert abs(TAX0 - 5912) < 1e-6 and abs(TAX1 - 6949.5) < 1e-6
MYTHTAX = 0.22 * (PAY1 - DED)
T_DED, T_10, T_12, T_RAISE, T_MYTH, T_WRONG, T_MATH, T_PAY, T_LAD, T_END = 3.0, 5.4, 7.0, 9.0, 12.0, 15.0, 16.0, 21.0, 26.4, 32.4
NROWS0 = 17
LX = 595
_BG = None


def Y(v):
    return BASE - v * S


def bg(c):
    global _BG
    if _BG is None:
        import random
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, 0.06, 0.08, 0.15)
        g.add_color_stop_rgb(0.55, 0.09, 0.12, 0.22)
        g.add_color_stop_rgb(1, 0.04, 0.05, 0.10)
        d.set_source(g)
        d.paint()
        g = cairo.RadialGradient(TX + TW / 2, 720, 40, TX + TW / 2, 720, 720)
        g.add_color_stop_rgba(0, 0.35, 0.55, 0.75, 0.30)
        g.add_color_stop_rgba(1, 0.35, 0.55, 0.75, 0.0)
        d.set_source(g)
        d.paint()
        for k in range(3):
            d.save()
            d.translate(760 + 120 * k, -100)
            d.rotate(0.38)
            lg = cairo.LinearGradient(-60, 0, 60, 0)
            lg.add_color_stop_rgba(0, 1, 1, 1, 0)
            lg.add_color_stop_rgba(0.5, 1, 1, 1, 0.035)
            lg.add_color_stop_rgba(1, 1, 1, 1, 0)
            d.set_source(lg)
            d.rectangle(-60, 0, 120, 2600)
            d.fill()
            d.restore()
        d.save()
        d.translate(TX + TW / 2, BASE + 6)
        d.scale(1, 0.16)
        g = cairo.RadialGradient(0, 0, 10, 0, 0, 330)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.55)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        d.set_source(g)
        d.arc(0, 0, 330, 0, 2 * math.pi)
        d.fill()
        d.restore()
        d.set_source_rgba(1, 1, 1, 0.06)
        d.rectangle(0, BASE + 4, VW, 2)
        d.fill()
        rng = random.Random(4)
        for _ in range(2500):
            d.set_source_rgba(1, 1, 1, rng.uniform(0.01, 0.035))
            d.rectangle(rng.uniform(0, VW), rng.uniform(0, VH), 2, 2)
            d.fill()
        g = cairo.RadialGradient(540, 900, 500, 540, 960, 1300)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
        d.set_source(g)
        d.paint()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def slab(c, x, y, w, h, col, a=1.0, studs=False, outline=None):
    rrect(c, x + 4, y + 8, w, h, 18)
    c.set_source_rgba(0, 0, 0, 0.35 * a)
    c.fill()
    rrect(c, x, y, w, h, 18)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, *mix(col, (1, 1, 1), 0.12), a)
    g.add_color_stop_rgba(1, *mix(col, (0, 0, 0), 0.10), a)
    c.set_source(g)
    c.fill()


BILL = (0.83, 0.88, 0.78)
BILL_D = (0.55, 0.66, 0.52)


def bundle(c, x, y, w, h, strap, a=1.0, tint=0.0, outline=None):
    body = mix(BILL, (0.95, 0.55, 0.50), tint)
    edge = mix(BILL_D, (0.70, 0.25, 0.22), tint)
    rrect(c, x, y, w, h, 3)
    c.set_source_rgba(*body, a)
    c.fill()
    c.set_line_width(1.4)
    yy = y + 4
    while yy < y + h - 2:
        c.set_source_rgba(*edge, 0.75 * a)
        c.move_to(x + 2, yy)
        c.line_to(x + w - 2, yy)
        c.stroke()
        yy += 4.5
    sw = 92
    c.rectangle(x + w / 2 - sw / 2, y - 1, sw, h + 2)
    c.set_source_rgba(*strap, a)
    c.fill()
    c.rectangle(x + w / 2 - sw / 2, y - 1, sw, 3)
    c.set_source_rgba(1, 1, 1, 0.35 * a)
    c.fill()
    rrect(c, x, y, w, h, 3)
    c.set_source_rgba(0, 0, 0, 0.30 * a)
    c.set_line_width(2)
    c.stroke()
    if outline:
        rrect(c, x - 4, y - 4, w + 8, h + 8, 6)
        c.set_source_rgba(*outline, a)
        c.set_line_width(5)
        c.stroke()


brick = slab


STRAP0 = (0.62, 0.66, 0.70)


def band_col(v0, v1, T):
    ded = e(T, T_DED, T_DED + 0.5)
    y10 = e(T, T_10, T_10 + 0.7)
    y12 = e(T, T_12, T_12 + 0.9)
    myth = e(T, T_MYTH + 0.2, T_MYTH + 0.6) * (1 - e(T, T_WRONG, T_WRONG + 0.5))
    r22 = e(T, T_MATH, T_MATH + 0.6)
    vm = (v0 + v1) / 2
    if vm < DED:
        return mix(STRAP0, (0.92, 0.94, 0.96), ded), 1 - 0.45 * ded, 0.0
    if vm < L10:
        col = mix(STRAP0, YEL, y10)
    elif vm < L12:
        col = mix(STRAP0, BLU, y12)
    else:
        col = mix(mix(STRAP0, BLU, y12), RED, r22)
    tint = 0.75 * r22 if vm >= L12 else 0.0
    return mix(col, RED, myth), 1.0, max(tint, 0.8 * myth)


def tower(c, T):
    t_land = lambda i: -1.0 + i * 0.12
    bands = [0, DED, L10, L12, 1e9]
    rows = []
    for i in range(NROWS0):
        rows.append((i * ROW, (i + 1) * ROW, t_land(i), False))
    rows.append((PAY0, PAY0 + 4000, T_RAISE + 0.15, True))
    rows.append((PAY0 + 4000, PAY1, T_RAISE + 0.45, True))
    top = None
    for (v0, v1, tl, rz) in rows:
        if v1 > PAY0 and not rz:
            v1 = PAY0
        dt = T - tl
        if dt < -0.35:
            continue
        drop = 0 if dt >= 0 else (-dt / 0.35) ** 2 * 520
        bounce = 0 if dt < 0 else 6 * math.sin(dt * 30) * math.exp(-dt * 12)
        oy = -drop + bounce
        a = 1.0 if dt >= 0 else e(dt, -0.35, -0.2)
        y0, y1 = Y(v1) + oy, Y(v0) + oy
        jx = ((int(v0 // ROW) * 37) % 13 - 6) * 0.8
        for j in range(len(bands) - 1):
            lo, hi = max(v0, bands[j]), min(v1, bands[j + 1])
            if hi <= lo:
                continue
            col, al, tint = band_col(lo, hi, T)
            c.save()
            c.rectangle(0, Y(hi) + oy - (6 if hi == v1 else 0), VW, (hi - lo) * S + (6 if hi == v1 else 0) + (1 if lo == v0 else 0))
            c.clip()
            bundle(c, TX + jx, y0 + 1, TW, y1 - y0 - 2, col, a * al, tint, outline=GOLD if rz and T < T_MYTH else None)
            c.restore()
        top = (v1, oy, a, jx)
    if top:
        v1, oy, a, jx = top
        col, al, tint = band_col(v1 - 1, v1, T)
        y = Y(v1) + oy
        c.save()
        c.translate(TX + jx, y)
        c.move_to(0, 0)
        c.line_to(TW, 0)
        c.line_to(TW - 26, -30)
        c.line_to(26, -30)
        c.close_path()
        c.set_source_rgba(*mix((0.90, 0.94, 0.86), (0.98, 0.70, 0.66), tint), a)
        c.fill_preserve()
        c.set_source_rgba(*BILL_D, a)
        c.set_line_width(2)
        c.stroke()
        c.save()
        c.translate(TW / 2, -15)
        c.scale(1, 0.28)
        c.arc(0, 0, 44, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(*BILL_D, 0.8 * a)
        c.set_line_width(3)
        c.stroke()
        c.move_to(TW / 2 - 46, -30)
        c.line_to(TW / 2 + 46, -30)
        c.line_to(TW / 2 + 46, 0)
        c.line_to(TW / 2 - 46, 0)
        c.close_path()
        c.set_source_rgba(*col, a)
        c.fill()
        c.restore()


def line_mark(c, v, T, t0, label, col):
    a = e(T, t0, t0 + 0.4)
    if a <= 0:
        return
    y = Y(v)
    c.set_source_rgba(*WHITE, 0.9 * a)
    c.set_line_width(5)
    c.set_dash([18, 10])
    c.move_to(TX - 60, y)
    c.line_to(TX + TW + 30, y)
    c.stroke()
    c.set_dash([])
    w = tw(c, label, 30, H) + 24
    rrect(c, TX - 64, y - 22, w, 44, 12)
    c.set_source_rgba(*INK, 0.92 * a)
    c.fill()
    txt(c, label, TX - 64 + w / 2, y + 11, 30, col, H, a=a)


def label(c, y, l1, l2, col, a, k=1.0, fg=WHITE):
    if a <= 0.01:
        return
    c.save()
    c.translate(LX + 195, y)
    s = 0.85 + 0.15 * k
    c.scale(s, s)
    w = 390
    rrect(c, -w / 2 + 5, -58 + 6, w, 116, 18)
    c.set_source_rgba(0, 0, 0, 0.3 * a)
    c.fill()
    rrect(c, -w / 2, -58, w, 116, 18)
    c.set_source_rgba(*col, 0.97 * a)
    c.fill()
    sz = 48
    while tw(c, l1, sz, H) > w - 30:
        sz -= 2
    txt(c, l1, 0, -8, sz, fg, H, a=a)
    sz2 = 50
    while tw(c, l2, sz2, H) > w - 30:
        sz2 -= 2
    txt(c, l2, 0, 45, sz2, fg, H, a=a)
    c.restore()


def board(c, T):
    a = e(T, T_10 - 0.2, T_10 + 0.2) * (1 - e(T, T_PAY - 0.3, T_PAY))
    ta = (1 - e(T, T_10 - 0.4, T_10 - 0.1))
    if ta > 0.01:
        rrect(c, LX, 305, 395, 96, 48)
        c.set_source_rgba(*INK, 0.95 * ta)
        c.fill()
        txt(c, "MYTH vs MATH", LX + 197, 350, 40, GOLD, H, a=ta)
        txt(c, "EPISODE 1", LX + 197, 388, 30, WHITE, H, a=ta)
    if a <= 0.01:
        return
    if T < T_12:
        v = TAX0 * 0 + 1280 * e(T, T_10 + 0.3, T_10 + 1.0)
    elif T < T_MYTH:
        v = 1280 + 4632 * e(T, T_12 + 0.3, T_12 + 1.2)
    elif T < T_WRONG + 0.3:
        v = TAX0 + (MYTHTAX - TAX0) * e(T, T_MYTH + 0.2, T_MYTH + 0.8)
    elif T < T_MATH:
        v = MYTHTAX + (TAX0 - MYTHTAX) * e(T, T_WRONG + 0.3, T_MATH)
    else:
        v = TAX0 + (TAX1 - TAX0) * e(T, T_MATH + 0.8, T_MATH + 2.2)
    myth = T_MYTH + 0.2 <= T < T_MATH
    rrect(c, LX, 305, 395, 110, 22)
    c.set_source_rgba(*INK, 0.96 * a)
    c.fill_preserve()
    c.set_source_rgba(*(RED if myth else GOLD), a)
    c.set_line_width(5)
    c.stroke()
    txt(c, "FEDERAL TAX", LX + 197, 342, 26, GOLD, H, a=a)
    s = money(v, True) + ("?!" if myth else "")
    sz = 52
    while tw(c, s, sz, H) > 360:
        sz -= 2
    txt(c, s, LX + 197, 398, sz, (1, 0.6, 0.55) if myth else WHITE, H, a=a)


CARDS = [
    (0.0, ("CAN A RAISE", "SHRINK YOUR PAY?")),
    (T_DED, ("FIRST $16,600 IS", "TAX-FREE")),
    (T_10 + 0.2, ("EACH SLICE GETS", "ITS OWN RATE")),
    (T_RAISE, ("NOW A $5,000 RAISE", "CROSSES THE 22% LINE")),
    (T_MYTH, ("MYTH: NOW ALL OF IT", "IS TAXED AT 22%")),
    (T_MATH, ("MATH: ONLY THE TOP", "$4,375 PAYS 22%")),
    (T_PAY, ("A BRACKET NEVER TAKES", "THE WHOLE RAISE")),
    (T_LAD, ("THE LINES MOVED UP", "FOR 2027")),
]


def card(c, T, custom=None, a=1.0):
    lines, ts = CARDS[0][1], 0
    for (t0, ln) in CARDS:
        if T >= t0:
            lines, ts = ln, t0
    if custom:
        lines, ts = custom, -9
    myth = lines[0].startswith("MYTH")
    s = 0.9 + 0.1 * back(e(T - ts, 0, 0.3))
    c.save()
    c.translate(540, 1222)
    c.scale(s, s)
    rrect(c, -446, -88, 900, 186, 30)
    c.set_source_rgba(0, 0, 0, 0.35 * a)
    c.fill()
    rrect(c, -450, -95, 900, 186, 30)
    c.set_source_rgba(1, 1, 1, a)
    c.fill()
    c.save()
    rrect(c, -450, -95, 900, 186, 30)
    c.clip()
    c.rectangle(-450, -95, 22, 186)
    c.set_source_rgba(*(RED if myth else YEL), a)
    c.fill()
    c.restore()
    sz = 60
    while tw(c, lines[0], sz, H) > 830:
        sz -= 2
    txt(c, lines[0], 0, -14, sz, INK, H, a=a)
    sz2 = 68
    while tw(c, lines[1], sz2, H) > 830:
        sz2 -= 2
    txt(c, lines[1], 0, 62, sz2, RED if myth else (0.10, 0.30, 0.70), H, a=a)
    c.restore()


def stamp(c, x, y, s, col, t, rot=-0.18, w=520, h=150, sz=96):
    k = back(e(t, 0, 0.25))
    if k <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    sc = 1.6 - 0.6 * k
    c.scale(sc, sc)
    a = min(1, k * 1.5)
    rrect(c, -w / 2, -h / 2, w, h, 18)
    c.set_source_rgba(1, 1, 1, 0.92 * a)
    c.fill_preserve()
    c.set_source_rgba(*col, a)
    c.set_line_width(12)
    c.stroke()
    txt(c, s, 0, sz * 0.36, sz, col, H, a=a)
    c.restore()


def wordmark(c, a=1.0):
    logo(c, 380, 140, 0.55, a)
    txt(c, "MONEY MAP", 560, 175, 40, WHITE, H, a=a, stroke=INK, sw=8)


def scene(c, T):
    tower(c, T)
    labs = [
        (Y(DED / 2), "TAX-FREE", "$16,600", (0.30, 0.34, 0.36), e(T, T_DED + 0.3, T_DED + 0.7)),
        (Y((DED + L10) / 2) - 10, "10% ON $12,800", "= $1,280", YEL, e(T, T_10 + 0.3, T_10 + 0.7)),
    ]
    if T < T_MATH + 0.6:
        labs.append((650, "12% ON $38,600", "= $4,632", BLU, e(T, T_12 + 0.4, T_12 + 0.8)))
    else:
        labs.append((650, "12% ON $39,225", "= $4,707", BLU, 1.0))
    for (y, l1, l2, col, a) in labs:
        label(c, y, l1, l2, col, a * (1 - 0.75 * e(T, T_MYTH + 0.2, T_MYTH + 0.5) * (1 - e(T, T_WRONG, T_WRONG + 0.4))), back(a), fg=INK if col == YEL else WHITE)
    ma = e(T, T_MATH + 0.5, T_MATH + 0.9)
    label(c, 482, "22% ON $4,375", "= $962.50", RED, ma, back(ma))
    if ma > 0:
        c.set_source_rgba(*RED, ma)
        c.set_line_width(6)
        c.move_to(TX + TW + 8, Y((L12 + PAY1) / 2))
        c.line_to(LX - 4, 482)
        c.stroke()
    line_mark(c, L10, T, T_10 + 0.1, "10% | 12%", YEL)
    line_mark(c, L12, T, T_RAISE - 0.4, "22% LINE", (1, 0.55, 0.50))
    if T_RAISE <= T < T_MYTH:
        a = e(T, T_RAISE + 0.5, T_RAISE + 0.8)
        y = Y(PAY1) - 70
        rrect(c, TX + 40, y - 40, TW - 80, 74, 37)
        c.set_source_rgba(*GOLD, a)
        c.fill()
        txt(c, "+$5,000 RAISE", TX + TW / 2, y + 14, 42, INK, H, a=a)
    if T_MYTH + 0.3 <= T < T_MATH:
        stamp(c, TX + TW / 2, Y(PAY1 / 1.6), "MYTH", RED, T - T_MYTH - 0.3, w=380, h=140)
    if T_WRONG <= T < T_MATH + 0.4:
        a = e(T, T_WRONG, T_WRONG + 0.25) * (1 - e(T, T_MATH, T_MATH + 0.4))
        c.set_source_rgba(*RED, a)
        c.set_line_width(22)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        y = Y(PAY1 / 1.6)
        c.move_to(TX + TW / 2 - 230, y + 70)
        c.line_to(TX + TW / 2 + 230, y - 70)
        c.stroke()
    ring(c, 540, Y(PAY1), T - T_MATH, 60, 300, 0.6, 10, RED)


def panel_pay(c, t):
    txt(c, "THE MATH", 540, 385, 82, GOLD, H, stroke=INK, sw=14, a=e(t, 0, 0.3))
    txt(c, "FEDERAL INCOME TAX ONLY", 540, 445, 40, WHITE, H, a=e(t, 0.1, 0.4))
    txt(c, "SINGLE FILER, 2027, EXAMPLE", 540, 492, 40, WHITE, H, a=e(t, 0.15, 0.45))
    rows = [("RAISE", "+$5,000.00", WHITE, (0.20, 0.24, 0.32), 0.3),
            ("EXTRA TAX", "-$1,037.50", WHITE, RED, 0.9),
            ("YOU KEEP", "+$3,962.50", INK, YEL, 1.6)]
    for i, (l, v, fg, bgc, t0) in enumerate(rows):
        k = back(e(t, t0, t0 + 0.35))
        if k <= 0.01:
            continue
        y = 520 + i * 150
        big = i == 2
        c.save()
        c.translate(540, y + 65)
        c.scale(k, k)
        rrect(c, -420 + 6, -65 + 8, 840, 130 + (20 if big else 0), 24)
        c.set_source_rgba(0, 0, 0, 0.35)
        c.fill()
        rrect(c, -420, -65, 840, 130 + (20 if big else 0), 24)
        c.set_source_rgb(*bgc)
        c.fill()
        txt(c, l, -385, 22 + (10 if big else 0), 50, fg, H, align="l")
        txt(c, v, 385, 24 + (10 if big else 0), 66 if big else 58, fg, H, align="r")
        c.restore()
    if t > 2.3:
        stamp(c, 540, 1045, "MYTH BUSTED", GRN, t - 2.3, rot=-0.06, w=660, h=110, sz=72)


def panel_lad(c, t):
    txt(c, "2027 TAX LINES", 540, 395, 80, GOLD, H, stroke=INK, sw=14, a=e(t, 0, 0.3))
    txt(c, "SINGLE FILER", 540, 455, 44, WHITE, H, a=e(t, 0.1, 0.4))
    rows = [("22%", "UP TO $109,125", RED, 1.5), ("12%", "UP TO $52,025", BLU, 1.0), ("10%", "UP TO $12,800", YEL, 0.5)]
    for i, (r, l, col, t0) in enumerate(rows):
        k = e(t, t0, t0 + 0.4)
        if k <= 0:
            continue
        y = 520 + i * 125
        x0 = 120 - 400 * (1 - k)
        fg = INK if col == YEL else WHITE
        brick(c, x0, y, 840, 100, col, studs=(i == 0))
        txt(c, r, x0 + 40, y + 70, 64, fg, H, align="l")
        txt(c, l, x0 + 810, y + 68, 52, fg, H, align="r")
    k = back(e(t, 2.2, 2.6))
    if k > 0.01:
        c.save()
        c.translate(540, 985)
        c.scale(k, k)
        brick(c, -420, -55, 840, 110, (0.92, 0.94, 0.96))
        txt(c, "TAX-FREE FIRST $16,600", 0, 20, 52, INK, H)
        c.restore()
    txt(c, "ALL UP ABOUT 3% ON 2026", 540, 1095, 48, YEL, H, a=e(t, 3.0, 3.4), stroke=INK, sw=8)


def endcard(c, t):
    a = e(t, 0.2, 0.7)
    logo(c, 540 - 96, 400, 3.2, a)
    txt(c, "MONEY MAP", 540, 780, 100, WHITE, H, a=a, stroke=INK, sw=16)
    txt(c, "FOLLOW THE MONEY.", 540, 868, 52, GOLD, H, a=e(t, 0.5, 1.0), stroke=INK, sw=10)
    b = e(t, 1.0, 1.5)
    brick(c, 150, 950, 780, 120, YEL, a=b, studs=True)
    txt(c, "FOLLOW FOR MORE", 540, 1030, 58, INK, H, a=b)
    n = e(t, 1.6, 2.1)
    txt(c, "MYTH vs MATH", 540, 1170, 56, WHITE, H, a=n, stroke=INK, sw=10)
    txt(c, "NEXT MYTH SOON", 540, 1240, 48, GOLD, H, a=n, stroke=INK, sw=10)


def draw(c, T):
    T = T % DUR
    bg(c)
    if T < T_END:
        fade_end = e(T, T_END - 0.4, T_END)
        scene(c, T)
        wordmark(c)
        dim = 0.82 * e(T, T_PAY - 0.05, T_PAY + 0.3)
        if dim > 0:
            c.set_source_rgba(0.03, 0.04, 0.09, dim)
            c.rectangle(0, 0, VW, VH)
            c.fill()
        board(c, T)
        if T_PAY <= T < T_LAD:
            panel_pay(c, T - T_PAY)
        elif T >= T_LAD:
            panel_lad(c, T - T_LAD)
        card(c, T)
        if fade_end > 0:
            c.set_source_surface(_BG, 0, 0)
            c.paint_with_alpha(fade_end)
    else:
        t = T - T_END
        out = e(T, DUR - 0.45, DUR - 0.05)
        c.save()
        endcard(c, t)
        c.restore()
        if out > 0:
            c.set_source_surface(_BG, 0, 0)
            c.paint_with_alpha(out)
    if T < 0.35:
        ring(c, 365, BASE, T, 60, 360, 0.6, 12)


def cover_draw(c, T=0):
    bg(c)
    TT = T_RAISE + 1.0
    tower(c, TT)
    line_mark(c, L12, TT, 0, "22% LINE", (1, 0.55, 0.50))
    wordmark(c)
    y = Y(PAY1) - 70
    rrect(c, TX + 40, y - 40, TW - 80, 74, 37)
    c.set_source_rgb(*GOLD)
    c.fill()
    txt(c, "+$5,000 RAISE", TX + TW / 2, y + 14, 42, INK, H)
    rrect(c, LX, 420, 395, 300, 28)
    c.set_source_rgba(*INK, 0.96)
    c.fill_preserve()
    c.set_source_rgb(*RED)
    c.set_line_width(6)
    c.stroke()
    txt(c, "YOUR TAX", LX + 197, 490, 48, GOLD, H)
    txt(c, "$?,???", LX + 197, 590, 86, WHITE, H)
    txt(c, "MYTH vs MATH", LX + 197, 680, 36, (1, 0.6, 0.55), H)
    card(c, 0, custom=("A RAISE THAT", "LOWERS YOUR PAY?"))


def music(path="tax_music.wav"):
    tr = Track(DUR, 31)
    rng = tr.rng
    bar = 4 * BEAT
    chords = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]
    roots = [36, 33, 29, 31]
    mel = [[(0, 76), (1, 79), (1.5, 81), (2.5, 79), (3, 76)], [(0, 72), (1, 76), (2, 74), (3, 72)],
           [(0, 69), (0.5, 72), (1.5, 77), (2.5, 76), (3, 74)], [(0, 74), (1, 79), (2, 83), (3, 81)]]
    clap = noise_hit(rng, 0.09, 1100, 3600, 0.025, 0.5)
    hat = noise_hit(rng, 0.05, 7000, None, 0.012, 0.10)
    for b in range(16):
        i = b % 4
        t0 = b * bar
        if 9 <= b <= 10:
            for q in range(4):
                tr.put(pluck(chords[i][q] - 12, 0.6, bright=0.8), t0 + q * BEAT)
            tr.put(pad([m - 12 for m in chords[i]], bar, 0.06), t0)
            tr.put(bassn(roots[i] - 1, 3 * BEAT, 0.22), t0)
            continue
        for q in range(8):
            tr.put(pluck(chords[i][[0, 2, 1, 3, 2, 1, 3, 2][q]], 1.0 if q % 2 == 0 else 0.65), t0 + q * 0.5 * BEAT)
            tr.put(hat, t0 + q * 0.5 * BEAT, 1.0 if q % 2 else 0.6)
        tr.put(bassn(roots[i], 1.2 * BEAT), t0)
        tr.put(bassn(roots[i] + 7, 0.8 * BEAT, 0.22), t0 + 1.5 * BEAT)
        tr.put(bassn(roots[i], 1.2 * BEAT), t0 + 2 * BEAT)
        if b >= 1:
            tr.put(kick(), t0)
            tr.put(kick(0.45), t0 + 2.5 * BEAT)
            tr.put(clap, t0 + BEAT)
            tr.put(clap, t0 + 3 * BEAT)
        if b >= 2 and b not in (13,):
            for tb, m in mel[i]:
                tr.put(marimba(m, 0.9), t0 + tb * BEAT)
    for i in range(NROWS0):
        tr.put(clack(rng, 0.35), -1.0 + i * 0.12)
    tr.put(kick(0.9), 0.0)
    tr.put(bell(1568, 0.5, 0.10), 0.0)
    for tp in (T_DED, T_10, T_12, T_PAY, T_LAD, T_END):
        tr.put(whoosh(rng, 0.5, 0.18), tp - 0.15)
    tr.put(clack(rng, 0.6), T_RAISE + 0.15)
    tr.put(clack(rng, 0.6), T_RAISE + 0.45)
    tr.put(bell(1046.5, 0.8, 0.12), T_RAISE + 0.5)
    x = np.arange(int(0.6 * SR)) / SR
    buzz = np.sign(np.sin(2 * np.pi * 110 * x)) * np.exp(-x * 4) * 0.12
    tr.put(buzz, T_MYTH + 0.3)
    tr.put(kick(1.0), T_MYTH + 0.3)
    tr.put(noise_hit(rng, 0.3, 200, 2000, 0.08, 0.4), T_WRONG)
    tr.put(riser(rng, 1.5, 0.18), T_MATH - 1.5)
    for f in (784.0, 987.8, 1174.7, 1568.0):
        tr.put(bell(f, 1.4, 0.09), T_MATH + 0.5)
    for k, t0 in enumerate((0.3, 0.9, 1.6)):
        tr.put(bell(1318.5 + 200 * k, 0.5, 0.10), T_PAY + t0)
    tr.put(kick(1.1), T_PAY + 2.3)
    tr.put(bell(2093, 0.8, 0.10), T_PAY + 2.35)
    for k in range(3):
        tr.put(clack(rng, 0.45), T_LAD + 0.5 + 0.5 * k)
    tr.put(bell(2093, 0.6, 0.09), T_END + 1.0)
    tr.save(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        for i, T in enumerate([float(x) for x in sys.argv[2:]]):
            still(draw, T, "a_%02d.png" % i)
    elif cmd == "cover":
        still(cover_draw, 0, sys.argv[2])
    elif cmd == "render":
        music()
        render(draw, DUR, sys.argv[2], "tax_music.wav", "tax")
