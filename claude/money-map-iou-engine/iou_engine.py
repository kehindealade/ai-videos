import cairo, math, json, os, sys, subprocess
from iou_common import *

GAP = 0.55
TAIL = 3.2


def ap(step, n, t, dur=0.6, delay=0.0):
    if step > n:
        return 1.0
    if step < n:
        return 0.0
    return e(t, delay, delay + dur)


# ------------------------------------------------------------------ helpers
def holder_stat(c, t, idx, pct, amt, step_alpha=1.0, grow_t=0.0):
    col = HCOL[idx]
    k = e(t, 0.0, 0.5)
    txt(c, pct, 480, 640, 330, col, LAB, "c", k)
    txt(c, "OF ALL U.S. DEBT", 480, 730, 62, WHITE, LAB, "c", k)
    txt(c, amt, 480, 330, 150, AMBER, LAB, "c", k)
    g = e(t, 0.1, 1.6)
    stack_bottom(c, 1290, 810, 13, 1.15, HNAME[idx], "", col, 1.0, 15, 4000 + idx, g)
    if g > 0.98:
        txt(c, "$%s" % amt.replace("$", "").replace(" TRILLION", "T"), 1290, 440 - 0, 0, col)


def stat_bar(c, x, y, w, h, parts, t, tdur=1.0, labels=True):
    tot = sum(p[0] for p in parts)
    xx = x
    k = e(t, 0, tdur)
    for val, col, lab, sub in parts:
        ww = w * val / tot * k
        rr(c, xx, y, max(2, ww), h, 10)
        c.set_source_rgb(*col)
        c.fill()
        xx += ww
    return xx


def treasury_icon(c, x, y, s=1.0, col=WHITE, a=1.0, label=True):
    bank_icon(c, x, y, s, col, a)
    if label:
        txt(c, "TREASURY", x, y + 100 * s, 34 * s, col, LAB, "c", a)


def paper_card(c, x, y, w, h, a=1.0, ang=0.0):
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(ang)
    shadow(c, -w / 2, -h / 2, w, h, 10, 0.35 * a, 10)
    rr(c, -w / 2, -h / 2, w, h, 10)
    c.set_source_rgba(*PAPER, a)
    c.fill_preserve()
    c.set_source_rgba(*INKG, a)
    c.set_line_width(4)
    c.stroke()
    c.restore()


