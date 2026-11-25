import cairo, math, random

W, H, FPS = 1920, 1080, 30
HEAD = "Archivo Black"
BODY = "DM Sans"
MONO = "Anonymous Pro"

PAPER = (0.975, 0.977, 0.985)
GRID = (0.85, 0.87, 0.91)
HDR = (0.915, 0.925, 0.955)
HDRT = (0.44, 0.47, 0.56)
NAVY = (0.10, 0.13, 0.29)
INK = (0.10, 0.12, 0.22)
SOFT = (0.40, 0.43, 0.52)
TEAL = (0.05, 0.56, 0.50)
TEAL_L = (0.82, 0.95, 0.92)
CORAL = (0.86, 0.28, 0.22)
CORAL_L = (0.99, 0.88, 0.85)
GOLD = (0.96, 0.69, 0.12)
GOLD_L = (1.0, 0.95, 0.80)
VIOLET = (0.40, 0.31, 0.80)
VIOLET_L = (0.91, 0.89, 0.99)
SKY = (0.20, 0.50, 0.90)
SKY_L = (0.87, 0.93, 1.0)
WHITE = (1, 1, 1)
GREYB = (0.72, 0.74, 0.80)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def e(t, a, b):
    return ease((t - a) / max(1e-6, b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def back(x):
    x = clamp(x)
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def font(c, f, bold=True):
    c.select_font_face(f, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)


def txt(c, s, x, y, size, col, f=BODY, align="c", a=1.0, bold=True, stroke=None, sw=8):
    if a <= 0:
        return 0
    font(c, f, bold)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.x_advance / 2
    elif align == "r":
        x -= ex.x_advance
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
    return ex.x_advance


def tw(c, s, size, f=BODY, bold=True):
    font(c, f, bold)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def fit(c, s, size, maxw, f=BODY):
    while size > 20 and tw(c, s, size, f) > maxw:
        size -= 2
    return size


def rr(c, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def fill(c, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.fill()


def box(c, x, y, w, h, col, a=1.0, r=0, line=None, lw=2):
    rr(c, x, y, w, h, r)
    c.set_source_rgba(*col, a)
    if line:
        c.fill_preserve()
        c.set_source_rgba(*line, a)
        c.set_line_width(lw)
        c.stroke()
    else:
        c.fill()


def circle(c, x, y, r, col, a=1.0, line=None, lw=4):
    c.new_path()
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(*col, a)
    if line:
        c.fill_preserve()
        c.set_source_rgba(*line, a)
        c.set_line_width(lw)
        c.stroke()
    else:
        c.fill()


def line(c, pts, col, w=6, a=1.0, prog=1.0, dash=None):
    if prog <= 0 or a <= 0:
        return
    segs = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    goal = sum(segs) * clamp(prog)
    c.set_source_rgba(*col, a)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_dash(dash or [])
    c.move_to(*pts[0])
    run = 0
    for i, sl in enumerate(segs):
        if run + sl <= goal:
            c.line_to(*pts[i + 1])
            run += sl
        else:
            f = (goal - run) / max(sl, 1e-6)
            c.line_to(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
            break
    c.stroke()
    c.set_dash([])


def arrow(c, x1, y1, x2, y2, col=INK, w=7, a=1.0, prog=1.0, head=24):
    if prog <= 0 or a <= 0:
        return
    ang = math.atan2(y2 - y1, x2 - x1)
    ex, ey = lerp(x1, x2, prog), lerp(y1, y2, prog)
    bx, by = ex - math.cos(ang) * head * 0.6, ey - math.sin(ang) * head * 0.6
    line(c, [(x1, y1), (bx, by)], col, w, a)
    if prog > 0.15:
        c.save()
        c.translate(ex, ey)
        c.rotate(ang)
        c.move_to(0, 0)
        c.line_to(-head, -head * 0.55)
        c.line_to(-head, head * 0.55)
        c.close_path()
        c.set_source_rgba(*col, a)
        c.fill()
        c.restore()


def shadow(c, x, y, w, h, r=10, a=0.16, off=8):
    for i in range(3):
        c.set_source_rgba(0.1, 0.12, 0.25, a / 3)
        rr(c, x - i * 2 + off * 0.3, y + off - i, w + i * 4, h + i * 3, r + i)
        c.fill()


def logo(c, x, y, s=1.0, a=1.0, light=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(0.96, 0.72, 0.22, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    for p in pts[:-1]:
        c.arc(p[0], p[1], 7, 0, 2 * math.pi)
        c.set_source_rgba(0.99, 0.97, 0.90, a)
        c.fill_preserve()
        c.set_source_rgba(0.96, 0.72, 0.22, a)
        c.set_line_width(3)
        c.stroke()
    c.arc(60, 60, 13, 0, 2 * math.pi)
    c.set_source_rgba(0.12, 0.64, 0.36, a)
    c.fill()
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(4)
    c.move_to(54, 60)
    c.line_to(59, 65)
    c.line_to(67, 55)
    c.stroke()
    c.restore()


def person(c, x, y, s, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.arc(x, y - 56 * s, 17 * s, 0, 2 * math.pi)
    c.fill()
    rr(c, x - 24 * s, y - 34 * s, 48 * s, 62 * s, 20 * s)
    c.fill()
    rr(c, x - 24 * s, y + 8 * s, 18 * s, 40 * s, 6 * s)
    c.fill()
    rr(c, x + 6 * s, y + 8 * s, 18 * s, 40 * s, 6 * s)
    c.fill()


def elder(c, x, y, s, col, a=1.0):
    person(c, x, y, s, col, a)
    line(c, [(x + 34 * s, y - 10 * s), (x + 38 * s, y + 48 * s)], col, 5 * s, a)
    line(c, [(x + 24 * s, y - 14 * s), (x + 36 * s, y - 12 * s)], col, 5 * s, a)


def bank_icon(c, x, y, s, col, a=1.0):
    c.set_source_rgba(*col, a)
    c.move_to(x - 60 * s, y - 20 * s)
    c.line_to(x, y - 62 * s)
    c.line_to(x + 60 * s, y - 20 * s)
    c.close_path()
    c.fill()
    for i in range(4):
        rr(c, x - 50 * s + i * 30 * s, y - 14 * s, 16 * s, 52 * s, 3 * s)
        c.fill()
    rr(c, x - 64 * s, y + 44 * s, 128 * s, 14 * s, 3 * s)
    c.fill()


def coin(c, x, y, r, a=1.0):
    circle(c, x, y, r, (0.97, 0.78, 0.28), a, (0.72, 0.52, 0.10), r * 0.12)
    circle(c, x, y, r * 0.70, (0.99, 0.87, 0.45), a, (0.76, 0.56, 0.14), r * 0.06)
    txt(c, "$", x, y + r * 0.36, r * 1.0, (0.60, 0.40, 0.06), HEAD, "c", a)


def money_fmt(v, cents=False):
    if cents:
        return "${:,.2f}".format(v)
    return "${:,.0f}".format(v)


def stamp(c, x, y, s, col, k, size=80, ang=-0.10, f=HEAD):
    if k <= 0:
        return
    sc = 1 + 0.6 * (1 - ease(k * 2.2))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(sc, sc)
    w = tw(c, s, size, f) + 60
    a = min(1, k * 4)
    c.set_line_width(9)
    c.set_source_rgba(*col, a)
    rr(c, -w / 2, -size * 0.80, w, size * 1.22, 12)
    c.stroke()
    txt(c, s, 0, size * 0.30, size, col, f, "c", a)
    c.restore()


def check_paper(c, x, y, w, h, amount, a=1.0, ang=0.0, payee="YOU", memo="MONTHLY BENEFIT"):
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(ang)
    c.translate(-w / 2, -h / 2)
    shadow(c, 0, 0, w, h, 12, 0.22 * a, 10)
    g = cairo.LinearGradient(0, 0, w, h)
    g.add_color_stop_rgba(0, 0.93, 0.97, 1.0, a)
    g.add_color_stop_rgba(1, 0.84, 0.91, 0.99, a)
    rr(c, 0, 0, w, h, 12)
    c.set_source(g)
    c.fill()
    c.set_source_rgba(0.55, 0.68, 0.88, 0.35 * a)
    c.set_line_width(1.2)
    for i in range(0, int(w), 14):
        c.move_to(i, 0)
        c.line_to(i + h * 0.4, h)
    c.stroke()
    rr(c, 6, 6, w - 12, h - 12, 9)
    c.set_source_rgba(*NAVY, a)
    c.set_line_width(3)
    c.stroke()
    s = h / 300.0
    txt(c, "SOCIAL SECURITY BENEFIT", 30 * s, 52 * s, 26 * s, NAVY, BODY, "l", a)
    txt(c, "PAY TO", 30 * s, 128 * s, 22 * s, SOFT, BODY, "l", a)
    txt(c, payee, 120 * s, 130 * s, 40 * s, INK, HEAD, "l", a)
    c.set_source_rgba(*NAVY, 0.5 * a)
    c.set_line_width(2)
    c.move_to(120 * s, 142 * s)
    c.line_to(w * 0.55, 142 * s)
    c.stroke()
    bw = w * 0.36
    box(c, w - bw - 30 * s, 90 * s, bw, 70 * s, WHITE, a, 6 * s, NAVY, 3)
    sz = fit(c, amount, 50 * s, bw - 24 * s, MONO)
    txt(c, amount, w - bw / 2 - 30 * s, 142 * s, sz, INK, MONO, "c", a)
    txt(c, memo, 30 * s, 252 * s, 22 * s, SOFT, BODY, "l", a)
    c.set_source_rgba(*NAVY, 0.6 * a)
    c.move_to(w * 0.55, 245 * s)
    c.curve_to(w * 0.62, 215 * s, w * 0.66, 260 * s, w * 0.72, 232 * s)
    c.curve_to(w * 0.76, 220 * s, w * 0.80, 250 * s, w * 0.88, 236 * s)
    c.set_line_width(3)
    c.stroke()
    c.restore()


def cnt(v0, v1, k, cents=False, pre="$"):
    v = lerp(v0, v1, ease(k))
    if cents:
        return pre + "{:,.2f}".format(v)
    return pre + "{:,.0f}".format(v)
