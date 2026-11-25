import cairo, math
VW, VH, FPS = 1080, 1920, 30
H = "Rounded Mplus 1c"
B = "Inter"
INK = (0.07, 0.10, 0.18)
WHITE = (1, 1, 1)
GOLD = (0.98, 0.78, 0.20)
CORAL = (0.96, 0.42, 0.38)
NAVY0 = (0.055, 0.075, 0.155)
NAVY1 = (0.09, 0.115, 0.22)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return x * x * (3 - 2 * x)


def back(x):
    x = clamp(x)
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def font(c, name, bold=True):
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)


def tw(c, s, size, f=H, bold=True):
    font(c, f, bold)
    c.set_font_size(size)
    ex = c.text_extents(s)
    return ex.width + ex.x_bearing


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


def lighten(col, k):
    return tuple(v + (1 - v) * k for v in col)


def darken(col, k):
    return tuple(v * (1 - k) for v in col)


AV_COL = [(0.96, 0.42, 0.38), (0.35, 0.80, 0.66), (0.98, 0.78, 0.25), (0.40, 0.65, 0.95),
          (0.68, 0.55, 0.92), (0.97, 0.58, 0.26), (0.93, 0.50, 0.72), (0.30, 0.72, 0.78)]
SKIN = [(0.46, 0.30, 0.19), (0.80, 0.60, 0.44), (0.36, 0.23, 0.15), (0.93, 0.76, 0.62),
        (0.55, 0.36, 0.23), (0.68, 0.46, 0.31), (0.42, 0.27, 0.17), (0.86, 0.66, 0.50)]
HAIR = (0.12, 0.09, 0.08)


def avatar(c, cx, cy, r, i, a=1.0):
    c.save()
    c.arc(cx, cy, r, 0, 2 * math.pi)
    c.clip()
    c.set_source_rgba(*AV_COL[i % 8], a)
    c.paint()
    c.set_source_rgba(*darken(SKIN[i % 8], 0.15), a)
    c.arc(cx, cy + r * 0.95, r * 0.62, 0, 2 * math.pi)
    c.fill()
    hr = r * 0.40
    hy = cy - r * 0.08
    k = i % 8
    c.set_source_rgba(*HAIR, a)
    if k == 1:
        c.arc(cx, hy - hr * 0.7, hr * 1.25, 0, 2 * math.pi)
        c.fill()
    if k == 2:
        c.rectangle(cx - hr * 1.15, hy - hr * 0.2, hr * 0.55, hr * 2.4)
        c.rectangle(cx + hr * 0.6, hy - hr * 0.2, hr * 0.55, hr * 2.4)
        c.fill()
    if k == 7:
        for j in range(5):
            ang = math.pi + j * math.pi / 4
            c.arc(cx + math.cos(ang) * hr * 1.0, hy + math.sin(ang) * hr * 0.9, hr * 0.42, 0, 2 * math.pi)
            c.fill()
    if k == 6:
        c.arc(cx, hy - hr * 1.3, hr * 0.5, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(*SKIN[k], a)
    c.arc(cx, hy, hr, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*HAIR, a)
    if k in (0, 3, 6):
        c.arc(cx, hy, hr * 1.02, math.pi * 1.02, math.pi * 1.98)
        c.close_path()
        c.fill()
    if k == 4:
        c.set_source_rgba(0.95, 0.95, 0.95, a)
        c.arc(cx, hy, hr * 1.04, math.pi * 1.0, math.pi * 2.0)
        c.close_path()
        c.fill()
        c.rectangle(cx - hr * 0.2, hy - hr * 0.1, hr * 1.5, hr * 0.22)
        c.fill()
    if k == 5:
        c.set_source_rgba(0.20, 0.55, 0.55, a)
        c.rectangle(cx - hr * 1.02, hy - hr * 0.75, hr * 2.04, hr * 0.5)
        c.fill()
    c.set_source_rgba(0.1, 0.07, 0.06, a)
    for sx in (-1, 1):
        c.arc(cx + sx * hr * 0.38, hy + hr * 0.05, max(1.5, hr * 0.09), 0, 2 * math.pi)
        c.fill()
    c.set_line_width(max(1.5, hr * 0.09))
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.arc(cx, hy + hr * 0.2, hr * 0.38, math.pi * 0.15, math.pi * 0.85)
    c.stroke()
    if k == 3:
        c.set_line_width(max(1.5, hr * 0.08))
        for sx in (-1, 1):
            c.arc(cx + sx * hr * 0.38, hy + hr * 0.05, hr * 0.25, 0, 2 * math.pi)
            c.stroke()
    c.restore()


def sprout(c, x, y, s, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_source_rgba(0.95, 0.65, 0.20, a)
    c.arc(0, 0, 70, math.pi, 2 * math.pi)
    c.fill()
    c.set_source_rgba(0.95, 0.65, 0.20, a)
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(-3, 4):
        ang = math.pi * 1.5 + k * 0.38
        c.move_to(math.cos(ang) * 88, math.sin(ang) * 88)
        c.line_to(math.cos(ang) * 112, math.sin(ang) * 112)
        c.stroke()
    c.set_source_rgba(0.96, 0.92, 0.80, a)
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
