import sys, os, math, hashlib, subprocess, re, wave
import numpy as np
import cairo

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W, H = 1920, 1080
NAVY = (0.071, 0.133, 0.224)
DESK = (0.827, 0.863, 0.878)
SHEET = (0.992, 0.994, 0.986)
GREEN = (0.031, 0.502, 0.412)
RED = (0.800, 0.196, 0.196)
MARK = (1.0, 0.875, 0.290)
MUTED = (0.420, 0.470, 0.530)
RULE = (0.780, 0.820, 0.850)
GOLD = (0.784, 0.588, 0.180)
CREAM = (0.953, 0.929, 0.878)
COL = {"navy": NAVY, "green": GREEN, "red": RED, "muted": MUTED, "gold": GOLD}
HEAD = ("Poppins", True)
LBL = ("Poppins Medium", False)
MONO = ("DejaVu Sans Mono", True)

SX, SY, SW, SH = 60, 36, 830, 892
RX0, RX1, RY0, RY1 = 960, 1850, 110, 900
RCX, RCY, RW = (RX0 + RX1) / 2, (RY0 + RY1) / 2, RX1 - RX0
KEEP = []
CAPY, CAPW, CAPS, TAGY = 1010, 1500, 42, 62
YOUX = 610
PORTRAIT = False


def set_portrait(rows):
    global W, H, SX, SY, SW, SH, RX0, RX1, RY0, RY1, RCX, RCY, RW, ROWS, CAPY, CAPW, CAPS, TAGY, YOUX, PORTRAIT
    PORTRAIT = True
    ROWS = [r for r in ROWS if r["id"] in rows]
    W, H = 1080, 1920
    SX, SY, SW = 60, 150, 960
    SH = 166 + RH * len(ROWS) + 70
    YOUX = 700
    RX0, RX1 = 60, 1020
    RY0, RY1 = SY + SH + 70, 1360
    RCX, RCY, RW = (RX0 + RX1) / 2, (RY0 + RY1) / 2, RX1 - RX0
    CAPY, CAPW, CAPS, TAGY = 1480, 900, 54, SY + SH + 40


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def prog(t, cue, d=0.45):
    return ease((t - cue) / d)


def setfont(c, font, size):
    c.select_font_face(font[0], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if font[1] else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def tw(c, s, font, size, track=0):
    setfont(c, font, size)
    return c.text_extents(s).x_advance + track * max(0, len(s) - 1)


def text(c, s, x, y, size, font=LBL, col=NAVY, align="l", a=1.0, track=0):
    setfont(c, font, size)
    w = c.text_extents(s).x_advance + track * max(0, len(s) - 1)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    c.set_source_rgba(col[0], col[1], col[2], a)
    if track:
        for ch in s:
            c.move_to(x, y)
            c.show_text(ch)
            x += c.text_extents(ch).x_advance + track
    else:
        c.move_to(x, y)
        c.show_text(s)
    c.new_path()
    return w


def fit(c, s, font, size, maxw):
    while tw(c, s, font, size) > maxw and size > 10:
        size -= 2
    return size


def wrap(c, s, font, size, maxw):
    out, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if tw(c, t, font, size) <= maxw or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def slip(c, x, y, w, h, a=1.0, fill=SHEET, r=10, line=3):
    rrect(c, x + 7, y + 9, w, h, r)
    c.set_source_rgba(*NAVY, 0.16 * a)
    c.fill()
    rrect(c, x, y, w, h, r)
    c.set_source_rgba(*fill, a)
    c.fill_preserve()
    c.set_source_rgba(*NAVY, a)
    c.set_line_width(line)
    c.stroke()


def pill(c, s, x, y, size, bg, fg=SHEET, a=1.0, align="c", font=HEAD, pad=18, track=2):
    w = tw(c, s, font, size, track) + pad * 2
    h = size * 1.8
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    rrect(c, x, y - h / 2, w, h, 8)
    c.set_source_rgba(*bg, a)
    c.fill()
    text(c, s, x + pad, y + size * 0.36, size, font, fg, "l", a, track)
    return w


def marker(c, x, y, w, h, k, a=1.0):
    if k <= 0:
        return
    c.set_source_rgba(*MARK, 0.85 * a)
    c.move_to(x - 8, y + 3)
    c.line_to(x - 4 + (w + 12) * k, y)
    c.line_to(x - 8 + (w + 14) * k, y + h)
    c.line_to(x - 12, y + h - 2)
    c.close_path()
    c.fill()


def brand_mark(c, x, y, s, a=1.0):
    rrect(c, x, y, s, s, s * 0.22)
    c.set_source_rgba(0.086, 0.082, 0.059, a)
    c.fill()
    pts = [(0.2, 0.76), (0.2, 0.28), (0.5, 0.58), (0.8, 0.28), (0.8, 0.62)]
    c.set_line_width(s * 0.085)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(*GOLD, a)
    c.move_to(x + pts[0][0] * s, y + pts[0][1] * s)
    for px, py in pts[1:]:
        c.line_to(x + px * s, y + py * s)
    c.stroke()
    for px, py in pts[:-1]:
        c.arc(x + px * s, y + py * s, s * 0.055, 0, 7)
        c.set_source_rgba(*CREAM, a)
        c.fill()
    ex, ey = x + 0.8 * s, y + 0.74 * s
    c.arc(ex, ey, s * 0.12, 0, 7)
    c.set_source_rgba(0.118, 0.478, 0.290, a)
    c.fill()
    c.set_source_rgba(*CREAM, a)
    c.set_line_width(s * 0.04)
    c.move_to(ex - s * 0.055, ey)
    c.line_to(ex - s * 0.012, ey + s * 0.045)
    c.line_to(ex + s * 0.06, ey - s * 0.045)
    c.stroke()
    c.set_line_cap(cairo.LINE_CAP_BUTT)


def make_bg():
    rng = np.random.default_rng(11)
    base = np.array(DESK) * 255
    n = rng.normal(0, 2.2, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2) * 30
    img = np.clip(base[None, None, :] + n - v[..., None], 0, 255).astype(np.uint8)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = img[..., 2], img[..., 1], img[..., 0], 255
    surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H, W * 4)
    KEEP.append(arr)
    c = cairo.Context(surf)
    if PORTRAIT:
        brand_mark(c, 60, 50, 60)
        text(c, "MONEY MAP", 136, 92, 30, HEAD, NAVY, track=6)
    rrect(c, SX + 10, SY + 14, SW, SH, 6)
    c.set_source_rgba(*NAVY, 0.20)
    c.fill()
    rrect(c, SX, SY, SW, SH, 6)
    c.set_source_rgb(*SHEET)
    c.fill()
    for i in range(int((SH - 40) / 61) + 1):
        c.arc(SX + 22, SY + 50 + i * 61, 8, 0, 7)
        c.set_source_rgb(*DESK)
        c.fill()
    c.set_source_rgba(*RULE, 0.9)
    c.set_dash([4, 6])
    c.set_line_width(2)
    c.move_to(SX + 44, SY)
    c.line_to(SX + 44, SY + SH)
    c.stroke()
    c.set_dash([])
    brand_mark(c, SX + 62, SY + 24, 62)
    text(c, "MONEY MAP", SX + 140, SY + 54, 28, HEAD, NAVY, track=5)
    text(c, "Follow the money.", SX + 140, SY + 82, 18, LBL, MUTED)
    text(c, "STATEMENT OF ACCOUNT", SX + SW - 30, SY + 54, 21, MONO, NAVY, "r")
    text(c, "PERIOD: 12 MONTHS", SX + SW - 30, SY + 82, 17, MONO, MUTED, "r")
    c.set_source_rgb(*NAVY)
    c.rectangle(SX + 62, SY + 110, SW - 92, 44)
    c.fill()
    text(c, "ENTRY", SX + 78, SY + 140, 18, HEAD, SHEET, track=4)
    text(c, "YOU", SX + YOUX, SY + 140, 18, HEAD, SHEET, "r", track=4)
    text(c, "THE BANK", SX + SW - 44, SY + 140, 18, HEAD, SHEET, "r", track=4)
    text(c, "US averages, 2026. Educational explainer, not financial advice.", SX + 62, SY + SH - 20, 15 if not PORTRAIT else 18, LBL, MUTED)
    return surf


