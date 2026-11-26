import cairo, math, os, subprocess, sys
from PIL import Image
from pc_common import (
    VW, VH, FPS, H, M,
    TEAL_DARK, TEAL, TEAL_LT, CHERRY, CHERRY_DARK, CREAM, CREAM_WARM,
    KRAFT, KRAFT_DARK, INK, PURPLE, MUSTARD, NIGHT, NIGHT_WIN, GOLD,
    SKIN, SKIN_SH, HAIR, WHITE,
    clamp, lerp, ease, ease_out, back_out,
    font, txt, rrect, caption_card, punch_card_counter,
    draw_woman, draw_mom, sprout, draw_safe_zones,
)

TOTAL_FRAMES = 1246
DUR = TOTAL_FRAMES / FPS

# Key event times shared with pc_audio.py
STAMP_TIMES = [4.9, 5.5, 6.1, 7.1, 7.8]
ENV_TEAR_T = 9.2
SNIP_TIMES = [11.3, 12.6, 13.9, 15.2]
SHOCK_T = 16.2
CARD_SLIDE_T = 26.0
PAID_STAMP_T = 27.2
CIRCLE_T = 33.4
END_T = 35.5

DEDUCTIONS = [
    ("FEDERAL TAX", "-$60", 1140),
    ("SOCIAL SECURITY", "-$74", 1066),
    ("MEDICARE", "-$17", 1049),
    ("STATE TAX", "-$39", 1010),
]


def bg_diner_wall(c, warm=0.0):
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, lerp(TEAL_DARK[0], 0.14, warm), lerp(TEAL_DARK[1], 0.34, warm), lerp(TEAL_DARK[2], 0.35, warm))
    g.add_color_stop_rgb(0.55, TEAL[0], TEAL[1], TEAL[2])
    g.add_color_stop_rgb(1, TEAL_DARK[0], TEAL_DARK[1], TEAL_DARK[2])
    c.set_source(g)
    c.paint()
    # Subtle cream subway tile band in mid wall
    c.set_source_rgba(*CREAM, 0.10)
    for y in range(240, 1480, 64):
        c.rectangle(0, y, VW, 2)
    c.fill()
    # Cherry chrome trim stripe
    c.set_source_rgb(*CHERRY)
    c.rectangle(0, 1440, VW, 26)
    c.fill()
    c.set_source_rgb(*CREAM_WARM)
    c.rectangle(0, 1466, VW, 454)
    c.fill()
    # Checkered diner floor edge to edge
    sq = 90
    c.set_source_rgba(*TEAL_DARK, 0.22)
    for row in range(6):
        for col in range(13):
            if (row + col) % 2 == 0:
                c.rectangle(col * sq, 1466 + row * sq, sq, sq)
    c.fill()


def draw_scene_1_clock(c, t):
    # Vintage diner time clock wall, full bleed
    bg_diner_wall(c)
    slam = back_out(t, 0.0, 0.28)
    shake = math.sin(t * 70) * 10 * max(0, 1 - t / 0.22)
    c.save()
    c.translate(shake, 0)
    # Time clock metal housing
    cx, cy = VW / 2, 815
    rrect(c, cx - 240, cy - 260, 480, 440, 44)
    c.set_source_rgb(0.16, 0.20, 0.22)
    c.fill()
    rrect(c, cx - 220, cy - 240, 440, 400, 34)
    c.set_source_rgb(*TEAL_DARK)
    c.fill()
    # Chrome bezel ring & clock face
    c.set_source_rgb(*CREAM_WARM)
    c.arc(cx, cy - 75, 130, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*CREAM)
    c.arc(cx, cy - 75, 114, 0, 2 * math.pi)
    c.fill()
    # Clock ticks
    c.set_source_rgb(*INK)
    for k in range(12):
        ang = k * math.pi / 6
        c.set_line_width(6 if k % 3 == 0 else 3)
        c.move_to(cx + math.cos(ang) * 88, cy - 75 + math.sin(ang) * 88)
        c.line_to(cx + math.cos(ang) * 104, cy - 75 + math.sin(ang) * 104)
        c.stroke()
    # Hands moving briskly on frame 1
    ang_m = -math.pi / 2 + t * 2.2
    ang_h = -math.pi / 2 + 1.4 + t * 0.2
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(9)
    c.move_to(cx, cy - 75)
    c.line_to(cx + math.cos(ang_h) * 58, cy - 75 + math.sin(ang_h) * 58)
    c.stroke()
    c.set_line_width(6)
    c.set_source_rgb(*CHERRY)
    c.move_to(cx, cy - 75)
    c.line_to(cx + math.cos(ang_m) * 86, cy - 75 + math.sin(ang_m) * 86)
    c.stroke()
    # Card slot
    rrect(c, cx - 165, cy + 88, 330, 24, 8)
    c.set_source_rgb(*INK)
    c.fill()
    # Manila card slamming down into slot
    card_y = lerp(cy + 30, cy + 100, slam)
    rrect(c, cx - 145, card_y, 290, 220, 12)
    c.set_source_rgb(*KRAFT)
    c.fill()
    rrect(c, cx - 133, card_y + 12, 266, 196, 8)
    c.set_source_rgba(*INK, 0.35)
    c.set_line_width(2.5)
    c.stroke()
    txt(c, "TIME CARD", cx, card_y + 48, 24, INK, M, "c", 0.8)
    txt(c, "80 HRS", cx, card_y + 132, 62, PURPLE, M, "c", 1.0)
    txt(c, "STAMPED", cx, card_y + 182, 22, CHERRY, M, "c", 0.9)
    # Impact lines on frame 1..0.4
    if t < 0.45:
        ia = 1 - t / 0.45
        c.set_source_rgba(*GOLD, ia)
        c.set_line_width(8)
        for k in range(6):
            ang = math.pi * 0.15 + k * math.pi * 0.14
            r0 = 250 + t * 140
            r1 = r0 + 55
            c.move_to(cx + math.cos(ang) * r0, cy + 70 + math.sin(ang) * r0 * 0.6)
            c.line_to(cx + math.cos(ang) * r1, cy + 70 + math.sin(ang) * r1 * 0.6)
            c.stroke()
    c.restore()

    # Big HOURS 80 badge shrinking up into the punch-card counter
    shrink = ease(t, 1.35, 2.2)
    cy_card = lerp(455, 366, shrink)
    sc_card = lerp(1.32, 1.0, shrink)
    punch_card_counter(c, 80, stamp_pulse=max(0, 1 - t / 0.35), a=1.0, scale=sc_card, cy=cy_card)
    caption_card(c, ["80 hours.", "Her first paycheck."], y_center=1215, a=1.0, size=56)


