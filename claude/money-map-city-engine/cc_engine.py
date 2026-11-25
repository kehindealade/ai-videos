import cairo, math, json, os, sys, subprocess
from cc_common import *
from cc_common import e as e_

TAIL = 3.6
PATHS_R = {k + "_r": list(reversed(v)) for k, v in PATHS.items()}
PATHS.update(PATHS_R)

CITY = (9.5, 7.0, 0.80, 585)
SHOPC = (4.6, 8.6, 1.70, 640)
HOOKC = (4.4, 9.0, 2.0, 720)
ISSC = (15.0, 6.9, 1.30, 640)
NETC = (10.9, 3.2, 1.25, 640)
ACQC = (4.2, 3.6, 1.20, 640)
HOMEC = (4.0, 10.6, 1.55, 640)
MIDC = (10.0, 7.0, 0.95, 600)
POSE = {
    ("hook", 0): HOOKC, ("hook", 1): HOOKC, ("hook", 2): HOOKC, ("hook", 3): CITY,
    ("play", 0): CITY, ("play", 1): CITY, ("play", 2): CITY, ("play", 3): CITY, ("play", 4): SHOPC,
    ("swipe", 0): SHOPC, ("swipe", 1): CITY, ("swipe", 2): ISSC, ("swipe", 3): SHOPC,
    ("split", 0): ISSC, ("split", 1): ISSC, ("split", 2): ISSC, ("split", 3): NETC, ("split", 4): ACQC, ("split", 5): SHOPC, ("split", 6): SHOPC,
    ("rew", 0): ISSC, ("rew", 1): MIDC, ("rew", 2): ISSC, ("rew", 3): ISSC, ("rew", 4): ISSC, ("rew", 5): HOMEC,
    ("pays", 0): SHOPC, ("pays", 1): SHOPC, ("pays", 2): SHOPC, ("pays", 3): CITY, ("pays", 4): CITY, ("pays", 5): CITY, ("pays", 6): SHOPC,
    ("other", 0): ISSC, ("other", 1): ISSC, ("other", 2): ISSC, ("other", 3): ISSC, ("other", 4): ISSC, ("other", 5): ISSC, ("other", 6): ISSC, ("other", 7): ISSC, ("other", 8): ISSC,
    ("year", 0): CITY, ("year", 1): CITY, ("year", 2): CITY,
    ("pts", 0): HOMEC, ("pts", 1): HOMEC, ("pts", 2): HOMEC,
    ("recap", 0): CITY, ("recap", 1): CITY, ("recap", 2): CITY, ("recap", 3): CITY,
}


# ------------------------------------------------------------------ helpers
def bstamp(c, s, x, y, col, k, size=64, ang=-0.07, bg=None):
    if k <= 0:
        return
    sc = 1 + 0.5 * (1 - ease(k * 2.4))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(sc, sc)
    w = tw(c, s, size, HEAD) + 64
    a = min(1, k * 4)
    if bg:
        box(c, -w / 2, -size * 0.82, w, size * 1.3, bg, a, 14)
    c.set_line_width(8)
    c.set_source_rgba(*col, a)
    rr(c, -w / 2, -size * 0.82, w, size * 1.3, 14)
    c.stroke()
    T(c, s, 0, size * 0.30, size, col, HEAD, "c", a)
    c.restore()


def mover(c, name, k, label, col=GOLD, h=0.55, tc=INK, s=1.0, a=1.0):
    x, y = on_path(name, k)
    packet(c, x, y, h, label, col, a, s, tc)
    return x, y


def dot_on(c, name, k, col, r=14, a=1.0, h=0.5):
    x, y = on_path(name, k)
    X, Y = P(x, y, h)
    z = CAM["z"]
    circle(c, X, Y, r * z * 1.3, col, a * 0.25)
    circle(c, X, Y, r * z, col, a, WHITE, 3)


def draw_world(c, tt, extras=(), plates=None, cars=True):
    ground(c, tt)
    objs = []
    for tx, ty in [(0.5, 13), (7, 13.2), (1, 4.3), (7.2, 0.5), (9.5, 5.6), (12, 6.5), (10.5, 8), (9.4, 12), (12.5, 11.5), (16, 11), (18.5, 12.5),
                   (16.5, 1.5), (19, 3.2), (13.2, 5.4), (13, 8.2), (15.4, 9.6), (18.6, 9.6), (9.5, 0.6), (13.4, 1.0), (18, 0.8), (1, 8.8), (6.8, 9.8)]:
        objs.append((tx + ty, lambda c, tx=tx, ty=ty: tree(c, tx, ty)))
    if cars:
        for i, (col, sp, ph) in enumerate([((0.92, 0.35, 0.30), 0.9, 0.0), ((0.30, 0.60, 0.90), 0.7, 0.4), ((0.95, 0.80, 0.20), 0.8, 0.7)]):
            u = (tt * sp * 0.05 + ph) % 1.0
            x = 0.5 + u * (GW - 1)
            objs.append((x + 9.5, lambda c, x=x, col=col: car(c, x, 9.5, True, col)))
        u = (tt * 0.04 + 0.2) % 1.0
        objs.append((8.5 + u * 13, lambda c, u=u: car(c, 8.5, 0.5 + u * 13, False, (0.55, 0.45, 0.85))))
    objs.append((BLD["home"][0] + BLD["home"][1] + 2, lambda c: bld_home(c)))
    objs.append((BLD["shop"][0] + BLD["shop"][1] + 3, lambda c: bld_shop(c)))
    objs.append((BLD["acq"][0] + BLD["acq"][1] + 3, lambda c: bld_acq(c, tt)))
    objs.append((BLD["net"][0] + BLD["net"][1] + 2, lambda c: bld_net(c, tt)))
    objs.append((BLD["iss"][0] + BLD["iss"][1] + 3, lambda c: bld_iss(c, tt)))
    for d, f in extras:
        objs.append((d, f))
    for d, f in sorted(objs, key=lambda o: o[0]):
        f(c)
    if plates:
        for k, v in plates.items():
            x, y, w, dd, h = BLD[k]
            up = {"net": 1.7, "home": 1.7, "shop": 0.55, "acq": 1.1, "iss": 1.5}[k]
            off = {"acq": (-150, -10), "net": (90, -10), "iss": (40, 0), "shop": (-90, 0), "home": (-50, 0)}[k]
            plate(c, NAME[k], x + w / 2, y + dd / 2, h + up, v[0], SUB[k] if v[1] else None, num=v[2] if len(v) > 2 else None, dx=off[0], dy=off[1])


def banner(c, l1, l2=None, a=1.0, y=40, col=NAVY, size=64):
    w1 = tw(c, l1, size, HEAD)
    w2 = tw(c, l2, size, HEAD) if l2 else 0
    w = max(w1, w2) + 90
    h = 100 + (size + 22 if l2 else 0)
    x = 960 - w / 2
    yy = y + (1 - ease(a)) * -50
    shadow(c, x, yy, w, h, 26, 0.28 * a, 10)
    box(c, x, yy, w, h, col, a, 26)
    T(c, l1, 960, yy + 80, size, WHITE, HEAD, "c", a)
    if l2:
        T(c, l2, 960, yy + 80 + size + 18, size, GOLD, HEAD, "c", a)


