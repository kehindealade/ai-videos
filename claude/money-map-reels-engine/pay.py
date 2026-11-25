import sys, math, cairo
from common import *

H = "Fira Sans Black"
B = "Fira Sans"
BEAT = 60 / 112
DUR = 72 * BEAT
BG = (0.96, 0.95, 0.98)
INK = (0.11, 0.09, 0.20)
SUB = (0.38, 0.36, 0.48)
VIO = (0.42, 0.25, 0.90)
MINT = (0.10, 0.66, 0.52)
PINK = (0.93, 0.27, 0.48)
AMB = (0.96, 0.62, 0.10)
RED = (0.85, 0.12, 0.18)
T_CART, T_JAN, T_LATE, T_SURV, T_END = 2.8, 11.6, 17.6, 22.0, 31.0
GIFTS = [("HEADPHONES", 120, VIO, 0, "headphones"), ("WINTER JACKET", 200, PINK, 8, "jacket"), ("VIDEO GAME", 80, AMB, 18, "game")]
DAY0 = 0
DLAB = {0: "NOV 27", 34: "DEC 31"}
PAYS = []
for gi, (n, p, col, d0, ic) in enumerate(GIFTS):
    for k in range(4):
        PAYS.append((d0 + 14 * k, p / 4, gi))
JAN0 = 35
JAN = sorted([(d, v, gi) for (d, v, gi) in PAYS if d >= JAN0])
assert abs(sum(v for d, v, gi in JAN) - 170) < 1e-6 and len(JAN) == 5


def jan_date(d):
    return "JAN %d" % (d - 34)


def gift_t(i):
    return T_CART + 0.4 + i * 2.2


def bg(c, T):
    c.set_source_rgb(*BG)
    c.paint()
    g = cairo.RadialGradient(200, 300, 50, 200, 300, 900)
    g.add_color_stop_rgba(0, *VIO, 0.10)
    g.add_color_stop_rgba(1, *VIO, 0)
    c.set_source(g)
    c.paint()
    g = cairo.RadialGradient(950, 1500, 50, 950, 1500, 900)
    g.add_color_stop_rgba(0, *MINT, 0.10)
    g.add_color_stop_rgba(1, *MINT, 0)
    c.set_source(g)
    c.paint()
    txt(c, "9:41", 90, 72, 40, INK, B, align="l")
    for k in range(4):
        c.rectangle(860 + k * 16, 72 - 10 - k * 7, 10, 10 + k * 7)
        c.set_source_rgba(*INK, 1)
        c.fill()
    rrect(c, 935, 44, 60, 30, 8)
    c.set_source_rgba(*INK, 1)
    c.set_line_width(3)
    c.stroke()
    rrect(c, 940, 49, 34, 20, 4)
    c.fill()
    rrect(c, 390, 30, 300, 56, 28)
    c.set_source_rgb(0.05, 0.05, 0.08)
    c.fill()
    logo(c, 395, 150, 0.5, 1)
    txt(c, "MONEY MAP", 565, 182, 40, INK, H)
    rrect(c, 420, 1850, 240, 12, 6)
    c.set_source_rgba(*INK, 0.8)
    c.fill()


def shadowcard(c, x, y, w, h, r=26, col=(1, 1, 1), a=1.0, sh=0.12):
    rrect(c, x, y + 10, w, h, r)
    c.set_source_rgba(0.2, 0.15, 0.4, sh * a)
    c.fill()
    rrect(c, x, y, w, h, r)
    c.set_source_rgba(*col, a)
    c.fill()


def icon(c, name, x, y, col, a=1.0):
    c.save()
    c.translate(x, y)
    c.arc(0, 0, 44, 0, 2 * math.pi)
    c.set_source_rgba(*mix(col, (1, 1, 1), 0.8), a)
    c.fill()
    c.set_source_rgba(*col, a)
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if name == "headphones":
        c.arc(0, 4, 22, math.pi, 2 * math.pi)
        c.stroke()
        rrect(c, -28, 2, 14, 22, 5)
        c.fill()
        rrect(c, 14, 2, 14, 22, 5)
        c.fill()
    elif name == "jacket":
        c.move_to(-12, -22)
        c.line_to(-26, -14)
        c.line_to(-26, 24)
        c.line_to(26, 24)
        c.line_to(26, -14)
        c.line_to(12, -22)
        c.line_to(0, -10)
        c.close_path()
        c.fill()
        c.set_source_rgba(1, 1, 1, a)
        c.set_line_width(3)
        c.move_to(0, -8)
        c.line_to(0, 22)
        c.stroke()
    else:
        rrect(c, -28, -14, 56, 30, 14)
        c.fill()
        c.set_source_rgba(1, 1, 1, a)
        c.set_line_width(4)
        c.move_to(-16, 1)
        c.line_to(-6, 1)
        c.move_to(-11, -4)
        c.line_to(-11, 6)
        c.stroke()
        c.arc(12, -2, 3.5, 0, 2 * math.pi)
        c.arc(18, 5, 3.5, 0, 2 * math.pi)
        c.fill()
    c.restore()


