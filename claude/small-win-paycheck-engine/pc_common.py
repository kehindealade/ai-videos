import cairo, math

VW, VH, FPS = 1080, 1920, 30
H = "Fredoka"
M = "Courier Prime"

# Diner shift palette
TEAL_DARK = (0.075, 0.31, 0.34)
TEAL = (0.11, 0.45, 0.49)
TEAL_LT = (0.20, 0.62, 0.64)
CHERRY = (0.79, 0.16, 0.24)
CHERRY_DARK = (0.56, 0.10, 0.16)
CREAM = (0.98, 0.95, 0.89)
CREAM_WARM = (0.94, 0.89, 0.78)
KRAFT = (0.90, 0.81, 0.66)
KRAFT_DARK = (0.78, 0.66, 0.49)
INK = (0.11, 0.10, 0.10)
PURPLE = (0.37, 0.17, 0.48)
MUSTARD = (0.87, 0.62, 0.20)
NIGHT = (0.07, 0.12, 0.19)
NIGHT_WIN = (0.11, 0.19, 0.29)
GOLD = (0.98, 0.80, 0.28)
SKIN = (0.85, 0.64, 0.50)
SKIN_SH = (0.74, 0.52, 0.38)
HAIR = (0.14, 0.10, 0.09)
GREY_HAIR = (0.64, 0.65, 0.68)
WHITE = (1.0, 1.0, 1.0)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * clamp(t)


