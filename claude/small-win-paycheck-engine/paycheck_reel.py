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
    ("FEDERAL", "-$60", 1140),
    ("SOC SEC", "-$74", 1066),
    ("MEDICARE", "-$17", 1049),
    ("STATE", "-$39", 1010),
]


def bg_diner_wall(c, warm=0.0):
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, lerp(TEAL_DARK[0], 0.14, warm), lerp(TEAL_DARK[1], 0.34, warm), lerp(TEAL_DARK[2], 0.35, warm))
    g.add_color_stop_rgb(0.55, TEAL[0], TEAL[1], TEAL[2])
    g.add_color_stop_rgb(1, TEAL_DARK[0], TEAL_DARK[1], TEAL_DARK[2])
    c.set_source(g)
    c.paint()
    # Subtle cream subway tile lines all the way to the top edge (no flat border band)
    c.set_source_rgba(*CREAM, 0.10)
    for y in range(24, 1460, 64):
        c.rectangle(0, y, VW, 2)
    c.fill()
    # Cherry chrome trim stripe
    c.set_source_rgb(*CHERRY)
    c.rectangle(0, 1450, VW, 24)
    c.fill()
    c.set_source_rgb(*CREAM_WARM)
    c.rectangle(0, 1474, VW, VH - 1474)
    c.fill()
    # Checkered diner floor edge to edge
    sq = 90
    c.set_source_rgba(*TEAL_DARK, 0.22)
    for row in range(6):
        for col in range(13):
            if (row + col) % 2 == 0:
                c.rectangle(col * sq, 1474 + row * sq, sq, sq)
    c.fill()


def draw_hook_envelope_stub(c, cx, cy, slam=1.0, rot=-0.03):
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    # Pay stub peeking out top of half-torn envelope
    rrect(c, -350, -255, 700, 320, 18)
    c.set_source_rgb(*CREAM)
    c.fill()
    # Gross and hidden net in >= 48px cap height
    txt(c, "GROSS", -310, -145, 80, INK, M, "l", 0.85)
    txt(c, "$1,200", 310, -140, 82, TEAL_DARK, M, "r", 1.0)
    txt(c, "NET", -310, -35, 80, INK, M, "l", 0.85)
    txt(c, "$???", 310, -30, 82, CHERRY, M, "r", 1.0)
    # Kraft envelope front
    rrect(c, -375, 20, 750, 220, 18)
    c.set_source_rgb(*KRAFT)
    c.fill()
    rrect(c, -375, 20, 750, 220, 18)
    c.set_source_rgb(*KRAFT_DARK)
    c.set_line_width(5)
    c.stroke()
    txt(c, "PAYROLL", 0, 155, 80, INK, M, "c", 0.58)
    # Thumb covering net area
    c.save()
    c.translate(lerp(360, 225, slam), -42)
    c.rotate(-0.32)
    c.scale(1.3, 0.72)
    c.set_source_rgb(*SKIN)
    c.arc(0, 0, 74, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*CREAM, 0.45)
    c.arc(-32, 0, 24, 0, 2 * math.pi)
    c.fill()
    c.restore()
    c.restore()


