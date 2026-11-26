import cairo, math, random

W, H, FPS = 1920, 1080, 30
SERIF = "Cormorant SC"
NUM = "IBM Plex Serif"
LAB = "Saira ExtraCondensed"
MONO = "DejaVu Sans Mono"
POP = "Poppins"

WALL0 = (0.055, 0.17, 0.14)
WALL1 = (0.03, 0.10, 0.085)
PAPER = (0.965, 0.93, 0.82)
PAPER2 = (0.90, 0.86, 0.72)
INKG = (0.07, 0.25, 0.19)
BRASS = (0.86, 0.68, 0.27)
BRASS2 = (0.58, 0.42, 0.14)
AMBER = (1.0, 0.78, 0.28)
BLACK = (0.04, 0.05, 0.05)
RED = (0.85, 0.20, 0.17)
WHITE = (0.97, 0.97, 0.94)
GREY = (0.62, 0.68, 0.66)
TRUST = (0.93, 0.74, 0.28)
FED = (0.45, 0.64, 0.90)
FOREIGN = (0.92, 0.38, 0.32)
OTHER = (0.40, 0.80, 0.54)
HCOL = [TRUST, FED, FOREIGN, OTHER]
HNAME = ["GOVERNMENT TRUST FUNDS", "THE FEDERAL RESERVE", "FOREIGN HOLDERS", "EVERYONE ELSE"]
HSHORT = ["GOVERNMENT", "FED", "ABROAD", "ALL OTHERS"]
SHARES = [19.2, 11.3, 22.7, 46.8]


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


def font(c, f, bold=True):
    c.select_font_face(f, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)


def _fs(size, f):
    return size * 1.22 if (f == LAB and 0 < size <= 64) else size


def txt(c, s, x, y, size, col, f=LAB, align="c", a=1.0, stroke=None, sw=8):
    size = _fs(size, f)
    font(c, f)
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


