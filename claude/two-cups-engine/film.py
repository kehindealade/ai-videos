import cairo, math, sys, subprocess, os, random
from timeline import *

W, H, FPS = 1920, 1080, 30
FONT = "Rounded Mplus 1c ExtraBold"


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


WALL = hx("5E6B78")
WALL_D = hx("3E4852")
FLOOR = hx("4A535C")
SKY = hx("8C98A4")
INK = hx("1E242B")
YEL = hx("F2C14E")
YEL_D = hx("C9962B")
CREAM = hx("F1EBDD")
SLATE_N = hx("2A3139")
SKIN = hx("77502F")
SKIN_D = hx("5E3E24")
SKIN_L = hx("8C6340")
HAIR = hx("ECEEF0")
CARD = hx("7B9084")
CARD_D = hx("5C6F65")
TROUS = hx("232830")
SLIP = hx("4B4440")
STEEL = hx("8794A1")
STEEL_D = hx("5F6C79")
MUST = hx("A39A63")
MUST_D = hx("7F7747")
MUST_L = hx("BDB580")
POT = hx("4A5A6B")
POT_D = hx("37444F")
LEAF_G = hx("5E9A66")
LEAF_B = hx("7A6E3E")
RAIN = hx("C3D0DC")

UI = {}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(p, q, k):
    return tuple(lerp(p[i], q[i], k) for i in range(3))


def pulse(t, a, d=0.5):
    return math.sin(math.pi * seg(t, a, a + d)) if a <= t <= a + d else 0.0


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ell(c, cx, cy, rx, ry):
    c.save()
    c.translate(cx, cy)
    c.scale(rx, ry)
    c.new_sub_path()
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def text(c, s, x, y, size, col, alpha=1.0, align="c"):
    c.select_font_face(FONT)
    c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        x = x - e.width / 2 - e.x_bearing
    elif align == "r":
        x = x - e.width - e.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, alpha)
    c.show_text(s)
    return e.width


def tint(c, col, a):
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


def glow(c, x, y, r, a, col=YEL):
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


def fillc(c, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.fill()


random.seed(5)
RAIN_L = [(random.random(), random.random(), 0.05 + 0.07 * random.random(), 0.9 + 1.2 * random.random()) for _ in range(90)]
DROPS = [(random.random(), random.random(), 3 + 5 * random.random()) for _ in range(26)]
STUB = [(random.uniform(-1, 1), random.uniform(0, 1), random.random()) for _ in range(90)]


def steam(c, x, y, t, seed=0, n=3, h=170, w=16, a=0.5, col=CREAM):
    for i in range(n):
        for j in range(24):
            k = j / 23
            xx = x + (i - (n - 1) / 2) * 20 + w * math.sin(t * 2.2 + j * 0.45 + seed + i * 2.1) * (0.4 + k)
            yy = y - k * h - ((t * 40 + i * 30) % 12)
            c.set_source_rgba(*col, a * (1 - k) ** 1.3 * min(1, k * 6))
            c.arc(xx, yy, 7 + k * 14, 0, 2 * math.pi)
            c.fill()


def mug_dim(c, x, y, s, col):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgb(*col)
    c.new_sub_path()
    c.move_to(-48, -90)
    c.line_to(48, -90)
    c.curve_to(48, -36, 38, 0, 24, 0)
    c.line_to(-24, 0)
    c.curve_to(-38, 0, -48, -36, -48, -90)
    c.close_path()
    c.fill()
    c.set_source_rgb(*col)
    c.set_line_width(13)
    c.new_sub_path()
    c.arc(52, -54, 24, -math.pi / 2 - 0.2, math.pi / 2 + 0.2)
    c.stroke()
    c.set_source_rgba(0, 0, 0, 0.2)
    ell(c, 0, -90, 48, 11)
    c.fill()
    c.restore()


def ik(sx, sy, tx, ty, l1, l2, out=1):
    if isinstance(out, tuple):
        return ik_side(sx, sy, tx, ty, l1, l2, out[1])
    dx, dy = tx - sx, ty - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    a = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dy, dx)
    best = None
    for sg in (1, -1):
        ex = sx + l1 * math.cos(base + sg * a)
        ey = sy + l1 * math.sin(base + sg * a)
        sc = ey + out * 0.25 * (ex - (sx + tx) / 2)
        if best is None or sc > best[0]:
            best = (sc, ex, ey)
    return best[1], best[2]


MOODS = {
    "neutral": dict(tilt=0, bdy=0, lid=0.0, eo=1.0, pdy=0, mouth="flat", bags=0.0),
    "sad": dict(tilt=14, bdy=2, lid=0.18, eo=0.95, pdy=7, mouth="down", bags=0.15),
    "tired": dict(tilt=5, bdy=6, lid=0.5, eo=0.9, pdy=5, mouth="tired", bags=0.5),
    "smile": dict(tilt=-3, bdy=-3, lid=0.0, eo=0.82, pdy=0, mouth="smile", bags=0.0),
    "surprised": dict(tilt=-4, bdy=-16, lid=0.0, eo=1.28, pdy=0, mouth="oh", bags=0.0),
}


def head(c, t, mood="neutral", look=(0.0, 0.0), seed=0.0):
    M = MOODS[mood]
    face = lambda: rrect(c, -100, -108, 200, 216, 82)
    c.set_source_rgb(*SKIN_D)
    for sx in (-1, 1):
        ell(c, sx * 102, 14, 16, 28)
        c.fill()
    c.set_source_rgb(*SKIN)
    face()
    c.fill()
    c.save()
    face()
    c.clip()
    c.set_source_rgba(*SKIN_L, 0.5)
    ell(c, -34, -62, 46, 22)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.12)
    ell(c, 0, 128, 130, 40)
    c.fill()
    c.set_source_rgba(0.62, 0.66, 0.72, 0.13)
    ell(c, 0, 92, 120, 52)
    c.fill()
    c.restore()
    c.save()
    rrect(c, -104, -112, 208, 224, 86)
    c.clip()
    c.set_source_rgb(*HAIR)
    c.new_sub_path()
    c.move_to(-130, -20)
    c.line_to(-100, -20)
    c.curve_to(-98, -50, -86, -66, -64, -78)
    c.curve_to(-40, -90, -18, -86, 0, -86)
    c.curve_to(18, -86, 40, -90, 64, -78)
    c.curve_to(86, -66, 98, -50, 100, -20)
    c.line_to(130, -20)
    c.line_to(130, -160)
    c.line_to(-130, -160)
    c.close_path()
    c.fill()
    c.restore()
    c.set_source_rgb(*HAIR)
    for sx in (-1, 1):
        ell(c, sx * 98, -36, 8, 24)
        c.fill()
    c.set_source_rgb(*SKIN_D)
    ell(c, 0, 22, 20, 26)
    c.fill()
    c.set_source_rgb(*SKIN)
    ell(c, -3, 14, 12, 14)
    c.fill()
    c.set_source_rgb(*HAIR)
    for sx in (-1, 1):
        c.save()
        c.translate(sx * 15, 56)
        c.rotate(sx * 0.12)
        ell(c, 0, 0, 22, 9)
        c.fill()
        c.restore()
    bl = 0.08 if ((t + seed) % 4.3) < 0.13 else 1.0
    lx, ly = look
    for sx in (-1, 1):
        cx, cy = sx * 50, -4
        c.set_source_rgba(*INK, 0.0)
        c.set_source_rgb(*mix(SKIN, (1, 1, 1), 0.0))
        c.set_source_rgb(0.95, 0.94, 0.90)
        eo = M["eo"] * bl
        ell(c, cx + lx * 3, cy, 18, 20 * eo)
        c.fill()
        c.set_source_rgb(*INK)
        pr = 9.5 if mood != "surprised" else 6.5
        ell(c, cx + lx * 9, cy + 1 + M["pdy"] * 0.7 * eo + ly * 6, pr, pr * min(1, eo + 0.1))
        c.fill()
        c.set_source_rgb(1, 1, 1)
        ell(c, cx + lx * 9 - 3, cy - 3 + M["pdy"] * 0.5 * eo, 2.4, 2.4)
        c.fill()
        if M["lid"] > 0:
            c.save()
            ell(c, cx + lx * 3, cy, 19, 21)
            c.clip()
            c.set_source_rgb(*SKIN)
            c.rectangle(cx - 22, cy - 24, 44, 24 * M["lid"] * 2 - 0)
            c.fill()
            c.set_source_rgb(*SKIN_D)
            c.set_line_width(4)
            c.move_to(cx - 22, cy - 24 + 48 * M["lid"])
            c.line_to(cx + 22, cy - 24 + 48 * M["lid"])
            c.stroke()
            c.restore()
        if mood == "smile":
            c.save()
            ell(c, cx, cy, 19, 21)
            c.clip()
            c.set_source_rgb(*SKIN)
            ell(c, cx, cy + 34, 30, 22)
            c.fill()
            c.restore()
        if M["bags"] > 0:
            c.set_source_rgba(*SKIN_D, M["bags"] + 0.2)
            c.set_line_width(5)
            c.new_sub_path()
            c.arc(cx, cy + 14, 34, 0.25 * math.pi, 0.75 * math.pi)
            c.stroke()
    c.set_source_rgba(*HAIR, 0.96)
    c.set_line_width(11)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        cx = sx * 50
        by = -54 + M["bdy"]
        inner = -sx
        c.move_to(cx - sx * 28, by + M["tilt"] * 0.2 * (1 if mood != "surprised" else 0) - (0 if M["tilt"] >= 0 else 0))
        c.curve_to(cx - sx * 10, by - 8 - (6 if mood == "surprised" else 0), cx + sx * 12, by - 6,
                   cx + sx * 28, by - M["tilt"] * 0.9 + 2)
        c.stroke()
    c.set_source_rgba(*INK, 0.10)
    for sx in (-1, 1):
        ell(c, sx * 50, -4, 37, 37)
        c.fill()
    c.set_source_rgb(*INK)
    c.set_line_width(6)
    for sx in (-1, 1):
        ell(c, sx * 50, -4, 37, 37)
        c.stroke()
    c.set_line_width(5)
    c.new_sub_path()
    c.arc(0, -16, 14, math.radians(25), math.radians(155))
    c.stroke()
    for sx in (-1, 1):
        c.move_to(sx * 86, -8)
        c.line_to(sx * 106, -4)
        c.stroke()
    c.set_source_rgba(1, 1, 1, 0.55)
    c.set_line_width(4)
    for sx in (-1, 1):
        c.new_sub_path()
        c.arc(sx * 50, -4, 28, math.radians(200), math.radians(245))
        c.stroke()
    c.set_source_rgb(0.20, 0.10, 0.07)
    c.set_line_width(7)
    m = M["mouth"]
    if m == "flat":
        c.move_to(-20, 74)
        c.curve_to(-8, 76, 8, 76, 20, 73)
        c.stroke()
    elif m == "down":
        c.move_to(-20, 82)
        c.curve_to(-10, 68, 10, 68, 20, 82)
        c.stroke()
    elif m == "tired":
        c.move_to(-17, 76)
        c.curve_to(-6, 72, 8, 74, 18, 80)
        c.stroke()
    elif m == "smile":
        c.move_to(-24, 68)
        c.curve_to(-12, 86, 12, 86, 24, 68)
        c.stroke()
        c.set_source_rgba(*SKIN_L, 0.55)
        for sx in (-1, 1):
            ell(c, sx * 56, 56, 15, 11)
            c.fill()
    elif m == "oh":
        ell(c, 0, 76, 11, 15)
        c.fill()


