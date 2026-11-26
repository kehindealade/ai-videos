import cairo, math, random, os, sys, subprocess

W, H, FPS = 1920, 1080, 30
FONT = "Rounded Mplus 1c ExtraBold"
FONTM = "Rounded Mplus 1c Medium"
GY = 880

WALL = (0.16, 0.18, 0.33)
WALL_D = (0.12, 0.13, 0.25)
FLOOR = (0.20, 0.17, 0.26)
NIGHTSKY = (0.07, 0.09, 0.20)
INK = (0.06, 0.07, 0.13)
LAMP = (0.98, 0.76, 0.42)
GLOW = (0.55, 0.75, 1.0)
SKIN = (0.42, 0.27, 0.18)
SKIN_D = (0.33, 0.20, 0.13)
HAIR = (0.08, 0.06, 0.07)
CARD = (0.85, 0.63, 0.25)
CARD_D = (0.68, 0.47, 0.17)
TEE = (0.93, 0.89, 0.84)
PANTS = (0.24, 0.27, 0.40)
SOFA = (0.45, 0.30, 0.42)
SOFA_D = (0.35, 0.22, 0.33)
BED = (0.80, 0.82, 0.90)
BLANKET = (0.42, 0.48, 0.72)
WOOD = (0.40, 0.28, 0.22)
HOOD = (0.55, 0.57, 0.62)
CREAM = (0.98, 0.95, 0.89)
ROSE = (0.93, 0.47, 0.50)
TEAR = (0.70, 0.86, 1.0)
FRIEND_SKIN = (0.60, 0.40, 0.27)
FRIEND_TOP = (0.27, 0.58, 0.52)
EX_TOP = (0.20, 0.36, 0.30)
BOX = (0.72, 0.56, 0.38)

UI = {}


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
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ell(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.new_sub_path()
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def text(c, s, x, y, size, col, a=1.0, align="c", font=FONT):
    c.select_font_face(font)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.width / 2 + ex.x_bearing
    elif align == "r":
        x -= ex.width + ex.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, a)
    c.show_text(s)
    c.new_path()
    return ex.width


def glow(c, x, y, r, a, col=LAMP):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g)
    c.paint()


def tint(c, col, a):
    if a > 0:
        c.set_source_rgba(*col, a)
        c.paint()


random.seed(7)
CITY = [(1010 + i * 34 + random.randint(-4, 4), random.randint(380, 500), random.randint(26, 40)) for i in range(11)]
WINS = [(random.random(), random.random(), random.random()) for _ in range(60)]
RAIN = [(random.random(), random.random(), 0.6 + random.random() * 0.6) for _ in range(90)]


def window(c, t, rain=0.0, moon=True):
    x0, y0, w, h = 1000, 220, 360, 340
    c.set_source_rgb(*mix(WALL_D, INK, 0.3))
    rr(c, x0 - 22, y0 - 22, w + 44, h + 44, 10)
    c.fill()
    c.set_source_rgb(*NIGHTSKY)
    c.rectangle(x0, y0, w, h)
    c.fill()
    if moon:
        c.set_source_rgb(0.95, 0.94, 0.85)
        c.arc(x0 + 280, y0 + 80, 30, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*NIGHTSKY)
        c.arc(x0 + 294, y0 + 70, 26, 0, 2 * math.pi)
        c.fill()
    for i, (bx, top, bw) in enumerate(CITY):
        c.set_source_rgb(0.12, 0.14, 0.26)
        c.rectangle(bx, y0 + top - 220, bw, h - top + 220)
        c.fill()
        for j in range(5):
            r = WINS[(i * 5 + j) % 60]
            if r[0] > 0.45:
                c.set_source_rgba(*LAMP, 0.55 + 0.4 * r[1])
                c.rectangle(bx + 6 + (j % 2) * 14, y0 + top - 200 + j * 22, 7, 9)
                c.fill()
    if rain > 0:
        c.set_line_width(2)
        for rx, ry, sp in RAIN:
            yy = y0 + ((ry + t * sp) % 1) * h
            xx = x0 + rx * w
            c.set_source_rgba(0.75, 0.82, 1.0, 0.5 * rain)
            c.move_to(xx, yy)
            c.line_to(xx - 4, yy + 18)
            c.stroke()
    c.set_source_rgb(*mix(WALL_D, INK, 0.3))
    c.rectangle(x0 + w / 2 - 6, y0, 12, h)
    c.rectangle(x0, y0 + h / 2 - 6, w, 12)
    c.fill()


