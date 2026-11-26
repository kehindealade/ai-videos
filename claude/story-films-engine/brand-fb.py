import cairo, math, os, sys
import film as F

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

INK, CREAM, GREEN, SAGE, RED = F.INK, F.CREAM, F.GREEN, F.SAGE, F.RED


def sprout(c, cx, cy, r):
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


def scene(W, H, gy, title_y, tag_y, logo_y, title_size, tag_size, shift=0):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.set_source_rgb(*F.SKY)
    c.paint()
    c.set_source_rgb(*F.GROUND)
    c.rectangle(0, gy, W, H - gy)
    c.fill()
    c.set_source_rgba(*INK, 0.10)
    c.rectangle(0, gy, W, 6)
    c.fill()
    k = 0.5
    c.save()
    c.translate(-420 + shift, gy - F.GY * k)
    c.scale(k, k)
    F.stall(c, 1.0)
    F.hero(c, 1.0, x=1850, mood="ok", whistle=1, face=-1)
    c.restore()
    c.save()
    c.translate(W - 840 - shift, gy - F.GY * k)
    c.scale(k, k)
    F.stall(c, 1.0, ox=280, wall=(0.45, 0.56, 0.60), wall_d=(0.36, 0.47, 0.52), awn=(F.OCHRE, F.CREAM), guitar=False)
    for i, x in enumerate((760, 900)):
        F.figure(c, x, F.GY, 1.0, F.STY[(i * 3 + 1) % len(F.STY)], face=1)
    c.restore()
    F.text(c, "SMALL WIN FILMS", W / 2, title_y, title_size, INK)
    F.text(c, "Small stories. Small wins.", W / 2, tag_y, tag_size, INK, 0.75)
    sprout(c, W / 2, logo_y, title_size * 0.44)
    return s


def banner():
    s = scene(2560, 1440, 900, 715, 805, 556, 132, 56)
    c = cairo.Context(s)
    c.set_source_rgba(1, 0.97, 0.88, 0.9)
    c.arc(2330, 300, 46, 0, 2 * math.pi)
    c.fill()
    s.write_to_png(os.path.join(OUT, "youtube-banner-2560x1440.png"))


def fb_cover():
    s = scene(1640, 624, 520, 360, 430, 210, 92, 40, shift=-170)
    s.write_to_png(os.path.join(OUT, "facebook-cover-1640x624.png"))


def thumb():
    src = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
    sc = cairo.Context(src)
    F.s6b(sc, 9.0)
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
    s.write_to_png(os.path.join(OUT, "thumbnail-film1-1280x720.png"))


avatar()
watermark()
banner()
fb_cover()
thumb()
print("ok")