def torso(c, hold=0.0):
    c.set_source_rgb(*CARD_D)
    rrect(c, -104, -394, 208, 262, 72)
    c.fill()
    c.set_source_rgb(*CARD)
    rrect(c, -98, -390, 196, 252, 68)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.move_to(-40, -392)
    c.line_to(40, -392)
    c.line_to(0, -290)
    c.close_path()
    c.fill()
    c.set_source_rgb(*SKIN_D)
    c.move_to(-26, -392)
    c.line_to(26, -392)
    c.line_to(0, -336)
    c.close_path()
    c.fill()
    c.set_source_rgb(*CARD_D)
    c.set_line_width(5)
    c.move_to(-40, -392)
    c.line_to(-14, -150)
    c.move_to(40, -392)
    c.line_to(14, -150)
    c.stroke()
    c.set_source_rgb(*CREAM)
    c.set_line_width(2)
    for k in range(3):
        c.arc(0, -276 + k * 52, 7, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(*CARD_D, 0.9)
    rrect(c, -76, -230, 50, 54, 10)
    c.fill()
    c.set_source_rgb(*CARD)
    rrect(c, -72, -226, 42, 46, 8)
    c.fill()


def kettle(c, x, y, s=1.0, t=0.0, glw=1.0, shake=0.0):
    c.save()
    c.translate(x + math.sin(t * 60) * 3 * shake, y)
    c.scale(s, s)
    glow(c, 0, -110, 300, 0.30 * glw, YEL)
    c.set_source_rgba(0, 0, 0, 0.3)
    ell(c, 0, 4, 170, 16)
    c.fill()
    c.set_source_rgb(*STEEL_D)
    c.set_line_width(20)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-132, -190)
    c.curve_to(-250, -210, -250, -60, -138, -50)
    c.stroke()
    c.set_source_rgb(*STEEL_D)
    c.move_to(112, -110)
    c.curve_to(170, -130, 190, -190, 214, -250)
    c.line_to(236, -240)
    c.curve_to(212, -150, 190, -90, 130, -70)
    c.close_path()
    c.fill()
    g = cairo.LinearGradient(-150, 0, 150, 0)
    g.add_color_stop_rgb(0, *STEEL_D)
    g.add_color_stop_rgb(0.35, *STEEL)
    g.add_color_stop_rgb(1, *mix(STEEL_D, INK, 0.2))
    c.set_source(g)
    c.new_sub_path()
    c.move_to(-120, -6)
    c.curve_to(-170, -6, -160, -150, -110, -200)
    c.line_to(110, -200)
    c.curve_to(160, -150, 170, -6, 120, -6)
    c.close_path()
    c.fill()
    g2 = cairo.LinearGradient(0, -140, 0, 0)
    g2.add_color_stop_rgba(0, *YEL, 0)
    g2.add_color_stop_rgba(1, *YEL, 0.55 * glw)
    c.set_source(g2)
    c.new_sub_path()
    c.move_to(-120, -6)
    c.curve_to(-170, -6, -160, -150, -110, -200)
    c.line_to(110, -200)
    c.curve_to(160, -150, 170, -6, 120, -6)
    c.close_path()
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.25)
    rrect(c, -100, -178, 16, 120, 8)
    c.fill()
    c.set_source_rgb(*STEEL_D)
    rrect(c, -78, -226, 156, 34, 16)
    c.fill()
    c.set_source_rgb(*INK)
    c.arc(0, -240, 14, 0, 2 * math.pi)
    c.fill()
    c.restore()


def chair(c, x, floor, s=1.0, back_h=420, front=True):
    c.save()
    c.translate(x, floor)
    c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.28)
    ell(c, 0, 4, 330, 26)
    c.fill()
    c.set_source_rgb(0.20, 0.17, 0.14)
    for sx in (-1, 1):
        rrect(c, sx * 250 - 18, -50, 36, 52, 10)
        c.fill()
    c.set_source_rgb(*MUST_D)
    rrect(c, -245, -back_h - 10, 490, back_h - 10, 110)
    c.fill()
    c.set_source_rgb(*MUST)
    rrect(c, -222, -back_h + 8, 444, back_h - 60, 96)
    c.fill()
    c.set_source_rgba(*MUST_L, 0.5)
    ell(c, -90, -back_h + 130, 70, 120)
    c.fill()
    c.set_source_rgb(*MUST_D)
    c.set_line_width(5)
    for k in range(3):
        c.move_to(-60 + k * 60, -back_h + 60)
        c.line_to(-60 + k * 60, -back_h + 250)
        c.stroke()
    c.restore()


def chair_arms(c, x, floor, s=1.0, ax=252):
    c.save()
    c.translate(x, floor)
    c.scale(s, s)
    for sx in (-1, 1):
        c.set_source_rgb(*MUST_D)
        rrect(c, sx * ax - 52, -250, 104, 220, 40)
        c.fill()
        c.set_source_rgb(*MUST)
        rrect(c, sx * ax - 44, -256, 88, 200, 36)
        c.fill()
        c.set_source_rgba(*MUST_L, 0.55)
        ell(c, sx * ax, -210, 24, 14)
        c.fill()
    c.restore()


def chair_seat(c, x, floor, s=1.0):
    c.save()
    c.translate(x, floor)
    c.scale(s, s)
    c.set_source_rgb(*MUST_D)
    rrect(c, -230, -100, 460, 100, 34)
    c.fill()
    c.set_source_rgb(*MUST)
    rrect(c, -220, -118, 440, 92, 30)
    c.fill()
    c.set_source_rgba(*MUST_L, 0.5)
    ell(c, -40, -92, 110, 18)
    c.fill()
    c.restore()


def chair_front(c, x, floor, s=1.0, back_h=420):
    chair_arms(c, x, floor, s)
    chair_seat(c, x, floor, s)


def lamp(c, x, floor, on=1.0):
    glow(c, x, floor - 520, 360, 0.42 * on, YEL)
    c.set_source_rgb(*WALL_D)
    rrect(c, x - 5, floor - 520, 10, 520, 4)
    c.fill()
    rrect(c, x - 50, floor - 12, 100, 14, 7)
    c.fill()
    c.set_source_rgb(*mix(CREAM, YEL, 0.5 * on))
    c.new_sub_path()
    c.move_to(x - 56, floor - 450)
    c.line_to(x + 56, floor - 450)
    c.line_to(x + 36, floor - 560)
    c.line_to(x - 36, floor - 560)
    c.close_path()
    c.fill()


def meter_draw(c, x0, y0, k, n, alpha=1.0, bump=0.0, shownum=True):
    c.save()
    c.translate(x0, y0)
    c.scale(k, k)
    c.set_source_rgba(0, 0, 0, 0.25 * alpha)
    rrect(c, 4, 8, 410, 200, 30)
    c.fill()
    c.set_source_rgba(0.97, 0.96, 0.93, 0.93 * alpha)
    rrect(c, 0, 0, 410, 200, 30)
    c.fill()
    text(c, "CUPS MADE", 205, 54, 31, INK, 0.7 * alpha)
    if shownum:
        c.save()
        c.translate(205, 150)
        sc = 1 + 0.3 * math.sin(math.pi * bump)
        c.scale(sc, sc)
        text(c, str(n), 0, 0, 112, INK, alpha)
        c.restore()
    c.restore()


def vignette(c, a=0.35):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.05, 0.06, 0.09, a)
    c.set_source(g)
    c.paint()


def wall_bg(c, d=0.0):
    vgrad(c, 0, 0, W, H, mix(WALL, WALL_D, 0.18 + d), mix(WALL, WALL_D, 0.05 + d))


def floor_bg(c, y, t=0.0):
    c.set_source_rgb(*FLOOR)
    c.rectangle(0, y, W, H - y)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.14)
    c.set_line_width(3)
    for k in range(1, 5):
        yy = y + (H - y) * (k / 5) ** 1.4
        c.move_to(0, yy)
        c.line_to(W, yy)
        c.stroke()
    c.set_source_rgba(0, 0, 0, 0.35)
    c.rectangle(0, y - 8, W, 12)
    c.fill()
    c.set_source_rgb(*WALL_D)
    c.rectangle(0, y - 40, W, 40)
    c.fill()


UI_ON = True
NSKIN = hx("9A6A45")
NSKIN_D = hx("7C5233")
NSKIN_L = hx("B3825A")
DRESS = hx("B4583A")
DRESS_D = hx("8C3F27")
WRAP = hx("2F6B6E")
WRAP_D = hx("234F52")
LEAF_N = hx("86C47E")
TEA = (0.42, 0.25, 0.10)
GREY = hx("8E9BA8")
GREY_D = hx("6C7986")


def cam(c, z, fx, fy):
    hw, hh = W / (2 * z), H / (2 * z)
    fx = clamp(fx, hw, W - hw)
    fy = clamp(fy, hh, H - hh)
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-fx, -fy)


def window(c, t, x, y, w, h, sun=0.0, rain=1.0, cross=True, behind=None):
    c.save()
    rrect(c, x - 18, y - 18, w + 36, h + 36, 14)
    fillc(c, WALL_D)
    c.restore()
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    sky = mix(SKY, hx("D9DDC6"), sun * 0.75)
    sky2 = mix(hx("7B8794"), hx("EFE3B0"), sun * 0.8)
    vgrad(c, x, y, w, h, sky2, sky)
    if sun > 0:
        glow(c, x + w * 0.75, y + h * 0.18, w * 0.9, 0.55 * sun, YEL)
    if behind:
        behind(c)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    passes = [(0.0, min(1.0, rain))]
    if rain > 1:
        passes.append((0.37, rain - 1))
    for off, a in passes:
        if a <= 0:
            continue
        for fx, fy, ln, sp in RAIN_L:
            yy = (fy + off + t * sp * 0.55 * (1 + 0.8 * off)) % 1.0
            xx = ((fx + off) % 1.0) * (w + 120) - 60 + yy * 40
            ly = y + yy * (h + 80) - 40
            c.set_source_rgba(*RAIN, 0.5 * a)
            c.set_line_width(2.5)
            c.move_to(x + xx, ly)
            c.line_to(x + xx - 14 * ln * 4, ly + 120 * ln * 1.6 + 30)
            c.stroke()
    if rain > 0:
        ra = min(1.0, rain)
        for fx, fy, r in DROPS:
            dy = (fy + t * 0.012 * (r / 5)) % 1.0
            c.set_source_rgba(*RAIN, 0.55 * ra)
            ell(c, x + fx * w, y + dy * h, r * 0.6, r)
            c.fill()
            c.set_source_rgba(1, 1, 1, 0.5 * ra)
            ell(c, x + fx * w - 1, y + dy * h - r * 0.4, 1.4, 2.2)
            c.fill()
    c.restore()
    if cross:
        c.set_source_rgb(*WALL_D)
        c.rectangle(x + w / 2 - 7, y, 14, h)
        c.fill()
        c.rectangle(x, y + h * 0.5 - 7, w, 14)
        c.fill()


def cup(c, x, y, s=1.0, t=0.0, st=True, sq=0.0, glw=0.35, seed=0, body=YEL, rim=YEL_D, tea=True, sa=1.0):
    if glw > 0:
        glow(c, x, y - 50 * s, 190 * s, glw, YEL)
    c.save()
    c.translate(x, y)
    c.scale(s * (1 + 0.04 * sq), s * (1 - 0.06 * sq))
    c.set_source_rgba(0, 0, 0, 0.28)
    ell(c, 0, 4, 66, 10)
    c.fill()
    c.set_source_rgb(*body)
    c.new_sub_path()
    c.move_to(-56, -104)
    c.line_to(56, -104)
    c.curve_to(56, -40, 44, -2, 28, 0)
    c.line_to(-28, 0)
    c.curve_to(-44, -2, -56, -40, -56, -104)
    c.close_path()
    c.fill()
    c.set_line_width(15)
    c.new_sub_path()
    c.arc(60, -62, 28, -math.pi / 2 - 0.2, math.pi / 2 + 0.2)
    c.stroke()
    c.set_source_rgb(*rim)
    c.new_sub_path()
    c.move_to(-52, -64)
    c.line_to(52, -64)
    c.curve_to(52, -40, 44, -8, 28, -2)
    c.line_to(-28, -2)
    c.curve_to(-44, -8, -52, -40, -52, -64)
    c.close_path()
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.28)
    rrect(c, -40, -96, 9, 62, 4)
    c.fill()
    c.set_source_rgb(*rim)
    ell(c, 0, -104, 56, 13)
    c.fill()
    if tea:
        c.set_source_rgb(*TEA)
        ell(c, 0, -103, 47, 9)
        c.fill()
    c.restore()
    if st and sa > 0.01 and tea:
        steam(c, x, y - 112 * s, t, seed, 3, 150 * s, 14 * s, 0.5 * sa)


def ik_side(sx, sy, tx, ty, l1, l2, side):
    dx, dy = tx - sx, ty - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    a = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dy, dx)
    cands = [(sx + l1 * math.cos(base + sg * a), sy + l1 * math.sin(base + sg * a)) for sg in (1, -1)]
    return max(cands, key=lambda e: 0.5 * side * e[0] + e[1])


def arm(c, sx, sy, tx, ty, l1, l2, wd, col=CARD, out=1, hand=True, hs=1.0, cold=CARD_D, cuff=CREAM, skin=SKIN,
        skin_l=SKIN_L, elbow=None):
    ex, ey = elbow if elbow else ik(sx, sy, tx, ty, l1, l2, out)
    ang = math.atan2(ty - ey, tx - ex)
    bx, by = tx - math.cos(ang) * wd * 0.42, ty - math.sin(ang) * wd * 0.42
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    for wdt, cc in ((wd + 8, cold), (wd, col)):
        c.set_source_rgb(*cc)
        c.set_line_width(wdt)
        c.move_to(sx, sy)
        c.line_to(ex, ey)
        c.line_to(bx, by)
        c.stroke()
    c.set_source_rgb(*cuff)
    c.set_line_width(wd * 0.82)
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    c.move_to(bx - math.cos(ang) * 4, by - math.sin(ang) * 4)
    c.line_to(bx + math.cos(ang) * wd * 0.22, by + math.sin(ang) * wd * 0.22)
    c.stroke()
    if hand:
        c.set_source_rgb(*skin)
        ell(c, tx + math.cos(ang) * wd * 0.05, ty + math.sin(ang) * wd * 0.05, wd * 0.52 * hs, wd * 0.46 * hs)
        c.fill()
        c.set_source_rgb(*skin_l)
        ell(c, tx - wd * 0.12, ty - wd * 0.12, wd * 0.16, wd * 0.12)
        c.fill()
    return ex, ey