def draw_scene_2_day1(c, t):
    lt = t - 2.5
    bg_diner_wall(c, warm=0.3)
    # Diner back shelf with coffee pots
    c.set_source_rgb(*CREAM_WARM)
    c.rectangle(0, 620, VW, 26)
    c.fill()
    for sx in (180, 880):
        rrect(c, sx - 45, 510, 90, 110, 24)
        c.set_source_rgba(*INK, 0.25)
        c.fill()
        rrect(c, sx - 38, 550, 76, 66, 16)
        c.set_source_rgb(0.32, 0.18, 0.10)
        c.fill()
    # Slow push-in on her tying her apron
    sc = lerp(2.05, 2.22, lt / 2.0)
    bob = math.sin(lt * 5.0) * 6
    draw_woman(c, VW / 2, 870 + bob, scale=sc, mood="nervous", uniform=True)
    # Hands tying apron strings
    knot = ease(lt, 0.2, 1.4)
    for sx in (-1, 1):
        hx = VW / 2 + sx * lerp(175, 92, knot)
        hy = 1040 + math.sin(lt * 8) * 10
        c.set_source_rgb(*SKIN)
        c.arc(hx, hy, 34, 0, 2 * math.pi)
        c.fill()
    punch_card_counter(c, 0, a=1.0)
    caption_card(c, "Day 1.", y_center=1215, a=ease(lt, 0.0, 0.25))


def draw_scene_3_shifts(c, t):
    lt = t - 4.5
    bg_diner_wall(c, warm=0.1)
    # Diner window behind with passing afternoon light
    rrect(c, 90, 460, 900, 440, 28)
    c.set_source_rgb(0.95, 0.84, 0.62)
    c.fill()
    c.set_source_rgba(*WHITE, 0.35)
    c.move_to(220, 460)
    c.line_to(380, 460)
    c.line_to(240, 900)
    c.line_to(80, 900)
    c.close_path()
    c.fill()
    # Her walking briskly carrying 4 plates on raised arms
    walk_x = VW / 2 + math.sin(lt * 5.5) * 44
    bob = abs(math.sin(lt * 9.0)) * 14
    draw_woman(c, walk_x, 865 - bob, scale=1.78, mood="smile", uniform=True)
    # Raised server arms
    c.set_source_rgb(*SKIN)
    c.set_line_width(34)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        c.move_to(walk_x + sx * 165, 1020 - bob * 0.7)
        c.line_to(walk_x + sx * 270, 930 - bob * 0.7)
        c.stroke()
    # Four balanced plates
    for px, py in ((walk_x - 300, 915), (walk_x - 230, 845), (walk_x + 300, 910), (walk_x + 230, 840)):
        c.save()
        c.translate(px, py - bob * 0.7)
        c.set_source_rgb(*CREAM)
        c.scale(1.0, 0.34)
        c.arc(0, 0, 74, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*CHERRY)
        c.arc(0, -10, 46, 0, 2 * math.pi)
        c.fill()
        c.restore()
    # Hours climbing with purple stamps at 4.9, 5.5, 6.1
    hrs = 0
    pulse = 0.0
    for st, val in ((4.9, 8), (5.5, 16), (6.1, 24)):
        if t >= st:
            hrs = val
            pulse = max(pulse, max(0, 1 - (t - st) / 0.25))
    punch_card_counter(c, hrs, stamp_pulse=pulse)
    caption_card(c, "Double shifts.", y_center=1215, a=ease(lt, 0.0, 0.25))


