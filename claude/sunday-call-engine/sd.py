import cairo, math, random

W, H, FPS = 1920, 1080, 30
FONT = "Rounded Mplus 1c ExtraBold"
FONTB = "Rounded Mplus 1c Bold"
FONTM = "Rounded Mplus 1c Medium"

ROSE = (0.812, 0.561, 0.525)
ROSE_D = (0.69, 0.43, 0.40)
CREAM = (0.973, 0.937, 0.871)
PAPER = (0.988, 0.965, 0.918)
PLUM = (0.435, 0.290, 0.478)
PLUM_D = (0.30, 0.19, 0.33)
INK = (0.13, 0.09, 0.12)
MINT = (0.549, 0.780, 0.659)
MINT_D = (0.38, 0.60, 0.49)
RED = (0.80, 0.16, 0.18)
WOOD = (0.55, 0.34, 0.22)
WOOD_D = (0.40, 0.24, 0.16)
TERRA = (0.56, 0.31, 0.23)
MUST = (0.88, 0.66, 0.27)
TEAL = (0.122, 0.239, 0.275)
TEAL_D = (0.07, 0.15, 0.18)
TEAL_L = (0.20, 0.36, 0.40)
GLOW = (0.55, 0.85, 0.95)
RUST = (0.722, 0.353, 0.180)
GRAN_SKIN = (0.42, 0.29, 0.20)
SON_SKIN = (0.29, 0.18, 0.12)
HAIR_G = (0.80, 0.78, 0.76)
HAIR_B = (0.06, 0.05, 0.05)
TEA = (0.62, 0.36, 0.16)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def e(t, a, b):
    return ease((t - a) / max(1e-6, b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def mix(p, q, k):
    return tuple(lerp(p[i], q[i], k) for i in range(3))


def rr(c, x, y, w, h, r):
    r = max(0.1, min(r, w / 2, h / 2))
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ell(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(max(rx, 0.01), max(ry, 0.01))
    c.new_sub_path()
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def fill(c, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.fill()


def text(c, s, x, y, size, col, a=1.0, align="c", font=FONT, outline=0.0):
    c.select_font_face(font)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.x_advance / 2
    elif align == "r":
        x -= ex.x_advance
    c.move_to(x, y)
    if outline > 0:
        c.text_path(s)
        c.set_source_rgba(0, 0, 0, 0.55 * a)
        c.set_line_width(outline)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgba(*col, a)
        c.fill()
    else:
        c.set_source_rgba(*col, a)
        c.show_text(s)
    c.new_path()
    return ex.x_advance


def glow(c, x, y, r, a, col=MUST):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g)
    c.rectangle(x - r, y - r, 2 * r, 2 * r)
    c.fill()


def vgrad(c, x, y, w, h, c0, c1):
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    c.set_source(g)
    c.rectangle(x, y, w, h)
    c.fill()


def caption(c, s, a, cx=W / 2, y=H - 78, size=74, maxw=1600):
    if a <= 0.01:
        return
    c.select_font_face(FONT)
    c.set_font_size(size)
    lines = [s]
    if c.text_extents(s).x_advance > maxw:
        wd = s.split()
        h = max(1, len(wd) // 2)
        lines = [" ".join(wd[:h]), " ".join(wd[h:])]
    for i, ln in enumerate(lines):
        yy = y + (i - (len(lines) - 1)) * size * 1.2
        ex = c.text_extents(ln)
        c.move_to(cx - ex.x_advance / 2, yy)
        c.text_path(ln)
        c.set_source_rgba(0, 0, 0, 0.66 * a)
        c.set_line_width(size * 0.18)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgba(*CREAM, a)
        c.fill()


# ------------------------------------------------------------ counter (red marker circle)
def marker_circle(c, cx, cy, rx, ry, k=1.0, lw=9, col=RED, a=1.0, seed=3):
    if k <= 0.001:
        return
    c.save()
    c.set_source_rgba(*col, a)
    c.set_line_width(lw)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    n = 60
    end = int(n * 1.12 * k)
    for i in range(end + 1):
        u = i / n
        ang = -2.2 + u * 2 * math.pi
        wob = 1 + 0.05 * math.sin(u * 7 + seed) + 0.04 * u
        x = cx + rx * wob * math.cos(ang)
        y = cy + ry * wob * math.sin(ang) - 6 * u
        if i == 0:
            c.move_to(x, y)
        else:
            c.line_to(x, y)
    c.stroke()
    c.restore()


def counter(c, n, label="SUNDAY · 6:00 PM", a=1.0, big=0.0, circ=1.0, pop=0.0):
    if a <= 0.01:
        return
    k = ease(big)
    x0, y0, s0 = 56, 44, 1.0
    x1, y1, s1 = 1010, 250, 2.05
    x, y, s = lerp(x0, x1, k), lerp(y0, y1, k), lerp(s0, s1, k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.22 * a)
    rr(c, 6, 9, 400, 160, 26)
    c.fill()
    c.set_source_rgba(*PAPER, 0.96 * a)
    rr(c, 0, 0, 400, 160, 26)
    c.fill()
    text(c, "MISSED", 28, 56, 34, PLUM_D, a, "l")
    text(c, "SUNDAYS", 28, 98, 34, PLUM_D, a, "l")
    c.set_source_rgba(*PLUM, 0.35 * a)
    c.rectangle(28, 116, 210, 3)
    c.fill()
    text(c, label, 28, 146, 22, PLUM, a, "l", FONTB)
    ps = 1 + 0.25 * math.sin(math.pi * clamp(pop))
    c.save()
    c.translate(318, 84)
    c.scale(ps, ps)
    text(c, str(n), 0, 34, 98, INK, a, "c")
    marker_circle(c, 0, 0, 58, 54, circ, 8, RED, a, seed=n)
    c.restore()
    c.restore()


# ------------------------------------------------------------ faces and figures
def face(c, skin, kind="gran", mood="calm", look=0.0, blink=1.0, mouth=0.0, tear=0.0, t=0.0, up=0.0):
    sd = mix(skin, INK, 0.3)
    lx = look * 14
    ly = -up * 8
    if kind == "gran":
        c.set_source_rgb(*HAIR_G)
        ell(c, -look * 20, -96, 40, 30)
        c.fill()
    c.set_source_rgb(*skin)
    ell(c, 0, 0, 62, 74)
    c.fill()
    c.set_source_rgb(*sd)
    ell(c, -61, 8, 9, 15)
    c.fill()
    ell(c, 61, 8, 9, 15)
    c.fill()
    if kind == "gran":
        c.set_source_rgb(*HAIR_G)
        c.new_path()
        c.move_to(-66, 10)
        c.curve_to(-74, -80, -32, -96, 0, -96)
        c.curve_to(32, -96, 74, -80, 66, 10)
        c.curve_to(58, -36, 28, -50, 0, -46)
        c.curve_to(-28, -50, -58, -36, -66, 10)
        c.close_path()
        c.fill()
        c.set_source_rgba(*mix(HAIR_G, INK, 0.25), 0.8)
        c.set_line_width(2.5)
        for i in range(-3, 4):
            c.move_to(i * 14, -90)
            c.curve_to(i * 18, -70, i * 22, -56, i * 26, -40)
            c.stroke()
        c.set_source_rgb(*MUST)
        for sg in (-1, 1):
            ell(c, sg * 64, 30, 5, 5)
            c.fill()
    else:
        c.set_source_rgb(*HAIR_B)
        c.new_path()
        c.move_to(-60, -20)
        c.curve_to(-64, -84, -30, -104, 0, -104)
        c.curve_to(30, -104, 64, -84, 60, -20)
        c.curve_to(52, -50, 30, -60, 0, -60)
        c.curve_to(-30, -60, -52, -50, -60, -20)
        c.close_path()
        c.fill()
        c.set_source_rgba(*mix(HAIR_B, skin, 0.35), 1)
        c.rectangle(-62, -34, 8, 30)
        c.rectangle(54, -34, 8, 30)
        c.fill()
    ey = 6 + ly
    for dx in (-23, 23):
        c.set_source_rgb(*CREAM)
        ell(c, dx + lx, ey, 11, 12 * blink)
        c.fill()
        c.set_source_rgb(*INK)
        ell(c, dx + lx + look * 4, ey + 1 + (2 if mood in ("sad", "worry") else 0) - up * 3, 6, 7 * blink)
        c.fill()
        if blink > 0.5:
            c.set_source_rgba(1, 1, 1, 0.85)
            ell(c, dx + lx + look * 4 + 2, ey - 2 - up * 3, 2.3, 2.3)
            c.fill()
        c.set_source_rgb(*(mix(HAIR_G, INK, 0.3) if kind == "gran" else HAIR_B))
        c.set_line_width(5.5)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        inner = 1 if dx < 0 else -1
        if mood in ("sad", "worry"):
            c.move_to(dx - 13 + lx, ey - 16 - (0 if inner > 0 else 6))
            c.line_to(dx + 13 + lx, ey - 16 - (6 if inner > 0 else 0))
        elif mood in ("joy", "surprise"):
            c.move_to(dx - 13 + lx, ey - 20 - (4 if mood == "surprise" else 0))
            c.line_to(dx + 13 + lx, ey - 22 - (4 if mood == "surprise" else 0))
        else:
            c.move_to(dx - 13 + lx, ey - 17)
            c.line_to(dx + 13 + lx, ey - 17)
        c.stroke()
    if kind == "gran":
        c.set_source_rgba(0.85, 0.70, 0.35, 1)
        c.set_line_width(3.5)
        for dx in (-23, 23):
            ell(c, dx + lx, ey, 19, 16)
            c.stroke()
        c.move_to(-4 + lx, ey)
        c.line_to(4 + lx, ey)
        c.stroke()
        c.set_source_rgba(*mix(skin, INK, 0.4), 0.6)
        c.set_line_width(2.5)
        for sg in (-1, 1):
            c.move_to(sg * 34 + lx, 40)
            c.curve_to(sg * 38 + lx, 50, sg * 34 + lx, 58, sg * 28 + lx, 62)
            c.stroke()
    if tear > 0 and blink > 0.5:
        c.set_source_rgba(0.75, 0.88, 1.0, 0.5 * tear)
        ell(c, -23 + lx, ey + 14, 10, 4)
        c.fill()
        ell(c, 23 + lx, ey + 14, 10, 4)
        c.fill()
    c.set_source_rgb(*mix(skin, INK, 0.35))
    ell(c, lx * 1.6, 28, 7, 5)
    c.fill()
    mx = lx * 1.3
    c.set_line_width(5)
    c.set_source_rgb(*mix(skin, INK, 0.6))
    if mouth > 0.05:
        c.set_source_rgb(0.28, 0.08, 0.10)
        ell(c, mx, 52, 13 + 7 * mouth, 5 + 12 * mouth)
        c.fill()
        if mood == "joy":
            c.set_source_rgb(*CREAM)
            c.rectangle(mx - 10 - 5 * mouth, 52 - 5 - 10 * mouth, 20 + 10 * mouth, 5)
            c.fill()
    elif mood in ("sad", "worry"):
        c.arc(mx, 60, 11, 1.2 * math.pi, 1.8 * math.pi)
        c.stroke()
    elif mood == "joy":
        c.arc(mx, 42, 18, 0.15 * math.pi, 0.85 * math.pi)
        c.stroke()
    elif mood == "soft":
        c.arc(mx, 44, 13, 0.25 * math.pi, 0.75 * math.pi)
        c.stroke()
    else:
        c.move_to(mx - 9, 51)
        c.line_to(mx + 9, 51)
        c.stroke()


def blink_at(t, off=0.0, per=4.4):
    return 0.12 if ((t + off) % per) < 0.12 else 1.0


def hand(c, x, y, skin, r=17):
    c.set_source_rgb(*skin)
    ell(c, x, y, r, r * 0.95)
    c.fill()


def receiver(c, x, y, s=1.0, ang=0.0, col=MINT):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.set_source_rgb(*mix(col, INK, 0.12))
    rr(c, -16, -70, 32, 140, 14)
    c.fill()
    c.set_source_rgb(*col)
    ell(c, 0, -76, 30, 22)
    c.fill()
    ell(c, 0, 76, 30, 22)
    c.fill()
    c.restore()


def gran(c, x, y, s=1.0, look=0.0, mood="calm", t=0.0, arms=None, seated=False, mouth=0.0, tear=0.0, up=0.0, k=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if not seated:
        c.set_source_rgb(*mix(SON_SKIN, GRAN_SKIN, 0.6))
        c.set_line_width(26)
        for sg in (-1, 1):
            c.move_to(sg * 22, -120)
            c.line_to(sg * 22, -24)
            c.stroke()
        c.set_source_rgb(*INK)
        for sg in (-1, 1):
            rr(c, sg * 22 - 22, -28, 46, 24, 10)
            c.fill()
        c.set_source_rgb(*PLUM_D)
        c.new_path()
        c.move_to(-70, -300)
        c.line_to(70, -300)
        c.line_to(92, -110)
        c.line_to(-92, -110)
        c.close_path()
        c.fill()
    c.set_source_rgb(*PLUM)
    rr(c, -82, -440, 164, 200 if seated else 230, 60)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-34, -442)
    c.line_to(0, -400)
    c.line_to(34, -442)
    c.close_path()
    c.fill()
    c.set_source_rgb(*mix(PLUM, INK, 0.3))
    c.set_line_width(4)
    c.move_to(0, -400)
    c.line_to(0, -230)
    c.stroke()
    for by in (-370, -320, -270):
        c.set_source_rgb(*CREAM)
        c.arc(8, by, 6, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgb(*PLUM)
    c.set_line_width(36)
    if arms == "phone":
        c.move_to(-70, -410)
        c.curve_to(-92, -330, -80, -270, -64, -240)
        c.stroke()
        hand(c, -64, -236, GRAN_SKIN)
        c.move_to(70, -410)
        c.curve_to(110, -470, 100, -520, 66, -530)
        c.stroke()
        receiver(c, 60, -540, 0.9, -0.35)
        hand(c, 62, -528, GRAN_SKIN, 18)
    elif arms == "cup":
        for sg in (-1, 1):
            c.move_to(sg * 70, -410)
            c.curve_to(sg * 96, -330, sg * 50, -280, sg * 22, -300)
            c.stroke()
        tea_cup(c, 0, -300, 0.8, steam=t)
        hand(c, -24, -296, GRAN_SKIN)
        hand(c, 24, -296, GRAN_SKIN)
    elif arms == "reach":
        c.move_to(-70, -410)
        c.curve_to(-92, -330, -80, -270, -64, -240)
        c.stroke()
        hand(c, -64, -236, GRAN_SKIN)
        rx = lerp(110, 190, k)
        ry = lerp(-330, -400, k)
        c.move_to(70, -410)
        c.curve_to(110, -400, rx - 30, ry + 10, rx, ry)
        c.stroke()
        hand(c, rx, ry, GRAN_SKIN)
    else:
        for sg in (-1, 1):
            c.move_to(sg * 70, -410)
            c.curve_to(sg * 92, -330, sg * 86, -270, sg * 74, -236)
            c.stroke()
            hand(c, sg * 74, -230, GRAN_SKIN)
    c.translate(0, -520)
    face(c, GRAN_SKIN, "gran", mood, look, blink_at(t), mouth, tear, t, up)
    c.restore()


def son(c, x, y, s=1.0, look=0.0, mood="calm", t=0.0, arms=None, seated=False, phones=False, mouth=0.0, up=0.0, k=0.0, lean=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(lean)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if not seated:
        c.set_source_rgb(0.12, 0.12, 0.14)
        c.set_line_width(42)
        for sg in (-1, 1):
            c.move_to(sg * 28, -170)
            c.line_to(sg * 28, -30)
            c.stroke()
        c.set_source_rgb(*CREAM)
        for sg in (-1, 1):
            rr(c, sg * 28 - 30, -36, 62, 30, 13)
            c.fill()
    c.set_source_rgb(*RUST)
    rr(c, -88, -450, 176, 310 if not seated else 260, 56)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-40, -452)
    c.line_to(0, -380)
    c.line_to(40, -452)
    c.close_path()
    c.fill()
    c.set_source_rgb(*mix(RUST, INK, 0.3))
    c.set_line_width(4)
    c.move_to(-30, -440)
    c.line_to(-14, -180)
    c.move_to(30, -440)
    c.line_to(14, -180)
    c.stroke()
    c.set_source_rgb(*RUST)
    c.set_line_width(40)
    if arms == "phone_ear":
        c.move_to(-78, -420)
        c.curve_to(-100, -340, -86, -270, -70, -230)
        c.stroke()
        hand(c, -70, -226, SON_SKIN)
        c.move_to(78, -420)
        c.curve_to(118, -480, 104, -530, 70, -540)
        c.stroke()
        c.set_source_rgb(0.08, 0.08, 0.1)
        c.save()
        c.translate(66, -548)
        c.rotate(-0.3)
        rr(c, -14, -44, 28, 88, 8)
        c.fill()
        c.restore()
        hand(c, 70, -536, SON_SKIN, 19)
    elif arms == "type":
        for sg in (-1, 1):
            c.move_to(sg * 78, -420)
            c.curve_to(sg * 100, -330, sg * 80, -260, sg * 40, -250)
            c.stroke()
            hand(c, sg * 40 + 6 * math.sin(t * 17 + sg), -248, SON_SKIN)
    elif arms == "hold":
        for sg in (-1, 1):
            c.move_to(sg * 78, -420)
            c.curve_to(sg * 100, -330, sg * 50, -280, sg * 18, -300)
            c.stroke()
        hand(c, -16, -296, SON_SKIN)
        hand(c, 16, -292, SON_SKIN)
    elif arms == "stretch":
        for sg in (-1, 1):
            c.move_to(sg * 78, -420)
            c.curve_to(sg * 130, -500, sg * 120, -600, sg * 80, -660)
            c.stroke()
            hand(c, sg * 80, -664, SON_SKIN)
    else:
        for sg in (-1, 1):
            c.move_to(sg * 78, -420)
            c.curve_to(sg * 100, -330, sg * 92, -260, sg * 80, -210)
            c.stroke()
            hand(c, sg * 80, -204, SON_SKIN)
    c.translate(0, -540)
    face(c, SON_SKIN, "son", mood, look, blink_at(t, 1.9, 4.9), mouth, 0.0, t, up)
    if phones:
        c.set_source_rgb(0.15, 0.15, 0.18)
        c.set_line_width(16)
        c.arc(0, -10, 84, math.pi * 1.05, math.pi * 1.95)
        c.stroke()
        for sg in (-1, 1):
            rr(c, sg * 70 - 18, -20, 36, 62, 14)
            c.fill()
    c.restore()


# ------------------------------------------------------------ props
def tea_cup(c, x, y, s=1.0, col=CREAM, steam=None, full=1.0, band=MINT):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgb(*mix(col, INK, 0.1))
    ell(c, 0, 4, 58, 10)
    c.fill()
    c.set_source_rgb(*col)
    c.new_path()
    c.move_to(-40, -50)
    c.curve_to(-40, -8, -24, 0, 0, 0)
    c.curve_to(24, 0, 40, -8, 40, -50)
    c.close_path()
    c.fill()
    c.set_source_rgb(*band)
    c.rectangle(-38, -40, 76, 8)
    c.fill()
    c.set_line_width(8)
    c.set_source_rgb(*col)
    c.arc(44, -30, 13, -math.pi / 2, math.pi / 2)
    c.stroke()
    c.set_source_rgb(*mix(col, INK, 0.2))
    ell(c, 0, -50, 40, 8)
    c.fill()
    if full > 0.02:
        c.set_source_rgb(*TEA)
        ell(c, 0, -50 + 6 * (1 - full), 35 * (0.6 + 0.4 * full), 6)
        c.fill()
    if steam is not None and full > 0.5:
        for j in range(3):
            c.set_source_rgba(1, 1, 1, 0.28)
            c.set_line_width(5)
            c.move_to(-14 + j * 14, -62)
            c.curve_to(-22 + j * 14, -84 - 6 * math.sin(steam * 2 + j), -4 + j * 14, -100, -14 + j * 14, -122 - 6 * math.sin(steam * 2 + j))
            c.stroke()
    c.restore()


def teapot(c, x, y, s=1.0, tilt=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(tilt)
    c.set_source_rgb(*MINT)
    ell(c, 0, -60, 82, 62)
    c.fill()
    c.set_source_rgb(*MINT_D)
    c.rectangle(-60, -82, 120, 10)
    c.fill()
    c.set_source_rgb(*MINT)
    c.set_line_width(14)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(70, -60)
    c.curve_to(110, -70, 120, -100, 130, -120)
    c.stroke()
    c.arc(-86, -60, 30, math.pi * 0.5, math.pi * 1.5)
    c.stroke()
    ell(c, 0, -122, 34, 10)
    c.fill()
    c.set_source_rgb(*MINT_D)
    ell(c, 0, -134, 10, 8)
    c.fill()
    c.restore()


def wall_clock(c, x, y, r, hh, mm, sec=None, face_col=PAPER, rim=WOOD_D):
    c.set_source_rgb(*rim)
    c.arc(x, y, r + 10, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*face_col)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    for i in range(12):
        a = i * math.pi / 6
        c.set_line_width(5 if i % 3 == 0 else 2.5)
        c.move_to(x + (r - 6) * math.sin(a), y - (r - 6) * math.cos(a))
        c.line_to(x + (r - 16) * math.sin(a), y - (r - 16) * math.cos(a))
        c.stroke()
    ah = (hh % 12 + mm / 60) * math.pi / 6
    am = mm * math.pi / 30
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(7)
    c.move_to(x, y)
    c.line_to(x + r * 0.5 * math.sin(ah), y - r * 0.5 * math.cos(ah))
    c.stroke()
    c.set_line_width(5)
    c.move_to(x, y)
    c.line_to(x + r * 0.78 * math.sin(am), y - r * 0.78 * math.cos(am))
    c.stroke()
    if sec is not None:
        a = sec * math.pi / 30
        c.set_source_rgb(*RED)
        c.set_line_width(2.5)
        c.move_to(x, y)
        c.line_to(x + r * 0.85 * math.sin(a), y - r * 0.85 * math.cos(a))
        c.stroke()
    c.set_source_rgb(*INK)
    c.arc(x, y, 6, 0, 2 * math.pi)
    c.fill()


def smartphone(c, x, y, s=1.0, state="down", buzz=0.0, ang=0.0, t=0.0, lock=("SUN", "6:00"), note=None, flip=1.0, lit=1.0):
    jx = 5 * math.sin(t * 90) * buzz
    c.save()
    c.translate(x + jx, y)
    c.rotate(ang + 0.02 * math.sin(t * 70) * buzz)
    c.scale(s * flip, s)
    pw, ph = 300, 600
    if state == "down" or flip < 0:
        if buzz > 0:
            glow(c, 0, 0, 420, 0.30 * buzz, GLOW)
        c.set_source_rgba(0, 0, 0, 0.35)
        rr(c, -pw / 2 + 10, -ph / 2 + 14, pw, ph, 44)
        c.fill()
        c.set_source_rgb(0.16, 0.19, 0.26)
        rr(c, -pw / 2, -ph / 2, pw, ph, 44)
        c.fill()
        c.set_source_rgb(0.10, 0.12, 0.17)
        rr(c, -pw / 2 + 24, -ph / 2 + 24, 110, 130, 26)
        c.fill()
        for (cx, cy) in ((-pw / 2 + 56, -ph / 2 + 60), (-pw / 2 + 102, -ph / 2 + 60), (-pw / 2 + 56, -ph / 2 + 118)):
            c.set_source_rgb(0.05, 0.05, 0.08)
            c.arc(cx, cy, 18, 0, 2 * math.pi)
            c.fill()
        c.restore()
        return
    c.set_source_rgba(0, 0, 0, 0.35)
    rr(c, -pw / 2 + 10, -ph / 2 + 14, pw, ph, 44)
    c.fill()
    c.set_source_rgb(0.04, 0.04, 0.06)
    rr(c, -pw / 2, -ph / 2, pw, ph, 44)
    c.fill()
    top = mix((0.10, 0.12, 0.20), (0.18, 0.30, 0.42), lit)
    bot = mix((0.05, 0.06, 0.10), (0.10, 0.16, 0.26), lit)
    vgrad(c, -pw / 2 + 12, -ph / 2 + 12, pw - 24, ph - 24, top, bot)
    c.set_source_rgb(0.04, 0.04, 0.06)
    rr(c, -40, -ph / 2 + 22, 80, 18, 9)
    c.fill()
    if lit < 0.05:
        c.restore()
        return
    a = lit
    if state == "incoming":
        text(c, "SUNDAY 6:00 PM", 0, -ph / 2 + 96, 22, (0.75, 0.82, 0.95), a, "c", FONTB)
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        c.set_source_rgba(*GLOW, (0.15 + 0.12 * pulse) * a)
        c.arc(0, -92, 66 + 12 * pulse, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*ROSE, a)
        c.arc(0, -92, 54, 0, 2 * math.pi)
        c.fill()
        text(c, "G", 0, -70, 64, CREAM, a, "c")
        text(c, "GRANDMA", 0, 26, 50, CREAM, a, "c")
        text(c, "calling...", 0, 66, 26, (0.75, 0.82, 0.95), a * 0.9, "c", FONTM)
        for sg, col, lab in ((-1, (0.88, 0.27, 0.28), "Decline"), (1, (0.30, 0.78, 0.45), "Accept")):
            c.set_source_rgba(*col, a)
            c.arc(sg * 72, 190, 40, 0, 2 * math.pi)
            c.fill()
            text(c, lab, sg * 72, 256, 20, CREAM, a * 0.9, "c", FONTM)
    elif state == "missed":
        text(c, lock[1], 0, -150, 92, CREAM, a, "c", FONTM)
        text(c, lock[0], 0, -100, 26, (0.75, 0.82, 0.95), a, "c", FONTB)
        if note:
            c.set_source_rgba(1, 1, 1, 0.16 * a)
            rr(c, -128, -40, 256, 110, 20)
            c.fill()
            text(c, note[0], -110, -6, 20, (0.85, 0.88, 0.95), a, "l", FONTB)
            text(c, note[1], -110, 32, 30, CREAM, a, "l", FONT)
            if len(note) > 2:
                text(c, note[2], -110, 58, 18, (0.75, 0.80, 0.92), a, "l", FONTM)
    elif state == "talk":
        text(c, "GRANDMA", 0, -120, 44, CREAM, a, "c")
        text(c, "0:%02d" % (int(t) % 60), 0, -70, 28, (0.6, 0.95, 0.7), a, "c", FONTM)
        c.set_source_rgba(*ROSE, a)
        c.arc(0, 40, 60, 0, 2 * math.pi)
        c.fill()
        text(c, "G", 0, 64, 70, CREAM, a, "c")
    c.restore()


# ------------------------------------------------------------ sets: her kitchen
random.seed(7)
DOTS = [(random.random() * W, random.random() * 640) for _ in range(160)]


def kitchen_bg(c, t, dusk=0.0, photo_tilt=0.0, clock=(5, 59, 40), cal=0):
    vgrad(c, 0, 0, W, 700, mix(ROSE, ROSE_D, 0.2 * dusk), mix(ROSE_D, (0.45, 0.28, 0.30), 0.5 * dusk))
    for (x, y) in DOTS:
        c.set_source_rgba(*CREAM, 0.16)
        c.arc(x, y, 4, 0, 2 * math.pi)
        c.fill()
    vgrad(c, 0, 640, W, 160, (0.93, 0.86, 0.76), (0.86, 0.78, 0.68))
    c.set_source_rgb(*WOOD_D)
    c.rectangle(0, 632, W, 14)
    c.fill()
    vgrad(c, 0, 800, W, 280, TERRA, mix(TERRA, INK, 0.3))
    c.set_source_rgba(0, 0, 0, 0.12)
    for i in range(12):
        c.rectangle(i * 170, 800, 4, 280)
        c.fill()
    c.rectangle(0, 900, W, 3)
    c.fill()
    c.set_source_rgb(*mix(CREAM, WOOD, 0.3))
    rr(c, 96, 156, 448, 428, 10)
    c.fill()
    vgrad(c, 120, 180, 400, 380, mix((0.98, 0.66, 0.40), (0.35, 0.28, 0.45), dusk), mix((0.90, 0.48, 0.48), (0.20, 0.17, 0.32), dusk))
    sy = lerp(470, 600, dusk)
    c.save()
    c.rectangle(120, 180, 400, 380)
    c.clip()
    c.set_source_rgba(1.0, 0.85, 0.55, 1 - 0.6 * dusk)
    c.arc(390, sy, 46, 0, 2 * math.pi)
    c.fill()
    glow(c, 390, sy, 200, 0.35 * (1 - dusk), (1.0, 0.8, 0.5))
    c.set_source_rgb(*mix((0.45, 0.30, 0.38), INK, 0.3 + 0.3 * dusk))
    for i, (bx, bw, bh) in enumerate(((120, 70, 120), (190, 60, 80), (250, 90, 150), (340, 70, 100), (410, 110, 130))):
        c.rectangle(bx, 560 - bh, bw, bh)
        c.fill()
    c.restore()
    c.set_source_rgb(*mix(CREAM, WOOD, 0.3))
    c.rectangle(316, 180, 8, 380)
    c.rectangle(120, 366, 400, 8)
    c.fill()
    c.set_source_rgb(*MUST)
    for sx in (70, 500):
        c.new_path()
        c.move_to(sx, 140)
        c.line_to(sx + 70, 140)
        c.curve_to(sx + 60, 300, sx + 40, 420, sx + 70, 600)
        c.line_to(sx, 600)
        c.close_path()
        c.fill()
    c.rectangle(60, 128, 520, 18)
    c.fill()
    wall_clock(c, 1000, 210, 72, clock[0], clock[1], clock[2])
    c.save()
    c.translate(760, 300)
    c.rotate(photo_tilt)
    c.set_source_rgb(*WOOD_D)
    rr(c, -82, -100, 164, 200, 6)
    c.fill()
    c.set_source_rgb(0.78, 0.84, 0.88)
    c.rectangle(-66, -84, 132, 168)
    c.fill()
    c.save()
    c.rectangle(-66, -84, 132, 168)
    c.clip()
    c.translate(0, 120)
    c.scale(0.3, 0.3)
    son(c, 0, 0, 1.0, 0.0, "joy", 0.0)
    c.set_source_rgb(0.10, 0.10, 0.14)
    c.new_path()
    c.move_to(-110, -650)
    c.line_to(0, -700)
    c.line_to(110, -650)
    c.line_to(0, -610)
    c.close_path()
    c.fill()
    c.restore()
    c.restore()
    calendar_small(c, 1640, 360, cal)
    wall_phone(c, 1340, 430, t)


def calendar_small(c, x, y, n=0):
    c.set_source_rgb(*WOOD_D)
    c.rectangle(x - 4, y - 160, 8, 12)
    c.fill()
    c.set_source_rgb(*PAPER)
    rr(c, x - 110, y - 150, 220, 290, 6)
    c.fill()
    c.set_source_rgb(*RED)
    c.rectangle(x - 110, y - 150, 220, 46)
    c.fill()
    text(c, "SUNDAYS", x, y - 116, 26, CREAM, 1.0, "c")
    for r in range(5):
        for k in range(7):
            cx = x - 90 + k * 30
            cy = y - 70 + r * 40
            c.set_source_rgba(*INK, 0.35)
            c.rectangle(cx - 6, cy - 4, 12, 8)
            c.fill()
        if r < 5:
            marker_circle(c, x + 90, y - 70 + r * 40, 14, 13, 1.0, 3.5, RED, 0.9, seed=r)


def wall_phone(c, x, y, t, off_hook=False, cord_to=None):
    c.set_source_rgba(0, 0, 0, 0.18)
    rr(c, x - 64, y - 116, 140, 250, 22)
    c.fill()
    c.set_source_rgb(*MINT)
    rr(c, x - 70, y - 124, 140, 250, 22)
    c.fill()
    c.set_source_rgb(*MINT_D)
    rr(c, x - 40, y - 20, 80, 110, 10)
    c.fill()
    for r in range(4):
        for k in range(3):
            c.set_source_rgb(*CREAM)
            rr(c, x - 32 + k * 24, y - 12 + r * 26, 18, 18, 5)
            c.fill()
    if not off_hook:
        receiver(c, x, y - 62, 0.85, math.pi / 2, MINT)
        c.set_source_rgb(*mix(MINT, INK, 0.2))
        c.set_line_width(5)
        for i in range(16):
            yy = y + 130 + i * 12
            c.arc(x - 60, yy, 9, 0, 2 * math.pi)
            c.stroke()
    elif cord_to is not None:
        c.set_source_rgb(*mix(MINT, INK, 0.2))
        c.set_line_width(5)
        x0, y0 = x - 60, y + 120
        x1, y1 = cord_to
        for i in range(28):
            u = i / 27
            px = lerp(x0, x1, u) + 12 * math.cos(u * 60)
            py = lerp(y0, y1, u) + 60 * math.sin(math.pi * u) + 12 * math.sin(u * 60)
            if i == 0:
                c.move_to(px, py)
            else:
                c.line_to(px, py)
        c.stroke()


def kitchen_table(c, cups=1, cup2_k=1.0, pot=True, t=0.0, fill2=0.0, x0=560):
    c.set_source_rgb(*WOOD)
    ell(c, x0 + 340, 820, 400, 60)
    c.fill()
    c.set_source_rgb(*WOOD_D)
    c.rectangle(x0 + 320, 840, 40, 220)
    c.fill()
    c.set_source_rgb(*CREAM)
    ell(c, x0 + 340, 812, 300, 40)
    c.fill()
    tea_cup(c, x0 + 220, 820, 0.95, steam=t)
    if cups > 1 and cup2_k > 0.01:
        c.save()
        c.translate(0, 0)
        tea_cup(c, lerp(x0 + 700, x0 + 470, cup2_k), 820, 0.95, col=(0.98, 0.90, 0.80), full=fill2, band=RED, steam=t if fill2 > 0.6 else None)
        c.restore()
    if pot:
        teapot(c, x0 + 340, 790, 0.8)


def kitchen(c, t, who=None, dusk=0.0, cups=1, cup2_k=1.0, clock=(5, 59, 40), photo_tilt=0.0, gk=0.0, mood="calm", fill2=0.0):
    kitchen_bg(c, t, dusk, photo_tilt, clock)
    if who == "phone":
        wall_phone(c, 1340, 430, t, True, (1220, 470))
        gran(c, 1200, 1010, 0.92, look=-0.2, mood=mood, t=t, arms="phone")
        kitchen_table(c, cups, cup2_k, True, t, fill2, x0=200)
    elif who == "sit":
        kitchen_table(c, cups, cup2_k, True, t, fill2)
        gran(c, 700, 1040, 0.9, look=0.6, mood=mood, t=t, seated=True)
        c.set_source_rgb(*WOOD)
        ell(c, 900, 820, 400, 60)
        c.fill()
        c.set_source_rgb(*CREAM)
        ell(c, 900, 812, 300, 40)
        c.fill()
        tea_cup(c, 780, 820, 0.95, steam=t)
        if cups > 1 and cup2_k > 0.01:
            tea_cup(c, lerp(1260, 1030, cup2_k), 820, 0.95, col=(0.98, 0.90, 0.80), full=fill2, band=RED, steam=t if fill2 > 0.6 else None)
        teapot(c, 900, 790, 0.8)
    elif who == "stand":
        kitchen_table(c, cups, cup2_k, True, t, fill2)
        gran(c, lerp(1500, 1160, gk), 1030, 0.92, look=-0.5, mood=mood, t=t)
    else:
        kitchen_table(c, cups, cup2_k, True, t, fill2)


# ------------------------------------------------------------ sets: his apartment (teal city night)
random.seed(19)
WINS = [(random.random(), random.random(), random.random()) for _ in range(90)]


def city_window(c, x, y, w, h, t, a=1.0):
    vgrad(c, x, y, w, h, (0.08, 0.12, 0.22), (0.22, 0.20, 0.36))
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    for i in range(9):
        bx = x + i * w / 8 - 30
        bh = h * (0.35 + 0.5 * ((i * 37) % 10) / 10)
        c.set_source_rgb(0.06, 0.09, 0.15)
        c.rectangle(bx, y + h - bh, w / 9 + 10, bh)
        c.fill()
    for (fx, fy, ph) in WINS:
        on = math.sin(t * 0.4 + ph * 20) > -0.3
        if on:
            c.set_source_rgba(1.0, 0.82, 0.45, 0.75)
            c.rectangle(x + fx * w, y + h * 0.35 + fy * h * 0.6, 7, 9)
            c.fill()
    c.restore()
    c.set_source_rgb(*TEAL_D)
    c.set_line_width(14)
    c.rectangle(x, y, w, h)
    c.stroke()
    c.rectangle(x + w / 2 - 5, y, 10, h)
    c.fill()


def apt_bg(c, t, lamp=1.0):
    vgrad(c, 0, 0, W, 760, TEAL_L, TEAL)
    c.set_source_rgba(1, 1, 1, 0.03)
    for i in range(0, W, 90):
        c.rectangle(i, 0, 3, 760)
        c.fill()
    vgrad(c, 0, 760, W, 320, (0.15, 0.20, 0.22), (0.08, 0.11, 0.12))
    city_window(c, 1180, 120, 560, 470, t)
    glow(c, 420, 300, 600, 0.22 * lamp, MUST)
    c.set_source_rgb(*TEAL_D)
    c.rectangle(398, 300, 8, 460)
    c.fill()
    c.set_source_rgb(*MUST)
    c.new_path()
    c.move_to(340, 300)
    c.line_to(464, 300)
    c.line_to(440, 220)
    c.line_to(364, 220)
    c.close_path()
    c.fill()


def couch(c, x=960, y=900, col=(0.34, 0.40, 0.46)):
    c.set_source_rgb(*mix(col, INK, 0.2))
    rr(c, x - 460, y - 330, 920, 220, 50)
    c.fill()
    c.set_source_rgb(*col)
    rr(c, x - 500, y - 160, 1000, 170, 40)
    c.fill()
    rr(c, x - 540, y - 260, 110, 280, 40)
    c.fill()
    rr(c, x + 430, y - 260, 110, 280, 40)
    c.fill()


def coffee_table(c, x=960, y=1010, w=760):
    c.set_source_rgb(*WOOD)
    rr(c, x - w / 2, y - 40, w, 34, 10)
    c.fill()
    c.set_source_rgb(*WOOD_D)
    c.rectangle(x - w / 2 + 30, y - 6, 22, 100)
    c.rectangle(x + w / 2 - 52, y - 6, 22, 100)
    c.fill()


def laptop(c, x, y, s=1.0, t=0.0, kind="code", a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgb(0.55, 0.58, 0.62)
    rr(c, -170, -230, 340, 220, 10)
    c.fill()
    vgrad(c, -158, -218, 316, 196, (0.12, 0.22, 0.30), (0.08, 0.14, 0.22))
    if kind == "code":
        for i in range(8):
            c.set_source_rgba(*[GLOW, MUST, CREAM][i % 3], 0.7)
            ww = 60 + ((i * 53 + int(t * 3)) % 160)
            c.rectangle(-140 + (i % 3) * 14, -200 + i * 22, ww, 8)
            c.fill()
    elif kind == "call":
        for r in range(2):
            for k in range(3):
                c.set_source_rgb(*[(0.40, 0.48, 0.58), (0.50, 0.42, 0.52), (0.36, 0.50, 0.46)][(r + k) % 3])
                rr(c, -150 + k * 102, -210 + r * 92, 96, 86, 6)
                c.fill()
                c.set_source_rgb(*mix(SON_SKIN, CREAM, 0.15 * ((r * 3 + k) % 4)))
                ell(c, -102 + k * 102, -176 + r * 92, 16, 18)
                c.fill()
                ell(c, -102 + k * 102, -138 + r * 92, 26, 16)
                c.fill()
    elif kind == "movie":
        c.set_source_rgba(*GLOW, 0.3 + 0.2 * math.sin(t * 3))
        c.rectangle(-158, -218, 316, 196)
        c.fill()
    c.set_source_rgb(0.62, 0.65, 0.70)
    c.new_path()
    c.move_to(-200, 0)
    c.line_to(200, 0)
    c.line_to(176, -12)
    c.line_to(-176, -12)
    c.close_path()
    c.fill()
    c.restore()
    glow(c, x, y - 120 * s, 380 * s, 0.22 * a, GLOW)


def takeaway(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-50, -90)
    c.line_to(50, -90)
    c.line_to(40, 0)
    c.line_to(-40, 0)
    c.close_path()
    c.fill()
    c.set_source_rgb(*RED)
    c.rectangle(-46, -64, 92, 12)
    c.fill()
    c.set_source_rgb(*INK)
    c.set_line_width(4)
    c.arc(0, -90, 34, math.pi, 2 * math.pi)
    c.stroke()
    c.restore()


def desk_front(c, y=760, x0=300, x1=1620):
    c.set_source_rgb(*WOOD)
    rr(c, x0, y, x1 - x0, 40, 10)
    c.fill()
    vgrad(c, x0 + 20, y + 40, x1 - x0 - 40, H - y, WOOD_D, mix(WOOD_D, INK, 0.5))


def apt(c, t, mode="couch", buzz=0.0, phone_state="down", look=0.0, mood="calm", lit=1.0, phone_at=None, arms=None, up=0.0, mouth=0.0):
    apt_bg(c, t)
    if mode in ("desk", "call"):
        son(c, 760, 1090, 1.0, look=look, mood=mood, t=t, arms=arms or "type", seated=True, phones=(mode == "desk"), up=up, mouth=mouth)
        desk_front(c)
        laptop(c, 1120, 760, 0.95, t, "code" if mode == "desk" else "call")
        st = "incoming" if (buzz > 0 and phone_state != "down" and mode == "desk") else phone_state
        smartphone(c, 520, 730, 0.22, st, buzz, -1.5, t, lit=lit)
    elif mode == "couch":
        couch(c)
        son(c, 880, 1060, 0.95, look=look, mood=mood, t=t, arms=arms, seated=True, up=up, mouth=mouth)
        coffee_table(c)
        px, py, pa = phone_at or (1160, 960, -1.5)
        smartphone(c, px, py, 0.2, phone_state, buzz, pa, t, lit=lit)
        takeaway(c, 700, 970, 0.9)
    elif mode == "sleep":
        couch(c)
        c.save()
        c.translate(960, 760)
        c.rotate(-1.35)
        son(c, 0, 400, 0.9, look=0, mood="calm", t=0.0, seated=True)
        c.restore()
        c.set_source_rgb(*SON_SKIN)
        c.set_source_rgba(0.05, 0.08, 0.1, 0.0)
        coffee_table(c)
        laptop(c, 1180, 970, 0.6, t, "movie")
        smartphone(c, 760, 1050, 0.2, "down", buzz, 0.2, t)
    elif mode == "table":
        son(c, 960, 1180, 1.0, look=look, mood=mood, t=t, arms=arms or "hold", seated=True, up=up, mouth=mouth)
        c.set_source_rgb(*WOOD)
        rr(c, 300, 820, 1320, 40, 10)
        c.fill()
        c.set_source_rgb(*WOOD_D)
        c.rectangle(340, 860, 30, 220)
        c.rectangle(1550, 860, 30, 220)
        c.fill()
        px, py, pa = phone_at or (960, 800, -1.57)
        smartphone(c, px, py, 0.24, phone_state, buzz, pa, t, lit=lit)
    # dim light for night
    c.set_source_rgba(0.02, 0.05, 0.08, 0.18)
    c.rectangle(0, 0, W, H)
    c.fill()


def office(c, t, look=0.0, mood="calm"):
    vgrad(c, 0, 0, W, 760, (0.86, 0.88, 0.86), (0.76, 0.80, 0.80))
    for i in range(5):
        c.set_source_rgb(0.68, 0.74, 0.76)
        rr(c, 80 + i * 380, 120, 300, 300, 8)
        c.fill()
        vgrad(c, 96 + i * 380, 136, 268, 268, (0.70, 0.84, 0.95), (0.86, 0.92, 0.98))
    c.set_source_rgb(0.62, 0.66, 0.66)
    c.rectangle(0, 760, W, 320)
    c.fill()
    for i, x in enumerate((200, 1700)):
        c.set_source_rgb(*[(0.45, 0.52, 0.60), (0.55, 0.45, 0.42)][i])
        ell(c, x, 560, 44, 50)
        c.fill()
        rr(c, x - 70, 610, 140, 160, 40)
        c.fill()
        c.set_source_rgb(0.4, 0.42, 0.45)
        rr(c, x - 100, 600, 200, 130, 8)
        c.fill()
    son(c, 1180, 1090, 1.0, look=look, mood=mood, t=t, arms="type", seated=True)
    c.set_source_rgb(0.92, 0.92, 0.90)
    rr(c, 300, 760, 1320, 40, 8)
    c.fill()
    vgrad(c, 320, 800, 1280, 280, (0.70, 0.72, 0.72), (0.55, 0.58, 0.58))
    c.set_source_rgb(0.2, 0.22, 0.25)
    rr(c, 420, 400, 520, 330, 12)
    c.fill()
    vgrad(c, 436, 416, 488, 298, (0.95, 0.96, 0.98), (0.88, 0.90, 0.95))
    for i in range(7):
        c.set_source_rgb(*[(0.3, 0.5, 0.8), (0.9, 0.6, 0.3), (0.4, 0.7, 0.5)][i % 3])
        c.rectangle(470, 450 + i * 36, 80 + (i * 61) % 260, 14)
        c.fill()
    c.set_source_rgb(0.2, 0.22, 0.25)
    c.rectangle(660, 730, 40, 34)
    c.fill()
    tea_cup(c, 1480, 770, 0.6, col=(0.95, 0.95, 0.95), band=(0.3, 0.5, 0.8))


def train(c, t, look=0.0, mood="calm", glance=0.0):
    vgrad(c, 0, 0, W, H, (0.30, 0.34, 0.38), (0.20, 0.23, 0.26))
    for wx in (80, 1080):
        c.set_source_rgb(0.12, 0.13, 0.16)
        rr(c, wx, 160, 760, 420, 30)
        c.fill()
        c.save()
        rr(c, wx + 12, 172, 736, 396, 24)
        c.clip()
        vgrad(c, wx, 160, 760, 420, (0.06, 0.08, 0.16), (0.16, 0.12, 0.26))
        for i in range(14):
            xx = wx + ((i * 173 - t * 900) % 1000) - 120
            c.set_source_rgba(1.0, 0.8, 0.45, 0.85)
            c.set_line_width(6)
            c.move_to(xx, 300 + (i * 47) % 200)
            c.line_to(xx + 140, 300 + (i * 47) % 200)
            c.stroke()
        c.restore()
    c.set_source_rgb(0.75, 0.76, 0.78)
    c.rectangle(0, 110, W, 14)
    c.fill()
    c.set_line_width(10)
    for x in range(200, W, 260):
        c.move_to(x, 124)
        c.line_to(x, 190)
        c.stroke()
        c.arc(x, 214, 24, 0, 2 * math.pi)
        c.stroke()
    c.set_source_rgb(0.36, 0.40, 0.44)
    c.rectangle(0, 860, W, 220)
    c.fill()
    son(c, 960, 1200, 1.08, look=look, mood=mood, t=t, arms="hold", up=glance)
    smartphone(c, 960, 860, 0.28, "missed" if glance > 0.5 else "down", 0, 0.0, t, lock=("WEDNESDAY", "8:40"), note=("MISSED CALL", "GRANDMA", "Sunday 6:00 PM"), flip=1.0 if glance > 0.5 else -1.0)


def card(c, s, a=1.0, sub=None):
    vgrad(c, 0, 0, W, H, (0.36, 0.22, 0.27), (0.20, 0.12, 0.17))
    for (x, y) in DOTS[:80]:
        c.set_source_rgba(*CREAM, 0.06)
        c.arc(x, y * 1.6, 4, 0, 2 * math.pi)
        c.fill()
    text(c, s, W / 2, H / 2 + 30, 104, CREAM, a)
    if sub:
        text(c, sub, W / 2, H / 2 + 130, 52, MUST, a)


def table_close(c, t, state="down", buzz=0.0, flip=1.0, lit=1.0, hand_k=0.0, lock=("SUN", "6:00"), note=None, py=540):
    vgrad(c, 0, 0, W, H, (0.42, 0.27, 0.18), (0.28, 0.17, 0.11))
    c.set_source_rgba(0, 0, 0, 0.10)
    c.set_line_width(3)
    for i in range(18):
        y = 40 + i * 60
        c.move_to(0, y)
        c.curve_to(600, y + 20 * math.sin(i), 1200, y - 18 * math.cos(i), W, y + 10)
        c.stroke()
    glow(c, 640, 540, 700, 0.08, GLOW)
    tea_cup(c, 1530, 900, 1.3, col=(0.95, 0.95, 0.95), band=TEAL, full=0.3)
    smartphone(c, 640, py, 1.12, state, buzz, -0.08, t, lock, note, flip, lit)
    if hand_k > 0.001:
        hx = lerp(1100, 860, ease(hand_k))
        c.save()
        c.translate(hx, py + 160)
        c.set_source_rgb(*RUST)
        c.set_line_width(150)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(700, 500)
        c.line_to(90, 60)
        c.stroke()
        c.set_source_rgb(*SON_SKIN)
        rr(c, -110, -70, 220, 150, 60)
        c.fill()
        c.restore()
    c.set_source_rgba(0, 0, 0, 0.25)
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1200)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    c.set_source(g)
    c.paint()


def son_close(c, t, mood="worry", look=0.6, glow_a=0.6, up=0.0, mouth=0.0, phone=False, bg="night"):
    if bg == "night":
        vgrad(c, 0, 0, W, H, TEAL, TEAL_D)
        city_window(c, 1220, 80, 620, 520, t)
    else:
        vgrad(c, 0, 0, W, H, (0.36, 0.30, 0.28), (0.20, 0.16, 0.15))
    c.save()
    c.translate(780, 560)
    c.scale(3.0, 3.0)
    c.set_source_rgb(*RUST)
    c.new_path()
    c.move_to(-170, 340)
    c.curve_to(-150, 140, -100, 92, -60, 82)
    c.line_to(60, 82)
    c.curve_to(100, 92, 150, 140, 170, 340)
    c.close_path()
    c.fill()
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-34, 80)
    c.line_to(0, 130)
    c.line_to(34, 80)
    c.close_path()
    c.fill()
    face(c, SON_SKIN, "son", mood, look, blink_at(t, 0.7, 4.0), mouth, 0.0, t, up)
    if phone:
        c.set_source_rgb(*RUST)
        c.set_line_width(40)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(110, 200)
        c.curve_to(120, 140, 100, 60, 72, 30)
        c.stroke()
        c.set_source_rgb(0.08, 0.08, 0.1)
        c.save()
        c.translate(70, 6)
        c.rotate(-0.25)
        rr(c, -14, -46, 28, 92, 8)
        c.fill()
        c.restore()
        hand(c, 74, 30, SON_SKIN, 18)
    c.restore()
    if glow_a > 0:
        glow(c, 900, 1100, 700, 0.35 * glow_a, GLOW)


def gran_close(c, t, mood="calm", look=-0.3, tear=0.0, up=0.0, mouth=0.0, ring=0.0, dusk=0.3):
    vgrad(c, 0, 0, W, H, mix(ROSE, ROSE_D, 0.3 + 0.4 * dusk), mix(ROSE_D, (0.40, 0.25, 0.28), 0.4 + 0.4 * dusk))
    for (x, y) in DOTS:
        c.set_source_rgba(*CREAM, 0.12)
        c.arc(x, y * 1.6, 4, 0, 2 * math.pi)
        c.fill()
    glow(c, 300, 300, 700, 0.25 * (1 - dusk), (1.0, 0.75, 0.45))
    c.save()
    c.translate(900, 560)
    c.scale(3.0, 3.0)
    c.set_source_rgb(*PLUM)
    c.new_path()
    c.move_to(-160, 340)
    c.curve_to(-140, 140, -96, 92, -58, 82)
    c.line_to(58, 82)
    c.curve_to(96, 92, 140, 140, 160, 340)
    c.close_path()
    c.fill()
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-32, 80)
    c.line_to(0, 120)
    c.line_to(32, 80)
    c.close_path()
    c.fill()
    face(c, GRAN_SKIN, "gran", mood, look, blink_at(t, 0.2, 4.6), mouth, tear, t, up)
    c.set_source_rgb(*PLUM)
    c.set_line_width(40)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-120, 220)
    c.curve_to(-130, 150, -110, 70, -84, 40)
    c.stroke()
    receiver(c, -86, 6, 0.7, 0.32)
    hand(c, -86, 34, GRAN_SKIN, 18)
    c.restore()
    if ring > 0:
        for i in range(3):
            k = ((t * 0.8 + i / 3) % 1)
            c.set_source_rgba(*CREAM, 0.35 * (1 - k) * ring)
            c.set_line_width(6)
            c.arc(640, 560, 80 + 220 * k, math.pi * 0.7, math.pi * 1.3)
            c.stroke()


def keypad_close(c, t, press=0.0, n_pressed=0):
    vgrad(c, 0, 0, W, H, ROSE, ROSE_D)
    for (x, y) in DOTS:
        c.set_source_rgba(*CREAM, 0.12)
        c.arc(x, y * 1.6, 5, 0, 2 * math.pi)
        c.fill()
    c.save()
    c.translate(W / 2 - 60, H / 2 + 20)
    c.scale(3.2, 3.2)
    c.translate(-1340, -430)
    c.set_source_rgb(*MINT)
    rr(c, 1340 - 70, 430 - 124, 140, 250, 22)
    c.fill()
    c.set_source_rgb(*MINT_D)
    rr(c, 1300, 410, 80, 110, 10)
    c.fill()
    digits = "123456789*0#"
    for r in range(4):
        for k in range(3):
            i = r * 3 + k
            lit = i < n_pressed
            c.set_source_rgb(*(mix(CREAM, MUST, 0.6) if lit else CREAM))
            rr(c, 1308 + k * 24, 418 + r * 26, 18, 18, 5)
            c.fill()
            text(c, digits[i], 1317 + k * 24, 432 + r * 26, 11, INK, 1.0, "c", FONTB)
    c.restore()
    fx = W / 2 - 60 + (-32 + (n_pressed % 3) * 24 + 9) * 3.2
    fy = H / 2 + 20 + (-12 + (n_pressed // 3 % 4) * 26 + 9) * 3.2
    c.save()
    c.translate(fx + 20, fy + 30 - 30 * press)
    c.set_source_rgb(*PLUM)
    c.set_line_width(120)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(460, 520)
    c.line_to(120, 120)
    c.stroke()
    c.set_source_rgb(*GRAN_SKIN)
    rr(c, -30, -40, 160, 190, 60)
    c.fill()
    c.set_source_rgb(*GRAN_SKIN)
    rr(c, -40, -50, 56, 120, 26)
    c.fill()
    c.restore()


def hangup_close(c, t, k=0.0):
    vgrad(c, 0, 0, W, H, ROSE, ROSE_D)
    for (x, y) in DOTS:
        c.set_source_rgba(*CREAM, 0.12)
        c.arc(x, y * 1.6, 5, 0, 2 * math.pi)
        c.fill()
    c.save()
    c.translate(W / 2 + 80, H / 2 + 60)
    c.scale(2.6, 2.6)
    c.translate(-1340, -430)
    c.set_source_rgb(*MINT)
    rr(c, 1270, 306, 140, 250, 22)
    c.fill()
    c.set_source_rgb(*MINT_D)
    rr(c, 1300, 410, 80, 110, 10)
    c.fill()
    for r in range(4):
        for kk in range(3):
            c.set_source_rgb(*CREAM)
            rr(c, 1308 + kk * 24, 418 + r * 26, 18, 18, 5)
            c.fill()
    yy = lerp(250, 368, ease(k))
    receiver(c, 1340, yy, 0.85, math.pi / 2)
    hand(c, 1360, yy + 10, GRAN_SKIN, 22)
    c.set_source_rgb(*PLUM)
    c.set_line_width(40)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(1520, yy + 150)
    c.line_to(1374, yy + 16)
    c.stroke()
    c.restore()


def calendar_close(c, t, week=1, draw=1.0):
    vgrad(c, 0, 0, W, H, ROSE, ROSE_D)
    c.save()
    c.translate(W / 2, H / 2 + 10)
    c.rotate(-0.03)
    c.set_source_rgba(0, 0, 0, 0.2)
    rr(c, -470, -440, 960, 900, 16)
    c.fill()
    c.set_source_rgb(*PAPER)
    rr(c, -480, -450, 960, 900, 16)
    c.fill()
    c.set_source_rgb(*RED)
    c.rectangle(-480, -450, 960, 120)
    c.fill()
    text(c, "S U N D A Y S", 0, -370, 60, CREAM, 1.0, "c")
    days = ["M", "T", "W", "T", "F", "S", "S"]
    for k in range(7):
        text(c, days[k], -400 + k * 133, -270, 40, PLUM_D if k < 6 else RED, 1.0, "c")
    for r in range(5):
        for k in range(7):
            n = r * 7 + k + 1
            if n > 30:
                continue
            text(c, str(n), -400 + k * 133, -180 + r * 130, 50, INK if k < 6 else RED, 0.75, "c", FONTB)
        if r < 5:
            kk = 1.0 if r < week - 1 else (draw if r == week - 1 else 0)
            if r <= week - 1:
                marker_circle(c, -400 + 6 * 133, -196 + r * 130, 56, 46, kk, 7, RED, 1.0, seed=r)
                if kk > 0.9:
                    text(c, "6 PM", -400 + 6 * 133 - 120, -150 + r * 130, 30, RED, min(1, (kk - 0.9) * 10), "c", FONTB)
    c.restore()


def split(c, t, left, right, clock=(6, 0, 0), a_div=1.0):
    c.save()
    c.rectangle(0, 0, W / 2 - 6, H)
    c.clip()
    c.translate(-W / 4, 0)
    left(c)
    c.restore()
    c.save()
    c.rectangle(W / 2 + 6, 0, W / 2, H)
    c.clip()
    c.translate(W / 4, 0)
    right(c)
    c.restore()
    c.set_source_rgba(*PAPER, a_div)
    c.rectangle(W / 2 - 6, 0, 12, H)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.25 * a_div)
    c.arc(W / 2 + 4, 150, 84, 0, 2 * math.pi)
    c.fill()
    wall_clock(c, W / 2, 144, 70, clock[0], clock[1], clock[2], PAPER, PLUM_D)