def ease(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return x * x * (3 - 2 * x)


def ease_out(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return 1 - (1 - x) ** 3


def back_out(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def font(c, name=H, bold=True):
    c.select_font_face(
        name,
        cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL,
    )


def txt(c, s, x, y, size, col, f=H, align="c", a=1.0, bold=True):
    font(c, f, bold)
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


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def caption_card(c, lines, y_center=1215, a=1.0, bg=INK, fg=CREAM, accent=CHERRY, size=56):
    if a <= 0.01 or not lines:
        return
    if isinstance(lines, str):
        lines = [lines]
    c.save()
    font(c, H, True)
    c.set_font_size(size)
    widths = [c.text_extents(ln).width for ln in lines]
    pad_x = 46
    line_h = int(size * 1.24)
    w = min(870, max(widths) + pad_x * 2)
    h = len(lines) * line_h + 44
    x = (VW - w) / 2
    y = y_center - h / 2
    # Shadow
    rrect(c, x + 6, y + 8, w, h, 22)
    c.set_source_rgba(0, 0, 0, 0.28 * a)
    c.fill()
    # Card
    rrect(c, x, y, w, h, 22)
    c.set_source_rgba(*bg, 0.94 * a)
    c.fill()
    # Cherry left stripe
    c.save()
    rrect(c, x, y, w, h, 22)
    c.clip()
    c.set_source_rgba(*accent, a)
    c.rectangle(x, y, 16, h)
    c.fill()
    c.restore()
    # Border
    rrect(c, x, y, w, h, 22)
    c.set_source_rgba(*CREAM, 0.16 * a)
    c.set_line_width(3)
    c.stroke()
    # Text
    start_y = y + 22 + size * 0.86
    for i, ln in enumerate(lines):
        txt(c, ln, VW / 2 + 6, start_y + i * line_h, size, fg, H, "c", a, True)
    c.restore()


def punch_card_counter(c, hours, stamp_pulse=0.0, a=1.0, scale=1.0, cy=366):
    if a <= 0.01:
        return
    c.save()
    c.translate(VW / 2, cy)
    s = scale * (1.0 + 0.08 * stamp_pulse)
    c.scale(s, s)
    w, h = 440, 96
    x, y = -w / 2, -h / 2
    # Drop shadow
    rrect(c, x + 5, y + 7, w, h, 14)
    c.set_source_rgba(0, 0, 0, 0.28 * a)
    c.fill()
    # Manila card
    rrect(c, x, y, w, h, 14)
    c.set_source_rgba(*KRAFT, a)
    c.fill()
    # Top punch notch
    c.set_source_rgba(*TEAL_DARK, a)
    c.arc(0, y, 14, 0, math.pi)
    c.fill()
    # Ruled border
    rrect(c, x + 6, y + 6, w - 12, h - 12, 10)
    c.set_source_rgba(*INK, 0.45 * a)
    c.set_line_width(2.5)
    c.stroke()
    # Label + stamped hours
    txt(c, "TIME CARD · HOURS", x + 26, y + 36, 22, INK, M, "l", 0.78 * a, True)
    txt(c, f"{int(hours):02d}", x + w - 28, y + 76, 62, PURPLE, M, "r", a, True)
    # Mini stamp squares
    for k in range(5):
        bx = x + 26 + k * 42
        by = y + 48
        rrect(c, bx, by, 32, 32, 6)
        filled = hours >= (k + 1) * 16
        c.set_source_rgba(*(PURPLE if filled else KRAFT_DARK), (0.88 if filled else 0.5) * a)
        c.fill()
        if filled:
            c.set_source_rgba(*CREAM, a)
            c.set_line_width(3.5)
            c.move_to(bx + 8, by + 16)
            c.line_to(bx + 14, by + 23)
            c.line_to(bx + 25, by + 10)
            c.stroke()
    c.restore()


def draw_woman(c, cx, cy, scale=1.0, mood="smile", uniform=True, blink=False):
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    # Ponytail back
    c.set_source_rgb(*HAIR)
    c.save()
    c.translate(78, -40)
    c.rotate(0.28)
    c.scale(0.8, 1.45)
    c.arc(0, 0, 52, 0, 2 * math.pi)
    c.fill()
    c.restore()
    # Cherry hair tie
    c.set_source_rgb(*CHERRY)
    c.arc(62, -74, 14, 0, 2 * math.pi)
    c.fill()
    # Torso
    if uniform:
        c.set_source_rgb(*TEAL)
        rrect(c, -118, 80, 236, 250, 70)
        c.fill()
        # Collar
        c.set_source_rgb(*CREAM)
        c.move_to(-34, 82)
        c.line_to(0, 128)
        c.line_to(34, 82)
        c.close_path()
        c.fill()
        # Cherry apron bib & straps
        c.set_source_rgb(*CHERRY)
        rrect(c, -74, 152, 148, 185, 16)
        c.fill()
        c.set_line_width(14)
        c.move_to(-56, 156)
        c.line_to(-46, 86)
        c.move_to(56, 156)
        c.line_to(46, 86)
        c.stroke()
        # Apron pocket
        c.set_source_rgb(*CHERRY_DARK)
        rrect(c, -46, 230, 92, 56, 8)
        c.fill()
    else:
        c.set_source_rgb(*TEAL_LT)
        rrect(c, -118, 80, 236, 250, 70)
        c.fill()
        c.set_source_rgb(*CREAM)
        c.arc(0, 84, 40, 0, math.pi)
        c.fill()
    # Neck
    c.set_source_rgb(*SKIN_SH)
    rrect(c, -22, 42, 44, 52, 16)
    c.fill()
    # Head
    c.set_source_rgb(*SKIN)
    c.arc(0, -18, 86, 0, 2 * math.pi)
    c.fill()
    # Ears
    for sx in (-1, 1):
        c.set_source_rgb(*SKIN)
        c.arc(sx * 84, -14, 16, 0, 2 * math.pi)
        c.fill()
    # Hair front cap & waves
    c.set_source_rgb(*HAIR)
    c.arc(0, -34, 90, math.pi * 0.98, math.pi * 2.02)
    c.close_path()
    c.fill()
    c.arc(-52, -70, 44, 0, 2 * math.pi)
    c.arc(46, -72, 46, 0, 2 * math.pi)
    c.fill()
    # Blush
    c.set_source_rgba(0.90, 0.45, 0.42, 0.25)
    for sx in (-1, 1):
        c.arc(sx * 46, 4, 16, 0, 2 * math.pi)
        c.fill()
    # Eyes & brows
    c.set_source_rgb(*INK)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        ex = sx * 32
        ey = -16
        if mood == "sleep" or blink:
            c.set_line_width(6)
            c.arc(ex, ey - 4, 12, math.pi * 0.15, math.pi * 0.85)
            c.stroke()
        elif mood == "shock":
            c.set_source_rgb(*WHITE)
            c.arc(ex, ey, 14, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*INK)
            c.arc(ex, ey, 7, 0, 2 * math.pi)
            c.fill()
        else:
            c.arc(ex, ey, 8.5, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*WHITE)
            c.arc(ex - 2.5, ey - 2.5, 2.5, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*INK)
        # Eyebrow
        c.set_line_width(5.5)
        if mood == "shock":
            c.move_to(ex - 16, ey - 28)
            c.line_to(ex + 16, ey - 32 if sx == -1 else ey - 26)
            c.stroke()
        elif mood == "nervous":
            c.move_to(ex - 15, ey - 22 + (4 if sx == -1 else -4))
            c.line_to(ex + 15, ey - 22 + (-4 if sx == -1 else 4))
            c.stroke()
        elif mood == "tired":
            c.move_to(ex - 15, ey - 20)
            c.line_to(ex + 15, ey - 20)
            c.stroke()
        else:
            c.move_to(ex - 15, ey - 24)
            c.line_to(ex + 15, ey - 26)
            c.stroke()
    # Mouth
    c.set_line_width(6)
    c.set_source_rgb(*INK)
    if mood in ("smile", "warm"):
        c.arc(0, 12, 24, math.pi * 0.15, math.pi * 0.85)
        c.stroke()
    elif mood == "nervous":
        c.move_to(-18, 26)
        c.curve_to(-6, 20, 6, 30, 18, 22)
        c.stroke()
    elif mood == "shock":
        c.arc(0, 28, 12, 0, 2 * math.pi)
        c.fill()
    elif mood in ("tired", "sleep"):
        c.move_to(-14, 24)
        c.line_to(14, 24)
        c.stroke()
    c.restore()


def draw_mom(c, cx, cy, scale=1.0, mood="warm", tear=0.0):
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    # Bob hair back
    c.set_source_rgb(*HAIR)
    rrect(c, -96, -88, 192, 168, 72)
    c.fill()
    # Mustard cardigan torso
    c.set_source_rgb(*MUSTARD)
    rrect(c, -124, 80, 248, 250, 74)
    c.fill()
    # Cream blouse V
    c.set_source_rgb(*CREAM)
    c.move_to(-38, 82)
    c.line_to(0, 172)
    c.line_to(38, 82)
    c.close_path()
    c.fill()
    # Neck
    c.set_source_rgb(*SKIN_SH)
    rrect(c, -22, 42, 44, 52, 16)
    c.fill()
    # Head
    c.set_source_rgb(*SKIN)
    c.arc(0, -18, 84, 0, 2 * math.pi)
    c.fill()
    # Hair bangs with grey streaks
    c.set_source_rgb(*HAIR)
    c.arc(0, -34, 88, math.pi * 1.0, math.pi * 2.0)
    c.close_path()
    c.fill()
    c.set_source_rgb(*GREY_HAIR)
    c.set_line_width(9)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-52, -88)
    c.curve_to(-32, -74, -18, -62, -12, -52)
    c.move_to(26, -92)
    c.curve_to(44, -76, 58, -62, 66, -46)
    c.stroke()
    # Blush
    c.set_source_rgba(0.90, 0.45, 0.42, 0.25)
    for sx in (-1, 1):
        c.arc(sx * 46, 4, 16, 0, 2 * math.pi)
        c.fill()
    # Eyes
    c.set_source_rgb(*INK)
    for sx in (-1, 1):
        ex = sx * 30
        ey = -14
        if mood == "laugh":
            c.set_line_width(6.5)
            c.arc(ex, ey + 6, 13, math.pi * 1.15, math.pi * 1.85)
            c.stroke()
        else:
            c.arc(ex, ey, 8, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*WHITE)
            c.arc(ex - 2, ey - 2, 2.5, 0, 2 * math.pi)
            c.fill()
            c.set_source_rgb(*INK)
        c.set_line_width(5)
        c.move_to(ex - 14, ey - 22)
        c.line_to(ex + 14, ey - 24)
        c.stroke()
    # Happy tear glisten
    if tear > 0.05:
        c.set_source_rgba(0.55, 0.82, 0.98, 0.9 * tear)
        c.arc(-34, 2 + tear * 14, 7, 0, 2 * math.pi)
        c.fill()
        c.arc(34, 0 + tear * 10, 6, 0, 2 * math.pi)
        c.fill()
    # Mouth
    c.set_line_width(6)
    c.set_source_rgb(*INK)
    if mood == "laugh":
        c.arc(0, 12, 26, math.pi * 0.1, math.pi * 0.9)
        c.close_path()
        c.set_source_rgb(*CHERRY_DARK)
        c.fill()
        c.arc(0, 12, 26, math.pi * 0.1, math.pi * 0.9)
        c.set_source_rgb(*INK)
        c.stroke()
    else:
        c.arc(0, 14, 22, math.pi * 0.15, math.pi * 0.85)
        c.stroke()
    c.restore()


def sprout(c, x, y, s, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0.95, 0.65, 0.20, a)
    c.arc(0, 0, 70, math.pi, 2 * math.pi)
    c.fill()
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(-3, 4):
        ang = math.pi * 1.5 + k * 0.38
        c.move_to(math.cos(ang) * 88, math.sin(ang) * 88)
        c.line_to(math.cos(ang) * 112, math.sin(ang) * 112)
        c.stroke()
    c.set_source_rgba(0.11, 0.45, 0.49, a)
    c.set_line_width(12)
    c.move_to(-130, 0)
    c.line_to(130, 0)
    c.stroke()
    c.set_source_rgba(0.18, 0.62, 0.38, a)
    c.set_line_width(12)
    c.move_to(0, 0)
    c.curve_to(0, -30, 2, -50, 0, -70)
    c.stroke()
    for sx in (-1, 1):
        c.move_to(0, -52)
        c.curve_to(sx * 20, -90, sx * 55, -90, sx * 62, -70)
        c.curve_to(sx * 40, -45, sx * 15, -46, 0, -52)
        c.fill()
    c.restore()


def draw_safe_zones(c):
    c.save()
    # Danger zones: top 270, bottom 400 (from 1520), right 70, left 70
    c.set_source_rgba(1.0, 0.15, 0.15, 0.22)
    c.rectangle(0, 0, VW, 270)
    c.rectangle(0, 1520, VW, VH - 1520)
    c.rectangle(0, 270, 70, 1250)
    c.rectangle(VW - 70, 270, 70, 1250)
    c.fill()
    # Safe band box: x 90..990, y 300..1340
    c.set_source_rgba(0.1, 0.9, 0.3, 0.9)
    c.set_line_width(4)
    c.rectangle(90, 300, 900, 1040)
    c.stroke()
    # Caption band y 1100..1300
    c.set_source_rgba(0.2, 0.7, 1.0, 0.7)
    c.set_line_width(2)
    c.set_dash([12, 8])
    c.rectangle(90, 1100, 900, 200)
    c.stroke()
    c.restore()
