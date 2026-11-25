import sys, json, os, math, cairo, numpy as np
from ss_common import *
from vcommon import *
import s2_content as C

NEWS = (0.935, 0.915, 0.865)
INKB = (0.08, 0.08, 0.09)
RED = (0.76, 0.12, 0.12)
GREYT = (0.45, 0.44, 0.42)
MAST = "Cardo"
HL = "Gelasio"
KICK = "Liberation Sans Narrow"
FIG = "Bitter"

BEATS = [
    ("PAYCHECK MYSTERY", ("WHERE DOES", "YOUR 6.2% GO?")),
    ("BY THE NUMBERS", ("$3,720 A YEAR", "FROM YOU")),
    ("AND THEN", ("YOUR EMPLOYER", "MATCHES IT")),
    ("NOT WHAT YOU THINK", ("NO ACCOUNT WITH", "YOUR NAME ON IT")),
    ("WHERE IT GOES", ("IT PAYS THIS", "MONTH'S CHECKS")),
    ("THE SPLIT", ("85¢ RETIREMENT,", "15¢ DISABILITY")),
    ("WHAT YOU GET", ("CREDITS, NOT", "A BALANCE")),
    ("THE FINISH LINE", ("40 CREDITS AND", "YOU QUALIFY")),
    ("BOTTOM LINE", ("TODAY'S CHECKS.", "YOUR SPOT LATER.")),
]

_bg = {}


def paper():
    if "p" in _bg:
        return _bg["p"]
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    c.set_source_rgb(*NEWS)
    c.paint()
    rg = np.random.RandomState(8)
    for _ in range(9000):
        c.set_source_rgba(0.3, 0.25, 0.15, rg.uniform(0.01, 0.05))
        c.rectangle(rg.uniform(0, VW), rg.uniform(0, VH), 1.5, 1.5)
        c.fill()
    txt(c, "THE PAYCHECK POST", 540, 172, fit(c, "THE PAYCHECK POST", 96, 960, MAST), INKB, MAST, "c")
    for y, w in ((60, 3), (70, 1), (200, 1), (212, 4)):
        box(c, 50, y, 980, w, INKB)
    txt(c, "2027 EDITION", 60, 248, 26, INKB, KICK, "l")
    txt(c, "WHERE YOUR MONEY GOES", 540, 248, 26, INKB, KICK, "c")
    txt(c, "PRICE: 6.2%", 1020, 248, 26, INKB, KICK, "r")
    box(c, 50, 262, 980, 2, INKB)
    # body text columns (texture)
    for col in range(3):
        x0 = 50 + col * 335
        for j in range(60):
            y = 1360 + j * 22
            if y > VH - 20:
                break
            w = 300 if j % 9 != 8 else rg.uniform(80, 220)
            box(c, x0, y, w, 9, GREYT, 0.35)
        if col < 2:
            box(c, x0 + 318, 1350, 1, 560, INKB, 0.5)
    box(c, 50, 1340, 980, 3, INKB)
    for side in range(2):
        x0 = 50 if side == 0 else 830
        pass
    g = cairo.RadialGradient(540, 960, 500, 540, 960, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.25, 0.18, 0.05, 0.28)
    c.set_source(g)
    c.paint()
    box(c, 0, 958, VW, 3, (0, 0, 0), 0.06)
    _bg["p"] = s
    return s


def halftone_box(c, x, y, w, h, a=1.0):
    box(c, x, y, w, h, (0.97, 0.96, 0.92), a, 0, INKB, 3)
    c.set_source_rgba(*INKB, 0.07 * a)
    for j in range(0, int(h), 14):
        for i in range(0, int(w), 14):
            r = 2.2 + 1.6 * math.sin(i * 0.02 + j * 0.015)
            c.arc(x + i + 7, y + j + 7, max(0.5, r), 0, 2 * math.pi)
            c.fill()