def draw_scene_1_hook(c, t):
    # Matches the cover visually: diner teal wall + half-torn payroll envelope + $1,200 stub + 80 HRS slamming in
    bg_diner_wall(c, warm=0.15)
    rg = cairo.RadialGradient(VW / 2, 820, 40, VW / 2, 820, 620)
    rg.add_color_stop_rgba(0, 1.0, 0.90, 0.65, 0.24)
    rg.add_color_stop_rgba(1, 1.0, 0.90, 0.65, 0.0)
    c.set_source(rg)
    c.paint()

    slam = back_out(t, 0.0, 0.35)
    shake = math.sin(t * 65) * 9 * max(0, 1 - t / 0.25)
    c.save()
    c.translate(shake, 0)
    draw_hook_envelope_stub(c, VW / 2, lerp(890, 815, slam), slam=slam, rot=-0.03 + (1 - slam) * 0.05)
    # Impact rays on frame 1..0.45
    if t < 0.45:
        ia = 1 - t / 0.45
        c.set_source_rgba(*GOLD, ia)
        c.set_line_width(8)
        for k in range(6):
            ang = math.pi * 0.12 + k * math.pi * 0.15
            r0 = 280 + t * 140
            r1 = r0 + 55
            c.move_to(VW / 2 + math.cos(ang) * r0, 780 + math.sin(ang) * r0 * 0.55)
            c.line_to(VW / 2 + math.cos(ang) * r1, 780 + math.sin(ang) * r1 * 0.55)
            c.stroke()
    c.restore()

    # Big 80 HRS punch card starting in safe band and shrinking smoothly into top counter spot
    shrink = ease(t, 1.25, 2.2)
    cy_card = lerp(430, 366, shrink)
    sc_card = lerp(1.18, 1.0, shrink)
    punch_card_counter(c, 80, stamp_pulse=max(0, 1 - t / 0.35), a=1.0, scale=sc_card, cy=cy_card)
    caption_card(c, ["First paycheck.", "What did she buy?"], y_center=1205, a=1.0, size=70)


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
    # Arms & hands tying apron strings (connected to shoulders)
    knot = ease(lt, 0.2, 1.4)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        hx = VW / 2 + sx * lerp(185, 96, knot)
        hy = 1045 + math.sin(lt * 8) * 8
        c.set_source_rgb(*TEAL)
        c.set_line_width(48)
        c.move_to(VW / 2 + sx * 200, 1120)
        c.line_to(hx, hy)
        c.stroke()
        c.set_source_rgb(*SKIN)
        c.arc(hx, hy, 34, 0, 2 * math.pi)
        c.fill()
    punch_card_counter(c, 0, a=1.0)
    caption_card(c, "Day 1.", y_center=1205, a=ease(lt, 0.0, 0.25), size=72)


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
    c.set_source_rgb(*SKIN)
    c.set_line_width(34)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        c.move_to(walk_x + sx * 165, 1020 - bob * 0.7)
        c.line_to(walk_x + sx * 270, 930 - bob * 0.7)
        c.stroke()
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
    hrs = 0
    pulse = 0.0
    for st, val in ((4.9, 8), (5.5, 16), (6.1, 24)):
        if t >= st:
            hrs = val
            pulse = max(pulse, max(0, 1 - (t - st) / 0.25))
    punch_card_counter(c, hrs, stamp_pulse=pulse)
    caption_card(c, "Double shifts.", y_center=1205, a=ease(lt, 0.0, 0.25), size=72)


def draw_scene_4_bus(c, t):
    lt = t - 6.5
    # Night bus interior full bleed with subtle ceiling gradient (no flat border bars, no floating feet)
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.05, 0.09, 0.15)
    g.add_color_stop_rgb(0.5, 0.09, 0.15, 0.23)
    g.add_color_stop_rgb(1, 0.06, 0.10, 0.16)
    c.set_source(g)
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
    # Tall bus seat extending cleanly down to the bottom edge (no floating feet)
    c.set_source_rgb(0.18, 0.26, 0.34)
    rrect(c, 190, 740, 700, 1220, 48)
    c.fill()
    c.set_source_rgb(0.14, 0.21, 0.29)
    rrect(c, 220, 770, 640, 1180, 36)
    c.fill()
    # Her leaning tiredly, eyes closed, gentle bus sway
    sway = math.sin(lt * 3.8) * 8
    c.save()
    c.translate(VW / 2 + sway, 910)
    c.rotate(-0.07)
    draw_woman(c, 0, 0, scale=1.92, mood="sleep", uniform=True)
    c.restore()
    hrs = 48
    pulse = 0.0
    for st, val in ((7.1, 64), (7.8, 80)):
        if t >= st:
            hrs = val
            pulse = max(pulse, max(0, 1 - (t - st) / 0.25))
    punch_card_counter(c, hrs, stamp_pulse=pulse)
    caption_card(c, "Day 10.", y_center=1205, a=ease(lt, 0.0, 0.25), size=72)