def draw_scene_4_bus(c, t):
    lt = t - 6.5
    # Night bus interior full bleed
    c.set_source_rgb(*NIGHT)
    c.paint()
    # Bus window with drifting city lights
    rrect(c, 50, 430, 980, 560, 36)
    c.set_source_rgb(*NIGHT_WIN)
    c.fill()
    c.save()
    rrect(c, 50, 430, 980, 560, 36)
    c.clip()
    for k in range(14):
        bx = ((k * 165 - lt * 340) % 1300) - 120
        bh = 120 + (k * 47) % 210
        c.set_source_rgb(0.06, 0.10, 0.16)
        c.rectangle(bx, 990 - bh, 110, bh)
        c.fill()
        c.set_source_rgba(*GOLD, 0.65)
        for wy in range(990 - bh + 22, 970, 38):
            c.rectangle(bx + 20, wy, 20, 16)
            c.rectangle(bx + 62, wy, 20, 16)
        c.fill()
    c.restore()
    # Bus seat back & rail
    c.set_source_rgb(0.18, 0.26, 0.34)
    rrect(c, 220, 760, 640, 720, 44)
    c.fill()
    # Her leaning tiredly, eyes closed, gentle bus sway
    sway = math.sin(lt * 3.8) * 8
    c.save()
    c.translate(VW / 2 + sway, 900)
    c.rotate(-0.08)
    draw_woman(c, 0, 0, scale=1.82, mood="sleep", uniform=True)
    c.restore()
    # Shoes kicked off at bottom (decoration zone)
    for sx, rot in ((370, -0.25), (650, 0.18)):
        c.save()
        c.translate(sx, 1600)
        c.rotate(rot)
        c.set_source_rgb(*CHERRY_DARK)
        rrect(c, -62, -24, 124, 48, 22)
        c.fill()
        c.restore()
    hrs = 48
    pulse = 0.0
    for st, val in ((7.1, 64), (7.8, 80)):
        if t >= st:
            hrs = val
            pulse = max(pulse, max(0, 1 - (t - st) / 0.25))
    punch_card_counter(c, hrs, stamp_pulse=pulse)
    caption_card(c, "Day 10.", y_center=1215, a=ease(lt, 0.0, 0.25))