def ledger(c, vals, k=1.0, hl=-1):
    names = ["YOUR BANK", "NETWORK", "STORE'S BANK", "STORE GETS"]
    cols = [C_ISS, C_NET, C_ACQ, C_SHOP]
    x0, w, h = 140, 390, 110
    y = 920 + (1 - ease(k)) * 200
    box(c, 110, y - 30, 1700, 170, NAVY, 0.94 * k, 28)
    for i in range(4):
        x = x0 + i * 420
        v = vals[i]
        on = v is not None
        bg = cols[i] if on else (0.20, 0.25, 0.42)
        if hl == i:
            box(c, x - 8, y - 6, w + 16, h + 12, GOLD, 1, 24)
        box(c, x, y, w, h, bg, 1, 20)
        T(c, names[i], x + w / 2, y + 36, 26, WHITE, BODY, "c", 0.92)
        T(c, v if on else "?", x + w / 2, y + 90, 54, WHITE, HEAD, "c")


def coin_stack_at(c, x, y, n, a=1.0, h0=0.0):
    for i in range(n):
        coin_at(c, x, y, h0 + i * 0.12, 22, a)


def whole_ids():
    return {"home": (1, True, 1), "shop": (1, True, 2), "acq": (1, True, 3), "net": (1, True, 4), "iss": (1, True, 5)}


# ------------------------------------------------------------------ scenes
def s_hook(c, t, st, gt, d):
    ex = []
    if st <= 2:
        ex.append((3.4 + 9.6, lambda c: person_b(c, 3.4, 9.6, (0.25, 0.55, 0.85), 1.0, 1.0, card=True, wave=math.sin(gt * 5) * 0.5)))
        ex.append((5.4 + 9.0, lambda c: person_b(c, 5.4, 9.0, (0.70, 0.42, 0.78), 1.0, 1.0, cash=True)))

        def term(c):
            ibox(c, 4.2, 9.1, 0.55, 0.45, 0.6, (0.30, 0.34, 0.45))
            X, Y = P(4.5, 9.35, 0.68)
            circle(c, X, Y, 10 * CAM["z"], (0.5, 1.0, 0.7) if (gt % 1.6) < 0.8 else (0.3, 0.7, 0.5))
        ex.append((4.5 + 9.3, term))
        draw_world(c, gt, ex, cars=False)
        XA, YA = P(3.4, 9.6, 2.45)
        XB, YB = P(5.4, 9.0, 2.45)
        k1 = back(e_(gt, 0.15, 0.7))
        pill(c, XA, YA - 20 * (1 - k1), "+$1.50 BACK", 46, WHITE, GREEN, k1, HEAD)
        k2 = back(e_(gt, 0.6, 1.2))
        pill(c, XB, YB - 20 * (1 - k2), "+$0", 46, WHITE, (0.45, 0.48, 0.58), k2, HEAD)
        XT, YT = P(4.5, 9.3, 2.0)
        c.save()
        c.translate(XT, YT)
        c.rotate(math.sin(gt * 2.2) * 0.05)
        box(c, -110, -56, 220, 112, (1.0, 0.97, 0.88), 1, 14, (0.8, 0.7, 0.4), 3)
        T(c, "JACKET", 0, -8, 30, SOFT, BODY, "c")
        T(c, "$100", 0, 42, 56, INK, HEAD, "c")
        c.restore()
        if st < 2:
            banner(c, "SAME $100 JACKET.", "ONE GETS $1.50 BACK.", e_(gt, 0, 0.25), 150)
        else:
            banner(c, "SAME $100. WHO PAYS", "FOR THE $1.50?", e_(t, 0, 0.3), 150, RED)
            q = 1 + 0.12 * math.sin(gt * 6)
            T(c, "?", XA + 20, YA + 190, 130 * q, GOLD, HEAD, "c", 0.95, stroke=NAVY, sw=10)
    else:
        draw_world(c, gt + 4, [], cars=True)
        coin_at(c, 4.0, 9.0, 0.4 + 0.5 * abs(math.sin(gt * 3)), 36, 1.0, "$100")
        banner(c, "FOLLOW THE $100", None, e_(t, 0.2, 0.6), 150)


def s_play(c, t, st, gt, d):
    ids = {}
    seq = {0: [], 1: ["home", "shop", "acq"], 2: ["home", "shop", "acq", "net", "iss"], 3: ["home", "shop", "acq", "net", "iss"], 4: ["home", "shop"]}
    pl = {}
    order = ["home", "shop", "acq", "net", "iss"]
    nums = {"home": 1, "shop": 2, "acq": 3, "net": 4, "iss": 5}
    for i, k in enumerate(order):
        if st == 0:
            pl[k] = (0, False, nums[k])
        elif st == 1:
            if k in ("home", "shop", "acq"):
                pl[k] = (back(e(t, 0.25 + 0.55 * order.index(k) * 0.9 / 2, 0.8 + 0.55 * order.index(k) * 0.9 / 2)), True, nums[k])
            else:
                pl[k] = (0, False, nums[k])
        elif st == 2:
            if k in ("home", "shop", "acq"):
                pl[k] = (1, True, nums[k])
            else:
                pl[k] = (back(e(t, 0.25 + (order.index(k) - 3) * 1.1, 0.85 + (order.index(k) - 3) * 1.1)), True, nums[k])
        elif st == 3:
            pl[k] = (1, True, nums[k]) if k in ("net", "iss") else (0.0, False, nums[k])
        else:
            pl[k] = (0, False, nums[k])
    pulse = 0.0
    draw_world(c, gt, [], plates=pl)
    if st == 0:
        for k in order:
            x, y, w, dd, h = BLD[k]
            X, Y = P(x + w / 2, y + dd / 2, h + 0.9)
            kk = back(e(gt, 0.1 + order.index(k) * 0.35, 0.6 + order.index(k) * 0.35))
            T(c, "?", X, Y, 90 * kk, GOLD, HEAD, "c", min(1, kk), stroke=NAVY, sw=9)
        banner(c, "5 PLAYERS. 1 SWIPE.", None, e(gt, 0.2, 0.7), 40)
    if st == 3:
        k = e(t, 0.2, 1.0)
        x, y = on_path("net_iss", 0.5)
        pill(c, *P(BLD["iss"][0] + 1.8, BLD["iss"][1] + 1.5, 4.2), "LENDS YOU THE MONEY", 34, WHITE, C_ISS, k, BODY)
        pill(c, *P(BLD["net"][0] + 1.0, BLD["net"][1] + 1.0, 8.0), "RUNS THE ROADS", 34, WHITE, C_NET, e(t, 1.4, 2.2), BODY)
        pk = (gt * 0.4) % 1.0
        for off in (0.0, 0.5):
            dot_on(c, "acq_net", (pk + off) % 1.0, (0.55, 0.95, 1.0), 12, e(t, 1.4, 2.0))
            dot_on(c, "net_iss", (pk + off) % 1.0, (0.55, 0.95, 1.0), 12, e(t, 1.4, 2.0))
    if st == 4:
        banner(c, "LET'S BUY SOMETHING", None, e(t, 0.1, 0.5), 40)
        coin_at(c, 4.0, 9.0, 0.4 + 0.4 * abs(math.sin(gt * 3)), 30, 1.0, "$100")