def room(c, t, lamp=1.0, rain=0.0, door_open=0.0, box=None, hoodie=True, bowl=False, takeaway=False):
    c.set_source_rgb(*WALL)
    c.paint()
    c.set_source_rgb(*WALL_D)
    c.rectangle(-600, 760, W + 1200, 120)
    c.fill()
    window(c, t, rain)
    c.set_source_rgb(*mix(WALL_D, INK, 0.4))
    c.rectangle(150, 290, 250, GY - 290)
    c.fill()
    c.set_source_rgb(0.30, 0.22, 0.30)
    c.save()
    c.rectangle(166, 306, 218, GY - 306)
    c.clip()
    if door_open > 0:
        c.set_source_rgb(0.85, 0.80, 0.62)
        c.rectangle(166, 306, 218, GY - 306)
        c.fill()
    c.set_source_rgb(0.30, 0.22, 0.30)
    c.rectangle(166, 306, 218 * (1 - 0.85 * door_open), GY - 306)
    c.fill()
    c.restore()
    c.set_source_rgb(*LAMP)
    c.arc(166 + 218 * (1 - 0.85 * door_open) - 26, 600, 9, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*FLOOR)
    c.rectangle(-600, GY, W + 1200, H - GY + 400)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.05)
    ell(c, 900, 950, 420, 40)
    c.fill()
    c.set_source_rgb(*SOFA_D)
    rr(c, 560, 600, 420, 130, 40)
    c.fill()
    c.set_source_rgb(*SOFA)
    rr(c, 540, 700, 460, 120, 34)
    c.fill()
    rr(c, 520, 660, 70, 170, 30)
    rr(c, 950, 660, 70, 170, 30)
    c.fill()
    c.set_source_rgb(*SOFA_D)
    c.rectangle(570, 820, 20, 60)
    c.rectangle(950, 820, 20, 60)
    c.fill()
    c.set_source_rgb(*WOOD)
    rr(c, 640, 830, 260, 20, 8)
    c.fill()
    c.rectangle(660, 850, 14, 30)
    c.rectangle(866, 850, 14, 30)
    c.fill()
    if bowl:
        c.set_source_rgb(*CREAM)
        c.move_to(700, 830)
        c.curve_to(705, 800, 765, 800, 770, 830)
        c.close_path()
        c.fill()
    if takeaway:
        c.set_source_rgb(0.95, 0.92, 0.85)
        c.move_to(780, 830)
        c.line_to(790, 790)
        c.line_to(850, 790)
        c.line_to(860, 830)
        c.close_path()
        c.fill()
        c.set_source_rgb(0.85, 0.30, 0.25)
        c.rectangle(795, 805, 50, 8)
        c.fill()
    c.set_source_rgb(*WOOD)
    c.rectangle(1050, 700, 14, 180)
    c.rectangle(1150, 700, 14, 180)
    c.fill()
    rr(c, 1040, 690, 134, 20, 6)
    c.fill()
    rr(c, 1140, 540, 20, 160, 6)
    c.fill()
    if hoodie:
        c.set_source_rgb(*HOOD)
        c.move_to(1120, 560)
        c.curve_to(1180, 560, 1185, 640, 1170, 700)
        c.line_to(1110, 720)
        c.curve_to(1100, 660, 1100, 600, 1120, 560)
        c.fill()
        c.set_source_rgb(*mix(HOOD, INK, 0.3))
        ell(c, 1150, 575, 26, 14)
        c.fill()
    c.set_source_rgb(*WOOD)
    rr(c, 1290, 740, 100, 140, 8)
    c.fill()
    c.set_source_rgb(*mix(WOOD, INK, 0.3))
    c.rectangle(1300, 790, 80, 4)
    c.fill()
    c.set_source_rgb(*INK)
    c.rectangle(1336, 640, 6, 100)
    c.fill()
    c.set_source_rgb(*(LAMP if lamp > 0.5 else mix(LAMP, INK, 0.7)))
    c.move_to(1300, 650)
    c.line_to(1318, 590)
    c.line_to(1360, 590)
    c.line_to(1378, 650)
    c.close_path()
    c.fill()
    c.set_source_rgb(*WOOD)
    rr(c, 1840, 560, 50, 320, 10)
    c.fill()
    c.set_source_rgb(*BED)
    rr(c, 1400, 700, 470, 110, 20)
    c.fill()
    c.set_source_rgb(*WOOD)
    rr(c, 1400, 800, 470, 40, 10)
    c.fill()
    c.rectangle(1410, 840, 20, 40)
    c.rectangle(1840, 840, 20, 40)
    c.fill()
    c.set_source_rgb(*CREAM)
    rr(c, 1700, 660, 150, 60, 26)
    c.fill()
    if box:
        bx, lab, tape = box
        c.set_source_rgb(*BOX)
        rr(c, bx, 780, 150, 100, 6)
        c.fill()
        c.set_source_rgb(*mix(BOX, INK, 0.25))
        c.rectangle(bx, 780, 150, 14)
        c.fill()
        if tape:
            c.set_source_rgba(0.9, 0.85, 0.7, 0.9)
            c.rectangle(bx + 60, 780, 30, 100 * tape)
            c.fill()
        if lab:
            text(c, lab, bx + 75, 850, 26, INK)
    if lamp > 0.5:
        glow(c, 1340, 640, 700, 0.28 * lamp)
    else:
        c.set_source_rgba(0.02, 0.03, 0.10, 0.55)
        c.paint()
        c.set_source_rgba(0.6, 0.7, 1.0, 0.07)
        c.move_to(1000, 220)
        c.line_to(1360, 220)
        c.line_to(1700, H)
        c.line_to(1100, H)
        c.close_path()
        c.fill()


