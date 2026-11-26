import cairo, math, json, os, sys, subprocess, random
import numpy as np

W, H, FPS = 1920, 1080, 30
HEAD = "Barlow Condensed"
BODY = "Barlow"

PAPER = (0.945, 0.953, 0.961)
GRID = (0.88, 0.90, 0.92)
PARK = (0.86, 0.93, 0.87)
WATER = (0.84, 0.90, 0.97)
INK = (0.106, 0.133, 0.188)
INK2 = (0.30, 0.34, 0.42)
RED = (0.886, 0.255, 0.180)
GREEN = (0.122, 0.639, 0.357)
BLUE = (0.184, 0.435, 0.871)
ORANGE = (0.949, 0.604, 0.122)
PURPLE = (0.541, 0.310, 0.788)
WHITE = (1, 1, 1)
GOLD = (0.89, 0.70, 0.25)
BOARD = (0.09, 0.10, 0.13)
AMBERT = (1.0, 0.78, 0.30)
STOPC = [INK, RED, BLUE, ORANGE, PURPLE, GREEN]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def e(t, a, b):
    return ease((t - a) / max(1e-6, b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def rr(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def txt(c, s, x, y, size, col, font=HEAD, align="l", alpha=1.0, bold=True):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.width / 2 + ex.x_bearing
    elif align == "r":
        x -= ex.width + ex.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, alpha)
    c.show_text(s)
    c.new_path()
    return ex.width


def tw(c, s, size, font=HEAD):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    return c.text_extents(s).width


random.seed(4)
STREETS = [(random.uniform(0, W), random.uniform(0, H), random.choice([0, 1])) for _ in range(26)]


def background(c):
    c.set_source_rgb(*PAPER)
    c.paint()
    c.set_source_rgb(*WATER)
    c.move_to(0, 860)
    c.curve_to(500, 800, 900, 980, 1400, 900)
    c.curve_to(1650, 860, 1800, 940, W, 900)
    c.line_to(W, H)
    c.line_to(0, H)
    c.close_path()
    c.fill()
    c.set_source_rgb(*PARK)
    rr(c, 1500, 120, 300, 180, 60)
    c.fill()
    rr(c, 120, 600, 220, 150, 50)
    c.fill()
    c.set_source_rgb(*GRID)
    c.set_line_width(6)
    for x, y, d in STREETS:
        if d:
            c.move_to(x, 0)
            c.line_to(x + 120, H)
        else:
            c.move_to(0, y)
            c.line_to(W, y - 80)
        c.stroke()


def station(c, x, y, r=22, col=INK, fill=WHITE, lw=9):
    c.new_path()
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgb(*fill)
    c.fill_preserve()
    c.set_line_width(lw)
    c.set_source_rgb(*col)
    c.stroke()


def logo(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(*GOLD, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    for p in pts[:-1]:
        c.arc(p[0], p[1], 7, 0, 2 * math.pi)
        c.set_source_rgba(0.98, 0.95, 0.86, a)
        c.fill_preserve()
        c.set_source_rgba(*GOLD, a)
        c.set_line_width(3)
        c.stroke()
    c.arc(60, 60, 13, 0, 2 * math.pi)
    c.set_source_rgba(*GREEN, a)
    c.fill()
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(4)
    c.move_to(54, 60)
    c.line_to(59, 65)
    c.line_to(67, 55)
    c.stroke()
    c.restore()


def chrome(c, stop):
    logo(c, 52, 34, 0.55)
    txt(c, "MONEY MAP", 100, 68, 34, INK)
    labels = ["START", "STOP 1", "STOP 2", "STOP 3", "STOP 4", "END"]
    x0 = W - 520
    c.set_source_rgb(*INK2)
    c.set_line_width(5)
    c.move_to(x0, 52)
    c.line_to(x0 + 450, 52)
    c.stroke()
    for i in range(6):
        x = x0 + i * 90
        on = i <= stop
        station(c, x, 52, 11 if i == stop else 8, STOPC[i] if on else INK2, STOPC[i] if i == stop else WHITE, 4)
    txt(c, labels[min(stop, 5)], x0 + 225, 98, 26, INK2, align="c")


def card(c, x, y, w, h, col=WHITE, shadow=True):
    if shadow:
        c.set_source_rgba(0, 0, 0, 0.10)
        rr(c, x + 6, y + 10, w, h, 22)
        c.fill()
    c.set_source_rgb(*col)
    rr(c, x, y, w, h, 22)
    c.fill()


def sign_plate(c, x, y, w, h, col, title, sub=None, a=1.0):
    c.push_group()
    card(c, x, y, w, h, BOARD)
    c.set_source_rgb(*col)
    rr(c, x, y, 34, h, 16)
    c.fill()
    c.rectangle(x + 18, y, 16, h)
    c.fill()
    if sub:
        txt(c, sub, x + 70, y + h * 0.38, h * 0.22, col)
        txt(c, title, x + 70, y + h * 0.80, h * 0.34, WHITE)
    else:
        txt(c, title, x + 70, y + h * 0.66, h * 0.42, WHITE)
    c.pop_group_to_source()
    c.paint_with_alpha(a)


def flap(c, s, x, y, size, col, t, align="l", seed=0):
    n = len(s)
    out = ""
    chars = "0123456789$.T-+"
    for i, ch in enumerate(s):
        k = t * 22 - i * 1.2
        if k >= 6 or ch == " ":
            out += ch
        elif k <= 0:
            out += " "
        else:
            out += chars[(int(k * 3) + i + seed) % len(chars)]
    return txt(c, out, x, y, size, col, align=align)


def token(c, x, y, label, col, size=40, r=None):
    w = tw(c, label, size) + 44
    h = size * 1.45
    c.set_source_rgba(0, 0, 0, 0.12)
    rr(c, x - w / 2 + 3, y - h / 2 + 6, w, h, h / 2)
    c.fill()
    c.set_source_rgb(*col)
    rr(c, x - w / 2, y - h / 2, w, h, h / 2)
    c.fill()
    txt(c, label, x, y + size * 0.36, size, WHITE, align="c")


def btc(c, x, y, size, col, a=1.0):
    txt(c, "B", x, y + size * 0.36, size, col, align="c", alpha=a)
    c.set_source_rgba(*col, a)
    c.set_line_width(size * 0.09)
    for dx in (-0.08, 0.1):
        c.move_to(x + dx * size, y - size * 0.5)
        c.line_to(x + dx * size, y - size * 0.36)
        c.move_to(x + dx * size, y + size * 0.36)
        c.line_to(x + dx * size, y + size * 0.5)
    c.stroke()


def coin(c, x, y, r, col=ORANGE, a=1.0):
    c.new_path()
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(*col, a)
    c.fill()
    c.arc(x, y, r * 0.78, 0, 2 * math.pi)
    c.set_source_rgba(1, 1, 1, 0.25 * a)
    c.set_line_width(r * 0.08)
    c.stroke()
    btc(c, x, y, r * 0.95, WHITE, a)


def stamp(c, x, y, s, col, k, size=90, ang=-0.12):
    if k <= 0:
        return
    sc = 1 + 0.6 * (1 - ease(k * 2))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(sc, sc)
    w = tw(c, s, size) + 60
    c.set_line_width(10)
    c.set_source_rgba(*col, min(1, k * 3))
    rr(c, -w / 2, -size * 0.75, w, size * 1.3, 18)
    c.stroke()
    txt(c, s, 0, size * 0.35, size, col, align="c", alpha=min(1, k * 3))
    c.restore()


def bigsay(c, lines, t, red=False, y0=None):
    n = len(lines)
    size = 118 if n <= 2 else 100
    gap = size * 1.08
    y = (y0 or (H / 2 - (n - 1) * gap / 2 + size * 0.35))
    for i, s in enumerate(lines):
        col = RED if (red and i == n - 1) else INK
        k = 1.0
        txt(c, s, W / 2, y + i * gap, size, col, align="c", alpha=k)


MAPX = [260, 560, 900, 1240, 1560, 1760]
MAPY = [560, 430, 640, 420, 620, 470]
STOP_NAMES = ["$1 TRILLION", "NEVER CASH", "EARLY SELLERS", "FORCED SELLERS", "PAID EITHER WAY", "END"]


def map_scene(c, t, p, first):
    at, done = p.get("at", 0), p.get("done", 0)
    reveal = p.get("reveal")
    recap = p.get("recap")
    prog = e(t, 0.0, 2.4) if reveal else 1.0
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    segs = len(MAPX) - 1
    total = prog * segs
    for i in range(segs):
        k = clamp(total - i)
        if k <= 0:
            break
        x0, y0, x1, y1 = MAPX[i], MAPY[i], MAPX[i + 1], MAPY[i + 1]
        mx = (x0 + x1) / 2
        c.set_source_rgb(*STOPC[i + 1])
        c.set_line_width(26)
        c.move_to(x0, y0)
        if k < 1:
            c.line_to(lerp(x0, x1, k), lerp(y0, y1, k))
        else:
            c.line_to(mx, y0)
            c.line_to(mx, y1)
            c.line_to(x1, y1)
        c.stroke()
    for i in range(len(MAPX)):
        if total < i - 0.05:
            break
        big = i == at
        station(c, MAPX[i], MAPY[i], 34 if big else 26, STOPC[i] if i else INK, WHITE, 12)
        if i <= done and i > 0:
            c.set_source_rgb(*GREEN)
            c.set_line_width(7)
            c.move_to(MAPX[i] - 12, MAPY[i])
            c.line_to(MAPX[i] - 3, MAPY[i] + 9)
            c.line_to(MAPX[i] + 13, MAPY[i] - 9)
            c.stroke()
        lab = STOP_NAMES[i] if i else "START"
        hi = recap is not None and i == recap
        above = MAPY[i] < 520
        ly = MAPY[i] - 70 if above else MAPY[i] + 98
        col = STOPC[i] if (hi or big) else INK2
        txt(c, ("STOP %d" % i) if 0 < i < 5 else ("" if i == 5 else ""), MAPX[i], ly - 40, 30, col, align="c")
        txt(c, lab, MAPX[i], ly, 44 if (hi or big) else 36, INK if (hi or big) else INK2, align="c")
    if not reveal:
        prev = max(0, at - 1) if not first else at
        k = e(t, 0.2, 2.2)
        xa, ya, xb, yb = MAPX[prev], MAPY[prev], MAPX[at], MAPY[at]
        x, y = lerp(xa, xb, k), lerp(ya, yb, k)
        if prev != at:
            mx = (xa + xb) / 2
            d1 = abs(mx - xa)
            d2 = abs(yb - ya)
            d3 = abs(xb - mx)
            L_ = d1 + d2 + d3
            s = k * L_
            if s < d1:
                x, y = xa + math.copysign(s, mx - xa), ya
            elif s < d1 + d2:
                x, y = mx, ya + math.copysign(s - d1, yb - ya)
            else:
                x, y = mx + math.copysign(s - d1 - d2, xb - mx), yb
        rr(c, x - 46, y - 30, 92, 60, 22)
        c.set_source_rgb(*INK)
        c.fill()
        txt(c, "$", x, y + 16, 44, AMBERT, align="c")
    if recap is not None and recap > 0:
        tips = {1: "MOST OF IT: A PRICE, NOT CASH", 2: "SOLD BEFORE THE DROP, FUND EXITS", 3: "$2B+ LIQUIDATED BETS", 4: "A FEE ON EVERY TRADE"}
        k = e(t, 0.1, 0.6)
        sign_plate(c, W / 2 - 560, 180, 1120, 110, STOPC[recap], tips[recap], a=k)
    if reveal:
        k = e(t, 2.0, 2.6)
        sign_plate(c, W / 2 - 360, 170, 720, 110, GREEN, "FOLLOW THE MONEY: 4 STOPS", a=k)


def hook_scene(c, t, p, gt):
    step = p["step"]
    card(c, 260, 200, 1400, 560, BOARD)
    txt(c, "ALL BITCOIN IN THE WORLD", 330, 290, 46, (0.6, 0.65, 0.72))
    tt = gt
    if tt < 1.0:
        txt(c, "$2.5 TRILLION", 330, 470, 170, AMBERT)
    else:
        flap(c, "$1.23 TRILLION", 330, 470, 170, AMBERT, (tt - 1.0) * 1.2, seed=3)
    k = e(gt, 2.6, 3.0)
    if k > 0:
        txt(c, "−$1.2 TRILLION", 330, 640, 110, RED, alpha=k)
    if step == 1:
        k2 = e(t, 0.0, 0.5)
        stamp(c, 1420, 640, "WHO GOT IT?", RED, k2, 72, -0.08)


def drop_scene(c, t, p):
    step = p["step"]
    x0, y0, x1, y1 = 420, 330, 1500, 770
    station(c, x0, y0, 30, RED, WHITE, 12)
    txt(c, "OCT 2025", x0, y0 - 110, 44, INK2, align="c")
    txt(c, "$126,000", x0, y0 - 52, 76, INK, align="c")
    if step >= 1:
        k = e(t, 0.0, 1.4)
        c.set_source_rgb(*RED)
        c.set_line_width(28)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(x0, y0)
        c.line_to(lerp(x0, x1, k), lerp(y0, y1, k))
        c.stroke()
        station(c, x0, y0, 30, RED, WHITE, 12)
        if k >= 1:
            station(c, x1, y1, 30, RED, WHITE, 12)
            txt(c, "NOV 2026", x1, y1 + 90, 44, INK2, align="c")
            txt(c, "$62,000", x1, y1 + 160, 76, INK, align="c")
            stamp(c, 1220, 420, "−51%", RED, e(t, 1.5, 1.9), 110)


def board_scene(c, t, p):
    rows = p["rows"]
    step = p["step"]
    x, y, w = 300, 180, 1320
    h = 170 + 150 * len(rows)
    card(c, x, y, w, h, BOARD)
    txt(c, p["title"], x + 60, y + 90, 52, (0.6, 0.65, 0.72))
    for i, (a, b) in enumerate(rows):
        yy = y + 210 + i * 150
        c.set_source_rgba(1, 1, 1, 0.06)
        rr(c, x + 40, yy - 85, w - 80, 120, 14)
        c.fill()
        if i < step:
            txt(c, a, x + 80, yy, 70, WHITE)
            txt(c, b, x + w - 80, yy, 90, AMBERT, align="r")
        elif i == step:
            flap(c, a, x + 80, yy, 70, WHITE, t)
            k = e(t, 0.4, 0.4)
            if t > 0.4:
                ww = tw(c, b, 90)
                flap(c, b, x + w - 80 - ww, yy, 90, AMBERT, t - 0.4, seed=i)


def say_scene(c, t, p):
    bigsay(c, p["lines"], t, p.get("red"))


def coins_scene(c, t, p):
    step = p["step"]
    cx = [360 + i * 133 for i in range(10)]
    cy = 520
    sold = step >= 4
    for i in range(10):
        x, y = cx[i], cy
        if i == 9 and sold:
            k = e(t, 0.0, 1.0) if step == 4 else 1
            x = lerp(cx[9], 1700, k)
            y = lerp(cy, 330, k)
        a = 1.0 if (step >= 0) else 0
        kin = e(t, i * 0.06, i * 0.06 + 0.4) if step == 0 else 1
        coin(c, x, y + (1 - kin) * 40, 52, ORANGE, kin)
        if step >= 1:
            if step >= 5 and i < 9:
                lab = "$50"
                col = RED
            elif i == 9 and sold:
                lab = "$50"
                col = RED
            else:
                lab = "$100"
                col = INK
            kk = e(t, i * 0.05, i * 0.05 + 0.3) if step == 1 else 1
            if step == 5 and i < 9:
                kk2 = e(t, 0.2 + i * 0.08, 0.5 + i * 0.08)
                lab = "$100" if kk2 < 0.5 else "$50"
                col = INK if kk2 < 0.5 else RED
            txt(c, lab, x, y + 110, 42, col, align="c", alpha=kk)
        if step == 3 and i == 9:
            c.set_line_width(6)
            c.set_source_rgba(*RED, 0.5 + 0.5 * math.sin(t * 6))
            c.arc(x, y, 66, 0, 2 * math.pi)
            c.stroke()
    if sold:
        k = e(t, 0.3, 0.9) if step == 4 else 1
        token(c, 1700, 240, "SOLD FOR $50", RED, 38)
        sign_plate(c, 330, 170, 560, 100, RED, "LAST PRICE: $50", a=k)
    elif step >= 1:
        sign_plate(c, 330, 170, 560, 100, INK, "LAST PRICE: $100", a=e(t, 0.0, 0.4) if step == 1 else 1)
    if step >= 2:
        if step < 5:
            val = 1000
        elif step == 5:
            val = int(lerp(1000, 500, e(t, 0.2, 1.6)))
        else:
            val = 500
        card(c, 700, 760, 520, 150, WHITE)
        txt(c, "TOTAL VALUE", 960, 812, 34, INK2, align="c")
        txt(c, "$%s" % format(val, ","), 960, 885, 76, RED if val < 1000 else INK, align="c")
    if step >= 6:
        k = e(t, 0.0, 0.5)
        card(c, 180, 760, 440, 150, WHITE)
        txt(c, "VANISHED", 400, 812, 34, INK2, align="c", alpha=k)
        txt(c, "$500", 400, 885, 76, RED, align="c", alpha=k)
        k2 = e(t, 1.6, 2.1)
        card(c, 1300, 760, 440, 150, WHITE)
        txt(c, "CHANGED HANDS", 1520, 812, 34, INK2, align="c", alpha=k2)
        txt(c, "$50", 1520, 885, 76, GREEN, align="c", alpha=k2)


def formula_scene(c, t, p):
    step = p["step"]
    txt(c, "MARKET VALUE", W / 2, 330, 120, INK, align="c")
    txt(c, "=", W / 2, 450, 90, INK2, align="c")
    txt(c, "LAST PRICE  ×  EVERY COIN", W / 2, 570, 96, BLUE, align="c")
    if step == 1:
        k = e(t, 0.4, 0.8)
        cx, cy = W / 2, 800
        card(c, cx - 170, cy - 110, 340, 200, WHITE)
        c.set_source_rgba(*INK2, k)
        rr(c, cx - 110, cy - 70, 220, 130, 16)
        c.set_line_width(8)
        c.stroke()
        c.arc(cx, cy - 5, 34, 0, 2 * math.pi)
        c.stroke()
        c.set_source_rgba(*RED, k)
        c.set_line_width(14)
        c.move_to(cx - 150, cy - 95)
        c.line_to(cx + 150, cy + 75)
        c.stroke()
        txt(c, "NOT CASH IN A VAULT", cx, cy + 160, 44, RED, align="c", alpha=k)
    if step >= 2:
        k = e(t, 0.2, 0.7) if step == 2 else 1
        if step == 3:
            price = lerp(126000, 62000, e(t, 0.3, 2.5))
        else:
            price = 64600
        val = price * 19.95e6 / 1e12
        txt(c, "$%s  ×  ~20 MILLION" % format(int(price), ","), W / 2, 720, 76, INK, align="c", alpha=k)
        txt(c, "= $%.2f TRILLION" % val, W / 2, 840, 96, RED if step == 3 else INK, align="c", alpha=k)


def trade_scene(c, t, p):
    step = p["step"]
    xa, xb, y = 520, 1400, 560
    c.set_line_width(26)
    c.set_source_rgb(*BLUE)
    c.move_to(xa, y)
    c.line_to(xb, y)
    c.stroke()
    station(c, xa, y, 60, BLUE, WHITE, 14)
    station(c, xb, y, 60, BLUE, WHITE, 14)
    txt(c, "SELLER", xa, y + 140, 60, INK, align="c")
    txt(c, "BUYER", xb, y + 140, 60, INK, align="c")
    k = (t * 0.45) % 1 if step < 2 else 1
    coin(c, lerp(xa, xb, k), y - 70, 40)
    token(c, lerp(xb, xa, k), y + 60, "$126,000" if step >= 1 else "$", GREEN, 36)
    if step >= 2:
        for i in range(4):
            c.set_source_rgb(*GREEN)
            rr(c, xa - 70, y - 230 - i * 34, 140, 28, 6)
            c.fill()
        stamp(c, xa, y - 330, "KEPT", GREEN, e(t, 0.2, 0.6) if step == 2 else 1, 70)
    if step >= 3:
        sign_plate(c, W / 2 - 520, 170, 1040, 100, GREEN, "ALREADY IN SOMEONE ELSE'S ACCOUNT", a=e(t, 0, 0.4))


def etf_scene(c, t, p):
    step = p["step"]
    nodes = [(420, "YOUR BROKER APP"), (960, "BITCOIN ETF"), (1500, "BITCOIN")]
    y = 560
    c.set_line_width(22)
    c.set_source_rgb(*PURPLE)
    c.move_to(420, y)
    c.line_to(1500, y)
    c.stroke()
    for x, n in nodes:
        station(c, x, y, 56, PURPLE, WHITE, 13)
        txt(c, n, x, y + 130, 50, INK, align="c")
    coin(c, 1500, y, 34)
    txt(c, "$", 420, y + 20, 56, GREEN, align="c")
    txt(c, "FUND", 960, y + 16, 40, PURPLE, align="c")
    if step == 0:
        k = (t * 0.4) % 1
        token(c, lerp(420, 1500, k), y - 90, "$ IN", GREEN, 36)
    else:
        k = (t * 0.4) % 1
        coin(c, lerp(1500, 960, min(1, k * 2)), y - 90, 30, ORANGE, 1 - max(0, k * 2 - 1))
        token(c, lerp(960, 420, k), y + 230 - 160, "$ BACK TO YOU", GREEN, 34)
        txt(c, "FUND SELLS BITCOIN", 1230, y - 150, 40, RED, align="c")
    if step == 2:
        sign_plate(c, W / 2 - 440, 170, 880, 100, GREEN, "REAL DOLLARS, PAID OUT", a=e(t, 0, 0.4))


def bars_scene(c, t, p):
    step = p["step"]
    txt(c, "$1.91 BILLION", W / 2, 330, 170, RED, align="c")
    txt(c, "PULLED OUT OF US SPOT BITCOIN ETFs, NOV 5 TO 13", W / 2, 410, 48, INK2, align="c")
    days = ["5", "6", "9", "10", "11", "12", "13"]
    hs = [0.6, 0.8, 0.5, 0.9, 0.7, 1.0, 0.75]
    for i in range(7):
        k = e(t, 0.3 + i * 0.25, 0.6 + i * 0.25) if step == 1 else (0.25 if step == 0 else 1)
        x = 520 + i * 135
        h = 260 * hs[i] * k
        c.set_source_rgb(*RED)
        rr(c, x, 520, 90, max(4, h), 10)
        c.fill()
        txt(c, "NOV " + days[i], x + 45, 860, 32, INK2, align="c")
    if step == 1:
        txt(c, "7 TRADING DAYS IN A ROW", W / 2, 950, 60, INK, align="c", alpha=e(t, 1.9, 2.3))
    txt(c, "(bar heights illustrative)", W - 60, H - 30, 22, INK2, font=BODY, align="r", bold=False)


def bignum_scene(c, t, p):
    k = e(t, 0, 0.6)
    card(c, 260, 260, 1400, 520, BOARD)
    flap(c, p["num"], W / 2 - tw(c, p["num"], 200) / 2, 560, 200, RED, t)
    txt(c, p["sub"], W / 2, 690, 54, WHITE, align="c", alpha=e(t, 0.8, 1.2))


def lev_scene(c, t, p):
    step = p["step"]
    bx, by, bw, bh = 1240, 940, 440, 60
    own = 1
    borrowed = 9 if step >= 1 else 0
    extra = 1 if step in (3, 4) else 0
    n = own + borrowed + extra
    if step >= 5:
        n = 9
    for i in range(n):
        y = by - i * (bh + 8)
        if step >= 5:
            col = (0.62, 0.66, 0.72)
            lab = "BORROWED $1,000"
        elif i == 0:
            col = GREEN
            lab = "YOURS $1,000"
        elif i <= 9:
            col = (0.62, 0.66, 0.72)
            lab = "BORROWED $1,000"
        else:
            col = GREEN
            lab = "GAIN $1,000"
        if step == 4 and 1 <= i <= 9:
            col = (0.62, 0.66, 0.72)
            a = 1 - e(t, 0.3, 1.2)
        else:
            a = 1.0
        if step == 1 and i >= 1:
            a = e(t, 0.4 + i * 0.12, 0.6 + i * 0.12)
        c.push_group()
        rr(c, bx, y - bh, bw, bh, 10)
        c.set_source_rgb(*col)
        c.fill()
        txt(c, lab, bx + bw / 2, y - 16, 32, WHITE, align="c")
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    if step in (5, 6, 7, 8):
        y = by
        k = e(t, 0.0, 0.6) if step == 5 else 1
        c.set_source_rgba(*RED, 1 - k)
        rr(c, bx, y - bh, bw, bh, 10)
        c.fill()
    labels = {0: "YOU HAVE $1,000", 1: "BET: $10,000", 2: "10× LEVERAGE", 3: "BITCOIN +10%:  $11,000", 4: "PAY BACK $9,000: YOU HAVE $2,000",
              5: "BITCOIN −10%:  $9,000", 6: "$9,000 = THE LOAN", 7: "AUTO-SELL", 8: "YOUR $1,000: $0"}
    col = GREEN if step in (3, 4) else (RED if step >= 5 else INK)
    txt(c, labels[step], 160, 330, 84 if step != 4 else 64, col)
    if step >= 7:
        stamp(c, 620, 600, "LIQUIDATED", RED, e(t, 0.3, 0.7) if step == 7 else 1, 96)
    if step == 8:
        cx, cy = 620, 840
        c.set_source_rgb(*INK)
        c.arc(cx, cy, 70, 0, 2 * math.pi)
        c.set_line_width(10)
        c.stroke()
        a = t * 4
        c.move_to(cx, cy)
        c.line_to(cx + 50 * math.sin(a), cy - 50 * math.cos(a))
        c.stroke()
        txt(c, "SECONDS", cx, cy + 130, 44, INK2, align="c")


def split_scene(c, t, p):
    step = p["step"]
    sx, sy = 420, 560
    station(c, sx, sy, 70, RED, WHITE, 14)
    txt(c, "$1,000", sx, sy + 20, 52, RED, align="c")
    txt(c, "YOUR MARGIN", sx, sy + 150, 46, INK, align="c")
    dest = [(1460, 330, "TRADERS BETTING DOWN", BLUE), (1460, 580, "EXCHANGE: LIQUIDATION FEE", ORANGE), (1460, 830, "INSURANCE FUND", PURPLE)]
    for i, (x, y, lab, col) in enumerate(dest):
        if step < i + 1 and step != 0:
            continue
        if step == 0:
            a = 0.25
        else:
            a = 1
        mx = (sx + x) / 2
        c.push_group()
        c.set_source_rgb(*col)
        c.set_line_width(22)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(sx, sy)
        c.line_to(mx, sy)
        c.line_to(mx, y)
        c.line_to(x - 260, y)
        c.stroke()
        station(c, x - 260, y, 30, col, WHITE, 10)
        txt(c, lab, x - 210, y + 18, 54, INK)
        c.pop_group_to_source()
        c.paint_with_alpha(a)
        if step == i + 1:
            k = (t * 0.5) % 1
            token(c, lerp(sx, x - 260, k), lerp(sy, y, k), "$", GREEN, 34)
    if step == 0:
        txt(c, "?", 1100, 620, 200, RED, align="c")


def domino_scene(c, t, p):
    step = p["step"]
    n = 9
    x0, y0 = 300, 820
    fall_n = {0: 0, 1: 1, 2: 3, 3: 9, 4: 9}[step]
    for i in range(n):
        x = x0 + i * 150
        start = 0.2 + (i - (fall_n - (3 if step == 2 else 1 if step == 1 else 0))) * 0.35 if step in (1, 2) else 0.2 + i * 0.25
        if step == 4:
            ang = 1.1
        elif i < fall_n:
            ang = 1.1 * e(t, start, start + 0.35) if step != 4 else 1.1
        else:
            ang = 0
        c.save()
        c.translate(x + 50, y0)
        c.rotate(ang)
        rr(c, -50, -260, 50, 260, 10)
        c.set_source_rgb(*(RED if ang > 0.05 else INK))
        c.fill()
        c.arc(-25, -200, 9, 0, 2 * math.pi)
        c.arc(-25, -70, 9, 0, 2 * math.pi)
        c.set_source_rgb(*WHITE)
        c.fill()
        c.restore()
        if i < 9:
            txt(c, "SALE", x + 25, y0 + 60, 30, INK2, align="c")
    price = 70000 - [0, 600, 1800, 5200, 6000][step] * (e(t, 0.2, 2.5) if step in (1, 2, 3) else 1)
    card(c, 1360, 160, 460, 170, BOARD)
    txt(c, "BTC PRICE", 1590, 215, 36, (0.6, 0.65, 0.72), align="c")
    txt(c, "$%s" % format(int(price), ","), 1590, 300, 84, RED if step else AMBERT, align="c")
    if step == 4:
        sign_plate(c, 160, 170, 980, 100, RED, "NO BIG NEWS NEEDED", a=e(t, 0.2, 0.6))
    txt(c, "(illustration, not real prices)", W - 60, H - 30, 22, INK2, font=BODY, align="r", bold=False)


def vchart_scene(c, t, p):
    pts = [(300, 330), (700, 360), (1000, 800), (1300, 560), (1620, 520)]
    k = e(t, 0.2, 3.0)
    c.set_source_rgb(*RED)
    c.set_line_width(14)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*pts[0])
    total = k * (len(pts) - 1)
    for i in range(1, len(pts)):
        kk = clamp(total - (i - 1))
        if kk <= 0:
            break
        c.line_to(lerp(pts[i - 1][0], pts[i][0], kk), lerp(pts[i - 1][1], pts[i][1], kk))
    c.stroke()
    if total > 2:
        station(c, 1000, 800, 24, RED, WHITE, 10)
        token(c, 1000, 900, "~$61,000", RED, 44)
    if total > 3.6:
        station(c, 1620, 520, 24, GREEN, WHITE, 10)
        token(c, 1620, 430, "~$64,600", GREEN, 44)
    txt(c, "ONE DAY, NOV 2026: FLASH CRASH, THEN BOUNCE", W / 2, 220, 60, INK, align="c")
    txt(c, "(shape illustrative)", W - 60, H - 30, 22, INK2, font=BODY, align="r", bold=False)


def gauge_scene(c, t, p):
    cx, cy, r = W / 2, 760, 420
    cols = [RED, ORANGE, (0.9, 0.85, 0.3), (0.55, 0.8, 0.35), GREEN]
    for i in range(5):
        c.set_source_rgb(*cols[i])
        c.set_line_width(70)
        c.arc(cx, cy, r, math.pi + i * math.pi / 5 + 0.02, math.pi + (i + 1) * math.pi / 5 - 0.02)
        c.stroke()
    v = lerp(50, 10, e(t, 0.2, 2.0))
    a = math.pi + math.pi * v / 100
    c.set_source_rgb(*INK)
    c.set_line_width(16)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(cx, cy)
    c.line_to(cx + (r - 70) * math.cos(a), cy + (r - 70) * math.sin(a))
    c.stroke()
    c.arc(cx, cy, 30, 0, 2 * math.pi)
    c.fill()
    txt(c, "FEAR INDEX", cx, 230, 64, INK2, align="c")
    txt(c, "%d" % round(v), cx, cy - 110, 170, RED, align="c")
    txt(c, "EXTREME FEAR", cx, cy + 120, 80, RED, align="c", alpha=e(t, 2.0, 2.4))


def toll_scene(c, t, p):
    step = p["step"]
    y = 600
    c.set_source_rgb(*ORANGE)
    c.set_line_width(26)
    c.move_to(200, y)
    c.line_to(1720, y)
    c.stroke()
    card(c, 860, 300, 200, 420, BOARD)
    txt(c, "EXCHANGE", 960, 360, 40, WHITE, align="c")
    txt(c, "FEE", 960, 420, 40, AMBERT, align="c")
    labs = ["BUY", "SELL", "PANIC SELL", "BUY", "SELL"]
    spd = 0.35 if step < 2 else 0.8
    nt = 3 if step < 2 else 6
    fees = 0
    for i in range(nt):
        k = (t * spd + i / nt) % 1
        d = 1 if i % 2 == 0 else -1
        x = lerp(220, 1700, k) if d > 0 else lerp(1700, 220, k)
        yy = y - 60 if d > 0 else y + 60
        coin(c, x, yy, 30)
        if step >= 1:
            txt(c, labs[i % 5], x, yy - 48 if d > 0 else yy + 76, 30, INK2, align="c")
    fee = int(t * (40 if step < 2 else 160)) + [0, 120, 300, 900][step]
    card(c, 1360, 160, 460, 150, WHITE)
    txt(c, "FEES EARNED", 1590, 210, 34, INK2, align="c")
    txt(c, "$%s" % format(fee * 1000, ","), 1590, 285, 72, GREEN, align="c")
    if step == 2:
        sign_plate(c, 120, 160, 880, 100, ORANGE, "MORE TRADING = MORE FEES", a=e(t, 0, 0.4))
    if step == 3:
        sign_plate(c, 120, 160, 1000, 100, ORANGE, "+ INTEREST ON LOANS + LIQUIDATIONS", a=e(t, 0, 0.4))
    txt(c, "(counter illustrative)", W - 60, H - 30, 22, INK2, font=BODY, align="r", bold=False)


def short_scene(c, t, p):
    step = p["step"]
    pts = [(260, 330), (700, 420), (1100, 640), (1500, 820)]
    c.set_source_rgb(*RED)
    c.set_line_width(26)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(*pts[0])
    for q in pts[1:]:
        c.line_to(*q)
    c.stroke()
    txt(c, "PRICE FALLS", 260, 250, 60, RED)
    station(c, 1500, 820, 40, BLUE, WHITE, 12)
    txt(c, "SHORT SELLER", 1500, 930, 60, INK, align="c")
    txt(c, "BET ON DOWN", 1500, 990, 40, INK2, align="c")
    k = (t * 0.5) % 1
    token(c, lerp(260, 1500, k), lerp(330, 820, k) - 60, "$", GREEN, 40)
    if step == 1:
        sign_plate(c, 980, 180, 820, 100, BLUE, "EVERY LIQUIDATION: SOMEONE'S PROFIT", a=e(t, 0, 0.4))


def stable_scene(c, t, p):
    step = p["step"]
    c.set_source_rgba(*PURPLE, 0.08)
    rr(c, 120, 220, 1000, 700, 40)
    c.fill()
    c.set_source_rgb(*PURPLE)
    c.set_line_width(8)
    c.set_dash([30, 18])
    rr(c, 120, 220, 1000, 700, 40)
    c.stroke()
    c.set_dash([])
    txt(c, "CRYPTO", 620, 300, 70, PURPLE, align="c")
    txt(c, "ORDINARY BANKS", 1500, 300, 60, INK2, align="c")
    random.seed(9)
    nt = 12
    for i in range(nt):
        bx = 260 + (i % 4) * 230
        byy = 450 + (i // 4) * 160
        leaving = step >= 3 and i % 3 == 0 or (step == 2 and i % 4 == 0)
        k = e(t, 0.3 + i * 0.08, 1.3 + i * 0.08) if leaving else 0
        x = lerp(bx, 1500 + (i % 3) * 80, k)
        y = lerp(byy, 520 + (i % 3) * 120, k)
        c.arc(x, y, 50, 0, 2 * math.pi)
        c.set_source_rgb(*GREEN)
        c.fill()
        txt(c, "$1", x, y + 16, 44, WHITE, align="c")
    if step == 1:
        sign_plate(c, 1180, 420, 640, 110, GREEN, "STABLECOIN = $1 TOKEN", a=e(t, 0, 0.4))
    if step >= 2:
        card(c, 1200, 760, 620, 170, BOARD)
        txt(c, "30-DAY CHANGE", 1510, 815, 36, (0.6, 0.65, 0.72), align="c")
        txt(c, "−$14.2 BILLION", 1510, 900, 80, RED, align="c")


def why_scene(c, t, p):
    step = p["step"]
    items = [("STRONGER DOLLAR", "+ RATE-HIKE FEARS", BLUE), ("BIG FUNDS", "SELLING", PURPLE), ("BORROWED BETS", "CLOSED BY FORCE", ORANGE)]
    for i, (a, b, col) in enumerate(items):
        x = 170 + i * 540
        on = step >= i + 1
        k = 1.0 if (step > i + 1 or (step == i + 1 and t > 0.5)) else (e(t, 0, 0.5) if step == i + 1 else 0.0)
        card(c, x, 330, 480, 330, WHITE)
        c.set_source_rgb(*(col if on else (0.85, 0.87, 0.9)))
        rr(c, x, 330, 480, 70, 22)
        c.fill()
        c.rectangle(x, 370, 480, 30)
        c.fill()
        txt(c, str(i + 1), x + 240, 385, 56, WHITE, align="c")
        txt(c, a, x + 240, 500, 54, INK, align="c", alpha=max(0.15, k))
        txt(c, b, x + 240, 570, 44, col, align="c", alpha=max(0.15, k))
    if step == -1:
        txt(c, "WHY DID IT FALL?", W / 2, 230, 96, INK, align="c")
    elif step < 4:
        txt(c, "3 PRESSURES AT ONCE", W / 2, 230, 80, INK, align="c")
    if step == 4:
        k = e(t, 0.2, 0.7)
        sign_plate(c, W / 2 - 450, 760, 900, 120, RED, "6 LOSING WEEKS IN A ROW", a=k)
        txt(c, "3 PRESSURES AT ONCE", W / 2, 230, 80, INK, align="c")


def sign_scene(c, t, p):
    k = e(t, 0.0, 0.5)
    x = lerp(-1500, W / 2 - 700, k)
    col = STOPC[min(p["n"], 5)]
    sub = ("STOP %d" % p["n"]) if 0 < p["n"] < 5 else ("LAST STATION" if p["n"] == 5 else "BEFORE WE BOARD")
    sign_plate(c, x, 380, 1400, 280, col, p["title"], sub)


def end_scene(c, t, p):
    logo(c, W / 2 - 120, 300, 4.0, e(t, 0, 0.6))
    txt(c, "FOLLOW THE MONEY.", W / 2, 760, 120, INK, align="c", alpha=e(t, 0.3, 0.9))
    txt(c, "MONEY MAP", W / 2, 860, 54, GOLD, align="c", alpha=e(t, 0.6, 1.2))


SC = dict(why=why_scene, map=None, hook=None, drop=drop_scene, board=board_scene, say=say_scene, coins=coins_scene, formula=formula_scene,
          trade=trade_scene, etf=etf_scene, bars=bars_scene, bignum=bignum_scene, lev=lev_scene, split=split_scene,
          domino=domino_scene, vchart=vchart_scene, gauge=gauge_scene, toll=toll_scene, short=short_scene,
          stable=stable_scene, sign=sign_scene, end=end_scene)


def build_timeline(L, durs, gap=0.62):
    tl = []
    t = 0.15
    for i, ln in enumerate(L):
        d = ln.get("dur") or (durs[i] + gap)
        if i + 1 < len(L) and L[i + 1]["scene"] == "sign":
            d += 0.5
        if ln["scene"] == "end":
            d += 2.5
        tl.append((t, d))
        t += d
    return tl, t


def stop_of(L, i):
    n = 0
    for j in range(i + 1):
        if L[j]["scene"] == "sign":
            n = L[j]["p"]["n"]
    return n


def group_start(L, tl, i):
    j = i
    while j > 0 and L[j - 1]["scene"] == L[i]["scene"] and L[i]["scene"] in ("hook",):
        j -= 1
    return tl[j][0]


def draw(c, L, tl, T):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    if T < tl[0][0]:
        i = 0
    t0, d = tl[i]
    t = max(0.0, T - t0)
    ln = L[i]
    background(c)
    sc = ln["scene"]
    p = ln["p"]
    fade = e(t, 0, 0.25) if (i > 0 and L[i - 1]["scene"] != sc) else 1.0
    c.push_group()
    if sc == "map":
        first = i > 0 and L[i - 1]["scene"] == "sign"
        map_scene(c, t, p, False)
    elif sc == "hook":
        hook_scene(c, t, p, T)
    else:
        SC[sc](c, t, p)
    c.pop_group_to_source()
    c.paint_with_alpha(fade)
    if sc != "end":
        chrome(c, stop_of(L, i))


def render(mod, durs_path, out, part=None, nparts=1):
    import importlib
    C = importlib.import_module(mod)
    durs = json.load(open(durs_path))
    tl, total = build_timeline(C.L, durs)
    n = int(total * FPS)
    a, b = 0, n
    if part is not None:
        a, b = n * part // nparts, n * (part + 1) // nparts
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b):
        draw(c, C.L, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()


def stills(mod, durs_path, outdir, times):
    import importlib
    C = importlib.import_module(mod)
    durs = json.load(open(durs_path))
    tl, total = build_timeline(C.L, durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    os.makedirs(outdir, exist_ok=True)
    for T in times:
        draw(c, C.L, tl, T)
        surf.write_to_png(os.path.join(outdir, "f_%06.2f.png" % T))
    return tl, total


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
