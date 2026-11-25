import sys, json, os, math, cairo, numpy as np
from ss_common import *
from vcommon import *
import s1_content as C

TMONO = "Liberation Mono"
DESK = (0.13, 0.20, 0.22)
TAPE = (0.995, 0.985, 0.95)
BEIGE = (0.88, 0.84, 0.76)
RED = (0.80, 0.12, 0.12)
BLACK = (0.10, 0.10, 0.12)
GREEN = (0.10, 0.55, 0.35)
LH = 78
HEADY = 1010

ENTRIES = [
    (0, 0.35, "RAISE", "?", BLACK),
    (1, 0.45, "COLA 2027", "3.6%", BLACK),
    (2, 0.22, "AVG 2026", "2,095.00", BLACK),
    (2, 0.68, "AVG 2027", "2,170.00", BLACK),
    (3, 0.25, "RAISE", "+75.00", GREEN),
    (4, 0.50, "PART B UP", "-6.50", RED),
    (6, 0.42, "NET RAISE", "68.50*", BLACK),
    (7, 0.45, "PART B/MO", "-209.40", RED),
    (8, 0.12, "CHECK", "2,170.00", BLACK),
    (8, 0.40, "PART B", "-209.40", RED),
    (8, 0.70, "LANDS", "1,960.60*", GREEN),
]

_bg = {}


def desk():
    if "d" in _bg:
        return _bg["d"]
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.17, 0.26, 0.28)
    g.add_color_stop_rgb(1, 0.09, 0.14, 0.16)
    c.set_source(g)
    c.paint()
    rg = np.random.RandomState(4)
    for i in range(0, VH, 3):
        c.set_source_rgba(1, 1, 1, 0.012 + 0.012 * rg.rand())
        c.rectangle(0, i, VW, 1)
        c.fill()
    for i in range(0, VW, 5):
        c.set_source_rgba(0, 0, 0, 0.02 * rg.rand())
        c.rectangle(i, 0, 2, VH)
        c.fill()
    r = cairo.RadialGradient(540, 800, 200, 540, 900, 1200)
    r.add_color_stop_rgba(0, 0, 0, 0, 0)
    r.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    c.set_source(r)
    c.paint()
    # machine body
    shadow(c, 60, 1060, 960, 900, 60, 0.5, 20)
    g = cairo.LinearGradient(0, 1060, 0, 1920)
    g.add_color_stop_rgb(0, 0.93, 0.90, 0.83)
    g.add_color_stop_rgb(1, 0.74, 0.70, 0.62)
    rr(c, 60, 1060, 960, 900, 60)
    c.set_source(g)
    c.fill()
    box(c, 200, 1040, 680, 70, (0.20, 0.20, 0.22), 1, 18)
    box(c, 230, 1060, 620, 20, (0.05, 0.05, 0.06), 1, 8)
    for j in range(5):
        for i in range(4):
            x, y = 150 + i * 150, 1400 + j * 100
            box(c, x, y + 8, 120, 80, (0.25, 0.25, 0.28), 1, 14)
            box(c, x, y, 120, 80, (0.38, 0.38, 0.42) if (i < 3) else (0.70, 0.22, 0.18), 1, 14)
            lab = ["7", "8", "9", "-", "4", "5", "6", "+", "1", "2", "3", "=", "0", "00", ".", "*", "C", "%", "T", "S"][j * 4 + i]
            txt(c, lab, x + 60, y + 54, 40, (0.95, 0.94, 0.90), TMONO, "c")
    box(c, 790, 1400, 160, 480, (0.25, 0.25, 0.28), 1, 18)
    box(c, 800, 1390, 140, 480, (0.33, 0.33, 0.36), 1, 18)
    line(c, [(830, 1500), (910, 1500)], (0.7, 0.7, 0.7), 4)
    line(c, [(830, 1560), (910, 1560)], (0.7, 0.7, 0.7), 4)
    _bg["d"] = s
    return s


def entry_time(tl, i, fr):
    t0, d = tl[i]
    return t0 + d * fr