def draw_pay_stub(c, cx, cy, gross=1200, net=1200, snipped=0, snip_prog=0.0, circle_prog=0.0, scale=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    w, h = 840, 690
    x, y = -w / 2, -h / 2
    # Shadow
    rrect(c, x + 10, y + 14, w, h, 20)
    c.set_source_rgba(0, 0, 0, 0.28)
    c.fill()
    # Cream stub paper
    rrect(c, x, y, w, h, 20)
    c.set_source_rgb(*CREAM)
    c.fill()
    # Top teal header bar
    c.save()
    rrect(c, x, y, w, h, 20)
    c.clip()
    c.set_source_rgb(*TEAL_DARK)
    c.rectangle(x, y, w, 102)
    c.fill()
    c.restore()
    txt(c, "EXAMPLE STUB", 0, y + 76, 72, GOLD, H, "c", 1.0)

    # Gross pay row (>= 48 px cap height)
    txt(c, "GROSS", x + 36, y + 174, 80, INK, M, "l", 0.85)
    txt(c, f"${gross:,}", x + w - 36, y + 174, 80, TEAL_DARK, M, "r", 1.0)
    c.set_source_rgba(*INK, 0.22)
    c.set_line_width(3)
    c.move_to(x + 32, y + 196)
    c.line_to(x + w - 32, y + 196)
    c.stroke()

    if circle_prog > 0.01:
        # Scene 10: clean dinner note circled in cherry marker (>= 48 px text)
        txt(c, "MOM'S DINNER", 0, y + 305, 68, INK, H, "c", 1.0)
        txt(c, "$46.80", 0, y + 425, 92, CHERRY, M, "c", 1.0)
        c.set_source_rgb(*CHERRY)
        c.set_line_width(11)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        end_ang = -math.pi * 0.2 + circle_prog * math.pi * 2.15
        c.save()
        c.translate(0, y + 398)
        c.scale(2.15, 0.82)
        c.arc(0, 0, 86, -math.pi * 0.2, end_ang)
        c.stroke()
        c.restore()
    else:
        # Four deduction rows, each >= 48 px cap height (Courier Prime Bold 74 px)
        for idx, (label, amt, _) in enumerate(DEDUCTIONS):
            ry = y + 214 + idx * 84
            if idx < snipped:
                # Snipped away: clean dashed empty slot only (no tiny faded text)
                c.set_source_rgba(*CHERRY, 0.28)
                c.set_line_width(3)
                c.set_dash([12, 10])
                c.move_to(x + 34, ry + 36)
                c.line_to(x + w - 34, ry + 36)
                c.stroke()
                c.set_dash([])
            elif idx == snipped and snip_prog > 0.0:
                c.save()
                drop = ease(snip_prog, 0.35, 1.0)
                c.translate(x + 30 + drop * 110, ry + drop * 210)
                c.rotate(drop * 0.22)
                rrect(c, 0, 0, w - 60, 74, 10)
                c.set_source_rgba(*CHERRY, 0.94 * (1 - drop * 0.85))
                c.fill()
                txt(c, label, 20, 58, 78, CREAM, M, "l", 1 - drop * 0.85)
                txt(c, amt, w - 80, 58, 80, CREAM, M, "r", 1 - drop * 0.85)
                c.restore()
                if snip_prog < 0.55:
                    sx = lerp(x + 28, x + w - 28, snip_prog / 0.55)
                    c.set_source_rgb(*CHERRY)
                    c.set_line_width(5)
                    c.set_dash([12, 8])
                    c.move_to(x + 28, ry + 36)
                    c.line_to(sx, ry + 36)
                    c.stroke()
                    c.set_dash([])
                    c.set_source_rgb(*INK)
                    c.set_line_width(6)
                    c.arc(sx + 20, ry + 22, 11, 0, 2 * math.pi)
                    c.stroke()
                    c.arc(sx + 20, ry + 50, 11, 0, 2 * math.pi)
                    c.stroke()
                    c.move_to(sx + 10, ry + 28)
                    c.line_to(sx - 20, ry + 44)
                    c.move_to(sx + 10, ry + 44)
                    c.line_to(sx - 20, ry + 28)
                    c.stroke()
            else:
                rrect(c, x + 30, ry, w - 60, 74, 10)
                c.set_source_rgba(*KRAFT, 0.45)
                c.fill()
                txt(c, label, x + 48, ry + 58, 78, INK, M, "l", 0.88)
                txt(c, amt, x + w - 48, ry + 58, 80, CHERRY_DARK, M, "r", 0.96)

    # Net pay footer (>= 48 px cap height)
    c.set_source_rgba(*INK, 0.35)
    c.set_line_width(3)
    c.move_to(x + 32, y + 564)
    c.line_to(x + w - 32, y + 564)
    c.stroke()
    txt(c, "NET", x + 36, y + 648, 82, INK, M, "l", 1.0)
    txt(c, f"${net:,}", x + w - 36, y + 650, 86, TEAL_DARK if net == 1200 else CHERRY_DARK, M, "r", 1.0)
    c.restore()


def draw_scene_5_envelope(c, t):
    lt = t - 8.5
    # Diner wood counter top-down
    c.set_source_rgb(0.28, 0.20, 0.15)
    c.paint()
    c.set_source_rgba(0.18, 0.12, 0.08, 0.35)
    for y in range(20, VH, 140):
        c.rectangle(0, y, VW, 6)
    c.fill()
    # Envelope slides in, stub rises cleanly out (no stray flying tear rectangle)
    slide = ease_out(lt, 0.0, 0.55)
    rise = back_out(lt, 0.75, 1.55)
    if rise > 0.02:
        stub_y = lerp(840, 710, rise)
        stub_sc = lerp(0.75, 1.0, rise)
        draw_pay_stub(c, VW / 2, stub_y, gross=1200, net=1200, snipped=0, scale=stub_sc)
    env_y = lerp(760, 1520, rise) + (1 - slide) * -380
    c.save()
    c.translate(VW / 2, env_y)
    rrect(c, -370, -140, 740, 280, 18)
    c.set_source_rgb(*KRAFT)
    c.fill()
    rrect(c, -370, -140, 740, 280, 18)
    c.set_source_rgb(*KRAFT_DARK)
    c.set_line_width(5)
    c.stroke()
    txt(c, "PAYROLL", 0, 24, 80, INK, M, "c", 0.58 * (1.0 - ease(lt, 0.7, 1.05)))
    c.restore()
    punch_card_counter(c, 80, a=1.0 - ease(lt, 0.45, 0.9))
    caption_card(c, "$1,200.", y_center=1205, a=ease(lt, 0.85, 1.15), accent=TEAL_LT, size=72)


def draw_scene_6_taxes(c, t):
    lt = t - 11.0
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.06, 0.25, 0.28)
    g.add_color_stop_rgb(1, 0.09, 0.35, 0.38)
    c.set_source(g)
    c.paint()
    c.set_source_rgba(*CREAM, 0.06)
    for x in range(40, VW, 80):
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
        draw_pay_stub(c, VW / 2, 710, gross=1200, net=net, snipped=snipped, snip_prog=snip_prog, scale=1.0)
        if t < 15.2:
            caption_card(c, "Then the taxes came.", y_center=1205, a=ease(lt, 0.0, 0.25), size=70)
        else:
            caption_card(c, "$1,010 left.", y_center=1205, a=1.0, accent=CHERRY, size=70)
    else:
        bg_diner_wall(c, warm=0.15)
        draw_woman(c, VW / 2, 740, scale=2.22, mood="shock", uniform=True)
        c.save()
        c.translate(VW / 2, 1005)
        c.rotate(-0.04)
        rrect(c, -210, -72, 420, 144, 14)
        c.set_source_rgb(*CREAM)
        c.fill()
        txt(c, "$1,010", 0, 24, 80, CHERRY_DARK, M, "c", 1.0)
        c.restore()
        caption_card(c, "$1,010 left.", y_center=1205, a=1.0, accent=CHERRY, size=70)