def draw_pay_stub(c, cx, cy, gross=1200, net=1200, snipped=0, snip_prog=0.0, circle_prog=0.0, show_net=True, scale=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    w, h = 780, 620
    x, y = -w / 2, -h / 2
    # Shadow
    rrect(c, x + 10, y + 14, w, h, 18)
    c.set_source_rgba(0, 0, 0, 0.26)
    c.fill()
    # Cream stub paper
    rrect(c, x, y, w, h, 18)
    c.set_source_rgb(*CREAM)
    c.fill()
    # Top teal header bar
    c.save()
    rrect(c, x, y, w, h, 18)
    c.clip()
    c.set_source_rgb(*TEAL_DARK)
    c.rectangle(x, y, w, 92)
    c.fill()
    c.restore()
    txt(c, "PAY STUB · BIWEEKLY", x + 36, y + 58, 30, CREAM, M, "l", 1.0)
    # EXAMPLE stamp in top right
    c.save()
    c.translate(x + w - 108, y + 48)
    c.rotate(-0.08)
    rrect(c, -76, -24, 152, 48, 8)
    c.set_source_rgba(*GOLD, 0.22)
    c.fill()
    rrect(c, -76, -24, 152, 48, 8)
    c.set_source_rgb(*GOLD)
    c.set_line_width(3)
    c.stroke()
    txt(c, "EXAMPLE", 0, 10, 24, GOLD, M, "c", 1.0)
    c.restore()

    # Gross pay row
    txt(c, "GROSS PAY (80 HRS)", x + 38, y + 150, 28, INK, M, "l", 0.78)
    txt(c, f"${gross:,}", x + w - 38, y + 154, 46, TEAL_DARK, M, "r", 1.0)
    c.set_source_rgba(*INK, 0.2)
    c.set_line_width(2)
    c.move_to(x + 36, y + 174)
    c.line_to(x + w - 36, y + 174)
    c.stroke()

    # Deduction rows
    for idx, (label, amt, _) in enumerate(DEDUCTIONS):
        ry = y + 200 + idx * 66
        if idx < snipped:
            # Already snipped away: faint dashed empty slot
            c.set_source_rgba(*CHERRY, 0.22)
            c.set_line_width(2)
            c.set_dash([8, 8])
            c.move_to(x + 36, ry + 26)
            c.line_to(x + w - 36, ry + 26)
            c.stroke()
            c.set_dash([])
            txt(c, f"{label}  {amt}", x + 38, ry + 34, 24, CHERRY, M, "l", 0.42)
        elif idx == snipped and snip_prog > 0.0:
            # Peeling / falling strip
            c.save()
            drop = ease(snip_prog, 0.35, 1.0)
            c.translate(x + 34 + drop * 110, ry + drop * 220)
            c.rotate(drop * 0.28)
            rrect(c, 0, 0, w - 68, 54, 8)
            c.set_source_rgba(*CHERRY, 0.92 * (1 - drop * 0.85))
            c.fill()
            txt(c, label, 22, 36, 26, CREAM, M, "l", 1 - drop * 0.85)
            txt(c, amt, w - 90, 36, 30, CREAM, M, "r", 1 - drop * 0.85)
            c.restore()
            # Animated scissor cut line across row
            if snip_prog < 0.55:
                sx = lerp(x + 28, x + w - 28, snip_prog / 0.55)
                c.set_source_rgb(*CHERRY)
                c.set_line_width(4)
                c.set_dash([10, 6])
                c.move_to(x + 28, ry + 26)
                c.line_to(sx, ry + 26)
                c.stroke()
                c.set_dash([])
                # Little scissor icon at sx
                c.set_source_rgb(*INK)
                c.set_line_width(5)
                c.arc(sx + 18, ry + 14, 9, 0, 2 * math.pi)
                c.stroke()
                c.arc(sx + 18, ry + 38, 9, 0, 2 * math.pi)
                c.stroke()
                c.move_to(sx + 9, ry + 20)
                c.line_to(sx - 18, ry + 32)
                c.move_to(sx + 9, ry + 32)
                c.line_to(sx - 18, ry + 20)
                c.stroke()
        else:
            rrect(c, x + 34, ry, w - 68, 54, 8)
            c.set_source_rgba(*KRAFT, 0.45)
            c.fill()
            txt(c, label, x + 56, ry + 36, 26, INK, M, "l", 0.85)
            txt(c, amt, x + w - 56, ry + 36, 30, CHERRY_DARK, M, "r", 0.95)

    # Net pay footer
    c.set_source_rgba(*INK, 0.35)
    c.set_line_width(3)
    c.move_to(x + 36, y + 480)
    c.line_to(x + w - 36, y + 480)
    c.stroke()
    txt(c, "TAKE-HOME PAY", x + 38, y + 552, 30, INK, M, "l", 1.0)
    if show_net:
        txt(c, f"${net:,}", x + w - 38, y + 562, 62, TEAL_DARK if net == 1200 else CHERRY_DARK, M, "r", 1.0)
    else:
        rrect(c, x + w - 260, y + 506, 224, 72, 12)
        c.set_source_rgb(*KRAFT_DARK)
        c.fill()
        txt(c, "$???", x + w - 148, y + 558, 48, INK, M, "c", 0.85)

    # Cherry marker circle around $46.80 dinner note if requested
    if circle_prog > 0.01:
        rrect(c, x + 38, y + 250, w - 76, 170, 14)
        c.set_source_rgb(*CREAM_WARM)
        c.fill()
        txt(c, "FIRST EXPENSE", x + 64, y + 306, 26, INK, M, "l", 0.75)
        txt(c, "DINNER FOR MOM", x + 64, y + 362, 34, INK, H, "l", 1.0)
        txt(c, "$46.80", x + w - 70, y + 364, 54, CHERRY, M, "r", 1.0)
        # Hand-drawn cherry circle
        c.set_source_rgb(*CHERRY)
        c.set_line_width(9)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        end_ang = -math.pi * 0.2 + circle_prog * math.pi * 2.15
        c.save()
        c.translate(x + w - 160, y + 345)
        c.scale(1.65, 0.72)
        c.arc(0, 0, 74, -math.pi * 0.2, end_ang)
        c.stroke()
        c.restore()
    c.restore()


def draw_scene_5_envelope(c, t):
    lt = t - 8.5
    # Diner wood counter top-down
    c.set_source_rgb(0.28, 0.20, 0.15)
    c.paint()
    c.set_source_rgba(0.18, 0.12, 0.08, 0.35)
    for y in range(0, VH, 140):
        c.rectangle(0, y, VW, 6)
    c.fill()
    # Envelope slides in, tears open, stub rises out
    slide = ease_out(lt, 0.0, 0.6)
    tear = ease(lt, 0.65, 1.15)
    rise = back_out(lt, 1.05, 1.85)
    # Stub rising from envelope
    stub_y = lerp(840, 720, rise)
    stub_sc = lerp(0.68, 1.0, rise)
    if rise > 0.02:
        draw_pay_stub(c, VW / 2, stub_y, gross=1200, net=1200, snipped=0, scale=stub_sc)
    # Kraft envelope sliding down below the caption as stub rises
    env_y = lerp(680, 1470, rise) + (1 - slide) * -420
    c.save()
    c.translate(VW / 2, env_y)
    rrect(c, -360, -150, 720, 300, 18)
    c.set_source_rgb(*KRAFT)
    c.fill()
    rrect(c, -360, -150, 720, 300, 18)
    c.set_source_rgb(*KRAFT_DARK)
    c.set_line_width(4)
    c.stroke()
    # Torn top strip
    c.save()
    c.translate(tear * 240, -150 - tear * 110)
    c.rotate(tear * 0.35)
    c.set_source_rgba(*KRAFT_DARK, 1 - tear * 0.8)
    c.rectangle(-360, -34, 720, 36)
    c.fill()
    c.restore()
    txt(c, "PAYROLL · CONFIDENTIAL", 0, 20, 30, INK, M, "c", 0.65)
    c.restore()
    punch_card_counter(c, 80, a=1.0 - ease(lt, 0.6, 1.1))
    caption_card(c, "$1,200.", y_center=1215, a=ease(lt, 1.0, 1.3), accent=TEAL_LT, size=66)


def draw_scene_6_taxes(c, t):
    lt = t - 11.0
    # Warm cream counter background
    c.set_source_rgb(*TEAL_DARK)
    c.paint()
    c.set_source_rgba(*CREAM, 0.06)
    for x in range(0, VW, 80):
        c.rectangle(x, 0, 2, VH)
    c.fill()

    if t < SHOCK_T:
        snipped = 0
        snip_prog = 0.0
        net = 1200
        for idx, st in enumerate(SNIP_TIMES):
            if t >= st + 0.95:
                snipped = idx + 1
                net = DEDUCTIONS[idx][2]
            elif t >= st:
                snipped = idx
                snip_prog = clamp((t - st) / 0.95)
                prev_net = 1200 if idx == 0 else DEDUCTIONS[idx - 1][2]
                net = int(lerp(prev_net, DEDUCTIONS[idx][2], ease(snip_prog, 0.25, 0.9)))
                break
        draw_pay_stub(c, VW / 2, 725, gross=1200, net=net, snipped=snipped, snip_prog=snip_prog, scale=1.05)
        if t < 15.2:
            caption_card(c, "Then the taxes came.", y_center=1215, a=ease(lt, 0.0, 0.25))
        else:
            caption_card(c, "$1,010 left.", y_center=1215, a=1.0, accent=CHERRY, size=62)
    else:
        # Her shocked reaction close-up holding the stub
        st = t - SHOCK_T
        bg_diner_wall(c, warm=0.15)
        draw_woman(c, VW / 2, 760, scale=2.25, mood="shock", uniform=True)
        # Stub held at chest height
        c.save()
        c.translate(VW / 2, 1020)
        c.rotate(-0.04)
        rrect(c, -180, -70, 360, 140, 12)
        c.set_source_rgb(*CREAM)
        c.fill()
        txt(c, "NET: $1,010", 0, 14, 38, CHERRY_DARK, M, "c", 1.0)
        c.restore()
        caption_card(c, "$1,010 left.", y_center=1215, a=1.0, accent=CHERRY, size=62)


def draw_scene_7_photo(c, t):
    lt = t - 18.0
    # Soft warm evening flat wall
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.14, 0.28, 0.32)
    g.add_color_stop_rgb(1, 0.08, 0.16, 0.20)
    c.set_source(g)
    c.paint()
    # Close-up of her, expression warming as she looks at her phone photo
    mood = "tired" if lt < 1.1 else "smile"
    draw_woman(c, VW / 2 - 110, 740, scale=1.95, mood=mood, uniform=False)
    # Phone rising on the right showing warm photo of her and Mom (no names)
    lift = back_out(lt, 0.4, 1.2)
    px, py = 745, lerp(1120, 740, lift)
    c.save()
    c.translate(px, py)
    c.rotate(0.06)
    rrect(c, -155, -245, 310, 490, 36)
    c.set_source_rgb(*INK)
    c.fill()
    rrect(c, -140, -230, 280, 460, 26)
    c.set_source_rgb(0.96, 0.86, 0.68)
    c.fill()
    # Clip photo content inside phone screen
    c.save()
    rrect(c, -140, -230, 280, 460, 26)
    c.clip()
    txt(c, "6:15", 0, -150, 48, INK, H, "c", 0.75)
    # Mini warm portrait of Mom and daughter
    draw_mom(c, -52, 60, scale=0.62, mood="warm")
    draw_woman(c, 54, 72, scale=0.58, mood="smile", uniform=False)
    c.restore()
    c.restore()
    caption_card(c, "She knew the first thing.", y_center=1215, a=ease(lt, 0.15, 0.45), accent=GOLD)


