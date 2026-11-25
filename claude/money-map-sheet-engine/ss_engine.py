import cairo, math, json, os, sys, subprocess
from ss_common import *

TAIL = 3.4
X0, Y0, CW_, CH_ = 72, 172, 150, 56


# ------------------------------------------------------------------ chrome
_BASE = {}


def base_surface():
    if "b" in _BASE:
        return _BASE["b"]
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.set_source_rgb(*PAPER)
    c.paint()
    c.set_source_rgb(*GRID)
    c.set_line_width(1.2)
    x = X0
    while x < W:
        c.move_to(x + 0.5, Y0)
        c.line_to(x + 0.5, 1018)
        x += CW_
    y = Y0
    while y < 1018:
        c.move_to(0, y + 0.5)
        c.line_to(W, y + 0.5)
        y += CH_
    c.stroke()
    box(c, 0, 132, W, 40, HDR)
    box(c, 0, 132, X0, 886, HDR)
    c.set_source_rgb(*GRID)
    c.set_line_width(1.2)
    for i in range(13):
        xx = X0 + i * CW_
        c.move_to(xx + 0.5, 132)
        c.line_to(xx + 0.5, 172)
        txt(c, chr(65 + i), xx + CW_ / 2, 160, 22, HDRT, BODY, "c")
    c.stroke()
    for j in range(15):
        yy = Y0 + j * CH_
        txt(c, str(j + 1), X0 / 2, yy + 36, 21, HDRT, BODY, "c")
    box(c, 0, 0, W, 64, NAVY)
    logo(c, 26, 14, 0.58)
    txt(c, "MONEY MAP", 82, 46, 30, WHITE, HEAD, "l")
    txt(c, "how-social-security-works", 960, 44, 26, (0.75, 0.79, 0.92), BODY, "c", bold=False)
    txt(c, "Follow the money.", W - 30, 44, 26, GOLD, BODY, "r")
    box(c, 0, 64, W, 68, WHITE)
    c.set_source_rgb(*GRID)
    c.set_line_width(2)
    c.move_to(0, 131)
    c.line_to(W, 131)
    c.stroke()
    box(c, 14, 76, 150, 44, PAPER, 1, 6, GRID, 2)
    txt(c, "fx", 196, 108, 30, SOFT, MONO, "c")
    box(c, 0, 1018, W, 62, HDR)
    _BASE["b"] = s
    return s


TABS = ["Start", "1 Money in", "2 Your record", "3 The formula", "4 Your age", "5 Raises", "6 The deposit", "Summary"]


def tabs(c, active, glow=0.0):
    x = 96
    for i, nm in enumerate(TABS):
        w = tw(c, nm, 26, BODY) + 56
        if i == active:
            box(c, x, 1018, w, 54, WHITE, 1, 0)
            box(c, x, 1018, w, 6, TEAL)
            txt(c, nm, x + w / 2, 1056, 26, INK, BODY, "c")
            if glow > 0:
                rr(c, x - 4, 1014, w + 8, 62, 6)
                c.set_source_rgba(*GOLD, glow)
                c.set_line_width(4)
                c.stroke()
        else:
            txt(c, nm, x + w / 2, 1056, 26, HDRT, BODY, "c", bold=False)
        x += w + 6


def fxbar(c, ref, formula, t):
    txt(c, ref, 89, 109, 28, INK, MONO, "c")
    n = int(len(formula) * e(t, 0.05, 0.05 + 0.035 * len(formula)))
    s = formula[:n]
    txt(c, s, 236, 109, 30, INK, MONO, "l", bold=False)
    if (t * 2) % 1 < 0.6:
        xx = 236 + tw(c, s, 30, MONO, False) + 3
        box(c, xx, 84, 3, 34, INK)


# ------------------------------------------------------------------ helpers
def panel(c, x, y, w, h, title=None, a=1.0, col=WHITE):
    if a <= 0:
        return
    shadow(c, x, y, w, h, 8, 0.18 * a, 8)
    box(c, x, y, w, h, col, a, 8, GRID, 2)
    if title:
        rr(c, x, y, w, 52, 8)
        c.set_source_rgba(*HDR, a)
        c.fill()
        box(c, x, y + 44, w, 8, HDR, a)
        txt(c, title, x + 22, y + 37, 26, HDRT, BODY, "l", a)


def cell(c, x, y, w, h, s, tc=INK, fc=WHITE, a=1.0, size=44, f=BODY, sel=False, align="c", line_col=GRID):
    if a <= 0:
        return
    box(c, x, y, w, h, fc, a, 0, line_col, 2)
    if s:
        sz = fit(c, s, size, w - 24, f)
        if align == "c":
            txt(c, s, x + w / 2, y + h / 2 + sz * 0.36, sz, tc, f, "c", a)
        elif align == "l":
            txt(c, s, x + 18, y + h / 2 + sz * 0.36, sz, tc, f, "l", a)
        else:
            txt(c, s, x + w - 18, y + h / 2 + sz * 0.36, sz, tc, f, "r", a)
    if sel:
        selbox(c, x, y, w, h, a)


def selbox(c, x, y, w, h, a=1.0, col=GOLD):
    rr(c, x - 2, y - 2, w + 4, h + 4, 2)
    c.set_source_rgba(*col, a)
    c.set_line_width(5)
    c.stroke()
    box(c, x + w - 6, y + h - 6, 13, 13, col, a, 1, WHITE, 2)


def typed(s, k):
    return s[:int(round(len(s) * clamp(k)))]


def cnt(v0, v1, k, cents=False, pre="$"):
    v = lerp(v0, v1, ease(k))
    if cents:
        return pre + "{:,.2f}".format(v)
    return pre + "{:,.0f}".format(v)


def head(c, s, t, y=250, size=64, col=INK):
    txt(c, s, 960, y, size, col, HEAD, "c", e(t, 0, 0.4))


def note(c, s, a=1.0, y=992):
    txt(c, s, 1880, y, 24, SOFT, BODY, "r", a, bold=False)


def colchart(c, x, y, w, h, vals, cols, k, labels=None, vlabels=None, maxv=None, lsize=30, vsize=36):
    n = len(vals)
    maxv = maxv or max(vals)
    gw = w / n
    bw = gw * 0.62
    c.set_source_rgb(*GRID)
    c.set_line_width(2)
    c.move_to(x, y + h)
    c.line_to(x + w, y + h)
    c.stroke()
    for i, v in enumerate(vals):
        kk = clamp(k * n - i * 0.6) if n > 1 else k
        kk = ease(clamp(k * 1.6 - i * (0.6 / n)))
        bh = h * v / maxv * kk
        bx = x + i * gw + (gw - bw) / 2
        if bh > 0:
            box(c, bx, y + h - bh, bw, bh, cols[i] if isinstance(cols, list) else cols, 1, 4)
        if labels:
            txt(c, labels[i], bx + bw / 2, y + h + lsize + 8, lsize, SOFT, BODY, "c", min(1, kk * 3))
        if vlabels and kk > 0.95:
            txt(c, vlabels[i], bx + bw / 2, y + h - bh - 14, vsize, INK, HEAD, "c")


# ------------------------------------------------------------------ scenes
def two_dollars(c, t, x0=330, y0=330, big=True, a=1.0):
    for i, (pct, col, fc) in enumerate((("90¢", TEAL, TEAL_L), ("15¢", CORAL, CORAL_L))):
        x = x0 + i * 820
        k = back(e(t, 0.05 + i * 0.35, 0.45 + i * 0.35))
        if k <= 0:
            continue
        aa = clamp(k) * a
        cell(c, x, y0, 440, 110, "$1 EARNED", INK, WHITE, aa, 52, HEAD)
        arrow(c, x + 220, y0 + 120, x + 220, y0 + 210, SOFT, 7, aa, e(t, 0.3 + i * 0.35, 0.6 + i * 0.35))
        kk = e(t, 0.5 + i * 0.35, 0.8 + i * 0.35)
        cell(c, x, y0 + 220, 440, 190, pct, col, fc, kk * a, 140, HEAD, sel=(i == 0))
        txt(c, "COUNTS TOWARD YOUR CHECK", x + 220, y0 + 460, 30, SOFT, BODY, "c", kk * a)
    k = back(e(t, 1.0, 1.4))
    if k > 0:
        c.save()
        c.translate(960, y0 + 300)
        c.scale(clamp(k, 0, 1.3), clamp(k, 0, 1.3))
        circle(c, 0, 0, 105, GOLD, a)
        txt(c, "6x", 0, 34, 96, NAVY, HEAD, "c", a)
        c.restore()


