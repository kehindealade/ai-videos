import cairo, math
import numpy as np
import wx_engine
from wx_common import *

VODIR = "vo_ink"
VOICE, SPEED = "af_aoede", 0.98
CAP_Y = 1345
PAD = ((87.3, 1.0), (130.8, 0.6), (220.0, 0.35))
LINES = [
    ("hook", "Per ounce, this ink costs three times more than aged Scotch.", "Per ounce, this ink costs three times more than aged Scotch."),
    ("printer", "One estimate says a seventy-dollar printer costs a hundred and twenty to build.", "One estimate: a $70 printer costs about $120 to build."),
    ("razor", "So the money is in the refills. It's the razor and blades model.", "So the money is in the refills. It's the razor and blades model."),
    ("chip", "And the cartridge is built to fit only that printer.", "And the cartridge is built to fit only that printer."),
    ("count", "You pay once for the printer. The ink can cost more within a year or two.", "You pay once for the printer. Ink can cost more within 1 to 2 years."),
    ("close", "You're not just buying ink. You're paying for the business model.", "You're not just buying ink. You're paying for the business model."),
]
BODY_PTS = [(0, 70), (70, 0), (280, 0), (280, 360), (230, 360), (230, 400), (50, 400), (50, 360), (0, 360)]
_BG = None


def bg(c, T=0.0):
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        d = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, *B0)
        g.add_color_stop_rgb(1, *B1)
        d.set_source(g)
        d.paint()
        rg = cairo.RadialGradient(VW / 2, 760, 50, VW / 2, 760, 900)
        rg.add_color_stop_rgba(0, 0.25, 0.5, 1, 0.22)
        rg.add_color_stop_rgba(1, 0.25, 0.5, 1, 0)
        d.set_source(rg)
        d.paint()
        d.set_line_width(1.5)
        for x in range(0, VW + 1, 40):
            d.set_source_rgba(0.8, 0.9, 1, 0.16 if x % 200 == 0 else 0.065)
            d.move_to(x + 0.5, 0)
            d.line_to(x + 0.5, VH)
            d.stroke()
        for y in range(0, VH + 1, 40):
            d.set_source_rgba(0.8, 0.9, 1, 0.16 if y % 200 == 0 else 0.065)
            d.move_to(0, y + 0.5)
            d.line_to(VW, y + 0.5)
            d.stroke()
        logo(d, 52, 56, 0.7, 1.0)
        txt(d, "MONEY MAP", 112, 82, 30, WHITE, LBL, "l", 0.95)
        txt(d, "WHY IS IT SO EXPENSIVE?  EP.01", 112, 118, 22, CYAN, LBL, "l", 0.85)
        _BG = s
    c.set_source_surface(_BG, 0, 0)
    c.paint()


