import sys, json, os, math, cairo, numpy as np
from ss_common import *
from vcommon import *
import s3_content as C

BG1, BG2 = (0.04, 0.14, 0.24), (0.06, 0.30, 0.38)
WATER, WATER2 = (0.20, 0.62, 0.90), (0.12, 0.45, 0.78)
GL = (0.80, 0.93, 1.0)
TX, TY, TW_, TH_ = 230, 370, 620, 520


def sim():
    b, apr = 3000.0, 0.22
    bal, ci, cp = [b], [0.0], [0.0]
    while b > 0.005 and len(bal) < 400:
        i = b * apr / 12
        pay = min(max(35, i + 0.01 * b), b + i)
        b = b + i - pay
        bal.append(max(0, b)); ci.append(ci[-1] + i); cp.append(cp[-1] + pay)
    return bal, ci, cp


BAL, CI, CP = sim()
NM = len(BAL) - 1


def at(arr, m):
    m = clamp(m, 0, NM)
    a = int(m)
    b = min(NM, a + 1)
    return arr[a] + (arr[b] - arr[a]) * (m - a)


_bg = None


def bg():
    global _bg
    if _bg is None:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        c = cairo.Context(s)
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, *BG1)
        g.add_color_stop_rgb(1, *BG2)
        c.set_source(g)
        c.paint()
        c.set_source_rgba(1, 1, 1, 0.05)
        c.set_line_width(2)
        for y in range(0, VH, 80):
            c.move_to(0, y); c.line_to(VW, y)
        c.stroke()
        _bg = s
    return _bg


def tank(c, T, level, drain=0.0, drip=0.0, mid=None):
    shadow(c, TX, TY, TW_, TH_, 36, 0.35, 14)
    box(c, TX, TY, TW_, TH_, (0.10, 0.22, 0.33), 1, 36, GL, 6)
    c.save()
    rr(c, TX + 6, TY + 6, TW_ - 12, TH_ - 12, 30)
    c.clip()
    top = TY + TH_ - 14 - (TH_ - 28) * clamp(level)
    for lay, (col, ph, amp) in enumerate(((WATER2, 0.0, 9), (WATER, 1.6, 7))):
        c.move_to(TX, TY + TH_)
        for x in range(0, TW_ + 8, 8):
            c.line_to(TX + x, top + amp * math.sin(x / 55.0 + T * 2.2 + ph) + lay * 6)
        c.line_to(TX + TW_, TY + TH_)
        c.close_path()
        c.set_source_rgba(*col, 0.92)
        c.fill()
    c.restore()
    for i, lb in enumerate(("$3,000", "$2,000", "$1,000", "$0")):
        y = TY + 14 + (TH_ - 28) * i / 3
        c.set_source_rgba(1, 1, 1, 0.55)
        c.set_line_width(3)
        c.move_to(TX + TW_ - 50, y); c.line_to(TX + TW_ - 8, y)
        c.stroke()
        txt(c, lb, TX + TW_ + 16, y + 11, 30, (0.85, 0.93, 1.0), BODY, "l", 0.9)
    box(c, TX + 20, TY + 20, 22, TH_ - 40, (1, 1, 1), 0.10, 11)
    return top


def pipe_and_tap(c, T, flow, dripk):
    box(c, 90, 310, 280, 38, (0.55, 0.60, 0.70), 1, 10)
    box(c, 90, 310, 38, 110, (0.55, 0.60, 0.70), 1, 10)
    box(c, TX + TW_ - 10, TY + TH_ - 70, 110, 34, (0.55, 0.60, 0.70), 1, 10)
    box(c, TX + TW_ + 90, TY + TH_ - 70, 34, 120, (0.55, 0.60, 0.70), 1, 10)
    if dripk > 0:
        for j in range(3):
            ph = (T * 1.4 + j / 3.0) % 1.0
            y = 430 + ph * (TY + 140 - 430)
            circle(c, 109, y, 15, CORAL, dripk * (1 - ph * 0.3))
    if flow > 0:
        for j in range(3):
            ph = (T * 1.1 + j / 3.0) % 1.0
            y = TY + TH_ - 36 + ph * 120
            circle(c, TX + TW_ + 107, y + 14, 11, (0.4, 0.85, 0.55), flow * (1 - ph * 0.4))