def s_hook(c, t, p, gt, d):
    st = p["step"]
    if st == 0:
        box(c, 260, 196, 1400, 96, NAVY, 1, 10)
        q = "WHY DO SOME DOLLARS COUNT 6x MORE?"
        txt(c, q, 960, 262, fit(c, q, 56, 1340, HEAD), WHITE, HEAD, "c")
        two_dollars(c, gt)
    elif st == 1:
        a = 1 - e(t, 0, 0.4)
        if a > 0:
            two_dollars(c, 9, a=a)
        k = back(e(t, 0.3, 0.9))
        if k > 0:
            check_paper(c, 360, 300 + (1 - clamp(k)) * 200, 1200, 420, "$?,???.??", clamp(k), -0.02)
        txt(c, "YOUR SOCIAL SECURITY CHECK", 960, 860, 54, INK, HEAD, "c", e(t, 0.8, 1.2))
    elif st == 2:
        cell(c, 560, 230, 800, 70, "BENEFICIARIES, JAN 2027", HDRT, HDR, e(t, 0, 0.3), 32)
        k = e(t, 0.2, 1.6)
        cell(c, 560, 300, 800, 170, cnt(0, 72, k, pre="") + ",000,000", INK, WHITE, e(t, 0.1, 0.3), 110, HEAD, sel=True)
        txt(c, "NEARLY", 520, 400, 40, SOFT, BODY, "r", e(t, 0.1, 0.3))
        for i in range(24):
            kk = back(e(t, 0.6 + i * 0.05, 1.0 + i * 0.05))
            if kk > 0:
                elder(c, 210 + i * 64, 700 + (1 - clamp(kk)) * 30, 0.9, (0.55, 0.60, 0.75), clamp(kk))
        k2 = e(t, d * 0.55, d * 0.55 + 0.5)
        box(c, 610, 820, 700, 90, GOLD_L, k2, 10, GOLD, 3)
        txt(c, "=SAME_FORMULA()", 960, 880, 50, INK, MONO, "c", k2)
    else:
        rows = ["PAY IN", "CREDITS", "AVERAGE EARNINGS", "THE FORMULA", "CLAIMING AGE", "YEARLY RAISE", "MEDICARE PART B"]
        panel(c, 460, 200, 1000, 760, "WORKSHEET: ONE SOCIAL SECURITY CHECK", e(t, 0, 0.3))
        for i, r in enumerate(rows):
            k = e(t, 0.3 + i * 0.18, 0.6 + i * 0.18)
            cell(c, 490, 268 + i * 82, 600, 74, r, INK, WHITE, k, 36, BODY, align="l")
            cell(c, 1090, 268 + i * 82, 340, 74, "?", SOFT, PAPER, k, 44, HEAD)
        k = e(t, 2.0, 2.4)
        cell(c, 490, 268 + 7 * 82 + 10, 600, 80, "LANDS IN YOUR BANK", WHITE, NAVY, k, 38, HEAD, align="l")
        cell(c, 1090, 268 + 7 * 82 + 10, 340, 80, "$?,???", NAVY, GOLD_L, k, 48, HEAD, sel=True)


def stub(c, a=1.0, rows=2, medicare=False):
    panel(c, 220, 220, 900, 560, "PAY STUB (EXAMPLE)", a)
    cell(c, 250, 290, 520, 80, "GROSS PAY, MONTH", INK, WHITE, a, 36, BODY, align="l")
    cell(c, 770, 290, 320, 80, "$5,000.00", INK, WHITE, a, 42, MONO)
    if rows >= 2:
        cell(c, 250, 370, 520, 80, "SOCIAL SECURITY 6.2%", INK, CORAL_L, a, 36, BODY, align="l")
        cell(c, 770, 370, 320, 80, "-$310.00", CORAL, CORAL_L, a, 42, MONO)
    if medicare:
        cell(c, 250, 450, 520, 80, "MEDICARE 1.45%", INK, VIOLET_L, a, 36, BODY, align="l")
        cell(c, 770, 450, 320, 80, "-$72.50", VIOLET, VIOLET_L, a, 42, MONO)


