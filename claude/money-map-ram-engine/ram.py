import cairo, math, random
import numpy as np
import rm_engine
from rm_common import *

VODIR = "vo_ram"
CAP_Y = 1250
TAIL_END = 2.2
# name, spoken text, burned caption, mood, gap after (s)
LINES = [
    ("hook", "Makers are building about a quarter more RAM this year. So why is it so expensive?", "Forecast: RAM output up about 26% in 2026 (Counterpoint)", "curious", 0.34),
    ("hbm", "Because AI data centers want a special kind: high bandwidth memory.", "AI data centers want high bandwidth memory (HBM)", "serious", 0.46),
    ("wafer", "One gigabyte of it takes roughly three times the factory space.", "1 GB of HBM uses about 3x the chip-making space", "surprised", 0.31),
    ("share", "So less is left for your phone and laptop.", "Less capacity left for phones and laptops", "calm", 0.52),
    ("price", "Counterpoint says one common laptop module jumped a hundred and eighty percent in a single quarter.", "One laptop module: +180% in a quarter (Counterpoint)", "serious", 0.47),
    ("when", "Samsung expects the shortage to last through twenty twenty-seven. Maybe twenty twenty-eight.", "Samsung: shortage lasts through 2027, maybe 2028", "calm", 0.44),
    ("close", "RAM isn't scarce because it's rare. It's scarce because AI is first in line.", "RAM isn't scarce because it's rare. AI is first in line.", "warm", 0.38),
]
_BG = None
_TR = []


def mk_bg():
    global _BG, _TR
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    d = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, *G0)
    g.add_color_stop_rgb(1, *G1)
    d.set_source(g)
    d.paint()
    glow(d, VW / 2, 760, 880, (0.15, 0.85, 0.65), 0.10)
    glow(d, VW / 2, 1500, 700, (0.25, 0.45, 1.0), 0.05)
    rnd = random.Random(7)
    trs = []
    for side in (0, 1):
        for k in range(9):
            x0 = (30 + k * 26) if side == 0 else (VW - 30 - k * 26)
            y0 = rnd.randint(140, 1800)
            dirn = 1 if side == 0 else -1
            pts = [(x0, y0)]
            x, y = x0, y0
            for _ in range(rnd.randint(2, 4)):
                if rnd.random() < 0.5:
                    y += rnd.choice([-1, 1]) * rnd.randint(60, 220)
                else:
                    x += dirn * rnd.randint(40, 120) * 0.6
                    y += rnd.choice([-1, 1]) * rnd.randint(30, 90)
                x = max(8, min(VW - 8, x))
                y = max(100, min(VH - 100, y))
                pts.append((x, y))
            trs.append(pts)
    for pts in trs:
        d.set_line_width(2)
        d.set_source_rgba(0.35, 1.0, 0.8, 0.07)
        d.move_to(*pts[0])
        for p in pts[1:]:
            d.line_to(*p)
        d.stroke()
        for p in (pts[0], pts[-1]):
            d.arc(p[0], p[1], 5, 0, 2 * math.pi)
            d.set_source_rgba(0.35, 1.0, 0.8, 0.14)
            d.fill()
    logo(d, 52, 56, 0.7, 1.0)
    txt(d, "MONEY MAP", 112, 82, 30, WHITE, LBL, "l", 0.95)
    txt(d, "WHY IS IT SO EXPENSIVE? EP.02", 112, 118, 22, MINT, LBL, "l", 0.85)
    _BG, _TR = s, trs


def bg(c, T=0.0):
    if _BG is None:
        mk_bg()
    c.set_source_surface(_BG, 0, 0)
    c.paint()
    for i, pts in enumerate(_TR):
        if i % 3:
            continue
        seq = pts
        segs = [math.hypot(seq[k + 1][0] - seq[k][0], seq[k + 1][1] - seq[k][1]) for k in range(len(seq) - 1)]
        tot = sum(segs)
        u = ((T * 0.11 + i * 0.173) % 1.0) * tot
        run = 0
        for k, sl in enumerate(segs):
            if run + sl >= u:
                f = (u - run) / max(sl, 1e-6)
                x = seq[k][0] + (seq[k + 1][0] - seq[k][0]) * f
                y = seq[k][1] + (seq[k + 1][1] - seq[k][1]) * f
                glow(c, x, y, 26, MINT, 0.5)
                break
            run += sl