def face(c, mood="sad", cry=0.0, blink=1.0, look=0.0, glow_a=0.0, t=0.0, strands=True):
    c.set_source_rgb(*HAIR)
    for i in range(9):
        a = math.pi * (1.05 + i * 0.11)
        ell(c, 74 * math.cos(a) * 1.05, -10 + 80 * math.sin(a), 22, 30)
        c.fill()
    c.set_source_rgb(*SKIN)
    ell(c, 0, 0, 62, 72)
    c.fill()
    c.set_source_rgb(*HAIR)
    for i in range(8):
        a = math.pi * (1.12 + i * 0.11)
        ell(c, 60 * math.cos(a), -18 + 64 * math.sin(a), 20, 22)
        c.fill()
    if strands:
        for sx in (-1, 1):
            rr(c, sx * 66 - 14, -10, 28, 110, 14)
            c.fill()
    ey = 8
    for dx in (-22, 22):
        c.set_source_rgb(*CREAM)
        ell(c, dx + 4 * look, ey, 10, 11 * blink)
        c.fill()
        c.set_source_rgb(*INK)
        ell(c, dx + 4 * look + 1, ey + 2 + (3 if mood in ("sad", "cry") else 0), 5.5, 6.5 * blink)
        c.fill()
        if cry > 0 and blink > 0.5:
            c.set_source_rgba(1, 1, 1, 0.8 * cry)
            ell(c, dx + 4 * look + 3, ey - 2, 2.5, 2.5)
            c.fill()
        c.set_source_rgb(*SKIN_D)
        c.set_line_width(5)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        inner = 1 if dx < 0 else -1
        if mood in ("sad", "cry"):
            c.move_to(dx - 12, ey - 12 - (0 if inner > 0 else 6))
            c.line_to(dx + 12, ey - 12 - (6 if inner > 0 else 0))
        elif mood == "calm":
            c.move_to(dx - 12, ey - 16)
            c.line_to(dx + 12, ey - 16)
        else:
            c.move_to(dx - 12, ey - 14)
            c.line_to(dx + 12, ey - 14)
        c.stroke()
    c.set_source_rgb(*SKIN_D)
    c.set_line_width(4)
    if mood == "cry":
        c.arc(0, 52, 11, 1.15 * math.pi, 1.85 * math.pi)
    elif mood == "sad":
        c.arc(0, 50, 10, 1.2 * math.pi, 1.8 * math.pi)
    else:
        c.move_to(-8, 44)
        c.line_to(8, 44)
    c.stroke()
    c.set_source_rgb(*SKIN_D)
    ell(c, 0, 26, 6, 4)
    c.fill()
    if cry > 0:
        for dx, ph in ((-24, 0.0), (24, 0.5)):
            k = ((t * 0.45 + ph) % 1)
            c.set_source_rgba(*TEAR, 0.85 * cry)
            ell(c, dx - 2, ey + 18 + 50 * k, 4, 6)
            c.fill()
            c.set_source_rgba(*TEAR, 0.35 * cry)
            c.set_line_width(3)
            c.move_to(dx - 2, ey + 14)
            c.line_to(dx - 2, ey + 14 + 50 * k)
            c.stroke()
    if glow_a > 0:
        g = cairo.LinearGradient(0, 120, 0, -60)
        g.add_color_stop_rgba(0, *GLOW, 0.35 * glow_a)
        g.add_color_stop_rgba(1, *GLOW, 0.0)
        c.set_source(g)
        ell(c, 0, 0, 62, 72)
        c.fill()


