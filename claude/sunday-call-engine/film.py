import cairo, sys, os, subprocess, math
from sd import *
import sd

TICKS = [(25.0, 1), (77.0, 2), (103.5, 3), (129.6, 4)]
PICKUP = 150.0


def ctr_n(T):
    if T < 5.0:
        return 3
    n = 0
    for tt, v in TICKS:
        if T >= tt:
            n = v
    return n


def ctr_anim(T):
    for tt, v in TICKS:
        if tt <= T < tt + 0.8:
            return e(T, tt, tt + 0.6), e(T, tt, tt + 0.45)
    return 1.0, 0.0


def push(c, T, t0, t1, z0=1.0, z1=1.07, cx=W / 2, cy=H / 2):
    z = lerp(z0, z1, e(T, t0, t1))
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx, hw, W - hw)
    cy = clamp(cy, hh, H - hh)
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


def S(t0, t1, fn):
    return (t0, t1, fn)


def s_open_a(c, T):
    c.save()
    push(c, T, 0, 1.7, 1.08, 1.0)
    table_close(c, T, "down", 1.0)
    c.restore()
    return dict(caps=[("She calls every Sunday at 6.", 0.15, 2.9)])


def s_open_b(c, T):
    tl = T - 1.7
    k = e(tl, 0.15, 0.85)
    f = -math.cos(math.pi * k)
    table_close(c, T, "incoming", 1.0, flip=f if abs(f) > 0.04 else 0.04, hand_k=clamp(tl / 0.6) * (1 - e(tl, 0.9, 1.4)))
    return dict(caps=[("She calls every Sunday at 6.", 0.15, 2.9), ("I let it ring.", 3.0, 4.95)])


def s_open_c(c, T):
    tl = T - 3.1
    ga = 0.9 if T < 4.6 else 0.9 * (1 - e(T, 4.6, 4.95))
    c.save()
    push(c, T, 3.1, 5.0, 1.0, 1.06, 820, 520)
    son_close(c, T, "worry", 0.5, ga, up=-0.3)
    c.restore()
    return dict(caps=[("I let it ring.", 3.0, 4.95)])


def s_card(c, T):
    card(c, "3 Sundays earlier.", e(T, 5.0, 5.35))
    return dict(card=True)


def clk(T, at):
    if T < at:
        s = 60 - (at - T)
        return (5, 59, s % 60)
    return (6, 0, (T - at) % 60)


def s_w1_wide(c, T):
    tl = T - 7
    c.save()
    push(c, T, 7, 9.5, 1.0, 1.06, 1200, 520)
    kitchen(c, T, "stand", 0.0, 1, 1.0, clk(T, 9.0), gk=e(tl, 0.0, 2.4), mood="soft")
    c.restore()
    return dict(caps=[("Week 1.", 7.2, 9.4)])


def s_w1_cal(c, T):
    tl = T - 9.5
    c.save()
    push(c, T, 9.5, 12, 1.0, 1.08, 1260, 360)
    calendar_close(c, T, 1, e(tl, 0.3, 1.5))
    c.restore()
    return dict()


def s_keypad(c, T, t0):
    tl = T - t0
    n = min(10, int(tl / 0.24))
    pr = (tl % 0.24) / 0.24
    keypad_close(c, T, math.sin(math.pi * pr), n)
    return dict()


def s_w1_key(c, T):
    return s_keypad(c, T, 12.0)


def L_phone(T, mood="soft", dusk=0.0, cups=1, cup2_k=1.0):
    return lambda cc: kitchen(cc, T, "phone", dusk, cups, cup2_k, (6, 0, T % 60), mood=mood)


def s_w1_split(c, T):
    split(c, T, L_phone(T), lambda cc: apt(cc, T, "desk", 1.0, "incoming", look=0.4, mood="calm"), (6, 0, (T - 9) % 60))
    return dict()


def s_w1_desk(c, T):
    c.save()
    push(c, T, 17.5, 20, 1.0, 1.1, 1100, 640)
    apt(c, T, "desk", 1.0, "incoming", look=0.3, mood="calm")
    c.restore()
    return dict()