def draw_scene_7_photo(c, t):
    lt = t - 18.0
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.14, 0.28, 0.32)
    g.add_color_stop_rgb(1, 0.08, 0.16, 0.20)
    c.set_source(g)
    c.paint()
    mood = "tired" if lt < 1.1 else "smile"
    draw_woman(c, VW / 2 - 110, 740, scale=1.95, mood=mood, uniform=False)
    # Phone rising on the right showing warm photo of her and Mom (no small clock text)
    lift = back_out(lt, 0.4, 1.2)
    px, py = 745, lerp(1120, 735, lift)
    c.save()
    c.translate(px, py)
    c.rotate(0.06)
    rrect(c, -155, -245, 310, 490, 36)
    c.set_source_rgb(*INK)
    c.fill()
    rrect(c, -140, -230, 280, 460, 26)
    c.set_source_rgb(0.96, 0.86, 0.68)
    c.fill()
    c.save()
    rrect(c, -140, -230, 280, 460, 26)
    c.clip()
    draw_mom(c, -52, 20, scale=0.68, mood="warm")
    draw_woman(c, 54, 34, scale=0.64, mood="smile", uniform=False)
    c.restore()
    c.restore()
    caption_card(c, "She knew the first thing.", y_center=1205, a=ease(lt, 0.15, 0.45), accent=GOLD, size=68)


