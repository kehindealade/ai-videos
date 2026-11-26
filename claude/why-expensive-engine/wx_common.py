import cairo, math
VW, VH, FPS = 1080, 1920, 30
HEAD = "Anton"
LBL = "Share Tech Mono"
HAND = "Architects Daughter"
CAPF = "Poppins"
BODY = "Inter"
WHITE = (0.93, 0.97, 1.0)
CYAN = (0.38, 0.86, 1.0)
YEL = (1.0, 0.86, 0.32)
RED = (1.0, 0.45, 0.42)
GREEN = (0.45, 0.95, 0.62)
GOLD = (0.89, 0.70, 0.25)
B0 = (0.03, 0.16, 0.42)
B1 = (0.01, 0.08, 0.26)
DARK = (0.02, 0.09, 0.27)
BOLDS = {"Poppins", "Inter", "DejaVu Sans Mono"}


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


def arrowhead(c, x, y, ang, s, col, a):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.move_to(0, 0)
    c.line_to(-s, -s * 0.38)
    c.line_to(-s, s * 0.38)
    c.close_path()
    c.set_source_rgba(*col, a)
    c.fill()
    c.restore()


def dim(c, x1, y1, x2, y2, label, off=0, col=WHITE, a=1.0, prog=1.0, size=30, side=1):
    ang = math.atan2(y2 - y1, x2 - x1)
    nx, ny = -math.sin(ang) * side, math.cos(ang) * side
    ax, ay, bx, by = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
    for px, py, qx, qy in ((x1, y1, ax, ay), (x2, y2, bx, by)):
        ln(c, [(px + nx * 12, py + ny * 12), (qx + nx * 22, qy + ny * 22)], col, 2.5, a * 0.8, prog=prog)
    ln(c, [(ax, ay), (bx, by)], col, 3, a, prog=prog)
    if prog > 0.95:
        arrowhead(c, ax, ay, ang + math.pi, 20, col, a)
        arrowhead(c, bx, by, ang, 20, col, a)
    if label:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        c.save()
        c.translate(mx, my)
        r = ang if abs(ang) < math.pi / 2 else ang + math.pi
        c.rotate(r)
        w = tw(c, label, size, LBL) + 24
        c.rectangle(-w / 2, -size * 0.62, w, size * 1.15)
        c.set_source_rgba(*B1, a)
        c.fill()
        txt(c, label, 0, size * 0.34, size, col, LBL, "c", a)
        c.restore()


def callout(c, x, y, w, lines, col=YEL, a=1.0, sc=1.0, size=40, head=None, tip=None, fill=True):
    if a <= 0:
        return
    hs = [size * (2.0 if s.startswith("^") else 1.2) for s in lines]
    h = sum(hs) + 34 + (size * 0.9 if head else 0)
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.scale(max(sc, 0.001), max(sc, 0.001))
    c.translate(-w / 2, -h / 2)
    rrect(c, 0, 0, w, h, 10)
    c.set_source_rgba(*DARK, a * 0.96)
    c.fill_preserve()
    c.set_source_rgba(*col, a)
    c.set_line_width(4)
    c.stroke()
    yy = 18
    if head:
        txt(c, head, w / 2, yy + size * 0.6, size * 0.62, col, LBL, "c", a * 0.9)
        yy += size * 0.9
    for s, hh in zip(lines, hs):
        big = s.startswith("^")
        s2 = s[1:] if big else s
        if big:
            txt(c, s2, w / 2, yy + hh * 0.84, size * 1.7, col, HEAD, "c", a)
        else:
            txt(c, s2, w / 2, yy + hh * 0.72, size, WHITE, LBL, "c", a)
        yy += hh
    c.restore()
    if tip is not None:
        tx, ty = tip
        ox, oy = x + w / 2, y + h
        ln(c, [(ox, oy), (tx, ty)], col, 3, a)
        c.arc(tx, ty, 9, 0, 2 * math.pi)
        c.set_source_rgba(*col, a)
        c.fill()
    return h


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