def dimm(c, x, y, w, h, lit=1.0, a=1.0, t=0.0, blink=False, col=MINT, lab="DDR5 RAM"):
    c.save()
    c.translate(x, y)
    glow(c, w / 2, h * 0.55, w * 0.62, col, 0.10 * a * lit)
    rrect(c, 0, 0, w, h, 14)
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgba(0, *BOARD2, a)
    g.add_color_stop_rgba(1, *BOARD, a)
    c.set_source(g)
    c.fill_preserve()
    c.set_source_rgba(0.5, 1.0, 0.85, 0.35 * a)
    c.set_line_width(3)
    c.stroke()
    cw = w / 64
    for k in range(48):
        px = w * 0.03 + k * (w * 0.94 / 48)
        if abs(px - w * 0.57) < w * 0.012:
            continue
        c.rectangle(px, h * 0.87, cw * 0.8, h * 0.13)
        c.set_source_rgba(*GOLDC, a)
        c.fill()
    n = 8
    cwid = (w * 0.9) / n
    for k in range(n):
        cx = w * 0.05 + k * cwid + cwid * 0.08
        ww = cwid * 0.84
        hh = h * 0.40
        cy = h * 0.14
        on = clamp(lit * (n + 2) - k)
        rrect(c, cx, cy, ww, hh, 7)
        c.set_source_rgba(*INK, a)
        c.fill_preserve()
        c.set_source_rgba(*mix((0.3, 0.35, 0.4), col, on), a * (0.6 + 0.4 * on))
        c.set_line_width(2.5)
        c.stroke()
        if on > 0:
            glow(c, cx + ww / 2, cy + hh / 2, ww * 0.9, col, 0.30 * on * a)
        c.arc(cx + 10, cy + 10, 3.5, 0, 2 * math.pi)
        c.set_source_rgba(0.8, 0.85, 0.9, 0.7 * a)
        c.fill()
        for q in range(2):
            ln(c, [(cx + ww * 0.25, cy + hh * (0.5 + q * 0.18)), (cx + ww * (0.7 - q * 0.2), cy + hh * (0.5 + q * 0.18))], (0.8, 0.85, 0.9), 2.5, 0.45 * a)
        ln(c, [(cx + ww / 2, cy + hh), (cx + ww / 2, h * 0.87)], GOLDC, 2, 0.35 * a)
    txt(c, lab, w * 0.07, h * 0.78, h * 0.12, WHITE, LBL, "l", 0.8 * a)
    c.restore()


def hbm(c, cx, base_y, w, prog, t, a=1.0):
    layers = 8
    gap = 46
    lh = 30
    rrect(c, cx - w * 0.68, base_y, w * 1.36, 44, 10)
    c.set_source_rgba(0.12, 0.13, 0.16, a)
    c.fill_preserve()
    c.set_source_rgba(*AMBER, 0.9 * a)
    c.set_line_width(4)
    c.stroke()
    n_vis = 0
    for k in range(layers):
        kk = back(clamp(prog * (layers + 1) - k))
        if kk <= 0:
            continue
        n_vis += 1
        yy = base_y - 18 - k * gap - (1 - kk) * 70
        c.save()
        c.translate(cx, yy)
        c.scale(1, 1)
        rrect(c, -w / 2, -lh / 2, w, lh, 8)
        g = cairo.LinearGradient(0, -lh / 2, 0, lh / 2)
        g.add_color_stop_rgba(0, 1.0, 0.8, 0.38, a * kk)
        g.add_color_stop_rgba(1, 0.85, 0.45, 0.08, a * kk)
        c.set_source(g)
        c.fill()
        c.restore()
    top = base_y - 18 - (layers - 1) * gap
    bot = base_y
    for k in range(5):
        px = cx - w * 0.38 + k * w * 0.19
        ln(c, [(px, bot), (px, top + (1 - clamp(prog * 1.1)) * (bot - top))], MINT, 4, 0.9 * a, dash=[3, 10])
    glow(c, cx, base_y - 18 - (layers - 1) * gap, w * 0.7, AMBER, 0.28 * clamp(prog) * a)


