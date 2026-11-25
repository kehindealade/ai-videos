import sys, math, random, cairo
from common import *

H = "Bitter"
B = "Open Sans"
DUR = 40.0
BEAT = DUR / 64
INK = (0.09, 0.08, 0.14)
LIT = (1.0, 0.82, 0.48)
DARKW = (0.12, 0.14, 0.24)
BURN = (0.95, 0.38, 0.16)
SEV = (0.80, 0.08, 0.16)
TEAL = (0.20, 0.72, 0.66)
CREAMC = (0.99, 0.96, 0.90)
GX0, GY0, GDX, GDY, WW, WH = 112, 392, 86, 68, 58, 48
T_FLAT, T_RACE, T_GRID, T_SEV, T_210, T_GAP, T_END = 3.0, 7.0, 14.0, 17.5, 21.0, 27.0, 33.0
_BG = None
rng0 = random.Random(9)
LITMAP = {}
for gy in range(-6, 22):
    for gx in range(10):
        LITMAP[(gx, gy)] = rng0.random() < 0.72
ORDER = list(range(100))
random.Random(5).shuffle(ORDER)
RANK = {k: i for i, k in enumerate(ORDER)}


def wpos(gx, gy):
    return GX0 + gx * GDX, GY0 + gy * GDY


def bg(c):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, 300)
        g.add_color_stop_rgb(0, 0.16, 0.12, 0.32)
        g.add_color_stop_rgb(1, 0.55, 0.30, 0.42)
        d.set_source(g)
        d.paint()
        g = cairo.LinearGradient(0, 0, VW, 0)
        g.add_color_stop_rgb(0, 0.30, 0.22, 0.24)
        g.add_color_stop_rgb(0.5, 0.40, 0.29, 0.29)
        g.add_color_stop_rgb(1, 0.26, 0.19, 0.22)
        d.set_source(g)
        d.rectangle(0, 230, VW, VH)
        d.fill()
        r = random.Random(3)
        for y in range(230, VH, 17):
            off = 0 if (y // 17) % 2 else 22
            for x in range(-off, VW, 44):
                d.set_source_rgba(0, 0, 0, r.uniform(0.04, 0.12))
                d.rectangle(x, y, 42, 15)
                d.fill()
        d.set_source_rgb(0.20, 0.15, 0.18)
        d.rectangle(0, 222, VW, 22)
        d.fill()
        for gy in range(-3, 22):
            for gx in range(10):
                x, y = wpos(gx, gy)
                if y < 250 or y > VH:
                    continue
                d.set_source_rgb(0.20, 0.15, 0.17)
                d.rectangle(x - 6, y + WH, WW + 12, 8)
                d.fill()
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def window(c, x, y, col, glow=0.0):
    if glow > 0:
        g = cairo.RadialGradient(x + WW / 2, y + WH / 2, 5, x + WW / 2, y + WH / 2, 70)
        g.add_color_stop_rgba(0, *col, 0.35 * glow)
        g.add_color_stop_rgba(1, *col, 0)
        c.set_source(g)
        c.rectangle(x - 50, y - 50, WW + 100, WH + 100)
        c.fill()
    c.rectangle(x, y, WW, WH)
    c.set_source_rgb(*col)
    c.fill()
    c.set_source_rgba(0.16, 0.12, 0.14, 1)
    c.set_line_width(4)
    c.rectangle(x, y, WW, WH)
    c.stroke()
    c.move_to(x + WW / 2, y)
    c.line_to(x + WW / 2, y + WH)
    c.set_line_width(3)
    c.stroke()


def facade(c, T, k_burn=0.0, k_sev=0.0, grid_hi=0.0):
    for gy in range(-3, 22):
        for gx in range(10):
            x, y = wpos(gx, gy)
            if y < 245 or y > VH:
                continue
            ing = 0 <= gy < 10
            idx = gy * 10 + gx if ing else -1
            lit = LITMAP[(gx, gy)]
            flick = 0.5 + 0.5 * math.sin(T * 0.7 + gx * 1.7 + gy * 2.3)
            col = mix(DARKW, LIT, 0.92 if lit else 0.08 + 0.05 * flick)
            glow = 0.6 if lit else 0
            if ing and grid_hi > 0:
                col = mix(col, LIT, grid_hi)
                glow = max(glow, 0.4 * grid_hi)
                r = RANK[idx]
                if r < 49:
                    kb = clamp((k_burn * 60 - r) / 6)
                    col = mix(col, BURN, kb)
                    glow = max(glow, kb)
                if r < 26:
                    ks = clamp((k_sev * 40 - r) / 6)
                    col = mix(col, SEV, ks)
            elif grid_hi > 0:
                col = mix(col, DARKW, 0.7 * grid_hi)
                glow *= 1 - grid_hi
            window(c, x, y, col, glow)


def dimmer(c, a):
    if a > 0:
        c.set_source_rgba(0.05, 0.04, 0.09, a)
        c.rectangle(0, 0, VW, VH)
        c.fill()


def panel(c, x, y, w, h, a=1.0):
    rrect(c, x + 6, y + 10, w, h, 28)
    c.set_source_rgba(0, 0, 0, 0.35 * a)
    c.fill()
    rrect(c, x, y, w, h, 28)
    c.set_source_rgba(*CREAMC, 0.97 * a)
    c.fill()


CARDS = [
    (0.0, ("RENTS WENT FLAT.", "SO WHY DOES IT HURT?")),
    (T_FLAT, ("NEW-LEASE RENTS BARELY", "MOVED SINCE MID-2023")),
    (T_RACE + 0.3, ("THE PROBLEM IS", "THE LAST 23 YEARS")),
    (T_RACE + 3.6, ("RENT ROSE 3X FASTER", "THAN RENTERS' PAY")),
    (T_GRID, ("OUT OF 100 RENTERS", "49 PAY OVER 30%")),
    (T_SEV, ("AND 26 OF THEM", "PAY OVER HALF")),
    (T_210, ("EARN UNDER $30,000?", "THIS IS WHAT'S LEFT")),
    (T_GAP, ("FLAT RENT ISN'T", "CHEAP RENT")),
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
    rrect(c, -444, -86, 900, 184, 18)
    c.set_source_rgba(0, 0, 0, 0.4)
    c.fill()
    rrect(c, -450, -94, 900, 184, 18)
    c.set_source_rgb(*INK)
    c.fill()
    rrect(c, -450, -94, 900, 184, 18)
    c.set_source_rgb(*LIT)
    c.set_line_width(5)
    c.stroke()
    sz = 58
    while tw(c, lines[0], sz, H) > 820:
        sz -= 2
    txt(c, lines[0], 0, -16, sz, CREAMC, H)
    sz2 = 64
    while tw(c, lines[1], sz2, H) > 820:
        sz2 -= 2
    txt(c, lines[1], 0, 60, sz2, LIT, H)
    c.restore()


def sign(c, T):
    a = 1 - e(T, T_FLAT - 0.3, T_FLAT)
    if a <= 0.01:
        return
    k = 1.0 + 0.04 * math.sin(T * 3)
    c.save()
    c.translate(540, 455)
    c.rotate(-0.04 + 0.02 * math.sin(T * 2.2))
    c.scale(k, k)
    c.set_source_rgba(0.15, 0.12, 0.12, a)
    c.set_line_width(5)
    c.move_to(-200, -150)
    c.line_to(-160, -70)
    c.move_to(200, -150)
    c.line_to(160, -70)
    c.stroke()
    rrect(c, -300, -70, 600, 170, 16)
    c.set_source_rgba(*SEV, a)
    c.fill()
    rrect(c, -288, -58, 576, 146, 12)
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(4)
    c.stroke()
    txt(c, "FOR RENT", 0, 30, 96, (1, 1, 1), H, a=a)
    c.restore()


def scene_flat(c, t):
    panel(c, 110, 340, 860, 700)
    txt(c, "RENT GROWTH, NEW LEASES", 540, 420, 46, INK, H)
    txt(c, "U.S., MID-2023 TO 2025", 540, 475, 40, (0.35, 0.33, 0.40), B)
    x0, x1, yb = 190, 890, 860
    c.set_source_rgba(*INK, 0.25)
    c.set_line_width(3)
    for k in range(4):
        y = 560 + k * 100
        c.move_to(x0, y)
        c.line_to(x1, y)
        c.stroke()
    p = e(t, 0.3, 2.0)
    c.set_source_rgb(*SEV)
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x0, 760)
    n = 60
    for i in range(1, int(n * p) + 1):
        x = x0 + (x1 - x0) * i / n
        c.line_to(x, 760 + 8 * math.sin(i * 0.7) * math.exp(-i * 0.02))
    c.stroke()
    k = back(e(t, 1.6, 2.0))
    if k > 0.01:
        c.save()
        c.translate(540, 950)
        c.scale(k, k)
        rrect(c, -230, -60, 460, 120, 60)
        c.set_source_rgb(*SEV)
        c.fill()
        txt(c, "ABOUT 0%", 0, 24, 66, (1, 1, 1), H)
        c.restore()


def scene_race(c, t):
    panel(c, 110, 340, 860, 720)
    txt(c, "2001 TO 2024", 540, 420, 52, INK, H)
    txt(c, "AFTER INFLATION", 540, 474, 40, (0.35, 0.33, 0.40), B)
    base = 960
    u = 9.0
    for (cx, lab, pct, col, l2) in ((360, "MEDIAN RENT", 30, SEV, "+30%"), (720, "RENTER INCOME", 9, TEAL, "+9%")):
        g = e(t, 0.6, 3.2)
        h0 = 180
        h = h0 + pct * 7 * g
        rrect(c, cx - 120, base - h, 240, h, 14)
        c.set_source_rgb(*col)
        c.fill()
        c.set_source_rgba(0, 0, 0, 0.18)
        c.rectangle(cx - 120, base - h0 - 2, 240, 4)
        c.fill()
        txt(c, "+%d%%" % round(pct * g), cx, base - h - 22, 76, col if col != TEAL else (0.05, 0.45, 0.42), H)
        txt(c, lab, cx, base + 60, 40, INK, H)
    c.set_source_rgba(*INK, 0.6)
    c.set_line_width(4)
    c.set_dash([14, 10])
    c.move_to(160, base - 180)
    c.line_to(920, base - 180)
    c.stroke()
    c.set_dash([])
    txt(c, "2001 LEVEL", 920, base - 180 + 42, 32, (0.35, 0.33, 0.40), B, align="r")


def scene_210(c, t):
    panel(c, 110, 340, 860, 720)
    txt(c, "RENTERS EARNING", 540, 425, 52, INK, H)
    txt(c, "UNDER $30,000", 540, 492, 58, SEV, H)
    txt(c, "LEFT EACH MONTH AFTER", 540, 575, 42, (0.35, 0.33, 0.40), B)
    txt(c, "RENT AND UTILITIES", 540, 625, 42, (0.35, 0.33, 0.40), B)
    v = 210 * e(t, 0.4, 1.6)
    k = 1 + 0.06 * max(0, 1 - abs(t - 1.7) / 0.25)
    c.save()
    c.translate(540, 780)
    c.scale(k, k)
    txt(c, "$%d" % round(v), 0, 50, 190, INK, H)
    c.restore()
    ring(c, 540, 760, t - 1.6, 120, 420, 0.5, 8, SEV)
    b = back(e(t, 2.4, 2.8))
    if b > 0.01:
        c.save()
        c.translate(540, 965)
        c.scale(b, b)
        rrect(c, -330, -55, 660, 110, 55)
        c.set_source_rgb(*SEV)
        c.fill()
        txt(c, "DOWN 60% SINCE 2001", 0, 20, 52, (1, 1, 1), H)
        c.restore()


def scene_gap(c, t):
    panel(c, 110, 340, 860, 720)
    txt(c, "WHY IT STILL HURTS", 540, 425, 56, INK, H)
    rows = [("RENT, 2001 TO 2024", "+30%", SEV, 0.4), ("RENTERS' PAY", "+9%", (0.05, 0.45, 0.42), 0.9),
            ("PAYING OVER 30%", "49%", BURN, 1.4), ("RENT GROWTH NOW", "~0%", INK, 1.9)]
    for i, (l, v, col, t0) in enumerate(rows):
        k = e(t, t0, t0 + 0.35)
        if k <= 0:
            continue
        y = 520 + i * 125
        x = 160 - 60 * (1 - k)
        c.set_source_rgba(*INK, 0.12 * k)
        c.rectangle(160, y + 40, 760, 3)
        c.fill()
        txt(c, l, x, y + 20, 44, INK, H, align="l", a=k)
        txt(c, v, 920, y + 24, 66, col, H, align="r", a=k)
    txt(c, "ONE FLAT YEAR CAN'T UNDO 23 YEARS", 540, 1015, 40, SEV, H, a=e(t, 2.6, 3.0))


def wordmark(c, a=1.0):
    logo(c, 380, 128, 0.55, a)
    txt(c, "MONEY MAP", 565, 162, 42, CREAMC, H, a=a, stroke=INK, sw=8)


def endcard(c, t):
    facade(c, 30 + t, grid_hi=0)
    dimmer(c, 0.72 * e(t, 0, 0.4))
    a = e(t, 0.2, 0.7)
    logo(c, 540 - 96, 400, 3.2, a)
    txt(c, "MONEY MAP", 540, 780, 100, CREAMC, H, a=a, stroke=INK, sw=14)
    txt(c, "FOLLOW THE MONEY.", 540, 866, 52, LIT, H, a=e(t, 0.5, 1.0), stroke=INK, sw=10)
    b = e(t, 1.0, 1.5)
    rrect(c, 150, 950, 780, 120, 60)
    c.set_source_rgba(*LIT, b)
    c.fill()
    txt(c, "FOLLOW FOR MORE", 540, 1032, 58, INK, H, a=b)
    n = e(t, 1.6, 2.1)
    txt(c, "HOW MUCH OF YOUR PAY", 540, 1170, 52, CREAMC, H, a=n, stroke=INK, sw=10)
    txt(c, "GOES TO RENT?", 540, 1236, 52, LIT, H, a=n, stroke=INK, sw=10)


def draw(c, T):
    T = T % DUR
    bg(c)
    if T >= T_END:
        endcard(c, T - T_END)
        return
    gh = e(T, T_GRID - 0.3, T_GRID + 0.3) * (1 - e(T, T_210 - 0.3, T_210))
    facade(c, T, k_burn=e(T, T_GRID + 0.6, T_GRID + 2.6), k_sev=e(T, T_SEV + 0.3, T_SEV + 2.0), grid_hi=gh)
    sign(c, T)
    wordmark(c)
    if T_FLAT <= T < T_GRID or T_210 <= T < T_END:
        a = e(T, T_FLAT - 0.2, T_FLAT + 0.2) if T < T_GRID else e(T, T_210 - 0.2, T_210 + 0.2)
        if T < T_GRID:
            a *= 1 - e(T, T_GRID - 0.3, T_GRID)
        else:
            a *= 1 - e(T, T_END - 0.3, T_END)
        dimmer(c, 0.55 * a)
        c.push_group()
        if T < T_RACE:
            scene_flat(c, T - T_FLAT)
        elif T < T_GRID:
            scene_race(c, T - T_RACE)
        elif T < T_GAP:
            scene_210(c, T - T_210)
        else:
            scene_gap(c, T - T_GAP)
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    if T_GRID <= T < T_210:
        kb = e(T, T_GRID + 2.4, T_GRID + 2.8)
        ks = e(T, T_SEV + 1.6, T_SEV + 2.0)
        for (y, s, col, k) in ((320, "49 OF 100: OVER 30%", BURN, kb), (1105, "", SEV, 0)):
            if k > 0 and s:
                w = tw(c, s, 50, H) + 60
                rrect(c, 540 - w / 2, 300, w, 76, 38)
                c.set_source_rgba(*INK, 0.92 * k)
                c.fill()
                c.arc(540 - w / 2 + 38, 338, 14, 0, 2 * math.pi)
                c.set_source_rgba(*BURN, k)
                c.fill()
                txt(c, s, 540 + 14, 356, 50, CREAMC, H, a=k)
        if ks > 0:
            s = "26 OF 100: OVER HALF"
            w = tw(c, s, 50, H) + 60
            rrect(c, 540 - w / 2, 1070, w, 76, 38)
            c.set_source_rgba(*INK, 0.92 * ks)
            c.fill()
            c.arc(540 - w / 2 + 38, 1108, 14, 0, 2 * math.pi)
            c.set_source_rgba(*SEV, ks)
            c.fill()
            txt(c, s, 540 + 14, 1126, 50, CREAMC, H, a=ks)
    if not (T_GRID + 2.4 <= T < T_210 and T_SEV + 1.6 <= T):
        card(c, T)
    if T < 0.35:
        ring(c, 540, 455, T, 80, 420, 0.6, 12)


def cover_draw(c, T=0):
    bg(c)
    facade(c, 2.0)
    wordmark(c)
    dimmer(c, 0.35)
    panel(c, 150, 384, 780, 470)
    txt(c, "RENT GROWTH: ~0%", 540, 480, 58, INK, H)
    c.set_source_rgba(*INK, 0.15)
    c.rectangle(210, 530, 660, 3)
    c.fill()
    txt(c, "SO WHY IS", 540, 640, 84, INK, H)
    txt(c, "RENT SO HIGH?", 540, 740, 84, SEV, H)
    txt(c, "NOT THIS YEAR'S RENT", 540, 812, 44, (0.35, 0.33, 0.40), H)
    card(c, 0, custom=("THE REAL REASON", "STARTED YEARS AGO"))


def music(path="rent_music.wav"):
    tr = Track(DUR, 44)
    rng = tr.rng
    bar = 4 * BEAT
    chords = [[52, 55, 59, 62], [48, 52, 55, 59], [55, 59, 62, 66], [50, 54, 57, 62]]
    roots = [40, 36, 43, 38]
    hat = noise_hit(rng, 0.05, 7500, None, 0.01, 0.07)
    snare = noise_hit(rng, 0.18, 900, 5000, 0.05, 0.32)
    m = int(DUR * SR)
    crackle = np.zeros(m)
    idx = rng.randint(0, m, 260)
    crackle[idx] = rng.uniform(-0.25, 0.25, len(idx))
    tr.put(crackle, 0, 0.5)
    mel = [[(0.5, 74), (1.5, 71), (2.5, 74), (3, 76)], [(0.5, 72), (2, 71), (3, 67)], [(0.5, 71), (1.5, 74), (2.5, 78), (3.5, 76)], [(1, 74), (2, 69), (3, 66)]]
    for b in range(16):
        i = b % 4
        t0 = b * bar
        for q, off in enumerate((0, 0.04, 0.08, 0.12)):
            tr.put(epiano(chords[i][q], 0.9, 2.6), t0 + off)
        tr.put(epiano(chords[i][1] + 12, 0.5, 1.2), t0 + 2.5 * BEAT)
        tr.put(bassn(roots[i], 1.8 * BEAT, 0.34), t0)
        tr.put(bassn(roots[i], 0.8 * BEAT, 0.26), t0 + 2.75 * BEAT)
        if b >= 1:
            tr.put(kick(0.55), t0)
            tr.put(kick(0.4), t0 + 2.5 * BEAT)
            tr.put(snare, t0 + BEAT)
            tr.put(snare, t0 + 3 * BEAT)
            for q in range(8):
                tr.put(hat, t0 + q * 0.5 * BEAT + (0.04 if q % 2 else 0), 1.0 if q % 2 == 0 else 0.6)
        if b >= 4:
            for tb, mm in mel[i]:
                tr.put(marimba(mm, 0.55), t0 + tb * BEAT)
    tr.put(kick(1.0), 0.0)
    tr.put(bell(880, 0.6, 0.10), 0.0)
    for tp in (T_FLAT, T_RACE, T_GRID, T_210, T_GAP, T_END):
        tr.put(whoosh(rng, 0.55, 0.18), tp - 0.2)
    tr.put(riser(rng, 2.6, 0.16), T_RACE + 0.6)
    tr.put(kick(1.0), T_RACE + 3.2)
    for f in (659.3, 784.0, 987.8):
        tr.put(bell(f, 1.2, 0.08), T_RACE + 3.2)
    for k in range(49):
        tr.put(bell(1400 + (k * 37) % 600, 0.15, 0.025), T_GRID + 0.6 + k * 2.0 / 60)
    tr.put(kick(1.0), T_SEV + 1.7)
    tr.put(noise_hit(rng, 0.4, 150, 1500, 0.1, 0.3), T_SEV + 1.7)
    tr.put(bell(1046.5, 0.8, 0.10), T_210 + 1.6)
    tr.put(kick(0.9), T_210 + 2.5)
    for k in range(4):
        tr.put(bell(1174.7 + 120 * k, 0.4, 0.07), T_GAP + 0.4 + 0.5 * k)
    tr.put(bell(1568, 0.6, 0.08), T_END + 1.0)
    tr.save(path, lp=8000)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        for i, T in enumerate([float(x) for x in sys.argv[2:]]):
            still(draw, T, "b_%02d.png" % i)
    elif cmd == "cover":
        still(cover_draw, 0, sys.argv[2])
    elif cmd == "render":
        music()
        render(draw, DUR, sys.argv[2], "rent_music.wav", "rent")