ROWS = [
    dict(id="dep", t="OPENING DEPOSIT", s="Your savings account", you="$1,000.00", bank=""),
    dict(id="int", t="INTEREST PAID TO YOU", s="0.38% a year, the US average", you="+$3.80", bank=""),
    dict(id="cc", t="IF LENT ON A CREDIT CARD", s="20.94% a year, the best case", you="", bank="+$210.00"),
    dict(id="avg", t="AVERAGE EARNED LENDING IT", s="3.32% a year across US banks", you="", bank="+$33.20"),
    dict(id="od", t="ONE OVERDRAFT FEE", s="If you slip below zero once", you="-$35.00", bank="+$35.00"),
    dict(id="swipe", t="CARD SWIPE FEES", s="Paid by shops each time you tap", you="", bank="+ A SLICE"),
    dict(id="big", t="DEALS, WEALTH, TRADING", s="From companies and wealthy clients", you="", bank="+ FEES"),
]
RH = 86


def ledger(c, t, sc):
    P = sc["P"]
    st = sc["led0"]
    shown = dict(st["shown"])
    for e in P.get("ledger", []):
        shown[e["row"]] = e["cue"]
    struck = dict(st["struck"])
    for e in P.get("strike", []):
        struck[e["row"]] = e["cue"]
    hl = {e["row"]: e["cue"] for e in P.get("hl", [])}
    y = SY + 166
    for r in ROWS:
        cue = shown.get(r["id"])
        if cue is not None and t >= cue:
            k = (t - cue) / 0.5
            a = min(1.0, k * 2)
            new = cue >= 0
            hcue = hl.get(r["id"], cue if new else None)
            if hcue is not None and t >= hcue:
                hk = ease((t - hcue) / 0.5)
                c.set_source_rgba(*MARK, 0.42)
                c.rectangle(SX + 52, y + 6, (SW - 72) * hk, RH - 12)
                c.fill()
            sk = 0.0
            if r["id"] in struck and t >= struck[r["id"]]:
                sk = ease((t - struck[r["id"]]) / 0.5)
            fade = 1 - 0.55 * sk
            n = len(r["t"]) if k >= 1 else max(1, int(len(r["t"]) * k))
            text(c, r["t"][:n], SX + 78, y + 38, 23, MONO, NAVY, "l", a * fade)
            text(c, r["s"], SX + 78, y + 66, 18, LBL, MUTED, "l", a * fade)
            if r["you"]:
                col = GREEN if r["you"][0] == "+" else RED if r["you"][0] == "-" else NAVY
                text(c, r["you"], SX + YOUX, y + 50, 27, MONO, col, "r", a * fade)
            if r["bank"]:
                text(c, r["bank"], SX + SW - 44, y + 50, 27, MONO, NAVY, "r", a * fade)
            if sk > 0:
                c.set_source_rgba(*RED, 0.9)
                c.set_line_width(4)
                c.move_to(SX + 70, y + 44)
                c.line_to(SX + 70 + (SW - 110) * sk, y + 40)
                c.stroke()
        c.set_source_rgba(*RULE, 1)
        c.set_dash([3, 5])
        c.set_line_width(2)
        c.move_to(SX + 62, y + RH)
        c.line_to(SX + SW - 30, y + RH)
        c.stroke()
        c.set_dash([])
        y += RH
    tc = P.get("totals", st["totals"])
    if tc is not None and t >= tc:
        a = prog(t, tc)
        c.set_source_rgba(*NAVY, a)
        c.rectangle(SX + 62, y + 14, SW - 92, 4)
        c.rectangle(SX + 62, y + 22, SW - 92, 2)
        c.fill()
        text(c, "AFTER ONE YEAR", SX + 78, y + 66, 22, HEAD, NAVY, "l", a, track=3)
        text(c, "+$3.80", SX + YOUX, y + 68, 30, MONO, GREEN, "r", a)
        text(c, "$33.20+", SX + SW - 44, y + 68, 30, MONO, NAVY, "r", a)


def src(c, t, P):
    if P.get("src"):
        text(c, P["src"], RX1, RY1 + 4, 19, LBL, MUTED, "r", prog(t, 0.3))