def s_swipe(c, t, st, gt, d):
    ex = []
    shopper = lambda c: person_b(c, 3.7, 9.15, (0.25, 0.55, 0.85), 1.1 if st != 1 else 0.8, 1.0, card=True, wave=(math.sin(gt * 6) * 0.5 if st == 0 else 0))
    ex.append((3.7 + 9.15, shopper))
    if st == 0:
        draw_world(c, gt, ex, cars=False)
        XT, YT = P(4.6, 9.2, 1.3)
        k = e(t, 0.4, 0.8)
        pill(c, XT, YT - 40, "TAP!", 52, WHITE, GREEN, back(k), HEAD)
        pill(c, XT + 260, YT + 30, "$100 JACKET", 34, INK, (1.0, 0.97, 0.88), e(t, 0.0, 0.3), HEAD, line_col=(0.8, 0.7, 0.4))
        banner(c, "ONE TAP.", None, e(t, 0, 0.3), 40)
    elif st == 1:
        draw_world(c, gt, ex, cars=False)
        run = e(t, 0.6, 2.6)
        back_ = e(t, 2.6, 3.9)
        segs = [("shop_acq", "STORE'S BANK"), ("acq_net", "NETWORK"), ("net_iss", "YOUR BANK")]
        total = run * 3
        for i, (nm, lb) in enumerate(segs):
            kk = clamp(total - i)
            if 0 < kk < 1 or (kk >= 1 and back_ < 1):
                dot_on(c, nm, kk if back_ <= 0 else 1.0, (0.30, 0.55, 1.0), 16, 1.0, 0.7)
        if back_ > 0:
            tot = back_ * 3
            for i, nm in enumerate(["net_iss_r", "acq_net_r", "shop_acq_r"]):
                kk = clamp(tot - i)
                if 0 < kk < 1:
                    dot_on(c, nm, kk, (0.2, 0.8, 0.4), 16, 1.0, 0.7)
        sec = clamp(gt - 0.6, 0, 2.0) / 2.0 * 2.0 if back_ < 1 else 2.0
        banner(c, "ASKING: CAN THIS CARD PAY $100?", None, e(t, 0.0, 0.4), 40)
        pill(c, 960, 330, "%.1f SECONDS" % (min(t, 3.3) / 3.3 * 2.0), 52, INK, WHITE, e(t, 0.3, 0.7), MONO, line_col=NAVY)
        if back_ > 0.8:
            pill(c, 960, 430, "YES", 60, WHITE, GREEN, back(e(t, 3.5, 4.0)), HEAD)
    elif st == 2:
        draw_world(c, gt, [], plates={"iss": (1, False, 5)})
        banner(c, "NOTHING IS PAID YET", None, e(t, 0.0, 0.4), 40, RED)
        bstamp(c, "JUST A PROMISE", 960, 820, RED, e(t, 0.6, 1.2), 90, -0.08, (1, 1, 1))
        coin_at(c, BLD["iss"][0] + 1.8, BLD["iss"][1] + 1.6, 4.5, 34, 0.5 * (1 - e(t, 0.4, 1.0)) + 0.35, "$?")
    else:
        draw_world(c, gt, ex, cars=False)
        banner(c, "MONEY MOVES LATER", None, e(t, 0.0, 0.4), 40)
        k = e(t, 0.5, 1.2)
        card(c, 1280, 290, 520, 300, k)
        T(c, "SETTLEMENT", 1540, 350, 36, SOFT, BODY, "c", k)
        T(c, "1 TO 2 DAYS", 1540, 450, 66, INK, HEAD, "c", k)
        T(c, "in a batch with the", 1540, 505, 30, SOFT, BODY, "c", k)
        T(c, "store's other sales", 1540, 545, 30, SOFT, BODY, "c", k)
        for i in range(6):
            kk = back(e(t, 1.0 + i * 0.15, 1.5 + i * 0.15))
            coin_at(c, 3.0 + (i % 3) * 0.7, 8.2 + (i // 3) * 0.6, 0.25, 22, kk)


LEDV = {}


def s_split(c, t, st, gt, d):
    vals = [None, None, None, None]
    hl = -1
    if st >= 1:
        vals[0] = "$1.90"
    if st >= 3:
        vals[1] = "$0.14"
    if st >= 4:
        vals[2] = "$0.48"
    if st >= 5:
        vals[3] = "$97.48"
    ex = []
    plates = {}
    ISS_C = (BLD["iss"][0] + 1.8, BLD["iss"][1] + 1.6)
    if st == 0:
        draw_world(c, gt, ex, cars=False)
        pk = back(e(t, 0.1, 0.6))
        X, Y = P(15.2, 7.2, 0.5)
        packet(c, 15.2, 7.2, 0.8, "$100.00", GOLD, pk, 1.5)
        cut = e(t, 1.4, 1.9)
        if cut > 0:
            c.set_source_rgba(*RED, 1)
            c.set_line_width(8)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(X - 120 + 240 * cut, Y - 150 + 120 * 0)
            c.line_to(X - 150 + 240 * cut, Y - 60)
            c.stroke()
        banner(c, "THE $100 GETS SLICED", None, e(t, 0.0, 0.4), 40)
    elif st == 1:
        draw_world(c, gt, ex, cars=False, plates={"iss": (1, False, 5)})
        k = e(t, 0.6, 1.8)
        packet(c, 15.2, 7.2, 0.8 + 0.2 * k, "$98.10", GOLD, 1.0, 1.4)
        sx, sy = lerp(15.2, ISS_C[0], k), lerp(7.2, ISS_C[1], k)
        packet(c, sx, sy, 0.8 + 3.0 * k, "$1.90", C_ISS, 1.0, 1.1, WHITE)
        pill(c, *P(ISS_C[0] - 3.2, ISS_C[1] + 2.4, 3.0), "INTERCHANGE", 34, WHITE, C_ISS, e(t, 1.8, 2.4), BODY)
        pill(c, *P(ISS_C[0] - 3.2, ISS_C[1] + 2.4, 2.2), "about 1.9% of the sale", 28, INK, WHITE, e(t, 2.2, 2.9), BODY)
        banner(c, "SLICE 1: YOUR BANK", None, e(t, 0.0, 0.4), 40, C_ISS)
    elif st == 2:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.74 * e(t, 0, 0.4))
        k = e(t, 0.2, 0.7)
        card(c, 300, 170, 1320, 640, k)
        T(c, "TYPICAL INTERCHANGE BY CARD TYPE", 960, 255, 44, NAVY, HEAD, "c", k)
        rows = [("BASIC CARD", 1.51, 1.80, BLUE), ("REWARDS CARD", 1.65, 2.40, C_ISS), ("PREMIUM CARD", 2.10, 2.65, VIOLET)]
        for i, (nm, lo, hi, col) in enumerate(rows):
            y = 330 + i * 130
            T(c, nm, 360, y + 62, 38, INK, BODY, "l", k)
            bx = 800
            bw = 700
            box(c, bx, y + 18, bw, 62, (0.93, 0.95, 0.98), k, 31)
            kk = e(t, 0.8 + i * 0.4, 1.6 + i * 0.4)
            x0 = bx + (lo - 1.4) / 1.4 * bw
            x1 = bx + (hi - 1.4) / 1.4 * bw
            box(c, x0, y + 18, (x1 - x0) * kk, 62, col, k, 31)
            T(c, "%.2f%% to %.2f%%" % (lo, hi), bx + bw + 20, y + 62, 34, INK, MONO, "l", kk * k)
        T(c, "The fancier the card, the more the store pays.", 960, 745, 36, SOFT, BODY, "c", e(t, 2.2, 2.8))
        T(c, "Published ranges, rounded. Source: card network rate tables via SuperMoney, May 2026.", 960, 790, 24, SOFT, BODY, "c", e(t, 2.2, 2.8) * 0.9)
    elif st == 3:
        draw_world(c, gt, ex, cars=False, plates={"net": (1, False, 4)})
        k = e(t, 0.0, 2.0)
        x, y = on_path("net_iss_r", k)
        packet(c, x, y, 0.7, "$98.10" if k < 1 else "$97.96", GOLD, 1.0, 1.3)
        if k >= 1:
            k2 = e(t, 2.3, 3.3)
            packet(c, D_NET[0], D_NET[1] - 1.0 * k2, 0.7 + 4.0 * k2, "$0.14", C_NET, 1.0, 1.0, WHITE)
        banner(c, "SLICE 2: THE NETWORK", None, e(t, 0.0, 0.4), 40, C_NET)
    elif st == 4:
        draw_world(c, gt, ex, cars=False, plates={"acq": (1, False, 3)})
        k = e(t, 0.0, 1.8)
        x, y = on_path("acq_net_r", k)
        packet(c, x, y, 0.7, "$97.96", GOLD, 1.0, 1.3)
        if k >= 1:
            k2 = e(t, 2.2, 3.2)
            packet(c, D_ACQ[0], D_ACQ[1] - 1.0 * k2, 0.7 + 3.0 * k2, "$0.48", C_ACQ, 1.0, 1.0, WHITE)
        banner(c, "SLICE 3: STORE'S BANK", None, e(t, 0.0, 0.4), 40, C_ACQ)
    elif st == 5:
        draw_world(c, gt, [], cars=False, plates={"shop": (1, False, 2)})
        k = e(t, 0.0, 1.8)
        x, y = on_path("shop_acq_r", k)
        packet(c, x, y, 0.7, "$97.48", GOLD, 1.0, 1.5)
        banner(c, "THE STORE GETS ABOUT $97.50", None, e(t, 0.8, 1.2), 40, C_SHOP)
        T(c, "FOR A $100 SALE", 960, 175, 46, NAVY, HEAD, "c", e(t, 1.4, 2.0), stroke=WHITE, sw=10)
    else:
        draw_world(c, gt, [], cars=False, plates={"shop": (1, False, 2)})
        packet(c, 4.0, 8.7, 0.7, "$97.48", GOLD, 1.0, 1.5)
        banner(c, "$2.52 SLICED OFF", None, 1.0, 40, NAVY)
        bstamp(c, "TYPICAL EXAMPLE, NOT A RECEIPT", 960, 640, RED, e(t, 0.4, 1.0), 52, -0.04, (1, 1, 1))
    if st != 2:
        ledger(c, vals, e(gt, 0, 0.6))


def s_rew(c, t, st, gt, d):
    ISS_C = (BLD["iss"][0] + 1.8, BLD["iss"][1] + 1.6)
    if st == 0:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, False, 5)})
        for i in range(4):
            coin_at(c, 15.0 + (i % 2) * 0.5, 7.0 + (i // 2) * 0.5, 0.2 + 0.1 * i, 26, e(t, 0.1 * i, 0.5 + 0.1 * i))
        packet(c, 15.2, 7.4, 1.4, "$1.90", C_ISS, back(e(t, 0.3, 0.8)), 1.5, WHITE)
        banner(c, "YOUR BANK'S $1.90", None, e(t, 0.0, 0.4), 40, C_ISS)
    elif st == 1:
        draw_world(c, gt, [], cars=False)
        k = e(t, 0.6, 3.6)
        for j in range(4):
            kk = clamp(k * 1.3 - j * 0.1)
            if 0 < kk < 1:
                x, y = on_path("iss_home", kk)
                coin_at(c, x, y, 0.5, 24)
        packet(c, 15.15, 7.2, 0.7, "$1.90", C_ISS, 1.0, 1.1, WHITE)
        pill(c, *P(10.5, 8.2, 2.0), "1.5% BACK = $1.50", 46, WHITE, GREEN, back(e(t, 0.4, 1.0)), HEAD)
        pill(c, *P(4.2, 10.6, 3.2), "POINTS OR CASH", 34, WHITE, GREEN, e(t, 3.2, 3.8), BODY)
        banner(c, "SOME OF IT COMES BACK TO YOU", None, e(t, 0.0, 0.4), 40, GREEN)
    elif st == 2:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, False, 5)})
        veil(c, 0.55 * e(t, 0, 0.4))
        card(c, 360, 200, 1200, 620, e(t, 0.1, 0.6))
        k = e(t, 0.1, 0.6)
        T(c, "$1.90", 960, 300, 80, C_ISS, HEAD, "c", k)
        parts = [("$1.50", "REWARDS TO YOU", GREEN, 0.789), ("$0.40", "FRAUD, RUNNING THE CARD, PROFIT", ORANGE, 0.211)]
        x = 440
        for i, (v, lb, col, fr) in enumerate(parts):
            kk = e(t, 0.8 + i * 0.8, 1.6 + i * 0.8)
            w = 1040 * fr * kk
            box(c, x, 360, max(1, w), 110, col, k, 18)
            if kk > 0.9:
                T(c, v, x + w / 2, 435, 52, WHITE, HEAD, "c", min(1, (kk - 0.9) * 10))
            x += w
        T(c, "REWARDS TO YOU", 440 + 1040 * 0.789 / 2, 520, 32, GREEN, BODY, "c", e(t, 1.5, 2.0))
        T(c, "OTHER COSTS + PROFIT", 440 + 1040 * 0.789 + 1040 * 0.211 / 2 - 40, 580, 30, ORANGE, BODY, "c", e(t, 2.4, 3.0))
        for j, lb in enumerate(["FRAUD LOSSES", "RUNNING THE CARD", "PROFIT"]):
            kk = back(e(t, 3.0 + j * 0.35, 3.5 + j * 0.35))
            pill(c, 560 + j * 400, 700, lb, 30, WHITE, ORANGE, kk, BODY)
    elif st == 3:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, False, 5)})
        veil(c, 0.7 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 340, 200, 1240, 600, k)
        T(c, "WHAT PART OF THE FEE PAYS FOR", 960, 290, 40, SOFT, HEAD, "c", k)
        kk = back(e(t, 0.5, 1.2))
        c.save()
        c.translate(620, 530)
        c.scale(kk, kk)
        c.set_source_rgba(*C_ISS, 1)
        c.move_to(0, -150); c.curve_to(110, -130, 150, -110, 150, -60); c.curve_to(150, 60, 80, 120, 0, 160)
        c.curve_to(-80, 120, -150, 60, -150, -60); c.curve_to(-150, -110, -110, -130, 0, -150)
        c.fill()
        c.set_source_rgba(1, 1, 1, 1)
        c.set_line_width(24); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.move_to(-56, 6); c.line_to(-16, 50); c.line_to(64, -50)
        c.stroke()
        c.restore()
        T(c, "FRAUD PROTECTION", 1180, 430, 50, NAVY, HEAD, "c", e(t, 0.9, 1.5))
        T(c, "Your liability for unauthorized", 1180, 500, 34, INK, BODY, "c", e(t, 1.3, 1.9))
        T(c, "card charges is capped at", 1180, 545, 34, INK, BODY, "c", e(t, 1.3, 1.9))
        T(c, "$50", 1180, 640, 100, C_ISS, HEAD, "c", back(e(t, 1.9, 2.5)))
        T(c, "by federal law. Many issuers advertise $0.", 1180, 700, 30, SOFT, BODY, "c", e(t, 2.6, 3.2))
    elif st == 4:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, False, 5)})
        veil(c, 0.7 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 220, 190, 700, 600, k)
        card(c, 1000, 190, 700, 600, e(t, 0.4, 0.9))
        for i, (ttl, sub, fee, rew, col, x0) in enumerate([("BASIC CARD", "no annual fee", "store pays ~1.5% to 1.8%", "rewards: smaller", BLUE, 220), ("PREMIUM CARD", "annual fee", "store pays ~2.1% to 2.65%", "rewards: richer", VIOLET, 1000)]):
            kk = e(t, 0.3 + i * 0.4, 0.9 + i * 0.4)
            box(c, x0 + 30, 220, 640, 90, col, kk, 18)
            T(c, ttl, x0 + 350, 282, 46, WHITE, HEAD, "c", kk)
            T(c, fee, x0 + 350, 400, 34, INK, BODY, "c", e(t, 1.2 + i * 0.5, 1.8 + i * 0.5))
            T(c, rew, x0 + 350, 470, 34, GREEN, BODY, "c", e(t, 1.8 + i * 0.5, 2.4 + i * 0.5))
            T(c, "annual fee: $0 to $95+" if i == 0 else "annual fee: $395 to $895", x0 + 350, 540, 34, INK, BODY, "c", e(t, 2.4 + i * 0.4, 3.0 + i * 0.4))
        T(c, "Typical ranges. Premium travel cards: $395 to $895 a year in 2026.", 960, 850, 26, SOFT, BODY, "c", e(t, 3.4, 4.0))
    else:
        draw_world(c, gt, [], cars=False)
        coin_at(c, 4.0, 11.7, 1.8 + 0.3 * math.sin(gt * 3), 44, 1.0, "$")
        banner(c, "REAL MONEY. NOT THIN AIR.", None, e(t, 0.0, 0.4), 40, NAVY)
        for i in range(5):
            kk = e(t, 0.2 + i * 0.25, 1.0 + i * 0.25)
            x, y = on_path("iss_home", kk)
            coin_at(c, x, y, 0.5, 22, kk * (1 - e(t, 2.8, 3.2)))


