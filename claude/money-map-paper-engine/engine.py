import sys, os, json, math, hashlib, subprocess, re, wave
import numpy as np
import cairo

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30
INK = (0.086, 0.082, 0.059)
CREAM = (0.953, 0.929, 0.878)
CARD = (1.0, 0.992, 0.969)
RED = (0.824, 0.251, 0.169)
GREEN = (0.118, 0.478, 0.290)
GOLD = (0.784, 0.588, 0.180)
MUTED = (0.50, 0.47, 0.40)
BLUE = (0.16, 0.33, 0.60)
COL = {"ink": INK, "red": RED, "green": GREEN, "gold": GOLD, "muted": MUTED, "cream": CREAM, "blue": BLUE}
SERIF = ("Lora", True)
UI = ("Inter", False)
UIB = ("Inter", True)
BLK = ("Inter ExtraBold", False)

SPOKEN = []
KEEP = []


def speak_text(s):
    for a, b in SPOKEN:
        s = s.replace(a, b)
    assert not re.search(r"[0-9$%¢]", s), "unspoken token in: " + s
    return s


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def prog(t, cue, d=0.45):
    return ease((t - cue) / d)


class Layout:
    def __init__(self, portrait):
        self.p = portrait
        self.W, self.H = (1080, 1920) if portrait else (1920, 1080)
        if portrait:
            self.x0, self.x1, self.y0, self.y1 = 70, 1010, 300, 1290
            self.cap_y, self.cap_size, self.cap_words = 1420, 62, 4
        else:
            self.x0, self.x1, self.y0, self.y1 = 130, 1790, 150, 850
            self.cap_y, self.cap_size, self.cap_words = 962, 44, 9
        self.cx = (self.x0 + self.x1) / 2
        self.cy = (self.y0 + self.y1) / 2
        self.cw = self.x1 - self.x0
        self.ch = self.y1 - self.y0


def setfont(c, font, size):
    c.select_font_face(font[0], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if font[1] else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def tw(c, s, font, size, track=0):
    setfont(c, font, size)
    return c.text_extents(s).x_advance + track * max(0, len(s) - 1)


def text(c, s, x, y, size, font=UI, col=INK, align="l", a=1.0, track=0):
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


def card(c, x, y, w, h, fill=CARD, a=1.0, r=18, sh=9, line=4, stroke=INK):
    if sh:
        rrect(c, x + sh, y + sh, w, h, r)
        c.set_source_rgba(*INK, a)
        c.fill()
    rrect(c, x, y, w, h, r)
    c.set_source_rgba(*fill, a)
    c.fill_preserve()
    c.set_source_rgba(*stroke, a)
    c.set_line_width(line)
    c.stroke()


def pill(c, s, x, y, size, bg, fg=CARD, a=1.0, align="c", font=UIB, pad=18):
    w = tw(c, s, font, size) + pad * 2
    h = size * 1.75
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    rrect(c, x, y - h / 2, w, h, h / 2)
    c.set_source_rgba(*bg, a)
    c.fill()
    text(c, s, x + pad, y + size * 0.36, size, font, fg, "l", a)
    return w


def brand_mark(c, x, y, s, a=1.0):
    rrect(c, x, y, s, s, s * 0.22)
    c.set_source_rgba(*INK, a)
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
    c.set_source_rgba(*GREEN, a)
    c.fill()
    c.set_source_rgba(*CREAM, a)
    c.set_line_width(s * 0.04)
    c.move_to(ex - s * 0.055, ey)
    c.line_to(ex - s * 0.012, ey + s * 0.045)
    c.line_to(ex + s * 0.06, ey - s * 0.045)
    c.stroke()


def make_bg(L, dark=False):
    W, H = L.W, L.H
    rng = np.random.default_rng(7)
    base = np.array(INK if dark else CREAM) * 255
    n = rng.normal(0, 3.2 if not dark else 2.0, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2) * (26 if not dark else 10)
    img = np.clip(base[None, None, :] + n - v[..., None], 0, 255).astype(np.uint8)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = img[..., 2], img[..., 1], img[..., 0], 255
    surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H, W * 4)
    KEEP.append(arr)
    return surf


def fmt_money(v, dec=0):
    neg = v < 0
    v = abs(v)
    s = f"{v:,.{dec}f}"
    return ("-$" if neg else "$") + s


# ---------------- scene drawers ----------------