def draw_scene_8_booth(c, t):
    lt = t - 21.5
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.24, 0.11, 0.12)
    g.add_color_stop_rgb(0.55, 0.38, 0.17, 0.15)
    g.add_color_stop_rgb(1, 0.20, 0.11, 0.09)
    c.set_source(g)
    c.paint()
    rg = cairo.RadialGradient(VW / 2, 340, 20, VW / 2, 540, 560)
    rg.add_color_stop_rgba(0, 1.0, 0.85, 0.45, 0.42)
    rg.add_color_stop_rgba(1, 1.0, 0.85, 0.45, 0.0)
    c.set_source(rg)
    c.paint()
    c.set_source_rgb(*MUSTARD)
    c.arc(VW / 2, 230, 110, math.pi, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*CHERRY_DARK)
    rrect(c, 40, 620, 320, 460, 34)
    rrect(c, 720, 620, 320, 460, 34)
    c.fill()
    draw_mom(c, 260, 740, scale=1.32, mood="warm")
    draw_woman(c, 820, 750, scale=1.28, mood="smile", uniform=False)
    c.set_source_rgb(0.42, 0.27, 0.18)
    rrect(c, 60, 910, 960, 240, 24)
    c.fill()
    for px in (310, 770):
        c.set_source_rgb(*CREAM)
        c.save()
        c.translate(px, 990)
        c.scale(1.0, 0.34)
        c.arc(0, 0, 86, 0, 2 * math.pi)
        c.fill()
        c.restore()
    # Black leather check folder with gold trim (no tiny text)
    chk = ease_out(lt, 0.4, 1.2)
    cy = lerp(890, 985, chk)
    c.save()
    c.translate(VW / 2, cy)
    rrect(c, -74, -46, 148, 92, 10)
    c.set_source_rgb(*INK)
    c.fill()
    rrect(c, -62, -34, 124, 68, 6)
    c.set_source_rgba(*GOLD, 0.75)
    c.set_line_width(3)
    c.stroke()
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
    caption_card(c, "For 22 years, Mom paid.", y_center=1205, a=ease(lt, 0.15, 0.45), accent=MUSTARD, size=68)


def draw_scene_9_payoff(c, t):
    lt = t - 25.5
    c.set_source_rgb(0.36, 0.22, 0.15)
    c.paint()
    c.set_source_rgba(0.20, 0.11, 0.07, 0.35)
    for y in range(20, VH, 160):
        c.rectangle(0, y, VW, 8)
    c.fill()
    rrect(c, 220, 510, 640, 420, 24)
    c.set_source_rgb(*INK)
    c.fill()
    # Her teal debit card sliding onto the check (clean chip + contactless waves, no tiny text)
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
    c.set_source_rgba(*CREAM, 0.6)
    c.set_line_width(6)
    for r in (26, 44, 62):
        c.new_sub_path()
        c.arc(110, -18, r, -0.6, 0.6)
    c.stroke()
    c.restore()

    # Receipt pops up with >= 48 px text + PAID stamp
    if t >= PAID_STAMP_T - 0.35:
        rp = back_out(t, PAID_STAMP_T - 0.35, PAID_STAMP_T + 0.1)
        c.save()
        c.translate(VW / 2, lerp(1140, 690, rp))
        rrect(c, -340, -265, 680, 530, 18)
        c.set_source_rgb(*CREAM)
        c.fill()
        txt(c, "DINNER", 0, -148, 70, INK, H, "c", 0.9)
        c.set_source_rgba(*INK, 0.25)
        c.set_line_width(3)
        c.set_dash([12, 8])
        c.move_to(-270, -110)
        c.line_to(270, -110)
        c.stroke()
        c.set_dash([])
        txt(c, "$46.80", 0, -2, 92, TEAL_DARK, M, "c", 1.0)
        if t >= PAID_STAMP_T:
            sp = back_out(t, PAID_STAMP_T, PAID_STAMP_T + 0.22)
            c.save()
            c.translate(0, 130)
            c.rotate(-0.11)
            s = lerp(1.85, 1.0, sp)
            c.scale(s, s)
            rrect(c, -175, -60, 350, 120, 16)
            c.set_source_rgba(*CHERRY, 0.14)
            c.fill()
            rrect(c, -175, -60, 350, 120, 16)
            c.set_source_rgb(*CHERRY)
            c.set_line_width(11)
            c.stroke()
            txt(c, "PAID", 0, 32, 86, CHERRY, H, "c", 1.0)
            c.restore()
        c.restore()

    caption_card(c, "Tonight, she did.", y_center=1205, a=ease(lt, 0.15, 0.45), accent=CHERRY, size=72)


