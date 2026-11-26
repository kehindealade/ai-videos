import cairo, math, os, sys
import film as F

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

REC = {}


def rmeter(c, n, bump=0.0):
    REC["meter"] = n


def rtag(c, s, pop=0.0):
    REC["tag"] = s


def rcap(c, t, s, a, b, dark=False, y0=990, size=70, col=None):
    if a <= t <= b:
        k = F.ease(F.seg(t, a, a + 0.35)) * (1 - F.ease(F.seg(t, b - 0.3, b)))
        REC.setdefault("caps", []).append((s, k))


F.meter, F.tag, F.caption = rmeter, rtag, rcap
F.dip = lambda *a, **k: None

INK, CREAM, ORANGE, GREEN, SAGE, CLAY_D, RED = F.INK, F.CREAM, F.ORANGE, F.GREEN, F.SAGE, F.CLAY_D, F.RED


def orange(c, cx, cy, r):
    c.set_source_rgb(*ORANGE)
    c.arc(cx, cy, r, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.22)
    F.ell(c, cx - r * 0.38, cy - r * 0.38, r * 0.26, r * 0.17)
    c.fill()
    c.set_source_rgba(0.6, 0.30, 0.05, 0.35)
    for i in range(14):
        a = i * 2.39
        d = r * (0.25 + 0.6 * ((i * 37) % 10) / 10)
        c.arc(cx + d * math.cos(a), cy + d * math.sin(a), r * 0.025, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgb(0.30, 0.22, 0.12)
    F.rrect(c, cx - r * 0.05, cy - r * 1.08, r * 0.10, r * 0.2, r * 0.04)
    c.fill()
    c.save()
    c.translate(cx + r * 0.22, cy - r * 0.98)
    c.rotate(-0.45)
    c.set_source_rgb(*GREEN)
    F.ell(c, 0, 0, r * 0.36, r * 0.15)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.25)
    c.set_line_width(r * 0.025)
    c.move_to(-r * 0.3, 0)
    c.line_to(r * 0.3, 0)
    c.stroke()
    c.restore()


def sprout(c, cx, cy, r, bg=None):
    c.new_path()
    c.save()
    c.translate(cx, cy)
    c.scale(r / 100.0, r / 100.0)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgb(*F.OCHRE)
    c.set_line_width(8)
    for ang in (-150, -120, -90, -60, -30):
        a = math.radians(ang)
        c.move_to(52 * math.cos(a), 44 + 52 * math.sin(a))
        c.line_to(70 * math.cos(a), 44 + 70 * math.sin(a))
        c.stroke()
    c.arc(0, 44, 40, math.pi, 2 * math.pi)
    c.close_path()
    c.fill()
    c.set_source_rgb(*F.CREAM)
    F.rrect(c, -92, 40, 184, 14, 7)
    c.fill()
    c.set_source_rgb(*GREEN)
    c.set_line_width(10)
    c.move_to(0, 42)
    c.curve_to(2, 10, -4, -30, 0, -58)
    c.stroke()
    for sgn, ang, ln, y in ((-1, -0.45, 40, -50), (1, 0.45, 46, -62)):
        c.save()
        c.translate(0, y)
        c.rotate(ang)
        c.translate(sgn * ln * 0.55, 0)
        c.move_to(-ln * 0.6, 0)
        c.curve_to(-ln * 0.3, -ln * 0.42, ln * 0.3, -ln * 0.42, ln * 0.6, 0)
        c.curve_to(ln * 0.3, ln * 0.42, -ln * 0.3, ln * 0.42, -ln * 0.6, 0)
        c.close_path()
        c.set_source_rgb(0.47, 0.70, 0.40)
        c.fill()
        c.restore()
    c.restore()


def avatar():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 800, 800)
    c = cairo.Context(s)
    c.set_source_rgb(*INK)
    c.paint()
    c.set_source_rgba(*SAGE, 0.18)
    c.arc(400, 410, 330, 0, 2 * math.pi)
    c.fill()
    sprout(c, 400, 420, 270)
    s.write_to_png(os.path.join(OUT, "profile-picture-800.png"))


def watermark():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 150, 150)
    c = cairo.Context(s)
    c.set_source_rgba(*INK, 0.85)
    c.arc(75, 75, 72, 0, 2 * math.pi)
    c.fill()
    sprout(c, 75, 80, 55)
    s.write_to_png(os.path.join(OUT, "watermark-150.png"))