def d_big(c, L, t, P):
    items = P["lines"]
    size = P.get("size", 84 if L.p else 96)
    maxw = L.cw - (0 if L.p else 200)
    blocks = []
    for it in items:
        sz = size * it.get("scale", 1.0)
        f = SERIF if it.get("serif", True) else BLK
        ls = wrap(c, it["t"], f, sz, maxw)
        blocks.append((it, ls, sz, f))
    gap = size * 0.55
    total = sum(len(ls) * sz * 1.18 for _, ls, sz, _ in blocks) + gap * (len(blocks) - 1)
    kick = P.get("kicker")
    y = L.cy - total / 2 + (40 if kick else 0)
    if kick:
        a = prog(t, P.get("kcue", 0))
        pill(c, kick, L.cx, y - 70, 26 if not L.p else 28, RED, CARD, a)
    for it, ls, sz, f in blocks:
        a = prog(t, it["cue"])
        dy = (1 - a) * 36
        col = COL[it.get("col", "ink")]
        for ln in ls:
            y += sz * 1.18
            text(c, ln, L.cx, y - sz * 0.28 + dy, sz, f, col, "c", a)
        if it.get("ul") and a > 0:
            wmax = max(tw(c, ln, f, sz) for ln in ls)
            c.set_source_rgba(*RED, a)
            c.rectangle(L.cx - wmax / 2, y + 10, wmax * prog(t, it["cue"] + 0.15, 0.6), 8)
            c.fill()
        y += gap


def d_stats(c, L, t, P):
    items = P["items"]
    n = len(items)
    title = P.get("title")
    if title:
        text(c, title, L.cx, L.y0 + 60, 44 if not L.p else 46, UIB, MUTED, "c", prog(t, 0), track=3)
    for i, it in enumerate(items):
        a = prog(t, it["cue"])
        if a <= 0:
            continue
        if L.p:
            bw, bh = L.cw, min(330, (L.ch - 150) / n - 30)
            x = L.x0
            y = L.y0 + 130 + i * (bh + 34)
        else:
            bw = (L.cw - 60 * (n - 1)) / n
            bh = 400
            x = L.x0 + i * (bw + 60)
            y = L.cy - bh / 2 + 30
        y += (1 - a) * 40
        card(c, x, y, bw, bh, a=a)
        k = ease_io((t - it["cue"]) / 1.0)
        v = it["v"] * k
        s = it.get("pre", "") + (f"{v:,.{it.get('dec', 0)}f}") + it.get("suf", "")
        size = it.get("size", 130 if not L.p else 120)
        while tw(c, s, BLK, size) > bw - 60:
            size -= 6
        text(c, s, x + bw / 2, y + bh * 0.52, size, BLK, COL[it.get("col", "ink")], "c", a)
        ls = wrap(c, it["label"], UI, 36 if not L.p else 38, bw - 70)
        for j, ln in enumerate(ls):
            text(c, ln, x + bw / 2, y + bh * 0.52 + 66 + j * 46, 36 if not L.p else 38, UI, INK, "c", a)
    note(c, L, t, P)
    src(c, L, t, P)


def note(c, L, t, P):
    ns = [n for n in P.get("notes", []) if t >= n["cue"]]
    if not ns:
        return
    n = ns[-1]
    a = prog(t, n["cue"], 0.35)
    size = 44 if not L.p else 46
    ls = wrap(c, n["t"], SERIF, size, L.cw - 40)
    y = L.y1 - (len(ls) - 1) * size * 1.25 - 6 + (1 - a) * 20
    for i, ln in enumerate(ls):
        text(c, ln, L.cx, y + i * size * 1.25, size, SERIF, COL[n.get("col", "ink")], "c", a)


def src(c, L, t, P):
    if P.get("src"):
        if L.p:
            text(c, P["src"], L.cx, L.y1 + 70, 22, UI, MUTED, "c", prog(t, 0.3))
        else:
            text(c, P["src"], L.x1, L.y1 + 44, 22, UI, MUTED, "r", prog(t, 0.3))


def icon_person(c, x, y, s, col, a):
    c.set_source_rgba(*col, a)
    c.arc(x, y - s * 0.3, s * 0.26, 0, 7)
    c.fill()
    c.arc(x, y + s * 0.5, s * 0.5, math.pi, 2 * math.pi)
    c.fill()


def icon_shop(c, x, y, s, a):
    w = s * 1.5
    c.set_source_rgba(*INK, a)
    c.rectangle(x - w / 2, y - s * 0.05, w, s * 0.6)
    c.fill()
    for i in range(5):
        c.set_source_rgba(*(RED if i % 2 == 0 else CARD), a)
        c.rectangle(x - w / 2 + i * w / 5, y - s * 0.5, w / 5, s * 0.45)
        c.fill()
    c.set_source_rgba(*CARD, a)
    c.rectangle(x - s * 0.16, y + s * 0.15, s * 0.32, s * 0.4)
    c.fill()