def headline(c, beat, t, k_out=0.0):
    kick, (l1, l2) = BEATS[beat]
    k = e(t, 0.0, 0.25) * (1 - k_out)
    sc = 1.0 + 0.05 * (1 - e(t, 0, 0.3))
    c.save()
    c.translate(540, 450)
    c.scale(sc, sc)
    w = tw(c, kick, 34, KICK) + 40
    box(c, -w / 2, -150, w, 50, RED, k, 4)
    txt(c, kick, 0, -113, 34, WHITE, KICK, "c", k)
    s1 = fit(c, l1, 92, 940, HL)
    s2 = fit(c, l2, 92, 940, HL)
    sz = min(s1, s2)
    txt(c, l1, 0, -10, sz, INKB, HL, "c", k)
    txt(c, l2, 0, 90, sz, INKB, HL, "c", k)
    c.restore()


def photo(c, beat, t, d, T):
    x, y, w, h = 90, 620, 900, 460
    k = e(t, 0.05, 0.3)
    halftone_box(c, x, y, w, h, k)
    cx = 540
    if beat == 0:
        box(c, 190, 660, 700, 380, WHITE, k, 6, INKB, 2)
        txt(c, "PAY STUB", 220, 715, 36, INKB, KICK, "l", k)
        rows = [("GROSS PAY", "$5,000.00"), ("FEDERAL TAX", "-$..."), ("SOCIAL SECURITY 6.2%", "-$310.00"), ("MEDICARE 1.45%", "-$72.50")]
        for j, (a1, b1) in enumerate(rows):
            txt(c, a1, 220, 790 + j * 64, 36, INKB, FIG, "l", k)
            txt(c, b1, 860, 790 + j * 64, 36, INKB, FIG, "r", k)
        kk = e(t, 0.6, 1.4)
        if kk > 0:
            c.save()
            c.translate(540, 905)
            c.scale(1, 0.16)
            c.new_path()
            c.arc(0, 0, 370, -math.pi * 0.6, -math.pi * 0.6 + 2.1 * math.pi * kk)
            c.restore()
            c.set_source_rgba(*RED, 0.9)
            c.set_line_width(8)
            c.stroke()
    elif beat == 1:
        txt(c, "SALARY", cx, 720, 44, GREYT, KICK, "c", k)
        txt(c, "$60,000", cx, 820, 96, INKB, FIG, "c", k)
        kk = e(t, 0.5, 1.0)
        txt(c, "x 6.2% =", cx, 900, 50, RED, FIG, "c", kk)
        txt(c, cnt(0, 3720, e(t, 0.8, 2.0)), cx, 1020, 110, RED, FIG, "c", kk)
    elif beat == 2:
        for i, (lab, col) in enumerate((("YOU", INKB), ("EMPLOYER", INKB))):
            bx = 260 + i * 340
            kk = back(e(t, 0.1 + i * 0.5, 0.5 + i * 0.5))
            if kk > 0:
                for j in range(6):
                    box(c, bx - 100, 960 - j * 26, 200, 22, (0.55, 0.72, 0.55), clamp(kk), 3, INKB, 2)
                txt(c, lab, bx, 720, 40, INKB, KICK, "c", clamp(kk))
                txt(c, "$3,720", bx, 1040, 52, INKB, FIG, "c", clamp(kk))
            if i == 0:
                txt(c, "+", 430, 900, 90, GREYT, FIG, "c", e(t, 0.4, 0.6))
        txt(c, "=", 745, 900, 80, GREYT, FIG, "c", e(t, 1.0, 1.3))
        kk = back(e(t, 1.2, 1.7))
        if kk > 0:
            txt(c, "$7,440", 885, 905, 60, RED, FIG, "c", clamp(kk))
            txt(c, "A YEAR", 885, 960, 34, RED, KICK, "c", clamp(kk))
    elif beat == 3:
        box(c, 270, 700, 540, 330, (0.86, 0.80, 0.62), k, 8, INKB, 3)
        box(c, 270, 670, 220, 50, (0.86, 0.80, 0.62), k, 8, INKB, 3)
        txt(c, "SAVINGS: YOUR NAME", 540, 860, 44, INKB, FIG, "c", k)
        kk = e(t, 0.4, 0.7)
        line(c, [(300, 845), (780, 845)], RED, 10, kk)
        stamp(c, 540, 980, "NOT A SAVINGS ACCOUNT", RED, e(t, 0.8, 1.1), 44, -0.06, KICK)
    elif beat == 4:
        for i in range(3):
            kk = back(e(t, 0.1 + i * 0.1, 0.4 + i * 0.1))
            if kk > 0:
                person(c, 190 + i * 80, 920, 1.0, INKB, clamp(kk))
        txt(c, "WORKERS", 270, 1030, 34, INKB, KICK, "c", k)
        for j in range(3):
            q = (T * 0.8 + j / 3) % 1.0
            coin(c, lerp(380, 640, q), 860 - math.sin(q * math.pi) * 40, 20)
        for i in range(3):
            kk = back(e(t, 0.5 + i * 0.1, 0.8 + i * 0.1))
            if kk > 0:
                elder(c, 730 + i * 80, 920, 1.0, INKB, clamp(kk))
        txt(c, "RETIREES & MORE", 810, 1030, 34, INKB, KICK, "c", k)
        kk = e(t, 0.9, 1.3)
        txt(c, "NEARLY 72 MILLION", cx, 730, 64, RED, FIG, "c", kk)
        txt(c, "PEOPLE PAID", cx, 785, 36, INKB, KICK, "c", kk)
    elif beat == 5:
        pc, py, r = 360, 850, 180
        kk = e(t, 0.2, 1.2)
        a0 = -math.pi / 2
        a1 = a0 + 2 * math.pi * 0.855 * kk
        c.move_to(pc, py)
        c.arc(pc, py, r, a0, a1)
        c.close_path()
        c.set_source_rgba(*INKB, 0.85)
        c.fill()
        if kk > 0.99:
            c.move_to(pc, py)
            c.arc(pc, py, r, a1, a0 + 2 * math.pi)
            c.close_path()
            c.set_source_rgba(*RED, 0.95)
            c.fill()
        k2 = e(t, 0.8, 1.2)
        txt(c, "85¢", 760, 820, 96, INKB, FIG, "c", k2)
        txt(c, "RETIREMENT + SURVIVORS", 760, 870, 30, INKB, KICK, "c", k2)
        k3 = e(t, 1.6, 2.0)
        txt(c, "15¢", 760, 990, 80, RED, FIG, "c", k3)
        txt(c, "DISABILITY", 760, 1035, 30, RED, KICK, "c", k3)
    elif beat == 6:
        txt(c, "$1,970 EARNED = 1 CREDIT", cx, 740, 54, INKB, FIG, "c", k)
        txt(c, "(2027)", cx, 790, 32, GREYT, KICK, "c", k)
        for i in range(4):
            kk = back(e(t, 0.8 + i * 0.35, 1.1 + i * 0.35))
            bx = 230 + i * 160
            box(c, bx, 840, 130, 130, WHITE, 1, 10, INKB, 4)
            if kk > 0:
                c.save()
                c.translate(bx + 65, 905)
                c.scale(clamp(kk, 0, 1.2), clamp(kk, 0, 1.2))
                line(c, [(-35, 0), (-8, 28), (38, -32)], RED, 14)
                c.restore()
        txt(c, "MAX 4 A YEAR", cx, 1040, 40, RED, KICK, "c", e(t, 2.0, 2.4))
    elif beat in (7, 8):
        n = int(e(t, 0.2, d * 0.7) * 40) if beat == 7 else 40
        for i in range(40):
            r, q = divmod(i, 10)
            bx, by = 175 + q * 74, 690 + r * 74
            box(c, bx, by, 62, 62, RED if i < n else WHITE, 1, 6, INKB, 3)
        txt(c, "%d / 40 CREDITS" % n, cx, 1040, 50, INKB, FIG, "c", k)
        kk = e(t, d * 0.7, d * 0.7 + 0.3) if beat == 7 else e(t, 0.3, 0.6)
        lab = "ABOUT 10 YEARS" if beat == 7 else "QUALIFIED"
        w = tw(c, lab, 60, KICK) + 70
        box(c, 540 - w / 2, 790, w, 96, INKB, kk, 10)
        txt(c, lab, 540, 860, 60, WHITE, KICK, "c", kk)