def wafer(c, cx, cy, r, s, hi, a=1.0, prog=1.0):
    g = cairo.RadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r)
    g.add_color_stop_rgba(0, 0.30, 0.34, 0.40, a)
    g.add_color_stop_rgba(1, 0.12, 0.14, 0.18, a)
    c.arc(cx, cy, r, 0, 2 * math.pi)
    c.set_source(g)
    c.fill_preserve()
    c.set_source_rgba(0.75, 0.82, 0.9, 0.5 * a)
    c.set_line_width(4)
    c.stroke()
    m = int(r / s) + 1
    for j in range(-m, m + 1):
        for i in range(-m, m + 1):
            px, py = cx + i * s, cy + j * s
            if math.hypot(px, py - 0) > 0 and math.hypot(px - cx, py - cy) > r - s * 0.9:
                continue
            col = hi.get((i, j))
            rrect(c, px - s * 0.42, py - s * 0.42, s * 0.84, s * 0.84, 5)
            if col is not None:
                col_, k = col
                c.set_source_rgba(*col_, a * k)
                c.fill()
            else:
                c.set_source_rgba(0.8, 0.9, 1.0, 0.13 * a * prog)
                c.fill()


def stamp_label(c, x, y, w, h, l1, l2, col, a=1.0, sc=1.0):
    if a <= 0:
        return
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.scale(max(sc, 0.001), max(sc, 0.001))
    c.translate(-w / 2, -h / 2)
    rrect(c, 0, 0, w, h, 12)
    c.set_source_rgba(0.02, 0.03, 0.05, 0.94 * a)
    c.fill_preserve()
    c.set_source_rgba(*col, a)
    c.set_line_width(4)
    c.stroke()
    txt(c, l1, w / 2, h * 0.42, 34, col, HEAD, "c", a)
    txt(c, l2, w / 2, h * 0.80, 26, WHITE, LBL, "c", a * 0.9)
    c.restore()


def head(c, l1, l2, t, col2=AMBER, y1=385, y2=485, size=100, fade=True):
    k = 1.0 + 0.05 * math.exp(-t * 9) if t < 1 else 1.0
    c.save()
    c.translate(VW / 2, (y1 + y2) / 2)
    c.scale(k, k)
    s1 = fit(c, l1, 900, size)
    s2 = fit(c, l2, 900, size)
    txt(c, l1, 0, y1 - (y1 + y2) / 2, s1, WHITE, HEAD, "c", e(t, 0, 0.12) if fade else 1.0)
    txt(c, l2, 0, y2 - (y1 + y2) / 2, s2, col2, HEAD, "c", e(t, 0.05, 0.2) if fade else 1.0)
    c.restore()


def s_hook(c, t, d):
    head(c, "MORE RAM.", "HIGHER PRICE.", t, AMBER, 385, 485, 98, fade=False)
    kq = 1.0 + 0.06 * math.sin(t * 5) if t > 0.6 else 1.0
    c.save()
    c.translate(VW / 2, 612)
    c.scale(kq, kq)
    txt(c, "WHY?", 0, 0, 118, MINT, HEAD, "c", 1.0)
    c.restore()
    dimm(c, 90, 690, 900, 230, lit=0.12 + 0.88 * e(t, 0.0, 1.6), t=t)
    k1 = back(e(t, 0.9, 1.3))
    if k1 > 0:
        c.save()
        c.translate(300, 1010)
        c.scale(max(k1, 0.001), max(k1, 0.001))
        rrect(c, -190, -42, 380, 84, 14)
        c.set_source_rgba(*MINT, 1)
        c.fill()
        tri(c, -152, 0, 20, INK)
        txt(c, "OUTPUT +26%", 28, 14, 36, INK, HEAD, "c")
        c.restore()
    k2 = back(e(t, 1.6, 2.0))
    if k2 > 0:
        c.save()
        c.translate(760, 1010)
        c.rotate(0.04 * math.sin(t * 4))
        c.scale(max(k2, 0.001), max(k2, 0.001))
        rrect(c, -190, -42, 380, 84, 14)
        c.set_source_rgba(*RED, 1)
        c.fill()
        tri(c, -152, 0, 20, INK)
        txt(c, "PRICE $???", 28, 14, 36, INK, HEAD, "c")
        c.restore()
    txt(c, "2026 FORECAST · COUNTERPOINT, MARCH", VW / 2, 1100, 26, WHITE, LBL, "c", 0.65 * e(t, 0.8, 1.4))