def banknote(c, x, y, s, label, a=1.0, col=GREEN):
    w, h = 150 * s, 76 * s
    rrect(c, x - w / 2, y - h / 2, w, h, 10 * s)
    c.set_source_rgba(*col, a)
    c.fill_preserve()
    c.set_source_rgba(*INK, a)
    c.set_line_width(3)
    c.stroke()
    text(c, label, x, y + 13 * s, 36 * s, BLK, CARD, "c", a)


def d_flow(c, L, t, P):
    nodes = P["nodes"]
    pos = {}
    nw, nh = (330, 250) if L.p else (380, 250)
    for k, nd in nodes.items():
        px, py = nd["pp"] if L.p else nd["pl"]
        pos[k] = (px, py)
    bal = {k: nodes[k].get("start", 0) for k in nodes}
    flying = []
    for e in P["events"]:
        if e["type"] != "move":
            continue
        d = e.get("d", 0.8)
        if t >= e["cue"]:
            bal[e["frm"]] -= e["amt"]
            if t >= e["cue"] + d:
                bal[e["to"]] += e["amt"]
            else:
                flying.append((e, (t - e["cue"]) / d))
    for k, nd in nodes.items():
        a = 1.0 if P.get("cont") else prog(t, nd.get("cue", 0))
        if a <= 0:
            continue
        x, y = pos[k]
        y += (1 - a) * 40
        hot = any(e["type"] == "glow" and e["node"] == k and e["cue"] <= t < e["cue"] + e.get("d", 99) for e in P["events"])
        card(c, x - nw / 2, y - nh / 2, nw, nh, a=a, fill=(1.0, 0.93, 0.72) if hot else CARD)
        if nd.get("shop"):
            icon_shop(c, x, y - nh / 2 + 62, 52, a)
        elif nd.get("pot"):
            rrect(c, x - 50, y - nh / 2 + 34, 100, 62, 12)
            c.set_source_rgba(*GOLD, a)
            c.fill_preserve()
            c.set_source_rgba(*INK, a)
            c.set_line_width(4)
            c.stroke()
        else:
            icon_person(c, x, y - nh / 2 + 62, 58, COL[nd.get("col", "blue")], a)
        text(c, nd["label"], x, y + 22, 34, UIB, INK, "c", a, track=2)
        if nd.get("bal"):
            text(c, nd["bal"], x, y + 64, 22, UIB, MUTED, "c", a, track=2)
            text(c, fmt_money(bal[k]), x, y + 112, 46, BLK, INK, "c", a)
        else:
            bs = [e for e in P["events"] if e["type"] == "badge" and e["node"] == k and e["cue"] <= t]
            if bs:
                b = bs[-1]
                ba = prog(t, b["cue"], 0.3)
                pill(c, b["t"], x, y + 82, 28, COL[b.get("col", "ink")], CARD, a * ba)
    coin = P.get("coin")
    if coin and t >= coin["cue"]:
        x, y = coin["pp"] if L.p else coin["pl"]
        a = prog(t, coin["cue"])
        r = 62
        face, sx = "?", 1.0
        for f in coin.get("flips", []):
            if t >= f["cue"]:
                k = (t - f["cue"]) / 0.9
                if k < 1:
                    sx = abs(math.cos(k * math.pi * 5))
                    y -= math.sin(k * math.pi) * 90
                    face = "?"
                else:
                    face = f["r"]
            if "reset" in f and t >= f["reset"]:
                face = "?"
        c.save()
        c.translate(x, y)
        c.scale(max(0.06, sx), 1)
        c.arc(0, 0, r, 0, 7)
        c.set_source_rgba(*GOLD, a)
        c.fill_preserve()
        c.set_source_rgba(*INK, a)
        c.set_line_width(5)
        c.stroke()
        text(c, face[0], 0, 22, 62, BLK, INK, "c", a)
        c.restore()
        if face != "?":
            text(c, face.upper(), x, y + r + 44, 30, UIB, INK, "c", a, track=3)
    for e, k in flying:
        x0, y0 = pos[e["frm"]]
        x1, y1 = pos[e["to"]]
        kk = ease_io(k)
        x = x0 + (x1 - x0) * kk
        y = y0 + (y1 - y0) * kk - math.sin(kk * math.pi) * 70
        banknote(c, x, y, 1.0, fmt_money(e["amt"]), col=COL[e.get("col", "green")])
    note(c, L, t, P)