def dollar_bill(c, x, y, s=1.0, a=1.0, ang=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    rr(c, -70, -34, 140, 68, 6)
    c.set_source_rgba(0.62, 0.82, 0.62, a)
    c.fill_preserve()
    c.set_source_rgba(0.12, 0.38, 0.22, a)
    c.set_line_width(3)
    c.stroke()
    circle(c, 0, 0, 20, (0.75, 0.9, 0.75), a, (0.12, 0.38, 0.22), 2)
    txt(c, "$", 0, 12, 34, (0.12, 0.38, 0.22), LAB, "c", a)
    c.restore()


def legend_dot(c, x, y, col, label, size=54, a=1.0):
    circle(c, x, y - size * 0.3, size * 0.32, col, a)
    txt(c, label, x + 36, y, size, WHITE, LAB, "l", a)


# ------------------------------------------------------------------ scenes
def s_hook(c, t, p, gt, d):
    brass(c, 300, 130, 1320, 410, 20, 14)
    txt(c, "NATIONAL DEBT", 960, 212, 48, GREY, LAB)
    txt(c, "$40.7 TRILLION", 960, 438, 238, AMBER, LAB)
    cert(c, 450, 800, 0.98, "CHINA", "$564 BILLION", -0.05, 1.0, 3141592, col=FOREIGN)
    stamp(c, 470, 800, "FALSE", RED, e(gt, 0.9, 1.35), 140, -0.2)
    tk = 1 - e(gt, 4.2, 4.9)
    if tk > 0:
        txt(c, "CHINA HOLDS", 1360, 770, 150, WHITE, LAB, "c", tk)
        txt(c, "MOST OF IT?", 1360, 910, 150, AMBER, LAB, "c", tk)
    k = e(gt, 4.6, 5.4)
    if k > 0:
        cx, cy = 1050, 800
        ang0 = -math.pi / 2
        sl = 2 * math.pi * 0.014 * 6
        c.set_line_width(70)
        c.set_source_rgba(*OTHER, k)
        c.arc(cx, cy, 130, ang0 + sl, ang0 + 2 * math.pi)
        c.stroke()
        c.set_source_rgba(*RED, k)
        c.arc(cx, cy, 130, ang0, ang0 + sl)
        c.stroke()
        txt(c, "1.4%", 1260, 800, 190, RED, LAB, "l", k)
        txt(c, "IS CHINA'S SHARE", 1260, 870, 64, WHITE, LAB, "l", k)
        txt(c, "(slice enlarged)", 1260, 915, 30, GREY, LAB, "l", k * 0.9)


def s_wall(c, t, p, gt, d):
    txt(c, "EVERY DOLLAR IS AN I.O.U.", 960, 215, 100, WHITE, SERIF, "c", e(t, 0, 0.5))
    n = 0
    for j in range(3):
        for i in range(6):
            x = 235 + i * 290
            y = 340 + j * 165
            k = back(e(t, 0.3 + n * 0.09, 0.8 + n * 0.09))
            n += 1
            if k > 0:
                cert(c, x, y + (1 - k) * 60, 0.40, "", "", (i * 3 + j) % 5 * 0.008 - 0.016, clamp(k), 100 + n, qmark=True)
    k = e(t, d * 0.62, d * 0.62 + 0.5)
    txt(c, "WHO HOLDS THEM?", 960, 900, 150, AMBER, LAB, "c", k)


def s_tsy(c, t, p, gt, d):
    f = t / d
    k = back(e(f, 0.3, 0.46))
    if k > 0:
        cert(c, 990, 520, 1.1 * k, "A LOAN TO THE U.S.", "$1,000", 0, clamp(k), 777)
    # lender
    person(c, 230, 700, 1.6, WHITE, e(f, 0, 0.1))
    txt(c, "YOU", 230, 860, 60, WHITE, LAB, "c", e(f, 0, 0.1))
    for i in range(5):
        kk = e(f, 0.08 + i * 0.03, 0.3 + i * 0.03)
        if kk > 0 and kk < 1:
            coin(c, lerp(330, 700, kk), lerp(640, 540, kk) - math.sin(kk * math.pi) * 60, 28)
    txt(c, "YOU LEND $1,000", 330, 400, 76, AMBER, LAB, "c", e(f, 0.06, 0.2))
    # due date
    k2 = e(f, 0.55, 0.68)
    if k2 > 0:
        paper_card(c, 1380, 290, 320, 150, k2)
        txt(c, "DUE DATE", 1540, 345, 40, INKG, LAB, "c", k2)
        txt(c, "SET IN ADVANCE", 1540, 405, 46, RED, LAB, "c", k2)
    k3 = e(f, 0.72, 0.95)
    if k3 > 0:
        for i in range(5):
            kk = e(k3, i * 0.12, 0.5 + i * 0.12)
            if 0 < kk < 1:
                coin(c, lerp(1100, 1480, kk), lerp(520, 640, kk) - math.sin(kk * math.pi) * 50, 26)
        txt(c, "$1,000 + INTEREST", 1500, 770, 70, AMBER, LAB, "c", e(f, 0.78, 0.9))
        arrow(c, 1130, 540, 1330, 620, WHITE, 8, k3)


def s_deficit(c, t, p, gt, d):
    st = p["step"]
    if st == 0:
        k = e(t, 0, 0.5)
        cert(c, 520, 520, 0.62, "DEFICIT", "ONE YEAR", 0, k, 4001, col=RED)
        txt(c, "ONE YEAR OF BORROWING", 520, 720, 54, WHITE, LAB, "c", k)
        g = e(t, d * 0.45, d * 0.95)
        stack_bottom(c, 1320, 700, 15, 0.95, "THE DEBT", "ALL YEARS", INKG, clamp(g * 4), 14, 4002, max(0.07, g))
        txt(c, "EVERY YEAR ADDED UP", 1320, 920, 54, AMBER, LAB, "c", e(t, d * 0.45, d * 0.6))
        txt(c, "=", 920, 560, 120, GREY, LAB, "c", e(t, d * 0.4, d * 0.5))
    else:
        txt(c, "$119,000", 960, 400, 300, AMBER, LAB, "c", e(t, 0, 0.5))
        txt(c, "FOR EVERY PERSON LIVING IN THE U.S.", 960, 490, 70, WHITE, LAB, "c", e(t, 0.4, 0.9))
        for i in range(18):
            k = back(e(t, 1.0 + i * 0.07, 1.4 + i * 0.07))
            if k > 0:
                person(c, 200 + i * 94, 780 + (1 - k) * 40, 1.15, (0.9, 0.9, 0.85), clamp(k))
        txt(c, "(about $40.7T divided by the U.S. population)", 960, 940, 36, GREY, LAB, "c", e(t, 1.5, 2.2))


def frame_box(c, cx, cy, w, h, col, a, q=True, scale=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    brass(c, -w / 2, -h / 2, w, h, 12, 14, a)
    if q:
        txt(c, "?", 0, 80, 300, col, LAB, "c", a * 0.9)
    c.restore()


def s_frames(c, t, p, gt, d):
    st = p["step"]
    times = [0.45, 0.55, 0.64, 0.80]
    if st == 0:
        for i in range(4):
            cx = 330 + i * 420
            k = back(e(t, 0.1 + i * 0.12, 0.6 + i * 0.12))
            frame_box(c, cx, 480, 360, 470, HCOL[i], clamp(k), True, max(0.01, k))
            kk = e(t, d * times[i], d * times[i] + 0.4)
            nm = HNAME[i].split(" ")
            half = (len(nm) + 1) // 2
            txt(c, " ".join(nm[:half]), cx, 780, 54, HCOL[i], LAB, "c", kk)
            txt(c, " ".join(nm[half:]), cx, 840, 54, HCOL[i], LAB, "c", kk)
    else:
        z = e(t, 0.8, d * 0.9)
        for i in range(4):
            cx = 330 + i * 420
            if i == 0:
                sc = lerp(1.0, 2.2, z)
                cx2 = lerp(cx, 960, z)
                cy2 = lerp(480, 520, z)
                frame_box(c, cx2, cy2, 360, 470, HCOL[0], 1.0, False, sc)
                cert(c, cx2, cy2, 0.52 * sc, "GOVERNMENT TRUST FUNDS", "", 0, e(z, 0.2, 0.7), 4003, col=INKG)
                if z < 0.3:
                    txt(c, "?", cx2, cy2 + 80 * sc, 300 * sc, HCOL[0], LAB, "c", 1 - z * 3)
            else:
                frame_box(c, cx, 480, 360, 470, HCOL[i], 1 - z, True)
        if z < 0.5:
            txt(c, "GOVERNMENT TRUST FUNDS", 330, 780, 54, HCOL[0], LAB, "c", 1 - z * 2)


def trust_bar(c, t, stampit=False, alpha=1.0):
    x, y, w, h = 300, 470, 1320, 150
    k = e(t, 0, 1.0)
    a = 2.3 / 7.8
    rr(c, x, y, w * a * k, h, 10)
    c.set_source_rgba(*TRUST, alpha)
    c.fill()
    rr(c, x + w * a * k + 6, y, max(2, w * (1 - a) * k - 6), h, 10)
    c.set_source_rgba(0.62, 0.50, 0.20, alpha)
    c.fill()
    kk = e(t, 0.8, 1.3) * alpha
    txt(c, "$2.3T", x + w * a / 2, y + 100, 90, BLACK, LAB, "c", kk)
    txt(c, "$5.5T", x + w * a + (w * (1 - a)) / 2, y + 100, 90, WHITE, LAB, "c", kk)
    txt(c, "SOCIAL SECURITY", x + w * a / 2, y - 60, 50, TRUST, LAB, "c", kk)
    txt(c, "RETIREMENT FUND", x + w * a / 2, y - 12, 50, TRUST, LAB, "c", kk)
    txt(c, "OTHER GOVERNMENT ACCOUNTS", x + w * a + (w * (1 - a)) / 2, y - 12, 50, (0.85, 0.72, 0.38), LAB, "c", kk)
    txt(c, "$7.8 TRILLION OWED TO TRUST FUNDS", 960, 330, 86, WHITE, LAB, "c", e(t, 0, 0.5) * alpha)
    if stampit:
        txt(c, "FEDERAL AND MILITARY RETIREMENT FUNDS AND MORE", x + w * a + (w * (1 - a)) / 2, y + h + 56, 40, GREY, LAB, "c", e(t, 0.6, 1.2))
        stamp(c, 960, 800, "GOVERNMENT OWES GOVERNMENT", TRUST, e(t, 2.0, 2.5), 84, -0.04)


def s_trust(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        holder_stat(c, t, 0, "19%", "$7.8T")
    elif st == 1:
        trust_bar(c, t)
    elif st == 2:
        # paycheck -> fund -> benefits ; fund -> treasury (lent) ; special IOU back
        paper_card(c, 150, 330, 300, 200, e(f, 0, 0.1))
        txt(c, "PAYCHECK", 300, 385, 34, INKG, LAB, "c", e(f, 0, 0.1))
        for i in range(3):
            c.set_source_rgba(*INKG, 0.5 * e(f, 0, 0.1))
            c.rectangle(185, 410 + i * 28, 230 - i * 40, 10)
            c.fill()
        txt(c, "PAYROLL TAX", 300, 485, 40, RED, LAB, "c", e(f, 0, 0.1))
        arrow(c, 460, 430, 700, 430, WHITE, 8, e(f, 0.05, 0.22))
        txt(c, "TAXES IN", 580, 395, 38, WHITE, LAB, "c", e(f, 0.1, 0.22))
        brass(c, 710, 320, 420, 230, 14, 12)
        txt(c, "SOCIAL SECURITY", 920, 420, 52, AMBER, LAB, "c")
        txt(c, "TRUST FUND", 920, 480, 52, AMBER, LAB, "c")
        arrow(c, 1150, 430, 1400, 430, WHITE, 8, e(f, 0.25, 0.42))
        txt(c, "BENEFITS OUT", 1275, 395, 38, WHITE, LAB, "c", e(f, 0.3, 0.42))
        person(c, 1550, 480, 1.6, (0.9, 0.9, 0.85), e(f, 0.28, 0.4))
        # extra lent to treasury
        k = e(f, 0.5, 0.65)
        if k > 0:
            arrow(c, 920, 570, 920, 760, TRUST, 8, k)
            treasury_icon(c, 920, 790, 0.8, WHITE, k)
            txt(c, "THE EXTRA IS LENT", 1130, 660, 46, TRUST, LAB, "l", k)
        k2 = e(f, 0.72, 0.95)
        if k2 > 0:
            cx = lerp(1000, 1000, k2)
            cert(c, 1040, lerp(780, 560, k2), 0.30, "", "", 0.1, clamp(k2 * 3) * (1 - e(f, 0.95, 1.0)), 5001)
            txt(c, "SPECIAL SECURITY", 1380, 760, 44, WHITE, LAB, "l", e(f, 0.75, 0.88))
            txt(c, "(AN I.O.U.)", 1380, 810, 44, WHITE, LAB, "l", e(f, 0.78, 0.9))
    elif st == 3:
        brass(c, 560, 230, 800, 540, 18, 14)
        txt(c, "TRUST FUND", 960, 300, 56, AMBER, LAB, "c")
        for i in range(10):
            k = back(e(t, 0.2 + i * 0.1, 0.5 + i * 0.1))
            if k > 0:
                cert(c, 700 + (i % 5) * 140, 430 + (i // 5) * 120, 0.24 * clamp(k), "", "", 0, clamp(k), 6000 + i)
        for i in range(3):
            k = back(e(t, d * 0.55 + i * 0.35, d * 0.55 + 0.5 + i * 0.35))
            if k > 0:
                cert(c, 1180, 430 + i * 85, 0.2 * clamp(k), "", "", 0, clamp(k), 6100 + i, col=OTHER)
        txt(c, "+ INTEREST", 1180, 700, 40, OTHER, LAB, "c", e(t, d * 0.55, d * 0.7))
        # no cash
        for i in range(4):
            coin(c, 190 + (i % 2) * 70, 440 + (i // 2) * 60, 28, 0.9)
        txt(c, "NO CASH", 225, 560, 60, RED, LAB, "c", e(t, 0.5, 1.0))
        line(c, [(110, 380), (340, 520)], RED, 14, e(t, 0.5, 1.0), 1.0)
        txt(c, "A BOX OF I.O.U.s, NOT A VAULT OF CASH", 960, 870, 70, WHITE, LAB, "c", e(t, d * 0.3, d * 0.5))
    elif st == 4:
        brass(c, 200, 330, 400, 240, 14, 12)
        txt(c, "TRUST FUND", 400, 440, 56, AMBER, LAB, "c")
        treasury_icon(c, 960, 440, 1.0, WHITE)
        person(c, 1650, 450, 1.4, (0.9, 0.9, 0.85))
        txt(c, "THE PUBLIC", 1650, 590, 44, WHITE, LAB, "c")
        # cert moves fund -> treasury
        k = e(f, 0.1, 0.35)
        if k < 1:
            cert(c, lerp(480, 840, k), lerp(450, 430, k) - math.sin(k * math.pi) * 50, 0.32, "", "", 0.1, 1.0, 7001)
        txt(c, "CASHES IN AN I.O.U.", 560, 650, 46, WHITE, LAB, "c", e(f, 0.1, 0.25))
        k2 = e(f, 0.45, 0.65)
        if 0 < k2 < 1:
            coin(c, lerp(1560, 1080, k2), 470 - math.sin(k2 * math.pi) * 60, 30)
        txt(c, "BORROWS CASH FROM THE PUBLIC", 1300, 700, 46, AMBER, LAB, "c", e(f, 0.45, 0.6))
        k3 = e(f, 0.72, 0.95)
        if 0 < k3 < 1:
            coin(c, lerp(840, 480, k3), 470 - math.sin(k3 * math.pi) * 60, 30)
        txt(c, "CASH GOES TO BENEFITS", 560, 740, 46, OTHER, LAB, "c", e(f, 0.72, 0.9))
    else:
        trust_bar(c, 99, True)


def s_gdp(c, t, p, gt, d):
    x, w = 300, 1100
    txt(c, "DEBT VS THE ECONOMY", 960, 250, 80, WHITE, LAB, "c", e(t, 0, 0.5))
    k = e(t, 0.4, 1.4)
    txt(c, "DEBT HELD BY THE PUBLIC", x, 400, 54, WHITE, LAB, "l", k)
    rr(c, x, 420, w * k, 120, 10)
    c.set_source_rgb(0.45, 0.68, 0.55)
    c.fill()
    txt(c, "$32.9T", x + w + 40, 505, 80, AMBER, LAB, "l", k)
    k2 = e(t, d * 0.4, d * 0.4 + 1.0)
    txt(c, "ONE YEAR OF U.S. ECONOMIC OUTPUT (GDP)", x, 660, 54, WHITE, LAB, "l", k2)
    rr(c, x, 680, w * 0.995 * k2, 120, 10)
    c.set_source_rgb(0.40, 0.58, 0.85)
    c.fill()
    txt(c, "$32.6T", x + w + 40, 765, 80, AMBER, LAB, "l", k2)
    txt(c, "ABOUT THE SAME", 960, 920, 90, OTHER, LAB, "c", e(t, d * 0.7, d * 0.8))
    txt(c, "(GDP: Q2 2026, annualized)", 1620, 1000, 28, GREY, LAB, "r")


def s_twobars(c, t, p, gt, d):
    if p["step"] == 1:
        return s_gdp(c, t, p, gt, d)
    f = t / d
    x, w = 300, 1320
    s_ = w / 40.7
    txt(c, "TWO WAYS TO COUNT THE DEBT", 960, 250, 80, WHITE, LAB, "c", e(t, 0, 0.5))
    k = e(t, 0.4, 1.4)
    txt(c, "GROSS DEBT", 300, 400, 54, WHITE, LAB, "l", k)
    rr(c, x, 420, 32.9 * s_ * k, 110, 10)
    c.set_source_rgb(0.45, 0.68, 0.55)
    c.fill()
    rr(c, x + 32.9 * s_ * k + 4, 420, 7.8 * s_ * k - 4, 110, 10)
    c.set_source_rgb(*TRUST)
    c.fill()
    txt(c, "$40.7T", 1560, 400, 70, AMBER, LAB, "r", k)
    k2 = e(f, 0.42, 0.55)
    txt(c, "HELD BY THE PUBLIC", 300, 660, 54, WHITE, LAB, "l", k2)
    rr(c, x, 680, 32.9 * s_ * k2, 110, 10)
    c.set_source_rgb(0.45, 0.68, 0.55)
    c.fill()
    txt(c, "$32.9T", 1560, 660, 70, AMBER, LAB, "r", k2)
    k3 = e(f, 0.6, 0.75)
    if k3 > 0:
        c.set_dash([14, 10])
        c.set_line_width(5)
        c.set_source_rgba(*TRUST, k3)
        rr(c, x + 32.9 * s_ + 4, 680, 7.8 * s_ - 4, 110, 10)
        c.stroke()
        c.set_dash([])
        txt(c, "LEFT OUT: TRUST FUNDS", x + 32.9 * s_ + 4 + 7.8 * s_ / 2, 830, 40, TRUST, LAB, "c", k3)


def s_fed(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        holder_stat(c, t, 1, "11%", "$4.6T")
    elif st == 1:
        # dial
        cx, cy = 960, 330
        c.set_line_width(26)
        for i, col in enumerate([OTHER, (0.9, 0.85, 0.3), FOREIGN]):
            c.set_source_rgba(*col, 0.9)
            c.arc(cx, cy + 90, 190, math.pi + i * math.pi / 3 + 0.02, math.pi + (i + 1) * math.pi / 3 - 0.02)
            c.stroke()
        ang = math.pi + math.pi * (0.35 + 0.3 * math.sin(f * 7))
        line(c, [(cx, cy + 90), (cx + 150 * math.cos(ang), cy + 90 + 150 * math.sin(ang))], WHITE, 10)
        circle(c, cx, cy + 90, 18, WHITE)
        txt(c, "INTEREST RATES", cx, cy - 130, 64, WHITE, LAB, "c", e(t, 0, 0.5))
        # shelf -> vault
        bank_icon(c, 330, 760, 1.2, (0.7, 0.8, 0.9))
        txt(c, "BANKS AND INVESTORS", 330, 880, 44, WHITE, LAB, "c")
        brass(c, 1360, 640, 360, 230, 14, 12)
        txt(c, "THE FED", 1540, 740, 64, FED, LAB, "c")
        txt(c, "VAULT", 1540, 800, 50, FED, LAB, "c")
        for i in range(4):
            kk = e((t * 0.5 + i * 0.25) % 1.4 / 1.4, 0, 1)
            cert(c, lerp(480, 1300, kk), 760 - math.sin(kk * math.pi) * 80, 0.20, "", "", 0.05, 1.0, 7100 + i)
        txt(c, "BUYS AND SELLS TREASURIES", 900, 940, 50, AMBER, LAB, "c", e(f, 0.5, 0.7))
    elif st == 2:
        pts = [(380, 780), (700, 650), (940, 600), (1080, 700), (1200, 420), (1330, 330), (1560, 460)]
        k = e(t, 0.2, d * 0.7)
        # filled area
        pp = pts
        c.save()
        total = k * (len(pp) - 1)
        c.move_to(pp[0][0], 880)
        c.line_to(*pp[0])
        for i in range(1, len(pp)):
            kk = clamp(total - (i - 1))
            if kk <= 0:
                break
            c.line_to(lerp(pp[i - 1][0], pp[i][0], kk), lerp(pp[i - 1][1], pp[i][1], kk))
        lastx = c.get_current_point()[0]
        c.line_to(lastx, 880)
        c.close_path()
        c.set_source_rgba(*FED, 0.35)
        c.fill()
        c.restore()
        line(c, pp, FED, 12, 1.0, k)
        c.set_source_rgba(*GREY, 0.8)
        c.set_line_width(3)
        c.move_to(330, 880)
        c.line_to(1620, 880)
        c.stroke()
        for x, y_, lab, ky in ((380, 930, "2008", 0.0), (1200, 930, "2020", 0.52), (1330, 290, "PEAK 2022", 0.64)):
            kk = e(k, ky, ky + 0.1)
            txt(c, lab, x, y_, 44, WHITE, LAB, "c", kk)
        txt(c, "FED'S TREASURY HOLDINGS", 960, 240, 76, WHITE, LAB, "c", e(t, 0, 0.5))
        txt(c, "(shape illustrative)", 1620, 1000, 30, GREY, LAB, "r")
    else:
        treasury_icon(c, 420, 480, 1.3, WHITE)
        brass(c, 1180, 360, 400, 240, 14, 12)
        txt(c, "THE FED", 1380, 490, 66, FED, LAB, "c")
        k = e(f, 0.05, 0.3)
        arrow(c, 560, 450, 1150, 450, WHITE, 8, k)
        txt(c, "INTEREST ON THE BONDS", 860, 420, 46, AMBER, LAB, "c", k)
        k2 = e(f, 0.35, 0.5)
        arrow(c, 1380, 620, 1380, 780, GREY, 8, k2)
        txt(c, "PAYS ITS OWN COSTS", 1380, 840, 46, GREY, LAB, "c", k2)
        k3 = e(f, 0.6, 0.85)
        arrow(c, 1150, 560, 560, 560, OTHER, 10, k3)
        txt(c, "ANY PROFIT GOES BACK", 860, 620, 52, OTHER, LAB, "c", e(f, 0.6, 0.75))


def s_foreign(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        holder_stat(c, t, 2, "23%", "$9.2T")
    elif st == 1:
        txt(c, "LARGEST FOREIGN HOLDERS, SEPT 2026", 960, 240, 72, WHITE, LAB, "c", e(t, 0, 0.5))
        rows = [("JAPAN", 1063, "$1,063B", 0.18), ("UNITED KINGDOM", 986, "$986B", 0.45), ("CHINA", 564, "$564B", 0.72)]
        for i, (nm, v, lab, f0) in enumerate(rows):
            y = 330 + i * 170
            k = e(f, f0, f0 + 0.16)
            txt(c, nm, 500, y + 80, 64, WHITE, LAB, "r", min(1, k * 3))
            rr(c, 530, y, max(4, v * 0.95 * k), 110, 10)
            c.set_source_rgba(*(FOREIGN if nm != "CHINA" else (0.95, 0.55, 0.30)), 1)
            c.fill()
            if k > 0.9:
                txt(c, lab, 530 + v * 0.95 + 24, y + 82, 70, AMBER, LAB, "l")
    elif st == 2:
        txt(c, "CHINA'S HOLDINGS", 960, 240, 80, WHITE, LAB, "c", e(t, 0, 0.5))
        k = e(t, 0.5, d * 0.6)
        x0, y0, x1, y1 = 450, 440, 1450, 740
        line(c, [(x0, y0), (lerp(x0, x1, k), lerp(y0, y1, k))], FOREIGN, 16, 1.0, 1.0)
        circle(c, x0, y0, 22, WHITE, 1, FOREIGN, 8)
        txt(c, "2013", x0, y0 - 100, 54, GREY, LAB, "c")
        txt(c, "$1.3 TRILLION", x0, y0 - 40, 70, WHITE, LAB, "c")
        if k > 0.98:
            circle(c, x1, y1, 22, WHITE, 1, FOREIGN, 8)
            txt(c, "SEPT 2026", x1, y1 + 80, 54, GREY, LAB, "c")
            txt(c, "$564 BILLION", x1, y1 + 140, 70, WHITE, LAB, "c")
            txt(c, "LOWEST IN MORE THAN 18 YEARS", 960, 900, 64, AMBER, LAB, "c", e(t, d * 0.75, d * 0.85))
    elif st == 2.5:
        txt(c, "WHY THE MYTH STUCK", 960, 240, 90, WHITE, LAB, "c", e(t, 0, 0.5))
        k = back(e(t, 0.3, 0.9))
        paper_card(c, 260, 320, 600, 460, clamp(k))
        txt(c, "MUCH OF THE 2010s", 560, 400, 50, INKG, LAB, "c", clamp(k))
        txt(c, "#1", 560, 600, 250, RED, LAB, "c", clamp(k))
        txt(c, "CHINA", 560, 700, 80, INKG, LAB, "c", clamp(k))
        k2 = back(e(t, d * 0.5, d * 0.5 + 0.6))
        paper_card(c, 1060, 320, 600, 460, clamp(k2))
        txt(c, "TODAY", 1360, 400, 50, INKG, LAB, "c", clamp(k2))
        txt(c, "#1", 1360, 600, 250, INKG, LAB, "c", clamp(k2))
        txt(c, "JAPAN", 1360, 700, 80, INKG, LAB, "c", clamp(k2))
        txt(c, "CHINA IS #3", 1360, 750, 40, RED, LAB, "c", clamp(k2))
    elif st == 3:
        txt(c, "WHERE HELD  ≠  WHO OWNS", 960, 240, 90, WHITE, LAB, "c", e(t, 0, 0.5))
        for i, (nm, amt) in enumerate((("BELGIUM", "$508B"), ("CAYMAN ISLANDS", "$487B"))):
            x = 360 + i * 700
            k = e(t, 0.6 + i * 0.4, 1.2 + i * 0.4)
            brass(c, x, 360, 560, 220, 14, 12, k)
            txt(c, nm, x + 280, 450, 66, AMBER, LAB, "c", k)
            txt(c, amt, x + 280, 530, 80, WHITE, LAB, "c", k)
            txt(c, "FINANCIAL CENTER", x + 280, 640, 44, GREY, LAB, "c", k)
        k = e(t, d * 0.62, d * 0.72)
        txt(c, "SOME ECONOMISTS: CHINA'S TRUE HOLDINGS ARE HIGHER", 960, 820, 62, FOREIGN, LAB, "c", k)
    elif st == 4:
        # ship -> dollars -> vaults
        y = 540
        c.set_source_rgba(0.15, 0.35, 0.45, 0.9)
        c.move_to(0, y + 70)
        for i in range(0, 900, 20):
            c.line_to(i, y + 70 + 10 * math.sin(i * 0.05 + t * 2))
        c.line_to(900, 760)
        c.line_to(0, 760)
        c.close_path()
        c.fill()
        c.save()
        c.translate(190 + e(f, 0, 0.5) * 40, y + math.sin(t * 2) * 6)
        c.move_to(0, 0)
        c.line_to(480, 0)
        c.line_to(430, 70)
        c.line_to(40, 70)
        c.close_path()
        c.set_source_rgb(0.30, 0.34, 0.38)
        c.fill()
        for r in range(2):
            for i, col in enumerate([(0.85, 0.35, 0.25), (0.30, 0.55, 0.80), (0.90, 0.70, 0.25), (0.40, 0.75, 0.50), (0.85, 0.35, 0.25), (0.30, 0.55, 0.80)]):
                c.rectangle(40 + i * 66, -56 - r * 56, 60, 52)
                c.set_source_rgb(*col)
                c.fill()
        c.restore()
        txt(c, "THEY SELL GOODS TO AMERICA", 340, 340, 52, WHITE, LAB, "c", e(f, 0.05, 0.2))
        k = e(f, 0.3, 0.55)
        for i in range(4):
            kk = (k * 1.0 + i * 0.12) % 1.0 if k > 0 else 0
            if k > 0:
                dollar_bill(c, lerp(760, 1180, kk), 520 - math.sin(kk * math.pi) * 40 + 60 * (i % 2), 0.7, 1.0, 0.1)
        txt(c, "THEY EARN DOLLARS", 960, 330, 52, AMBER, LAB, "c", e(f, 0.3, 0.45))
        vk = e(f, 0.55, 0.8)
        for i, nm in enumerate(("TOKYO", "LONDON", "BEIJING")):
            bank_icon(c, 1300 + i * 190 - 90, 600, 0.9, FOREIGN, vk)
            txt(c, nm, 1300 + i * 190 - 90, 710, 40, WHITE, LAB, "c", vk)
        txt(c, "SAFE, EASY TO SELL, PAYS INTEREST", 960, 940, 64, OTHER, LAB, "c", e(f, 0.78, 0.92))
    elif st == 5:
        txt(c, "WHO OWNS THE FOREIGN SHARE?", 960, 260, 80, WHITE, LAB, "c", e(t, 0, 0.5))
        x, y, w, h = 300, 420, 1320, 170
        k = e(t, 0.3, 1.2)
        rr(c, x, y, w * 0.4 * k, h, 10)
        c.set_source_rgb(*FOREIGN)
        c.fill()
        rr(c, x + w * 0.4 * k + 5, y, max(2, w * 0.6 * k - 5), h, 10)
        c.set_source_rgb(0.62, 0.30, 0.28)
        c.fill()
        kk = e(t, 1.0, 1.5)
        txt(c, "~40%", x + w * 0.2, y + 120, 110, WHITE, LAB, "c", kk)
        txt(c, "~60%", x + w * 0.7, y + 120, 110, WHITE, LAB, "c", kk)
        txt(c, "GOVERNMENTS AND", x + w * 0.2, y + 250, 46, FOREIGN, LAB, "c", kk)
        txt(c, "CENTRAL BANKS", x + w * 0.2, y + 300, 46, FOREIGN, LAB, "c", kk)
        txt(c, "PRIVATE INVESTORS", x + w * 0.7, y + 250, 46, (0.9, 0.55, 0.5), LAB, "c", kk)
        txt(c, "BANKS, PENSION FUNDS, COMPANIES", x + w * 0.7, y + 300, 40, GREY, LAB, "c", kk)
    else:
        txt(c, "TOTAL FOREIGN HOLDINGS", 960, 260, 80, WHITE, LAB, "c", e(t, 0, 0.5))
        brass(c, 300, 340, 560, 300, 18, 14, e(t, 0.2, 0.7))
        txt(c, "RECORD, FEB 2026", 580, 430, 44, GREY, LAB, "c", e(t, 0.4, 0.9))
        txt(c, "$9.49T", 580, 570, 150, AMBER, LAB, "c", e(t, 0.4, 0.9))
        k = e(t, 1.2, 1.9)
        arrow(c, 900, 490, 1020, 490, FOREIGN, 12, k, 36)
        brass(c, 1060, 340, 560, 300, 18, 14, k)
        txt(c, "SEPT 2026", 1340, 430, 44, GREY, LAB, "c", k)
        txt(c, "$9.24T", 1340, 570, 150, FOREIGN, LAB, "c", k)


def s_other(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        holder_stat(c, t, 3, "47%", "$19.1T")
    elif st == 1:
        items = [("BANKS", "bank"), ("MUTUAL FUNDS", "fund"), ("PENSION FUNDS", "pension"), ("INSURERS", "ins"), ("STATE + LOCAL GOVERNMENTS", "state"), ("PEOPLE", "person")]
        for i, (nm, kind) in enumerate(items):
            cx = 420 + (i % 3) * 540
            cy = 360 + (i // 3) * 330
            k = back(e(t, 0.2 + i * 0.5, 0.7 + i * 0.5))
            if k <= 0:
                continue
            a = clamp(k)
            paper_card(c, cx - 230, cy - 120, 460, 260, a)
            if kind == "bank":
                bank_icon(c, cx, cy - 30, 0.9, INKG, a)
            elif kind == "fund":
                for j, hh in enumerate((50, 80, 65, 100)):
                    rr(c, cx - 70 + j * 38, cy + 30 - hh, 26, hh, 4)
                    c.set_source_rgba(*INKG, a)
                    c.fill()
            elif kind == "pension":
                circle(c, cx, cy - 20, 52, INKG, a)
                txt(c, "65", cx, cy - 0, 54, PAPER, LAB, "c", a)
            elif kind == "ins":
                c.move_to(cx, cy - 70)
                c.curve_to(cx + 70, cy - 60, cx + 70, cy + 10, cx, cy + 50)
                c.curve_to(cx - 70, cy + 10, cx - 70, cy - 60, cx, cy - 70)
                c.set_source_rgba(*INKG, a)
                c.fill()
            elif kind == "state":
                bank_icon(c, cx, cy - 30, 0.9, RED, a)
            else:
                person(c, cx, cy - 10, 1.4, INKG, a)
            txt(c, nm, cx, cy + 108, 36 if len(nm) < 20 else 30, INKG, LAB, "c", a)
    elif st == 2:
        paper_card(c, 340, 200, 700, 640, e(t, 0, 0.5))
        txt(c, "YOUR RETIREMENT ACCOUNT", 690, 280, 52, INKG, LAB, "c", e(t, 0, 0.5))
        parts = [(0.40, (0.35, 0.55, 0.80), "STOCKS"), (0.25, (0.80, 0.60, 0.25), "CASH"), (0.20, OTHER, "TREASURIES"), (0.15, (0.55, 0.45, 0.70), "OTHER")]
        ang = -math.pi / 2
        for j, (v, col, nm) in enumerate(parts):
            k = e(t, 0.5 + j * 0.3, 1.0 + j * 0.3)
            a2 = ang + 2 * math.pi * v * k
            c.move_to(690, 560)
            c.arc(690, 560, 210, ang, a2)
            c.close_path()
            c.set_source_rgb(*col)
            c.fill()
            mid = ang + math.pi * v
            if k > 0.9:
                txt(c, nm, 690 + 140 * math.cos(mid), 560 + 140 * math.sin(mid) + 10, 36, WHITE, LAB, "c")
            ang += 2 * math.pi * v
        arrow(c, 1250, 440, 880, 520, AMBER, 10, e(t, 2.4, 3.0))
        k = e(t, 2.6, 3.2)
        cert(c, 1400, 380, 0.6, "TREASURIES", "", 0, k, 8001)
        txt(c, "A SLICE OF THE DEBT", 1400, 590, 54, AMBER, LAB, "c", k)
    else:
        for i, (a1, b1, sym) in enumerate((("CAN BE SOLD", "QUICKLY", "clock"), ("PAYMENTS COME FROM", "THE GOVERNMENT", "bank"))):
            cx = 500 + i * 920
            k = back(e(t, 0.2 + i * 1.5, 0.8 + i * 1.5))
            if k <= 0:
                continue
            a = clamp(k)
            paper_card(c, cx - 330, 250, 660, 340, a)
            if sym == "clock":
                circle(c, cx, 380, 62, INKG, a)
                circle(c, cx, 380, 52, PAPER, a)
                line(c, [(cx, 380), (cx, 340)], INKG, 8, a)
                line(c, [(cx, 380), (cx + 30, 390)], INKG, 8, a)
            else:
                bank_icon(c, cx, 370, 0.9, INKG, a)
            txt(c, a1, cx, 510, 50, INKG, LAB, "c", a)
            txt(c, b1, cx, 566, 50, RED, LAB, "c", a)
        k = e(t, d * 0.62, d * 0.8)
        txt(c, "CLOSE TO", 960, 770, 70, WHITE, LAB, "c", k)
        txt(c, "CASH THAT EARNS INTEREST", 960, 860, 110, AMBER, LAB, "c", k)


def s_pay(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    if st == 0:
        cert(c, 960, 500, 1.0, "OLD I.O.U.", "$1,000", 0, 1.0, 9001)
        k = e(t, 0.4, 1.4)
        for sgn in (1, -1):
            c.set_line_width(18)
            c.set_source_rgba(*AMBER, 0.95)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            a0 = (0.2 if sgn == 1 else math.pi + 0.2)
            c.arc(960, 500, 360, a0, a0 + 2.4 * k)
            c.stroke()
            ae = a0 + 2.4 * k
            if k > 0.2:
                c.save()
                c.translate(960 + 360 * math.cos(ae), 500 + 360 * math.sin(ae))
                c.rotate(ae + math.pi / 2)
                c.move_to(0, 0)
                c.line_to(-26, -48)
                c.line_to(26, -48)
                c.close_path()
                c.set_source_rgba(*AMBER, 1)
                c.fill()
                c.restore()
        txt(c, "ROLLED OVER", 960, 960, 130, AMBER, LAB, "c", e(t, d * 0.5, d * 0.65))
    elif st == 1:
        txt(c, "TREASURIES COME IN LENGTHS", 960, 240, 80, WHITE, LAB, "c", e(t, 0, 0.5))
        x0, sc = 300, 1320 / 30
        c.set_source_rgba(*GREY, 0.8)
        c.set_line_width(3)
        c.move_to(x0, 820)
        c.line_to(x0 + 1320, 820)
        c.stroke()
        for yrs in (0, 10, 20, 30):
            txt(c, "%d" % yrs if yrs else "0", x0 + yrs * sc, 870, 40, GREY, LAB, "c")
        txt(c, "YEARS", x0 + 1320 + 70, 870, 36, GREY, LAB, "c")
        rows = [("BILLS", "A YEAR OR LESS", 0, 1, 0.2, (0.55, 0.78, 0.90)), ("NOTES", "2 TO 10 YEARS", 2, 10, 0.45, (0.55, 0.85, 0.60)), ("BONDS", "20 OR 30 YEARS", 20, 30, 0.72, (0.93, 0.74, 0.28))]
        for i, (nm, sub, a1, b1, f0, col) in enumerate(rows):
            y = 340 + i * 130
            k = e(f, f0, f0 + 0.15)
            ww = max(44, (b1 - a1) * sc) * k
            rr(c, x0 + a1 * sc, y, ww, 90, 10)
            c.set_source_rgb(*col)
            c.fill()
            txt(c, nm, x0 + a1 * sc + (ww + 24 if a1 < 15 else -24), y + 62, 64, WHITE, LAB, "l" if a1 < 15 else "r", clamp(k * 3))
            if a1 < 15:
                txt(c, sub, x0 + a1 * sc + ww + 24 + tw(c, nm, 64) + 24, y + 62, 44, col, LAB, "l", clamp(k * 3))
            else:
                txt(c, sub, x0 + a1 * sc - 24 - tw(c, nm, 64) - 24, y + 62, 44, col, LAB, "r", clamp(k * 3))
    elif st == 2:
        treasury_icon(c, 300, 500, 1.3, WHITE)
        txt(c, "AUCTION EVERY WEEK", 300, 780, 56, AMBER, LAB, "c", e(t, 0, 0.5))
        for i in range(4):
            k = back(e(t, 0.4 + i * 0.15, 0.9 + i * 0.15))
            if k > 0:
                bank_icon(c, 820 + (i % 2) * 220, 380 + (i // 2) * 220, 0.7 * clamp(k), (0.7, 0.8, 0.9), clamp(k))
        txt(c, "BIG BANKS BID FIRST", 930, 810, 54, WHITE, LAB, "c", e(f, 0.3, 0.45))
        arrow(c, 440, 500, 640, 500, WHITE, 8, e(f, 0.25, 0.4))
        k = e(f, 0.55, 0.75)
        arrow(c, 1120, 500, 1330, 500, WHITE, 8, k)
        for i in range(5):
            person(c, 1470 + (i % 3) * 120, 430 + (i // 3) * 170, 1.0, (0.9, 0.9, 0.85), k)
        txt(c, "INVESTORS WORLDWIDE", 1540, 810, 54, WHITE, LAB, "c", k)
    elif st == 3:
        left = 4 - int(e(f, 0.1, 0.45) * 4)
        cert(c, 700, 480, 0.95, "OLD I.O.U.", "$1,000", 0, 1 - e(f, 0.55, 0.7), 9101)
        txt(c, "DUE IN %d DAY%s" % (left, "" if left == 1 else "S") if left else "DUE TODAY", 700, 720, 60, AMBER if left else RED, LAB, "c", e(f, 0, 0.1))
        stamp(c, 700, 480, "PAID BACK", OTHER, e(f, 0.45, 0.58), 90, -0.1)
        k = e(f, 0.6, 0.85)
        if k > 0:
            cert(c, lerp(1750, 1280, ease_out(k)), 480, 0.95, "NEW I.O.U.", "$1,000", 0, clamp(k * 2), 9102)
            txt(c, "SOLD TO SOMEONE NEW", 1280, 720, 54, AMBER, LAB, "c", e(f, 0.75, 0.9))
    elif st == 4:
        brass(c, 460, 330, 1000, 340, 20, 16)
        txt(c, "AVERAGE INTEREST RATE", 960, 430, 54, GREY, LAB, "c", e(t, 0.2, 0.7))
        txt(c, "3.4%", 960, 600, 240, AMBER, LAB, "c", e(t, 0.3, 0.8))
        txt(c, "ON MARKETABLE TREASURY DEBT, JULY 2026", 960, 790, 52, WHITE, LAB, "c", e(t, 0.6, 1.1))
        k = back(e(f, 0.62, 0.78))
        if k > 0:
            cert(c, 560, 930, 0.3 * clamp(k), "", "", -0.08, clamp(k), 9301)
            arrow(c, 700, 930, 1000, 930, WHITE, 6, e(f, 0.68, 0.8), 20)
            txt(c, "NEW I.O.U. = THE RATE OF THE DAY", 1020, 950, 54, AMBER, LAB, "l", e(f, 0.72, 0.85))
    else:
        treasury_icon(c, 960, 500, 1.4, WHITE)
        pos = [(300, 260), (1620, 260), (300, 800), (1620, 800)]
        counts = [4, 2, 5, 9]
        for i in range(4):
            x, y = pos[i]
            stack_bottom(c, x, y + 60, 4, 0.42, "", "", HCOL[i], 1.0, 12, 100 + i)
            txt(c, HSHORT[i], x, (y + 175) if y < 500 else (y - 120), 48, HCOL[i], LAB, "c")
            tot = counts[i]
            for j in range(tot):
                kk = ((f * 2.4 + j / tot) % 1.0)
                coin(c, lerp(960, x, kk), lerp(500, y, kk), 20, 1.0 if kk < 0.9 else 1 - (kk - 0.9) * 10)
        txt(c, "INTEREST FLOWS TO ALL FOUR", 960, 1000, 54, AMBER, LAB, "c", e(t, 0.5, 1.0))


def s_pie(c, t, p, gt, d):
    st = p["step"]
    f = t / d
    cx, cy, r = 640, 560, 330
    vals = SHARES
    if st == 0:
        amts = ["$7.8T", "$4.6T", "$9.2T", "$19.1T"]
        ang = -math.pi / 2
        times = [0.16, 0.34, 0.5, 0.7]
        for i in range(4):
            k = e(f, times[i] - 0.1, times[i] + 0.08)
            a2 = ang + 2 * math.pi * vals[i] / 100 * k
            c.move_to(cx, cy)
            c.arc(cx, cy, r, ang, a2)
            c.close_path()
            c.set_source_rgb(*HCOL[i])
            c.fill_preserve()
            c.set_source_rgb(*WALL1)
            c.set_line_width(6)
            c.stroke()
            ang += 2 * math.pi * vals[i] / 100
            if k > 0.5:
                y = 330 + i * 150
                legend_dot(c, 1100, y, HCOL[i], HNAME[i], 56, clamp(k * 2 - 1))
                txt(c, "%d%%" % round(vals[i]) if i != 1 else "11%", 1740, y, 70, HCOL[i], LAB, "r", clamp(k * 2 - 1))
    elif st == 1:
        ang = -math.pi / 2
        for i in range(4):
            a2 = ang + 2 * math.pi * vals[i] / 100
            c.move_to(cx, cy)
            c.arc(cx, cy, r, ang, a2)
            c.close_path()
            dim = 1.0 if i == 2 else 0.55
            c.set_source_rgba(*HCOL[i], dim if e(t, 3, 4) > 0 or True else 1)
            c.fill_preserve()
            c.set_source_rgb(*WALL1)
            c.set_line_width(6)
            c.stroke()
            ang += 2 * math.pi * vals[i] / 100
        k = e(f, 0.05, 0.3)
        txt(c, "77%", 1380, 400, 230, OTHER, LAB, "c", k)
        txt(c, "HELD INSIDE THE U.S.", 1380, 470, 56, WHITE, LAB, "c", k)
        txt(c, "GOVERNMENT ACCOUNTS, THE FED,", 1380, 520, 38, GREY, LAB, "c", k)
        txt(c, "AMERICAN BANKS, FUNDS AND SAVERS", 1380, 562, 38, GREY, LAB, "c", k)
        k2 = e(f, 0.55, 0.8)
        txt(c, "23%", 1380, 770, 200, FOREIGN, LAB, "c", k2)
        txt(c, "HELD ABROAD. BIGGEST: JAPAN", 1380, 840, 56, WHITE, LAB, "c", k2)
    else:
        stack_bottom(c, 760, 820, 16, 1.25, "OWED AT HOME", "77%", INKG, 1.0, 15, 4000, 1.0)
        k = e(t, 0.4, 1.0)
        cert(c, 1560, 780, 0.34, "CHINA", "1.4%", -0.04, k, 3141592, col=FOREIGN)
        txt(c, "CHINA", 1560, 900, 50, FOREIGN, LAB, "c", k)
        txt(c, "THE CERTIFICATE FROM THE START", 1480, 330, 56, WHITE, LAB, "c", e(t, 0.8, 1.4))
        arrow(c, 1560, 380, 1560, 640, AMBER, 8, e(t, 1.0, 1.6))


def s_data(c, t, p, gt, d):
    txt(c, "CHECK IT YOURSELF", 960, 250, 100, WHITE, LAB, "c", e(t, 0, 0.5))
    for i, (a1, b1, c1) in enumerate((("DEBT TO THE PENNY", "EVERY BUSINESS DAY", "THE TOTAL"), ("TIC REPORTS", "EVERY MONTH", "FOREIGN HOLDINGS"))):
        x = 330 + i * 700
        k = back(e(t, 0.5 + i * 2.2, 1.1 + i * 2.2))
        if k <= 0:
            continue
        brass(c, x, 360, 560, 340, 18, 14, clamp(k))
        txt(c, a1, x + 280, 470, 66, AMBER, LAB, "c", clamp(k))
        txt(c, b1, x + 280, 560, 58, WHITE, LAB, "c", clamp(k))
        txt(c, c1, x + 280, 640, 46, GREY, LAB, "c", clamp(k))
    txt(c, "TREASURY'S OWN DATA", 960, 880, 90, OTHER, LAB, "c", e(t, d * 0.78, d * 0.9))


def s_plain(c, t, p, gt, d):
    txt(c, "WHO IS OWED.", 960, 440, 230, WHITE, SERIF, "c", e(t, 0, 0.6))
    line(c, [(560, 520), (1360, 520)], BRASS, 6, e(t, 0.6, 1.0))
    txt(c, "NOT GOOD OR BAD.", 960, 700, 150, AMBER, SERIF, "c", e(t, 1.2, 1.8))


def s_end(c, t, p, gt, d):
    logo(c, 960 - 60 * 3.6, 150, 3.6, e(t, 0, 0.6))
    txt(c, "FOLLOW THE MONEY.", 960, 640, 150, WHITE, LAB, "c", e(t, 0.3, 0.9))
    k = e(t, 1.2, 1.9)
    brass(c, 380, 720, 1160, 140, 18, 12, k)
    txt(c, "NEXT: WHERE THE INTEREST GOES", 960, 810, 84, AMBER, LAB, "c", k)
    k2 = back(e(t, 2.2, 2.8))
    rr(c, 960 - 160, 900, 320, 90, 45)
    c.set_source_rgba(0.85, 0.16, 0.16, clamp(k2))
    c.fill()
    txt(c, "FOLLOW", 960, 965, 70, WHITE, LAB, "c", clamp(k2))


SC = dict(data=s_data, hook=s_hook, wall=s_wall, tsy=s_tsy, deficit=s_deficit, frames=s_frames, trust=s_trust, twobars=s_twobars, fed=s_fed,
          foreign=s_foreign, other=s_other, pay=s_pay, pie=s_pie, plain=s_plain, end=s_end)


# ------------------------------------------------------------------ chrome
def chrome(c, L, i, t, show_ticker=True):
    logo(c, 46, 22, 0.55)
    txt(c, "MONEY MAP", 96, 60, 38, WHITE, LAB, "l")
    rev = -1
    rt = 99
    t0s = L[i].get("_t0", 0)
    for j in range(i + 1):
        if "reveal" in L[j]["p"]:
            rev = L[j]["p"]["reveal"]
    if L[i]["scene"] in ("pie", "data", "plain"):
        rev = 3
    if rev < 0:
        return
    x0, w, y, h = 1330, 520, 44, 26
    txt(c, "WHO HOLDS THE DEBT", x0 + w, 34, 24, GREY, LAB, "r")
    tot = sum(SHARES)
    xx = x0
    for j in range(4):
        ww = w * SHARES[j] / tot
        if j <= rev:
            rr(c, xx, y, ww - 4, h, 6)
            c.set_source_rgb(*HCOL[j])
            c.fill()
            txt(c, HSHORT[j], xx + ww / 2, y + h + 26, 22, HCOL[j], LAB, "c")
        else:
            rr(c, xx, y, ww - 4, h, 6)
            c.set_source_rgba(1, 1, 1, 0.10)
            c.fill()
        xx += ww


def plaque(c, n, title, t):
    k = e(t, 0, 0.45) * (1 - e(t, 3.3, 3.8))
    if k <= 0:
        return
    w = tw(c, title, 54, LAB) + 260
    x = 960 - w / 2
    y = 940 + (1 - k) * 160
    brass(c, x, y, w, 96, 14, 9)
    txt(c, "CHAPTER %d" % n, x + 46, y + 62, 34, BRASS, LAB, "l")
    txt(c, title, x + 250, y + 66, 54, AMBER, LAB, "l")


# ------------------------------------------------------------------ timeline / render
def build_timeline(L, durs):
    tl = []
    t = 0.12
    for i, ln in enumerate(L):
        d = durs[i] + GAP
        if ln["scene"] == "end":
            d += TAIL
        tl.append((t, d))
        t += d
    return tl, t


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
    draw_wall(c)
    sc = ln["scene"]
    new = i == 0 or L[i - 1]["scene"] != sc
    fade = e(t, 0, 0.22) if (new and i > 0) else 1.0
    p = dict(ln["p"])
    c.push_group()
    SC[sc](c, t, p, gt, d)
    c.pop_group_to_source()
    c.paint_with_alpha(fade)
    if sc not in ("hook", "end", "plain"):
        chrome(c, L, i, t)
    elif sc == "plain":
        chrome(c, L, i, t)
    else:
        if sc == "hook":
            logo(c, 46, 22, 0.55)
            txt(c, "MONEY MAP", 96, 60, 38, WHITE, LAB, "l")
    if "ch" in ln["p"]:
        import iou_content as C
        if ln["p"]["ch"] > 0:
            plaque(c, ln["p"]["ch"], C.CH[ln["p"]["ch"]], t)


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
    for f in range(a, b):
        draw(c, C.L, tl, f / FPS)
        surf.flush()
        pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    pr.wait()


def stills(mod, vodir, outdir, times):
    import importlib
    C = importlib.import_module(mod)
    durs = json.load(open(os.path.join(vodir, "durs.json")))
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