def legs(c, walk=0.0, ph=0.0):
    for i, sx in enumerate((-1, 1)):
        sn = math.sin(ph + i * math.pi)
        dy = -16 * max(0.0, sn) * walk
        dx = 12 * sn * walk
        c.set_source_rgb(*TROUS)
        rrect(c, sx * 36 - 36 + dx, -170 + dy, 72, 150, 26)
        c.fill()
        c.set_source_rgb(*SLIP)
        ell(c, sx * 46 + dx * 1.4, -10 + dy, 52, 22)
        c.fill()


def man(c, t, x, feet, s=1.0, mood="neutral", look=(0, 0), tl=None, tr=None, seed=0.0, bob=0.0, walk=0.0, ph=0.0,
        arms=True, alen=112):
    c.save()
    c.translate(x, feet)
    c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.25)
    ell(c, 0, 0, 130, 18)
    c.fill()
    legs(c, walk, ph)
    c.translate(0, bob)
    torso(c)
    c.save()
    c.translate(0, -470)
    head(c, t, mood, look, seed)
    c.restore()
    c.restore()
    sh = [(x - 88 * s, feet - 360 * s + bob * s), (x + 88 * s, feet - 360 * s + bob * s)]
    if arms:
        man_arms(c, sh, s, tl, tr, x, feet - 160 * s, alen)
    return sh


def man_arms(c, sh, s, tl, tr, x, resty, alen=112, which=(0, 1)):
    for i, (tg, sx) in enumerate(((tl, -1), (tr, 1))):
        if i not in which:
            continue
        if tg is None:
            tg = (x + sx * 116 * s, resty)
        arm(c, sh[i][0], sh[i][1], tg[0], tg[1], alen * s, alen * s, 62 * s, out=sx)


def man_sit(c, t, x, hips, s=1.0, mood="neutral", look=(0, 0), tl=None, tr=None, seed=0.0, bob=0.0, floor=None,
            alen=118, arms=True):
    fl = floor if floor is not None else hips + 130 * s
    c.save()
    c.translate(x, hips)
    c.scale(s, s)
    fh = (fl - hips) / s
    for sx in (-1, 1):
        c.set_source_rgb(*TROUS)
        rrect(c, sx * 46 - 31, 52, 62, fh - 52 - 14, 22)
        c.fill()
        c.set_source_rgb(*SLIP)
        ell(c, sx * 50 + sx * 6, fh - 12, 48, 20)
        c.fill()
    c.save()
    c.translate(0, bob)
    c.translate(0, 132)
    torso(c)
    c.translate(0, -470)
    head(c, t, mood, look, seed)
    c.restore()
    for sx in (-1, 1):
        c.set_source_rgb(*mix(TROUS, (1, 1, 1), 0.08))
        rrect(c, sx * 46 - 44, -34, 88, 96, 40)
        c.fill()
        c.set_source_rgba(1, 1, 1, 0.10)
        rrect(c, sx * 46 - 34, -28, 68, 20, 10)
        c.fill()
    c.restore()
    sy = hips + (132 - 360) * s + bob * s
    sh = [(x - 84 * s, sy), (x + 84 * s, sy)]
    if arms:
        sit_arms(c, sh, s, x, hips, tl, tr, alen)
    return sh


def sit_arms(c, sh, s, x, hips, tl=None, tr=None, alen=118, which=(0, 1), side=False):
    for i, (tg, sx) in enumerate(((tl, -1), (tr, 1))):
        if i not in which:
            continue
        if tg is None:
            tg = (x + sx * 92 * s, hips + 6 * s)
        arm(c, sh[i][0], sh[i][1], tg[0], tg[1], alen * s, alen * s, 60 * s, out=("s", sx) if side else sx)


def leaf(c, x0, y0, ang, L, wdt, col, col_d):
    c.save()
    c.translate(x0, y0)
    c.rotate(ang)
    c.set_source_rgb(*col_d)
    c.set_line_width(4)
    c.move_to(0, 0)
    c.line_to(0, -L * 0.3)
    c.stroke()
    c.translate(0, -L * 0.3 - L * 0.35)
    c.set_source_rgb(*col)
    ell(c, 0, 0, wdt, L * 0.35)
    c.fill()
    c.set_source_rgb(*col_d)
    c.set_line_width(2.5)
    c.move_to(0, L * 0.33)
    c.line_to(0, -L * 0.3)
    c.stroke()
    c.restore()


def plant(c, x, y, s=1.0, state=0.5, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    hk = min(1.0, state / 0.6)
    droop = 1 - hk
    col = mix(LEAF_B, LEAF_G, hk)
    col_d = mix(col, INK, 0.25)
    sway = math.sin(t * 0.8) * 0.02
    leaves = [(-68, 150), (-40, 190), (-14, 215), (12, 205), (38, 185), (64, 150), (-90, 110), (88, 115)]
    for a, L in leaves:
        L = L * (0.82 + 0.18 * hk)
        sg = 1 if a >= 0 else -1
        a0 = math.radians(a) + sway
        a1 = a0 + sg * math.radians(100) * droop
        p0 = (0, -104)
        p1 = (p0[0] + L * 0.55 * math.sin(a0), p0[1] - L * 0.55 * math.cos(a0))
        tip = (p1[0] + L * 0.5 * math.sin(a1), p1[1] - L * 0.5 * math.cos(a1))
        c.set_source_rgb(*col_d)
        c.set_line_width(6)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(*p0)
        c.curve_to(p0[0], p0[1] - 20, p1[0], p1[1] + 10, *p1)
        c.stroke()
        mx, my = (p1[0] + tip[0]) / 2, (p1[1] + tip[1]) / 2
        c.save()
        c.translate(mx, my)
        c.rotate(a1)
        c.set_source_rgb(*col)
        ell(c, 0, 0, 20 + 4 * hk, L * 0.28)
        c.fill()
        c.set_source_rgb(*col_d)
        c.set_line_width(3)
        c.move_to(0, L * 0.28)
        c.line_to(0, -L * 0.28)
        c.stroke()
        c.restore()
    for a, L, s0, s1 in ((-22, 92, 0.2, 0.3), (26, 104, 0.42, 0.5), (-48, 96, 0.43, 0.5)):
        k = seg(state, s0, s1)
        if k <= 0:
            continue
        sz = ease(k) * (1 + 0.35 * math.sin(math.pi * k))
        leaf(c, 0, -110, math.radians(a) + sway, L * sz, 17 * sz, LEAF_N, mix(LEAF_G, INK, 0.25))
    if state > 0.55:
        g = ease(seg(state, 0.55, 0.7))
        bud = ease(seg(state, 0.6, 0.72))
        op = ease(seg(state, 0.86, 1.0))
        fx, fy = 4, -104 - 232 * g
        c.set_source_rgb(*mix(LEAF_G, INK, 0.25))
        c.set_line_width(6)
        c.move_to(0, -108)
        c.curve_to(0, -140, 4, -104 - 150 * g, fx, fy + 18)
        c.stroke()
        if op < 1 and bud > 0:
            c.save()
            c.translate(fx, fy)
            c.scale(bud * (1 - op * 0.6), bud * (1 - op * 0.6))
            c.set_source_rgb(*YEL)
            ell(c, 0, -12, 15, 26)
            c.fill()
            c.set_source_rgb(*LEAF_G)
            c.move_to(-20, 4)
            c.curve_to(-22, -18, -10, -30, 0, -8)
            c.curve_to(10, -30, 22, -18, 20, 4)
            c.curve_to(10, 18, -10, 18, -20, 4)
            c.fill()
            c.restore()
        if op > 0:
            c.save()
            c.translate(fx, fy)
            c.scale(op, op)
            glow(c, 0, 0, 110, 0.45 * op, YEL)
            for i in range(9):
                c.save()
                c.rotate(i * 2 * math.pi / 9)
                c.set_source_rgb(*YEL)
                ell(c, 0, -30, 15, 25)
                c.fill()
                c.restore()
            c.set_source_rgb(*YEL_D)
            c.arc(0, 0, 17, 0, 2 * math.pi)
            c.fill()
            c.restore()
    c.set_source_rgb(*POT_D)
    c.new_sub_path()
    c.move_to(-64, -104)
    c.line_to(64, -104)
    c.line_to(50, 0)
    c.line_to(-50, 0)
    c.close_path()
    c.fill()
    c.set_source_rgb(*POT)
    rrect(c, -72, -116, 144, 34, 10)
    c.fill()
    c.new_sub_path()
    c.move_to(-58, -84)
    c.line_to(58, -84)
    c.line_to(47, -4)
    c.line_to(-47, -4)
    c.close_path()
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.12)
    rrect(c, -50, -78, 12, 66, 5)
    c.fill()
    c.restore()


def meter(c, n, alpha=1.0, bump=0.0, shownum=True):
    UI["meter"] = (n, alpha, bump, shownum)
    if UI_ON:
        meter_draw(c, 1470, 34, 1.0, n, alpha, bump, shownum)


def tag_draw(c, x, y, size, s, pop=0.0, alpha=1.0):
    c.select_font_face(FONT)
    c.set_font_size(size)
    wd = c.text_extents(s).width
    c.save()
    c.translate(x, y)
    k = 1 + 0.2 * math.sin(math.pi * pop)
    c.scale(k, k)
    c.set_source_rgba(0, 0, 0, 0.3 * alpha)
    rrect(c, 3, -size * 0.92 + 5, wd + size * 1.7, size * 1.84, size * 0.92)
    c.fill()
    c.set_source_rgba(*INK, alpha)
    rrect(c, 0, -size * 0.92, wd + size * 1.7, size * 1.84, size * 0.92)
    c.fill()
    c.set_source_rgba(*CREAM, 0.25 * alpha)
    c.set_line_width(2)
    rrect(c, 1, -size * 0.92 + 1, wd + size * 1.7 - 2, size * 1.84 - 2, size * 0.9)
    c.stroke()
    text(c, s, size * 0.85, size * 0.36, size, CREAM, alpha, "l")
    c.restore()


def tag(c, s, pop=0.0, alpha=1.0):
    UI["tag"] = (s, pop, alpha)
    if UI_ON:
        tag_draw(c, 60, 84, 36, s, pop, alpha)


def caption(c, t, s, a, b, y0=1012, size=70, col=CREAM):
    if t < a or t > b:
        return
    k = ease(seg(t, a, a + 0.35)) * (1 - ease(seg(t, b - 0.3, b)))
    y = y0 + 16 * (1 - ease(seg(t, a, a + 0.35)))
    UI.setdefault("caps", []).append((s, k, col))
    if not UI_ON:
        return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0.06, 0.07, 0.10, 0)
    g.add_color_stop_rgba(1, 0.06, 0.07, 0.10, 0.6 * k)
    c.set_source(g)
    c.rectangle(0, 860, W, H - 860)
    c.fill()
    for dx, dy, al in ((0, 7, 0.35), (4, 5, 0.6), (-3, 5, 0.4)):
        text(c, s, W / 2 + dx, y + dy, size, INK, al * k)
    text(c, s, W / 2, y, size, col, k)


def big_two(c, t, ts=TWO_T):
    f = ease(seg(t, ts, ts + 0.8))
    UI["two"] = t
    if t >= ts:
        meter(c, 2, ease(seg(t, ts - 0.1, ts + 0.5)), pulse(t, ts + 0.8, 0.4), shownum=(t >= ts + 0.8))
    if t < ts + 0.8 and UI_ON:
        px = lerp(W / 2, 1675, f)
        py = lerp(745, 150, f)
        sz = lerp(470, 112, f) * (1 + 0.18 * (1 - seg(t, 0, 0.18)))
        for dx, dy, col, al in ((7, 9, INK, 0.45), (0, 0, CREAM, 1.0)):
            text(c, "2", px + dx * (1 - f), py + dy * (1 - f), sz, col, al * (1 if f < 0.9 else 1 - (f - 0.9) * 10))