def s_pay(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        a = e(t, 0, 0.3)
        panel(c, 420, 220, 1080, 600, "PAY STUB (EXAMPLE, $60,000 A YEAR)", a)
        cell(c, 450, 300, 640, 100, "GROSS PAY, MONTH", INK, WHITE, a, 44, BODY, align="l")
        cell(c, 1090, 300, 380, 100, "$5,000.00", INK, WHITE, a, 52, MONO)
        k = e(f, 0.4, 0.6)
        cell(c, 450, 400, 640, 100, "SOCIAL SECURITY 6.2%", INK, CORAL_L, k, 44, BODY, align="l")
        cell(c, 1090, 400, 380, 100, cnt(0, -310, e(f, 0.5, 0.8), True).replace("$-", "-$"), CORAL, CORAL_L, k, 52, MONO, sel=k > 0.9)
        txt(c, "$310 A MONTH FROM YOU", 960, 640, 58, CORAL, HEAD, "c", e(f, 0.75, 0.9))
    elif st == 1:
        a = 1.0
        cell(c, 260, 300, 420, 90, "YOU PAY", INK, HDR, a, 40, HEAD)
        cell(c, 260, 390, 420, 160, "$310", CORAL, CORAL_L, a, 100, HEAD)
        txt(c, "+", 760, 500, 110, SOFT, HEAD, "c", e(t, 0.2, 0.5))
        k = e(t, 0.4, 0.8)
        cell(c, 840, 300, 420, 90, "EMPLOYER PAYS", INK, HDR, k, 40, HEAD)
        cell(c, 840, 390, 420, 160, "$310", CORAL, CORAL_L, k, 100, HEAD)
        txt(c, "=", 1340, 500, 110, SOFT, HEAD, "c", e(t, 0.8, 1.1))
        k2 = back(e(t, 1.0, 1.5))
        cell(c, 1420, 300, 420, 90, "12.4% TOTAL", WHITE, NAVY, clamp(k2), 40, HEAD)
        cell(c, 1420, 390, 420, 160, "$620", NAVY, GOLD_L, clamp(k2), 100, HEAD, sel=True)
        k3 = e(f, 0.62, 0.78)
        if k3 > 0:
            panel(c, 560, 650, 800, 240, None, k3)
            person(c, 700, 790, 1.4, NAVY, k3)
            txt(c, "SELF-EMPLOYED?", 790, 740, 46, INK, HEAD, "l", k3)
            txt(c, "YOU PAY BOTH HALVES", 790, 810, 44, CORAL, HEAD, "l", k3)
    elif st == 2:
        stub(c, 1.0, 2, True)
        k = back(e(t, 0.6, 1.1))
        if k > 0:
            box(c, 1180, 300, 560, 200, VIOLET_L, clamp(k), 12, VIOLET, 3)
            txt(c, "MEDICARE: 1.45%", 1460, 370, 44, VIOLET, HEAD, "c", clamp(k))
            txt(c, "YOU + EMPLOYER EACH", 1460, 430, 36, INK, BODY, "c", clamp(k))
        k2 = e(f, 0.55, 0.7)
        stamp(c, 1460, 640, "NO CEILING", VIOLET, k2, 72, -0.06)
    elif st == 3:
        head(c, "WHERE SOCIAL SECURITY TAX STOPS", t, 260, 56)
        x, y, w, h = 200, 420, 1520, 140
        mx = 250000.0
        cap = 192300 / mx * w
        k = e(t, 0.3, 1.6)
        box(c, x, y, w * k, h, TEAL_L, 1, 10, TEAL, 3)
        if k > cap / w:
            box(c, x + cap, y, (w * k - cap), h, (0.92, 0.92, 0.94), 1, 10, GREYB, 3)
        kk = e(f, 0.35, 0.5)
        line(c, [(x + cap, y - 40), (x + cap, y + h + 40)], CORAL, 6, kk)
        txt(c, "$192,300", x + cap, y - 60, 52, CORAL, HEAD, "c", kk)
        txt(c, "2027 CAP", x + cap, y + h + 90, 40, CORAL, HEAD, "c", kk)
        txt(c, "TAXED 6.2%", x + cap / 2, y + 90, 50, TEAL, HEAD, "c", e(t, 0.6, 1.0))
        txt(c, "NOT TAXED", x + cap + (w - cap) / 2, y + 90, 36, SOFT, HEAD, "c", e(f, 0.5, 0.7))
        for i, v in enumerate((0, 50000, 100000, 150000, 250000)):
            txt(c, "$%dK" % (v // 1000), x + v / mx * w, y + h + 50, 28, SOFT, BODY, "c", e(t, 0.3, 0.8), bold=False)
        txt(c, "(2026 cap: $184,500)", 960, 860, 34, SOFT, BODY, "c", e(f, 0.7, 0.9), bold=False)
    elif st == 4:
        k = e(t, 0, 0.3)
        cell(c, 460, 330, 1000, 130, "ACCOUNT: YOUR NAME", INK, WHITE, k, 64, HEAD)
        line(c, [(470, 395), (1450, 395)], CORAL, 12, 1, e(f, 0.45, 0.65))
        stamp(c, 960, 640, "NOT A SAVINGS ACCOUNT", CORAL, e(f, 0.55, 0.7), 70, -0.05)
    elif st == 5:
        for i in range(4):
            k = back(e(t, 0.1 + i * 0.1, 0.5 + i * 0.1))
            if k > 0:
                person(c, 260 + (i % 2) * 120, 400 + (i // 2) * 170, 1.3, TEAL, clamp(k))
        txt(c, "TODAY'S WORKERS", 320, 680, 40, TEAL, HEAD, "c", e(t, 0.3, 0.6))
        for j in range(4):
            kk = ((t * 0.7 + j * 0.25) % 1.0)
            if f > 0.12:
                coin(c, lerp(480, 1400, kk), 430 - math.sin(kk * math.pi) * 60, 26)
        arrow(c, 480, 480, 1400, 480, SOFT, 6, e(f, 0.05, 0.25))
        for i in range(4):
            k = back(e(t, 0.6 + i * 0.1, 1.0 + i * 0.1))
            if k > 0:
                elder(c, 1530 + (i % 2) * 120, 400 + (i // 2) * 170, 1.3, NAVY, clamp(k))
        txt(c, "TODAY'S CHECKS", 1590, 680, 40, NAVY, HEAD, "c", e(t, 0.8, 1.1))
        k = e(f, 0.55, 0.7)
        arrow(c, 940, 520, 940, 700, GOLD, 7, k)
        txt(c, "ANY EXTRA", 980, 620, 36, GOLD, HEAD, "l", k)
        k2 = e(f, 0.65, 0.85)
        cell(c, 640, 720, 600, 90, "TWO TRUST FUNDS", WHITE, NAVY, k2, 40, HEAD)
        cell(c, 640, 810, 600, 80, "LENT TO THE TREASURY", INK, GOLD_L, k2, 36, BODY, sel=k2 > 0.9)
    elif st == 6:
        head(c, "WHERE EACH SOCIAL SECURITY TAX DOLLAR GOES", t, 250, 50)
        n = int(e(t, 0.3, d * 0.75) * 100)
        for i in range(100):
            r, q = divmod(i, 10)
            x = 300 + q * 62
            y = 300 + r * 62
            col = TEAL if i < 85 else VIOLET
            if i < n:
                box(c, x, y, 56, 56, col, 1, 4)
            else:
                box(c, x, y, 56, 56, WHITE, 1, 4, GRID, 2)
        k = e(f, 0.3, 0.5)
        txt(c, "~85¢", 1300, 470, 120, TEAL, HEAD, "c", k)
        txt(c, "RETIREMENT AND SURVIVORS", 1300, 530, 38, INK, HEAD, "c", k)
        k2 = e(f, 0.7, 0.85)
        txt(c, "~15¢", 1300, 760, 120, VIOLET, HEAD, "c", k2)
        txt(c, "DISABILITY", 1300, 820, 38, INK, HEAD, "c", k2)
    else:
        head(c, "SOCIAL SECURITY'S INCOME, 2025", t, 260, 56)
        x, y, w, h = 200, 400, 1520, 170
        parts = [(91.3, TEAL, "PAYROLL TAXES ~91%"), (4.8, SKY, "INTEREST"), (3.9, VIOLET, "TAX ON BENEFITS")]
        xx = x
        k = e(t, 0.4, 1.6)
        for i, (v, col, lab) in enumerate(parts):
            ww = w * v / 100 * k
            box(c, xx, y, max(2, ww - 4), h, col, 1, 6)
            xx += ww
        txt(c, "PAYROLL TAXES: ABOUT 91%", x + w * 0.45, y + 105, 58, WHITE, HEAD, "c", e(t, 1.2, 1.6))
        k2 = e(f, 0.55, 0.7)
        arrow(c, 1560, 700, 1620, y + h + 10, SKY, 6, k2)
        txt(c, "INTEREST", 1520, 740, 40, SKY, HEAD, "r", k2)
        arrow(c, 1780, 780, 1700, y + h + 10, VIOLET, 6, e(f, 0.7, 0.85))
        txt(c, "TAXES ON BENEFITS", 1800, 830, 40, VIOLET, HEAD, "r", e(f, 0.7, 0.85))


def s_rec(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        head(c, "1 CREDIT = $1,970 EARNED (2027)", t, 260, 56)
        k = e(t, 0.6, d * 0.85)
        v = 7880 * k
        cell(c, 340, 360, 560, 80, "EARNINGS THIS YEAR", INK, HDR, 1, 36)
        cell(c, 340, 440, 560, 160, "${:,.0f}".format(v), INK, WHITE, 1, 90, MONO, sel=True)
        cell(c, 1020, 360, 560, 80, "CREDITS", INK, HDR, 1, 36)
        n = min(4, int(v // 1970 + 1e-6))
        for i in range(4):
            on = i < n
            box(c, 1040 + i * 132, 460, 116, 116, TEAL if on else WHITE, 1, 10, TEAL, 4)
            if on:
                line(c, [(1068 + i * 132, 518), (1092 + i * 132, 545), (1130 + i * 132, 490)], WHITE, 10)
        x, w = 340, 1240
        box(c, x, 700, w, 30, HDR, 1, 15)
        box(c, x, 700, w * k, 30, TEAL, 1, 15)
        for i in range(1, 5):
            xx = x + w * i / 4
            line(c, [(xx, 690), (xx, 740)], NAVY, 4)
            txt(c, "${:,}".format(1970 * i), xx, 790, 32, SOFT, BODY, "c")
        txt(c, "MAX 4 A YEAR", 960, 880, 46, NAVY, HEAD, "c", e(f, 0.8, 0.95))
    elif st == 1:
        head(c, "40 CREDITS TO QUALIFY", t, 250, 56)
        n = int(e(t, 0.4, d * 0.8) * 40 + 0.001)
        for r in range(10):
            txt(c, "YEAR %d" % (r + 1), 600, 330 + r * 66, 30, SOFT, BODY, "r", bold=False)
            for q in range(4):
                i = r * 4 + q
                x = 640 + q * 74
                on = i < n
                box(c, x, 296 + r * 66, 60, 54, TEAL if on else WHITE, 1, 6, TEAL, 3)
        k = e(f, 0.8, 0.9)
        cell(c, 1100, 520, 560, 160, "%d / 40" % n, NAVY, GOLD_L, 1, 96, HEAD, sel=True)
        stamp(c, 1380, 820, "QUALIFIED", TEAL, k, 76, -0.08)
    elif st == 2:
        cell(c, 260, 400, 560, 160, "QUALIFIED", WHITE, TEAL, e(t, 0, 0.3), 64, HEAD)
        arrow(c, 860, 480, 1060, 480, SOFT, 8, e(t, 0.4, 0.9))
        cell(c, 1100, 400, 560, 160, "AMOUNT = ?", NAVY, GOLD_L, e(t, 0.7, 1.0), 64, HEAD, sel=True)
        txt(c, "DEPENDS ON YOUR EARNINGS RECORD", 960, 700, 52, INK, HEAD, "c", e(f, 0.55, 0.75))
    elif st in (3, 4, 5):
        import random as _r
        rg = _r.Random(5)
        vals = [0.25 + 0.75 * (i / 40) ** 0.6 + rg.uniform(-0.12, 0.12) for i in range(40)]
        vals[1] = 0.12
        vals[3] = 0.15
        vals[39] = 0.10
        vals[38] = 0.30
        vals[0] = 0.14
        order = sorted(range(40), key=lambda i: vals[i])
        low = set(order[:5])
        x, y, w, h = 200, 330, 1520, 520
        gw = w / 40
        head(c, {3: "YOUR 35 HIGHEST YEARS COUNT", 4: "OLD YEARS ARE INDEXED", 5: "FEWER THAN 35? ZEROS"}[st], t, 260, 56)
        for i in range(40):
            v = vals[i]
            if st == 4 and i == 6:
                v = lerp(v, v * 2.1, e(f, 0.25, 0.6))
            bx = x + i * gw + 4
            k = 1.0 if st != 3 else e(t, 0.2 + i * 0.02, 0.5 + i * 0.02)
            if st == 5 and i >= 30:
                cell(c, bx - 2, y + h - 70, gw - 4, 70, "0", CORAL, CORAL_L, e(f, 0.3 + (i - 30) * 0.05, 0.4 + (i - 30) * 0.05), 34, HEAD)
                continue
            col = TEAL
            if st == 3 and i in low:
                col = GREYB if f > 0.45 else TEAL
            if st != 3 and i in low:
                col = GREYB
            if st == 4 and i == 6:
                col = GOLD
            bh = h * v * k
            box(c, bx, y + h - bh, gw - 8, bh, col, 1, 3)
        line(c, [(x, y + h), (x + w, y + h)], SOFT, 3)
        txt(c, "EACH BAR = ONE WORKING YEAR", x, y + h + 50, 30, SOFT, BODY, "l", bold=False)
        if st == 3:
            k = e(f, 0.5, 0.65)
            box(c, 220, 300, 520, 90, GREYB, k, 10)
            txt(c, "5 LOWEST: DROPPED", 480, 362, 40, WHITE, HEAD, "c", k)
        if st == 4:
            k = e(f, 0.2, 0.4)
            bx = x + 6 * gw
            box(c, bx - 60, 300, 360, 110, GOLD_L, k, 10, GOLD, 3)
            txt(c, "1990s PAY", bx + 120, 345, 34, INK, HEAD, "c", k)
            txt(c, "+ WAGE GROWTH", bx + 120, 392, 34, GOLD, HEAD, "c", k)
        if st == 5:
            box(c, 220, 300, 560, 90, CORAL_L, e(f, 0.5, 0.7), 10, CORAL, 3)
            txt(c, "5 MISSING YEARS = 0", 500, 360, 40, CORAL, HEAD, "c", e(f, 0.5, 0.7))
    elif st == 6:
        cell(c, 200, 330, 520, 80, "BEST 35 YEARS, ADDED", INK, HDR, 1, 34)
        cell(c, 200, 410, 520, 150, "SUM", INK, WHITE, 1, 80, HEAD)
        txt(c, "÷", 800, 515, 120, SOFT, "DejaVu Sans", "c", e(t, 0.4, 0.7))
        k = e(t, 0.6, 1.0)
        cell(c, 880, 330, 420, 80, "MONTHS", INK, HDR, k, 34)
        cell(c, 880, 410, 420, 150, "420", INK, WHITE, k, 90, HEAD)
        txt(c, "=", 1370, 510, 120, SOFT, HEAD, "c", e(f, 0.55, 0.7))
        k2 = back(e(f, 0.7, 0.85))
        cell(c, 1440, 330, 360, 80, "AIME", WHITE, NAVY, clamp(k2), 40, HEAD)
        cell(c, 1440, 410, 360, 150, "$ ?", NAVY, GOLD_L, clamp(k2), 90, HEAD, sel=True)
        txt(c, "AVERAGE INDEXED MONTHLY EARNINGS", 960, 720, 56, NAVY, HEAD, "c", e(f, 0.75, 0.9))
        txt(c, "35 YEARS x 12 MONTHS = 420", 960, 800, 36, SOFT, BODY, "c", e(t, 1.0, 1.4), bold=False)
    elif st == 7:
        cell(c, 660, 300, 600, 90, "AIME (EXAMPLE)", WHITE, NAVY, 1, 44, HEAD)
        k = e(t, 0.3, 1.4)
        cell(c, 660, 390, 600, 200, cnt(0, 5000, k), NAVY, GOLD_L, 1, 130, HEAD, sel=True)
        k2 = e(f, 0.55, 0.75)
        txt(c, "≈ $60,000 A YEAR", 960, 720, 66, TEAL, HEAD, "c", k2)
        txt(c, "IN TODAY'S MONEY", 960, 790, 40, SOFT, BODY, "c", k2)
    else:
        k = e(t, 0, 0.4)
        panel(c, 420, 230, 1080, 640, "YOUR EARNINGS RECORD", k)
        cell(c, 450, 300, 300, 66, "YEAR", HDRT, HDR, k, 30)
        cell(c, 750, 300, 720, 66, "TAXED SOCIAL SECURITY EARNINGS", HDRT, HDR, k, 30)
        for i in range(6):
            kk = e(t, 0.4 + i * 0.25, 0.7 + i * 0.25)
            cell(c, 450, 366 + i * 66, 300, 66, "20%02d" % (20 + i), INK, WHITE, kk, 32, MONO)
            cell(c, 750, 366 + i * 66, 720, 66, "$" + "{:,}".format(48000 + i * 2350), INK, WHITE, kk, 32, MONO)
        txt(c, "FREE ONLINE ACCOUNT AT SSA.GOV", 960, 820, 44, TEAL, HEAD, "c", e(f, 0.6, 0.8))
        note(c, "(sample rows, not a real record)", k)


BEND1, BEND2, XMAX = 1340, 8077, 10000


def slicebar(c, t, hl=-1, marker=True, a=1.0, y=430):
    x, w, h = 200, 1520, 150
    sc = w / XMAX
    k = e(t, 0.1, 1.0)
    segs = [(0, BEND1, TEAL, "90%"), (BEND1, BEND2, SKY, "32%"), (BEND2, XMAX, VIOLET, "15%")]
    for i, (a0, a1, col, pct) in enumerate(segs):
        kk = e(t, 0.1 + i * 0.25, 0.5 + i * 0.25)
        if kk <= 0:
            continue
        dim = 1.0 if (hl < 0 or hl == i) else 0.25
        box(c, x + a0 * sc + 3, y, (a1 - a0) * sc * kk - 6, h, col, a * dim, 8)
        if kk > 0.9:
            sz = 70 if (a1 - a0) * sc > 200 else 44
            txt(c, pct, x + (a0 + a1) / 2 * sc, y + h / 2 + sz * 0.36, sz, WHITE, HEAD, "c", a * dim)
    for b in (BEND1, BEND2):
        kk = e(t, 0.6, 1.0)
        line(c, [(x + b * sc, y - 30), (x + b * sc, y + h + 30)], NAVY, 4, a * kk, 1, [10, 8])
        txt(c, "${:,}".format(b), x + b * sc, y + h + 76, 40, NAVY, HEAD, "c", a * kk)
    txt(c, "$0", x, y + h + 76, 34, SOFT, BODY, "c", a * k)
    txt(c, "AIME", x + w, y + h + 76, 34, SOFT, BODY, "c", a * k)
    if marker:
        km = e(t, 1.0, 1.4)
        mx = x + 5000 * sc
        c.move_to(mx, y - 8)
        c.line_to(mx - 22, y - 48)
        c.line_to(mx + 22, y - 48)
        c.close_path()
        c.set_source_rgba(*GOLD, a * km)
        c.fill()
        txt(c, "YOUR $5,000", mx, y - 66, 40, INK, HEAD, "c", a * km)


def s_form(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        cell(c, 560, 360, 800, 180, "ONE FLAT %", INK, WHITE, e(t, 0, 0.3), 110, HEAD)
        line(c, [(580, 450), (1340, 450)], CORAL, 14, 1, e(f, 0.5, 0.7))
        stamp(c, 960, 720, "NOPE", CORAL, e(f, 0.55, 0.7), 90, -0.1)
    elif 1 <= st <= 4:
        head(c, "THE FORMULA: THREE SLICES", gt if st == 1 else 9, 260, 56)
        slicebar(c, gt if st == 1 else 9, hl=-1 if st == 1 else st - 2)
        if st >= 2:
            k = back(e(t, 0.2, 0.7))
            lab = {2: ("FIRST $1,340", "90%", TEAL), 3: ("$1,340 TO $8,077", "32%", SKY), 4: ("ABOVE $8,077", "15%", VIOLET)}[st]
            cell(c, 560, 760, 520, 120, lab[0], INK, WHITE, clamp(k), 44, HEAD)
            cell(c, 1080, 760, 280, 120, lab[1], WHITE, lab[2], clamp(k), 70, HEAD, sel=True)
        note(c, "Bend points for people first eligible (turning 62) in 2027")
    elif st == 5:
        two_dollars(c, t * 1.3, 330, 300)
    elif st in (6, 7):
        panel(c, 260, 220, 1400, 680, "EXAMPLE: AIME $5,000", 1)
        rows = [("90% x $1,340", "$1,206.00", TEAL), ("32% x $3,660", "$1,171.20", SKY), ("15% x $0", "$0.00", VIOLET)]
        for i, (a1, b1, col) in enumerate(rows):
            k = e(f if st == 6 else 9, 0.1 + i * 0.3, 0.3 + i * 0.3)
            cell(c, 300, 300 + i * 110, 120, 110, "", INK, col, k)
            cell(c, 420, 300 + i * 110, 700, 110, a1, INK, WHITE, k, 52, MONO, align="l")
            cell(c, 1120, 300 + i * 110, 500, 110, b1, INK, WHITE, k, 56, MONO, align="r")
        if st == 7:
            k = back(e(t, 0.3, 0.8))
            cell(c, 300, 650, 820, 140, "=SUM  (AT FULL RETIREMENT AGE)", WHITE, NAVY, clamp(k), 40, HEAD, align="l")
            cell(c, 1120, 650, 500, 140, cnt(0, 2377.2, e(t, 0.4, 1.6), True), NAVY, GOLD_L, clamp(k), 70, MONO, sel=True, align="r")
            txt(c, "PRIMARY INSURANCE AMOUNT", 960, 870, 44, NAVY, HEAD, "c", e(f, 0.55, 0.7))
    elif st in (8, 9):
        head(c, "SAME FORMULA, THREE EARNERS", t if st == 8 else 9, 250, 56)
        data = [("LOWER", 1340, 1206, 90, TEAL), ("EXAMPLE", 5000, 2377, 48, SKY), ("HIGHER", 10000, 3650, 37, VIOLET)]
        for i, (nm, aime, pia, pct, col) in enumerate(data):
            x = 260 + i * 480
            k = e(t if st == 8 else 9, 0.3 + i * 0.4, 0.8 + i * 0.4)
            cell(c, x, 310, 420, 70, nm + " EARNER", WHITE, col, k, 36, HEAD)
            cell(c, x, 380, 420, 80, "AIME ${:,}".format(aime), INK, WHITE, k, 40, MONO)
            cell(c, x, 460, 420, 80, "CHECK ${:,}".format(pia), INK, WHITE, k, 40, MONO)
            if st == 9:
                kk = e(t, 0.3 + i * 0.9, 1.2 + i * 0.9)
                bh = 300 * pct / 100 * kk
                box(c, x + 110, 900 - bh, 200, bh, col, 1, 6)
                if kk > 0.9:
                    txt(c, "%d%%" % pct, x + 210, 890 - bh - 10, 64, INK, HEAD, "c")
        if st == 9:
            line(c, [(240, 900), (1700, 900)], SOFT, 3)
            txt(c, "SHARE OF AVERAGE EARNINGS REPLACED", 960, 960, 34, SOFT, BODY, "c", e(t, 0.3, 0.7))
    else:
        cell(c, 560, 290, 800, 90, "MAXIMUM AT FULL RETIREMENT AGE", WHITE, NAVY, 1, 38, HEAD)
        cell(c, 560, 380, 800, 220, cnt(0, 4188, e(t, 0.4, 1.6)), NAVY, GOLD_L, 1, 140, HEAD, sel=True)
        txt(c, "A MONTH, 2027", 960, 680, 50, INK, HEAD, "c", e(t, 0.8, 1.2))
        txt(c, "NEEDS TOP EARNINGS FOR ABOUT 35 YEARS", 960, 780, 42, SOFT, BODY, "c", e(f, 0.5, 0.7))


def agebars(c, t, f, st):
    ages = [62, 63, 64, 65, 66, 67, 68, 69, 70]
    pct = [70, 75, 80, 86.7, 93.3, 100, 108, 116, 124]
    x, y, w, h = 240, 300, 1440, 520
    gw = w / 9
    base = h / 130
    for i, a in enumerate(ages):
        v = pct[i]
        show = 1.0
        if st == 0:
            v = 100
            show = e(t, 0.2 + i * 0.08, 0.5 + i * 0.08)
        elif st == 1:
            v = 100 if i != 0 else lerp(100, 70, e(f, 0.3, 0.6))
            if 0 < i < 5:
                v = lerp(100, pct[i], e(f, 0.6, 0.8))
            if i > 5:
                v = 100
        elif st == 2:
            if i > 5:
                v = lerp(100, pct[i], e(f, 0.2 + (i - 6) * 0.15, 0.4 + (i - 6) * 0.15))
        bh = base * v * show
        col = GOLD if a == 67 else (CORAL if a < 67 else TEAL)
        if st == 0:
            col = GOLD if a == 67 else GREYB
        box(c, x + i * gw + 18, y + h - bh, gw - 36, bh, col, 1, 6)
        txt(c, str(a), x + i * gw + gw / 2, y + h + 50, 40, INK, HEAD, "c", show)
        if st >= 1 and (i in (0, 5, 8)) and (st == 1 and i in (0, 5) or st == 2 and i in (5, 8)):
            txt(c, "%d%%" % round(v), x + i * gw + gw / 2, y + h - bh - 16, 40, INK, HEAD, "c")
    line(c, [(x, y + h), (x + w, y + h)], SOFT, 3)
    txt(c, "AGE YOU CLAIM", 960, y + h + 110, 32, SOFT, BODY, "c", bold=False)


def s_age(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st in (0, 1, 2):
        agebars(c, t, f, st)
        if st == 0:
            k = e(f, 0.5, 0.7)
            box(c, 1110, 210, 640, 76, GOLD_L, k, 10, GOLD, 3)
            txt(c, "FULL RETIREMENT AGE: 67", 1430, 262, 38, INK, HEAD, "c", k)
            txt(c, "(born 1960 or later)", 1430, 316, 30, SOFT, BODY, "c", k, bold=False)
        if st == 1:
            stamp(c, 600, 300, "-30% FOR LIFE", CORAL, e(f, 0.6, 0.75), 70, -0.06)
        if st == 2:
            stamp(c, 1320, 280, "+8% A YEAR", TEAL, e(f, 0.35, 0.5), 66, -0.06)
    elif st == 3:
        head(c, "SAME RECORD, THREE START AGES", t, 250, 56)
        colchart(c, 420, 320, 1080, 500, [1664, 2377, 2947], [CORAL, GOLD, TEAL], e(t, 0.3, 2.2), ["AT 62", "AT 67", "AT 70"], ["$1,664", "$2,377", "$2,947"], 3000, 40, 56)
        note(c, "Example (AIME $5,000), monthly, before yearly raises", 1, 1000)
    elif st == 4:
        head(c, "CLAIMED EARLY, STILL WORKING (2027)", t, 250, 52)
        cell(c, 300, 340, 620, 90, "EARNINGS LIMIT", INK, HDR, 1, 40)
        cell(c, 300, 430, 620, 160, "$25,560", NAVY, WHITE, 1, 100, HEAD, sel=True)
        k = e(f, 0.3, 0.5)
        cell(c, 1020, 340, 620, 90, "ABOVE THE LIMIT", INK, HDR, k, 40)
        for i in range(2):
            kk = back(e(f, 0.35 + i * 0.08, 0.5 + i * 0.08))
            if kk > 0:
                coin(c, 1130 + i * 110, 510, 46 * clamp(kk, 0, 1.2))
        txt(c, "EARN $2", 1180, 620, 44, TEAL, HEAD, "c", k)
        arrow(c, 1300, 510, 1420, 510, SOFT, 6, e(f, 0.5, 0.6))
        kk = back(e(f, 0.6, 0.72))
        if kk > 0:
            coin(c, 1520, 510, 46 * clamp(kk, 0, 1.2))
        txt(c, "$1 HELD BACK", 1520, 620, 44, CORAL, HEAD, "c", e(f, 0.6, 0.72))
        txt(c, "UNTIL THE YEAR YOU REACH FULL RETIREMENT AGE", 960, 780, 38, SOFT, BODY, "c", e(f, 0.75, 0.9))
        note(c, "Under full retirement age all year. Different limit in the year you reach it.", 1, 1000)
    elif st == 5:
        cx, cy = 960, 420
        tilt = 0.06 * math.sin(t * 1.6)
        line(c, [(cx, cy - 40), (cx, cy + 300)], NAVY, 10)
        box(c, cx - 140, cy + 300, 280, 24, NAVY, 1, 8)
        c.save()
        c.translate(cx, cy - 40)
        c.rotate(tilt)
        line(c, [(-520, 0), (520, 0)], NAVY, 10)
        for sgn, lab, sub, col in ((-1, "BIGGER CHECK", "CLAIM LATER", TEAL), (1, "MORE CHECKS", "CLAIM EARLIER", CORAL)):
            x = sgn * 480
            line(c, [(x, 0), (x - 100, 160)], SOFT, 3)
            line(c, [(x, 0), (x + 100, 160)], SOFT, 3)
            box(c, x - 210, 160, 420, 150, WHITE, 1, 10, col, 4)
            txt(c, lab, x, 230, 44, col, HEAD, "c")
            txt(c, sub, x, 280, 32, SOFT, BODY, "c")
        c.restore()
        txt(c, "A TRADE, NOT ONE RIGHT ANSWER", 960, 920, 50, INK, HEAD, "c", e(f, 0.5, 0.7))
    else:
        head(c, "COUPLES: THE SPOUSAL BENEFIT", t, 250, 56)
        x, y = 360, 360
        cell(c, x, y, 380, 80, "WORKER", WHITE, NAVY, 1, 40, HEAD)
        box(c, x + 420, y, 900 * e(t, 0.3, 1.2), 80, GOLD, 1, 8)
        txt(c, "FULL AMOUNT (100%)", x + 450, y + 54, 38, NAVY, HEAD, "l", e(t, 1.0, 1.3))
        k = e(f, 0.45, 0.6)
        cell(c, x, y + 160, 380, 80, "SPOUSE", WHITE, TEAL, k, 40, HEAD)
        box(c, x + 420, y + 160, 450 * e(f, 0.5, 0.75), 80, TEAL, 1, 8)
        line(c, [(x + 870, y + 130), (x + 870, y + 270)], CORAL, 5, e(f, 0.7, 0.8), 1, [10, 8])
        txt(c, "UP TO 50%", x + 900, y + 214, 44, TEAL, HEAD, "l", e(f, 0.7, 0.8))
        txt(c, "BASED ON THE WORKER'S RECORD", 960, 760, 44, SOFT, BODY, "c", e(f, 0.75, 0.9))


def s_cola(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        k = back(e(t, 0.1, 0.6))
        c.save()
        c.translate(960, 520)
        c.scale(clamp(k), clamp(k))
        box(c, -300, -260, 600, 500, WHITE, 1, 18, GRID, 3)
        box(c, -300, -260, 600, 120, CORAL, 1, 18)
        box(c, -300, -170, 600, 30, CORAL)
        txt(c, "JANUARY", 0, -180, 60, WHITE, HEAD, "c")
        txt(c, "RAISE", 0, 40, 110, NAVY, HEAD, "c")
        txt(c, "EVERY YEAR", 0, 140, 46, SOFT, BODY, "c")
        c.restore()
        txt(c, "COST-OF-LIVING ADJUSTMENT (COLA)", 960, 900, 46, INK, HEAD, "c", e(f, 0.6, 0.8))
    elif st == 1:
        cell(c, 560, 300, 800, 90, "2027 COLA", WHITE, NAVY, 1, 44, HEAD)
        cell(c, 560, 390, 800, 240, cnt(0, 3.6, e(t, 0.4, 1.5), True, pre="").rstrip("0").rstrip(".") + "%", TEAL, TEAL_L, 1, 170, HEAD, sel=True)
        txt(c, "FOLLOWS CPI-W: AN INFLATION INDEX FOR WORKERS", 960, 730, 40, SOFT, BODY, "c", e(f, 0.3, 0.6))
    elif st == 2:
        head(c, "COLA BY YEAR", t, 250, 56)
        colchart(c, 360, 320, 1200, 520, [8.7, 3.2, 2.5, 2.8, 3.6], [CORAL, SKY, SKY, SKY, TEAL], e(t, 0.2, 2.4), ["2023", "2024", "2025", "2026", "2027"], ["8.7%", "3.2%", "2.5%", "2.8%", "3.6%"], 9.5, 38, 50)
    elif st == 3:
        cell(c, 220, 330, 480, 80, "AVERAGE BEFORE", INK, HDR, 1, 36)
        cell(c, 220, 410, 480, 160, "$2,095", INK, WHITE, 1, 96, HEAD)
        txt(c, "x 1.036", 830, 470, 50, TEAL, HEAD, "c", e(t, 0.4, 0.8))
        arrow(c, 730, 520, 930, 520, SOFT, 6, e(t, 0.5, 0.9))
        k = e(f, 0.45, 0.6)
        cell(c, 960, 330, 480, 80, "AVERAGE AFTER", WHITE, NAVY, k, 36, HEAD)
        cell(c, 960, 410, 480, 160, cnt(2095, 2170, e(f, 0.5, 0.8)), NAVY, GOLD_L, k, 96, HEAD, sel=True)
        kk = back(e(f, 0.75, 0.88))
        if kk > 0:
            circle(c, 1640, 490, 150 * clamp(kk, 0, 1.1), TEAL)
            txt(c, "+$75", 1640, 515, 76, WHITE, HEAD, "c")
        note(c, "SSA estimate, all retired workers, January 2027", 1, 1000)
    else:
        head(c, "SAME 3.6%, DIFFERENT DOLLARS", t, 250, 56)
        for i, (b, r) in enumerate(((1000, 36), (2000, 72), (3000, 108))):
            x = 300 + i * 460
            k = e(t, 0.3 + i * 0.4, 0.7 + i * 0.4)
            cell(c, x, 340, 400, 90, "CHECK $%s" % "{:,}".format(b), INK, WHITE, k, 40, MONO)
            bh = r * 3.0 * e(t, 0.5 + i * 0.4, 1.0 + i * 0.4)
            box(c, x + 100, 900 - bh, 200, bh, TEAL, 1, 6)
            txt(c, "+$%d" % r, x + 200, 880 - bh, 56, TEAL, HEAD, "c", k)
        line(c, [(260, 900), (1660, 900)], SOFT, 3)
        note(c, "Illustration: 3.6% of each check, per month", 1, 1000)


def s_dep(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        check_paper(c, 180, 330, 800, 300, "$2,170.00", e(t, 0, 0.3), -0.02, memo="AVERAGE RETIRED WORKER, 2027")
        arrow(c, 1010, 480, 1260, 480, SOFT, 8, e(f, 0.3, 0.6))
        bank_icon(c, 1500, 470, 1.6, NAVY, e(f, 0.4, 0.6))
        cell(c, 1300, 640, 400, 110, "DEPOSIT ?", NAVY, GOLD_L, e(f, 0.5, 0.7), 52, HEAD, sel=True)
    elif st == 1:
        check_paper(c, 180, 330, 800, 300, "$2,170.00", 1, -0.02, memo="AVERAGE RETIRED WORKER, 2027")
        k = e(f, 0.3, 0.7)
        y = lerp(470, 760, ease_out(k))
        cell(c, 1100, y - 50, 640, 110, "MEDICARE PART B", WHITE, VIOLET, e(f, 0.2, 0.3), 50, HEAD)
        arrow(c, 980, 520, 1090, y, VIOLET, 6, e(f, 0.3, 0.6))
        txt(c, "TAKEN OUT BEFORE IT PAYS", 1420, y + 120, 36, VIOLET, HEAD, "c", e(f, 0.6, 0.8))
    elif st == 2:
        cell(c, 360, 320, 520, 90, "PART B, 2026", INK, HDR, 1, 40)
        cell(c, 360, 410, 520, 160, "$202.90", INK, WHITE, 1, 90, MONO)
        arrow(c, 900, 490, 1020, 490, SOFT, 6, e(t, 0.4, 0.8))
        k = e(t, 0.5, 0.9)
        cell(c, 1040, 320, 520, 90, "PART B, 2027", WHITE, VIOLET, k, 40, HEAD)
        cell(c, 1040, 410, 520, 160, "$209.40", VIOLET, VIOLET_L, k, 90, MONO, sel=True)
        stamp(c, 960, 760, "+$6.50 A MONTH", CORAL, e(f, 0.6, 0.75), 72, -0.05)
        note(c, "Standard monthly premium (CMS, 17 Nov 2026)", 1, 1000)
    elif st == 3:
        panel(c, 460, 240, 1000, 560, "THE DEPOSIT (AVERAGE, STANDARD PART B)", 1)
        rows = [("CHECK", "$2,170.00", INK, WHITE), ("PART B", "-$209.40", CORAL, CORAL_L)]
        for i, (a1, b1, col, fc) in enumerate(rows):
            k = e(f, 0.05 + i * 0.25, 0.2 + i * 0.25)
            cell(c, 500, 320 + i * 120, 440, 120, a1, INK, fc, k, 52, HEAD, align="l")
            cell(c, 940, 320 + i * 120, 480, 120, b1, col, fc, k, 60, MONO, align="r")
        k = back(e(f, 0.55, 0.7))
        cell(c, 500, 580, 440, 150, "LANDS IN BANK", WHITE, TEAL, clamp(k), 46, HEAD, align="l")
        cell(c, 940, 580, 480, 150, "$1,960.60", TEAL, TEAL_L, clamp(k), 70, MONO, sel=True, align="r")
        note(c, "Other deductions (tax withholding, other plans) vary by person", 1, 1000)
    elif st == 4:
        cell(c, 460, 330, 1000, 100, "BENEFIT THAT CAN BE TAXABLE", WHITE, NAVY, 1, 46, HEAD)
        k = e(t, 0.4, 1.4)
        box(c, 460, 470, 1000, 130, HDR, 1, 10)
        box(c, 460, 470, 1000 * 0.85 * k, 130, GOLD, 1, 10)
        txt(c, "UP TO 85%", 460 + 425, 560, 70, NAVY, HEAD, "c", e(t, 1.0, 1.4))
        txt(c, "DEPENDS ON YOUR OTHER INCOME", 960, 720, 50, SOFT, HEAD, "c", e(f, 0.5, 0.7))
    else:
        cell(c, 300, 340, 560, 100, "HIGHER INCOME", WHITE, NAVY, 1, 46, HEAD)
        arrow(c, 880, 390, 1040, 390, SOFT, 6, e(t, 0.3, 0.7))
        cell(c, 1060, 340, 560, 100, "HIGHER PART B", WHITE, VIOLET, e(t, 0.5, 0.9), 46, HEAD)
        k = e(f, 0.5, 0.7)
        box(c, 560, 560, 800, 160, GOLD_L, k, 12, GOLD, 3)
        txt(c, "BASED ON INCOME FROM", 960, 625, 44, INK, HEAD, "c", k)
        txt(c, "2 YEARS EARLIER", 960, 690, 54, GOLD, HEAD, "c", k)


def s_recap(c, t, p, gt, d):
    st = p["step"]
    if st == 0:
        rows = [("PAY IN", "6.2% + 6.2%"), ("CREDITS", "40"), ("AVERAGE EARNINGS", "BEST 35 YEARS"), ("THE FORMULA", "90 / 32 / 15"),
                ("CLAIMING AGE", "62 TO 70"), ("YEARLY RAISE", "+3.6%"), ("MEDICARE PART B", "-$209.40")]
        panel(c, 460, 200, 1000, 760, "WORKSHEET: ONE SOCIAL SECURITY CHECK", 1)
        n = len(rows)
        for i, (r, v) in enumerate(rows):
            k = e(t, 0.4 + i * (d - 2.2) / n, 0.8 + i * (d - 2.2) / n)
            cell(c, 490, 268 + i * 82, 600, 74, r, INK, WHITE, 1, 36, BODY, align="l")
            cell(c, 1090, 268 + i * 82, 340, 74, v if k > 0.2 else "?", TEAL if k > 0.2 else SOFT, TEAL_L if k > 0.2 else PAPER, 1, 40, HEAD, sel=(0.05 < k < 0.99))
        k = e(t, d - 1.4, d - 0.9)
        cell(c, 490, 268 + 7 * 82 + 10, 600, 80, "LANDS IN YOUR BANK", WHITE, NAVY, 1, 38, HEAD, align="l")
        cell(c, 1090, 268 + 7 * 82 + 10, 340, 80, "YOUR CHECK" if k > 0.5 else "$?,???", NAVY, GOLD_L, 1, 40, HEAD, sel=True)
    else:
        z = e(t, 0, d * 0.9)
        cols, rws = int(lerp(1, 14, z)), int(lerp(1, 8, z))
        sw = 1000 / max(1, cols) * lerp(1, 1.5, z)
        sh = sw * 0.76
        x0 = 960 - cols * sw / 2
        y0 = 590 - rws * sh / 2
        for j in range(rws):
            for i in range(cols):
                x, y = x0 + i * sw, y0 + j * sh
                box(c, x + sw * 0.06, y + sh * 0.06, sw * 0.88, sh * 0.88, WHITE, 1, max(1, sw * 0.04), GRID, 1)
                box(c, x + sw * 0.06, y + sh * 0.06, sw * 0.88, sh * 0.14, NAVY, 1, 0)
                box(c, x + sw * 0.5, y + sh * 0.72, sw * 0.36, sh * 0.12, GOLD, 1, 0)
        k = e(t, 1.0, 1.6)
        box(c, 410, 420, 1100, 240, NAVY, 0.95 * k, 16)
        txt(c, "NEARLY 72,000,000", 960, 540, 80, WHITE, HEAD, "c", k)
        txt(c, "CHECKS. ONE SHEET.", 960, 610, 46, GOLD, HEAD, "c", k)


def s_end(c, t, p, gt, d):
    box(c, 0, 0, W, H, NAVY)
    logo(c, 960 - 60 * 3.2, 170, 3.2, e(t, 0, 0.6))
    txt(c, "FOLLOW THE MONEY.", 960, 590, 120, WHITE, HEAD, "c", e(t, 0.3, 0.9))
    k = e(t, 1.0, 1.6)
    box(c, 260, 660, 1400, 130, WHITE, k, 14)
    txt(c, "NEXT: WHO PAYS FOR YOUR POINTS?", 960, 745, 60, NAVY, HEAD, "c", k)
    k2 = back(e(t, 2.0, 2.6))
    box(c, 960 - 170, 840, 340, 96, CORAL, clamp(k2), 48)
    txt(c, "FOLLOW", 960, 906, 58, WHITE, HEAD, "c", clamp(k2))


SC = dict(hook=s_hook, pay=s_pay, rec=s_rec, form=s_form, age=s_age, cola=s_cola, dep=s_dep, recap=s_recap, end=s_end)

FX = {
    ("hook", 0): ("B2", "=CHECK_VALUE($1)"), ("hook", 1): ("B3", "=YOUR_CHECK"), ("hook", 2): ("B4", "=COUNT(BENEFICIARIES)"), ("hook", 3): ("A1", "=BUILD(ONE_CHECK)"),
    ("pay", 0): ("C2", "=5000*6.2%"), ("pay", 1): ("C3", "=310+310"), ("pay", 2): ("C4", "=5000*1.45%"), ("pay", 3): ("C5", "=MIN(PAY,192300)*6.2%"),
    ("pay", 4): ("C6", "=ACCOUNT(\"YOUR NAME\")"), ("pay", 5): ("C7", "=TODAYS_WORKERS->TODAYS_CHECKS"), ("pay", 6): ("C8", "=5.3%/6.2%"), ("pay", 7): ("C9", "=PAYROLL/INCOME"),
    ("rec", 0): ("D2", "=FLOOR(EARNINGS/1970)"), ("rec", 1): ("D3", "=MIN(4,CREDITS)*10"), ("rec", 2): ("D4", "=IF(CREDITS>=40,\"IN\")"), ("rec", 3): ("D5", "=LARGE(YEARS,1..35)"),
    ("rec", 4): ("D6", "=PAY*WAGE_INDEX"), ("rec", 5): ("D7", "=IF(YEARS<35,0)"), ("rec", 6): ("D8", "=SUM(TOP35)/420"), ("rec", 7): ("D9", "=5000"), ("rec", 8): ("D10", "=RECORD(\"ssa.gov\")"),
    ("form", 0): ("E2", "=AIME*FLAT%"), ("form", 1): ("E3", "=SLICES(AIME,1340,8077)"), ("form", 2): ("E4", "=90%*MIN(AIME,1340)"), ("form", 3): ("E5", "=32%*(MIN(AIME,8077)-1340)"),
    ("form", 4): ("E6", "=15%*MAX(0,AIME-8077)"), ("form", 5): ("E7", "=90/15"), ("form", 6): ("E8", "=1206+1171.20"), ("form", 7): ("E9", "=SUM(E4:E6)"),
    ("form", 8): ("E10", "=PIA(1340;5000;10000)"), ("form", 9): ("E11", "=PIA/AIME"), ("form", 10): ("E12", "=MAX_PIA(2027)"),
    ("age", 0): ("F2", "=FRA(1960)"), ("age", 1): ("F3", "=PIA*70%"), ("age", 2): ("F4", "=PIA*(1+8%*YEARS)"), ("age", 3): ("F5", "=2377*{70%,100%,124%}"),
    ("age", 4): ("F6", "=(EARNED-25560)/2"), ("age", 5): ("F7", "=TRADE(SIZE,YEARS)"), ("age", 6): ("F8", "=PIA*50%"),
    ("cola", 0): ("G2", "=RAISE(JAN)"), ("cola", 1): ("G3", "=CPI_W(Q3)"), ("cola", 2): ("G4", "=COLA(2023:2027)"), ("cola", 3): ("G5", "=2095*1.036"), ("cola", 4): ("G6", "=CHECK*3.6%"),
    ("dep", 0): ("H2", "=2170"), ("dep", 1): ("H3", "=CHECK-PART_B"), ("dep", 2): ("H4", "=209.40-202.90"), ("dep", 3): ("H5", "=2170-209.40"), ("dep", 4): ("H6", "=UP_TO(85%)"), ("dep", 5): ("H7", "=IRMAA(INCOME-2Y)"),
    ("recap", 0): ("A1", "=WORKSHEET"), ("recap", 1): ("A1", "=72000000*SHEET"), ("end", 0): ("A1", "=FOLLOW_THE_MONEY()"),
}


# ------------------------------------------------------------------ timeline / render
def build_timeline(L, durs):
    tl = []
    t = 0.08
    for i, ln in enumerate(L):
        d = durs[i] + ln.get("gap", 0.45)
        if ln["scene"] == "end":
            d += TAIL
        tl.append((t, d))
        t += d
    return tl, t


def toast(c, n, title, t):
    k = e(t, 0, 0.4) * (1 - e(t, 3.0, 3.5))
    if k <= 0:
        return
    s = "SHEET %d  ·  %s" % (n, title)
    w = tw(c, s, 40, HEAD) + 90
    x = 960 - w / 2
    y = 930 + (1 - k) * 120
    shadow(c, x, y, w, 76, 38, 0.3 * k, 6)
    box(c, x, y, w, 76, TEAL, k, 38)
    txt(c, s, 960, y + 52, 40, WHITE, HEAD, "c", k)


def draw(c, L, tl, T):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0.0, T - t0)
    ln = L[i]
    g0 = i
    while g0 > 0 and L[g0 - 1]["scene"] == ln["scene"]:
        g0 -= 1
    gt = T - tl[g0][0]
    sc = ln["scene"]
    if sc == "end":
        s_end(c, t, ln["p"], gt, d)
        return
    c.set_source_surface(base_surface(), 0, 0)
    c.paint()
    new = i == 0 or L[i - 1]["scene"] != sc or L[i - 1]["p"]["step"] != ln["p"]["step"]
    fade = e(t, 0, 0.18) if (new and i > 0) else 1.0
    c.save()
    c.rectangle(0, 172, W, 846)
    c.clip()
    c.push_group()
    SC[sc](c, t, dict(ln["p"]), gt, d)
    c.pop_group_to_source()
    c.paint_with_alpha(fade)
    c.restore()
    ref, fx = FX.get((sc, ln["p"]["step"]), ("A1", ""))
    fxbar(c, ref, fx, t)
    act = 0
    lastch = None
    for j in range(i + 1):
        if "ch" in L[j]["p"]:
            act = L[j]["p"]["ch"]
            lastch = j
    if sc == "recap":
        act = 7
    glow = 0.0
    if lastch is not None and lastch == i:
        glow = e(t, 0, 0.3) * (1 - e(t, 1.5, 2.2))
    tabs(c, act, glow)
    if "ch" in ln["p"]:
        import ss_content as C
        toast(c, ln["p"]["ch"], C.CH[ln["p"]["ch"]], t)


def render(mod, vodir, out, part=0, nparts=1):
    import importlib
    C = importlib.import_module(mod)
    durs = json.load(open(os.path.join(vodir, "durs.json")))
    tl, total = build_timeline(C.L, durs)
    n = int(total * FPS)
    a, b = n * part // nparts, n * (part + 1) // nparts
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fr in range(a, b):
        draw(c, C.L, tl, fr / FPS)
        surf.flush()
        pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    pr.wait()


def stills(mod, vodir, outdir, mode="mid"):
    import importlib
    C = importlib.import_module(mod)
    durs = json.load(open(os.path.join(vodir, "durs.json")))
    tl, total = build_timeline(C.L, durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    os.makedirs(outdir, exist_ok=True)
    if mode == "mid":
        times = [a + d * 0.85 for a, d in tl]
    else:
        times = [float(x) for x in mode.split(",")]
    for k, T in enumerate(times):
        draw(c, C.L, tl, T)
        surf.write_to_png(os.path.join(outdir, "s%02d_%06.2f.png" % (k, T)))
    return tl, total


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
    elif cmd == "stills":
        tl, total = stills(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "mid")
        print("total", round(total, 1))