def s_w1_gran(c, T):
    c.save()
    push(c, T, 20, 23, 1.0, 1.06)
    gran_close(c, T, "soft", -0.3, ring=1.0, dusk=0.1)
    c.restore()
    return dict()


def s_w1_hang(c, T):
    hangup_close(c, T, e(T, 23.4, 24.9))
    return dict(caps=[("No answer.", 23.5, 25.9)])


def s_w1_sit(c, T):
    c.save()
    push(c, T, 26, 30, 1.0, 1.05, 760, 640)
    kitchen(c, T, "sit", 0.15, 1, mood="calm")
    c.restore()
    return dict()


def s_mon(c, T):
    c.save()
    push(c, T, 30, 34, 1.06, 1.0)
    office(c, T, 0.1, "calm")
    c.restore()
    return dict(caps=[("Monday.", 30.2, 33.8)], label="MONDAY")


def s_mon_phone(c, T):
    tl = T - 34
    sw = e(tl, 1.8, 2.6)
    c.save()
    c.translate(-700 * sw, 0)
    table_close(c, T, "missed", 0.0, lock=("MONDAY", "9:12"), note=("MISSED CALL", "GRANDMA", "Sunday 6:00 PM"), hand_k=0.0)
    c.restore()
    if sw > 0:
        c.save()
        c.translate(W * (1 - sw), 0)
        office(c, T, 0.0, "calm")
        c.restore()
    return dict(caps=[("He meant to call back.", 34.2, 38.8)], label="MONDAY")


def s_mon_back(c, T):
    c.save()
    push(c, T, 37, 42, 1.0, 1.12, 960, 560)
    office(c, T, 0.0, "calm")
    c.restore()
    return dict(caps=[("He meant to call back.", 34.2, 38.8)], label="MONDAY")


def s_wed(c, T):
    tl = T - 42
    train(c, T, 0.0 if tl < 2.5 else 0.1, "calm", e(tl, 2.4, 2.8))
    return dict(caps=[("Wednesday.", 42.2, 45.6)], label="WEDNESDAY")


def s_wed_phone(c, T):
    c.save()
    push(c, T, 47, 50, 1.0, 1.1, 640, 540)
    table_close(c, T, "missed", 0.0, lock=("WEDNESDAY", "8:40"), note=("MISSED CALL", "GRANDMA", "Sunday 6:00 PM"))
    c.restore()
    return dict(label="WEDNESDAY")


def s_fri(c, T):
    c.save()
    push(c, T, 50, 56, 1.0, 1.08, 900, 640)
    apt(c, T, "couch", 0.0, "down", look=0.0, mood="calm")
    laptop(c, 1240, 940, 0.55, T, "movie")
    c.restore()
    return dict(caps=[("Friday.", 50.2, 53.8)], label="FRIDAY")


def s_fri_close(c, T):
    tl = T - 56
    yawn = math.sin(math.pi * clamp((tl - 0.6) / 1.6))
    son_close(c, T, "calm", 0.0, 0.5, mouth=0.8 * yawn, up=-0.2)
    return dict(label="FRIDAY")


def s_sat(c, T):
    c.save()
    push(c, T, 59, 64, 1.0, 1.06)
    apt(c, T, "sleep", 0.0)
    c.restore()
    return dict(caps=[("Saturday.", 59.2, 63.6)], label="SATURDAY")


def s_w2_wide(c, T):
    tl = T - 64
    c.save()
    push(c, T, 64, 69, 1.0, 1.06, 1000, 700)
    kitchen(c, T, "sit", 0.1, 2, e(tl, 1.0, 2.6), clk(T, 68.5), mood="soft")
    c.restore()
    return dict(caps=[("Week 2.", 64.2, 66.8), ("She set out his cup.", 66.9, 68.9)])