def hand(c, x, y, col=SKIN):
    c.set_source_rgb(*col)
    ell(c, x, y, 16, 15)
    c.fill()


def phone_obj(c, x, y, ang=0.0, s=1.0, lit=True):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.set_source_rgb(*INK)
    rr(c, -20, -36, 40, 72, 8)
    c.fill()
    if lit:
        c.set_source_rgb(*GLOW)
        rr(c, -16, -31, 32, 62, 5)
        c.fill()
    c.restore()


def her(c, x, y, pose="stand", mood="sad", cry=0.0, t=0.0, phone=False, look=0.0, s=1.0, walk=None, arms=None, face_dir=1):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    blink = 0.12 if (t % 4.1) < 0.12 else 1.0
    if pose == "lie":
        c.translate(0, 0)
        c.save()
        c.translate(-10, -170)
        c.rotate(-0.35)
        face(c, mood, cry, blink if mood != "sleep" else 0.1, look, 0.6 if phone else 0, t, strands=False)
        c.restore()
        c.restore()
        return
    sit = pose in ("sit", "floor")
    if pose == "stand" or pose == "walk":
        sw = 20 * math.sin(walk) if walk is not None else 0
        c.set_source_rgb(*PANTS)
        c.set_line_width(40)
        for sg in (-1, 1):
            c.move_to(sg * 24, -200)
            c.line_to(sg * 24 + sw * sg, -26)
            c.stroke()
        c.set_source_rgb(*INK)
        for sg in (-1, 1):
            rr(c, sg * 24 + sw * sg - 26, -30, 56, 26, 12)
            c.fill()
        c.translate(0, -190)
    elif pose == "sit":
        c.set_source_rgb(*PANTS)
        c.set_line_width(40)
        for sg in (-1, 1):
            c.move_to(sg * 22, -110)
            c.line_to(sg * 22 + 70 * face_dir, -105)
            c.line_to(sg * 22 + 74 * face_dir, -10)
            c.stroke()
        c.translate(0, -100)
    elif pose == "floor":
        c.set_source_rgb(*PANTS)
        c.set_line_width(40)
        for sg in (-1, 1):
            c.move_to(sg * 22, -20)
            c.line_to(sg * 18 + 50 * face_dir, -110)
            c.line_to(sg * 18 + 100 * face_dir, -20)
            c.stroke()
        c.translate(0, -10)
    c.set_source_rgb(*TEE)
    rr(c, -60, -230, 120, 230, 50)
    c.fill()
    c.set_source_rgb(*CARD)
    c.move_to(-70, -210)
    c.curve_to(-80, -120, -76, -40, -66, 0)
    c.line_to(-22, 0)
    c.line_to(-14, -220)
    c.close_path()
    c.fill()
    c.move_to(70, -210)
    c.curve_to(80, -120, 76, -40, 66, 0)
    c.line_to(22, 0)
    c.line_to(14, -220)
    c.close_path()
    c.fill()
    if phone or arms == "phone":
        for sg in (-1, 1):
            c.set_source_rgb(*CARD_D)
            c.set_line_width(30)
            c.move_to(sg * 60, -200)
            c.curve_to(sg * 70, -120, sg * 40, -110, sg * 12, -140)
            c.stroke()
        phone_obj(c, 0, -150, 0.2, 1.0)
        hand(c, -12, -138)
        hand(c, 14, -134)
    elif arms == "knees":
        c.set_source_rgb(*CARD_D)
        c.set_line_width(30)
        for sg in (-1, 1):
            c.move_to(sg * 60, -200)
            c.curve_to(sg * 70, -140, 40 * face_dir + sg * 10, -110, 50 * face_dir + sg * 6, -100)
            c.stroke()
        hand(c, 50 * face_dir, -100)
    elif arms == "box":
        c.set_source_rgb(*CARD_D)
        c.set_line_width(30)
        for sg in (-1, 1):
            c.move_to(sg * 60, -200)
            c.line_to(sg * 50 + 60 * face_dir, -90)
            c.stroke()
        hand(c, 60 * face_dir - 40, -88)
        hand(c, 60 * face_dir + 40, -88)
    elif arms == "reach":
        c.set_source_rgb(*CARD_D)
        c.set_line_width(30)
        c.move_to(-60, -200)
        c.curve_to(-70, -120, -60, -60, -50, -40)
        c.stroke()
        c.move_to(60 * face_dir, -200)
        c.line_to(150 * face_dir, -250)
        c.stroke()
        hand(c, -50, -40)
        hand(c, 150 * face_dir, -250)
    else:
        c.set_source_rgb(*CARD_D)
        c.set_line_width(30)
        for sg in (-1, 1):
            c.move_to(sg * 62, -200)
            c.curve_to(sg * 74, -120, sg * 70, -60, sg * 64, -40)
            c.stroke()
            hand(c, sg * 64, -36)
    c.translate(0, -300)
    c.scale(0.95, 0.95)
    face(c, mood, cry, blink, look, 0.8 if phone else 0, t)
    c.restore()