def draw_tape(c, T, tl, final=False):
    times = [entry_time(tl, i, fr) for (i, fr, *_ ) in ENTRIES]
    printed = [k for k, tt in enumerate(times) if T >= tt]
    off = 0.0
    for k in printed:
        off += LH * ease_out((T - times[k]) / 0.22)
    tx, tw_ = 250, 580
    shadow(c, tx, -40, tw_, HEADY + 80, 4, 0.35, 10)
    box(c, tx, -40, tw_, HEADY + 80, TAPE, 1, 0)
    c.set_source_rgba(0.75, 0.72, 0.65, 0.4)
    c.set_line_width(1)
    for k in range(-1, 30):
        y = HEADY - 40 - off % LH - k * LH
        c.move_to(tx + 10, y + 0.5)
        c.line_to(tx + tw_ - 10, y + 0.5)
    c.stroke()
    for n, k in enumerate(printed):
        i, fr, lab, val, col = ENTRIES[k]
        later = sum(LH * ease_out((T - times[m]) / 0.22) for m in printed if m > k)
        y = HEADY - 50 - later
        if y < -60:
            continue
        a = clamp((T - times[k]) / 0.12)
        txt(c, lab, tx + 26, y, 44, BLACK, TMONO, "l", a)
        txt(c, val, tx + tw_ - 26, y, 46, col, TMONO, "r", a)
        if val.endswith("*"):
            c.set_source_rgba(*BLACK, 0.6 * a)
            c.set_dash([6, 6])
            c.set_line_width(2)
            c.move_to(tx + 20, y - 54)
            c.line_to(tx + tw_ - 20, y - 54)
            c.stroke()
            c.set_dash([])
    box(c, 200, HEADY + 20, 680, 40, (0.20, 0.20, 0.22), 1, 12)


def pill(c, s, sub, col, k, y=560, w=620):
    if k <= 0:
        return
    sc = 0.7 + 0.3 * back(k)
    c.save()
    c.translate(540, y)
    c.scale(sc, sc)
    shadow(c, -w / 2, -110, w, 220, 30, 0.4 * clamp(k), 12)
    box(c, -w / 2, -110, w, 220, col, clamp(k), 30)
    txt(c, s, 0, 30, 120, WHITE, HEAD, "c", clamp(k))
    if sub:
        txt(c, sub, 0, 84, 38, WHITE, BODY, "c", clamp(k))
    c.restore()


def make():
    durs = json.load(open("vo_s1/durs.json"))
    tl, total = timeline(C.L, durs, 0.10, 1.6)
    caps = caps_for(C.L, tl, durs)

    def beat(T):
        i = 0
        while i + 1 < len(tl) and T >= tl[i + 1][0]:
            i += 1
        return i, T - tl[i][0], tl[i][1]

    def draw(c, T):
        c.set_source_surface(desk(), 0, 0)
        c.paint()
        i, t, d = beat(T)
        draw_tape(c, T, tl)
        box(c, 36, 92, 330, 84, NAVY, 0.94, 42)
        logo(c, 58, 112, 0.6)
        txt(c, "MONEY MAP", 112, 147, 31, WHITE, HEAD, "l")
        if i == 0:
            k = 1 - e(t, d - 0.3, d)
            box(c, 130, 400, 820, 330, NAVY, 0.95 * k, 26)
            txt(c, "SOCIAL SECURITY RAISE: +$75", 540, 500, 48, GOLD, HEAD, "c", k)
            txt(c, "HOW MUCH", 540, 600, 92, WHITE, HEAD, "c", k)
            txt(c, "ACTUALLY ARRIVES?", 540, 690, 70, WHITE, HEAD, "c", k)
        if i == 3:
            pill(c, "+$75", "A MONTH, AVERAGE RETIREE", GREEN, e(t, 0.1, 0.5) * (1 - e(t, d - 0.25, d)))
        if i == 4:
            pill(c, "+$6.50", "MEDICARE PART B, 2027", RED, e(t, 0.6 * d, 0.6 * d + 0.4) * (1 - e(t, d - 0.25, d)))
        if i == 5:
            k = e(t, 0.2, 0.5)
            box(c, 150, 420, 780, 260, RED, 0.94 * k, 24)
            txt(c, "PART B PREMIUM", 540, 520, 60, WHITE, HEAD, "c", k)
            txt(c, "TAKEN OUT OF THE CHECK", 540, 600, 46, WHITE, BODY, "c", k)
            arrow(c, 540, 690, 540, 860, RED, 12, k, e(t, 0.5, 1.0), 40)
        if i == 6:
            pill(c, "$68.50", "THE RAISE YOU SEE", NAVY, e(t, 0.5 * d, 0.5 * d + 0.4) * (1 - e(t, d - 0.25, d)), 520, 700)
        if i == 8:
            k = e(t, 0.78 * d, 0.78 * d + 0.4)
            pill(c, "$1,960", "LANDS IN THE BANK (AVERAGE)", GREEN, k, 480, 760)
        if i == 9:
            k = e(t, 0.0, 0.4)
            box(c, 110, 360, 860, 560, NAVY, 0.95 * k, 30)
            logo(c, 540 - 60 * 1.2, 410, 1.2, k)
            txt(c, "FOLLOW THE MONEY.", 540, 600, 64, WHITE, HEAD, "c", k)
            txt(c, "FULL VIDEO:", 540, 690, 40, GOLD, BODY, "c", k)
            txt(c, "HOW SOCIAL SECURITY WORKS", 540, 745, 46, GOLD, HEAD, "c", k)
            kk = back(e(t, 0.6, 1.0))
            box(c, 540 - 150, 800, 300, 84, CORAL, clamp(kk), 42)
            txt(c, "FOLLOW", 540, 858, 50, WHITE, HEAD, "c", clamp(kk))
            k2 = e(t, d - 0.6, d)
            if k2 > 0:
                box(c, 130, 400, 820, 330, NAVY, k2, 26)
                txt(c, "SOCIAL SECURITY RAISE: +$75", 540, 500, 48, GOLD, HEAD, "c", k2)
                txt(c, "HOW MUCH", 540, 600, 92, WHITE, HEAD, "c", k2)
                txt(c, "ACTUALLY ARRIVES?", 540, 690, 70, WHITE, HEAD, "c", k2)
        draw_caption(c, caps, T)
        note = "Average retired worker, standard Part B premium (SSA, CMS 2027)"
        if i >= 2:
            txt(c, note, 540, 1375, 26, (0.85, 0.85, 0.85), BODY, "c", 0.9, bold=False)

    return draw, tl, total, caps