def sprout(c, cx, cy, r, a=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(r / 100.0, r / 100.0)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(0.85, 0.64, 0.25, a)
    c.set_line_width(8)
    for ang in (-150, -120, -90, -60, -30):
        g = math.radians(ang)
        c.move_to(52 * math.cos(g), 44 + 52 * math.sin(g))
        c.line_to(70 * math.cos(g), 44 + 70 * math.sin(g))
        c.stroke()
    c.arc(0, 44, 40, math.pi, 2 * math.pi)
    c.close_path()
    c.fill()
    c.set_source_rgba(*CREAM, a)
    rrect(c, -92, 40, 184, 14, 7)
    c.fill()
    c.set_source_rgba(0.37, 0.54, 0.31, a)
    c.set_line_width(10)
    c.move_to(0, 42)
    c.curve_to(2, 10, -4, -30, 0, -58)
    c.stroke()
    for sgn, ang, ln, y in ((-1, -0.45, 40, -50), (1, 0.45, 46, -62)):
        c.save()
        c.translate(0, y)
        c.rotate(ang)
        c.translate(sgn * ln * 0.55, 0)
        c.move_to(-ln * 0.6, 0)
        c.curve_to(-ln * 0.3, -ln * 0.42, ln * 0.3, -ln * 0.42, ln * 0.6, 0)
        c.curve_to(ln * 0.3, ln * 0.42, -ln * 0.3, ln * 0.42, -ln * 0.6, 0)
        c.close_path()
        c.set_source_rgba(0.47, 0.70, 0.40, a)
        c.fill()
        c.restore()
    c.restore()


def woman_head(c, t, mood="neutral", look=(0.0, 0.0), seed=0.0):
    c.set_source_rgb(*NSKIN_D)
    for sx in (-1, 1):
        ell(c, sx * 92, 18, 14, 24)
        c.fill()
    c.set_source_rgb(*NSKIN)
    rrect(c, -92, -96, 184, 200, 78)
    c.fill()
    c.save()
    rrect(c, -92, -96, 184, 200, 78)
    c.clip()
    c.set_source_rgba(0, 0, 0, 0.10)
    ell(c, 0, 124, 120, 36)
    c.fill()
    c.restore()
    c.set_source_rgb(*CREAM)
    for sx in (-1, 1):
        c.arc(sx * 94, 44, 7, 0, 2 * math.pi)
        c.fill()

    def wrap_path():
        c.new_sub_path()
        c.move_to(-104, -24)
        c.curve_to(-118, -120, -70, -176, 0, -178)
        c.curve_to(76, -180, 120, -124, 104, -24)
        c.curve_to(60, -46, -60, -46, -104, -24)
        c.close_path()

    c.set_source_rgb(*WRAP)
    wrap_path()
    c.fill()
    c.save()
    wrap_path()
    c.clip()
    c.set_source_rgba(*CREAM, 0.85)
    for row in range(7):
        for col in range(9):
            px = -120 + col * 30 + (15 if row % 2 else 0)
            py = -180 + row * 24
            c.move_to(px, py - 6)
            c.line_to(px + 6, py)
            c.line_to(px, py + 6)
            c.line_to(px - 6, py)
            c.close_path()
            c.fill()
    c.set_source_rgba(*DRESS, 0.9)
    for row in range(4):
        c.rectangle(-130, -150 + row * 34, 260, 5)
        c.fill()
    c.restore()
    c.set_source_rgb(*WRAP_D)
    ell(c, 58, -168, 40, 26)
    c.fill()
    c.set_source_rgb(*WRAP)
    ell(c, 30, -186, 30, 20)
    c.fill()
    bl = 0.08 if ((t + seed) % 3.9) < 0.13 else 1.0
    lx, ly = look
    for sx in (-1, 1):
        cx, cy = sx * 44, 4
        c.set_source_rgb(0.96, 0.95, 0.91)
        ell(c, cx + lx * 3, cy, 16, 17 * bl)
        c.fill()
        c.set_source_rgb(*INK)
        ell(c, cx + lx * 7, cy + 1 + ly * 5, 9, 9 * min(1, bl + 0.1))
        c.fill()
        c.set_source_rgb(1, 1, 1)
        ell(c, cx + lx * 7 - 3, cy - 3, 2.4, 2.4)
        c.fill()
        c.set_source_rgb(*INK)
        c.set_line_width(4)
        c.move_to(cx + sx * 14, cy - 12)
        c.line_to(cx + sx * 22, cy - 18)
        c.stroke()
    c.set_source_rgb(0.18, 0.11, 0.08)
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        c.move_to(sx * 22, -26 - (4 if mood == "soft" else 0))
        c.curve_to(sx * 34, -34, sx * 54, -34, sx * 66, -26 + (4 if mood == "soft" else 0))
        c.stroke()
    c.set_source_rgb(*NSKIN_D)
    ell(c, 0, 36, 16, 18)
    c.fill()
    c.set_source_rgb(*NSKIN)
    ell(c, -2, 30, 10, 11)
    c.fill()
    c.set_source_rgb(0.42, 0.17, 0.12)
    c.set_line_width(7)
    if mood == "smile":
        c.move_to(-26, 68)
        c.curve_to(-12, 86, 12, 86, 26, 68)
        c.stroke()
    elif mood == "soft":
        c.move_to(-18, 76)
        c.curve_to(-6, 80, 6, 80, 18, 76)
        c.stroke()
    else:
        c.move_to(-18, 74)
        c.curve_to(-6, 78, 6, 78, 18, 74)
        c.stroke()
    c.set_source_rgba(*NSKIN_L, 0.45)
    for sx in (-1, 1):
        ell(c, sx * 58, 52, 16, 11)
        c.fill()


def woman(c, t, x, feet, s=1.0, mood="neutral", look=(0, 0), tl=None, tr=None, walk=0.0, ph=0.0, bob=0.0,
          sit=False, arms=True):
    c.save()
    c.translate(x, feet)
    c.scale(s, s)
    if not sit:
        c.set_source_rgba(0, 0, 0, 0.25)
        ell(c, 0, 0, 120, 16)
        c.fill()
        for i, sx in enumerate((-1, 1)):
            sn = math.sin(ph + i * math.pi)
            dy = -14 * max(0.0, sn) * walk
            dx = 10 * sn * walk
            c.set_source_rgb(*NSKIN_D)
            rrect(c, sx * 30 - 15 + dx, -112 + dy, 30, 100, 14)
            c.fill()
            c.set_source_rgb(0.24, 0.19, 0.17)
            ell(c, sx * 34 + dx * 1.3, -10 + dy, 32, 15)
            c.fill()
        c.set_source_rgb(*DRESS_D)
        c.move_to(-98, -214)
        c.line_to(98, -214)
        c.line_to(134, -96)
        c.curve_to(60, -84, -60, -84, -134, -96)
        c.close_path()
        c.fill()
        c.set_source_rgb(*DRESS)
        c.move_to(-94, -214)
        c.line_to(94, -214)
        c.line_to(126, -106)
        c.curve_to(60, -96, -60, -96, -126, -106)
        c.close_path()
        c.fill()
    c.translate(0, bob)
    c.set_source_rgb(*DRESS_D)
    rrect(c, -96, -384, 192, 196, 62)
    c.fill()
    c.set_source_rgb(*DRESS)
    rrect(c, -91, -380, 182, 188, 58)
    c.fill()
    c.set_source_rgb(*NSKIN)
    c.move_to(-30, -382)
    c.line_to(30, -382)
    c.line_to(0, -334)
    c.close_path()
    c.fill()
    c.set_source_rgb(*DRESS_D)
    rrect(c, -91, -222, 182, 16, 6)
    c.fill()
    c.set_source_rgba(*CREAM, 0.5)
    for k in range(4):
        c.arc(-60 + k * 40, -300 + (k % 2) * 30, 5, 0, 2 * math.pi)
        c.fill()
    c.save()
    c.translate(0, -462)
    c.scale(0.95, 0.95)
    woman_head(c, t, mood, look, 1.3)
    c.restore()
    c.restore()
    sh = [(x - 76 * s, feet - 352 * s + bob * s), (x + 76 * s, feet - 352 * s + bob * s)]
    if arms:
        woman_arms(c, sh, s, x, feet, tl, tr)
    return sh


def woman_arms(c, sh, s, x, feet, tl=None, tr=None, which=(0, 1)):
    for i, (tg, sx) in enumerate(((tl, -1), (tr, 1))):
        if i not in which:
            continue
        if tg is None:
            tg = (x + sx * 108 * s, feet - 170 * s)
        arm(c, sh[i][0], sh[i][1], tg[0], tg[1], 108 * s, 108 * s, 52 * s, col=DRESS, out=sx, cold=DRESS_D,
            cuff=DRESS_D, skin=NSKIN, skin_l=NSKIN_L)


def soup_pot(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.25)
    ell(c, 0, 4, 120, 12)
    c.fill()
    c.set_source_rgb(*STEEL_D)
    rrect(c, -112, -120, 224, 120, 30)
    c.fill()
    c.set_source_rgb(*STEEL)
    rrect(c, -104, -116, 208, 104, 26)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.25)
    rrect(c, -84, -100, 14, 70, 7)
    c.fill()
    c.set_source_rgb(*STEEL_D)
    for sx in (-1, 1):
        rrect(c, sx * 112 - 22 + sx * 8, -100, 44, 18, 9)
        c.fill()
    c.set_source_rgb(*STEEL_D)
    ell(c, 0, -122, 118, 20)
    c.fill()
    c.set_source_rgb(*INK)
    rrect(c, -18, -152, 36, 26, 10)
    c.fill()
    c.restore()
    steam(c, x - 40 * s, y - 150 * s, t, 3.1, 2, 110 * s, 10 * s, 0.35)


def kettle_at(c, kx, ky, s, ang, t, glw=0.4, mirror=False):
    c.save()
    c.translate(kx, ky)
    c.rotate(ang)
    if mirror:
        c.scale(-1, 1)
    kettle(c, 0, 0, s, t, glw)
    c.restore()
    m = -1 if mirror else 1

    def wp(lx, ly):
        lx *= m * s
        ly *= s
        return kx + math.cos(ang) * lx - math.sin(ang) * ly, ky + math.sin(ang) * lx + math.cos(ang) * ly

    return wp(228, -246), wp(-222, -128)


def stream(c, p0, p1, t, a=1.0, wd=9):
    if a <= 0:
        return
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    mx = (p0[0] + p1[0]) / 2 + 3 * math.sin(t * 20)
    for w, al, col in ((wd + 4, 0.35, YEL_D), (wd, 0.95, TEA)):
        c.set_source_rgba(*col, al * a)
        c.set_line_width(w)
        c.move_to(*p0)
        c.curve_to(p0[0] + 18, p0[1] + 4, mx, p1[1] - 30, p1[0], p1[1])
        c.stroke()


def held_cup(c, hx, hy, s, t, tea=True, sa=1.0, side=1, tilt=0.0, glw=0.25, seed=0.0, body=YEL, rim=YEL_D):
    c.save()
    c.translate(hx, hy)
    c.rotate(tilt)
    cup(c, -side * 82 * s, 30 * s, s, t, False, glw=glw, tea=tea, body=body, rim=rim)
    c.restore()
    if sa > 0 and tea:
        steam(c, hx - side * 82 * s, hy - 82 * s, t, seed, 3, 150 * s, 14 * s, 0.5 * sa)


def thumb(c, hx, hy, s, skin=SKIN):
    c.set_source_rgb(*skin)
    ell(c, hx - 4 * s, hy - 14 * s, 16 * s, 11 * s)
    c.fill()


def lip_point(hx, hy, s, tilt, side=1):
    lx, ly = -side * 82 * s + 56 * s, 30 * s - 104 * s
    return hx + math.cos(tilt) * lx - math.sin(tilt) * ly, hy + math.sin(tilt) * lx + math.cos(tilt) * ly


WX, WY, WW, WH = 250, 170, 460, 370
TX0, TX1, TY = 770, 1190, 712
HERX, HISX = 870, 1090
MX, MHIPS, MS, MFLOOR = 1300, 742, 0.8, 895
CX0, CX1, CTOP = 1390, 1700, 640
KX = 1470
DX0, DX1, DY0 = 1745, 1905, 196
FLY = 880
ARMX = 600


def sill(c, x, y, w):
    c.set_source_rgb(*WALL_D)
    rrect(c, x, y + 6, w, 30, 8)
    c.fill()
    c.set_source_rgb(0.47, 0.53, 0.59)
    rrect(c, x - 4, y, w + 8, 16, 6)
    c.fill()