def header(c, T):
    if T < T_JAN:
        a = (1 - e(T, T_JAN - 0.3, T_JAN)) * e(T, T_CART - 0.1, T_CART + 0.3)
        txt(c, "HOLIDAY CART", 100, 360, 60, INK, H, align="l", a=a)
        rrect(c, 760, 312, 220, 64, 32)
        c.set_source_rgba(*AMB, a)
        c.fill()
        txt(c, "EXAMPLE", 870, 357, 38, INK, H, a=a)
    elif T < T_SURV:
        a = e(T, T_JAN, T_JAN + 0.3) * (1 - e(T, T_SURV - 0.3, T_SURV))
        v = sum(val * e(T, T_JAN + 0.8 + i * 0.55, T_JAN + 1.1 + i * 0.55) for i, (d, val, gi) in enumerate(JAN))
        txt(c, "DUE IN JANUARY", 100, 345, 44, SUB, H, align="l", a=a)
        late = T >= T_LATE + 0.6
        txt(c, "$%d" % round(v), 980, 372, 92, RED if late else VIO, H, align="r", a=a)


def cart(c, T):
    a = 1 - e(T, T_JAN - 0.4, T_JAN)
    if a <= 0.01:
        return
    for i, (n, p, col, d0, ic) in enumerate(GIFTS):
        t0 = gift_t(i) if T >= 0.3 else -9
        k = back(e(T, t0, t0 + 0.35)) if T >= T_CART else 0
        if k <= 0.01:
            continue
        y = 410 + i * 128
        c.save()
        c.translate(540, y + 55)
        c.scale(k, k)
        c.translate(-540, -(y + 55))
        shadowcard(c, 90, y, 900, 110, 24, a=a)
        icon(c, ic, 155, y + 55, col, a)
        txt(c, n, 220, y + 52, 42, INK, H, align="l", a=a)
        txt(c, "$%d" % p, 220, y + 94, 36, SUB, B, align="l", a=a)
        pk = e(T, t0 + 0.6, t0 + 0.9)
        s = "4 x $%d" % (p // 4)
        w = tw(c, s, 40, H) + 50
        rrect(c, 960 - w, y + 28, w, 56, 28)
        c.set_source_rgba(*mix((0.9, 0.9, 0.92), col, pk), a)
        c.fill()
        txt(c, s, 960 - w / 2, y + 70, 40, (1, 1, 1) if pk > 0.5 else SUB, H, a=a)
        c.restore()
    timeline(c, T, a)


def tx(d):
    return 130 + d * (820 / 61.0)


def timeline(c, T, a):
    y = 900
    ka = e(T, T_CART + 0.2, T_CART + 0.6) * a
    if ka <= 0.01:
        return
    shadowcard(c, 90, 800, 900, 270, 24, a=ka)
    txt(c, "PAYMENT DATES", 130, 860, 38, INK, H, align="l", a=ka)
    jz = e(T, T_JAN - 2.2, T_JAN - 1.6)
    if jz > 0:
        rrect(c, tx(JAN0) - 14, 880, tx(61) - tx(JAN0) + 28, 150, 16)
        c.set_source_rgba(*RED, 0.10 * jz * ka)
        c.fill()
        txt(c, "JANUARY", (tx(JAN0) + tx(61)) / 2, 860, 38, RED, H, a=jz * ka)
    c.set_source_rgba(*INK, 0.25 * ka)
    c.set_line_width(4)
    c.move_to(tx(0), y + 60)
    c.line_to(tx(61), y + 60)
    c.stroke()
    for d, lab in ((0, "NOV 27"), (35, "JAN 1"), (60, "JAN 26")):
        c.move_to(tx(d), y + 48)
        c.line_to(tx(d), y + 72)
        c.stroke()
        txt(c, lab, tx(d), y + 116, 32, SUB, H, a=ka)
    stack = {}
    for (d, v, gi) in sorted(PAYS):
        t0 = gift_t(gi) + 0.7 + (d - GIFTS[gi][3]) / 14 * 0.18
        k = back(e(T, t0, t0 + 0.25))
        if k <= 0.01:
            continue
        lvl = stack.get(d // 3, 0)
        stack[d // 3] = lvl + 1
        cx, cy = tx(d), y + 60 - 34 - lvl * 40
        c.arc(cx, cy, 17 * k, 0, 2 * math.pi)
        c.set_source_rgba(*GIFTS[gi][2], ka)
        c.fill()


def notifs(c, T):
    if not (T_JAN <= T < T_SURV):
        return
    fa = 1 - e(T, T_SURV - 0.3, T_SURV)
    for i, (d, v, gi) in enumerate(JAN):
        t0 = T_JAN + 0.8 + i * 0.55
        k = e(T, t0, t0 + 0.3)
        if k <= 0:
            continue
        y = 410 + i * 134 - 60 * (1 - back(k))
        late = i == 1 and T >= T_LATE
        c.save()
        if late:
            c.translate(math.sin((T - T_LATE) * 40) * math.exp(-(T - T_LATE) * 6) * 14, 0)
        shadowcard(c, 90, y, 900, 118, 26, a=fa * k, col=(1, 0.93, 0.94) if late else (1, 1, 1))
        if late:
            rrect(c, 90, y, 900, 118, 26)
            c.set_source_rgba(*RED, fa)
            c.set_line_width(5)
            c.stroke()
        rrect(c, 120, y + 24, 70, 70, 18)
        c.set_source_rgba(*(RED if late else GIFTS[gi][2]), fa * k)
        c.fill()
        txt(c, "!" if late else "$", 155, y + 76, 50, (1, 1, 1), H, a=fa * k)
        title = "PAYMENT MISSED" if late else "PAYMENT DUE TODAY"
        txt(c, title, 215, y + 54, 40, RED if late else INK, H, align="l", a=fa * k)
        sub = "LATE FEES CAN APPLY" if late else "%s  ·  %s" % (jan_date(d), GIFTS[gi][0])
        txt(c, sub, 215, y + 96, 34, SUB, B, align="l", a=fa * k, bold=True)
        txt(c, "$%d" % v, 960, y + 76, 54, RED if late else INK, H, align="r", a=fa * k)
        c.restore()


def survey(c, T):
    a = e(T, T_SURV, T_SURV + 0.3) * (1 - e(T, T_END - 0.3, T_END))
    if a <= 0.01:
        return
    t = T - T_SURV
    txt(c, "100 HOLIDAY SHOPPERS", 540, 352, 60, INK, H, a=a)
    shadowcard(c, 90, 390, 900, 700, 30, a=a)
    k1 = e(t, 0.6, 2.0)
    k2 = e(t, 2.8, 3.8)
    for i in range(100):
        gx, gy = i % 10, i // 10
        x, y = 180 + gx * 80, 450 + gy * 52
        col = (0.85, 0.85, 0.89)
        if i < 38 and k1 * 40 > i:
            col = VIO
        if i < 14 and k2 * 16 > i:
            col = RED
        c.arc(x, y - 12, 11, 0, 2 * math.pi)
        c.set_source_rgba(*col, a)
        c.fill()
        c.move_to(x - 17, y + 16)
        c.curve_to(x - 17, y - 3, x + 17, y - 3, x + 17, y + 16)
        c.close_path()
        c.fill()
    ya = e(t, 1.4, 1.8)
    rrect(c, 130, 960, 410, 100, 20)
    c.set_source_rgba(*VIO, a * ya)
    c.fill()
    txt(c, "38 WILL USE IT", 335, 1027, 46, (1, 1, 1), H, a=a * ya)
    yb = e(t, 3.4, 3.8)
    rrect(c, 555, 960, 400, 100, 20)
    c.set_source_rgba(*RED, a * yb)
    c.fill()
    txt(c, "~14 EXPECT TO", 755, 1004, 40, (1, 1, 1), H, a=a * yb)
    txt(c, "PAY LATE", 755, 1048, 40, (1, 1, 1), H, a=a * yb)


CARDS = [
    (0.0, ("4 EASY PAYMENTS.", "THEN JANUARY HITS.")),
    (T_CART + 0.2, ("3 GIFTS, $400.", "EACH ONE SPLIT IN 4")),
    (gift_t(2) + 1.2, ("THE SMALL PAYMENTS", "KEEP STACKING UP")),
    (T_JAN, ("$170 IS STILL DUE", "AFTER THE HOLIDAYS")),
    (T_LATE, ("MISS ONE, AND", "LATE FEES CAN KICK IN")),
    (T_SURV, ("38 IN 100 PLAN TO USE IT.", "ABOUT 14 EXPECT TO PAY LATE")),
    (T_SURV + 5.0, ("47% OF USERS PAID LATE", "IN THE PAST YEAR")),
]


def card(c, T, custom=None):
    lines, ts = CARDS[0][1], 0
    for (t0, ln) in CARDS:
        if T >= t0:
            lines, ts = ln, t0
    if custom:
        lines, ts = custom, -9
    s = 0.92 + 0.08 * back(e(T - ts, 0, 0.3))
    c.save()
    c.translate(540, 1225)
    c.scale(s, s)
    rrect(c, -450, -84, 900, 184, 34)
    c.set_source_rgba(0.2, 0.1, 0.5, 0.25)
    c.fill()
    rrect(c, -450, -94, 900, 184, 34)
    c.set_source_rgb(*INK)
    c.fill()
    sz = 60
    while tw(c, lines[0], sz, H) > 820:
        sz -= 2
    txt(c, lines[0], 0, -14, sz, (1, 1, 1), H)
    sz2 = 62
    while tw(c, lines[1], sz2, H) > 820:
        sz2 -= 2
    txt(c, lines[1], 0, 60, sz2, (0.75, 0.66, 1.0) if "LATE" not in lines[1] and "SLIP" not in lines[1] else (1, 0.55, 0.6), H)
    c.restore()


def hook_notifs(c, T):
    a = 1 - e(T, T_CART - 0.4, T_CART)
    if a <= 0.01:
        return
    items = [("PAYMENT DUE", "$30", VIO), ("PAYMENT DUE", "$50", PINK), ("PAYMENT DUE", "$20", AMB), ("PAYMENT DUE", "$50", PINK), ("PAYMENT DUE", "$30", VIO)]
    for i, (t1, v, col) in enumerate(items):
        t0 = -0.4 + i * 0.42
        k = e(T, t0, t0 + 0.3)
        if k <= 0:
            continue
        y = 420 + i * 130 - 50 * (1 - back(k))
        shadowcard(c, 90 + i * 6, y, 900 - i * 12, 112, 26, a=a * k)
        rrect(c, 120 + i * 6, y + 22, 68, 68, 18)
        c.set_source_rgba(*col, a * k)
        c.fill()
        txt(c, "$", 154 + i * 6, y + 74, 48, (1, 1, 1), H, a=a * k)
        txt(c, t1, 215 + i * 6, y + 70, 42, INK, H, align="l", a=a * k)
        txt(c, v, 960 - i * 6, y + 72, 52, INK, H, align="r", a=a * k)
    txt(c, "JANUARY", 540, 365, 64, RED, H, a=a)


def endcard(c, t):
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.30, 0.17, 0.72)
    g.add_color_stop_rgb(1, 0.12, 0.07, 0.30)
    c.set_source(g)
    c.paint_with_alpha(e(t, 0, 0.35))
    a = e(t, 0.2, 0.7)
    logo(c, 540 - 96, 400, 3.2, a)
    txt(c, "MONEY MAP", 540, 780, 100, (1, 1, 1), H, a=a)
    txt(c, "FOLLOW THE MONEY.", 540, 866, 52, GOLD, H, a=e(t, 0.5, 1.0))
    b = e(t, 1.0, 1.5)
    rrect(c, 150, 950, 780, 120, 60)
    c.set_source_rgba(1, 1, 1, b)
    c.fill()
    txt(c, "FOLLOW FOR MORE", 540, 1032, 58, INK, H, a=b)
    n = e(t, 1.6, 2.1)
    txt(c, "DID YOU SPLIT A GIFT", 540, 1170, 52, (1, 1, 1), H, a=n)
    txt(c, "THIS YEAR?", 540, 1236, 52, GOLD, H, a=n)


def draw(c, T):
    T = T % DUR
    bg(c, T)
    if T >= T_END:
        endcard(c, T - T_END)
        return
    header(c, T)
    hook_notifs(c, T)
    cart(c, T)
    c.save()
    notifs(c, T)
    c.restore()
    survey(c, T)
    card(c, T)
    if T < 0.35:
        ring(c, 540, 500, T, 80, 420, 0.5, 12, VIO)


def cover_draw(c, T=0):
    bg(c, 0)
    txt(c, "JANUARY", 540, 365, 64, RED, H)
    for i, (v, col) in enumerate((("$50", PINK), ("$30", VIO), ("$??", RED))):
        y = 420 + i * 140
        shadowcard(c, 90, y, 900, 118, 26)
        rrect(c, 120, y + 24, 70, 70, 18)
        c.set_source_rgb(*col)
        c.fill()
        txt(c, "!" if i == 2 else "$", 155, y + 76, 50, (1, 1, 1), H)
        txt(c, "PAYMENT MISSED" if i == 2 else "PAYMENT DUE TODAY", 215, y + 72, 42, RED if i == 2 else INK, H, align="l")
        txt(c, v, 960, y + 76, 54, RED if i == 2 else INK, H, align="r")
    txt(c, "HOW MUCH IS", 540, 950, 70, INK, H)
    txt(c, "STILL DUE?", 540, 1030, 70, VIO, H)
    card(c, 0, custom=("THE HOLIDAY BILL", "THAT ARRIVES LATE"))


def music(path="pay_music.wav"):
    tr = Track(DUR, 57)
    rng = tr.rng
    bar = 4 * BEAT
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]
    roots = [45, 41, 36, 43]
    hat = noise_hit(rng, 0.04, 8000, None, 0.008, 0.09)
    clap = noise_hit(rng, 0.12, 1200, 4200, 0.03, 0.4)
    sleigh = noise_hit(rng, 0.08, 6000, 12000, 0.02, 0.07)
    mel = [[(0, 76), (0.5, 79), (1, 81), (2, 79), (3, 76)], [(0, 77), (1, 76), (2, 72), (3, 69)],
           [(0, 72), (0.5, 76), (1.5, 79), (2.5, 83), (3, 81)], [(0, 79), (1, 77), (2, 74), (3.5, 71)]]
    for b in range(18):
        i = b % 4
        t0 = b * bar
        late = 11 <= b <= 12
        for q in range(4):
            tr.put(pluck(chords[i][q] + (0 if not late else -1), 0.7, 1.0, 1.3), t0 + q * BEAT * 0.5 + 0.02 * q)
        tr.put(pad(chords[i], bar, 0.035), t0)
        tr.put(bassn(roots[i], 0.9 * BEAT, 0.32), t0)
        tr.put(bassn(roots[i] + 12, 0.4 * BEAT, 0.2), t0 + 1.5 * BEAT)
        tr.put(bassn(roots[i], 0.9 * BEAT, 0.3), t0 + 2.5 * BEAT)
        if b >= 1:
            for q in range(4):
                tr.put(kick(0.55), t0 + q * BEAT)
            tr.put(clap, t0 + BEAT)
            tr.put(clap, t0 + 3 * BEAT)
            for q in range(8):
                tr.put(sleigh if q % 2 else hat, t0 + q * 0.5 * BEAT)
        if b >= 2 and not late:
            for tb, mm in mel[i]:
                tr.put(bell(mtof(mm), 0.6, 0.05), t0 + tb * BEAT)
    tr.put(kick(1.0), 0)
    for i in range(5):
        tr.put(bell(1760, 0.25, 0.07), -0.4 + i * 0.42 + 0.05)
    for tp in (T_CART, T_JAN, T_SURV, T_END):
        tr.put(whoosh(rng, 0.5, 0.18), tp - 0.15)
    for i in range(3):
        tr.put(bell(1318.5, 0.3, 0.08), gift_t(i))
        for k in range(4):
            tr.put(bell(2093 + 150 * k, 0.15, 0.04), gift_t(i) + 0.7 + k * 0.18)
    for i in range(5):
        tr.put(bell(1568, 0.3, 0.08), T_JAN + 0.8 + i * 0.55)
    x = np.arange(int(0.5 * SR)) / SR
    tr.put(np.sign(np.sin(2 * np.pi * 98 * x)) * np.exp(-x * 5) * 0.12, T_LATE)
    tr.put(kick(1.1), T_LATE)
    for k in range(38):
        tr.put(bell(1700 + (k * 53) % 500, 0.1, 0.025), T_SURV + 0.6 + k * 1.4 / 40)
    tr.put(kick(1.0), T_SURV + 3.4)
    tr.put(bell(659.3, 0.8, 0.08), T_SURV + 3.4)
    tr.put(bell(2093, 0.6, 0.08), T_END + 1.0)
    tr.save(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        for i, T in enumerate([float(x) for x in sys.argv[2:]]):
            still(draw, T, "c_%02d.png" % i)
    elif cmd == "cover":
        still(cover_draw, 0, sys.argv[2])
    elif cmd == "render":
        music()
        render(draw, DUR, sys.argv[2], "pay_music.wav", "pay")