def cover(path):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    c.set_source_surface(desk(), 0, 0)
    c.paint()
    tx, tw_ = 250, 580
    box(c, tx, -40, tw_, HEADY + 80, TAPE, 1, 0)
    rows = [("AVG 2027", "2,170.00", BLACK), ("RAISE", "+75.00", GREEN), ("PART B", "-???", RED), ("LANDS", "?,???.??", BLACK)]
    for k, (a1, b1, col) in enumerate(rows):
        y = HEADY - 50 - (len(rows) - 1 - k) * LH
        txt(c, a1, tx + 26, y, 44, BLACK, TMONO, "l")
        txt(c, b1, tx + tw_ - 26, y, 46, col, TMONO, "r")
    box(c, 200, HEADY + 20, 680, 40, (0.20, 0.20, 0.22), 1, 12)
    box(c, 36, 92, 330, 84, NAVY, 0.94, 42)
    logo(c, 58, 112, 0.6)
    txt(c, "MONEY MAP", 112, 147, 31, WHITE, HEAD, "l")
    box(c, 110, 384, 860, 300, NAVY, 0.96, 28)
    txt(c, "YOUR $75 RAISE.", 540, 470, 66, GOLD, HEAD, "c")
    txt(c, "HOW MUCH LANDS?", 540, 600, fit(c, "HOW MUCH LANDS?", 96, 800, HEAD), WHITE, HEAD, "c")
    s.write_to_png(path)


def audio(tl, total, caps):
    ev = []
    ev.append((thump(0.45), 0.0, 1.0))
    times = [entry_time(tl, i, fr) for (i, fr, *_ ) in ENTRIES]
    for k, tt in enumerate(times):
        for j in range(4):
            ev.append((noise_hit(k * 7 + j, 0.03, 0.004, 0.10), tt - 0.25 + j * 0.06, 1.0))
        ev.append((noise_hit(k + 50, 0.08, 0.02, 0.12, 8), tt, 1.0))
        ev.append((noise_hit(k + 90, 0.22, 0.06, 0.05, 30), tt + 0.02, 1.0))
        if ENTRIES[k][3].endswith("*"):
            ev.append((tone(1760, 0.8, 0.10, 5) + np.pad(tone(2637, 0.6, 0.05, 6), (0, int(0.2 * SR))), tt + 0.15, 1.0))
    for i, beat in enumerate(tl):
        if i in (3, 4, 6):
            ev.append((thump(0.35), beat[0] + beat[1] * (0.1 if i == 3 else 0.5 if i == 6 else 0.6), 1.0))

    def bed(total):
        n = int(total * SR)
        out = np.zeros(n)
        beat = 60 / 92.0
        notes = [220.0, 261.63, 329.63, 392.0, 329.63, 261.63, 196.0, 246.94]
        t = 0.0
        k = 0
        while t < total:
            p = tone(notes[k % 8] * 2, beat, 0.010, 5)
            a = int(t * SR)
            b = min(n, a + len(p))
            out[a:b] += p[:b - a]
            t += beat / 2
            k += 1
        out += np.convolve(np.random.RandomState(2).randn(n), np.ones(60) / 60, mode="same") * 0.004
        return out

    write_audio("vo_s1", C.L, tl, total, ev, bed, "s1.wav", caps, "s1.srt")


if __name__ == "__main__":
    cmd = sys.argv[1]
    draw, tl, total, caps = make()
    if cmd == "stills":
        ts_ = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [tl[i][0] + tl[i][1] * 0.8 for i in range(len(tl))] + [0.0, 0.5, 1.0, 2.0]
        stills(draw, ts_, "st_s1")
        print("total", round(total, 2))
    elif cmd == "cover":
        cover("cover_s1.png")
    elif cmd == "render":
        audio(tl, total, caps)
        render(draw, total, "s1_video.mp4")
        print("total", round(total, 2))
