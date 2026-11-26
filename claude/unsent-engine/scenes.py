import math, cairo
from film import *

LONG = "How are you already happy? I can't sleep. I keep thinking it was my fault. I still check if you're online. Was any of it real? I miss you so much it hurts."
OLD = [("Home safe?", True), ("yes. night", False)]


def bed_lie(c, t, mood="sad", phone=True, cry=0.0, lamp=1.0, phone_up=1.0):
    br = 3 * math.sin(t * 1.4)
    her(c, 1770, 860, pose="lie", mood=mood, cry=cry, t=t, phone=phone)
    c.set_source_rgb(*BLANKET)
    c.move_to(1410, 800)
    c.curve_to(1420, 700 - br, 1560, 680 - br, 1690, 720)
    c.line_to(1700, 800)
    c.close_path()
    c.fill()
    if phone and phone_up > 0:
        hand(c, 1660, 600 + 40 * (1 - phone_up))
        phone_obj(c, 1660, 570 + 40 * (1 - phone_up), -0.3, 1.2)
        glow(c, 1680, 620, 260, 0.35 * phone_up, GLOW)


def s0(c, t):
    room(c, t + 30, lamp=0.0, rain=0.4)
    tint(c, INK, 0.45)
    c.save()
    c.translate(620, 600)
    c.scale(3.3, 3.3)
    c.set_source_rgb(*CARD)
    rr(c, -110, 80, 220, 140, 60)
    c.fill()
    face(c, "sad", 0.5, 1.0, 0.8, 1.0, t)
    c.restore()
    glow(c, 640, 1000, 700, 0.30, GLOW)
    d = typed("I miss you.", t, -1, 0, 3.9, 4.6)
    st = dict(mode="chat", old=OLD, draft=d, send=0.5 + 0.5 * math.sin(t * 5) if t < 3.9 else 0, thumb=e(t, 0.4, 1.4) if t < 3.9 else 0)
    return dict(phone=st, side="r", night="NIGHT 31", meter=31, big_meter=1 - e(t, 2.0, 2.9), caps=[("I wrote him 31 texts. I sent none.", 0.0, 4.8)], cam=(1.0, W / 2, H / 2))


def s0b(c, t):
    c.set_source_rgb(*INK)
    c.paint()
    text(c, "31 nights earlier.", W / 2, H / 2 + 20, 76, CREAM, e(t, 0.05, 0.4))
    return dict(phone=None, night=None, meter=None, caps=[], card=True)


def s1(c, t):
    door = 1.0 - e(t, 3.0, 4.4)
    room(c, t, lamp=1.0, door_open=door)
    if t < 4.2:
        ex_x = lerp(620, 270, e(t, 0.0, 3.4))
        a = 1 - e(t, 3.2, 3.8)
        c.push_group()
        person(c, ex_x, GY, EX_TOP, (0.5, 0.33, 0.22), back=True, walk=t * 7 if t < 3.4 else None, carry="box")
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    if t < 5.2:
        her(c, 820, GY, "stand", "sad", 0, t)
    elif t < 7.5:
        x = lerp(820, 470, e(t, 5.2, 7.2))
        her(c, x, GY, "walk", "sad", 0, t, walk=t * 6, face_dir=-1)
    else:
        her(c, 470, GY, "floor", "sad", 0.4 * e(t, 7.5, 9), t, phone=t > 9.0, arms="knees" if t <= 9.0 else None)
    d = typed("Please come back.", t, 10.0, 12.4, 14.0, 15.4)
    ph = dict(mode="chat", old=OLD, draft=d) if 9.6 < t < 16.4 else None
    n = 1 if t >= 15.4 else 0
    z = lerp(1.0, 1.45, e(t, 8.5, 10.0))
    return dict(phone=ph, side="r", night="NIGHT 1", meter=n, caps=[("Night 1. He's gone.", 4.8, 9.4)], cam=(z, 520, 640))