def draw_scene_8_booth(c, t):
    lt = t - 21.5
    # Warm evening restaurant booth, cherry & amber glow
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.24, 0.11, 0.12)
    g.add_color_stop_rgb(0.55, 0.38, 0.17, 0.15)
    g.add_color_stop_rgb(1, 0.20, 0.11, 0.09)
    c.set_source(g)
    c.paint()
    # Hanging amber lamp glow
    rg = cairo.RadialGradient(VW / 2, 340, 20, VW / 2, 540, 560)
    rg.add_color_stop_rgba(0, 1.0, 0.85, 0.45, 0.42)
    rg.add_color_stop_rgba(1, 1.0, 0.85, 0.45, 0.0)
    c.set_source(rg)
    c.paint()
    # Lamp shade (decoration)
    c.set_source_rgb(*MUSTARD)
    c.arc(VW / 2, 230, 110, math.pi, 2 * math.pi)
    c.fill()
    # Cherry booth seats
    c.set_source_rgb(*CHERRY_DARK)
    rrect(c, 40, 620, 320, 460, 34)
    rrect(c, 720, 620, 320, 460, 34)
    c.fill()
    # Mom left, daughter right
    draw_mom(c, 260, 740, scale=1.32, mood="warm")
    draw_woman(c, 820, 750, scale=1.28, mood="smile", uniform=False)
    # Restaurant wood table
    c.set_source_rgb(0.42, 0.27, 0.18)
    rrect(c, 60, 910, 960, 240, 24)
    c.fill()
    # Two dinner plates
    for px in (310, 770):
        c.set_source_rgb(*CREAM)
        c.save()
        c.translate(px, 990)
        c.scale(1.0, 0.34)
        c.arc(0, 0, 86, 0, 2 * math.pi)
        c.fill()
        c.restore()
    # Black check folder slides to center of table
    chk = ease_out(lt, 0.4, 1.2)
    cx = lerp(540, 540, chk)
    cy = lerp(890, 985, chk)
    c.save()
    c.translate(cx, cy)
    rrect(c, -74, -46, 148, 92, 10)
    c.set_source_rgb(*INK)
    c.fill()
    txt(c, "CHECK", 0, 10, 22, GOLD, M, "c", 0.9)
    c.restore()
    # Mom's hand reaching toward check out of habit
    reach = ease(lt, 1.4, 3.0)
    hx = lerp(290, 465, reach)
    c.set_source_rgb(*MUSTARD)
    c.set_line_width(44)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(250, 975)
    c.line_to(hx - 28, 985)
    c.stroke()
    c.set_source_rgb(*SKIN)
    c.arc(hx, 985, 30, 0, 2 * math.pi)
    c.fill()
    caption_card(c, "For 22 years, Mom paid.", y_center=1215, a=ease(lt, 0.15, 0.45), accent=MUSTARD)