def clock(c, x, y, r, T):
    c.set_source_rgba(0, 0, 0, 0.25)
    c.arc(x + 4, y + 6, r + 8, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*WALL_D)
    c.arc(x, y, r + 8, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*mix(CREAM, WALL, 0.25))
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*INK)
    for k in range(12):
        a = k * math.pi / 6
        c.arc(x + 0.8 * r * math.cos(a), y + 0.8 * r * math.sin(a), 2.5, 0, 2 * math.pi)
        c.fill()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for ang, ln, wd in ((-2.2, 0.5, 6), (-0.6, 0.72, 4.5)):
        c.set_line_width(wd)
        c.move_to(x, y)
        c.line_to(x + ln * r * math.cos(ang), y + ln * r * math.sin(ang))
        c.stroke()
    sa = math.floor(T) * math.pi / 30 - math.pi / 2
    c.set_source_rgb(*hx("B4583A"))
    c.set_line_width(2.5)
    c.move_to(x, y)
    c.line_to(x + 0.82 * r * math.cos(sa), y + 0.82 * r * math.sin(sa))
    c.stroke()
    c.set_source_rgb(*INK)
    c.arc(x, y, 5, 0, 2 * math.pi)
    c.fill()


def counter(c, t, sink=True):
    c.set_source_rgb(*WALL_D)
    rrect(c, CX0, CTOP + 10, CX1 - CX0, FLY - CTOP - 6, 6)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.06)
    for k in range(2):
        rrect(c, CX0 + 18 + k * 150, CTOP + 36, 136, FLY - CTOP - 60, 6)
        c.fill()
    c.set_source_rgb(0.47, 0.53, 0.59)
    rrect(c, CX0 - 12, CTOP - 6, CX1 - CX0 + 24, 26, 8)
    c.fill()
    if sink:
        c.set_source_rgb(*STEEL_D)
        c.set_line_width(10)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(1640, CTOP - 4)
        c.line_to(1640, CTOP - 70)
        c.curve_to(1640, CTOP - 96, 1600, CTOP - 96, 1600, CTOP - 70)
        c.stroke()
        c.set_source_rgba(0, 0, 0, 0.3)
        rrect(c, 1560, CTOP - 2, 120, 10, 4)
        c.fill()


def shelf(c, ny=2):
    c.set_source_rgb(*WALL_D)
    rrect(c, CX0, 340, CX1 - CX0, 14, 6)
    c.fill()
    for xx in (1430, 1660):
        mug_dim(c, xx, 340, 0.5, hx("8E9BA8") if xx < 1500 else hx("9AA4AC"))
    for i, xx in enumerate((1515, 1580)):
        if i < ny:
            cup(c, xx, 340, 0.44, 0, False, glw=0.1, tea=False)
        else:
            c.set_source_rgba(0, 0, 0, 0.2)
            ell(c, xx, 338, 22, 4)
            c.fill()


def door(c, t, op=0.0, shake=0.0, sun=0.0, rain=1.0, outside=None):
    c.set_source_rgb(*WALL_D)
    rrect(c, DX0 - 18, DY0 - 18, DX1 - DX0 + 36, FLY - DY0 + 18, 10)
    c.fill()
    c.save()
    c.rectangle(DX0, DY0, DX1 - DX0, FLY - DY0)
    c.clip()
    vgrad(c, DX0, DY0, DX1 - DX0, FLY - DY0, mix(hx("7B8794"), hx("EFE3B0"), sun * 0.8), mix(SKY, hx("D9DDC6"), sun))
    c.set_source_rgb(*mix(hx("55606A"), hx("8E9878"), sun))
    c.rectangle(DX0, 760, DX1 - DX0, 200)
    c.fill()
    if outside:
        outside(c)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for fx, fy, ln, sp in RAIN_L[:40]:
        yy = (fy + t * sp * 0.55) % 1.0
        xx = DX0 + fx * (DX1 - DX0 + 60) - 30
        c.set_source_rgba(*RAIN, 0.45 * rain)
        c.set_line_width(2.5)
        c.move_to(xx, DY0 + yy * 760 - 60)
        c.line_to(xx - 12, DY0 + yy * 760 + 40)
        c.stroke()
    c.restore()
    pw = (DX1 - DX0) * (1 - 0.82 * ease(op))
    sx = math.sin(t * 70) * 3 * shake
    px0 = DX1 - pw + sx
    col = mix(hx("4F5B66"), INK, 0.15)
    c.set_source_rgb(*col)
    rrect(c, px0, DY0, pw, FLY - DY0, 4)
    c.fill()
    if pw > 30:
        c.set_source_rgba(1, 1, 1, 0.06)
        for k in range(2):
            rrect(c, px0 + pw * 0.14, DY0 + 40 + k * 330, pw * 0.72, 290, 6)
            c.fill()
        c.set_source_rgb(*CREAM)
        c.arc(px0 + pw * 0.14, 560, 9, 0, 2 * math.pi)
        c.fill()


def kchair(c, x, floor, s):
    c.save()
    c.translate(x, floor)
    c.scale(s, s)
    col = hx("3A3430")
    c.set_source_rgb(*col)
    rrect(c, -110, -420, 220, 30, 12)
    c.fill()
    for sx in (-1, 1):
        rrect(c, sx * 96 - 10, -420, 20, 420, 8)
        c.fill()
    for k in range(3):
        rrect(c, -60 + k * 50, -390, 14, 200, 6)
        c.fill()
    rrect(c, -120, -196, 240, 26, 10)
    c.fill()
    c.restore()


def table(c, t, cups, extra=None):
    c.set_source_rgba(0, 0, 0, 0.25)
    ell(c, (TX0 + TX1) / 2, FLY + 18, 260, 18)
    c.fill()
    c.set_source_rgb(0.16, 0.19, 0.23)
    for xx in (TX0 + 34, TX1 - 34):
        rrect(c, xx - 12, TY + 10, 24, FLY + 16 - TY - 10, 6)
        c.fill()
    c.set_source_rgb(0.22, 0.25, 0.29)
    rrect(c, TX0, TY, TX1 - TX0, 26, 8)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.06)
    rrect(c, TX0, TY, TX1 - TX0, 6, 3)
    c.fill()
    if extra:
        extra(c)
    for cp in cups:
        cup(c, cp["x"], TY + 2, cp.get("s", 0.5), t, cp.get("st", True), glw=cp.get("glw", 0.22), seed=cp.get("seed", 0),
            tea=cp.get("tea", True), sa=cp.get("sa", 1.0), body=cp.get("body", YEL), rim=cp.get("rim", YEL_D),
            sq=cp.get("sq", 0.0))


def room(c, t, P):
    sun = P.get("sun", 0.0)
    rn = P.get("rain", 1.0)
    wall_bg(c, P.get("dark", 0.0) * 0.4)
    floor_bg(c, FLY)
    if sun > 0:
        g = cairo.LinearGradient(WX, WY, WX + 300, FLY + 200)
        g.add_color_stop_rgba(0, *YEL, 0.0)
        g.add_color_stop_rgba(0.3, *YEL, 0.14 * sun)
        g.add_color_stop_rgba(1, *YEL, 0.03 * sun)
        c.set_source(g)
        c.move_to(WX, WY + WH)
        c.line_to(WX + WW, WY + WH)
        c.line_to(WX + WW + 520, H + 40)
        c.line_to(WX + 200, H + 40)
        c.close_path()
        c.fill()
    lamp(c, 130, FLY + 4, P.get("lamp", 1.0))
    window(c, t, WX, WY, WW, WH, sun, rn, behind=P.get("behind"))
    sill(c, WX - 30, WY + WH + 6, WW + 60)
    plant(c, WX + WW / 2, WY + WH + 8, 0.72, P.get("plant", 0.0), t)
    clock(c, 1010, 290, 46, P.get("clock", t))
    door(c, t, P.get("door", 0.0), P.get("knock", 0.0), sun, rn, P.get("outside"))
    counter(c, t)
    shelf(c, P.get("shelf", 0))
    if P.get("kettle", True):
        kettle(c, KX, CTOP - 4, 0.48, t, P.get("kglow", 0.3))
    if P.get("pot", False):
        soup_pot(c, 1600, CTOP - 4, 0.5, t)
    chair(c, ARMX, 900, 0.55, 420)
    chair_front(c, ARMX, 900, 0.55)
    if P.get("hischair", True):
        kchair(c, MX, MFLOOR + 4, 0.8)


def post(c, P):
    if P.get("sun", 0) > 0:
        glow(c, WX + WW * 0.6, WY + 120, 900, 0.14 * P["sun"], YEL)
        tint(c, YEL, 0.05 * P["sun"])
    if P.get("dark", 0) > 0:
        tint(c, (0.05, 0.06, 0.09), P["dark"])


def drink_target(u, d, rest, mouth):
    up = ease(seg(u, d[0], d[1]))
    down = ease(seg(u, d[2], d[3]))
    k = up * (1 - down)
    return (lerp(rest[0], mouth[0], k), lerp(rest[1], mouth[1], k)), k


HIS_REST = (HISX + 44, TY - 30)
HIS_MOUTH = (MX + 22, 584)


def him_at_table(c, t, mood, look, cups_her, his_cup=True, drink=0.0, tr=None, tl=None, bob=None, his_tea=True,
                 his_sa=1.0, glw=0.22, extra=None, behind_table=None):
    b = 1.5 * math.sin(t * 1.4) if bob is None else bob
    sh = man_sit(c, t, MX, MHIPS, MS, mood, look, seed=0.4, bob=b, floor=MFLOOR, arms=False)
    if behind_table:
        behind_table(c)
    table(c, t, cups_her, extra)
    sit_arms(c, sh, MS, MX, MHIPS, tr=tr, which=(1,))
    if his_cup:
        hp = (lerp(HIS_REST[0], HIS_MOUTH[0], drink), lerp(HIS_REST[1], HIS_MOUTH[1], drink))
        sit_arms(c, sh, MS, MX, MHIPS, tl=hp if tl is None else tl, which=(0,))
        if tl is None:
            held_cup(c, hp[0], hp[1], 0.5, t, his_tea, his_sa * (1 - drink), 1, -0.15 * drink, glw)
            thumb(c, hp[0], hp[1], 0.5)
        if tl is not None:
            cup(c, HISX, TY + 2, 0.5, t, True, glw=glw, tea=his_tea, sa=his_sa)
    else:
        sit_arms(c, sh, MS, MX, MHIPS, tl=tl, which=(0,))
    return sh


def cold_hand(c, x, y, side, sk=1.0):
    c.save()
    c.translate(x, y)
    c.scale(sk, sk)
    c.translate(-x, -y)
    c.set_source_rgb(*SKIN)
    ell(c, x, y, 38, 50)
    c.fill()
    for k in range(3):
        c.set_source_rgb(*SKIN)
        rrect(c, x - side * 82 - 6 if side > 0 else x + 4, y - 40 + k * 28, 88, 24, 12)
        c.fill()
        c.set_source_rgba(*SKIN_D, 0.5)
        c.set_line_width(2)
        yy = y - 16 + k * 28
        c.move_to(x - side * 10, yy)
        c.line_to(x - side * 76, yy)
        c.stroke()
    c.set_source_rgb(*SKIN_L)
    c.save()
    c.translate(x - side * 46, y - 50)
    c.rotate(side * 0.25)
    ell(c, 0, 0, 34, 12)
    c.fill()
    c.restore()
    c.restore()


def cold_draw(c, t, mood, look, sq_t=0.0):
    wall_bg(c)
    window(c, t, 1210, 280, 520, 400, 0.0, 0.9)
    glow(c, 1000, 800, 700, 0.18, YEL)
    c.set_source_rgb(0.20, 0.235, 0.27)
    c.rectangle(-100, 805, W + 200, 400)
    c.fill()
    c.set_source_rgb(0.27, 0.31, 0.35)
    c.rectangle(-100, 805, W + 200, 18)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.05)
    c.rectangle(-100, 823, W + 200, 6)
    c.fill()
    mx = 540
    bob = 3 * math.sin(t * 1.6)
    c.save()
    c.translate(mx, 1410)
    c.scale(2.15, 2.15)
    c.translate(0, bob / 2.15)
    torso(c)
    c.translate(0, -470 + 8)
    head(c, t, mood, look, 0.9)
    c.restore()
    c1x, c2x, cy = 905, 1150, 872
    land = seg(sq_t, 0.0, 0.14)
    lift2 = 22 * (1 - ease(land))
    sq = pulse(sq_t, 0.0, 0.2)
    hl = (c1x - 66, cy - 52)
    hr = (c2x + 122, cy - 62 - lift2)
    shl = (mx - 80 * 2.15, 1410 - 352 * 2.15 + bob)
    shr = (mx + 80 * 2.15, 1410 - 352 * 2.15 + bob)
    arm(c, shr[0], shr[1], hr[0] - 10, hr[1] + 30, 0, 0, 120, out=1, hand=False, elbow=(shr[0] + 120, 1010))
    arm(c, shl[0], shl[1], hl[0] - 14, hl[1] + 30, 0, 0, 120, out=-1, hand=False, elbow=(shl[0] + 70, 1020))
    cup(c, c1x, cy, 1.18, t, True, sq=0, seed=0.0)
    cup(c, c2x, cy - lift2, 1.18, t, True, sq=sq, seed=1.7)
    cold_hand(c, hl[0], hl[1], -1)
    cold_hand(c, hr[0], hr[1], 1)