def person(c, x, y, top, skin, hair="short", s=1.0, back=False, walk=None, carry=None, sit=False, face_dir=1):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    sw = 20 * math.sin(walk) if walk is not None else 0
    c.set_source_rgb(0.18, 0.18, 0.24)
    c.set_line_width(40)
    if sit:
        for sg in (-1, 1):
            c.move_to(sg * 22, -110)
            c.line_to(sg * 22 + 70 * face_dir, -105)
            c.line_to(sg * 22 + 74 * face_dir, -10)
            c.stroke()
        c.translate(0, -100)
    else:
        for sg in (-1, 1):
            c.move_to(sg * 24, -200)
            c.line_to(sg * 24 + sw * sg, -26)
            c.stroke()
        c.translate(0, -190)
    c.set_source_rgb(*top)
    rr(c, -66, -240, 132, 240, 50)
    c.fill()
    if carry == "box":
        c.set_source_rgb(*BOX)
        rr(c, -80, -170, 160, 110, 6)
        c.fill()
    if carry == "bag":
        c.set_source_rgb(0.95, 0.92, 0.85)
        rr(c, 60, -110, 60, 70, 8)
        c.fill()
    c.translate(0, -300)
    c.set_source_rgb(*skin)
    ell(c, 0, 0, 58, 66)
    c.fill()
    c.set_source_rgb(*HAIR)
    if back:
        ell(c, 0, -6, 60, 62)
        c.fill()
    elif hair == "wrap":
        c.set_source_rgb(0.85, 0.45, 0.30)
        ell(c, 0, -46, 70, 44)
        c.fill()
        c.set_source_rgb(*INK)
        for dx in (-20, 20):
            ell(c, dx + 6 * face_dir, 8, 5, 6)
            c.fill()
        c.set_source_rgb(*mix(skin, INK, 0.4))
        c.set_line_width(4)
        c.arc(6 * face_dir, 34, 12, 0.2 * math.pi, 0.8 * math.pi)
        c.stroke()
    else:
        c.arc(0, -8, 60, math.pi * 1.05, math.pi * 1.95)
        c.close_path()
        c.fill()
        c.set_source_rgb(*INK)
        for dx in (-20, 20):
            ell(c, dx + 6 * face_dir, 8, 5, 6)
            c.fill()
        c.set_source_rgb(*mix(skin, INK, 0.4))
        c.set_line_width(4)
        c.arc(6 * face_dir, 30, 14, 0.15 * math.pi, 0.85 * math.pi)
        c.stroke()
    c.restore()


