import cairo, math
VW, VH, FPS = 1080, 1920, 30
H = "Poppins"
B = "Inter"
M = "DejaVu Sans Mono"
GOLD = (0.89, 0.70, 0.25)
GREEN = (0.24, 0.86, 0.52)
RED = (0.90, 0.22, 0.29)
AMBER = (0.98, 0.72, 0.20)
CREAM = (0.98, 0.94, 0.80)
INK = (0.08, 0.10, 0.16)


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


def txt(c, s, x, y, size, col, f=H, align="c", a=1.0, bold=True, stroke=None, sw=10):
    font(c, f, bold)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.width / 2 + ex.x_bearing
    elif align == "r":
        x -= ex.width + ex.x_bearing
    c.move_to(x, y)
    if stroke:
        c.text_path(s)
        c.set_source_rgba(*stroke, a)
        c.set_line_width(sw)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgba(*col, a)
        c.fill()
    else:
        c.set_source_rgba(*col, a)
        c.show_text(s)
    c.new_path()
    return ex.width


def wrap(c, s, maxw, size, f=H, bold=True):
    font(c, f, bold)
    c.set_font_size(size)
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if c.text_extents(t).x_advance > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def block(c, s, cx, cy, size, col, maxw=920, lh=1.18, a=1.0, f=H, stroke=None, sw=10):
    ls = wrap(c, s, maxw, size, f)
    y0 = cy - (len(ls) - 1) * size * lh / 2 + size * 0.35
    for i, ln in enumerate(ls):
        txt(c, ln, cx, y0 + i * size * lh, size, col, f, a=a, stroke=stroke, sw=sw)
    return len(ls)


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def logo(c, x, y, s, a, col=GOLD):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(*col, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    c.arc(60, 60, 13, 0, 2 * math.pi)
    c.set_source_rgba(0.12, 0.64, 0.36, a)
    c.fill()
    c.restore()


def starburst(c, cx, cy, r1, r2, n, rot=0):
    c.new_path()
    for i in range(n * 2):
        a = rot + i * math.pi / n
        r = r1 if i % 2 == 0 else r2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        (c.move_to if i == 0 else c.line_to)(x, y)
    c.close_path()