def s_w2_split(c, T):
    tl = T - 69
    bz = 1.0 if tl < 3.0 else 0.0
    st = "incoming" if tl < 3.0 else "down"
    split(c, T, L_phone(T, "soft", 0.15, 2), lambda cc: apt(cc, T, "call", bz, st, look=0.0 if tl < 2.0 else 0.5, mood="calm", mouth=0.3 * max(0, math.sin(T * 8)) if tl < 2 else 0.0), (6, 0, (T - 68.5) % 60))
    return dict()


def s_w2_gran(c, T):
    tl = T - 74
    c.save()
    push(c, T, 74, 78, 1.0, 1.08, 900, 520)
    gran_close(c, T, "calm" if tl < 2.2 else "sad", -0.3, ring=1.0 if tl < 2.8 else 0.0, dusk=0.25)
    c.restore()
    return dict()


def s_w2_back(c, T):
    tl = T - 78
    c.save()
    push(c, T, 78, 83, 1.04, 1.0, 1000, 700)
    kitchen(c, T, "sit", 0.25, 2, 1 - e(tl, 1.0, 3.2), mood="sad")
    c.restore()
    return dict(caps=[("She put it back.", 79.2, 82.8)])


def s_w2_his(c, T):
    tl = T - 83
    if tl < 3.5:
        c.save()
        push(c, T, 83, 86.5, 1.0, 1.08, 640, 540)
        table_close(c, T, "missed", 0.0, lock=("SUNDAY", "7:30"), note=("MISSED CALL", "GRANDMA", "Sunday 6:00 PM"), hand_k=0.0)
        c.restore()
    else:
        son_close(c, T, "calm", -0.3, 0.4, up=-0.6)
    return dict(caps=[("Later.", 86.6, 89.6)], label="SUNDAY · 7:30 PM")


def s_w3_wide(c, T):
    tl = T - 90
    kitchen_bg(c, T, 0.2, 0.14 * (1 - e(tl, 1.0, 2.6)), clk(T, 93.5))
    gran(c, 900, 1030, 0.92, look=-0.6, mood="soft", t=T, arms="reach", k=e(tl, 0.5, 1.4) * (1 - e(tl, 2.8, 3.6)))
    kitchen_table(c, 1, 1.0, True, T, x0=760)
    return dict(caps=[("Week 3.", 90.2, 93.6)])


def s_w3_split(c, T):
    split(c, T, L_phone(T, "calm", 0.3), lambda cc: apt(cc, T, "sleep", 1.0), (6, 0, (T - 93.5) % 60))
    return dict()


def s_w3_gran(c, T):
    tl = T - 99
    c.save()
    push(c, T, 99, 104, 1.0, 1.1, 900, 520)
    gran_close(c, T, "worry" if tl < 3 else "sad", -0.2, ring=1.0 if tl < 4.2 else 0.0, dusk=0.4, up=-0.2)
    c.restore()
    return dict()


def s_w3_sit(c, T):
    c.save()
    push(c, T, 104, 110, 1.0, 1.1, 760, 640)
    kitchen(c, T, "sit", 0.6, 1, mood="sad")
    c.restore()
    return dict()


def s_w4_phone(c, T):
    tl = T - 110
    tm = "5:58" if tl < 2.5 else "5:59"
    c.save()
    push(c, T, 110, 115, 1.0, 1.1, 640, 540)
    table_close(c, T, "missed", 0.0, lock=("SUNDAY", tm), note=None)
    c.restore()
    return dict(caps=[("Week 4.", 110.2, 113.4), ("He watched the clock.", 113.5, 114.9)])


def s_w4_cup(c, T):
    tl = T - 115
    c.save()
    push(c, T, 115, 119, 1.0, 1.06, 1000, 700)
    kitchen(c, T, "sit", 0.3, 2, e(tl, 0.4, 2.0), clk(T, 118.5), mood="soft")
    c.restore()
    return dict(caps=[("He watched the clock.", 115.0, 115.6)])