def s_pays(c, t, st, gt, d):
    if st == 0:
        ex = [(4.2 + 9.0, lambda c: person_b(c, 3.6, 9.0, (0.85, 0.65, 0.20), 1.25, 1.0))]
        draw_world(c, gt, ex, cars=False, plates={"shop": (1, False, 2)})
        k = e(t, 0.4, 1.2)
        packet(c, 3.0, 8.1, 1.0, "-$2.52", RED, back(k), 1.6, WHITE)
        banner(c, "THE STORE COVERS THE SLICES", None, e(t, 0.0, 0.4), 40, C_SHOP)
    elif st == 1:
        ex = [(3.7 + 9.15, lambda c: person_b(c, 3.4, 9.2, (0.25, 0.55, 0.85), 1.25, 1.0, card=True)), (5.7 + 9.0, lambda c: person_b(c, 5.6, 9.0, (0.70, 0.42, 0.78), 1.25, 1.0, cash=True))]
        draw_world(c, gt, ex, cars=False, plates={"shop": (1, False, 2)})
        for i, x in enumerate([3.4, 5.6]):
            XT, YT = P(x, 9.0 + 0.2 * (i == 0), 2.4)
            k = back(e(t, 0.3 + 0.3 * i, 0.9 + 0.3 * i))
            pill(c, XT, YT, "$100", 54, INK, (1.0, 0.97, 0.88), k, HEAD, line_col=(0.8, 0.7, 0.4))
        banner(c, "ONE PRICE TAG FOR EVERYONE", None, e(t, 0.0, 0.4), 40, NAVY)
    elif st == 2:
        draw_world(c, gt, [], cars=False, plates={"shop": (1, False, 2)})
        veil(c, 0.55 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 360, 230, 1200, 560, k)
        XB = 960
        T(c, "THE JACKET", XB, 320, 38, SOFT, BODY, "c", k)
        T(c, "$100", 760, 470, 110, INK, HEAD, "c", k)
        kk = e(t, 0.9, 1.5)
        T(c, "+", 960, 465, 80, RED, HEAD, "c", kk)
        box(c, 1020, 390, 400, 120, RED_L, kk, 24, RED, 4)
        T(c, "cost of accepting", 1220, 442, 30, RED, BODY, "c", kk)
        T(c, "cards, built in", 1220, 484, 30, RED, BODY, "c", kk)
        k2 = e(t, 1.8, 2.4)
        box(c, 440, 580, 1040, 130, BLUE_L, k2, 24)
        T(c, "NBER working paper · July 2026", 960, 640, 38, NAVY, HEAD, "c", k2)
        T(c, "Egan, Matvos, Seru, Wang and Yao", 960, 688, 28, SOFT, BODY, "c", k2)
    elif st == 3:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.7 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 220, 200, 1480, 620, k)
        box(c, 280, 330, 440, 300, (0.93, 0.94, 0.97), k, 24)
        T(c, "CASH + DEBIT", 500, 400, 40, SOFT, HEAD, "c", k)
        T(c, "shoppers", 500, 450, 36, SOFT, BODY, "c", k)
        box(c, 1200, 330, 440, 300, GREEN_L, k, 24)
        T(c, "CREDIT CARD", 1420, 400, 40, GREEN, HEAD, "c", k)
        T(c, "users", 1420, 450, 36, GREEN, BODY, "c", k)
        for i in range(6):
            kk = (e(t, 0.8, 3.4) * 1.0 + i / 6.0) % 1.0
            if e(t, 0.6, 1.0) > 0:
                xx = lerp(740, 1180, kk)
                coin_at_screen = (xx, 480 + math.sin(kk * math.pi) * -40)
                circle(c, coin_at_screen[0], coin_at_screen[1], 20, GOLD, e(t, 0.6, 1.0), GOLD_D, 3)
        arrow(c, 740, 560, 1180, 560, NAVY, 10, e(t, 0.6, 1.0), 1.0, 34)
        T(c, "about $30 billion a year", 960, 705, 62, NAVY, HEAD, "c", e(t, 1.2, 1.9))
        T(c, "estimated transfer, if stores pass fees into every price", 960, 760, 30, SOFT, BODY, "c", e(t, 1.9, 2.6))
    elif st == 4:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.7 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 260, 220, 1400, 580, k)
        T(c, "TWO CAVEATS FROM THE PAPER", 960, 310, 44, NAVY, HEAD, "c", k)
        box(c, 320, 360, 1280, 140, RED_L, e(t, 0.5, 1.1), 24)
        T(c, "1  It assumes stores pass the fees into every price", 380, 450, 40, RED, BODY, "l", e(t, 0.5, 1.1))
        box(c, 320, 540, 1280, 140, BLUE_L, e(t, 1.6, 2.2), 24)
        T(c, "2  It shrinks by about a quarter: cash, debit and", 380, 610, 40, NAVY, BODY, "l", e(t, 1.6, 2.2))
        T(c, "    credit shoppers often use different stores", 380, 656, 40, NAVY, BODY, "l", e(t, 1.6, 2.2))
        T(c, "-25%", 1470, 640, 60, NAVY, HEAD, "c", e(t, 2.2, 2.8))
    elif st == 5:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.72 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 340, 180, 1240, 660, k)
        T(c, "PREMIUM CARDS' SHARE OF CREDIT CARD SPENDING", 960, 270, 36, NAVY, HEAD, "c", k)
        for i, (yr, v, col) in enumerate([("2006", 15, BLUE), ("2022", 60, VIOLET)]):
            kk = e(t, 0.8 + i * 1.0, 1.9 + i * 1.0)
            x = 560 + i * 460
            hh = 360 * v / 60.0 * kk
            box(c, x, 760 - hh, 280, hh, col, k, 18)
            T(c, yr, x + 140, 805, 38, SOFT, BODY, "c", k)
            if kk > 0.5:
                T(c, "%d%%" % round(v * kk / max(kk, 1e-6) if kk >= 1 else v * kk), x + 140, 760 - hh - 16, 64, col, HEAD, "c", k)
    else:
        ex = [(3.7 + 9.15, lambda c: person_b(c, 3.4, 9.2, (0.25, 0.55, 0.85), 1.25, 1.0, card=True)), (5.7 + 9.0, lambda c: person_b(c, 5.6, 9.0, (0.70, 0.42, 0.78), 1.25, 1.0, cash=True))]
        draw_world(c, gt, ex, cars=False, plates={"shop": (1, False, 2)})
        k1 = back(e(t, 0.3, 0.9))
        k2 = back(e(t, 1.0, 1.6))
        pill(c, *P(2.6, 7.2, 1.6), "CARD SURCHARGE +3%", 34, WHITE, RED, k1, HEAD)
        pill(c, *P(5.4, 7.6, 1.2), "CASH DISCOUNT", 34, WHITE, GREEN, k2, HEAD)
        banner(c, "EITHER WAY, SOMEONE PAYS THE FEE", None, e(t, 0.0, 0.4), 40, NAVY)