def s_hbm(c, t, d):
    head(c, "AI WANTS A", "SPECIAL KIND.", t, AMBER, 385, 485, 98)
    k = e(t, 0.0, 0.7)
    dimm(c, lerp(90, 40, k), lerp(690, 1000, k), lerp(900, 330, k), lerp(230, 86, k), lit=1.0 - 0.7 * k, a=1.0 - 0.45 * k, col=MINT, lab="")
    prog = e(t, 0.5, 2.2)
    hbm(c, 600, 930, 300, prog, t, e(t, 0.4, 0.8))
    a2 = e(t, 1.6, 2.1)
    txt(c, "HBM", 600, 1035, 54, AMBER, HEAD, "c", a2)
    txt(c, "HIGH BANDWIDTH MEMORY", 600, 1078, 28, WHITE, LBL, "c", 0.8 * a2)
    txt(c, "REGULAR RAM", 205, 1130, 26, MINT, LBL, "c", 0.8 * k)


def s_wafer(c, t, d):
    head(c, "SAME FACTORY.", "3x THE SPACE.", t, AMBER, 385, 485, 98)
    cx, cy, r, s = 540, 830, 290, 46
    wafer(c, cx, cy, r, s, {}, e(t, 0.0, 0.4), 1.0)
    hi = {}
    k1 = e(t, 0.7, 1.0)
    hi[(-3, -2)] = (MINT, 0.95 * k1)
    for i, cell in enumerate(((2, 2), (3, 2), (2, 3))):
        hi[cell] = (AMBER, 0.95 * e(t, 1.4 + i * 0.35, 1.7 + i * 0.35))
    wafer(c, cx, cy, r, s, hi, 1.0, 0.0) if False else None
    for cell, (col_, kk) in hi.items():
        if kk <= 0:
            continue
        px, py = cx + cell[0] * s, cy + cell[1] * s
        glow(c, px, py, 70, col_, 0.35 * kk)
        rrect(c, px - s * 0.42, py - s * 0.42, s * 0.84, s * 0.84, 5)
        c.set_source_rgba(*col_, kk)
        c.fill()
    la = e(t, 0.9, 1.3)
    if la > 0:
        ln(c, [(cx - 3 * s, cy - 2 * s), (cx - 3 * s - 40, cy - 2 * s - 70), (150, cy - 2 * s - 70)], MINT, 3, la)
        stamp_label(c, 90, cy - 2 * s - 138, 330, 90, "1 GB", "REGULAR RAM", MINT, la)
    lb = e(t, 1.9, 2.3)
    if lb > 0:
        ln(c, [(cx + 3 * s, cy + 2 * s + 20), (cx + 3 * s + 30, cy + 2 * s + 90), (880, cy + 2 * s + 90)], AMBER, 3, lb)
        stamp_label(c, 660, cy + 2 * s + 60, 330, 90, "1 GB", "OF HBM", AMBER, lb)
    kb = back(e(t, 2.6, 3.0))
    if kb > 0:
        c.save()
        c.translate(880, 610)
        c.scale(max(kb, 0.001), max(kb, 0.001))
        c.arc(0, 0, 76, 0, 2 * math.pi)
        c.set_source_rgb(*AMBER)
        c.fill()
        txt(c, "3x", 0, 28, 84, INK, HEAD)
        c.restore()
    txt(c, "ILLUSTRATION · RATIO PER TOM'S HARDWARE, DEC 2025", VW / 2, 1150, 24, WHITE, LBL, "c", 0.6 * e(t, 0.5, 1.0))