def tw(c, s, size, f=LAB):
    size = _fs(size, f)
    font(c, f)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def rr(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


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


def arrow(c, x1, y1, x2, y2, col=WHITE, w=8, a=1.0, prog=1.0, head=26):
    if prog <= 0:
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


def shadow(c, x, y, w, h, r=14, a=0.35, off=10):
    c.set_source_rgba(0, 0, 0, a)
    rr(c, x + off * 0.5, y + off, w, h, r)
    c.fill()


def brass(c, x, y, w, h, r=16, lw=10, a=1.0):
    g = cairo.LinearGradient(x, y, x, y + h)
    g.add_color_stop_rgba(0, 0.95, 0.80, 0.40, a)
    g.add_color_stop_rgba(0.5, *BRASS, a)
    g.add_color_stop_rgba(1, *BRASS2, a)
    rr(c, x, y, w, h, r)
    c.set_source(g)
    c.fill()
    rr(c, x + lw, y + lw, w - 2 * lw, h - 2 * lw, max(4, r - 6))
    c.set_source_rgba(*BLACK, a)
    c.fill()


# ---------- cached wall ----------
_WALLS = {}


def wall_surface(w=W, h=H):
    key = (w, h)
    if key in _WALLS:
        return _WALLS[key]
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *WALL0)
    g.add_color_stop_rgb(1, *WALL1)
    c.set_source(g)
    c.paint()
    pw, ph = 240, 180
    for gy in range(-1, h // ph + 2):
        for gx in range(-1, w // pw + 2):
            x, y = gx * pw + (pw // 2 if gy % 2 else 0), gy * ph
            c.set_source_rgba(1, 1, 1, 0.022)
            c.rectangle(x + 3, y + 3, pw - 6, ph - 6)
            c.fill()
            c.set_source_rgba(0, 0, 0, 0.30)
            c.set_line_width(3)
            c.rectangle(x, y, pw, ph)
            c.stroke()
            c.set_source_rgba(1, 1, 1, 0.05)
            c.set_line_width(2)
            c.move_to(x + 4, y + ph - 3)
            c.line_to(x + 4, y + 4)
            c.line_to(x + pw - 3, y + 4)
            c.stroke()
            for rx, ry in ((x + 16, y + 16), (x + pw - 16, y + 16), (x + 16, y + ph - 16), (x + pw - 16, y + ph - 16)):
                c.set_source_rgba(0, 0, 0, 0.35)
                c.arc(rx + 1, ry + 2, 4.5, 0, 2 * math.pi)
                c.fill()
                c.set_source_rgba(0.55, 0.75, 0.65, 0.16)
                c.arc(rx, ry, 4, 0, 2 * math.pi)
                c.fill()
    rg = cairo.RadialGradient(w / 2, h / 2, min(w, h) * 0.28, w / 2, h / 2, max(w, h) * 0.65)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0)
    rg.add_color_stop_rgba(1, 0, 0, 0, 0.62)
    c.set_source(rg)
    c.paint()
    _WALLS[key] = s
    return s


def draw_wall(c, w=W, h=H):
    c.set_source_surface(wall_surface(w, h), 0, 0)
    c.paint()


# ---------- certificate ----------
CW, CH = 560, 330
_CERT = None


def _guilloche(c, x0, y0, x1, y1, amp, k, col, a):
    c.set_line_width(1.4)
    c.set_source_rgba(*col, a)
    for ph in (0, math.pi):
        c.move_to(x0, y0 + amp * math.sin(ph))
        n = int(x1 - x0)
        for i in range(0, n + 1, 2):
            c.line_to(x0 + i, y0 + amp * math.sin(i * k + ph))
        c.stroke()
        c.move_to(x0, y1 + amp * math.sin(ph))
        for i in range(0, n + 1, 2):
            c.line_to(x0 + i, y1 + amp * math.sin(i * k + ph))
        c.stroke()
    for ph in (0, math.pi):
        c.move_to(x0 + amp * math.sin(ph), y0)
        m = int(y1 - y0)
        for i in range(0, m + 1, 2):
            c.line_to(x0 + amp * math.sin(i * k + ph), y0 + i)
        c.stroke()
        c.move_to(x1 + amp * math.sin(ph), y0)
        for i in range(0, m + 1, 2):
            c.line_to(x1 + amp * math.sin(i * k + ph), y0 + i)
        c.stroke()


def _rosette(c, cx, cy, r, col, a, n=18):
    c.set_line_width(1.2)
    c.set_source_rgba(*col, a)
    for i in range(n):
        ang = i * math.pi / n
        c.save()
        c.translate(cx, cy)
        c.rotate(ang)
        c.scale(1, 0.38)
        c.new_path()
        c.arc(0, 0, r, 0, 2 * math.pi)
        c.restore()
        c.stroke()


def cert_base():
    global _CERT
    if _CERT is not None:
        return _CERT
    S = 2
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, CW * S, CH * S)
    c = cairo.Context(s)
    c.scale(S, S)
    g = cairo.LinearGradient(0, 0, CW, CH)
    g.add_color_stop_rgb(0, *PAPER)
    g.add_color_stop_rgb(1, *PAPER2)
    rr(c, 0, 0, CW, CH, 10)
    c.set_source(g)
    c.fill()
    rng = random.Random(7)
    for _ in range(260):
        c.set_source_rgba(0.5, 0.42, 0.25, 0.05)
        c.arc(rng.uniform(0, CW), rng.uniform(0, CH), rng.uniform(0.5, 2.2), 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(*INKG, 1)
    c.set_line_width(5)
    rr(c, 8, 8, CW - 16, CH - 16, 6)
    c.stroke()
    c.set_line_width(1.5)
    rr(c, 30, 30, CW - 60, CH - 60, 3)
    c.stroke()
    _guilloche(c, 40, 17, CW - 40, CH - 17, 5, 0.09, INKG, 0.55)
    for cx, cy in ((46, 46), (CW - 46, 46), (46, CH - 46), (CW - 46, CH - 46)):
        circle(c, cx, cy, 24, PAPER, 1, INKG, 2)
        _rosette(c, cx, cy, 21, INKG, 0.7, 14)
    c.save()
    c.translate(CW / 2, CH / 2 + 8)
    _rosette(c, 0, 0, 96, INKG, 0.10, 26)
    c.restore()
    txt(c, "THE UNITED STATES OF AMERICA", CW / 2, 76, 25, INKG, SERIF)
    txt(c, "I.O.U.", CW / 2, 150, 92, INKG, SERIF)
    txt(c, "PROMISES TO PAY THE BEARER, WITH INTEREST", CW / 2, 182, 20, INKG, SERIF, a=0.8)
    c.set_source_rgba(*INKG, 0.8)
    c.set_line_width(2)
    c.move_to(150, 194)
    c.line_to(CW - 150, 194)
    c.stroke()
    # seal
    sx, sy = 92, CH - 92
    circle(c, sx, sy, 42, BRASS, 1, BRASS2, 3)
    circle(c, sx, sy, 33, BRASS, 1, BRASS2, 1.5)
    c.set_source_rgba(*BRASS2, 1)
    for i in range(5):
        a1 = -math.pi / 2 + i * 2 * math.pi / 5
        a2 = a1 + 2 * math.pi / 10
        c.line_to(sx + 22 * math.cos(a1), sy + 22 * math.sin(a1)) if i else c.move_to(sx + 22 * math.cos(a1), sy + 22 * math.sin(a1))
        c.line_to(sx + 9 * math.cos(a2), sy + 9 * math.sin(a2))
    c.close_path()
    c.fill()
    _CERT = s
    return s


def cert(c, x, y, s=1.0, holder="", amount="", ang=0.0, a=1.0, serial=0, col=None, blank=False, qmark=False, lift=0.0):
    base = cert_base()
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.translate(-CW / 2, -CH / 2)
    shadow(c, 0, 0, CW, CH, 10, 0.38 * a, 14 + lift)
    c.save()
    c.scale(0.5, 0.5)
    c.set_source_surface(base, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint_with_alpha(a)
    c.restore()
    if holder or qmark:
        bw = CW - 240
        rr(c, 120, 206, bw, 44, 6)
        c.set_source_rgba(*(col or INKG), a)
        c.fill()
        c.set_source_rgba(*BRASS, a)
        c.set_line_width(2)
        rr(c, 124, 210, bw - 8, 36, 4)
        c.stroke()
        txt(c, "?" if qmark else holder, CW / 2, 242, 38 if len(holder) < 16 else (32 if len(holder) < 22 else 27), WHITE, LAB, a=a)
    if amount:
        txt(c, amount, CW / 2, 292, 44, INKG, NUM, a=a)
    txt(c, "No. %07d" % serial, CW - 52, 300, 17, (0.55, 0.12, 0.10), MONO, "r", a)
    c.restore()


def sheet(c, x, y, s=1.0, a=1.0, ang=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    rr(c, -CW / 2, -CH / 2, CW, CH, 10)
    c.set_source_rgba(*PAPER2, a)
    c.fill_preserve()
    c.set_source_rgba(*INKG, a * 0.8)
    c.set_line_width(3)
    c.stroke()
    c.restore()


def stack(c, x, y, n, s=1.0, holder="", amount="", col=None, a=1.0, dy=14, serial=1, grow=1.0, qmark=False):
    k = max(1, int(round(n * clamp(grow))))
    for i in range(k - 1):
        sheet(c, x + ((i * 37) % 5 - 2) * 3 * s, y - (k - 1 - i) * dy * s * -1 + 0, s, a, ((i * 53) % 7 - 3) * 0.006)
    top_y = y - (k - 1) * dy * s
    # sheets are drawn bottom-up: bottom sheet at y, upper ones higher
    cert(c, x, top_y, s, holder, amount, 0.0, a, serial, col, qmark=qmark)


def stack_bottom(c, x, y, n, s=1.0, holder="", amount="", col=None, a=1.0, dy=14, serial=1, grow=1.0):
    k = max(1, int(round(n * clamp(grow))))
    for i in range(k - 1):
        yy = y - i * dy * s
        sheet(c, x + ((i * 37) % 5 - 2) * 3 * s, yy, s, a, ((i * 53) % 7 - 3) * 0.006)
    cert(c, x, y - (k - 1) * dy * s, s, holder, amount, 0.0, a, serial, col)


def stamp(c, x, y, s, col, k, size=96, ang=-0.12):
    if k <= 0:
        return
    sc = 1 + 0.7 * (1 - ease(k * 2.2))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(sc, sc)
    w = tw(c, s, size, LAB) + 70
    a = min(1, k * 4)
    c.set_line_width(11)
    c.set_source_rgba(*col, a)
    rr(c, -w / 2, -size * 0.78, w, size * 1.25, 14)
    c.stroke()
    c.set_line_width(3)
    rr(c, -w / 2 + 12, -size * 0.78 + 12, w - 24, size * 1.25 - 24, 8)
    c.stroke()
    txt(c, s, 0, size * 0.34, size, col, LAB, "c", a)
    c.restore()


def logo(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(0.89, 0.70, 0.25, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    for p in pts[:-1]:
        c.arc(p[0], p[1], 7, 0, 2 * math.pi)
        c.set_source_rgba(0.98, 0.95, 0.86, a)
        c.fill_preserve()
        c.set_source_rgba(0.89, 0.70, 0.25, a)
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


def coin(c, x, y, r, a=1.0):
    circle(c, x, y, r, (0.95, 0.78, 0.30), a, (0.70, 0.50, 0.12), r * 0.12)
    circle(c, x, y, r * 0.72, (0.98, 0.86, 0.45), a, (0.75, 0.55, 0.15), r * 0.06)
    txt(c, "$", x, y + r * 0.38, r * 1.05, (0.62, 0.42, 0.08), LAB, "c", a)


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


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3