def d_bars(c, L, t, P):
    bars = P["bars"]
    n = len(bars)
    keys = P["keys"]
    title = P.get("title")
    ta = prog(t, 0)
    if title:
        ls = wrap(c, title, SERIF, 52, L.cw)
        for i, ln in enumerate(ls):
            text(c, ln, L.cx, L.y0 + 50 + i * 62, 52, SERIF, INK, "c", ta)
        top = L.y0 + 60 + len(ls) * 62
    else:
        top = L.y0
    has_note = bool(P.get("notes"))
    base = L.y1 - (125 if has_note else 70)
    hmax = base - top - 105
    vals = [0.0] * n
    tags = [None] * n
    for kf in keys:
        k = ease_io((t - kf["cue"]) / kf.get("d", 0.7))
        if k > 0:
            vals = [v + (nv - v) * k for v, nv in zip(vals, kf["v"])]
            if kf.get("tags"):
                tags = kf["tags"]
    bw = min(230, (L.cw - 80) / n * 0.6)
    step = min((L.cw - 60) / n, bw * 1.9)
    x0 = L.cx - step * (n - 1) / 2
    mx = P["max"]
    c.set_source_rgba(*INK, ta)
    c.rectangle(L.cx - step * n / 2, base, step * n, 5)
    c.fill()
    for i, b in enumerate(bars):
        x = x0 + i * step
        h = hmax * vals[i] / mx
        col = COL[b.get("col", "ink")]
        if h > 1:
            c.set_source_rgba(*INK, 1)
            c.rectangle(x - bw / 2 + 8, base - h + 8, bw, h - 8)
            c.fill()
            c.set_source_rgba(*col, 1)
            c.rectangle(x - bw / 2, base - h, bw, h)
            c.fill_preserve()
            c.set_source_rgba(*INK, 1)
            c.set_line_width(4)
            c.stroke()
            s = P.get("pre", "") + f"{vals[i]:,.{P.get('dec', 0)}f}" + P.get("suf", "")
            text(c, s, x, base - h - 22, 54 if n <= 3 else 44, BLK, INK, "c")
        if tags[i]:
            pill(c, tags[i], x, base - h - 110, 26, INK, CARD)
        lsz = 30 if n <= 3 else 26
        for j, ln in enumerate(b["label"].split("|")):
            text(c, ln, x, base + 46 + j * (lsz + 8), lsz, UIB, INK, "c", ta, track=1)
    note(c, L, t, P)
    src(c, L, t, P)


def d_table(c, L, t, P):
    rows = P["rows"]
    title = P.get("title")
    y = L.y0 + 20
    if title:
        text(c, title, L.cx, y + 44, 50, SERIF, INK, "c", prog(t, 0))
        y += 100
    has_note = bool(P.get("notes"))
    rh = min(128, (L.y1 - y - (130 if has_note else 20)) / len(rows) - 18)
    w = min(L.cw, P.get("w", 1300))
    x = L.cx - w / 2
    fs = min(46, rh * 0.42) if not L.p else min(40, rh * 0.38)
    for r in rows:
        a = prog(t, r["cue"])
        if a > 0:
            yy = y + (1 - a) * 30
            hl = r.get("hl")
            card(c, x, yy, w, rh, a=a, fill=COL[hl] if hl else CARD, sh=7)
            fg = CARD if hl else INK
            cells = r["c"]
            text(c, cells[0], x + 36, yy + rh / 2 + fs * 0.35, fs, UIB, fg, "l", a)
            if len(cells) > 2:
                text(c, cells[1], x + w * 0.62, yy + rh / 2 + fs * 0.35, fs, UI, fg, "r", a)
            text(c, cells[-1], x + w - 36, yy + rh / 2 + fs * 0.35, fs * 1.08, BLK, fg if hl else COL[r.get("col", "ink")], "r", a)
        y += rh + 18
    note(c, L, t, P)
    src(c, L, t, P)