def draw_scene_10_warmth(c, t):
    lt = t - 30.0
    if t < 33.2:
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
        c.set_source_rgb(0.44, 0.28, 0.18)
        c.rectangle(0, 940, VW, VH - 940)
        c.fill()
        c.set_source_rgb(0.36, 0.22, 0.14)
        c.rectangle(0, 940, VW, 16)
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
        c.set_source_rgb(0.32, 0.21, 0.14)
        c.paint()
        c.set_source_rgba(0.20, 0.12, 0.08, 0.35)
        for y in range(20, VH, 140):
            c.rectangle(0, y, VW, 6)
        c.fill()
        cp = ease(t, CIRCLE_T, CIRCLE_T + 1.1)
        draw_pay_stub(c, VW / 2, 710, gross=1200, net=1010, snipped=4, circle_prog=cp, scale=1.0)

    caption_card(c, ["Best $46.80", "she ever spent."], y_center=1205, a=ease(lt, 0.15, 0.45), accent=GOLD, size=70)


def draw_scene_11_end(c, t):
    lt = t - END_T
    # Full-bleed warm cream paper gradient edge to edge (NO teal top/bottom bands that look like borders)
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, 0.96, 0.91, 0.81)
    g.add_color_stop_rgb(0.5, 0.99, 0.96, 0.90)
    g.add_color_stop_rgb(1, 0.93, 0.86, 0.74)
    c.set_source(g)
    c.paint()
    # Subtle warm ruled paper lines edge to edge
    c.set_source_rgba(*TEAL_DARK, 0.08)
    for y in range(40, VH, 88):
        c.rectangle(0, y, VW, 3)
    c.fill()

    a = ease(lt, 0.0, 0.4)
    sprout(c, VW / 2, 460, 1.02, a)
    txt(c, "NUMBERS THAT", VW / 2, 610, 72, TEAL_DARK, H, "c", a)
    txt(c, "SAY EVERYTHING", VW / 2, 692, 72, TEAL_DARK, H, "c", a)
    txt(c, "EP 2 · PAYCHECK", VW / 2, 800, 74, INK, H, "c", 0.90 * a)

    # Cherry CTA pill inside safe band
    pulse = 1.0 + 0.025 * math.sin(lt * 6.0)
    c.save()
    c.translate(VW / 2, 965)
    c.scale(pulse, pulse)
    rrect(c, -360, -64, 720, 128, 64)
    c.set_source_rgba(*CHERRY, a)
    c.fill()
    txt(c, "FOLLOW FOR EP 3", 0, 26, 72, CREAM, H, "c", a)
    c.restore()

    txt(c, "Next: The gym card.", VW / 2, 1175, 72, INK, H, "c", 0.85 * a)

    # Subtle loop transition into frame 1
    if t > DUR - 0.25:
        lp = ease(t, DUR - 0.25, DUR)
        c.set_source_rgba(*TEAL_DARK, lp * 0.72)
        c.paint()


def draw_frame(c, t):
    if t < 2.5:
        draw_scene_1_hook(c, t)
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
    # Matches Frame 1 visually, full bleed edge to edge, all text >= 48 px cap height
    bg_diner_wall(c, warm=0.15)
    rg = cairo.RadialGradient(VW / 2, 980, 40, VW / 2, 980, 620)
    rg.add_color_stop_rgba(0, 1.0, 0.90, 0.65, 0.26)
    rg.add_color_stop_rgba(1, 1.0, 0.90, 0.65, 0.0)
    c.set_source(rg)
    c.paint()

    # Question block strictly inside y 384..900 (here y 405..665)
    rrect(c, 96, 405, 888, 260, 28)
    c.set_source_rgba(*INK, 0.93)
    c.fill()
    rrect(c, 96, 405, 888, 260, 28)
    c.set_source_rgb(*CHERRY)
    c.set_line_width(8)
    c.stroke()
    txt(c, "FIRST PAYCHECK.", VW / 2, 512, 74, GOLD, H, "c", 1.0)
    txt(c, "WHAT DID SHE BUY?", VW / 2, 612, 72, CREAM, H, "c", 1.0)

    # Matching half-torn envelope + $1,200 stub + hidden net
    draw_hook_envelope_stub(c, VW / 2, 1020, slam=1.0, rot=-0.03)


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
    mode = sys.argv[1] if len(sys.argv) > 1 else "cover"
    if mode == "cover":
        out = sys.argv[2] if len(sys.argv) > 2 else "cover.png"
        render_cover(out, safe=False)
        print("cover done:", out)
    elif mode == "render":
        out = sys.argv[2] if len(sys.argv) > 2 else "silent.mp4"
        render_video(out)
        print("render done:", out)
