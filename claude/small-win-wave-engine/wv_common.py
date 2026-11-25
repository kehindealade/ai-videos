import cairo, math
VW, VH, FPS = 1080, 1920, 30
H = "Luckiest Guy"
B = "Inter"
INK = (0.10, 0.09, 0.14)
CREAM = (1.0, 0.96, 0.86)
CORAL = (0.95, 0.40, 0.33)
MINT = (0.55, 0.88, 0.76)
WHITE = (1, 1, 1)


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


def lerp(a, b, k):
    return a + (b - a) * k


def lerp2(p, q, k):
    return (lerp(p[0], q[0], k), lerp(p[1], q[1], k))


def font(c, name, bold=None):
    if bold is None:
        bold = name != H
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)


def tw(c, s, size, f=H, bold=None):
    font(c, f, bold)
    c.set_font_size(size)
    ex = c.text_extents(s)
    return ex.width + ex.x_bearing


def txt(c, s, x, y, size, col, f=H, align="c", a=1.0, bold=None):
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


def darken(col, k):
    return tuple(v * (1 - k) for v in col)


def lighten(col, k):
    return tuple(v + (1 - v) * k for v in col)


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