def cartridge(c, x, y, s, prog=1.0, chip=0.0, mirror=False, a=1.0, ink=True, col=WHITE):
    c.save()
    c.translate(x, y)
    if mirror:
        c.translate(280 * s, 0)
        c.scale(-s, s)
    else:
        c.scale(s, s)
    w = 5.5
    p1 = clamp(prog * 1.25)
    p2 = clamp(prog * 1.25 - 0.25)
    c.move_to(*BODY_PTS[0])
    for p in BODY_PTS[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgba(*col, 0.07 * a * p1)
    c.fill()
    ln(c, BODY_PTS, col, w, a, True, p1)
    if p2 > 0:
        ln(c, [(28, 120), (252, 120), (252, 236), (28, 236)], col, 3.5, a * 0.9, True, p2)
        for k, wd in enumerate((200, 150, 175)):
            ln(c, [(48, 150 + k * 30), (48 + wd * p2, 150 + k * 30)], col, 3, a * 0.55)
        if ink:
            rrect(c, 28, 262, 224, 70, 6)
            c.set_source_rgba(0.1, 0.1, 0.12, 0.8 * a * p2)
            c.fill_preserve()
            c.set_source_rgba(*col, a * p2)
            c.set_line_width(3.5)
            c.stroke()
            c.rectangle(34, 270, 212, 54)
            c.set_source_rgba(0.04, 0.05, 0.08, 0.95 * a * p2)
            c.fill()
            c.rectangle(34, 296, 212, 28)
            c.set_source_rgba(0.1, 0.1, 0.14, 1)
            c.fill()
        ccol = CYAN if chip > 0 else col
        if chip > 0:
            c.set_source_rgba(*CYAN, 0.35 * chip * a)
            c.rectangle(64, 358, 152, 44)
            c.fill()
        ln(c, [(74, 366), (206, 366), (206, 394), (74, 394)], ccol, 4 if chip > 0 else 3.5, a, True, p2)
        for k in range(6):
            px = 86 + k * 20
            c.rectangle(px, 372, 12, 16)
            c.set_source_rgba(*ccol, a * p2 * (1.0 if chip > 0 else 0.7))
            c.fill()
        ln(c, [(140, -34), (140, 436)], col, 2, a * 0.3 * p2, dash=[18, 6, 3, 6])
    c.restore()


def printer(c, x, y, s, prog=1.0, a=1.0, col=WHITE, paper=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = clamp(prog * 1.2)
    p2 = clamp(prog * 1.2 - 0.2)
    top = [(50, 0), (470, 0), (520, 80), (0, 80)]
    ln(c, top, col, 6, a, True, p)
    c.move_to(*top[0])
    for q in top[1:]:
        c.line_to(*q)
    c.close_path()
    c.set_source_rgba(*col, 0.06 * a * p)
    c.fill()
    rrect(c, 0, 80, 520, 170, 16)
    c.set_source_rgba(*col, 0.07 * a * p)
    c.fill_preserve()
    c.set_source_rgba(*col, a * p)
    c.set_line_width(6)
    c.stroke()
    if p2 > 0:
        ln(c, [(60, 250), (460, 250), (485, 305), (35, 305)], col, 5, a, True, p2)
        if paper:
            ln(c, [(110, 305), (110, 345), (410, 345), (410, 305)], col, 4, a * 0.9, False, p2)
        rrect(c, 50, 112, 250, 62, 8)
        c.set_source_rgba(*col, a * 0.85 * p2)
        c.set_line_width(3.5)
        c.stroke()
        rrect(c, 380, 112, 100, 62, 8)
        c.stroke()
        for k in range(3):
            c.arc(402 + k * 34, 143, 8, 0, 2 * math.pi)
            c.fill()
        ln(c, [(70, 205), (450, 205)], col, 3, a * 0.5, False, p2)
        ln(c, [(260, -40), (260, 360)], col, 2, a * 0.3 * p2, dash=[18, 6, 3, 6])
    c.restore()


def coin(c, x, y, r, a=1.0):
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(*GOLD, a)
    c.fill_preserve()
    c.set_source_rgba(0.5, 0.35, 0.05, a)
    c.set_line_width(max(2, r * 0.1))
    c.stroke()
    txt(c, "$", x, y + r * 0.38, r * 1.15, (0.35, 0.22, 0.02), HEAD, "c", a)


def hook_layout(c, t, ink_prog=1.0, bars=True, a_text=1.0, top=True):
    if top:
        k = 1.0 + 0.04 * math.exp(-t * 9) if t < 1 else 1.0
        c.save()
        c.translate(VW / 2, 385)
        c.scale(k, k)
        txt(c, "THIS INK COSTS MORE", 0, -55, 104, WHITE, HEAD, "c", a_text)
        txt(c, "THAN AGED SCOTCH?", 0, 55, 104, YEL, HEAD, "c", a_text)
        c.restore()
    prog = 0.6 + 0.4 * e(t, 0, 0.5)
    cartridge(c, 410, 480, 0.92, prog if bars else 1.0)
    dim(c, 695, 721, 695, 785, "ABOUT 0.9 OZ", off=0, col=CYAN, prog=e(t, 0.1, 0.6), size=28, side=1)
    sc = 0.92 + 0.08 * back(e(t, 0, 0.4))
    callout(c, 40, 600, 330, ["HP 962 BLACK", "^$40.22", "PER OUNCE"], YEL, 1.0, sc, 34, tip=(437, 753))


def bars(c, t):
    rows = [("STEAK (DRY-AGED RIBEYE)", 3.41, WHITE, 0.0, 0.5), ("SCOTCH (18-YEAR-OLD)", 13.01, CYAN, 0.4, 1.0), ("THIS INK (HP 962 BLACK)", 40.22, YEL, 0.9, 2.0)]
    for k, (lab, val, col, t0, t1) in enumerate(rows):
        yy = 925 + k * 92
        kk = e(t, t0, t1)
        txt(c, lab, 80, yy, 30, WHITE, LBL, "l", 0.95)
        wd = max(4, 700 * val / 40.22 * kk)
        c.rectangle(80, yy + 12, wd, 44)
        c.set_source_rgba(*col, 0.92)
        c.fill()
        c.rectangle(80, yy + 12, 700 * val / 40.22, 44)
        c.set_source_rgba(*col, 0.16)
        c.set_line_width(2)
        c.stroke()
        txt(c, "$%.2f" % (val * kk), 80 + wd + 14, yy + 52, 44, col, HEAD, "l", e(t, t0, t0 + 0.2))
    k = back(e(t, 2.3, 2.7))
    if k > 0:
        c.save()
        c.translate(880, 1040)
        c.scale(max(k, 0.001), max(k, 0.001))
        c.arc(0, 0, 62, 0, 2 * math.pi)
        c.set_source_rgb(*YEL)
        c.fill()
        txt(c, "3x", 0, 24, 70, (0.05, 0.1, 0.3), HEAD)
        c.restore()
    txt(c, "PRICES PER OUNCE · TECHLICIOUS, JAN 2025", 80, 1200, 24, WHITE, LBL, "l", 0.7 * e(t, 0.5, 1.0))


def s_hook(c, t, d):
    hook_layout(c, t)
    bars(c, t)


def s_printer(c, t, d):
    txt(c, "THE $70 PRINTER", VW / 2, 330, 110, WHITE, HEAD)
    txt(c, "COSTS HOW MUCH TO MAKE?", VW / 2, 420, 62, YEL, HEAD)
    printer(c, 290, 500, 0.86, e(t, 0, 1.3))
    k = back(e(t, 1.2, 1.6))
    callout(c, 40, 880, 440, ["SOLD FOR", "^$70"], YEL, 1.0, 0.9 + 0.1 * k if k > 0 else 0.001, 34, tip=(400, 785))
    k2 = back(e(t, 2.3, 2.7))
    callout(c, 560, 880, 460, ["BUILD COST (EST.)", "^~$120"], RED, 1.0, 0.9 + 0.1 * k2 if k2 > 0 else 0.001, 34, tip=(640, 790))
    k3 = back(e(t, 3.5, 3.9))
    if k3 > 0:
        c.save()
        c.translate(VW / 2, 1140)
        c.scale(max(k3, 0.001), max(k3, 0.001))
        txt(c, "-$50", 0, 0, 100, RED, HEAD, "c", 1.0, stroke=DARK, sw=10)
        txt(c, "ON THIS ONE MODEL", 0, 44, 28, WHITE, LBL)
        c.restore()
    txt(c, "ESTIMATE: IHS MARKIT, VIA CONSUMER REPORTS", 80, 1215, 24, WHITE, LBL, "l", 0.7 * e(t, 2.3, 2.8))


def s_razor(c, t, d):
    txt(c, "RAZOR + BLADES", VW / 2, 330, 120, WHITE, HEAD)
    printer(c, 70, 440, 0.34, e(t, 0, 0.5), paper=False)
    txt(c, "RAZOR = THE PRINTER", 290, 520, 40, WHITE, LBL, "l", e(t, 0.3, 0.6))
    pill(c, 480, 590, 320, 56, GREEN, e(t, 0.5, 0.9))
    txt(c, "SOLD CHEAP", 480, 609, 34, (0.02, 0.2, 0.1), LBL, "c", e(t, 0.5, 0.9))
    txt(c, "BLADES = THE INK", 70, 760, 40, WHITE, LBL, "l", e(t, 1.0, 1.3))
    for k in range(4):
        t0 = 1.4 + k * 0.5
        kk = back(e(t, t0, t0 + 0.35))
        cx = 90 + k * 230
        if kk > 0:
            c.save()
            c.translate(cx + 70, 900)
            c.scale(max(kk, 0.001), max(kk, 0.001))
            cartridge(c, -70, -100, 0.5, 1.0, a=1.0)
            c.restore()
            coin(c, cx + 70, 1075, 46 * max(kk, 0.01), e(t, t0 + 0.2, t0 + 0.4))
    pill(c, 540, 1170, 700, 60, YEL, e(t, 3.3, 3.7))
    txt(c, "SOLD AGAIN AND AGAIN", 540, 1191, 34, (0.1, 0.1, 0.25), LBL, "c", e(t, 3.3, 3.7))


def s_chip(c, t, d):
    txt(c, "BUILT FOR", VW / 2, 300, 100, WHITE, HEAD)
    txt(c, "ONE PRINTER", VW / 2, 400, 100, YEL, HEAD)
    chipk = e(t, 0.3, 0.6)
    cartridge(c, 120, 470, 0.95, e(t, 0, 0.4), chipk)
    bx, by, br = 760, 655, 170
    kk = e(t, 0.6, 1.0)
    if kk > 0:
        ln(c, [(120 + 140 * 0.95, 470 + 380 * 0.95), (bx - 120, by + 120)], CYAN, 2.5, 0.8 * kk)
        c.save()
        c.arc(bx, by, br * kk, 0, 2 * math.pi)
        c.set_source_rgba(*DARK, 0.97)
        c.fill_preserve()
        c.set_source_rgba(*CYAN, 1)
        c.set_line_width(5)
        c.stroke_preserve()
        c.clip()
        c.translate(bx - 140 * 1.2 * 0.0, by)
        for q in range(6):
            px = -105 + q * 42
            rrect(c, px, -26, 28, 50, 4)
            c.set_source_rgba(*CYAN, 0.95)
            c.fill()
        ln(c, [(-135, -48), (135, -48), (135, 48), (-135, 48)], CYAN, 4, 1, True)
        c.restore()
        txt(c, "CHIP", bx, by - br - 16, 34, CYAN, LBL, "c", kk)
    k = back(e(t, 1.0, 1.4))
    if k > 0:
        callout(c, 520, 860, 420, ["FITS THIS", "PRINTER ONLY"], CYAN, 1.0, 0.9 + 0.1 * k, 38)
    x0 = 70 + 170 * e(t, 1.3, 2.0)
    if t > 2.0:
        x0 -= 50 * e(t, 2.0, 2.4)
    cartridge(c, x0, 960, 0.5, 1.0, mirror=True, col=RED if t > 2.0 else WHITE)
    slot = 380
    rrect(c, slot, 940, 130, 230, 10)
    c.set_source_rgba(*WHITE, 0.6)
    c.set_line_width(3.5)
    c.set_dash([14, 8])
    c.stroke()
    c.set_dash([])
    kx = back(e(t, 2.0, 2.35))
    if kx > 0:
        c.save()
        c.translate(445, 1055)
        c.scale(max(kx, 0.001), max(kx, 0.001))
        ln(c, [(-40, -40), (40, 40)], RED, 12)
        ln(c, [(40, -40), (-40, 40)], RED, 12)
        c.restore()
        txt(c, "NO FIT", 445, 1215, 40, RED, LBL, "c", kx)


def s_count(c, t, d):
    txt(c, "PAID ONCE.", VW / 2, 320, 112, WHITE, HEAD)
    txt(c, "REFILLED AGAIN.", VW / 2, 430, 112, YEL, HEAD)
    base, ax = 1065, 120
    ln(c, [(ax, base), (VW - 120, base)], WHITE, 4, 0.9)
    ph = 230
    c.rectangle(210, base - ph, 220, ph)
    c.set_source_rgba(*YEL, 0.9)
    c.fill()
    txt(c, "PRINTER", 320, base + 44, 32, WHITE, LBL)
    txt(c, "PAID ONCE", 320, base + 80, 26, YEL, LBL, "c", 0.85)
    line_y = base - ph
    ln(c, [(ax, line_y), (VW - 110, line_y)], YEL, 3, 0.9 * e(t, 0.4, 0.8), dash=[16, 10])
    txt(c, "PRINTER PRICE", VW - 120, line_y - 14, 28, YEL, LBL, "r", e(t, 0.4, 0.8))
    n = 0
    for k in range(7):
        t0 = 1.0 + k * 0.42
        kk = back(e(t, t0, t0 + 0.3))
        if kk <= 0:
            continue
        n = k + 1
        by = base - (k + 1) * 50
        c.save()
        c.translate(640 + 110, by + 25 - (1 - kk) * 60)
        c.scale(1, max(kk, 0.001))
        c.translate(-110, -25)
        c.rectangle(0, 0, 220, 46)
        past = (k + 1) * 50 > ph
        c.set_source_rgba(*(RED if past else CYAN), 0.92)
        c.fill()
        txt(c, "REFILL", 110, 33, 28, DARK, LBL)
        c.restore()
    txt(c, "INK SPENT", 750, base + 44, 32, WHITE, LBL)
    txt(c, "ILLUSTRATION", 750, base + 80, 26, WHITE, LBL, "c", 0.7)
    for lab, k in (("YEAR 1", 2), ("YEAR 2", 5)):
        yy = base - (k + 1) * 50 + 25
        ln(c, [(640 - 60, yy), (640 - 8, yy)], WHITE, 3, 0.9 * e(t, 1.0 + k * 0.42, 1.3 + k * 0.42))
        txt(c, lab, 640 - 70, yy + 9, 28, WHITE, LBL, "r", e(t, 1.0 + k * 0.42, 1.3 + k * 0.42))
    kc = back(e(t, 1.0 + 4 * 0.42, 1.0 + 4 * 0.42 + 0.4))
    if kc > 0:
        c.save()
        c.translate(540, 560)
        c.scale(max(kc, 0.001), max(kc, 0.001))
        rrect(c, -330, -48, 660, 96, 14)
        c.set_source_rgba(*RED, 1)
        c.fill()
        txt(c, "INK COST > PRINTER PRICE", 0, 18, 56, (1, 1, 1), HEAD)
        c.restore()
    txt(c, "MODERATE USE, PRINTER UNDER $200 · TECHLICIOUS", 80, 1195, 24, WHITE, LBL, "l", 0.7 * e(t, 0.6, 1.0))


def endcard(c, t):
    a = e(t, 0, 0.4)
    c.set_source_rgba(0.01, 0.06, 0.2, 0.985 * a)
    c.rectangle(0, 0, VW, VH)
    c.fill()
    logo(c, VW / 2 - 150, 520, 5.0, a)
    txt(c, "MONEY MAP", VW / 2, 970, 130, WHITE, HEAD, "c", a)
    txt(c, "WHY IS IT SO EXPENSIVE?", VW / 2, 1050, 44, CYAN, LBL, "c", e(t, 0.2, 0.6))
    txt(c, "NEXT: WHY IS LEGO SO EXPENSIVE?", VW / 2, 1130, 36, WHITE, LBL, "c", e(t, 0.4, 0.8))
    pill(c, VW / 2, 1240, 640, 100, GOLD, e(t, 0.5, 0.9))
    txt(c, "FOLLOW FOR EP. 2", VW / 2, 1262, 56, (0.05, 0.08, 0.2), HEAD, "c", e(t, 0.5, 0.9))


def s_close(c, t, d):
    cartridge(c, 410, 480, 0.92, 1.0)
    callout(c, 40, 600, 330, ["HP 962 BLACK", "^$40.22", "PER OUNCE"], YEL, 1.0, 1.0, 34, tip=(437, 753))
    k = back(e(t, 0.5, 0.9))
    if k > 0:
        c.save()
        c.translate(VW / 2, 325)
        c.rotate(-0.06)
        c.scale(max(k, 0.001), max(k, 0.001))
        rrect(c, -420, -130, 840, 260, 14)
        c.set_source_rgba(*DARK, 0.97)
        c.fill_preserve()
        c.set_source_rgba(*YEL, 1)
        c.set_line_width(8)
        c.stroke()
        rrect(c, -404, -114, 808, 228, 10)
        c.set_line_width(3)
        c.stroke()
        txt(c, "NOT JUST INK:", 0, -20, 96, WHITE, HEAD)
        txt(c, "A BUSINESS MODEL", 0, 76, 96, YEL, HEAD)
        c.restore()
    if t > d - 2.0:
        endcard(c, t - (d - 2.0))


SCENES = {"hook": s_hook, "printer": s_printer, "razor": s_razor, "chip": s_chip, "count": s_count, "close": s_close}


def draw(c, name, t, d, T, i):
    SCENES[name](c, t, d)


def cover(c):
    bg(c, 0.1)
    txt(c, "WHY IS INK", VW / 2, 420, 160, WHITE, HEAD, "c", 1.0, stroke=DARK, sw=14)
    txt(c, "SO EXPENSIVE?", VW / 2, 590, 160, YEL, HEAD, "c", 1.0, stroke=DARK, sw=14)
    cartridge(c, 342, 700, 1.35, 1.0)
    callout(c, 50, 1010, 330, ["HP 962 BLACK", "^$40.22", "PER OUNCE"], YEL, 1.0, 1.0, 34, tip=(342, 1130))
    dim(c, 780, 1062, 780, 1160, "ABOUT 0.9 OZ", off=0, col=CYAN, size=24)


def tone(mix, sr, t, f, dur, amp, dec):
    j = int(t * sr)
    m = int(dur * sr)
    if j < 0 or j + m > len(mix):
        return
    x = np.arange(m) / sr
    mix[j:j + m] += amp * np.sin(2 * np.pi * f * x) * np.exp(-x / dec)


def burst(mix, sr, rng, t, dur, amp, sweep=False):
    j = int(t * sr)
    m = int(dur * sr)
    if j < 0 or j + m > len(mix):
        return
    n = rng.randn(m)
    n = n - np.convolve(n, np.ones(9) / 9, mode="same")
    env = np.sin(np.pi * np.arange(m) / m) ** 1.5 if sweep else np.exp(-np.arange(m) / (0.05 * sr))
    mix[j:j + m] += n * env * amp


def sfx(tl, mix, sr, rng):
    S = [t for t, _ in tl]
    for t0 in S:
        burst(mix, sr, rng, t0 + 0.02, 0.35, 0.022, True)
    h = S[0]
    for k in range(14):
        tone(mix, sr, h + 0.1 + k * 0.14, 1500 + 40 * k, 0.05, 0.025, 0.015)
    tone(mix, sr, h + 2.3, 180, 0.3, 0.12, 0.08)
    p = S[1]
    tone(mix, sr, p + 1.25, 1200, 0.12, 0.05, 0.04)
    tone(mix, sr, p + 2.35, 1000, 0.12, 0.05, 0.04)
    tone(mix, sr, p + 3.5, 120, 0.4, 0.14, 0.1)
    r = S[2]
    for k in range(4):
        t0 = r + 1.4 + k * 0.5
        tone(mix, sr, t0, 520, 0.08, 0.06, 0.03)
        for f in (2400, 3100):
            tone(mix, sr, t0 + 0.25, f, 0.25, 0.03, 0.07)
    ch = S[3]
    tone(mix, sr, ch + 0.65, 1800, 0.06, 0.07, 0.02)
    tone(mix, sr, ch + 1.05, 900, 0.1, 0.05, 0.03)
    tone(mix, sr, ch + 2.0, 110, 0.35, 0.16, 0.08)
    burst(mix, sr, rng, ch + 2.0, 0.2, 0.05)
    tone(mix, sr, ch + 2.25, 90, 0.3, 0.05, 0.1)
    cn = S[4]
    for k in range(7):
        t0 = cn + 1.0 + k * 0.42
        tone(mix, sr, t0, 700 + 40 * k, 0.07, 0.05, 0.03)
        for f in (2600, 3300):
            tone(mix, sr, t0 + 0.04, f, 0.2, 0.025, 0.06)
    tone(mix, sr, cn + 1.0 + 4 * 0.42 + 0.3, 140, 0.4, 0.12, 0.09)
    cl = S[5]
    tone(mix, sr, cl + 0.55, 130, 0.4, 0.14, 0.09)
    end = cl + tl[5][1] - 2.0
    for f, dt in ((880, 0), (1320, 0.12)):
        tone(mix, sr, end + dt, f, 0.5, 0.05, 0.18)


if __name__ == "__main__":
    import sys
    wx_engine.main(sys.modules["__main__"])