def s2(c, t):
    room(c, t, lamp=1.0, bowl=True)
    look = e(t, 0.5, 1.2) * (1 - e(t, 3.0, 3.6))
    her(c, 760, GY, "sit", "sad", 0, t, phone=t > 3.4, look=look)
    d = typed("Did you eat?", t, 4.4, 6.0, 8.0, 9.2)
    ph = dict(mode="chat", old=OLD, draft=d) if 4.0 < t < 10.0 else None
    n = 3 if t >= 9.2 else 1
    z = lerp(1.25, 1.5, e(t, 0, 17))
    return dict(phone=ph, side="r", night="NIGHT 3", meter=n, caps=[("Night 3. I still worry if he ate.", 10.0, 16.3)], cam=(z, 900, 640))


def s3(c, t):
    door = e(t, 1.0, 1.8) * (1 - e(t, 13.6, 14.4))
    room(c, t, lamp=1.0, door_open=door, takeaway=2.0 < t)
    if t < 5.0:
        fx = lerp(280, 560, e(t, 1.6, 4.6))
        person(c, fx, GY, FRIEND_TOP, FRIEND_SKIN, hair="wrap", walk=t * 7 if 1.6 < t < 4.6 else None, carry="bag" if t < 4.0 else None, face_dir=1)
    elif t < 11.0:
        person(c, 600, GY, FRIEND_TOP, FRIEND_SKIN, hair="wrap", sit=True, face_dir=1)
    elif t < 14.0:
        fx = lerp(600, 260, e(t, 11.0, 13.6))
        person(c, fx, GY, FRIEND_TOP, FRIEND_SKIN, hair="wrap", walk=t * 7, face_dir=-1)
    her(c, 860, GY, "sit", "sad", 0, t, phone=(t < 6.0 or t > 15.0), face_dir=-1)
    if 6.0 <= t <= 15.0:
        k = e(t, 6.0, 7.4)
        c.set_source_rgb(*INK)
        rr(c, lerp(840, 730, k) - 30, lerp(700, 822, k) - 8, 60, 14, 5)
        c.fill()
    d = typed("I'm fine.", t, 15.8, 17.0, 18.2, 19.0)
    ph = dict(mode="chat", old=OLD, draft=d) if 15.4 < t < 19.6 else None
    n = 7 if t >= 19.0 else 3
    return dict(phone=ph, side="r", night="NIGHT 7", meter=n, caps=[("Night 7.", 0.4, 3.4), ("My friend said: don't text him.", 7.0, 11.4)], cam=(1.2, 700, 620))


def s4(c, t):
    room(c, t, lamp=1.0, rain=1.0)
    cry = e(t, 9.5, 12.0)
    hold = t > 22.0
    her(c, 1500, GY, "sit", "cry" if t > 9.5 else "sad", cry, t, phone=not hold, face_dir=-1, arms="knees" if hold else None)
    if hold:
        phone_obj(c, 1500, GY - 270, 0, 1.0, lit=False)
    if t < 7.0:
        ph = dict(mode="photo")
    elif t < 22.0:
        d = typed(LONG, t, 7.4, 15.0, 19.0, 21.4)
        ph = dict(mode="chat", old=OLD, draft=d)
    else:
        ph = None
    n = 12 if t >= 21.4 else 7
    z = lerp(1.15, 1.7, e(t, 8.0, 14.0))
    return dict(phone=ph, side="l", night="NIGHT 12", meter=n, caps=[("Night 12. He looked happy.", 1.8, 6.8), ("I wrote a whole page.", 15.0, 20.0)], cam=(z, 1480, 560))


def s5(c, t):
    has_hood = t < 2.5
    tape = e(t, 5.0, 6.8)
    room(c, t, lamp=1.0, hoodie=has_hood, box=(900, None, tape))
    if t < 2.5:
        x = lerp(1250, 1180, e(t, 0.2, 1.4))
        her(c, x, GY, "stand", "sad", 0, t, arms="reach", face_dir=-1)
    elif t < 8.0:
        x = lerp(1180, 1040, e(t, 2.5, 3.8))
        her(c, x, GY, "stand", "sad", 0, t, arms="box", face_dir=-1)
        if t < 4.4:
            c.set_source_rgb(*HOOD)
            rr(c, x - 110, GY - 300 + 120 * e(t, 3.6, 4.4), 120, 70, 14)
            c.fill()
    else:
        her(c, 1040, GY, "stand", "sad", 0, t, phone=True)
    d = typed("Do you want your hoodie back?", t, 9.2, 12.0, 15.0, 16.6)
    ph = dict(mode="chat", old=OLD, draft=d) if 8.8 < t < 17.4 else None
    n = 20 if t >= 16.6 else 12
    return dict(phone=ph, side="l", night="NIGHT 20", meter=n, caps=[("Night 20. I packed what he left.", 1.0, 6.4)], cam=(1.3, 1000, 620))