def note(c, t, P, y=None):
    ns = [n for n in P.get("notes", []) if t >= n["cue"]]
    if not ns:
        return
    n = ns[-1]
    a = prog(t, n["cue"], 0.35)
    size = 40
    ls = wrap(c, n["t"], HEAD, size, RW - 20)
    y0 = (y if y is not None else RY1 - 40) - (len(ls) - 1) * size * 1.25
    for i, ln in enumerate(ls):
        text(c, ln, RCX, y0 + i * size * 1.25 + (1 - a) * 16, size, HEAD, COL[n.get("col", "navy")], "c", a)


def stamp(c, t, st, x, y):
    if not st or t < st["cue"]:
        return
    k = prog(t, st["cue"], 0.25)
    c.save()
    c.translate(x, y)
    c.rotate(-0.12)
    sc = 1.5 - 0.5 * k
    c.scale(sc, sc)
    size = st.get("size", 64)
    sw = tw(c, st["t"], HEAD, size, 3) + 60
    rrect(c, -sw / 2, -size * 0.85, sw, size * 1.7, 12)
    c.set_source_rgba(*SHEET, 0.9 * k)
    c.fill_preserve()
    c.set_source_rgba(*RED, 0.95 * k)
    c.set_line_width(8)
    c.stroke()
    text(c, st["t"], 0, size * 0.36, size, HEAD, RED, "c", 0.95 * k, track=3)
    c.restore()


def d_num(c, t, P):
    items = P["items"]
    n = len(items)
    head = P.get("head")
    top = RY0 + 10
    if head:
        text(c, head, RCX, top + 34, 28, HEAD, MUTED, "c", prog(t, 0), track=4)
        top += 70
    has_note = bool(P.get("notes"))
    avail = RY1 - top - (120 if has_note else 40)
    gap = 30
    bh = min(380, (avail - gap * (n - 1)) / n)
    y = top + (avail - (bh * n + gap * (n - 1))) / 2
    bw = RW - 60
    x = RCX - bw / 2
    for it in items:
        a = prog(t, it["cue"])
        if a > 0:
            yy = y + (1 - a) * 36
            slip(c, x, yy, bw, bh, a)
            c.set_source_rgba(*COL[it.get("col", "navy")], a)
            c.rectangle(x, yy + 14, 12, bh - 28)
            c.fill()
            if "s" in it:
                s = it["s"]
            else:
                k = ease_io((t - it["cue"]) / 1.0) if it.get("count", True) else 1
                s = it.get("pre", "") + f"{it['v'] * k:,.{it.get('dec', 0)}f}" + it.get("suf", "")
            full = it.get("s") or it.get("pre", "") + f"{it['v']:,.{it.get('dec', 0)}f}" + it.get("suf", "")
            size = fit(c, full, MONO, min(170, bh * 0.50), bw - 110)
            lsz = 30 if n < 3 else 26
            ls = wrap(c, it["label"], LBL, lsz, bw - 100)
            block = size * 0.74 + 26 + len(ls) * lsz * 1.3
            by = yy + (bh - block) / 2 + size * 0.74
            text(c, s, RCX, by, size, MONO, COL[it.get("col", "navy")], "c", a)
            for j, ln in enumerate(ls):
                text(c, ln, RCX, by + 26 + lsz + j * lsz * 1.3, lsz, LBL, NAVY, "c", a)
        y += bh + gap
    stamp(c, t, P.get("stamp"), RCX, RCY + 300)
    note(c, t, P)
    src(c, t, P)


def d_text(c, t, P):
    items = P["lines"]
    size = P.get("size", 76)
    blocks = []
    for it in items:
        sz = size * it.get("scale", 1.0)
        f = MONO if it.get("mono") else HEAD
        ls = wrap(c, it["t"], f, sz, RW - 30)
        blocks.append((it, ls, sz, f))
    gap = size * 0.5
    total = sum(len(ls) * sz * 1.22 for _, ls, sz, _ in blocks) + gap * (len(blocks) - 1)
    kick = P.get("kicker")
    y = RCY - total / 2 + (30 if kick else 0)
    if kick:
        pill(c, kick, RX0 + 20, y - 54, 24, NAVY, SHEET, prog(t, P.get("kcue", 0)), "l")
    for it, ls, sz, f in blocks:
        a = prog(t, it["cue"])
        dy = (1 - a) * 30
        col = COL[it.get("col", "navy")]
        for ln in ls:
            y += sz * 1.22
            if it.get("hl") and a > 0:
                marker(c, RX0 + 20, y - sz * 1.08, tw(c, ln, f, sz), sz * 1.12, prog(t, it["cue"] + 0.15, 0.6), a)
            text(c, ln, RX0 + 20, y - sz * 0.28 + dy, sz, f, col, "l", a)
        y += gap
    src(c, t, P)


def d_list(c, t, P):
    items = P["items"]
    y = RY0 + 10
    if P.get("title"):
        ls = wrap(c, P["title"], HEAD, 46, RW - 20)
        for ln in ls:
            text(c, ln, RX0 + 20, y + 46, 46, HEAD, NAVY, "l", prog(t, P.get("tcue", 0)))
            y += 58
        y += 26
    has_note = bool(P.get("notes"))
    rh = min(150, (RY1 - y - (110 if has_note else 20)) / len(items) - 20)
    for it in items:
        a = prog(t, it["cue"])
        if a > 0:
            xx = RX0 + 20 + (1 - a) * 50
            slip(c, xx, y, RW - 40, rh, a)
            c.set_source_rgba(*COL[it.get("col", "navy")], a)
            c.rectangle(xx, y + 12, 12, rh - 24)
            c.fill()
            if it.get("s"):
                text(c, it["h"], xx + 40, y + rh * 0.44, fit(c, it["h"], MONO, 34, RW - 110), MONO, NAVY, "l", a)
                text(c, it["s"], xx + 40, y + rh * 0.44 + 40, fit(c, it["s"], LBL, 27, RW - 110), LBL, MUTED, "l", a)
            else:
                text(c, it["h"], xx + 40, y + rh / 2 + 12, fit(c, it["h"], MONO, 34, RW - 110), MONO, NAVY, "l", a)
        y += rh + 20
    note(c, t, P)
    src(c, t, P)