def scene_cold(c, t):
    c.save()
    if t < COLD_B:
        z = 1 + 0.035 * t / 6
        cam(c, z, W / 2, H / 2)
        cold_draw(c, t, "neutral" if t < 1.6 else "tired", (0.55 * seg(t, 0.3, 1.0), 0.7 * seg(t, 0.3, 1.0)), t)
    else:
        u = t - COLD_B
        cam(c, 1.16 + 0.02 * u, 800, 585)
        cold_draw(c, t, "sad", (0.9, 0.85), t)
    c.restore()
    vignette(c, 0.3)
    tag(c, "DAY 40")
    big_two(c, t)
    caption(c, t, "I still make two cups.", 0.4, 5.85)


def card_rain(c, t, a=0.1):
    c.save()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for fx, fy, ln, sp in RAIN_L:
        yy = (fy + t * sp * 0.5) % 1.0
        xx = fx * (W + 200) - 100 + yy * 120
        c.set_source_rgba(*RAIN, a)
        c.set_line_width(2.5)
        c.move_to(xx, yy * (H + 200) - 100)
        c.line_to(xx - 30, yy * (H + 200) - 100 + 150 * ln * 2 + 40)
        c.stroke()
    c.restore()


def scene_card(c, t):
    vgrad(c, 0, 0, W, H, SLATE_N, mix(SLATE_N, INK, 0.5))
    card_rain(c, t + 6, 0.12)
    k = 1.0
    text(c, "40 days earlier.", W / 2, H / 2 + 28, 108, CREAM, k)
    c.set_source_rgba(*YEL, 0.9 * k)
    rrect(c, W / 2 - 60, H / 2 + 80, 120, 6, 3)
    c.fill()
    vignette(c, 0.4)


def kettle_shot(c, t, sun=0.0, rain=0.8):
    wall_bg(c, 0.04 - 0.06 * sun)
    window(c, t, 1260, 170, 520, 420, sun, rain)
    c.set_source_rgb(0.17, 0.20, 0.24)
    c.rectangle(0, 800, W, 300)
    c.fill()
    c.set_source_rgb(0.24, 0.27, 0.31)
    c.rectangle(0, 800, W, 22)
    c.fill()
    cx = 900
    glow(c, cx, 700, 600, 0.28, YEL)
    boil = seg(t, 0, 2.2)
    for i in range(7):
        fx = cx - 150 + i * 50
        fl = 40 + 14 * math.sin(t * 14 + i * 2)
        c.set_source_rgba(*YEL, 0.95)
        c.new_sub_path()
        c.move_to(fx - 16, 830)
        c.curve_to(fx - 14, 830 - fl, fx, 830 - fl - 20, fx, 830 - fl - 24)
        c.curve_to(fx, 830 - fl - 20, fx + 14, 830 - fl, fx + 16, 830)
        c.close_path()
        c.fill()
    c.set_source_rgb(*INK)
    rrect(c, cx - 290, 800, 580, 36, 12)
    c.fill()
    c.set_source_rgba(*YEL, 0.35)
    rrect(c, cx - 250, 800, 500, 10, 5)
    c.fill()
    kettle(c, cx, 805, 2.15, t, 1.0, shake=0.4 * boil)
    sx = cx + 2.15 * 225
    steam(c, sx + 10, 290, t, 0.5, 4, 360, 30, 0.55 * (0.4 + 0.6 * boil))
    steam(c, sx - 20, 330, t + 1.3, 2.5, 3, 300, 26, 0.35)
    for k in range(5):
        c.set_source_rgba(*CREAM, 0.5 * boil)
        c.set_line_width(7)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        a0 = -0.9 + k * 0.3
        c.move_to(sx + 40 + 30 * math.cos(a0 * 1.2), 430 + 60 * math.sin(a0) - 30)
        c.line_to(sx + 40 + 70 * math.cos(a0 * 1.2), 430 + 110 * math.sin(a0) - 30)
        c.stroke()
    he = ease(seg(t, 2.0, 2.7))
    if he > 0:
        arm(c, -200, 1080 + 200 * (1 - he), lerp(-100, 592, he), lerp(700, 690, he), 300, 300, 124, out=-1)
    if sun > 0:
        tint(c, YEL, 0.05 * sun)
    vignette(c, 0.32)


def shelf_shot(c, t, mode="two", sun=0.0, rain=0.7):
    wall_bg(c, 0.03 - 0.05 * sun)
    window(c, t, 1380, 90, 440, 320, sun, rain)
    glow(c, 960, 520, 700, 0.15, YEL)
    c.set_source_rgb(*WALL_D)
    rrect(c, -60, 620, W + 120, 40, 8)
    c.fill()
    c.set_source_rgba(0, 0, 0, 0.35)
    c.rectangle(-60, 660, W + 120, 26)
    c.fill()
    for sx in (260, 1660):
        c.set_source_rgb(*WALL_D)
        c.new_sub_path()
        c.move_to(sx - 20, 660)
        c.line_to(sx + 20, 660)
        c.line_to(sx, 740)
        c.close_path()
        c.fill()
    cols = [hx("8E9BA8"), hx("A8B0B4"), hx("7C8A9A"), hx("9AA4AC")]
    for i, xx in enumerate([180, 420, 650, 1280, 1500, 1730]):
        mug_dim(c, xx, 622, 1.35, cols[i % 4])
    take = D1_TAKE if mode == "two" else D90_TAKE
    drop = 330
    res = []
    for idx, (cc, side) in enumerate((((850, 622), -1), ((1090, 622), 1))):
        a, b = take[idx]
        p = seg(t, a, b)
        pre = ease(seg(t, a - 0.6, a))
        dn = ease(seg(p, 0.35, 1.0))
        hop = 50 * pulse(p, 0.0, 0.35)
        y = cc[1] + drop * dn - hop
        back = 0.0
        rel = 0.0
        if mode == "back" and idx == 1:
            back = ease(seg(t, D90_BACK[0], D90_BACK[1]))
            rel = ease(seg(t, D90_BACK[1] + 0.1, D90_BACK[1] + 0.8))
            y = lerp(y, cc[1], back)
        if mode == "back" and idx == 0:
            gone = ease(seg(t, 6.6, 7.6))
            y += 600 * gone
        sq = pulse(t, D90_BACK[1] - 0.05, 0.2) if (mode == "back" and idx == 1) else 0.0
        cup(c, cc[0], y, 1.45, t, False, sq, 1.3 * idx, 0.3 if back < 0.99 else 0.12, tea=False)
        gx = cc[0] + side * 100
        gy = lerp(1250, cc[1] - 56, pre) + (y - cc[1])
        if rel > 0:
            gx += side * 160 * rel
            gy = lerp(gy, 1300, rel)
        res.append((gx, gy, side, cc))
    for gx, gy, side, cc in res:
        arm(c, cc[0] + side * 520, 1260, gx, gy, 420, 420, 130, out=side)
    if sun > 0:
        tint(c, YEL, 0.05 * sun)
    vignette(c, 0.32)


def pour_shot(c, t, xs, pours, sun=0.0, rain=0.7):
    wall_bg(c, 0.02 - 0.05 * sun)
    window(c, t, 1300, 110, 460, 330, sun, rain)
    c.set_source_rgb(0.17, 0.20, 0.24)
    c.rectangle(0, 820, W, 300)
    c.fill()
    c.set_source_rgb(0.24, 0.27, 0.31)
    c.rectangle(0, 820, W, 22)
    c.fill()
    glow(c, 1000, 700, 700, 0.2, YEL)
    cs = 1.25
    ctop = 830 - 104 * cs
    ks, pa = 0.9, 0.62
    rest = (330, 830)
    tipoff = (math.cos(pa) * 228 * ks + math.sin(pa) * 246 * ks, math.sin(pa) * 228 * ks - math.cos(pa) * 246 * ks)
    K = rest
    ang = 0.0
    pouring = None
    seq = [rest]
    for (a, b), i in zip(pours, range(len(pours))):
        seq.append((xs[i] - 18 - tipoff[0], ctop - 70 - tipoff[1]))
    kx, ky = rest
    prev = rest
    for i, (a, b) in enumerate(pours):
        tgt = seq[i + 1]
        mv = ease(seg(t, a - 0.6, a))
        if t >= a - 0.6:
            kx, ky = lerp(prev[0], tgt[0], mv), lerp(prev[1], tgt[1], mv)
            ang = pa * ease(seg(t, a - 0.2, a + 0.15)) * (1 - ease(seg(t, b - 0.15, b + 0.2)))
            if a <= t <= b:
                pouring = i
        prev = tgt
    if t > pours[-1][1] + 0.2:
        r = ease(seg(t, pours[-1][1] + 0.3, pours[-1][1] + 1.1))
        kx, ky = lerp(prev[0], rest[0], r), lerp(prev[1], rest[1], r)
    for i, x in enumerate(xs):
        full = t > (pours[i][0] + pours[i][1]) / 2
        cup(c, x, 830, cs, t, full, 0, 1.1 * i, 0.32, tea=full, sa=ease(seg(t, pours[i][1], pours[i][1] + 1.0)))
    tip, hnd = kettle_at(c, kx, ky, ks, ang, t, 0.25)
    if pouring is not None:
        a, b = pours[pouring]
        k = seg(t, a, a + 0.15) * (1 - seg(t, b - 0.15, b))
        stream(c, tip, (xs[pouring] - 4, ctop - 6), t, k, 11)
    arm(c, -260, 240, hnd[0] - 10, hnd[1] + 6, 330, 330, 120, out=-1)
    if sun > 0:
        tint(c, YEL, 0.05 * sun)
    vignette(c, 0.32)


def her_cup_shot(c, t):
    wall_bg(c, 0.05)
    window(c, t, 140, 120, 560, 420, 0.0, 0.9)
    c.set_source_rgb(*FLOOR)
    c.rectangle(0, 880, W, 200)
    c.fill()
    chair(c, 560, 1010, 1.05, 420)
    chair_front(c, 560, 1010, 1.05)
    lamp(c, 1000, 950, 0.6)
    c.set_source_rgba(*WALL_D, 0.35)
    c.paint()
    c.set_source_rgb(0.22, 0.25, 0.29)
    rrect(c, 820, 840, 1200, 300, 16)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.06)
    rrect(c, 820, 840, 1200, 8, 4)
    c.fill()
    sa = 1 - ease(seg(t, D1_STEAM[0], D1_STEAM[1]))
    cup(c, 1240, 860, 1.7, t, True, glw=0.18 + 0.2 * sa, seed=0.7, sa=sa)
    vignette(c, 0.36)


def scene_day1(c, t):
    s = 0
    for i, a in enumerate(D1):
        if t >= a:
            s = i
    u = t - D1[s]
    bump = 0.0
    if s == 0:
        kettle_shot(c, u)
    elif s == 1:
        shelf_shot(c, u, "two")
        bump = pulse(u, D1_TAKE[0][1], 0.4) + pulse(u, D1_TAKE[1][1], 0.4)
    elif s == 2:
        P = dict(plant=0.0, rain=1.0, shelf=0)
        c.save()
        cam(c, 1.06, 1010, 560)
        room(c, t, P)
        table(c, t, [dict(x=HERX, tea=False, st=False), dict(x=HISX, tea=False, st=False, seed=1.2)])
        raise_k = ease(seg(u, 0.7, 1.3)) * (1 - ease(seg(u, 2.5, 3.3)))
        mood = "neutral" if u < 0.7 else ("surprised" if u < 2.4 else "sad")
        look = (-0.3, 0.5) if u < 0.6 else ((-1.0, -0.1) if u < 2.6 else (-0.6, 0.8))
        man(c, t, 1590, 905, 0.86, mood, look, tl=(lerp(1490, 1420, raise_k), lerp(760, 610, raise_k)),
            seed=0.4, bob=1.5 * math.sin(t * 1.5))
        post(c, P)
        c.restore()
        vignette(c, 0.35)
    elif s == 3:
        pour_shot(c, u, [820, 1180], D1_POUR)
    else:
        her_cup_shot(c, u)
    tag(c, "DAY 1")
    meter(c, 2, 1.0, bump)
    caption(c, t, "Day 1.", 0.3, 3.85)
    caption(c, t, "The house is too quiet.", 9.0, 12.9)