def s_other(c, t, st, gt, d):
    if st <= 1:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, True, 5)})
        k = e(t, 0.1, 0.7)
        veil(c, 0.35 * k)
        streams = [("SWIPE FEES", "paid by stores", C_SHOP, 270), ("INTEREST", "paid by borrowers", RED, 760), ("ANNUAL FEES", "paid by cardholders", VIOLET, 1250)]
        for i, (a, b, col, x) in enumerate(streams):
            kk = back(e(gt, 0.3 + i * 0.35, 0.9 + i * 0.35)) if st == 0 else 1.0
            hl = (st == 1 and i == 1)
            card(c, x, 560, 400, 230, kk, WHITE if not (st == 1 and i != 1) else (0.94, 0.95, 0.98))
            if hl:
                box(c, x - 8, 552, 416, 246, GOLD, kk, 30)
                box(c, x, 560, 400, 230, WHITE, kk, 26)
            box(c, x + 24, 580, 352, 70, col, kk, 16)
            T(c, a, x + 200, 632, 38, WHITE, HEAD, "c", kk)
            T(c, b, x + 200, 700, 32, SOFT, BODY, "c", kk)
            if i == 1 and st == 1:
                T(c, "avg ~22% APR", x + 200, 756, 36, RED, HEAD, "c", e(t, 0.6, 1.2))
        banner(c, "3 WAYS A CARD MAKES MONEY", None, e(gt, 0, 0.4), 40, NAVY)
        if st == 1:
            T(c, "Fed: 22.36% average rate on accounts charged interest, Aug 2026", 960, 850, 28, SOFT, BODY, "c", e(t, 1.2, 1.8))
    elif st == 2:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.74 * e(t, 0, 0.4))
        k = e(t, 0.1, 0.6)
        card(c, 260, 190, 1400, 640, k)
        T(c, "PAY THE FULL STATEMENT BALANCE BY THE DUE DATE", 960, 280, 40, NAVY, HEAD, "c", k)
        for i, (x, a1, a2, col) in enumerate([(420, "STATEMENT", "$1,000", BLUE), (960, "DUE DATE", "PAY $1,000", GREEN), (1500, "INTEREST", "$0", GREEN)]):
            kk = back(e(t, 0.5 + i * 0.7, 1.1 + i * 0.7))
            c.save()
            c.translate(x, 480)
            c.scale(kk, kk)
            box(c, -200, -110, 400, 220, col, 1, 26)
            T(c, a1, 0, -30, 34, WHITE, BODY, "c")
            T(c, a2, 0, 50, 56, WHITE, HEAD, "c")
            c.restore()
            if i < 2:
                arrow(c, x + 220, 480, x + 330, 480, NAVY, 8, e(t, 0.9 + i * 0.7, 1.4 + i * 0.7), 1.0, 30)
        T(c, "on purchases, generally", 1500, 640, 30, GREEN, BODY, "c", e(t, 2.2, 2.8))
        box(c, 540, 690, 840, 90, BLUE_L, e(t, 3.0, 3.6), 24)
        T(c, "Bills must be sent at least 21 days before they are due", 960, 748, 34, NAVY, BODY, "c", e(t, 3.0, 3.6))
    elif st in (3, 4):
        draw_world(c, gt, [], cars=False)
        veil(c, 0.78)
        card(c, 300, 150, 1320, 720)
        T(c, "FOR SCALE (BILLIONS OF DOLLARS)", 960, 235, 40, NAVY, HEAD, "c")
        base_y = 780
        k1 = e(t, 0.3, 1.5) if st == 3 else 1.0
        h1 = 440 * k1
        box(c, 540, base_y - h1, 300, h1, RED, 1, 18)
        T(c, "$160B", 690, base_y - h1 - 18, 64, RED, HEAD, "c", min(1, k1 * 3))
        T(c, "card interest charges", 690, base_y + 44, 30, INK, BODY, "c")
        T(c, "2024 · CFPB", 690, base_y + 80, 26, SOFT, BODY, "c")
        if st == 4:
            k2 = e(t, 0.3, 1.5)
            h2 = 440 * 66 / 160 * k2
            box(c, 1080, base_y - h2, 300, h2, C_SHOP, 1, 18)
            T(c, "$66B", 1230, base_y - h2 - 18, 64, C_SHOP, HEAD, "c", min(1, k2 * 3))
            T(c, "swipe fees (credit + debit)", 1230, base_y + 44, 30, INK, BODY, "c")
            T(c, "2025 · St. Louis Fed", 1230, base_y + 80, 26, SOFT, BODY, "c")
            T(c, "different years, so treat it as scale", 960, 850, 28, SOFT, BODY, "c", e(t, 1.8, 2.4))
    elif st == 5:
        draw_world(c, gt, [], cars=False, plates={"iss": (1, False, 5)})
        veil(c, 0.55 * e(t, 0, 0.4))
        for i, (v, lb, col) in enumerate([("$0", "many cards", GREEN), ("$395", "mid premium", BLUE), ("$795", "top premium", VIOLET), ("$895", "top premium", VIOLET)]):
            kk = back(e(t, 0.3 + i * 0.45, 0.9 + i * 0.45))
            x = 330 + i * 360
            c.save()
            c.translate(x + 150, 520 + (1 - kk) * 80)
            c.rotate(-0.06 + i * 0.04)
            card(c, -150, -170, 300, 340, kk)
            box(c, -120, -140, 240, 56, col, kk, 14)
            T(c, "ANNUAL FEE", 0, -100, 28, WHITE, HEAD, "c", kk)
            T(c, v, 0, 30, 84, col, HEAD, "c", kk)
            T(c, lb, 0, 100, 30, SOFT, BODY, "c", kk)
            c.restore()
        banner(c, "3. ANNUAL FEES", None, e(t, 0, 0.4), 40, VIOLET)
        T(c, "Top premium cards, 2026 (Kiplinger, CNBC)", 960, 880, 28, SOFT, BODY, "c", e(t, 2.2, 2.8))
    elif st == 6:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.78)
        card(c, 340, 230, 1240, 560)
        T(c, "EXAMPLE: $1,000 OF SPENDING", 960, 320, 40, SOFT, HEAD, "c")
        T(c, "$1,000  ×  2%  =", 760, 520, 80, INK, MONO, "c", e(t, 0.3, 0.9))
        kk = back(e(t, 1.4, 2.0))
        c.save()
        c.translate(1330, 500)
        c.scale(kk, kk)
        box(c, -170, -90, 340, 150, GREEN_L, 1, 26, GREEN, 5)
        T(c, "$20", 0, 28, 100, GREEN, HEAD, "c")
        c.restore()
        T(c, "in rewards", 1330, 600, 32, GREEN, BODY, "c", e(t, 1.8, 2.4))
    elif st == 7:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.78)
        card(c, 340, 230, 1240, 560)
        T(c, "SAME $1,000, CARRIED FOR A WHOLE YEAR", 960, 320, 40, SOFT, HEAD, "c")
        T(c, "$1,000  ×  22%  ≈", 760, 520, 80, INK, MONO, "c")
        kk = back(e(t, 0.8, 1.4))
        c.save()
        c.translate(1330, 500)
        c.scale(kk, kk)
        box(c, -190, -90, 380, 150, RED_L, 1, 26, RED, 5)
        T(c, "$220", 0, 28, 100, RED, HEAD, "c")
        c.restore()
        T(c, "in interest", 1330, 600, 32, RED, BODY, "c", e(t, 1.2, 1.8))
        T(c, "Rough example: assumes the full balance sits there all year.", 960, 740, 28, SOFT, BODY, "c", e(t, 1.6, 2.2))
    else:
        draw_world(c, gt, [], cars=False)
        veil(c, 0.78)
        card(c, 300, 200, 1320, 620)
        T(c, "BREAK-EVEN ON A $795 ANNUAL FEE, AT 3% BACK", 960, 290, 38, SOFT, HEAD, "c")
        T(c, "$795  ÷  3%  =", 700, 500, 80, INK, MONO, "c", e(t, 0.3, 0.9))
        kk = back(e(t, 1.2, 1.8))
        c.save()
        c.translate(1380, 480)
        c.scale(kk, kk)
        box(c, -260, -90, 520, 150, (0.93, 0.91, 0.99), 1, 26, VIOLET, 5)
        T(c, "$26,500", 0, 28, 96, VIOLET, HEAD, "c")
        c.restore()
        T(c, "of spending a year", 1380, 580, 32, VIOLET, BODY, "c", e(t, 1.6, 2.2))
        T(c, "Before counting credits, perks and the sign-up bonus.", 960, 720, 30, SOFT, BODY, "c", e(t, 2.0, 2.6))


