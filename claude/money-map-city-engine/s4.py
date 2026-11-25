import sys, json, os, math, cairo, random, numpy as np
from ss_common import *
from vcommon import *
import s4_content as C

CORK, CORK2 = (0.70, 0.52, 0.34), (0.60, 0.43, 0.27)
PAPERC = (0.99, 0.97, 0.90)
STR = (0.82, 0.14, 0.16)
_bg = None


def bg():
    global _bg
    if _bg is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        c = cairo.Context(s)
        c.set_source_rgb(*CORK)
        c.paint()
        r = random.Random(5)
        for _ in range(2600):
            x, y = r.uniform(0, VW), r.uniform(0, VH)
            c.set_source_rgba(*(CORK2 if r.random() < 0.5 else (0.78, 0.60, 0.42)), 0.55)
            c.arc(x, y, r.uniform(1.5, 5), 0, 6.3)
            c.fill()
        box(c, 0, 0, VW, 26, (0.35, 0.22, 0.12))
        box(c, 0, VH - 26, VW, 26, (0.35, 0.22, 0.12))
        box(c, 0, 0, 26, VH, (0.35, 0.22, 0.12))
        box(c, VW - 26, 0, 26, VH, (0.35, 0.22, 0.12))
        _bg = s
    return _bg


POS = {'you': (290, 328), 'q': (790, 328), 'sale': (540, 563), 'store': (790, 718), 'bank': (290, 718), 'tag': (540, 913)}


def card(c, key, cx, cy, w, h, ang, col, head, big, sub, k, bigcol=INK, dim=1.0, hc=None):
    POS[key] = (cx, cy - h / 2 + 18)
    if k <= 0:
        return
    sc = 0.8 + 0.2 * back(k)
    a = clamp(k * 1.6) * dim
    c.save()
    c.translate(cx, cy + (1 - k) * -40)
    c.rotate(ang)
    c.scale(sc, sc)
    shadow(c, -w / 2, -h / 2, w, h, 6, 0.30 * a, 10)
    box(c, -w / 2, -h / 2, w, h, col, a, 6)
    if head:
        box(c, -w / 2, -h / 2, w, 52, hc or NAVY, a, 6)
        txt(c, head, 0, -h / 2 + 38, 28, WHITE, HEAD, "c", a)
    txt(c, big, 0, 18 if sub else 36, fit(c, big, 70, w - 40, HEAD), bigcol, HEAD, "c", a)
    if sub:
        txt(c, sub, 0, h / 2 - 28, 27, SOFT, BODY, "c", a)
    circle(c, 0, -h / 2 + 2, 15, STR, a, (0.5, 0.05, 0.05), 3)
    circle(c, -4, -h / 2 - 2, 4.5, (1, 0.7, 0.7), a)
    c.restore()


def string(c, k1, k2, prog, a=1.0):
    if prog <= 0:
        return
    (x1, y1), (x2, y2) = POS[k1], POS[k2]
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 50
    c.set_source_rgba(*STR, a)
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    n = 24
    c.move_to(x1, y1)
    for j in range(1, int(n * prog) + 1):
        u = j / n
        x = (1 - u) ** 2 * x1 + 2 * (1 - u) * u * mx + u * u * x2
        y = (1 - u) ** 2 * y1 + 2 * (1 - u) * u * my + u * u * y2
        c.line_to(x, y)
    c.stroke()