def draw_scene_9_payoff(c, t):
    lt = t - 25.5
    # Warm wood table top-down close-up
    c.set_source_rgb(0.36, 0.22, 0.15)
    c.paint()
    c.set_source_rgba(0.20, 0.11, 0.07, 0.35)
    for y in range(0, VH, 160):
        c.rectangle(0, y, VW, 8)
    c.fill()
    # Black check folder
    rrect(c, 220, 510, 640, 420, 24)
    c.set_source_rgb(*INK)
    c.fill()
    # Her teal debit card sliding onto the check first
    sl = back_out(t, CARD_SLIDE_T, CARD_SLIDE_T + 0.65)
    cx = lerp(1160, 540, sl)
    c.save()
    c.translate(cx, 720)
    c.rotate(-0.06)
    rrect(c, -210, -130, 420, 260, 22)
    c.set_source_rgb(*TEAL)
    c.fill()
    rrect(c, -165, -45, 72, 54, 10)
    c.set_source_rgb(*GOLD)
    c.fill()
    txt(c, "FIRST PAYCHECK", -165, 82, 24, CREAM, M, "l", 0.85)
    c.restore()

    # Receipt pops up with $46.80 + PAID stamp slamming down
    if t >= PAID_STAMP_T - 0.35:
        rp = back_out(t, PAID_STAMP_T - 0.35, PAID_STAMP_T + 0.1)
        c.save()
        c.translate(VW / 2, lerp(1150, 695, rp))
        rrect(c, -310, -255, 620, 510, 16)
        c.set_source_rgb(*CREAM)
        c.fill()
        txt(c, "DINNER FOR TWO", 0, -155, 34, INK, M, "c", 0.85)
        c.set_source_rgba(*INK, 0.25)
        c.set_line_width(3)
        c.set_dash([10, 8])
        c.move_to(-250, -120)
        c.line_to(250, -120)
        c.stroke()
        c.set_dash([])
        txt(c, "TOTAL", -240, -10, 34, INK, M, "l", 0.8)
        txt(c, "$46.80", 240, 2, 68, TEAL_DARK, M, "r", 1.0)
        if t >= PAID_STAMP_T:
            sp = back_out(t, PAID_STAMP_T, PAID_STAMP_T + 0.22)
            c.save()
            c.translate(0, 125)
            c.rotate(-0.12)
            s = lerp(1.9, 1.0, sp)
            c.scale(s, s)
            rrect(c, -165, -56, 330, 112, 16)
            c.set_source_rgba(*CHERRY, 0.14)
            c.fill()
            rrect(c, -165, -56, 330, 112, 16)
            c.set_source_rgb(*CHERRY)
            c.set_line_width(10)
            c.stroke()
            txt(c, "PAID", 0, 28, 78, CHERRY, H, "c", 1.0)
            c.restore()
        c.restore()

    caption_card(c, "Tonight, she did.", y_center=1215, a=ease(lt, 0.15, 0.45), accent=CHERRY, size=62)