def pill(c, s, sub, col, k, y, w=760):
    if k <= 0:
        return
    sc = 0.85 + 0.15 * back(k)
    c.save()
    c.translate(540, y)
    c.scale(sc, sc)
    shadow(c, -w / 2, -80, w, 160, 30, 0.3 * k, 8)
    box(c, -w / 2, -80, w, 160, col, clamp(k * 1.5), 30)
    txt(c, s, 0, 18, fit(c, s, 78, w - 60, HEAD), WHITE, HEAD, "c", clamp(k * 1.5))
    txt(c, sub, 0, 60, 30, (1, 1, 1), BODY, "c", clamp(k * 1.5) * 0.9)
    c.restore()


def chips(c, T, borrowed, interest, paid, k):
    if k <= 0:
        return
    items = (("BORROWED", borrowed, SKY), ("INTEREST", interest, CORAL), ("PAID SO FAR", paid, TEAL))
    for j, (lb, v, col) in enumerate(items):
        x = 50 + j * 335
        box(c, x, 985, 315, 128, col, 0.95 * k, 24)
        txt(c, lb, x + 157, 1025, 30, WHITE, BODY, "c", k)
        txt(c, money_fmt(v), x + 157, 1090, 56, WHITE, HEAD, "c", k)


def make():
    durs = json.load(open("vo_s3/durs.json"))
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
        box(c, 36, 92, 330, 84, NAVY, 0.94, 42)
        logo(c, 58, 112, 0.6)
        txt(c, "MONEY MAP", 112, 147, 31, WHITE, HEAD, "l")
        level, flow, dripk, m = 1.0, 0.0, 0.0, 0.0
        chk = 0.0
        if i == 1:
            flow = e(t, 0.2, 0.6)
        if i == 2:
            flow = 1.0; dripk = e(t, 0.0, 0.4); m = 1 * e(t, 0.3, d)
        if i == 3:
            flow = 1.0; dripk = 1.0; m = 1 + 11 * e(t, 0.2, d - 0.2)
        if i >= 4:
            flow = 1.0; dripk = 1.0
            m = 12 + (NM - 12) * ease(e(t, 0.0, d * 0.9)) if i == 4 else NM
            if i == 5 or i == 6:
                m = NM
        if i >= 7:
            m = NM
        level = at(BAL, m) / 3000.0
        if i >= 7:
            flow = 0; dripk = 0
        pipe_and_tap(c, T, flow, dripk)
        tank(c, T, level)
        if i == 0:
            k = 1 - e(t, d - 0.3, d)
            box(c, 120, 440, 840, 300, NAVY, 0.94 * k, 28)
            txt(c, "$3,000 ON A CARD", 540, 530, 52, GOLD, HEAD, "c", k)
            txt(c, "MINIMUM ONLY.", 540, 625, 78, WHITE, HEAD, "c", k)
            txt(c, "HOW LONG?", 540, 710, 70, GOLD, HEAD, "c", k)
        if i == 1:
            pill(c, "MINIMUM: ~$86", "MONTH ONE", NAVY, e(t, 0.3, 0.7), 560)
        if i == 2:
            k = e(t, 0.2, 0.7)
            pill(c, "$56 INTEREST", "goes straight to the bank", CORAL, k, 520, 720)
            pill(c, "$30 PAYS DEBT", "the only part that lowers the tank", TEAL, e(t, 1.2, 1.7), 720, 720)
        if i == 3:
            pill(c, "ONLY ~$340 CLEARED", "after 12 months of minimums", NAVY, e(t, 0.4, 0.9), 560)
        if i >= 4:
            yrs = m / 12.0
            lab = ("MONTH %d" % round(m)) if i == 4 else "ABOUT 12 YEARS"
            box(c, 90, 895, 900, 80, NAVY, 0.92, 24)
            txt(c, "MONTH %d  ·  %.1f YEARS" % (round(m), yrs) if i == 4 else "MONTH %d  ·  ABOUT 12 YEARS" % NM, 540, 953, 48, WHITE, HEAD, "c")
        if i >= 4:
            ck = 1.0 if i >= 4 else 0.0
            chips(c, T, 3000, at(CI, m), at(CP, m), ck)
        if i == 5:
            k = e(t, 0.5, 1.0)
            box(c, 140, 440, 800, 240, CORAL, 0.95 * k, 28)
            txt(c, "~$4,000 INTEREST", 540, 550, 66, WHITE, HEAD, "c", k)
            txt(c, "on a $3,000 balance", 540, 625, 40, WHITE, BODY, "c", k)
        if i == 6:
            k = e(t, 0.3, 0.8)
            box(c, 120, 440, 840, 280, NAVY, 0.95 * k, 28)
            txt(c, "$7,000 PAID", 540, 560, 84, GOLD, HEAD, "c", k)
            txt(c, "for $3,000 of stuff", 540, 650, 44, WHITE, BODY, "c", k)
        if i == 7:
            k = e(t, 0.1, 0.5)
            box(c, 110, 420, 860, 330, WHITE, 0.95 * k, 26)
            txt(c, "ROUGH EXAMPLE", 540, 510, 40, NAVY, HEAD, "c", k)
            txt(c, "22% APR · min = interest + 1%", 540, 580, 38, SOFT, BODY, "c", k)
            txt(c, "$35 floor · no new purchases", 540, 635, 38, SOFT, BODY, "c", k)
            txt(c, "YOUR CARD'S RULES WILL DIFFER", 540, 705, 34, CORAL, HEAD, "c", k)
        if i == 8:
            k = e(t, 0.0, 0.4)
            box(c, 110, 330, 860, 600, NAVY, 0.96 * k, 30)
            logo(c, 540 - 72, 380, 1.2, k)
            txt(c, "FOLLOW THE MONEY.", 540, 570, 64, WHITE, HEAD, "c", k)
            txt(c, "FULL VIDEO:", 540, 660, 40, GOLD, BODY, "c", k)
            txt(c, "HOW CREDIT CARD", 540, 725, 46, GOLD, HEAD, "c", k)
            txt(c, "REWARDS WORK", 540, 780, 46, GOLD, HEAD, "c", k)
            kk = back(e(t, 0.6, 1.0))
            box(c, 540 - 150, 830, 300, 84, CORAL, clamp(kk), 42)
            txt(c, "FOLLOW", 540, 888, 50, WHITE, HEAD, "c", clamp(kk))
        draw_caption(c, caps, T, bg=(0.02, 0.06, 0.12))

    return draw, tl, total, caps