def d_receipt(c, t, P):
    rows = P["rows"]
    w = P.get("w", 640)
    rh = 74
    vis = [r for r in rows if t >= r["cue"]]
    grow = sum(prog(t, r["cue"], 0.35) for r in rows if r["cue"] >= 0) + sum(1 for r in rows if r["cue"] < 0)
    tot = P.get("total")
    tk = prog(t, tot["cue"], 0.35) if tot else 0
    h = 130 + grow * rh + tk * 120 + 40
    x = RCX - w / 2
    y = RY0 + 20
    c.set_source_rgba(*NAVY, 0.16)
    c.rectangle(x + 8, y + 10, w, h)
    c.fill()
    c.set_source_rgb(*SHEET)
    c.move_to(x, y)
    c.line_to(x + w, y)
    c.line_to(x + w, y + h)
    nz = 20
    for i in range(nz):
        c.line_to(x + w - (i + 0.5) * w / nz, y + h + 14)
        c.line_to(x + w - (i + 1) * w / nz, y + h)
    c.close_path()
    c.fill_preserve()
    c.set_source_rgb(*NAVY)
    c.set_line_width(3)
    c.stroke()
    text(c, P.get("title", "RECEIPT"), RCX, y + 62, fit(c, P.get("title", "RECEIPT"), HEAD, 34, w - 60), HEAD, NAVY, "c", 1, track=3)
    c.set_source_rgb(*NAVY)
    c.set_dash([6, 6])
    c.set_line_width(2)
    c.move_to(x + 30, y + 96)
    c.line_to(x + w - 30, y + 96)
    c.stroke()
    c.set_dash([])
    yy = y + 130
    for r in rows:
        a = 1.0 if r["cue"] < 0 else prog(t, r["cue"], 0.35)
        if a > 0:
            if r.get("hl"):
                marker(c, x + 30, yy - 4, w - 60, rh - 14, a)
            lsz = fit(c, r["t"], MONO, 27, w - 70 - (150 if r.get("amt") else 0))
            text(c, r["t"], x + 36, yy + 38, lsz, MONO, COL[r.get("col", "navy")], "l", a)
            if r.get("amt"):
                acue = r.get("acue", r["cue"])
                text(c, r["amt"], x + w - 36, yy + 38, 29, MONO, COL[r.get("col", "navy")], "r", 1.0 if acue < 0 else prog(t, acue, 0.3))
            yy += rh * a
    if tot and tk > 0:
        c.set_source_rgba(*NAVY, tk)
        c.rectangle(x + 30, yy + 4, w - 60, 4)
        c.fill()
        text(c, tot["label"], x + 36, yy + 74, 30, HEAD, NAVY, "l", tk, track=2)
        text(c, tot["t"], x + w - 36, yy + 80, 56, MONO, RED, "r", tk)
    stamp(c, t, P.get("stamp"), RCX, y + h * 0.55)
    note(c, t, P)
    src(c, t, P)


def d_rates(c, t, P):
    ax = RX0 + 150
    y0, y1, mx = RY1 - 60, RY0 + 30, 22.0
    ta = prog(t, 0) if not P.get("cont") else 1.0

    def Y(v):
        return y0 + (y1 - y0) * v / mx
    c.set_source_rgba(*NAVY, ta)
    c.rectangle(ax - 3, y1, 6, y0 - y1)
    c.fill()
    for v in range(0, 23):
        big = v % 5 == 0
        c.rectangle(ax - (26 if big else 14), Y(v) - 1.5, 26 if big else 14, 3)
        c.fill()
        if big:
            text(c, f"{v}%", ax - 40, Y(v) + 10, 26, MONO, NAVY, "r", ta)
    text(c, "INTEREST PER YEAR", ax - 118, (y0 + y1) / 2, 20, HEAD, MUTED, "c", 0)
    for m in P["marks"]:
        a = 1.0 if m["cue"] < 0 else prog(t, m["cue"])
        if a <= 0:
            continue
        col = COL[m.get("col", "navy")]
        yy = Y(m["v"])
        ly = yy + m.get("dy", 0)
        ln = 150 * a
        c.set_source_rgba(*col, a)
        c.set_line_width(5)
        c.move_to(ax, yy)
        c.line_to(ax + ln * 0.5, yy)
        c.line_to(ax + ln, ly)
        c.stroke()
        c.arc(ax, yy, 9, 0, 7)
        c.fill()
        lw = tw(c, m["label"], HEAD, 27, 1) + tw(c, m["val"], MONO, 30) + 60
        rrect(c, ax + 150, ly - 30, lw, 60, 8)
        c.set_source_rgba(*col, a)
        c.fill()
        text(c, m["label"], ax + 168, ly + 10, 27, HEAD, SHEET, "l", a, track=1)
        text(c, m["val"], ax + 150 + lw - 18, ly + 11, 30, MONO, SHEET, "r", a)
    b = P.get("bracket")
    if b and t >= b["cue"]:
        a = prog(t, b["cue"], 0.6)
        bx = RX1 - 50
        ya, yb = Y(b["lo"]), Y(b["hi"])
        yb2 = ya + (yb - ya) * a
        c.set_source_rgba(*RED, 1)
        c.set_line_width(7)
        c.move_to(bx - 26, ya)
        c.line_to(bx, ya)
        c.line_to(bx, yb2)
        c.line_to(bx - 26, yb2)
        c.stroke()
        text(c, b["t"], bx - 50, Y(14.2), 58, HEAD, RED, "r", a)
        if b.get("s"):
            text(c, b["s"], bx - 50, Y(14.2) + 46, 26, LBL, NAVY, "r", a)
    src(c, t, P)