def scene_days(c, t):
    i = min(5, int(t / DAYS_STEP))
    d = i + 2
    u = t - i * DAYS_STEP
    P = dict(plant=0.0, rain=1.0, dark=[0.0, 0.08, 0.03, 0.1, 0.05, 0.12][i], lamp=[1, 0.6, 1, 0.5, 1, 0.4][i])
    c.save()
    if i % 2 == 0:
        cam(c, 1.12, 920, 560)
    else:
        cam(c, 1.75, 1080, 540)
    room(c, t, P)
    dk = drink_target(u, DAYS_DRINK, (0, 0), (1, 1))[1]
    sq = pulse(u, DAYS_DRINK[3], 0.2)
    moods = ["neutral", "tired", "sad", "tired", "neutral", "tired"]
    look = (-0.9, 0.4) if u > DAYS_DRINK[3] + 0.1 else (0.2, 0.3)
    him_at_table(c, t, moods[i], look, [dict(x=HERX, seed=0.3)], drink=dk)
    post(c, P)
    c.restore()
    vignette(c, 0.35)
    tag(c, "DAY %d" % d, pulse(u, 0.0, 0.45) if i > 0 else 0.0)
    meter(c, 2)


def plant_shot(c, t, state, sun=0.0, rain=1.0, who=True, tilt=0.0, hand=None, pour=0.0, mood="neutral",
               look=(1.0, 0.3), behind=None, dark=0.0):
    wall_bg(c, 0.02 + dark * 0.4 - 0.05 * sun)
    window(c, t, 780, 110, 760, 600, sun, rain, behind=behind)
    sill(c, 740, 716, 840)
    c.set_source_rgb(*mix(WALL, WALL_D, 0.3))
    c.rectangle(0, 760, W, 400)
    c.fill()
    c.set_source_rgb(*WALL_D)
    c.rectangle(0, 752, W, 12)
    c.fill()
    plant(c, 1160, 724, 1.2, state, t)
    if who:
        hp = hand or (880, 860)
        sh = man(c, t, 640, 1250, 1.45, mood, look, seed=0.2, bob=1.5 * math.sin(t * 1.4), arms=False)
        man_arms(c, sh, 1.45, None, None, 640, 1250 - 160 * 1.45, 112, which=(0,))
        man_arms(c, sh, 1.45, None, hp, 640, 1250 - 160 * 1.45, 124, which=(1,))
        held_cup(c, hp[0], hp[1], 1.0, t, True, 0.0, -1, tilt, 0.28)
        if pour > 0:
            lp = lip_point(hp[0], hp[1], 1.0, tilt, -1)
            stream(c, lp, (lp[0] + 30, 600), t, pour, 10)
        thumb(c, hp[0] + 16, hp[1] - 6, 1.6)
    if sun > 0:
        tint(c, YEL, 0.05 * sun)
    if dark > 0:
        tint(c, (0.05, 0.06, 0.09), dark)
    vignette(c, 0.34)


def pour_plant(c, t, st0, st1, pr, grow, mood="neutral", sun=0.0, rain=1.0):
    up = ease(seg(t, pr[0] - 2.0, pr[0] - 0.5))
    tl = ease(seg(t, pr[0] - 0.5, pr[0] + 0.2)) * (1 - ease(seg(t, pr[1], pr[1] + 0.6)))
    hand = (lerp(880, 975, up), lerp(880, 450, up))
    pk = seg(t, pr[0] + 0.1, pr[0] + 0.3) * (1 - seg(t, pr[1] - 0.3, pr[1]))
    state = lerp(st0, st1, grow(t))
    plant_shot(c, t, state, sun, rain, True, 1.0 * tl, hand, pk, mood, (1.0, 0.4))


def scene_day8(c, t):
    P = dict(plant=0.0, rain=1.0)
    if t < D8_B:
        u = t
        c.save()
        cam(c, 1.12, 1060, 560)
        room(c, t, P)
        wk = ease(seg(u, D8_WALK[0], D8_WALK[1]))
        x = lerp(960, 1560, wk)
        walking = 1.0 if D8_WALK[0] < u < D8_WALK[1] else 0.0
        lift = ease(seg(u, D8_LIFT[0], D8_LIFT[1]))
        mood = "sad" if u < 3.6 else "neutral"
        look = (-0.4, 0.7) if u < 1.4 else ((0.9, 0.2) if u < 3.6 else (-1.0, -0.1))
        cups = [dict(x=HISX, seed=1.1, st=True)]
        if lift <= 0:
            cups.append(dict(x=HERX, st=False, glw=0.1))
        sh = man(c, t, x, 905, 0.86, mood, look, seed=0.4, bob=2.5 * walking * abs(math.sin(u * 6)), walk=walking,
                 ph=u * 12, arms=False)
        table(c, t, cups)
        man_arms(c, sh, 0.86, None, None, x, 905 - 160 * 0.86, which=(1,))
        if lift > 0:
            hp = (lerp(HERX + 44, x - 110, lift), lerp(TY - 30, 640, lift))
            held_cup(c, hp[0], hp[1], 0.5, t, True, 0.0, 1, 0.0, 0.1)
            man_arms(c, sh, 0.86, hp, None, x, 905 - 160 * 0.86, which=(0,))
        else:
            reach = ease(seg(u, 0.1, D8_LIFT[0]))
            man_arms(c, sh, 0.86, (lerp(x - 100, HERX + 44, reach), lerp(760, TY - 30, reach)), None, x,
                     905 - 160 * 0.86, which=(0,))
        post(c, P)
        c.restore()
        vignette(c, 0.35)
    else:
        u = t - D8_B
        pour_plant(c, u, 0.0, 0.1, D8_POUR, lambda v: ease(seg(v, D8_POUR[1] - 0.4, D8_POUR[1] + 1.2)),
                   "neutral" if u < D8_POUR[1] + 0.6 else "sad")
    tag(c, "DAY 8")
    meter(c, 2)
    caption(c, t, "Day 8.", 0.3, 3.6)
    caption(c, t, "She loved this plant.", D8_B + 3.4, D8_B + 8.6)


def scene_day14(c, t):
    s = 0
    for i, a in enumerate(D14):
        if t >= a:
            s = i
    u = t - D14[s]
    P = dict(plant=0.2, rain=1.0)
    knock = sum(pulse(t, k, 0.18) for k in D14_KNOCK)
    NX = 1000
    hercup = dict(x=815, seed=0.3)
    mug = dict(x=1010, body=GREY, rim=GREY_D, glw=0.0, tea=False, st=False, seed=2.0)
    hisc = dict(x=1165, seed=1.1)
    tp = [905, TY + 2, 0.0]

    def teapot(cc):
        kettle_at(cc, tp[0], tp[1], 0.3, tp[2], t, 0.12)

    c.save()
    if s == 0:
        cam(c, 1.05, 1000, 560)
        P["knock"] = knock
        room(c, t, P)
        look = (0.2, 0.4) if t < 0.8 else (1.0, -0.1)
        sh = man_sit(c, t, MX, MHIPS, MS, "neutral" if t < 0.8 else "surprised", look, seed=0.4, floor=MFLOOR,
                     arms=False)
        table(c, t, [hercup, mug, hisc], teapot)
        sit_arms(c, sh, MS, MX, MHIPS, tl=(HISX + 30, TY - 20))
    elif s == 1:
        cam(c, 1.6, 1500, 560)
        P["door"] = seg(u, D14_DOOR[0], D14_DOOR[1])
        wk = ease(seg(u, D14_WALK[0], D14_WALK[1]))
        setk = ease(seg(u, D14_SET[0], D14_SET[1]))
        P["pot"] = setk >= 1
        room(c, t, P)
        sh = man_sit(c, t, MX, MHIPS, MS, "surprised" if u < 2.4 else "neutral", (1.0, -0.1), seed=0.4, floor=MFLOOR,
                     arms=False)
        table(c, t, [hercup, mug, hisc], teapot)
        sit_arms(c, sh, MS, MX, MHIPS, tl=(HISX + 30, TY - 20))
        wx = lerp(1825, 1600, wk)
        walking = 1.0 if D14_WALK[0] < u < D14_WALK[1] else 0.0
        py = lerp(800, CTOP - 4, setk)
        px = wx
        sh2 = woman(c, t, wx, 905, 0.8, "soft" if u > 2.5 else "neutral", (-0.8, 0.1), walk=walking, ph=u * 11,
                    bob=2 * walking * abs(math.sin(u * 5.5)), arms=False)
        if setk < 1:
            soup_pot(c, px, py, 0.5, t)
            woman_arms(c, sh2, 0.8, wx, 905, (px - 64, py - 46), (px + 64, py - 46))
        else:
            woman_arms(c, sh2, 0.8, wx, 905)
    elif s == 2:
        cam(c, 1.7, 1010, 560)
        P["pot"] = True
        room(c, t, P)
        sh = man_sit(c, t, MX, MHIPS, MS, "neutral", (-1.0, -0.2), seed=0.4, floor=MFLOOR, arms=False)
        lk = (-0.9, 0.9) if u < 1.4 else ((0.9, 0.9) if u < 2.6 else (-0.3, 0.8))
        sh2 = woman(c, t, NX, 905, 0.8, "soft", lk, arms=False)
        lift = ease(seg(u, D14_POUR[0] - 0.4, D14_POUR[0])) * (1 - ease(seg(u, D14_POUR[1], D14_POUR[1] + 0.4)))
        tilt = ease(seg(u, D14_POUR[0], D14_POUR[0] + 0.3)) * (1 - ease(seg(u, D14_POUR[1] - 0.3, D14_POUR[1])))
        tp[0], tp[1], tp[2] = lerp(905, 902, lift), lerp(TY + 2, 652, lift), 0.6 * tilt
        full = u > (D14_POUR[0] + D14_POUR[1]) / 2
        mug["tea"] = full
        mug["st"] = full
        table(c, t, [hercup, mug, hisc])
        tip, hnd = kettle_at(c, tp[0], tp[1], 0.3, tp[2], t, 0.12)
        if tilt > 0.6:
            stream(c, tip, (1012, TY + 2 - 50), t, tilt, 6)
        sit_arms(c, sh, MS, MX, MHIPS, tl=(HISX + 30, TY - 20))
        reach = ease(seg(u, D14_POUR[0] - 1.0, D14_POUR[0] - 0.4)) * (1 - ease(seg(u, D14_POUR[1] + 0.4, D14_POUR[1] + 1.0)))
        woman_arms(c, sh2, 0.8, NX, 905, (lerp(930, hnd[0], reach), lerp(TY - 4, hnd[1] + 4, reach)), (1070, TY - 4))
    else:
        cam(c, 1.3, 1010, 560)
        P["pot"] = True
        room(c, t, P)
        sh = man_sit(c, t, MX, MHIPS, MS, "neutral" if u < 1.5 else "tired", (-1.0, 0.2), seed=0.4, floor=MFLOOR,
                     arms=False)
        sh2 = woman(c, t, NX, TY + 190 * 0.8, 0.8, "soft", (0.9, 0.3) if u < 2.5 else (-0.5, 0.6), sit=True,
                    arms=False)
        mug["tea"] = True
        mug["st"] = True
        table(c, t, [hercup, mug, hisc], teapot)
        sit_arms(c, sh, MS, MX, MHIPS, tl=(HISX + 44, TY - 30))
        woman_arms(c, sh2, 0.8, NX, 905, (972, TY - 22), (1056, TY - 22))
    post(c, P)
    c.restore()
    vignette(c, 0.35)
    tag(c, "DAY 14")
    meter(c, 2)
    caption(c, t, "Someone sat in the quiet with me.", 14.2, 19.7)


def scene_day30(c, t):
    P = dict(plant=0.3, rain=1.7, dark=0.3, lamp=0.0, clock=t + 4)
    c.save()
    if t < D30_B:
        cam(c, 1.0 + 0.012 * t, 960, 560)
    else:
        cam(c, 1.75 + 0.01 * (t - D30_B), 1010, 540)
    room(c, t, P)
    him_at_table(c, t, "tired", (-1.0, 0.25), [dict(x=HERX, st=False, glw=0.12)], drink=0.0, his_sa=0.0,
                 glw=0.12, bob=0.8 * math.sin(t * 0.9))
    post(c, P)
    c.restore()
    vignette(c, 0.45)
    tag(c, "DAY 30")
    meter(c, 2)