def s_pts(c, t, st, gt, d):
    ex = []
    draw_world(c, gt, ex, cars=False)
    veil(c, 0.62)
    if st == 0:
        k = back(e(t, 0.2, 0.8))
        c.save()
        c.translate(960, 480)
        c.scale(k, k)
        circle(c, 0, 0, 170, (0.55, 0.40, 0.95), 1, WHITE, 10)
        T(c, "1", 0, 40, 160, WHITE, HEAD, "c")
        T(c, "POINT", 0, 105, 38, (0.9, 0.85, 1.0), HEAD, "c")
        c.restore()
        T(c, "Not a dollar.", 960, 760, 64, NAVY, HEAD, "c", e(t, 1.0, 1.6))
    elif st == 1:
        card(c, 300, 230, 1320, 560)
        T(c, "WHAT ONE POINT CAN BE WORTH", 960, 320, 40, SOFT, HEAD, "c")
        for i, (a, b, col, x) in enumerate([("AS CASH", "about 1¢", GREEN, 520), ("ON TRAVEL", "up to about 2¢", VIOLET, 1180)]):
            kk = back(e(t, 0.4 + i * 0.8, 1.0 + i * 0.8))
            c.save()
            c.translate(x + 110, 540)
            c.scale(kk, kk)
            circle(c, 0, 0, 120, col, 1, WHITE, 8)
            T(c, a, 0, -10, 34, WHITE, HEAD, "c")
            T(c, b, 0, 36, 32, WHITE, BODY, "c")
            c.restore()
        T(c, "depends on how you redeem it", 960, 730, 34, SOFT, BODY, "c", e(t, 2.2, 2.8))
    else:
        card(c, 360, 260, 1200, 480)
        T(c, "THE BANK SETS THE RULES", 960, 410, 64, NAVY, HEAD, "c", e(t, 0.2, 0.8))
        bstamp(c, "AND CAN CHANGE THEM", 960, 580, RED, e(t, 0.9, 1.5), 66, -0.05, (1, 1, 1))