def draw_scene_10_warmth(c, t):
    lt = t - 30.0
    if t < 33.2:
        # Close-up of Mom laughing with happy tears, hands clasped across table
        g = cairo.LinearGradient(0, 0, 0, VH)
        g.add_color_stop_rgb(0, 0.34, 0.15, 0.14)
        g.add_color_stop_rgb(1, 0.19, 0.10, 0.09)
        c.set_source(g)
        c.paint()
        rg = cairo.RadialGradient(VW / 2, 540, 40, VW / 2, 640, 600)
        rg.add_color_stop_rgba(0, 1.0, 0.86, 0.48, 0.34)
        rg.add_color_stop_rgba(1, 1.0, 0.86, 0.48, 0.0)
        c.set_source(rg)
        c.paint()
        sc = lerp(2.05, 2.20, lt / 3.2)
        draw_mom(c, VW / 2, 690, scale=sc, mood="laugh", tear=ease(lt, 0.2, 1.0))
        # Clasped hands on the table
        c.set_source_rgb(0.44, 0.28, 0.18)
        rrect(c, 0, 940, VW, 180, 0)
        c.fill()
        c.set_source_rgb(*SKIN)
        c.arc(VW / 2 - 22, 1020, 44, 0, 2 * math.pi)
        c.arc(VW / 2 + 24, 1025, 42, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*SKIN_SH)
        c.set_line_width(6)
        c.arc(VW / 2, 1022, 54, math.pi * 0.1, math.pi * 0.9)
        c.stroke()
    else:
        # Pay stub on the table with $46.80 circled in cherry marker
        c.set_source_rgb(0.32, 0.21, 0.14)
        c.paint()
        cp = ease(t, CIRCLE_T, CIRCLE_T + 1.1)
        draw_pay_stub(c, VW / 2, 720, gross=1200, net=1010, snipped=4, circle_prog=cp, scale=1.02)

    caption_card(c, ["Best $46.80", "she ever spent."], y_center=1215, a=ease(lt, 0.15, 0.45), accent=GOLD, size=56)


def draw_scene_11_end(c, t):
    lt = t - END_T
    # Full-bleed perforated cream pay stub end card
    c.set_source_rgb(*CREAM)
    c.paint()
    # Top and bottom teal diner stripes (decoration)
    c.set_source_rgb(*TEAL_DARK)
    c.rectangle(0, 0, VW, 170)
    c.rectangle(0, VH - 170, VW, 170)
    c.fill()
    # Perforation dots along top & bottom edges of safe area
    c.set_source_rgba(*INK, 0.22)
    for x in range(40, VW, 44):
        c.new_sub_path()
        c.arc(x, 215, 6, 0, 2 * math.pi)
        c.new_sub_path()
        c.arc(x, VH - 215, 6, 0, 2 * math.pi)
    c.fill()

    a = ease(lt, 0.0, 0.4)
    sprout(c, VW / 2, 490, 1.05, a)
    txt(c, "NUMBERS THAT SAY EVERYTHING", VW / 2, 650, 44, TEAL_DARK, H, "c", a)
    txt(c, "EPISODE 2 · FIRST PAYCHECK", VW / 2, 725, 36, INK, M, "c", 0.85 * a)
    txt(c, "Small Win Films", VW / 2, 815, 42, CHERRY_DARK, H, "c", a)

    # Cherry CTA pill inside safe band (y 920..1030)
    pulse = 1.0 + 0.03 * math.sin(lt * 6.0)
    c.save()
    c.translate(VW / 2, 985)
    c.scale(pulse, pulse)
    rrect(c, -310, -56, 620, 112, 56)
    c.set_source_rgba(*CHERRY, a)
    c.fill()
    txt(c, "FOLLOW FOR EPISODE 3", 0, 18, 44, CREAM, H, "c", a)
    c.restore()

    txt(c, "Next: The gym card.", VW / 2, 1135, 38, INK, H, "c", 0.78 * a)

    # Subtle loop foreshadow in the last 0.25 s
    if t > DUR - 0.25:
        lp = ease(t, DUR - 0.25, DUR)
        c.set_source_rgba(*TEAL_DARK, lp * 0.75)
        c.paint()


def draw_frame(c, t):
    if t < 2.5:
        draw_scene_1_clock(c, t)
    elif t < 4.5:
        draw_scene_2_day1(c, t)
    elif t < 6.5:
        draw_scene_3_shifts(c, t)
    elif t < 8.5:
        draw_scene_4_bus(c, t)
    elif t < 11.0:
        draw_scene_5_envelope(c, t)
    elif t < 18.0:
        draw_scene_6_taxes(c, t)
    elif t < 21.5:
        draw_scene_7_photo(c, t)
    elif t < 25.5:
        draw_scene_8_booth(c, t)
    elif t < 30.0:
        draw_scene_9_payoff(c, t)
    elif t < END_T:
        draw_scene_10_warmth(c, t)
    else:
        draw_scene_11_end(c, t)