def make():
    durs = json.load(open("vo_s4/durs.json"))
    tl, total = timeline(C.L, durs, 0.10, 1.6)
    caps = caps_for(C.L, tl, durs)

    def beat(T):
        i = 0
        while i + 1 < len(tl) and T >= tl[i + 1][0]:
            i += 1
        return i, T - tl[i][0], tl[i][1]

    def draw(c, T):
        c.set_source_surface(bg(), 0, 0)
        c.paint()
        i, t, d = beat(T)
        box(c, 40, 92, 330, 84, NAVY, 0.94, 42)
        logo(c, 62, 112, 0.6)
        txt(c, "MONEY MAP", 116, 147, 31, WHITE, HEAD, "l")
        dim = 1.0 if i < 4 else 0.0
        if i >= 4:
            dim = 0.22 + 0.78 * (1 - e(t, 0.0, 0.4))
        lim = lambda a_: 1.0 if i > a_ else e(t, 0.0, 0.5) if i == a_ else 0.0
        if i >= 1:
            string(c, "sale", "store", e(t, 0.3, 1.0) if i == 1 else 1.0, dim)
        if i >= 2:
            string(c, "store", "bank", e(t, 0.2, 0.9) if i == 2 else 1.0, dim)
            string(c, "bank", "you", e(t, 0.8, 1.4) if i == 2 else 1.0, dim)
        if i >= 3:
            string(c, "store", "tag", e(t, 0.2, 0.9) if i == 3 else 1.0, dim)
        card(c, "you", 290, 400, 380, 180, -0.05, (1.0, 0.95, 0.70), "YOUR CARD", "1.5% BACK", "$1.50 on a $100 sale", back(lim(0)) if i >= 0 else 0, TEAL, dim)
        card(c, "q", 790, 400, 340, 180, 0.06, (1.0, 0.80, 0.78), "THE QUESTION", "WHO PAYS?", "for that $1.50", back(e(t, 0.7, 1.2)) if i == 0 else (1.0 if i > 0 else 0), CORAL, dim)
        card(c, "sale", 540, 610, 330, 130, 0.0, PAPERC, None, "$100 SALE", None, lim(1), INK, dim)
        card(c, "store", 790, 790, 380, 180, 0.04, PAPERC, "THE STORE", "PAYS ~$2.52", "in card fees", lim(1) if i >= 1 else 0, CORAL, dim)
        card(c, "bank", 290, 790, 380, 180, -0.04, PAPERC, "YOUR BANK", "KEEPS ~$1.90", "sends you $1.50", lim(2), TEAL, dim)
        card(c, "tag", 540, 985, 380, 180, 0.05, (0.88, 0.94, 1.0), "THE PRICE TAG", "OFTEN HIGHER", "for every shopper", lim(3), SKY, dim)
        if i == 4:
            k = e(t, 0.3, 0.8)
            c.save()
            c.translate(540, 560); c.rotate(-0.02)
            shadow(c, -430, -250, 860, 500, 8, 0.35 * k, 14)
            box(c, -430, -250, 860, 500, PAPERC, k, 8)
            box(c, -430, -250, 860, 70, NAVY, k, 8)
            txt(c, "ONE ESTIMATE  ·  JULY 2026 PAPER", 0, -200, 32, WHITE, HEAD, "c", k)
            txt(c, "~$30 BILLION A YEAR", 0, -70, fit(c, "~$30 BILLION A YEAR", 92, 800, HEAD), TEAL, HEAD, "c", k)
            box(c, -380, -20, 300, 120, (0.90, 0.92, 0.96), k, 14)
            txt(c, "CASH + DEBIT", -230, 40, 32, INK, HEAD, "c", k)
            txt(c, "shoppers", -230, 80, 28, SOFT, BODY, "c", k)
            box(c, 80, -20, 300, 120, (0.84, 0.95, 0.88), k, 14)
            txt(c, "CARD USERS", 230, 40, 32, TEAL, HEAD, "c", k)
            txt(c, "get the rewards", 230, 80, 28, SOFT, BODY, "c", k)
            arrow(c, -70, 40, 60, 40, NAVY, 10, k, e(t, 0.9, 1.5), 34)
            txt(c, "if stores pass fees into every price", 0, 190, 34, SOFT, BODY, "c", k)
            txt(c, "NBER working paper (Egan et al.)", 0, 235, 26, SOFT, BODY, "c", k)
            c.restore()
        if i == 5:
            k = e(t, 0.1, 0.6)
            c.save()
            c.translate(540, 560); c.rotate(0.02)
            shadow(c, -420, -220, 840, 440, 8, 0.35 * k, 14)
            box(c, -420, -220, 840, 440, (1.0, 0.95, 0.70), k, 8)
            txt(c, "TWO CAVEATS", 0, -140, 56, NAVY, HEAD, "c", k)
            txt(c, "1  Assumes stores pass fees", 0, -60, 40, INK, BODY, "c", k)
            txt(c, "   into every price", 0, -10, 40, INK, BODY, "c", k)
            txt(c, "2  The size shrinks ~25% if", 0, 70, 40, INK, BODY, "c", e(t, 0.7, 1.2))
            txt(c, "   shoppers use different stores", 0, 120, 40, INK, BODY, "c", e(t, 0.7, 1.2))
            c.restore()
        if i == 6:
            k = e(t, 0.0, 0.4)
            box(c, 110, 300, 860, 640, NAVY, 0.96 * k, 30)
            logo(c, 540 - 72, 350, 1.2, k)
            txt(c, "REAL MONEY.", 540, 560, 72, WHITE, HEAD, "c", k)
            txt(c, "NOT FREE MONEY.", 540, 650, 72, GOLD, HEAD, "c", k)
            txt(c, "FULL VIDEO: HOW CREDIT CARD", 540, 740, 36, WHITE, BODY, "c", k)
            txt(c, "REWARDS WORK", 540, 785, 44, GOLD, HEAD, "c", k)
            kk = back(e(t, 0.6, 1.0))
            box(c, 540 - 150, 830, 300, 84, CORAL, clamp(kk), 42)
            txt(c, "FOLLOW", 540, 888, 50, WHITE, HEAD, "c", clamp(kk))
        draw_caption(c, caps, T, bg=(0.17, 0.10, 0.06))

    return draw, tl, total, caps