def s_recap(c, t, st, gt, d):
    pl = whole_ids()
    draw_world(c, gt, [], plates={k: (1, False, v[2]) for k, v in pl.items()} if st == 0 else None, cars=True)
    ph = (gt * 0.22) % 1.0
    if st == 0:
        banner(c, "THE LOOP", None, e(t, 0, 0.4), 40, NAVY)
        k = e(t, 0.5, 2.5)
        mover(c, "home_shop", clamp(k * 1.0), "$100", GOLD, 0.6, INK, 0.9)
        dot_on(c, "shop_acq", (gt * 0.3) % 1.0, (0.30, 0.55, 1.0), 12)
    elif st == 1:
        banner(c, "WHO KEEPS WHAT", None, e(t, 0, 0.4), 40, NAVY)
        packet(c, 15.2, 7.4, 1.5, "BANK: REWARDS + RUNNING THE CARD", C_ISS, back(e(t, 0.3, 0.9)), 0.8, WHITE)
        packet(c, 10.8, 3.6, 6.4, "NETWORK: SMALLER CUT", C_NET, back(e(t, 1.4, 2.0)), 0.8, WHITE)
        packet(c, 4.0, 3.6, 3.4, "STORE'S BANK: SMALLER CUT", C_ACQ, back(e(t, 2.2, 2.8)), 0.8, WHITE)
    elif st == 2:
        banner(c, "WHERE THE COST LANDS", None, e(t, 0, 0.4), 40, NAVY)
        packet(c, 4.0, 8.9, 2.4, "STORE: BUILDS IT INTO PRICES", C_SHOP, back(e(t, 0.3, 0.9)), 0.8, WHITE)
        packet(c, 15.2, 7.4, 1.5, "BORROWERS: INTEREST", RED, back(e(t, 1.6, 2.2)), 0.8, WHITE)
    else:
        veil(c, 0.7 * e(t, 0, 0.5))
        k = back(e(t, 0.3, 0.9))
        c.save()
        c.translate(960, 450)
        c.scale(k, k)
        card(c, -640, -190, 1280, 380)
        T(c, "REAL MONEY.", 0, -30, 100, GREEN, HEAD, "c")
        T(c, "NOT FREE MONEY.", 0, 90, 100, NAVY, HEAD, "c")
        c.restore()