def s_share(c, t, d):
    head(c, "MORE FOR AI.", "LESS FOR YOU.", t, AMBER, 385, 485, 98)
    x0, y0, W, H = 100, 640, 880, 130
    kshare = lerp(0.24, 0.62, e(t, 0.3, 2.0))
    rrect(c, x0, y0, W, H, 18)
    c.set_source_rgba(*MINT, 0.9)
    c.fill()
    c.save()
    rrect(c, x0, y0, W, H, 18)
    c.clip()
    c.rectangle(x0, y0, W * kshare, H)
    c.set_source_rgba(*AMBER, 1)
    c.fill()
    c.restore()
    xs = x0 + W * kshare
    ln(c, [(xs, y0 - 26), (xs, y0 + H + 26)], WHITE, 6, 1.0)
    txt(c, "AI MEMORY", x0 + 24, y0 + H / 2 + 12, 34, INK, HEAD, "l", e(t, 0.2, 0.5))
    if kshare < 0.48:
        pass
    txt(c, "EVERYTHING ELSE", x0 + W - 24, y0 + H / 2 + 12, 34, INK, HEAD, "r", e(t, 0.2, 0.5) * clamp((1 - kshare) * 3 - 0.35))
    txt(c, "FACTORY CAPACITY (ILLUSTRATION)", x0, y0 - 52, 30, WHITE, LBL, "l", 0.85)
    for k in range(7):
        t0 = 0.3 + k * 0.2
        kk = e(t, t0, t0 + 0.7)
        px = lerp(x0 + W - 90, xs + 40, kk)
        glow(c, px, y0 + H / 2, 34, WHITE, 0.0)
        if 0 < kk < 1:
            c.arc(px, y0 + H + 62, 12, 0, 2 * math.pi)
            c.set_source_rgba(*AMBER, 0.9)
            c.fill()
    sc = 1.0 - 0.5 * e(t, 0.3, 2.0)
    ph_x, ph_y = 230, 950
    c.save()
    c.translate(ph_x, ph_y)
    c.scale(sc, sc)
    rrect(c, -50, -90, 100, 180, 16)
    c.set_source_rgba(0.1, 0.12, 0.16, 1)
    c.fill_preserve()
    c.set_source_rgba(*MINT, 1)
    c.set_line_width(5)
    c.stroke()
    c.restore()
    c.save()
    c.translate(650, 985)
    c.scale(sc, sc)
    rrect(c, -150, -95, 300, 190, 12)
    c.set_source_rgba(0.1, 0.12, 0.16, 1)
    c.fill_preserve()
    c.set_source_rgba(*MINT, 1)
    c.set_line_width(5)
    c.stroke()
    rrect(c, -190, 95, 380, 16, 8)
    c.set_source_rgba(*MINT, 1)
    c.fill()
    c.restore()
    txt(c, "YOUR PHONE", ph_x, 1100, 28, MINT, LBL, "c", 0.9 * e(t, 0.5, 0.9))
    txt(c, "YOUR LAPTOP", 650, 1110, 28, MINT, LBL, "c", 0.9 * e(t, 0.5, 0.9))


def s_price(c, t, d):
    head(c, "ONE LAPTOP MODULE.", "ONE QUARTER.", t, AMBER, 385, 485, 86)
    base = 1055
    bw = 230
    h0, h1 = 150, 150 + 270 * e(t, 0.7, 2.4)
    x0, x1 = 250, 600
    c.rectangle(x0, base - h0, bw, h0)
    c.set_source_rgba(*MINT, 0.95)
    c.fill()
    top = base - h1
    c.rectangle(x1, top, bw, h1)
    g = cairo.LinearGradient(0, top, 0, base)
    g.add_color_stop_rgba(0, *RED, 1)
    g.add_color_stop_rgba(1, 0.8, 0.2, 0.2, 1)
    c.set_source(g)
    c.fill()
    ln(c, [(x0 + bw, base - h0), (x1 + bw + 40, base - h0)], WHITE, 3, 0.6 * e(t, 0.6, 1.0), dash=[10, 8])
    txt(c, "100", x0 + bw / 2, base - h0 / 2 + 22, 64, INK, HEAD, "c", e(t, 0.2, 0.5))
    txt(c, "%d" % round(100 + 180 * e(t, 0.7, 2.4)), x1 + bw / 2, min(base - 20, top + 80), 64, INK, HEAD, "c", e(t, 0.8, 1.1))
    txt(c, "START", x0 + bw / 2, base + 40, 30, WHITE, LBL, "c", 0.9)
    txt(c, "A QUARTER LATER", x1 + bw / 2, base + 40, 30, WHITE, LBL, "c", 0.9)
    v = round(180 * e(t, 0.7, 2.4))
    ks = 1.0 + 0.04 * math.sin(t * 10) if 0.7 < t < 2.4 else 1.0
    c.save()
    c.translate(330, 670)
    c.scale(ks, ks)
    txt(c, "+%d%%" % v, 0, 0, 150, AMBER if v < 180 else RED, HEAD, "c", e(t, 0.5, 0.8))
    c.restore()
    txt(c, "8 GB DDR4 LAPTOP MODULE · COUNTERPOINT, Q1 2026", VW / 2, 1140, 24, WHITE, LBL, "c", 0.6)