def s6(c, t):
    lamp = 0.0 if t > 26.0 else 1.0
    rain = 1.0 - e(t, 9.0, 12.0)
    room(c, t, lamp=lamp, rain=rain, box=(900, None, 1.0))
    up = 1.0 - e(t, 23.6, 24.4)
    bed_lie(c, t, "sad", True, 0.3 if t < 13 else 0.15, lamp, up)
    if t < 15.5:
        d = typed("I miss you.", t, 1.0, 3.2, 13.0, 14.4)
        th = e(t, 4.0, 5.4) * (1 - e(t, 12.6, 13.0))
        ph = dict(mode="chat", old=OLD, draft=d, send=(0.5 + 0.5 * math.sin(t * 3)) * th, thumb=th)
    elif t < 21.0:
        ph = dict(mode="contact", old=OLD, k=e(t, 19.6, 20.0))
    elif t < 23.6:
        ph = dict(mode="deleted")
    else:
        ph = None
    n = 31 if t >= 14.4 else 20
    z = lerp(1.25, 1.55, e(t, 0, 14))
    return dict(phone=ph, side="l", night="NIGHT 31", meter=n, caps=[("Night 31. I didn't send it.", 15.0, 20.2)], cam=(z, 1560, 620))


def s7(c, t):
    lamp = 0.0 if t > 15.5 else 1.0
    room(c, t, lamp=lamp, box=(420, "DONATE", 1.0))
    up = e(t, 1.6, 2.4) * (1 - e(t, 8.6, 9.4))
    bed_lie(c, t, "calm" if t > 10 else "sad", up > 0.02, 0.0, lamp, up)
    ph = dict(mode="chat", old=OLD, draft="") if 2.8 < t < 8.6 else None
    return dict(phone=ph, side="l", night="NIGHT 32", meter=31, caps=[("Night 32. I wrote nothing.", 9.4, 14.4)], cam=(lerp(1.0, 1.2, e(t, 0, 20)), 1100, 600))


def sprout(c, cx, cy, s, a):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.set_source_rgba(0.85, 0.64, 0.25, a)
    c.set_line_width(8)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for ang in (-150, -120, -90, -60, -30):
        g = math.radians(ang)
        c.move_to(52 * math.cos(g), 44 + 52 * math.sin(g))
        c.line_to(70 * math.cos(g), 44 + 70 * math.sin(g))
        c.stroke()
    c.arc(0, 44, 40, math.pi, 2 * math.pi)
    c.close_path()
    c.fill()
    c.set_source_rgba(*CREAM, a)
    rr(c, -92, 40, 184, 14, 7)
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


def s8(c, t):
    c.set_source_rgb(*INK)
    c.paint()
    sprout(c, W / 2, 250, 1.6, e(t, 7.0, 8.0))
    text(c, "It still hurts.", W / 2, 520, 92, CREAM, e(t, 0.6, 1.6) * (1 - e(t, 19.0, 19.9)))
    text(c, "But tonight, I didn't write.", W / 2, 660, 92, LAMP, e(t, 3.6, 4.6) * (1 - e(t, 19.0, 19.9)))
    text(c, "Small Win Films", W / 2, 860, 40, CREAM, 0.6 * e(t, 8.0, 9.0) * (1 - e(t, 19.0, 19.9)))
    return dict(phone=None, night=None, meter=None, caps=[], card=True)


SCENES = [("s0", s0, 5), ("s0b", s0b, 2), ("s1", s1, 18), ("s2", s2, 17), ("s3", s3, 20), ("s4", s4, 28), ("s5", s5, 20), ("s6", s6, 30), ("s7", s7, 20), ("s8", s8, 20)]