def d_ticket(c, L, t, P):
    legs = P["legs"]
    w = min(L.cw, 760)
    rh = 84 if not L.p else 96
    h = 150 + len(legs) * rh + 150
    a = prog(t, 0)
    x = L.cx - w / 2 - (0 if L.p else P.get("shift", 0))
    y = L.cy - h / 2 + (1 - a) * 50
    card(c, x, y, w, h, a=a, r=14)
    c.set_source_rgba(*INK, a)
    c.rectangle(x, y, w, 96)
    c.fill()
    text(c, P.get("title", "PARLAY TICKET"), x + 36, y + 62, 34, UIB, CARD, "l", a, track=4)
    text(c, P.get("stake", "STAKE $10"), x + w - 36, y + 62, 30, UIB, GOLD, "r", a, track=2)
    yy = y + 130
    for lg in legs:
        la = prog(t, lg["cue"])
        if la > 0:
            text(c, lg["t"], x + 40 + (1 - la) * 30, yy + 52, 36, UIB, INK, "l", la)
            if lg.get("tag"):
                text(c, lg["tag"], x + w - 110, yy + 52, 28, UI, MUTED, "r", la)
            if lg.get("rcue") is not None and t >= lg["rcue"]:
                ra = prog(t, lg["rcue"], 0.3)
                ok = lg["r"] == "ok"
                c.arc(x + w - 60, yy + 40, 26 * (0.6 + 0.4 * ra), 0, 7)
                c.set_source_rgba(*(GREEN if ok else RED), ra)
                c.fill()
                c.set_source_rgba(*CARD, ra)
                c.set_line_width(6)
                cx_, cy_ = x + w - 60, yy + 40
                if ok:
                    c.move_to(cx_ - 12, cy_)
                    c.line_to(cx_ - 3, cy_ + 10)
                    c.line_to(cx_ + 13, cy_ - 9)
                else:
                    c.move_to(cx_ - 10, cy_ - 10)
                    c.line_to(cx_ + 10, cy_ + 10)
                    c.move_to(cx_ + 10, cy_ - 10)
                    c.line_to(cx_ - 10, cy_ + 10)
                c.stroke()
            c.set_source_rgba(*MUTED, 0.5 * la)
            c.set_dash([8, 8])
            c.set_line_width(2)
            c.move_to(x + 30, yy + rh - 6)
            c.line_to(x + w - 30, yy + rh - 6)
            c.stroke()
            c.set_dash([])
        yy += rh
    pay = P.get("pay")
    if pay and t >= pay["cue"]:
        pa = prog(t, pay["cue"])
        text(c, pay["label"], x + 40, yy + 74, 28, UIB, MUTED, "l", pa, track=3)
        text(c, pay["t"], x + w - 40, yy + 84, 64, BLK, COL[pay.get("col", "green")], "r", pa)
    st = P.get("stamp")
    if st and t >= st["cue"]:
        k = prog(t, st["cue"], 0.25)
        c.save()
        c.translate(L.cx - (0 if L.p else P.get("shift", 0)), y + h * 0.55)
        c.rotate(-0.16)
        sc = 1.6 - 0.6 * k
        c.scale(sc, sc)
        sw = tw(c, st["t"], BLK, 110) + 70
        rrect(c, -sw / 2, -80, sw, 160, 16)
        c.set_source_rgba(*COL[st.get("col", "red")], 0.94 * k)
        c.set_line_width(12)
        c.stroke()
        text(c, st["t"], 0, 40, 110, BLK, COL[st.get("col", "red")], "c", 0.94 * k)
        c.restore()
    side = P.get("side")
    if side and not L.p:
        sx = x + w + 90
        sy = L.cy - 120
        for it in side:
            sa = prog(t, it["cue"])
            if sa > 0:
                ls = wrap(c, it["t"], SERIF, 50, L.x1 - sx)
                for ln in ls:
                    text(c, ln, sx, sy + (1 - sa) * 20, 50, SERIF, COL[it.get("col", "ink")], "l", sa)
                    sy += 64
                sy += 30
    note(c, L, t, P)


