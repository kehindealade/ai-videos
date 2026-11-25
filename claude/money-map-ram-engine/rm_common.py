import cairo, math
VW, VH, FPS = 1080, 1920, 30
HEAD = "Archivo Black"
LBL = "Anonymous Pro"
CAPF = "Poppins"
BOLDS = {"Poppins", "Anonymous Pro", "Inter"}
WHITE = (0.95, 0.97, 0.98)
MINT = (0.25, 1.0, 0.72)
AMBER = (1.0, 0.64, 0.18)
RED = (1.0, 0.36, 0.34)
GOLDC = (0.93, 0.77, 0.32)
BOARD = (0.04, 0.2, 0.17)
BOARD2 = (0.06, 0.28, 0.23)
INK = (0.03, 0.04, 0.055)
G0 = (0.075, 0.09, 0.115)
G1 = (0.02, 0.025, 0.04)
GREY = (0.55, 0.6, 0.66)


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


def mix(c1, c2, k):
    return tuple(lerp(a, b, k) for a, b in zip(c1, c2))


def font(c, name):
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if name in BOLDS else cairo.FONT_WEIGHT_NORMAL)


def txt(c, s, x, y, size, col, f=HEAD, align="c", a=1.0, stroke=None, sw=10):
    font(c, f)
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


def tw(c, s, size, f):
    font(c, f)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def fit(c, s, maxw, size, f=HEAD):
    while tw(c, s, size, f) > maxw and size > 20:
        size -= 2
    return size


def wrap(c, s, maxw, size, f=CAPF):
    font(c, f)
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


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def pill(c, cx, cy, w, h, col, a=1.0):
    rrect(c, cx - w / 2, cy - h / 2, w, h, h / 2)
    c.set_source_rgba(*col, a)
    c.fill()


def ln(c, pts, col=WHITE, w=5, a=1.0, closed=False, prog=1.0, dash=None):
    if prog <= 0 or a <= 0:
        return
    seq = list(pts) + ([pts[0]] if closed else [])
    segs = [math.hypot(seq[i + 1][0] - seq[i][0], seq[i + 1][1] - seq[i][1]) for i in range(len(seq) - 1)]
    total = sum(segs) or 1
    goal = total * clamp(prog)
    c.set_source_rgba(*col, a)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_dash(dash or [])
    c.move_to(*seq[0])
    run = 0
    for i, sl in enumerate(segs):
        if run + sl <= goal:
            c.line_to(*seq[i + 1])
            run += sl
        else:
            f = (goal - run) / max(sl, 1e-6)
            c.line_to(seq[i][0] + (seq[i + 1][0] - seq[i][0]) * f, seq[i][1] + (seq[i + 1][1] - seq[i][1]) * f)
            break
    c.stroke()
    c.set_dash([])


def glow(c, x, y, r, col, a):
    if a <= 0:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()


def logo(c, x, y, s, a, col=GOLDC):
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


def tri(c, cx, cy, s, col, a=1.0, up=True):
    d = -1 if up else 1
    c.move_to(cx, cy + d * s)
    c.line_to(cx - s * 0.9, cy - d * s * 0.7)
    c.line_to(cx + s * 0.9, cy - d * s * 0.7)
    c.close_path()
    c.set_source_rgba(*col, a)
    c.fill()


def tag(c, x, y, w, h, label, col, tcol=INK, a=1.0, size=40, f=HEAD):
    rrect(c, x, y, w, h, 14)
    c.set_source_rgba(*col, a)
    c.fill()
    txt(c, label, x + w / 2, y + h / 2 + size * 0.36, size, tcol, f, "c", a)