def s_w4_down(c, T):
    tl = T - 119
    k = e(tl, 0.2, 0.9)
    f = math.cos(math.pi * k)
    c.save()
    push(c, T, 119, 124, 1.0, 1.06)
    table_close(c, T, "incoming", 1.0, flip=f if abs(f) > 0.04 else -0.04, hand_k=(1 - e(tl, 1.0, 1.8)) if tl > 0.9 else clamp(tl / 0.3))
    c.restore()
    return dict(caps=[("He turned it over.", 120.3, 123.6)])


def s_w4_split(c, T):
    split(c, T, lambda cc: gran_close(cc, T, "worry", -0.3, 0.0, ring=1.0, dusk=0.45), lambda cc: son_close(cc, T, "worry", 0.0, 0.5, up=-0.7), (6, 0, (T - 118.5) % 60))
    return dict()


def s_w4_sit(c, T):
    c.save()
    push(c, T, 129, 134, 1.0, 1.12, 1000, 620)
    kitchen(c, T, "sit", 0.5, 2, 1.0, mood="sad")
    c.restore()
    return dict(caps=[("This time, she left it out.", 130.2, 133.8)])


def s_quiet(c, T):
    c.save()
    push(c, T, 134, 140, 1.0, 1.12, 780, 500)
    son_close(c, T, "sad", 0.0, 0.0, up=-0.5)
    c.set_source_rgba(0, 0, 0, 0.25)
    c.paint()
    c.restore()
    return dict()


def s_card5(c, T):
    card(c, "Week 5.", e(T, 140, 140.35))
    return dict(card=True)


def s_w5_wait(c, T):
    tl = T - 142
    tm = "5:59" if tl < 2.6 else "6:00"
    c.save()
    push(c, T, 142, 146, 1.0, 1.1, 640, 540)
    table_close(c, T, "missed", 0.0, lock=("SUNDAY", tm), note=None, hand_k=1.0)
    c.restore()
    return dict(caps=[("This time, he was waiting.", 142.4, 145.8)])


def s_w5_key(c, T):
    return s_keypad(c, T, 146.0)


def s_w5_pick(c, T):
    tl = T - 149
    bz = 1.0 if T < PICKUP else 0.0
    table_close(c, T, "incoming", bz, hand_k=e(tl, 0.65, 1.0))
    if T >= PICKUP:
        c.set_source_rgba(1, 1, 1, 0.5 * (1 - e(T, PICKUP, PICKUP + 0.4)))
        c.paint()
    return dict(caps=[("First ring.", 150.3, 151.9)])


def s_w5_gran(c, T):
    tl = T - 152
    mood = "surprise" if tl < 1.6 else "joy"
    c.save()
    push(c, T, 152, 157, 1.0, 1.08, 900, 520)
    gran_close(c, T, mood, -0.2, tear=e(tl, 2.0, 4.0) * 0.6, up=0.4 if tl < 1.6 else 0.1, mouth=0.4 if tl < 1.6 else 0.0, dusk=0.4)
    c.restore()
    return dict()


def pour_close(c, T, k):
    vgrad(c, 0, 0, W, H, mix(ROSE, ROSE_D, 0.5), (0.40, 0.25, 0.28))
    c.set_source_rgb(*CREAM)
    ell(c, W / 2, 900, 900, 160)
    c.fill()
    tea_cup(c, 1080, 860, 3.0, col=(0.98, 0.90, 0.80), band=RED, full=clamp(k), steam=T if k > 0.7 else None)
    tilt = lerp(0.1, 0.65, e(k, 0.0, 0.2)) * (1 - e(k, 0.92, 1.0) * 0.8)
    teapot(c, 640, 560, 2.4, tilt)
    if 0.12 < k < 0.94:
        c.set_source_rgba(*TEA, 0.95)
        c.set_line_width(16 + 4 * math.sin(T * 20))
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        sx = 640 + 2.4 * (130 * math.cos(tilt) + 120 * math.sin(tilt))
        sy = 560 + 2.4 * (130 * math.sin(tilt) - 120 * math.cos(tilt))
        c.move_to(sx, sy)
        c.curve_to(sx + 30, sy + 120, 1070, 560, 1075, 700)
        c.stroke()
    c.set_source_rgb(*PLUM)
    c.set_line_width(110)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    hx = 640 + 2.4 * (-112 * math.cos(tilt) + 60 * math.sin(tilt))
    hy = 560 + 2.4 * (-112 * math.sin(tilt) - 60 * math.cos(tilt))
    c.move_to(-60, hy + 300)
    c.line_to(hx - 40, hy + 30)
    c.stroke()
    hand(c, hx, hy, GRAN_SKIN, 54)