def d_phone(c, L, t, P):
    pw, ph = (520, 860) if not L.p else (560, 900)
    a = prog(t, 0)
    x = L.cx - pw / 2 - (0 if L.p else 330)
    y = L.cy - ph / 2 + (1 - a) * 50 + (0 if L.p else 20)
    if not L.p:
        sc = L.ch / ph
        c.save()
        c.translate(L.cx - 330, L.cy)
        c.scale(sc, sc)
        c.translate(-(L.cx - 330), -L.cy)
    card(c, x, y, pw, ph, a=a, r=54, fill=INK, sh=10)
    rrect(c, x + 18, y + 18, pw - 36, ph - 36, 40)
    c.set_source_rgba(*CREAM, a)
    c.fill()
    text(c, "BET SLIP", x + pw / 2, y + 110, 34, UIB, INK, "c", a, track=5)
    c.set_source_rgba(*INK, a * 0.15)
    c.rectangle(x + 50, y + 140, pw - 100, 3)
    c.fill()
    text(c, P.get("pick", "Home team to win"), x + 60, y + 220, 34, UIB, INK, "l", a)
    text(c, "Your stake", x + 60, y + 310, 28, UI, MUTED, "l", a)
    card(c, x + 60, y + 335, pw - 120, 110, a=a, sh=0, r=14)
    st = P["stake"]
    if t >= st["cue"]:
        k = min(1.0, (t - st["cue"]) / 0.6)
        s = st["t"][: max(1, int(len(st["t"]) * k + 0.999))]
        text(c, s, x + 90, y + 412, 62, BLK, INK, "l", a)
    b = P["button"]
    pressed = t >= b["cue"]
    card(c, x + 60, y + 490 + (5 if pressed else 0), pw - 120, 100, a=a, fill=GREEN, sh=0 if pressed else 7, r=14)
    text(c, "PLACE BET", x + pw / 2, y + 554 + (5 if pressed else 0), 34, UIB, CARD, "c", a, track=4)
    m = P["msg"]
    if t >= m["cue"]:
        ma = prog(t, m["cue"], 0.3)
        sh = math.sin((t - m["cue"]) * 40) * 8 * max(0, 1 - (t - m["cue"]) * 2.5)
        card(c, x + 44 + sh, y + 630, pw - 88, 170, a=ma, fill=RED, r=16)
        text(c, m["a"], x + pw / 2 + sh, y + 696, 23, UIB, CARD, "c", ma)
        text(c, m["b"], x + pw / 2 + sh, y + 762, 54, BLK, CARD, "c", ma)
    if not L.p:
        c.restore()
        sx = L.cx - 20
        sy = L.cy - 150
        for it in P.get("side", []):
            sa = prog(t, it["cue"])
            if sa > 0:
                ls = wrap(c, it["t"], SERIF, 56, L.x1 - sx)
                for ln in ls:
                    text(c, ln, sx, sy + (1 - sa) * 20, 56, SERIF, COL[it.get("col", "ink")], "l", sa)
                    sy += 72
                sy += 34
    else:
        note(c, L, t, {"notes": [{"t": it["t"], "cue": it["cue"], "col": it.get("col", "ink")} for it in P.get("side", [])]})


def d_list(c, L, t, P):
    items = P["items"]
    y = L.y0 + 10
    if P.get("title"):
        text(c, P["title"], L.cx, y + 50, 54, SERIF, INK, "c", prog(t, 0))
        y += 120
    rh = min(190, (L.y1 - y) / len(items) - 24)
    w = min(L.cw, 1350)
    x = L.cx - w / 2
    for it in items:
        a = prog(t, it["cue"])
        if a > 0:
            xx = x + (1 - a) * 60
            card(c, xx, y, w, rh, a=a)
            c.set_source_rgba(*COL[it.get("col", "red")], a)
            rrect(c, xx + 22, y + 22, rh - 44, rh - 44, 14)
            c.fill()
            text(c, it["n"], xx + rh / 2, y + rh / 2 + 28, 78, BLK, CARD, "c", a)
            text(c, it["h"], xx + rh + 16, y + rh * 0.46, 50 if not L.p else 44, SERIF, INK, "l", a)
            ls = wrap(c, it["s"], UI, 30, w - rh - 50)
            for j, ln in enumerate(ls[:2]):
                text(c, ln, xx + rh + 16, y + rh * 0.46 + 46 + j * 38, 30, UI, MUTED, "l", a)
        y += rh + 24


def d_chapter(c, L, t, P):
    a = prog(t, 0.05, 0.5)
    text(c, P["n"], L.cx, L.cy - 40 + (1 - a) * 40, 240 if not L.p else 260, BLK, RED, "c", a)
    ls = wrap(c, P["title"], SERIF, 84, L.cw)
    a2 = prog(t, 0.3, 0.5)
    for i, ln in enumerate(ls):
        text(c, ln, L.cx, L.cy + 110 + i * 100 + (1 - a2) * 30, 84, SERIF, CREAM, "c", a2)
    c.set_source_rgba(*GOLD, a2)
    wbar = 220 * prog(t, 0.5, 0.6)
    c.rectangle(L.cx - wbar / 2, L.cy + 150 + len(ls) * 100 - 60, wbar, 8)
    c.fill()


def d_end(c, L, t, P):
    a = prog(t, 0.0, 0.5)
    s = 190
    brand_mark(c, L.cx - s / 2, L.cy - 300 + (1 - a) * 30, s, a)
    text(c, "MONEY MAP", L.cx, L.cy - 50, 44, UIB, CREAM, "c", a, track=10)
    a2 = prog(t, P.get("cue", 0.4), 0.5)
    text(c, "Follow the money.", L.cx, L.cy + 110 + (1 - a2) * 30, 110 if not L.p else 100, SERIF, CREAM, "c", a2)
    a3 = prog(t, P.get("cue2", 1.2), 0.5)
    if P.get("next"):
        ls = wrap(c, P["next"], UI, 38, L.cw)
        for i, ln in enumerate(ls):
            text(c, ln, L.cx, L.cy + 215 + i * 50, 38, UI, GOLD, "c", a3)
    pill(c, P.get("cta", "Subscribe for the next case"), L.cx, L.cy + 350, 32, RED, CARD, a3)


