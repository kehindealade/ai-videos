import cairo, math, json, os, sys, subprocess, random
import engine as E
from engine import txt, tw, rr, e, lerp, clamp, ease, coin, stamp, station, token, sign_plate, card, logo

VW, VH, FPS = 1080, 1920, 30

S1 = dict(voice="af_bella", speed=0.98, lines=[
    ("hook", "One person sold one coin, and five hundred dollars disappeared."),
    ("c0", "Here's how."),
    ("c1", "Ten people, ten coins. The last coin that traded sold for $100. So all ten are worth $1,000."),
    ("c2", "Now one person sells his coin for $50."),
    ("c3", "That's the new last price, so every coin is now worth $50."),
    ("c4", "Total: $500. But only $50 actually changed hands."),
    ("c5", "That's how bitcoin can lose a trillion dollars in value. Most of it was a price, not cash."),
    ("end", "The full story is on Money Map."),
])

S2 = dict(voice="af_sarah", speed=0.98, lines=[
    ("hook", "He turned $1,000 into zero in about ten seconds."),
    ("l1", "He borrowed $9,000, to bet $10,000 that bitcoin would go up."),
    ("l2", "Then bitcoin fell about ten percent."),
    ("l3", "His $10,000 was now worth $9,000. Exactly what he owed."),
    ("l4", "So the exchange sold everything. Automatically."),
    ("l5", "His $1,000 went to the traders betting against him, plus a fee to the exchange."),
    ("l6", "Over one weekend this month, more than two billion dollars of bets went the same way."),
    ("end", "Not advice. Just where the money went. Full video on Money Map."),
])

random.seed(5)
VSTREETS = [(random.uniform(0, VW), random.uniform(0, VH), random.choice([0, 1])) for _ in range(30)]


def bg(c):
    c.set_source_rgb(*E.PAPER)
    c.paint()
    c.set_source_rgb(*E.GRID)
    c.set_line_width(6)
    for x, y, d in VSTREETS:
        if d:
            c.move_to(x, 0)
            c.line_to(x + 160, VH)
        else:
            c.move_to(0, y)
            c.line_to(VW, y - 90)
        c.stroke()
    c.set_source_rgb(*E.PARK)
    rr(c, 760, 1560, 260, 160, 50)
    c.fill()
    logo(c, 60, 120, 0.6)
    txt(c, "MONEY MAP", 112, 158, 40, E.INK)