def make():
    durs = json.load(open("vo_s2/durs.json"))
    tl, total = timeline(C.L, durs, 0.10, 1.8)
    caps = caps_for(C.L, tl, durs)

    def beat(T):
        i = 0
        while i + 1 < len(tl) and T >= tl[i + 1][0]:
            i += 1
        return i, T - tl[i][0], tl[i][1]

    def draw(c, T):
        c.set_source_surface(paper(), 0, 0)
        c.paint()
        i, t, d = beat(T)
        last = i == len(tl) - 1
        if last and t > d - 1.0:
            kk = e(t, d - 1.0, d - 0.7)
            c.push_group()
            headline(c, 0, 9)
            photo(c, 0, 9, 9, T)
            c.pop_group_to_source()
            c.paint_with_alpha(kk)
            if kk < 1:
                c.push_group()
                headline(c, i, t)
                photo(c, i, t, d, T)
                c.pop_group_to_source()
                c.paint_with_alpha(1 - kk)
        else:
            headline(c, i, t if i > 0 else max(t, 0.3))
            photo(c, i, t if i > 0 else t + 0.3, d, T)
        if last:
            k = e(t, 0.3, 0.6) * (1 - e(t, d - 1.0, d - 0.7))
            box(c, 90, 1130, 900, 210, INKB, 0.95 * k, 10)
            txt(c, "FULL STORY: HOW SOCIAL SECURITY WORKS", 540, 1195, 38, WHITE, KICK, "c", k)
            logo(c, 170, 1228, 0.8, k)
            txt(c, "MONEY MAP", 240, 1290, 50, WHITE, HEAD, "l", k)
            box(c, 690, 1238, 250, 74, CORAL, k, 37)
            txt(c, "FOLLOW", 815, 1290, 42, WHITE, HEAD, "c", k)
        else:
            draw_caption(c, caps, T, BODY, (0.08, 0.08, 0.09), WHITE, GOLD, 1130)

    return draw, tl, total, caps