DRAW = {"big": d_big, "stats": d_stats, "flow": d_flow, "bars": d_bars, "table": d_table, "ticket": d_ticket,
        "phone": d_phone, "list": d_list, "chapter": d_chapter, "end": d_end}
DARK = {"chapter", "end"}


def chrome(c, L, t, sc, T, cap):
    dark = sc["kind"] in DARK
    fg = CREAM if dark else INK
    if L.p:
        brand_mark(c, 70, 150, 64)
        text(c, "MONEY MAP", 150, 194, 28, UIB, fg, "l", track=5)
        if sc.get("tag"):
            text(c, sc["tag"], L.x1, 194, 24, UIB, RED if not dark else GOLD, "r", track=3)
        c.set_source_rgba(*fg, 0.9)
        c.rectangle(70, 236, L.W - 140, 3)
        c.fill()
        text(c, "18+ · EXAMPLES ONLY · NOT BETTING ADVICE", 70, 272, 20, UIB, MUTED, "l", track=2)
    else:
        brand_mark(c, L.x1 - 56, 44, 56)
        text(c, "MONEY MAP", L.x1 - 76, 82, 24, UIB, fg, "r", track=5)
        if sc.get("tag"):
            text(c, sc["tag"], L.x0, 82, 24, UIB, RED if not dark else GOLD, "l", track=4)
        c.set_source_rgba(*fg, 0.9)
        c.rectangle(L.x0, 116, L.cw, 3)
        c.fill()
        text(c, "18+ · EXAMPLES ONLY · NOT BETTING ADVICE", L.x0, L.H - 34, 18, UIB, MUTED, "l", track=2)
    c.set_source_rgba(*RED, 1)
    c.rectangle(0, L.H - 8, L.W * t / T, 8)
    c.fill()
    if cap:
        size = L.cap_size
        ls = wrap(c, cap, UIB, size, L.cw - (0 if L.p else 300))
        y = L.cap_y - (len(ls) - 1) * size * 0.65
        for i, ln in enumerate(ls):
            w = tw(c, ln, UIB, size)
            yy = y + i * size * 1.3
            rrect(c, L.cx - w / 2 - 26, yy - size * 0.98, w + 52, size * 1.42, 14)
            c.set_source_rgba(*(CREAM if dark else INK), 1)
            c.fill()
            text(c, ln, L.cx, yy, size, UIB, INK if dark else CREAM, "c")


# ---------------- timeline ----------------

def tts_all(scenes, voice, speed, cache):
    os.makedirs(cache, exist_ok=True)
    todo = []
    for sc in scenes:
        for ln in sc["say"]:
            sp = speak_text(ln)
            h = hashlib.md5(f"{voice}|{speed}|{sp}".encode()).hexdigest()[:16]
            todo.append((sp, os.path.join(cache, h + ".npy")))
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
            print("tts", i + 1, len(missing), flush=True)
    return [np.load(p) for _, p in todo]


def resolve(cue, lines):
    if isinstance(cue, (int, float)) and not isinstance(cue, bool):
        return None
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