PH_W, PH_H = 430, 800


def phone_ui(c, x, y, st, t, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.35)
    rr(c, 10, 18, PH_W, PH_H, 56)
    c.fill()
    c.set_source_rgb(0.05, 0.05, 0.07)
    rr(c, 0, 0, PH_W, PH_H, 56)
    c.fill()
    c.set_source_rgb(0.96, 0.96, 0.98)
    rr(c, 14, 14, PH_W - 28, PH_H - 28, 44)
    c.fill()
    c.set_source_rgb(0.05, 0.05, 0.07)
    rr(c, PH_W / 2 - 60, 26, 120, 30, 15)
    c.fill()
    mode = st.get("mode", "chat")
    if mode == "photo":
        c.set_source_rgb(0.15, 0.12, 0.25)
        c.rectangle(14, 120, PH_W - 28, 470)
        c.fill()
        for i in range(14):
            c.set_source_rgba(*[(1, 0.7, 0.3), (1, 0.4, 0.6), (0.5, 0.8, 1)][i % 3], 0.7)
            c.arc(40 + (i * 37) % 360, 150 + (i * 53) % 120, 8, 0, 2 * math.pi)
            c.fill()
        person(c, PH_W / 2 - 60, 600, EX_TOP, (0.50, 0.33, 0.22), s=0.85)
        person(c, PH_W / 2 + 90, 600, (0.85, 0.40, 0.45), (0.62, 0.44, 0.30), hair="wrap", s=0.8)
        text(c, "David", 40, 100, 30, INK, align="l")
        text(c, "best night in ages", 40, 640, 26, INK, align="l", font=FONTM)
        c.set_source_rgb(0.9, 0.3, 0.4)
        text(c, "♥ 214", 40, 690, 26, (0.9, 0.3, 0.4), align="l")
        c.restore()
        return
    text(c, "David", PH_W / 2, 105, 32, INK)
    c.set_source_rgb(0.85, 0.86, 0.9)
    c.rectangle(14, 125, PH_W - 28, 2)
    c.fill()
    old = st.get("old", [])
    yy = 170
    for m, mine in old:
        w = 250
        xx = PH_W - 34 - w if mine else 34
        c.set_source_rgb(*((0.25, 0.48, 0.95) if mine else (0.88, 0.89, 0.93)))
        rr(c, xx, yy, w, 56, 24)
        c.fill()
        text(c, m, xx + 20, yy + 37, 24, WHITE if mine else INK, align="l", font=FONTM)
        yy += 72
    if mode == "contact":
        c.set_source_rgba(0, 0, 0, 0.45)
        rr(c, 14, 14, PH_W - 28, PH_H - 28, 44)
        c.fill()
        k = st.get("k", 0)
        c.set_source_rgb(0.98, 0.98, 1)
        rr(c, 50, 300, PH_W - 100, 230, 28)
        c.fill()
        text(c, "Delete contact?", PH_W / 2, 360, 32, INK)
        text(c, "David", PH_W / 2, 405, 26, (0.4, 0.4, 0.5), font=FONTM)
        c.set_source_rgb(*mix((0.92, 0.3, 0.3), (0.7, 0.15, 0.15), k))
        rr(c, 80, 440, PH_W - 160, 64, 32)
        c.fill()
        text(c, "Delete", PH_W / 2, 483, 30, WHITE)
        c.restore()
        return
    if mode == "deleted":
        c.set_source_rgb(0.96, 0.96, 0.98)
        rr(c, 14, 14, PH_W - 28, PH_H - 28, 44)
        c.fill()
        text(c, "Contacts", PH_W / 2, 105, 32, INK)
        for i, n in enumerate(["Ada", "Chioma", "Dad", "Mum", "Work"]):
            text(c, n, 50, 200 + i * 70, 28, INK, align="l", font=FONTM)
            c.set_source_rgb(0.88, 0.88, 0.92)
            c.rectangle(50, 220 + i * 70, PH_W - 100, 2)
            c.fill()
        c.restore()
        return
    draft = st.get("draft", "")
    lines = wrap(c, draft, 26, PH_W - 150)
    nb = max(1, len(lines))
    by = PH_H - 120 - (nb - 1) * 34
    c.set_source_rgb(1, 1, 1)
    rr(c, 30, by - 10, PH_W - 120, 64 + (nb - 1) * 34, 30)
    c.fill()
    c.set_source_rgb(0.8, 0.8, 0.86)
    c.set_line_width(2)
    rr(c, 30, by - 10, PH_W - 120, 64 + (nb - 1) * 34, 30)
    c.stroke()
    if not draft:
        text(c, "Message", 56, by + 32, 26, (0.6, 0.6, 0.66), align="l", font=FONTM)
    for i, ln in enumerate(lines):
        wdt = text(c, ln, 56, by + 32 + i * 34, 26, INK, align="l", font=FONTM)
    if (t * 2) % 1 < 0.6:
        lw = c.text_extents(lines[-1] if lines else "").x_advance if lines else 0
        c.set_source_rgb(0.25, 0.48, 0.95)
        c.rectangle(58 + lw, by + 8 + (nb - 1) * 34, 3, 32)
        c.fill()
    sc = st.get("send", 0.0)
    c.set_source_rgb(*mix((0.25, 0.48, 0.95), (0.55, 0.75, 1.0), sc))
    c.arc(PH_W - 55, by + 22 + (nb - 1) * 34, 32 + 6 * sc, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(1, 1, 1)
    c.set_line_width(5)
    cx, cy = PH_W - 55, by + 22 + (nb - 1) * 34
    c.move_to(cx - 12, cy + 2)
    c.line_to(cx + 12, cy - 8)
    c.line_to(cx + 2, cy + 14)
    c.stroke()
    if st.get("thumb"):
        k = st["thumb"]
        c.set_source_rgba(*SKIN, 0.97)
        ell(c, cx + 30 - 10 * k, cy + 110 - 70 * k, 46, 70)
        c.fill()
    c.restore()


WHITE = (1, 1, 1)


def wrap(c, s, size, maxw):
    c.select_font_face(FONTM)
    c.set_font_size(size)
    out, cur = [], ""
    for w in s.split(" "):
        tr = (cur + " " + w).strip() if cur else w
        if c.text_extents(tr).x_advance > maxw and cur:
            out.append(cur)
            cur = w
        else:
            cur = tr
    if cur or s.endswith(" "):
        out.append(cur)
    return out[-6:]


def typed(s, t, a, b, d0, d1):
    if t < a:
        return ""
    if t < b:
        return s[:int(len(s) * (t - a) / (b - a))]
    if t < d0:
        return s
    if t < d1:
        return s[:int(len(s) * (1 - (t - d0) / (d1 - d0)))]
    return ""