def s_pour(c, T):
    tl = T - 157
    pour_close(c, T, e(tl, 0.3, 4.2))
    return dict(caps=[("She poured his cup.", 157.4, 161.6)])


LINE = "Hi, Grandma. Sorry I'm late."
LINE_T = 162.5
LAUGH_T = 166.6


def s_talk(c, T):
    talk = 0.6 * max(0, math.sin(T * 11)) if LINE_T < T < LINE_T + 2.6 else 0.0
    laugh = 0.7 * max(0, math.sin(T * 14)) if LAUGH_T < T < LAUGH_T + 2.6 else 0.0
    split(c, T, lambda cc: gran_close(cc, T, "joy", -0.1, 0.5, up=0.2, mouth=laugh, dusk=0.45), lambda cc: son_close(cc, T, "joy" if T > LINE_T + 1.6 else "soft", 0.0, 0.3, mouth=talk, phone=True), (6, 1, T % 60))
    return dict(caps=[(LINE, LINE_T, LINE_T + 3.6)], label="PICKED UP · RING 1")


def sprout(c, cx, cy, s=1.0, a=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.set_source_rgba(0.93, 0.70, 0.25, a)
    c.arc(0, 30, 120, math.pi, 2 * math.pi)
    c.fill()
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(7):
        ang = math.pi + (i + 0.5) * math.pi / 7
        c.move_to(140 * math.cos(ang), 30 + 140 * math.sin(ang))
        c.line_to(195 * math.cos(ang), 30 + 195 * math.sin(ang))
        c.stroke()
    c.set_source_rgba(0.30, 0.24, 0.20, a)
    c.rectangle(-260, 30, 520, 12)
    c.fill()
    c.set_source_rgba(0.33, 0.62, 0.32, a)
    c.set_line_width(14)
    c.move_to(0, 30)
    c.curve_to(0, -10, 4, -30, 2, -55)
    c.stroke()
    for sg in (-1, 1):
        c.new_path()
        c.move_to(2, -40)
        c.curve_to(sg * 30, -100, sg * 90, -90, sg * 92, -70)
        c.curve_to(sg * 70, -30, sg * 30, -30, 2, -40)
        c.fill()
    c.restore()


def end_card(c, T, vw=W, vh=H, vertical=False):
    vgrad(c, 0, 0, vw, vh, PAPER, (0.95, 0.90, 0.82))
    c.set_source_rgb(*RED)
    c.rectangle(0, 0, vw, 26)
    c.fill()
    tl = T
    cx = vw / 2
    if vertical:
        sprout(c, cx, 560, 1.1)
        text(c, "Small Win Films", cx, 820, 92, PLUM_D)
        text(c, "Who's still waiting", cx, 1010, 70, INK)
        text(c, "for your call?", cx, 1100, 70, INK)
        marker_circle(c, cx, 1060, 430, 110, e(tl, 0.4, 1.6), 9, RED, 1.0, 5)
        pill = "SUBSCRIBE FOR THE NEXT FILM"
        c.select_font_face(FONT)
        c.set_font_size(44)
        w = c.text_extents(pill).x_advance + 80
        c.set_source_rgb(*PLUM)
        rr(c, (vw - w) / 2, 1250, w, 96, 48)
        c.fill()
        text(c, pill, cx, 1314, 44, CREAM)
        return
    sprout(c, cx, 330, 0.85)
    text(c, "Small Win Films", cx, 560, 92, PLUM_D)
    text(c, "Who's still waiting for your call?", cx, 730, 66, INK)
    marker_circle(c, cx, 708, 640, 80, e(tl, 0.4, 1.6), 9, RED, 1.0, 5)
    text(c, "Small stories. Small wins.", cx, 900, 40, PLUM, 1.0, "c", FONTB)


def s_end(c, T):
    end_card(c, T - 172)
    return dict(card=True)


SCENES = [
    S(0, 1.7, s_open_a), S(1.7, 3.1, s_open_b), S(3.1, 5.0, s_open_c), S(5.0, 7.0, s_card),
    S(7.0, 9.5, s_w1_wide), S(9.5, 12.0, s_w1_cal), S(12.0, 14.5, s_w1_key), S(14.5, 17.5, s_w1_split),
    S(17.5, 20.0, s_w1_desk), S(20.0, 23.0, s_w1_gran), S(23.0, 26.0, s_w1_hang), S(26.0, 30.0, s_w1_sit),
    S(30.0, 34.0, s_mon), S(34.0, 37.0, s_mon_phone), S(37.0, 42.0, s_mon_back), S(42.0, 47.0, s_wed),
    S(47.0, 50.0, s_wed_phone), S(50.0, 56.0, s_fri), S(56.0, 59.0, s_fri_close), S(59.0, 64.0, s_sat),
    S(64.0, 69.0, s_w2_wide), S(69.0, 74.0, s_w2_split), S(74.0, 78.0, s_w2_gran), S(78.0, 83.0, s_w2_back),
    S(83.0, 90.0, s_w2_his), S(90.0, 94.0, s_w3_wide), S(94.0, 99.0, s_w3_split), S(99.0, 104.0, s_w3_gran),
    S(104.0, 110.0, s_w3_sit), S(110.0, 115.0, s_w4_phone), S(115.0, 119.0, s_w4_cup), S(119.0, 124.0, s_w4_down),
    S(124.0, 129.0, s_w4_split), S(129.0, 134.0, s_w4_sit), S(134.0, 140.0, s_quiet), S(140.0, 142.0, s_card5),
    S(142.0, 146.0, s_w5_wait), S(146.0, 149.0, s_w5_key), S(149.0, 152.0, s_w5_pick), S(152.0, 157.0, s_w5_gran),
    S(157.0, 162.0, s_pour), S(162.0, 172.0, s_talk), S(172.0, 180.0, s_end),
]
DUR = 180.0


def scene_at(T):
    for t0, t1, fn in SCENES:
        if t0 <= T < t1:
            return fn
    return SCENES[-1][2]


def frame(c, T, hud=True):
    st = scene_at(T)(c, T)
    if st.get("card"):
        return st
    g = cairo.LinearGradient(0, H - 280, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    c.set_source(g)
    c.rectangle(0, H - 280, W, 280)
    c.fill()
    if hud:
        circ, pop = ctr_anim(T)
        big = 1.0 if T < 2.9 else 1 - e(T, 2.9, 4.2)
        counter(c, ctr_n(T), st.get("label", "SUNDAY · 6:00 PM"), 1.0, big, circ, pop)
    for s, a, b in st.get("caps", []):
        if a <= T <= b:
            k = e(T, a, a + 0.22) * (1 - e(T, b - 0.22, b))
            caption(c, s, k)
    return st


def pipe(out, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (w, h), "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)


def render(t0, t1, out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    p = pipe(out, W, H)
    for i in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        c.save()
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame(c, i / FPS)
        c.restore()
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    print("done", out, flush=True)


def stills(times, outdir):
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    for T in times:
        c.save()
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame(c, T)
        c.restore()
        surf.write_to_png("%s/f_%06.2f.png" % (outdir, T))


if __name__ == "__main__":
    if sys.argv[1] == "render":
        render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "stills":
        stills([float(x) for x in sys.argv[3:]], sys.argv[2])