def capt(c, s, k):
    words = s.split()
    lines, cur = [], ""
    c.select_font_face(E.HEAD, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(66)
    for w in words:
        trial = (cur + " " + w).strip()
        if c.text_extents(trial).x_advance > 900 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    y0 = 1330 - (len(lines) - 1) * 40
    for i, ln in enumerate(lines):
        ex = c.text_extents(ln)
        x = VW / 2 - ex.width / 2 - ex.x_bearing
        y = y0 + i * 80
        c.move_to(x, y)
        c.text_path(ln)
        c.set_source_rgba(1, 1, 1, k)
        c.set_line_width(14)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgba(*E.INK, k)
        c.fill()


def coins_v(c, t, step):
    pos = [(150 + (i % 5) * 195, 560 + (i // 5) * 260) for i in range(10)]
    for i, (x, y) in enumerate(pos):
        if i == 9 and step >= 2:
            k = e(t, 0.2, 1.2) if step == 2 else 1
            x, y = lerp(x, 900, k), lerp(y, 340, k)
        coin(c, x, y, 72)
        if step >= 1:
            sold = step >= 3 or (i == 9 and step >= 2)
            lab = "$50" if sold else "$100"
            if step == 3 and i < 9:
                kk = e(t, 0.2 + i * 0.08, 0.5 + i * 0.08)
                lab = "$100" if kk < 0.5 else "$50"
            txt(c, lab, x, y + 125, 46, E.RED if lab == "$50" else E.INK, align="c")
    if step >= 1:
        val = 1000 if step < 3 else int(lerp(1000, 500, e(t, 0.3, 1.8))) if step == 3 else 500
        card(c, 290, 1000, 500, 150, (1, 1, 1))
        txt(c, "TOTAL VALUE", 540, 1050, 34, E.INK2, align="c")
        txt(c, "$%s" % format(val, ","), 540, 1125, 80, E.RED if val < 1000 else E.INK, align="c")
    if step >= 4:
        stamp(c, 540, 400, "ONLY $50 MOVED", E.GREEN, e(t, 0.6, 1.0) if step == 4 else 1, 64, -0.06)


def lev_v(c, t, step):
    n = 10 if step < 2 else 9
    for i in range(n):
        y = 1150 - i * 66
        col = E.GREEN if (i == 0 and step < 2) else (0.62, 0.66, 0.72)
        lab = "HIS $1,000" if (i == 0 and step < 2) else "BORROWED $1,000"
        a = e(t, 0.3 + i * 0.1, 0.5 + i * 0.1) if (step == 1 and i > 0) else 1
        c.push_group()
        rr(c, 290, y - 58, 500, 58, 10)
        c.set_source_rgb(*col)
        c.fill()
        txt(c, lab, 540, y - 17, 34, (1, 1, 1), align="c")
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    labs = {1: "BET: $10,000", 2: "BITCOIN −10%", 3: "$9,000 = WHAT HE OWED", 4: "AUTO-SELL"}
    if step in labs:
        txt(c, labs[step], 540, 420, 84, E.RED if step >= 2 else E.INK, align="c")
    if step >= 4:
        stamp(c, 540, 780, "LIQUIDATED", E.RED, e(t, 0.3, 0.7), 110)


def split_v(c, t):
    sx, sy = 540, 420
    station(c, sx, sy, 80, E.RED, (1, 1, 1), 14)
    txt(c, "$1,000", sx, sy + 22, 56, E.RED, align="c")
    dest = [(300, 900, "TRADERS BETTING DOWN", E.BLUE), (780, 900, "EXCHANGE FEE", E.ORANGE)]
    for i, (x, y, lab, col) in enumerate(dest):
        c.set_source_rgb(*col)
        c.set_line_width(24)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(sx, sy)
        c.line_to(sx, 650)
        c.line_to(x, 650)
        c.line_to(x, y)
        c.stroke()
        station(c, x, y, 40, col, (1, 1, 1), 12)
        txt(c, lab, x, y + 100, 44, E.INK, align="c")
        k = (t * 0.5 + i * 0.5) % 1
        if k < 0.5:
            yy = lerp(sy, 650, k * 2)
            xx = sx
        else:
            xx = lerp(sx, x, min(1, (k - 0.5) * 4))
            yy = lerp(650, y, max(0, (k - 0.75) * 4))
        token(c, xx, yy, "$", E.GREEN, 40)


def draw(c, S, tl, T):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0, T - t0)
    sc, line = S["lines"][i]
    bg(c)
    if S is S1:
        if sc == "hook":
            coins_v(c, T + 3, 3)
            stamp(c, 450, 330, "1 COIN SOLD. $500 GONE.", E.RED, 1, 70, -0.05)
        elif sc in ("c0", "c1"):
            coins_v(c, t, 1 if sc == "c1" else 0)
        elif sc == "c2":
            coins_v(c, t, 2)
        elif sc == "c3":
            coins_v(c, t, 3)
        elif sc == "c4":
            coins_v(c, t, 4)
        elif sc == "c5":
            txt(c, "A PRICE,", 540, 640, 140, E.INK, align="c")
            txt(c, "NOT CASH.", 540, 800, 140, E.RED, align="c")
            txt(c, "−$1.2 TRILLION", 540, 1000, 90, E.AMBERT if False else E.ORANGE, align="c", alpha=e(t, 1.0, 1.5))
    else:
        if sc == "hook":
            txt(c, "$1,000", 540, 620, 200, E.GREEN, align="c")
            c.set_source_rgb(*E.INK)
            c.set_line_width(14)
            c.move_to(540, 690)
            c.line_to(540, 820)
            c.move_to(490, 770)
            c.line_to(540, 830)
            c.line_to(590, 770)
            c.stroke()
            txt(c, "$0", 540, 1060, 220, E.RED, align="c")
            txt(c, "IN ~10 SECONDS", 540, 1160, 60, E.INK2, align="c")
        elif sc in ("l1", "l2", "l3", "l4"):
            lev_v(c, t, int(sc[1]))
        elif sc == "l5":
            split_v(c, t)
        elif sc == "l6":
            card(c, 90, 500, 900, 500, E.BOARD)
            txt(c, "$2 BILLION+", 540, 760, 150, E.RED, align="c")
            txt(c, "LIQUIDATED IN ONE WEEKEND", 540, 870, 50, (1, 1, 1), align="c")
    if sc == "end":
        card(c, 90, 520, 900, 520, E.BOARD)
        txt(c, "FULL VIDEO", 540, 640, 60, E.AMBERT, align="c")
        txt(c, "WHY IS BITCOIN", 540, 790, 110, (1, 1, 1), align="c")
        txt(c, "CRASHING?", 540, 920, 110, (1, 1, 1), align="c")
    capt(c, line, 1.0 if i == 0 else e(t, 0, 0.2))


def build(S, durs, gap=0.32):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + gap + (1.2 if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def render(S, durs, out):
    tl, total = build(S, durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        draw(c, S, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    return tl, total


def still(S, durs, T, path):
    tl, total = build(S, durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    draw(c, S, tl, T)
    surf.write_to_png(path)