def xpos(yr):
    return 130 + (yr - 2026) * 270


def s_when(c, t, d):
    head(c, "HOW LONG?", "ASK SAMSUNG.", t, AMBER, 385, 485, 100)
    y0, H = 700, 86
    ln(c, [(xpos(2026), y0 + H + 40), (xpos(2029), y0 + H + 40)], WHITE, 3, 0.8)
    for yr in (2026, 2027, 2028, 2029):
        ln(c, [(xpos(yr), y0 + H + 30), (xpos(yr), y0 + H + 52)], WHITE, 3, 0.9)
    for yr in (2026, 2027, 2028):
        txt(c, str(yr), xpos(yr) + 135, y0 + H + 112, 44, WHITE, HEAD, "c", 0.95)
    k1 = e(t, 0.4, 1.8)
    x_a, x_b = xpos(2026), xpos(2028)
    rrect(c, x_a, y0, (x_b - x_a) * k1, H, 14)
    c.set_source_rgba(*RED, 1)
    c.fill()
    k2 = e(t, 1.9, 2.8)
    if k2 > 0:
        ln(c, [(x_b + 6, y0 + H / 2), (x_b + 6 + (xpos(2029) - x_b - 6) * k2, y0 + H / 2)], AMBER, 18, 1.0, dash=[26, 16])
    txt(c, "SHORTAGE", x_a + 22, y0 + H / 2 + 14, 40, INK, HEAD, "l", e(t, 0.5, 0.9))
    txt(c, "MAYBE", (x_b + xpos(2029)) / 2, y0 - 22, 38, AMBER, HEAD, "c", k2)
    tx = xpos(2026) + 270 * (10.8 / 12)
    kt = e(t, 0.2, 0.6)
    ln(c, [(tx, y0 - 50), (tx, y0 + H + 36)], WHITE, 4, 0.95 * kt)
    txt(c, "TODAY", tx, y0 - 66, 30, WHITE, LBL, "c", kt)
    txt(c, "OTHER FORECASTS DIFFER", VW / 2, 1010, 36, GREY, HEAD, "c", e(t, 2.4, 2.9))
    txt(c, "A FORECAST, NOT A GUARANTEE", VW / 2, 1060, 28, WHITE, LBL, "c", 0.75 * e(t, 2.6, 3.1))
    txt(c, "SAMSUNG VIA PCWORLD, 31 JUL 2026", VW / 2, 1130, 24, WHITE, LBL, "c", 0.6)