def d_iou(c, t, P):
    a = prog(t, 0)
    vx, vy, vs = RCX - 150, RY0 + 40, 300
    slip(c, vx, vy, vs, vs, a, fill=(0.88, 0.90, 0.92), r=22, line=5)
    c.set_source_rgba(*NAVY, a)
    c.set_line_width(6)
    c.arc(vx + vs / 2, vy + vs / 2, 78, 0, 7)
    c.stroke()
    for i in range(4):
        ang = i * math.pi / 2 + 0.4
        c.move_to(vx + vs / 2, vy + vs / 2)
        c.line_to(vx + vs / 2 + math.cos(ang) * 78, vy + vs / 2 + math.sin(ang) * 78)
        c.stroke()
    text(c, "YOUR NAME", vx + vs / 2, vy + vs - 22, 20, HEAD, MUTED, "c", a, track=3)
    xc = P["x"]
    if t >= xc:
        k = prog(t, xc, 0.3)
        c.set_source_rgba(*RED, k)
        c.set_line_width(18)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(vx + 30, vy + 30)
        c.line_to(vx + 30 + (vs - 60) * k, vy + 30 + (vs - 60) * k)
        c.move_to(vx + vs - 30, vy + 30)
        c.line_to(vx + vs - 30 - (vs - 60) * k, vy + 30 + (vs - 60) * k)
        c.stroke()
        c.set_line_cap(cairo.LINE_CAP_BUTT)
    ic = P["iou"]
    if t >= ic:
        k = prog(t, ic)
        w, h = 760, 300
        x, y = RCX - w / 2, vy + vs + 60 + (1 - k) * 40
        slip(c, x, y, w, h, k)
        text(c, "I.O.U.", x + 40, y + 86, 64, HEAD, RED, "l", k, track=4)
        text(c, "THE BANK OWES YOU", x + 40, y + 150, 30, MONO, NAVY, "l", k)
        text(c, "$1,000.00", x + w - 40, y + 160, 62, MONO, NAVY, "r", k)
        c.set_source_rgba(*NAVY, k)
        c.set_dash([6, 6])
        c.set_line_width(2)
        c.move_to(x + 40, y + 196)
        c.line_to(x + w - 40, y + 196)
        c.stroke()
        c.set_dash([])
        pc = P.get("promise", ic)
        text(c, "Payable whenever you ask", x + 40, y + 248, 30, LBL, MUTED, "l", prog(t, pc))


def d_split(c, t, P):
    a = prog(t, 0)
    w, h = RW - 80, 150
    x, y = RX0 + 40, RCY - 60
    text(c, "YOUR $1,000", RCX, y - 60, 44, HEAD, NAVY, "c", a, track=3)
    k = ease_io((t - P["cue"]) / 0.9) if t >= P["cue"] else 0
    sw = w * 0.14
    gapx = 40 * k
    rrect(c, x, y, sw, h, 8)
    c.set_source_rgba(*NAVY, a)
    c.fill()
    k2 = ease_io((t - P["cue2"]) / 1.0) if t >= P["cue2"] else 0
    rx = x + sw + gapx + k2 * 30
    rrect(c, rx, y, w - sw - gapx - 30, h, 8)
    c.set_source_rgba(*GREEN, a)
    c.fill()
    if k > 0:
        text(c, "KEPT", x + sw / 2, y + h + 48, 26, HEAD, NAVY, "c", k, track=2)
        text(c, "READY", x + sw / 2, y + h + 82, 26, HEAD, NAVY, "c", k, track=2)
    if k2 > 0:
        text(c, "SENT OUT TO WORK", rx + (w - sw - gapx - 30) / 2, y + h / 2 + 16, 44, HEAD, SHEET, "c", k2, track=3)
        for i in range(3):
            ph = ((t - P["cue2"]) * 0.7 + i / 3) % 1
            ax_ = rx + 80 + ph * (w - sw - gapx - 240)
            ay = y + h + 66
            c.set_source_rgba(*GREEN, k2 * math.sin(ph * math.pi))
            c.set_line_width(8)
            c.move_to(ax_, ay)
            c.line_to(ax_ + 70, ay)
            c.move_to(ax_ + 48, ay - 18)
            c.line_to(ax_ + 72, ay)
            c.line_to(ax_ + 48, ay + 18)
            c.stroke()


def car(c, x, y, s, col, a=1.0):
    c.set_source_rgba(*col, a)
    rrect(c, x - 90 * s, y - 34 * s, 180 * s, 50 * s, 14 * s)
    c.fill()
    c.move_to(x - 56 * s, y - 34 * s)
    c.line_to(x - 34 * s, y - 72 * s)
    c.line_to(x + 40 * s, y - 72 * s)
    c.line_to(x + 66 * s, y - 34 * s)
    c.close_path()
    c.fill()
    c.set_source_rgba(*SHEET, a)
    c.move_to(x - 40 * s, y - 38 * s)
    c.line_to(x - 26 * s, y - 62 * s)
    c.line_to(x + 32 * s, y - 62 * s)
    c.line_to(x + 48 * s, y - 38 * s)
    c.close_path()
    c.fill()
    for dx in (-52, 52):
        c.arc(x + dx * s, y + 16 * s, 22 * s, 0, 7)
        c.set_source_rgba(*NAVY, a)
        c.fill()
        c.arc(x + dx * s, y + 16 * s, 9 * s, 0, 7)
        c.set_source_rgba(*SHEET, a)
        c.fill()


def clock(c, x, y, r, hour, a=1.0):
    c.arc(x, y, r, 0, 7)
    c.set_source_rgba(*SHEET, a)
    c.fill_preserve()
    c.set_source_rgba(*NAVY, a)
    c.set_line_width(7)
    c.stroke()
    for i in range(12):
        ang = i * math.pi / 6
        c.move_to(x + math.sin(ang) * r * 0.82, y - math.cos(ang) * r * 0.82)
        c.line_to(x + math.sin(ang) * r * 0.93, y - math.cos(ang) * r * 0.93)
        c.set_line_width(5)
        c.stroke()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    ha = (hour % 12) / 12 * 2 * math.pi
    ma = (hour % 1) * 2 * math.pi
    c.set_line_width(10)
    c.move_to(x, y)
    c.line_to(x + math.sin(ha) * r * 0.5, y - math.cos(ha) * r * 0.5)
    c.stroke()
    c.set_source_rgba(*RED, a)
    c.set_line_width(6)
    c.move_to(x, y)
    c.line_to(x + math.sin(ma) * r * 0.74, y - math.cos(ma) * r * 0.74)
    c.stroke()
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    hh = int(hour)
    lab = f"{(hh - 1) % 12 + 1}:{int((hour % 1) * 60) // 5 * 5:02d} {'am' if hh < 12 else 'pm'}"
    text(c, lab, x, y + r + 50, 34, MONO, NAVY, "c", a)