def draw_cover(c):
    # Full-bleed diner teal background with warm spotlight
    bg_diner_wall(c, warm=0.15)
    rg = cairo.RadialGradient(VW / 2, 980, 40, VW / 2, 980, 620)
    rg.add_color_stop_rgba(0, 1.0, 0.90, 0.65, 0.26)
    rg.add_color_stop_rgba(1, 1.0, 0.90, 0.65, 0.0)
    c.set_source(rg)
    c.paint()

    # Question block strictly inside y 384..900 (here y 410..670)
    rrect(c, 100, 405, 880, 245, 28)
    c.set_source_rgba(*INK, 0.92)
    c.fill()
    rrect(c, 100, 405, 880, 245, 28)
    c.set_source_rgb(*CHERRY)
    c.set_line_width(8)
    c.stroke()
    txt(c, "FIRST PAYCHECK.", VW / 2, 505, 72, GOLD, H, "c", 1.0)
    txt(c, "WHAT DID SHE BUY?", VW / 2, 600, 66, CREAM, H, "c", 1.0)

    # Half-torn kraft envelope with pay stub peeking out (GROSS $1,200 visible, NET hidden behind thumb)
    c.save()
    c.translate(VW / 2, 1080)
    c.rotate(-0.04)
    # Stub peeking out top
    rrect(c, -310, -320, 620, 390, 16)
    c.set_source_rgb(*CREAM)
    c.fill()
    c.set_source_rgb(*TEAL_DARK)
    c.rectangle(-310, -320, 620, 68)
    c.fill()
    txt(c, "PAY STUB · 80 HRS", 0, -276, 26, CREAM, M, "c", 1.0)
    txt(c, "GROSS PAY", -270, -175, 30, INK, M, "l", 0.8)
    txt(c, "$1,200", 270, -165, 62, TEAL_DARK, M, "r", 1.0)
    txt(c, "TAKE-HOME", -270, -70, 30, INK, M, "l", 0.8)
    txt(c, "$???", 270, -64, 54, CHERRY, M, "r", 1.0)
    # Half-torn envelope front
    rrect(c, -340, -10, 680, 290, 18)
    c.set_source_rgb(*KRAFT)
    c.fill()
    rrect(c, -340, -10, 680, 290, 18)
    c.set_source_rgb(*KRAFT_DARK)
    c.set_line_width(5)
    c.stroke()
    txt(c, "PAYROLL", 0, 145, 42, INK, M, "c", 0.55)
    # Her thumb covering the net amount area
    c.set_source_rgb(*SKIN)
    c.save()
    c.translate(215, -45)
    c.rotate(-0.35)
    c.scale(1.3, 0.72)
    c.arc(0, 0, 74, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*CREAM, 0.45)
    c.arc(-32, 0, 24, 0, 2 * math.pi)
    c.fill()
    c.restore()
    c.restore()


def render_still(t, out_path, safe=False):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(surf)
    draw_frame(c, t)
    if safe:
        draw_safe_zones(c)
    surf.write_to_png(out_path)


def render_cover(out_path, safe=False):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(surf)
    draw_cover(c)
    if safe:
        draw_safe_zones(c)
    surf.write_to_png(out_path)


def render_strip_15s(out_path):
    # 15 frames (t=0..14), 5 cols x 3 rows, scaled to 270x480 each
    w, h = 270, 480
    sheet = Image.new("RGB", (w * 5, h * 3), (20, 20, 20))
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(surf)
    for sec in range(15):
        draw_frame(c, float(sec))
        raw = bytes(surf.get_data())
        im = Image.frombuffer("RGBA", (VW, VH), raw, "raw", "BGRA", 0, 1).convert("RGB").resize((w, h), Image.LANCZOS)
        sheet.paste(im, ((sec % 5) * w, (sec // 5) * h))
    sheet.save(out_path)


def render_safe_sheet(out_path):
    # 8 key frames + cover with safe-zone overlays, 3x3 grid at 360x640
    times = [0.2, 3.2, 5.6, 7.6, 10.2, 13.0, 23.0, 28.0, 38.0]
    w, h = 360, 640
    sheet = Image.new("RGB", (w * 3, h * 3), (20, 20, 20))
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(surf)
    for i, t in enumerate(times):
        draw_frame(c, t)
        draw_safe_zones(c)
        raw = bytes(surf.get_data())
        im = Image.frombuffer("RGBA", (VW, VH), raw, "raw", "BGRA", 0, 1).convert("RGB").resize((w, h), Image.LANCZOS)
        sheet.paste(im, ((i % 3) * w, (i // 3) * h))
    sheet.save(out_path)


def render_video(out_path):
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "bgra", "-s", f"{VW}x{VH}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(surf)
    for f in range(TOTAL_FRAMES):
        draw_frame(c, f / FPS)
        proc.stdin.write(surf.get_data())
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed with {rc}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if mode == "stills":
        os.makedirs("preview", exist_ok=True)
        render_strip_15s("preview/strip_15s.png")
        render_safe_sheet("preview/safe_sheet.png")
        render_cover("preview/cover_safe.png", safe=True)
        render_still(0.0, "preview/frame_0.png", safe=True)
        render_still(13.0, "preview/frame_taxes.png", safe=True)
        render_still(28.0, "preview/frame_paid.png", safe=True)
        print("stills done")
    elif mode == "cover":
        out = sys.argv[2] if len(sys.argv) > 2 else "cover.png"
        render_cover(out, safe=False)
        print("cover done:", out)
    elif mode == "render":
        out = sys.argv[2] if len(sys.argv) > 2 else "silent.mp4"
        render_video(out)
        print("render done:", out)