def cover(path):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    c.set_source_surface(bg(), 0, 0)
    c.paint()
    c.save()
    c.translate(0, 600)
    tank(c, 0.0, 0.93)
    pipe_and_tap(c, 0.3, 1.0, 1.0)
    c.restore()
    box(c, 36, 92, 330, 84, NAVY, 0.94, 42)
    logo(c, 58, 112, 0.6)
    txt(c, "MONEY MAP", 112, 147, 31, WHITE, HEAD, "l")
    box(c, 70, 384, 940, 470, NAVY, 0.96, 28)
    txt(c, "MINIMUM PAYMENT ONLY.", 540, 480, fit(c, "MINIMUM PAYMENT ONLY.", 58, 820, HEAD), GOLD, HEAD, "c")
    txt(c, "HOW LONG UNTIL", 540, 610, 84, WHITE, HEAD, "c")
    txt(c, "$3,000 IS GONE?", 540, 740, fit(c, "$3,000 IS GONE?", 96, 820, HEAD), WHITE, HEAD, "c")
    s.write_to_png(path)


def audio(tl, total, caps):
    ev = [(thump(0.45), 0.0, 1.0)]
    for i, b in enumerate(tl):
        if i in (1, 2, 4, 6):
            ev.append((thump(0.35), b[0] + 0.3, 1.0))
        for j in range(5):
            ev.append((noise_hit(i * 11 + j, 0.09, 0.03, 0.05, 20), b[0] + 0.2 + j * 0.25, 1.0))
    def bed(total):
        n = int(total * SR)
        out = np.zeros(n)
        beat = 60 / 88.0
        notes = [196.0, 246.94, 293.66, 349.23, 293.66, 246.94, 220.0, 261.63]
        t = 0.0; k = 0
        while t < total:
            p = tone(notes[k % 8] * 2, beat, 0.010, 5)
            a = int(t * SR); b = min(n, a + len(p))
            out[a:b] += p[:b - a]
            t += beat / 2; k += 1
        out += np.convolve(np.random.RandomState(4).randn(n), np.ones(60) / 60, mode="same") * 0.004
        return out
    write_audio("vo_s3", C.L, tl, total, ev, bed, "s3.wav", caps, "s3.srt")


if __name__ == "__main__":
    cmd = sys.argv[1]
    draw, tl, total, caps = make()
    if cmd == "stills":
        ts_ = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [tl[i][0] + tl[i][1] * 0.8 for i in range(len(tl))] + [0.0]
        stills(draw, ts_, "st_s3")
        print("total", round(total, 2))
    elif cmd == "cover":
        cover("cover_s3.png")
    elif cmd == "render":
        audio(tl, total, caps)
        render(draw, total, "s3_video.mp4")
        print("total", round(total, 2))