def s_year(c, t, st, gt, d):
    draw_world(c, gt, [], cars=False)
    veil(c, 0.74)
    card(c, 200, 150, 1520, 740)
    T(c, "ONE YEAR ON A 1.5% CARD", 960, 235, 42, NAVY, HEAD, "c")
    kk = e(t, 0.2, 0.9) if st == 0 else 1.0
    box(c, 300, 290, 1320, 90, (0.93, 0.95, 0.98), 1, 24)
    T(c, "SPENT: $20,000", 960, 352, 52, INK, HEAD, "c", kk)
    if st >= 1:
        k1 = e(t, 0.3, 1.0) if st == 1 else 1.0
        box(c, 300, 450, 1320 * 0.0 + 600 * k1, 100, GREEN, 1, 22)
        if k1 > 0.8:
            T(c, "REWARDS: ~$300", 600, 518, 42, WHITE, HEAD, "c", min(1, (k1 - 0.8) * 5))
        k2 = e(t, 1.6, 2.6) if st == 1 else 1.0
        wtot = 1000 * k2
        segs = [(380, C_ISS), (28, C_NET), (96, C_ACQ)]
        x = 300
        for v, col in segs:
            w = wtot * v / 504.0
            box(c, x, 610, max(0.1, w), 100, col, 1, 10 if w > 20 else 2)
            x += w
        if k2 > 0.9:
            T(c, "STORES PAID ABOUT $500 IN FEES", 800, 765, 36, RED, HEAD, "c", min(1, (k2 - 0.9) * 8))
            T(c, "bank $380", 300 + 1000 * 190 / 504.0, 668, 34, WHITE, HEAD, "c")
    if st == 2:
        k3 = e(t, 0.4, 1.2)
        c.set_source_rgba(*C_ISS, 0.95 * k3)
        c.set_line_width(7)
        c.rectangle(300, 600, 1000 * 380 / 504.0, 120)
        c.stroke()
        box(c, 1100, 450, 520, 130, (0.88, 0.96, 0.95), k3, 24, C_ISS, 4)
        T(c, "the bank's $380 covers", 1360, 505, 30, C_ISS, BODY, "c", k3)
        T(c, "rewards + fraud + costs + profit", 1360, 548, 28, C_ISS, BODY, "c", k3)
    T(c, "Labelled example at $2.52 in fees per $100. Real rates vary.", 960, 850, 26, SOFT, BODY, "c", 0.9)


SC = {"hook": s_hook, "play": s_play, "swipe": s_swipe, "split": s_split, "rew": s_rew, "pays": s_pays, "other": s_other, "pts": s_pts, "year": s_year, "recap": s_recap}


def s_end(c, t, p, gt, d):
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgb(0, 0.07, 0.11, 0.26)
    g.add_color_stop_rgb(1, 0.10, 0.20, 0.40)
    c.set_source(g)
    c.paint()
    for i in range(12):
        for j in range(8):
            circle(c, 100 + i * 160, 80 + j * 140, 3, (0.4, 0.5, 0.8), 0.25)
    k = back(e(t, 0.0, 0.7))
    logo(c, 960 - 55 * k, 190, 1.8 * k)
    T(c, "MONEY MAP", 960, 470, 110, WHITE, HEAD, "c", e(t, 0.2, 0.7))
    T(c, "Follow the money.", 960, 545, 44, GOLD, BODY, "c", e(t, 0.4, 0.9))
    kk = e(t, 1.0, 1.7)
    box(c, 360, 640, 1200, 170, (0.14, 0.24, 0.46), kk, 34, GOLD, 5)
    T(c, "NEXT: HOW MORTGAGE RATES WORK", 960, 748, 62, WHITE, HEAD, "c", kk)
    pk = e(t, 1.8, 2.4)
    box(c, 740, 870, 440, 90, GOLD, pk, 45)
    T(c, "FOLLOW FOR MORE", 960, 930, 40, INK, HEAD, "c", pk)


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


def pose_for(L, i):
    ln = L[i]
    return POSE.get((ln["scene"], ln["p"]["step"]), CITY)


def draw(c, L, tl, T_):
    i = 0
    while i + 1 < len(tl) and T_ >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0.0, T_ - t0)
    ln = L[i]
    g0 = i
    while g0 > 0 and L[g0 - 1]["scene"] == ln["scene"]:
        g0 -= 1
    gt = T_ - tl[g0][0]
    sc = ln["scene"]
    if sc == "end":
        s_end(c, t, ln["p"], gt, d)
        return
    cur = pose_for(L, i)
    if i > 0 and L[i - 1]["scene"] != "end":
        prev = pose_for(L, i - 1)
    else:
        prev = cur
    k = e(t, 0.0, 1.3)
    cx, cy, z = cam_lerp(prev, cur, k)
    sy = lerp(prev[3], cur[3], ease(k))
    set_cam(cx, cy, z, sy)
    SC[sc](c, t, ln["p"]["step"], gt, d)
    hud(c)
    if "ch" in ln["p"]:
        import cc_content as C
        sign(c, ln["p"]["ch"], C.CH[ln["p"]["ch"]], t)


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
        times = [a + min(d * 0.85, 4.2) for a, d in tl]
    else:
        times = [float(x) for x in mode.split(",")]
    for k, T_ in enumerate(times):
        draw(c, C.L, tl, T_)
        surf.write_to_png(os.path.join(outdir, "s%02d_%06.2f.png" % (k, T_)))
    return tl, total


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
    elif cmd == "stills":
        tl, total = stills(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "mid")
        print("total", round(total, 1))