def person(c, x, y, s, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.arc(x, y - s * 0.3, s * 0.26, 0, 7)
    c.fill()
    c.arc(x, y + s * 0.5, s * 0.5, math.pi, 2 * math.pi)
    c.fill()


def spot(c, x, y, w, h, label=None, a=1.0):
    c.set_source_rgba(*NAVY, a)
    c.set_dash([14, 10])
    c.set_line_width(5)
    c.rectangle(x - w / 2, y - h / 2, w, h)
    c.stroke()
    c.set_dash([])
    if label:
        text(c, label, x, y + h / 2 + 34, 22, HEAD, MUTED, "c", a, track=3)


def d_car(c, t, P):
    a = prog(t, 0)
    if P["mode"] == "day":
        out, back = P["out"], P["back"]
        hour = 9.0
        if t >= out:
            hour = 9 + 8 * min(1.0, (t - out) / max(0.1, back - out))
        clock(c, RX0 + 150, RY0 + 130, 105, hour, a)
        text(c, "YOU ARE AT THE OFFICE", RX0 + 300, RY0 + 110, 30, HEAD, NAVY, "l", a, track=2)
        text(c, "You don't need the car until 5.", RX0 + 300, RY0 + 156, 28, LBL, MUTED, "l", a)
        ry = RY1 - 150
        c.set_source_rgba(*RULE, a)
        c.rectangle(RX0 + 20, ry + 44, RW - 40, 10)
        c.fill()
        sx = RX0 + 170
        spot(c, sx, ry - 10, 250, 150, "YOUR PARKING SPOT", a)
        far = RX1 - 150
        if t < out:
            k = 0
        elif t < back - 1.3:
            k = ease_io((t - out) / 1.3)
        else:
            k = 1 - ease_io((t - (back - 1.3)) / 1.3)
        x = sx + (far - sx) * k
        bob = math.sin(t * 9) * 3 * (1 if 0 < k else 0)
        car(c, x, ry + bob, 1.0, GREEN, a)
        if k > 0.9:
            for i in range(3):
                ph = ((t - out) * 0.6 + i / 3) % 1
                text(c, "+$", far - 30 + i * 40, ry - 100 - ph * 110, 44, MONO, GOLD, "c", math.sin(ph * math.pi))
            text(c, "OUT DOING DELIVERIES", far - 60, ry - 250, 24, HEAD, GREEN, "c", 1, track=2)
        note(c, t, P, RY1 - 300)
    else:
        clock(c, RX0 + 150, RY0 + 130, 105, 12.0, a)
        text(c, "EVERYONE WALKS OUT AT NOON", RX0 + 300, RY0 + 110, 30, HEAD, NAVY, "l", a, track=2)
        text(c, "All asking for their keys at once.", RX0 + 300, RY0 + 156, 28, LBL, MUTED, "l", a)
        cols, rows_ = 4, 2
        gw = (RW - 60) / cols
        for i in range(cols * rows_):
            cx = RX0 + 30 + gw * (i % cols + 0.5)
            cy = RY0 + 400 + (i // cols) * 210
            spot(c, cx, cy, gw - 40, 120, None, a)
            pc = P["people"] + i * 0.12
            if t >= pc:
                k = prog(t, pc, 0.3)
                person(c, cx - 30, cy - 4, 64, NAVY, k)
                text(c, "?", cx + 44, cy + 26, 70, HEAD, RED, "c", k)
        note(c, t, P, RY1 - 10)


def note_money(c, x, y, s, label, col=GREEN, a=1.0):
    w, h = 170 * s, 84 * s
    rrect(c, x - w / 2, y - h / 2, w, h, 8 * s)
    c.set_source_rgba(*col, a)
    c.fill_preserve()
    c.set_source_rgba(*NAVY, a)
    c.set_line_width(3)
    c.stroke()
    text(c, label, x, y + 13 * s, 36 * s, MONO, SHEET, "c", a)


def d_swipe(c, t, P):
    a = prog(t, 0)
    nw, nh = 300, 210
    you = (RX0 + 170, RY0 + 170)
    shop = (RX1 - 170, RY0 + 170)
    bank = (RCX, RY1 - 190)
    for (x, y), lab, kind in ((you, "YOU", 0), (shop, "THE SHOP", 1)):
        slip(c, x - nw / 2, y - nh / 2, nw, nh, a)
        if kind == 0:
            person(c, x, y - 30, 70, NAVY, a)
        else:
            c.set_source_rgba(*NAVY, a)
            c.rectangle(x - 60, y - 40, 120, 56)
            c.fill()
            for i in range(5):
                c.set_source_rgba(*(RED if i % 2 == 0 else SHEET), a)
                c.rectangle(x - 60 + i * 24, y - 78, 24, 40)
                c.fill()
        text(c, lab, x, y + 72, 28, HEAD, NAVY, "c", a, track=3)
    bc = P["bank"]
    ba = prog(t, bc)
    if ba > 0:
        bw = 620
        slip(c, bank[0] - bw / 2, bank[1] - 80, bw, 190, ba, fill=(0.93, 0.96, 0.95))
        text(c, "THE BANK THAT GAVE YOU THE CARD", bank[0], bank[1] - 24, 25, HEAD, NAVY, "c", ba, track=2)
    pc = P["pay"]
    sc_ = P["slice"]
    if t >= pc:
        k = ease_io((t - pc) / 1.4)
        x = you[0] + (shop[0] - you[0]) * k
        y = you[1] - math.sin(k * math.pi) * 40
        if k < 1:
            note_money(c, x, y, 1.0, "$100")
        if t >= sc_:
            k2 = ease_io((t - sc_) / 1.1)
            mx, my = (you[0] + shop[0]) / 2 + 80, you[1] + 20
            sx_ = mx + (bank[0] - mx) * k2
            sy_ = my + (bank[1] + 50 - my) * k2
            if k2 < 1:
                note_money(c, sx_, sy_, 0.6, "SLICE", GOLD)
            if k2 >= 1:
                pill(c, "GETS MOST OF THE SLICE", bank[0], bank[1] + 50, 24, GREEN, SHEET, prog(t, sc_ + 1.1, 0.3))
        if k >= 1:
            lab = "RECEIVES LESS THAN $100" if t >= P["less"] else "GETS PAID"
            pill(c, lab, shop[0], shop[1] + nh / 2 + 44, 22, RED if t >= P["less"] else NAVY, SHEET, 1)
    if t >= pc:
        pill(c, "PAYS $100", you[0], you[1] + nh / 2 + 44, 22, NAVY, SHEET, prog(t, pc, 0.3))


def d_scale(c, t, P):
    a = prog(t, 0)
    g = P["grow"]
    k = ease_io((t - g) / 1.8) if t >= g else 0
    v = 10 ** (3 + 9 * k)
    s = "$" + f"{int(round(v)):,}" + ("+" if k >= 1 else "")
    if 0 < k < 1:
        s = "$" + f"{int(float(f'{v:.2g}')):,}"
    size = fit(c, s, MONO, 150, RW - 40)
    slip(c, RX0 + 10, RCY - 150, RW - 20, 260, a)
    text(c, s, RCX, RCY + size * 0.34 - 20, size, MONO, RED if k >= 1 else NAVY, "c", a)
    lab = P["after"] if k >= 1 else P["before"]
    text(c, lab, RCX, RCY + 170, 34, LBL, NAVY, "c", a)
    note(c, t, P)


def d_end(c, t, P):
    a = prog(t, 0.0, 0.5)
    s = 170
    brand_mark(c, RCX - s / 2, RCY - 290 + (1 - a) * 30, s, a)
    text(c, "MONEY MAP", RCX, RCY - 60, 40, HEAD, NAVY, "c", a, track=10)
    a2 = prog(t, P["cue"], 0.5)
    sz = 92
    w = tw(c, "Follow the money.", HEAD, sz)
    marker(c, RCX - w / 2, RCY + 20, w, sz * 1.1, prog(t, P["cue"] + 0.2, 0.7), a2)
    text(c, "Follow the money.", RCX, RCY + 100, sz, HEAD, NAVY, "c", a2)
    a3 = prog(t, P.get("cue2", 0), 0.5)
    text(c, P.get("label", "NEXT"), RCX, RCY + 210, 24, HEAD, RED, "c", a3, track=6)
    ls = wrap(c, P["next"], LBL, 34, RW - 40)
    for i, ln in enumerate(ls):
        text(c, ln, RCX, RCY + 262 + i * 46, 34, LBL, NAVY, "c", a3)


DRAW = {"num": d_num, "text": d_text, "list": d_list, "receipt": d_receipt, "rates": d_rates, "iou": d_iou,
        "split": d_split, "car": d_car, "swipe": d_swipe, "scale": d_scale, "end": d_end}


def chrome(c, t, sc, T, cap):
    if sc.get("tag"):
        pill(c, sc["tag"], RX0 + 20, TAGY, 22 if not PORTRAIT else 26, NAVY, SHEET, 1, "l", track=3)
    if not PORTRAIT:
        c.set_source_rgba(*NAVY, 0.25)
        c.rectangle(RX0 + 20, 92, RW - 40, 2)
        c.fill()
    c.set_source_rgba(*GREEN, 1)
    c.rectangle(0, H - 6, W * t / T, 6)
    c.fill()
    if cap:
        size = CAPS
        ls = wrap(c, cap, LBL, size, CAPW)
        y = CAPY - (len(ls) - 1) * size * 0.65
        for i, ln in enumerate(ls):
            w = tw(c, ln, LBL, size)
            yy = y + i * size * 1.3
            rrect(c, W / 2 - w / 2 - 28, yy - size * 1.0, w + 56, size * 1.46, 8)
            c.set_source_rgba(*SHEET, 1)
            c.fill_preserve()
            c.set_source_rgba(*NAVY, 1)
            c.set_line_width(3)
            c.stroke()
            text(c, ln, W / 2, yy, size, LBL, NAVY, "c")


def tts_all(scenes, voice, speed, cache):
    os.makedirs(cache, exist_ok=True)
    todo = []
    for sc in scenes:
        for ln in sc["say"]:
            assert not re.search(r"[0-9$%]", ln), "unspoken token in: " + ln
            h = hashlib.md5(f"{voice}|{speed}|{ln}".encode()).hexdigest()[:16]
            todo.append((ln, os.path.join(cache, h + ".npy")))
    missing = [x for x in todo if not os.path.exists(x[1])]
    if missing:
        from kokoro_onnx import Kokoro
        k = Kokoro(os.path.join(ROOT, "models/kokoro-v1.0.onnx"), os.path.join(ROOT, "models/voices-v1.0.bin"))
        for i, (sp, path) in enumerate(missing):
            s, sr = k.create(sp, voice=voice, speed=speed, lang="en-us")
            assert sr == 24000
            s = np.asarray(s, np.float32)
            nz = np.where(np.abs(s) > 0.004)[0]
            if len(nz):
                s = s[max(0, nz[0] - 600): nz[-1] + 1800]
            np.save(path, s)
            if i % 20 == 0:
                print("tts", i + 1, len(missing), flush=True)
    return [np.load(p) for _, p in todo]


def resolve(cue, lines):
    m = re.match(r"^(\d+)(?::(.*?))?(?:([+-]\d+(?:\.\d+)?))?$", cue)
    i = int(m.group(1))
    t0, t1, txt = lines[i]
    off = float(m.group(3)) if m.group(3) else 0.0
    w = m.group(2)
    if not w:
        return t0 + off
    if w == "$":
        return t1 + off
    occ = 1
    if "#" in w:
        w, o = w.split("#")
        occ = int(o)
    low = txt.lower()
    p = -1
    for _ in range(occ):
        p = low.find(w.lower(), p + 1)
        assert p >= 0, f"cue word '{w}' not in: {txt}"
    return t0 + (t1 - t0) * p / max(1, len(txt)) + off


CUEKEYS = ("cue", "cue2", "acue", "kcue", "tcue", "x", "iou", "promise", "out", "back", "people", "bank", "pay", "slice", "less", "grow", "totals")


def walk(o, fn):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in CUEKEYS and isinstance(v, str):
                o[k] = fn(v)
            else:
                walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def build(scenes, voice, speed, gap=0.55, scene_gap=1.0, lead=0.5, tail=3.5):
    clips = tts_all(scenes, voice, speed, os.path.join(ROOT, "cache"))
    sr = 24000
    t = lead
    audio, ci, cues, chimes = [], 0, [], []
    state = {"shown": {}, "struck": {}, "totals": None}
    for sc in scenes:
        sc["t0"] = t - (0.25 if sc is not scenes[0] else lead)
        lines = []
        for j, ln in enumerate(sc["say"]):
            clip = clips[ci]
            ci += 1
            d = len(clip) / sr
            lines.append((t, t + d, ln))
            audio.append((t, clip))
            t += d + (gap if j < len(sc["say"]) - 1 else 0)
        t += sc.get("pad", scene_gap)
        sc["lines"] = lines
        local = [(a - sc["t0"], b - sc["t0"], s) for a, b, s in lines]

        def fn(v, local=local, sc=sc):
            r = resolve(v, local)
            cues.append(sc["t0"] + r)
            return r
        walk(sc["P"], fn)
        sc["led0"] = {"shown": dict(state["shown"]), "struck": dict(state["struck"]), "totals": state["totals"]}
        for e in sc["P"].get("ledger", []):
            state["shown"][e["row"]] = -1
            chimes.append(sc["t0"] + e["cue"])
        for e in sc["P"].get("strike", []):
            state["struck"][e["row"]] = -1
        if "totals" in sc["P"]:
            state["totals"] = -1
            chimes.append(sc["t0"] + sc["P"]["totals"])
        caps = []
        for a, b, s in lines:
            words = s.split()
            chunks, cur = [], []
            for w in words:
                cur.append(w)
                if len(cur) >= (5 if PORTRAIT else 9) or (w[-1] in ".?!,:;" and len(cur) >= (3 if PORTRAIT else 4)):
                    chunks.append(" ".join(cur))
                    cur = []
            if cur:
                if chunks and len(cur) <= 2:
                    chunks[-1] += " " + " ".join(cur)
                else:
                    chunks.append(" ".join(cur))
            tot = sum(len(x) for x in chunks)
            acc = 0
            for ch in chunks:
                ca = a + (b - a) * acc / tot
                acc += len(ch)
                cb = a + (b - a) * acc / tot
                caps.append((ca, cb + 0.12, ch.rstrip(",;:")))
        sc["caps"] = caps
    T = t + tail - scene_gap
    for i, sc in enumerate(scenes):
        sc["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else T
    return audio, T, cues, chimes


def frame(c, bg, scenes, T, t):
    sc = next((s for s in scenes if s["t0"] <= t < s["t1"]), scenes[-1])
    c.set_source_surface(bg, 0, 0)
    c.paint()
    lt = t - sc["t0"]
    ledger(c, lt, sc)
    DRAW[sc["kind"]](c, lt, sc["P"])
    cap = next((s for a, b, s in sc["caps"] if a <= t < b), None)
    chrome(c, t, sc, T, cap)


def load(name):
    import importlib
    mod = importlib.import_module(name)
    return mod.get()


def render_scene(args):
    name, idx, out = args
    scenes, voice, speed = load(name)
    audio, T, cues, chimes = build(scenes, voice, speed)
    bg = make_bg()
    sc = scenes[idx]
    f0, f1 = round(sc["t0"] * FPS), round(sc["t1"] * FPS)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "2", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        frame(c, bg, scenes, T, f / FPS)
        surf.flush()
        p.stdin.write(surf.get_data())
    p.stdin.close()
    assert p.wait() == 0
    os.rename(tmp, out)
    return idx


def sfx_click(sr=24000):
    n = int(sr * 0.05)
    x = np.arange(n) / sr
    rng = np.random.default_rng(3)
    return (rng.normal(0, 1, n) * np.exp(-x * 140) * 0.035 + np.sin(2 * np.pi * 900 * x) * np.exp(-x * 110) * 0.03).astype(np.float32)


def sfx_chime(sr=24000):
    n = int(sr * 0.7)
    x = np.arange(n) / sr
    s = np.sin(2 * np.pi * 880 * x) * np.exp(-x * 7) + 0.6 * np.sin(2 * np.pi * 1318.5 * np.maximum(0, x - 0.09)) * np.exp(-np.maximum(0, x - 0.09) * 7) * (x > 0.09)
    return (s * 0.07).astype(np.float32)


def mix_audio(audio, T, cues, chimes, path):
    sr = 24000
    buf = np.zeros(int((T + 0.5) * sr), np.float32)
    for t, clip in audio:
        i = int(t * sr)
        buf[i:i + len(clip)] += clip[: len(buf) - i]
    buf *= 0.85 / np.abs(buf).max()
    click, chime = sfx_click(), sfx_chime()
    last = -1
    cs = set(round(x, 3) for x in chimes)
    for q in sorted(cues):
        if round(q, 3) in cs:
            continue
        if q - last > 0.3:
            i = int(q * sr)
            buf[i:i + len(click)] += click[: len(buf) - i]
            last = q
    for q in chimes:
        i = int(q * sr)
        buf[i:i + len(chime)] += chime[: len(buf) - i]
    buf = np.clip(buf, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())


def main():
    cmd, name = sys.argv[1], sys.argv[2]
    scenes, voice, speed = load(name)
    audio, T, cues, chimes = build(scenes, voice, speed)
    nwords = sum(len(l.split()) for s in scenes for l in s["say"])
    print(f"{name}: {len(scenes)} scenes, {nwords} words, {T:.1f}s = {int(T // 60)}:{int(T % 60):02d}")
    if cmd == "info":
        for i, s in enumerate(scenes):
            print(i, s["kind"], f"{s['t0']:.1f}-{s['t1']:.1f}", (s["say"] or [""])[0][:50])
    elif cmd == "stills":
        bg = make_bg()
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        c = cairo.Context(surf)
        od = sys.argv[3]
        os.makedirs(od, exist_ok=True)
        which = sys.argv[4:]
        for i, s in enumerate(scenes):
            if which and str(i) not in which:
                continue
            for frac, tag in ((0.5, "m"), (0.97, "e")):
                t = s["t0"] + (s["t1"] - s["t0"]) * frac
                frame(c, bg, scenes, T, t)
                surf.write_to_png(f"{od}/{i:02d}{tag}.png")
    elif cmd == "render":
        from multiprocessing import Pool
        od = os.path.join(ROOT, "out", name)
        os.makedirs(od, exist_ok=True)
        jobs = [(name, i, f"{od}/s{i:03d}.mp4") for i in range(len(scenes)) if not os.path.exists(f"{od}/s{i:03d}.mp4")]
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_scene, jobs):
                print("scene", i, flush=True)
        with open(f"{od}/list.txt", "w") as f:
            for i in range(len(scenes)):
                f.write(f"file 's{i:03d}.mp4'\n")
        mix_audio(audio, T, cues, chimes, f"{od}/audio.wav")
        final = sys.argv[3]
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{od}/list.txt", "-i", f"{od}/audio.wav",
                               "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                               "-ar", "48000", "-movflags", "+faststart", "-shortest", final])
        print("wrote", final)


if __name__ == "__main__":
    sys.modules["stmt"] = sys.modules["__main__"]
    main()