def cover(path):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    c.set_source_surface(bg(), 0, 0)
    c.paint()
    POS.update({'you': (290, 1030), 'store': (790, 1160), 'tag': (540, 1320)})
    string(c, "you", "store", 1.0)
    string(c, "store", "tag", 1.0)
    card(c, "you", 290, 1112, 380, 180, -0.05, (1.0, 0.95, 0.70), "YOUR CARD", "1.5% BACK", "$1.50 on a $100 sale", 1.0, TEAL)
    card(c, "store", 790, 1242, 380, 180, 0.04, PAPERC, "THE STORE", "PAYS ~$?.??", "in card fees", 1.0, CORAL)
    card(c, "tag", 540, 1402, 400, 180, -0.02, (0.88, 0.94, 1.0), "WHO ELSE?", "? ? ?", "pays for your points", 1.0, SKY)
    box(c, 40, 92, 330, 84, NAVY, 0.94, 42)
    logo(c, 62, 112, 0.6)
    txt(c, "MONEY MAP", 116, 147, 31, WHITE, HEAD, "l")
    box(c, 70, 384, 940, 480, NAVY, 0.96, 28)
    txt(c, "1.5% BACK. BUT", 540, 490, 84, GOLD, HEAD, "c")
    txt(c, "WHO PAYS FOR", 540, 620, 88, WHITE, HEAD, "c")
    txt(c, "YOUR POINTS?", 540, 750, 100, WHITE, HEAD, "c")
    s.write_to_png(path)


def audio(tl, total, caps):
    ev = [(thump(0.45), 0.0, 1.0)]
    for i, b in enumerate(tl):
        if i in (1, 2, 3, 4):
            ev.append((thump(0.3), b[0] + 0.3, 1.0))
        for j in range(3):
            ev.append((noise_hit(i * 17 + j, 0.05, 0.012, 0.09, 6), b[0] + 0.15 + j * 0.2, 1.0))
    def bed(total):
        n = int(total * SR)
        out = np.zeros(n)
        beat = 60 / 96.0
        notes = [220.0, 277.18, 329.63, 415.3, 329.63, 277.18, 246.94, 293.66]
        t = 0.0; k = 0
        while t < total:
            p = tone(notes[k % 8] * 2, beat, 0.010, 5)
            a = int(t * SR); b = min(n, a + len(p))
            out[a:b] += p[:b - a]
            t += beat / 2; k += 1
        out += np.convolve(np.random.RandomState(6).randn(n), np.ones(60) / 60, mode="same") * 0.004
        return out
    write_audio("vo_s4", C.L, tl, total, ev, bed, "s4.wav", caps, "s4.srt")


if __name__ == "__main__":
    cmd = sys.argv[1]
    draw, tl, total, caps = make()
    if cmd == "stills":
        ts_ = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [tl[i][0] + tl[i][1] * 0.85 for i in range(len(tl))]
        stills(draw, ts_, "st_s4")
        print("total", round(total, 2))
    elif cmd == "cover":
        cover("cover_s4.png")
    elif cmd == "render":
        audio(tl, total, caps)
        render(draw, total, "s4_video.mp4")
        print("total", round(total, 2))