def center_sit(c, t, P, dn, mood, look):
    room(c, t, P)
    b = 1.5 * math.sin(t * 1.4)
    kchair(c, 980, MFLOOR + 4, 0.8)
    sh = man_sit(c, t, 980, 770, MS, mood, look, seed=0.4, bob=b, floor=MFLOOR, arms=False)
    lift = 46 * (1 - dn)
    sq = pulse(t, D40_SET - 0.05, 0.2)
    table(c, t, [])
    sit_arms(c, sh, MS, 980, 770, tl=(818, TY - 30 - lift), tr=(1176, TY - 34 - lift), alen=125, side=True)
    cup(c, 860, TY + 2 - lift, 0.62, t, True, 0, 0.0, 0.25, sa=0.7)
    cup(c, 1100, TY + 2 - lift, 0.62, t, True, sq, 1.7, 0.25, sa=0.7)
    cold_hand(c, 822, TY - 34 - lift, -1, 0.5)
    cold_hand(c, 1172, TY - 38 - lift, 1, 0.5)


def scene_day40(c, t):
    if t < D40_B:
        P = dict(plant=0.4, rain=1.1, dark=0.12, lamp=0.6, hischair=False)
        c.save()
        cam(c, 1.3, 900, 560)
        dn = ease(seg(t, 0.0, D40_SET))
        center_sit(c, t, P, dn, "tired" if t < 3.2 else "sad", (0.0, 0.8) if t < 3.2 else (-1.0, -0.2))
        post(c, P)
        c.restore()
        vignette(c, 0.35)
    else:
        u = t - D40_B
        pour_plant(c, u, 0.4, 0.5, D40_POUR, lambda v: seg(v, D40_POP, D40_POP + 0.5),
                   "tired" if u < D40_POP else "neutral", rain=1.0)
        tint(c, (0.05, 0.06, 0.09), 0.08)
    tag(c, "DAY 40")
    meter(c, 2)


def neighbour_out(t, x, feet, s, wave):
    def f(c):
        c.set_source_rgba(*mix(hx("55606A"), SKY, 0.4), 1)
        c.rectangle(0, feet - 160 * s, W, 400)
        c.fill()
        sh = woman(c, t, x, feet, s, "smile", (-1.0, 0.1), arms=False)
        wv = math.sin(t * 9) * wave
        woman_arms(c, sh, s, x, feet, None, (x + 150 * s + 30 * wv, feet - 520 * s), )
        c.set_source_rgb(*mix(WRAP, INK, 0.2))
        c.set_line_width(5)
        c.move_to(x - 70 * s, feet - 330 * s)
        c.line_to(x - 70 * s, feet - 700 * s)
        c.stroke()
        c.set_source_rgb(*WRAP)
        c.move_to(x - 290 * s, feet - 640 * s)
        c.curve_to(x - 270 * s, feet - 820 * s, x + 130 * s, feet - 820 * s, x + 150 * s, feet - 640 * s)
        c.close_path()
        c.fill()
        c.set_source_rgba(*CREAM, 0.6)
        for k in range(4):
            c.arc(x - 240 * s + k * 110 * s, feet - 650 * s, 6, 0, 2 * math.pi)
            c.fill()
    return f


def scene_day60(c, t):
    s = 0
    for i, a in enumerate(D60):
        if t >= a:
            s = i
    u = t - D60[s]
    P = dict(plant=0.75, rain=0.45, dark=0.0, lamp=0.5)
    if s == 0:
        c.save()
        cam(c, 1.1, 900, 560)
        room(c, t, P)
        him_at_table(c, t, "neutral", (-0.9, 0.0), [dict(x=HERX, seed=0.3)], drink=0.0)
        post(c, P)
        c.restore()
        vignette(c, 0.33)
    elif s == 1:
        wv = ease(seg(u, 1.4, 2.0))
        ent = ease(seg(u, 0.0, 1.4))
        plant_shot(c, t, 0.75, 0.15, 0.45, False, behind=neighbour_out(t, lerp(1720, 1360, ent), 890, 0.9, wv))
    else:
        c.save()
        cam(c, 1.9, 1210, 500)
        room(c, t, P)
        wv = ease(seg(u, 0.8, 1.4)) * (1 - ease(seg(u, 5.4, 6.2)))
        mood = "neutral" if u < 1.3 else "smile"
        wvx = math.sin(u * 8) * 18 * wv
        him_at_table(c, t, mood, (-1.0, -0.3), [dict(x=HERX, seed=0.3)], drink=0.0,
                     tr=None, tl=(lerp(HISX + 44, 1150 + wvx, wv), lerp(TY - 30, 430, wv)))
        post(c, P)
        c.restore()
        vignette(c, 0.33)
    tag(c, "DAY 60")
    meter(c, 2)


def day90_sit(c, t, u):
    wall_bg(c, -0.02)
    floor_bg(c, 900)
    c.set_source_rgba(*POT, 0.55)
    ell(c, 640, 930, 520, 70)
    c.fill()
    window(c, t, 1100, 250, 560, 440, 1.0, 0.0)
    c.set_source_rgb(*WALL_D)
    rrect(c, 1060, 688, 640, 36, 8)
    c.fill()
    c.set_source_rgb(0.47, 0.53, 0.59)
    rrect(c, 1056, 684, 648, 16, 6)
    c.fill()
    g = cairo.LinearGradient(1300, 350, 700, 900)
    g.add_color_stop_rgba(0, *YEL, 0.0)
    g.add_color_stop_rgba(0.2, *YEL, 0.20)
    g.add_color_stop_rgba(1, *YEL, 0.04)
    c.set_source(g)
    c.move_to(1100, 690)
    c.line_to(1660, 690)
    c.line_to(900, 1080)
    c.line_to(160, 1080)
    c.close_path()
    c.fill()
    lamp(c, 150, 905, 0.3)
    plant(c, 1380, 684, 1.0, 1.0, t)
    chair(c, 640, 935, 1.0, 640)
    chair_seat(c, 640, 935, 1.0)
    s = 0.94
    b = 1.5 * math.sin(t * 1.3)
    dk = ease(seg(u, D90_DRINK[0], D90_DRINK[0] + 0.7)) * (1 - ease(seg(u, D90_DRINK[1], D90_DRINK[1] + 0.7)))
    mood = "smile" if dk < 0.5 else "neutral"
    look = (0.6, 0.3) if u < 5.2 else (1.0, -0.2)
    sh = man_sit(c, t, 640, 800, s, mood, look, seed=0.3, bob=b, floor=925, arms=False)
    chair_arms(c, 640, 935, 1.0, ax=150)
    sit_arms(c, sh, s, 640, 800, tl=(500, 668), which=(0,), alen=110)
    hp = (lerp(790, 668, dk), lerp(668, 566, dk))
    held_cup(c, hp[0], hp[1], 0.62, t, True, 1 - dk, 1, -0.45 * dk, 0.3, 0.5)
    sit_arms(c, sh, s, 640, 800, tr=hp, which=(1,), alen=110)
    glow(c, 1380, 420, 760, 0.16, YEL)
    tint(c, YEL, 0.05)
    vignette(c, 0.3)


def scene_day90(c, t):
    s = 0
    for i, a in enumerate(D90):
        if t >= a:
            s = i
    u = t - D90[s]
    n = 2
    bump = 0.0
    if s == 0:
        kettle_shot(c, u, 1.0, 0.0)
    elif s == 1:
        shelf_shot(c, u, "back", 1.0, 0.0)
        n = 2 if u < D90_BACK[1] else 1
        bump = pulse(u, D90_BACK[1], 0.45)
    elif s == 2:
        pour_shot(c, u, [1000], [D90_POUR], 1.0, 0.0)
    elif s == 3:
        P = dict(plant=1.0, rain=0.0, sun=1.0, lamp=0.2, shelf=1)
        c.save()
        cam(c, 1.06, 900, 560)
        room(c, t, P)
        table(c, t, [])
        wk = ease(seg(u, D90_WALK[0], D90_WALK[1]))
        walking = 1.0 if D90_WALK[0] < u < D90_WALK[1] else 0.0
        x = lerp(1560, 790, wk)
        sh = man(c, t, x, 960, 0.86, "neutral" if u < 4.5 else "smile", (-1.0, 0.1), seed=0.4,
                 bob=2.5 * walking * abs(math.sin(u * 6)), walk=walking, ph=u * 12, arms=False)
        man_arms(c, sh, 0.86, None, None, x, 960 - 160 * 0.86, which=(1,))
        hp = (x - 120, 720)
        held_cup(c, hp[0], hp[1], 0.5, t, True, 1.0, 1, 0.0, 0.25)
        man_arms(c, sh, 0.86, hp, None, x, 960 - 160 * 0.86, which=(0,))
        post(c, P)
        c.restore()
        vignette(c, 0.3)
    else:
        day90_sit(c, t, u)
    if s >= 2:
        n = 1
    tag(c, "DAY 90")
    meter(c, n, 1.0, bump)
    caption(c, t, "Day 90.", 0.3, 3.85)
    caption(c, t, "One cup.", D90[4] + 1.4, 29.8)


def scene_close(c, t):
    vgrad(c, 0, 0, W, H, SLATE_N, mix(SLATE_N, INK, 0.6))
    glow(c, W / 2, H / 2, 700, 0.06, YEL)
    a = ease(seg(t, 0.4, 1.0)) * (1 - ease(seg(t, 9.4, 9.95)))
    b = ease(seg(t, 0.4 + CLOSE_L2, 1.0 + CLOSE_L2)) * (1 - ease(seg(t, 9.4, 9.95)))
    text(c, "You don't stop missing them.", W / 2, 470, 80, CREAM, a)
    text(c, "You learn to sit with it.", W / 2, 620, 92, YEL, b)
    vignette(c, 0.4)


def scene_sign(c, t):
    c.set_source_rgb(*mix(SLATE_N, INK, 0.6))
    c.paint()
    k = ease(seg(t, 0.1, 0.8))
    sprout(c, W / 2, 430, 120, k)
    text(c, "Small Win Films", W / 2, 690, 64, CREAM, ease(seg(t, 0.5, 1.1)))
    tint(c, (0, 0, 0), ease(seg(t, 3.6, 4.9)))


SC = {"cold": scene_cold, "card": scene_card, "day1": scene_day1, "days": scene_days, "day8": scene_day8,
      "day14": scene_day14, "day30": scene_day30, "day40": scene_day40, "day60": scene_day60, "day90": scene_day90,
      "close": scene_close, "sign": scene_sign}


def scene_at(T):
    for n, d in DURS:
        if T < START[n] + d:
            return n, T - START[n]
    n, d = DURS[-1]
    return n, d - 1e-3


def frame(c, T):
    UI.clear()
    n, t = scene_at(T)
    c.save()
    SC[n](c, t)
    c.restore()


def scene_frame(c, n, t):
    UI.clear()
    c.save()
    SC[n](c, t)
    c.restore()


def surf_new():
    return cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def ff_writer(tmp, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s",
                             "%dx%d" % (w, h), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset",
                             "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)


def render_scene(name, outdir):
    out = os.path.join(outdir, "%02d_%s.mp4" % ([n for n, _ in DURS].index(name), name))
    tmp = out[:-4] + ".part.mp4"
    surf = surf_new()
    c = cairo.Context(surf)
    d = dict(DURS)[name]
    p = ff_writer(tmp, W, H)
    for i in range(int(round(d * FPS))):
        scene_frame(c, name, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(1)
    os.rename(tmp, out)


def still(T, path):
    surf = surf_new()
    c = cairo.Context(surf)
    frame(c, T)
    surf.write_to_png(path)


def strip(path, times, cols=5, label=True):
    rows = (len(times) + cols - 1) // cols
    sheet = cairo.ImageSurface(cairo.FORMAT_RGB24, 384 * cols, 216 * rows)
    sc = cairo.Context(sheet)
    sc.set_source_rgb(*INK)
    sc.paint()
    surf = surf_new()
    c = cairo.Context(surf)
    for i, T in enumerate(times):
        frame(c, T)
        cx, cy = (i % cols) * 384, (i // cols) * 216
        sc.save()
        sc.translate(cx, cy)
        sc.scale(0.2, 0.2)
        pat = cairo.SurfacePattern(surf)
        pat.set_filter(cairo.FILTER_BEST)
        sc.set_source(pat)
        sc.paint()
        sc.restore()
        if label:
            sc.set_source_rgba(0, 0, 0, 0.75)
            rrect(sc, cx + 144, cy + 6, 96, 28, 14)
            sc.fill()
            text(sc, "t=%.1f" % T, cx + 192, cy + 26, 19, CREAM)
        sc.set_source_rgba(*INK, 1)
        sc.set_line_width(2)
        sc.rectangle(cx, cy, 384, 216)
        sc.stroke()
    sheet.write_to_png(path)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for a in sys.argv[3:]:
            still(float(a), os.path.join(sys.argv[2], "s_%06.2f.png" % float(a)))
    elif mode == "strip":
        strip(sys.argv[2], [float(a) for a in sys.argv[3:]])
    elif mode == "scenes":
        for n in sys.argv[3:]:
            render_scene(n, sys.argv[2])