def figure_row(c, xs, scale, faces):
    for i, x in enumerate(xs):
        F.figure(c, x, F.GY, scale, F.STY[(i * 2 + 1) % len(F.STY)], face=faces)


def banner():
    W, H = 2560, 1440
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.set_source_rgb(*F.SKY)
    c.paint()
    gy = 900
    c.set_source_rgb(*F.GROUND)
    c.rectangle(0, gy, W, H - gy)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, gy, W, 6)
    c.fill()
    c.set_source_rgba(1, 0.97, 0.88, 0.9)
    c.arc(2400, 590, 46, 0, 2 * math.pi)
    c.fill()
    k = 0.5
    c.save()
    c.translate(-420, gy - F.GY * k)
    c.scale(k, k)
    F.stall(0, 0.0) if False else None
    F.stall(c, 1.0)
    F.hero(c, 1.0, x=1850, mood="ok", whistle=1, face=-1)
    c.restore()
    c.save()
    c.translate(1720, gy - F.GY * k)
    c.scale(k, k)
    F.stall(c, 1.0, ox=280, wall=(0.45, 0.56, 0.60), wall_d=(0.36, 0.47, 0.52), awn=(F.OCHRE, F.CREAM), guitar=False)
    for i, x in enumerate((760, 900)):
        F.figure(c, x, F.GY, 1.0, F.STY[(i * 3 + 1) % len(F.STY)], face=1)
    c.restore()
    F.text(c, "SMALL WIN FILMS", W / 2, 715, 132, INK)
    F.text(c, "Small stories. Small wins.", W / 2, 805, 56, INK, 0.75)
    sprout(c, W / 2, 556, 58)
    s.write_to_png(os.path.join(OUT, "banner-2560x1440.png"))
    c.set_source_rgba(1, 0, 0, 0.9)
    c.set_line_width(4)
    c.rectangle(507, 508, 1546, 423)
    c.stroke()
    s.write_to_png(os.path.join(OUT, "_banner-check.png"))


def thumb():
    src = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
    sc = cairo.Context(src)
    F.s6b(sc, 9.0)
    F.hero(sc, 9.0, mood="tired", sit=1.0, lean=0.16 + 0.012 * math.sin(9.0 * 1.2), rh=(60, -40), lh=(-60, -40))
    F.lantern(sc, 690)
    F.tint(sc, F.NIGHT, 0.20)
    F.glow(sc, 640, 640, 520, 0.38)
    rim = cairo.RadialGradient(470, 500, 0, 470, 500, 300)
    rim.add_color_stop_rgba(0, 0.05, 0.06, 0.14, 0)
    rim.add_color_stop_rgba(1, 0.05, 0.06, 0.14, 0)
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    c = cairo.Context(s)
    k = 1280 / 960
    c.save()
    c.scale(k, k)
    c.set_source_surface(src, -150, -365)
    c.paint()
    c.restore()
    g = cairo.LinearGradient(560, 0, 1280, 0)
    g.add_color_stop_rgba(0, 0.05, 0.06, 0.12, 0)
    g.add_color_stop_rgba(0.35, 0.05, 0.06, 0.12, 0.55)
    g.add_color_stop_rgba(1, 0.05, 0.06, 0.12, 0.75)
    c.set_source(g)
    c.paint()
    x0, y0, w, h = 790, 64, 440, 592
    c.set_source_rgba(0, 0, 0, 0.35)
    F.rrect(c, x0 + 10, y0 + 14, w, h, 44)
    c.fill()
    c.set_source_rgb(*CREAM)
    F.rrect(c, x0, y0, w, h, 44)
    c.fill()
    c.set_source_rgb(*INK)
    F.rrect(c, x0 + 90, y0 + 36, w - 180, 96, 48)
    c.fill()
    F.text(c, "DAY 40", x0 + w / 2, y0 + 108, 66, CREAM)
    F.text(c, "0", x0 + w / 2, y0 + 440, 330, RED)
    F.text(c, "CUSTOMERS", x0 + w / 2, y0 + 540, 62, INK)
    s.write_to_png(os.path.join(OUT, "thumbnail-for-40-days-1280x720.png"))


avatar()
watermark()
banner()
thumb()
print("ok")