def s_close(c, t, d):
    head(c, "AI IS FIRST", "IN LINE.", t, AMBER, 385, 485, 100)
    base = 1000
    items = [("AI DATA", "CENTERS", AMBER, 290, 360, 100), ("PHONES", "", MINT, 150, 190, 430), ("LAPTOPS", "", MINT, 160, 150, 610), ("YOU", "", WHITE, 120, 120, 800)]
    for k, (l1, l2, col, w, h, x) in enumerate(items):
        t0 = 0.3 + k * 0.45
        kk = back(e(t, t0, t0 + 0.4))
        if kk <= 0:
            continue
        c.save()
        c.translate(x + w / 2, base)
        c.scale(1, max(kk, 0.001))
        rrect(c, -w / 2, -h, w, h, 14)
        c.set_source_rgba(0.04, 0.05, 0.07, 1)
        c.fill_preserve()
        c.set_source_rgba(*col, 1)
        c.set_line_width(5)
        c.stroke()
        if k == 0:
            for q in range(5):
                ln(c, [(-w / 2 + 28, -h + 40 + q * 56), (w / 2 - 28, -h + 40 + q * 56)], AMBER, 4, 0.8)
                c.arc(w / 2 - 44, -h + 40 + q * 56, 6, 0, 2 * math.pi)
                c.set_source_rgba(*MINT, 1)
                c.fill()
        c.restore()
        txt(c, l1, x + w / 2, base + 48, 28 if k else 30, col, LBL, "c", kk)
        if l2:
            txt(c, l2, x + w / 2, base + 82, 28, col, LBL, "c", kk)
    kf = back(e(t, 1.2, 1.6))
    if kf > 0:
        c.save()
        c.translate(245, base - 400)
        c.rotate(-0.08)
        c.scale(max(kf, 0.001), max(kf, 0.001))
        rrect(c, -105, -34, 210, 68, 12)
        c.set_source_rgba(*AMBER, 1)
        c.fill()
        txt(c, "FIRST", 0, 14, 40, INK, HEAD)
        c.restore()
    ka = e(t, 2.0, 2.6)
    ln(c, [(110, base + 110), (940, base + 110)], WHITE, 4, 0.6 * ka)
    tri(c, 950, base + 110, 18, WHITE, 0.6 * ka, up=True) if False else None
    txt(c, "THE LINE", VW / 2, base + 150, 26, WHITE, LBL, "c", 0.6 * ka)
    if t > d - 2.2:
        endcard(c, t - (d - 2.2))


def endcard(c, t):
    a = e(t, 0, 0.4)
    c.set_source_rgba(0.015, 0.02, 0.035, a)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    glow(c, VW / 2, 760, 700, MINT, 0.10 * a)
    logo(c, VW / 2 - 150, 450, 5.0, a)
    txt(c, "MONEY MAP", VW / 2, 970, 124, WHITE, HEAD, "c", a)
    txt(c, "WHY IS IT SO EXPENSIVE? · EP. 2", VW / 2, 1050, 38, MINT, LBL, "c", e(t, 0.2, 0.6))
    txt(c, "NEXT: WHY ARE CARS SO EXPENSIVE?", VW / 2, 1120, 34, WHITE, LBL, "c", e(t, 0.4, 0.8))
    pill(c, VW / 2, 1230, 640, 100, GOLDC, e(t, 0.5, 0.9))
    txt(c, "FOLLOW FOR EP. 3", VW / 2, 1252, 52, INK, HEAD, "c", e(t, 0.5, 0.9))


SCENES = {"hook": s_hook, "hbm": s_hbm, "wafer": s_wafer, "share": s_share, "price": s_price, "when": s_when, "close": s_close}


def draw(c, name, t, d, T, i):
    SCENES[name](c, t, d)


def cover(c):
    bg(c, 3.0)
    for s_, y, sz, col in (("MORE RAM.", 540, 150, WHITE), ("HIGHER PRICE.", 680, 118, AMBER), ("WHY?", 880, 190, MINT)):
        sz = fit(c, s_, 860, sz)
        txt(c, s_, VW / 2, y, sz, col, HEAD, "c", 1.0, stroke=(0.02, 0.03, 0.05), sw=14)
    dimm(c, 90, 930, 900, 230, lit=1.0)
    c.save()
    c.translate(830, 930)
    c.rotate(0.10)
    rrect(c, -150, -46, 300, 92, 16)
    c.set_source_rgba(*RED, 1)
    c.fill()
    txt(c, "PRICE $???", 0, 16, 44, INK, HEAD)
    c.restore()


def bed(tl, mx, sr, rng, total):
    n = len(mx)
    tt = np.arange(n) / sr
    for fr, amp in ((110.0, 1.0), (164.8, 0.6), (220.0, 0.35)):
        mx += 0.010 * amp * np.sin(2 * np.pi * fr * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * tt / 7))
    scale = [220.0, 261.6, 329.6, 392.0, 440.0]
    step = 60 / 100 / 2
    k = 0
    t = 0.4
    r2 = np.random.RandomState(3)
    while t < total:
        f = scale[r2.randint(0, len(scale))]
        pluck(mx, sr, t, f, 0.30, 0.020)
        t += step * (2 if r2.rand() < 0.35 else 1)
        k += 1