def walk(o, fn):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("cue", "rcue", "kcue", "cue2", "reset") and isinstance(v, str):
                o[k] = fn(v)
            else:
                walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def build(scenes, voice, speed, L, gap=0.36, scene_gap=0.7, lead=0.5, tail=3.0):
    clips = tts_all(scenes, voice, speed, os.path.join(ROOT, "cache"))
    sr = 24000
    t = lead
    audio = []
    ci = 0
    cues = []
    for sc in scenes:
        sc["t0"] = t - (0.25 if sc is not scenes[0] else lead)
        lines = []
        if not sc["say"]:
            t += sc.get("hold", 2.0)
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
        caps = []
        for a, b, s in lines:
            words = s.split()
            chunks, cur = [], []
            for w in words:
                cur.append(w)
                if len(cur) >= L.cap_words or (w[-1] in ".?!,:;" and len(cur) >= max(2, L.cap_words // 2)):
                    chunks.append(" ".join(cur))
                    cur = []
            if cur:
                if chunks and len(cur) == 1:
                    chunks[-1] += " " + cur[0]
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
    return audio, T, cues


def frame(c, L, bgs, scenes, T, t):
    sc = next(s for s in scenes if s["t0"] <= t < s["t1"]) if t < T else scenes[-1]
    c.set_source_surface(bgs[sc["kind"] in DARK], 0, 0)
    c.paint()
    DRAW[sc["kind"]](c, L, t - sc["t0"], sc["P"])
    cap = next((s for a, b, s in sc["caps"] if a <= t < b), None)
    chrome(c, L, t, sc, T, cap)


def render_scene(args):
    name, portrait, idx, out = args
    import importlib
    mod = importlib.import_module("content")
    scenes, voice, speed = mod.get(name)
    L = Layout(portrait)
    audio, T, cues = build(scenes, voice, speed, L)
    bgs = {False: make_bg(L), True: make_bg(L, True)}
    sc = scenes[idx]
    f0, f1 = round(sc["t0"] * FPS), round(sc["t1"] * FPS)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, L.W, L.H)
    c = cairo.Context(surf)
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{L.W}x{L.H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "2", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        frame(c, L, bgs, scenes, T, f / FPS)
        surf.flush()
        p.stdin.write(surf.get_data())
    p.stdin.close()
    assert p.wait() == 0
    os.rename(tmp, out)
    return idx


def sfx_tick(sr=24000):
    n = int(sr * 0.06)
    x = np.arange(n) / sr
    return (np.sin(2 * np.pi * 1500 * x) * np.exp(-x * 90) * 0.05).astype(np.float32)


def sfx_thump(sr=24000):
    n = int(sr * 0.5)
    x = np.arange(n) / sr
    return (np.sin(2 * np.pi * (70 + 40 * np.exp(-x * 14)) * x) * np.exp(-x * 9) * 0.22).astype(np.float32)


def mix_audio(audio, T, cues, scenes, path):
    sr = 24000
    buf = np.zeros(int((T + 0.5) * sr), np.float32)
    for t, clip in audio:
        i = int(t * sr)
        buf[i:i + len(clip)] += clip[: len(buf) - i]
    pk = np.abs(buf).max()
    buf *= 0.85 / pk
    tick, thump = sfx_tick(), sfx_thump()
    last = -1
    for q in sorted(cues):
        if q - last > 0.3:
            i = int(q * sr)
            buf[i:i + len(tick)] += tick[: len(buf) - i]
            last = q
    for sc in scenes:
        if sc["kind"] == "chapter":
            i = int((sc["t0"] + 0.05) * sr)
            buf[i:i + len(thump)] += thump[: len(buf) - i]
    buf = np.clip(buf, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())


def main():
    import importlib
    cmd, name = sys.argv[1], sys.argv[2]
    portrait = name != "long"
    mod = importlib.import_module("content")
    scenes, voice, speed = mod.get(name)
    L = Layout(portrait)
    audio, T, cues = build(scenes, voice, speed, L)
    nwords = sum(len(l.split()) for s in scenes for l in s["say"])
    print(f"{name}: {len(scenes)} scenes, {nwords} words, {T:.1f}s = {int(T // 60)}:{int(T % 60):02d}")
    if cmd == "info":
        for i, s in enumerate(scenes):
            print(i, s["kind"], f"{s['t0']:.1f}-{s['t1']:.1f}", (s["say"] or [""])[0][:50])
    elif cmd == "stills":
        bgs = {False: make_bg(L), True: make_bg(L, True)}
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, L.W, L.H)
        c = cairo.Context(surf)
        od = sys.argv[3]
        os.makedirs(od, exist_ok=True)
        which = sys.argv[4:]
        for i, s in enumerate(scenes):
            if which and str(i) not in which:
                continue
            for frac, tag in ((0.5, "m"), (0.97, "e")):
                t = s["t0"] + (s["t1"] - s["t0"]) * frac
                frame(c, L, bgs, scenes, T, t)
                surf.write_to_png(f"{od}/{i:02d}{tag}.png")
    elif cmd == "render":
        from multiprocessing import Pool
        od = os.path.join(ROOT, "out", name)
        os.makedirs(od, exist_ok=True)
        jobs = [(name, portrait, i, f"{od}/s{i:03d}.mp4") for i in range(len(scenes)) if not os.path.exists(f"{od}/s{i:03d}.mp4")]
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_scene, jobs):
                print("scene", i, flush=True)
        with open(f"{od}/list.txt", "w") as f:
            for i in range(len(scenes)):
                f.write(f"file 's{i:03d}.mp4'\n")
        mix_audio(audio, T, cues, scenes, f"{od}/audio.wav")
        final = sys.argv[3]
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{od}/list.txt", "-i", f"{od}/audio.wav",
                               "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                               "-ar", "48000", "-movflags", "+faststart", "-shortest", final])
        print("wrote", final)


if __name__ == "__main__":
    sys.modules["engine"] = sys.modules["__main__"]
    main()