def cover(path):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(s)
    c.set_source_surface(paper(), 0, 0)
    c.paint()
    photo(c, 0, 9, 9, 0)
    c.save()
    c.translate(540, 450)
    w = tw(c, "PAYCHECK MYSTERY", 34, KICK) + 40
    box(c, -w / 2, -150, w, 50, RED, 1, 4)
    txt(c, "PAYCHECK MYSTERY", 0, -113, 34, WHITE, KICK, "c")
    txt(c, "6.2% OF YOUR PAY.", 0, -10, 84, INKB, HL, "c")
    txt(c, "WHERE DOES IT GO?", 0, 90, 84, RED, HL, "c")
    c.restore()
    s.write_to_png(path)


def audio(tl, total, caps):
    ev = [(thump(0.4), 0.0, 1.0)]
    for i, (t0, d) in enumerate(tl):
        ev.append((noise_hit(i + 3, 0.35, 0.08, 0.06, 40), t0 - 0.05, 1.0))
        ev.append((thump(0.25), t0 + 0.02, 1.0))
        if i in (3, 7, 8):
            ev.append((thump(0.4), t0 + (0.8 if i == 3 else (d * 0.7 if i == 7 else 0.3)), 1.0))

    def bed(total):
        n = int(total * SR)
        out = np.zeros(n)
        beat = 60 / 100.0
        prog = [(174.61, 220.0, 261.63), (146.83, 174.61, 220.0), (130.81, 164.81, 196.0), (146.83, 196.0, 246.94)]
        t, k = 0.0, 0
        while t < total:
            ch = prog[(k // 4) % 4]
            f = ch[k % 3] * (2 if k % 2 else 1)
            p = tone(f, beat * 0.9, 0.011, 6)
            a = int(t * SR)
            b = min(n, a + len(p))
            out[a:b] += p[:b - a]
            t += beat / 2
            k += 1
        out += np.convolve(np.random.RandomState(5).randn(n), np.ones(60) / 60, mode="same") * 0.004
        return out

    write_audio("vo_s2", C.L, tl, total, ev, bed, "s2.wav", caps, "s2.srt")


if __name__ == "__main__":
    cmd = sys.argv[1]
    draw, tl, total, caps = make()
    if cmd == "stills":
        ts_ = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [tl[i][0] + tl[i][1] * 0.8 for i in range(len(tl))] + [0.0, 0.5, 1.0, 2.0]
        stills(draw, ts_, "st_s2")
        print("total", round(total, 2))
    elif cmd == "cover":
        cover("cover_s2.png")
    elif cmd == "render":
        audio(tl, total, caps)
        render(draw, total, "s2_video.mp4")
        print("total", round(total, 2))