def pluck(mx, sr, t, f, dur, amp):
    i0 = int(t * sr)
    nn = int(dur * sr)
    if i0 >= len(mx):
        return
    x = np.arange(nn) / sr
    w = amp * np.sin(2 * np.pi * f * x) * np.exp(-x * 11) + amp * 0.4 * np.sin(2 * np.pi * f * 2 * x) * np.exp(-x * 16)
    j = min(len(mx) - i0, nn)
    mx[i0:i0 + j] += w[:j]


def blip(mx, sr, t, f, dur=0.08, amp=0.08, f2=None):
    i0 = int(t * sr)
    nn = int(dur * sr)
    if i0 >= len(mx):
        return
    x = np.arange(nn) / sr
    ff = f if f2 is None else np.linspace(f, f2, nn)
    ph = 2 * np.pi * np.cumsum(ff * np.ones(nn)) / sr
    w = amp * np.sin(ph) * np.exp(-x * (5 / dur))
    j = min(len(mx) - i0, nn)
    mx[i0:i0 + j] += w[:j]


def whoosh(mx, sr, t, dur=0.5, amp=0.05, rng=None, up=True):
    i0 = int(t * sr)
    nn = int(dur * sr)
    if i0 >= len(mx):
        return
    nz = rng.randn(nn)
    k = np.ones(40) / 40
    nz = np.convolve(nz, k, "same")
    env = np.sin(np.pi * np.arange(nn) / nn) ** 2
    w = amp * nz * env * 3
    j = min(len(mx) - i0, nn)
    mx[i0:i0 + j] += w[:j]


def thump(mx, sr, t, amp=0.22):
    blip(mx, sr, t, 120, 0.22, amp, 45)


def sfx(tl, mx, sr, rng):
    for i, (t0, dd) in enumerate(tl):
        whoosh(mx, sr, t0 - 0.05 if i else t0, 0.4, 0.05, rng)
    t0 = tl[0][0]
    for k in range(8):
        blip(mx, sr, t0 + 0.15 + k * 0.12 * 1.0, 700 + k * 60, 0.05, 0.05)
    blip(mx, sr, t0 + 0.9, 880, 0.12, 0.09)
    blip(mx, sr, t0 + 1.6, 220, 0.2, 0.10, 160)
    t0 = tl[1][0]
    for k in range(8):
        blip(mx, sr, t0 + 0.5 + k * 0.19, 300 + k * 70, 0.06, 0.07)
    t0 = tl[2][0]
    blip(mx, sr, t0 + 0.7, 990, 0.1, 0.08)
    for k in range(3):
        blip(mx, sr, t0 + 1.4 + k * 0.35, 520 + k * 60, 0.09, 0.08)
    thump(mx, sr, t0 + 2.6)
    t0 = tl[3][0]
    whoosh(mx, sr, t0 + 0.3, 1.7, 0.04, rng)
    for k in range(7):
        blip(mx, sr, t0 + 0.4 + k * 0.2, 600 - k * 30, 0.05, 0.05)
    t0 = tl[4][0]
    for k in range(18):
        blip(mx, sr, t0 + 0.7 + k * 0.095, 400 + k * 40, 0.04, 0.05)
    thump(mx, sr, t0 + 2.4, 0.26)
    t0 = tl[5][0]
    whoosh(mx, sr, t0 + 0.4, 1.4, 0.04, rng)
    blip(mx, sr, t0 + 1.9, 330, 0.12, 0.09)
    blip(mx, sr, t0 + 2.0, 330, 0.12, 0.09, 300)
    t0 = tl[6][0]
    for k in range(4):
        blip(mx, sr, t0 + 0.3 + k * 0.45, 440 + k * 70, 0.1, 0.09)
    blip(mx, sr, t0 + 1.3, 700, 0.1, 0.09)
    thump(mx, sr, t0 + 1.2)
    te = tl[-1][0] + tl[-1][1] - 2.2
    for k, f in enumerate((523.3, 659.3, 784.0)):
        blip(mx, sr, te + 0.05 + k * 0.1, f, 0.5, 0.07)


bed.__doc__ = "quiet A minor pad plus pentatonic plucks"


class _EP:
    pass


EP = _EP()
for _n in ("VODIR", "CAP_Y", "TAIL_END", "LINES", "bg", "draw", "cover", "bed", "sfx"):
    setattr(EP, _n, globals()[_n])

if __name__ == "__main__":
    rm_engine.main(EP)
