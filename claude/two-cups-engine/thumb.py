import cairo, sys
import film as F

F.UI_ON = False


def base(z, fx, fy, t=1.4):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
    c = cairo.Context(s)
    c.save()
    F.cam(c, z, fx, fy)
    F.cold_draw(c, t, "sad", (0.85, 0.75), 1.0)
    c.restore()
    F.vignette(c, 0.3)
    return s


def bold(c, s, x, y, size, col, align="l", stroke=10):
    c.select_font_face(F.FONT)
    c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        x = x - e.width / 2 - e.x_bearing
    elif align == "r":
        x = x - e.width - e.x_bearing
    c.move_to(x + 5, y + 8)
    c.text_path(s)
    c.set_source_rgba(0, 0, 0, 0.45)
    c.fill()
    c.move_to(x, y)
    c.text_path(s)
    c.set_source_rgb(*F.INK)
    c.set_line_width(stroke)
    c.set_line_join(1)
    c.stroke_preserve()
    c.set_source_rgb(*col)
    c.fill()


def thumbnail(path):
    b = base(1.12, 860, 600)
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    c = cairo.Context(out)
    c.save()
    c.scale(1280 / 1920, 720 / 1080)
    c.set_source_surface(b, 0, 0)
    c.paint()
    c.restore()
    g = cairo.LinearGradient(700, 0, 1280, 0)
    g.add_color_stop_rgba(0, 0.06, 0.07, 0.10, 0)
    g.add_color_stop_rgba(1, 0.06, 0.07, 0.10, 0.55)
    c.set_source(g)
    c.rectangle(0, 0, 1280, 720)
    c.fill()
    bold(c, "STILL", 1240, 150, 118, F.CREAM, "r", 12)
    bold(c, "TWO CUPS", 1240, 270, 118, F.YEL, "r", 12)
    bold(c, "2", 1010, 560, 300, F.CREAM, "c", 14)
    F.tag_draw(c, 34, 62, 40, "DAY 40")
    out.write_to_png(path)


def cover(path):
    b = base(1.0, 960, 540)
    VW, VH = 1080, 1920
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(out)
    x0, cw = 250, 1100
    b.flush()
    d = b.get_data()
    st = b.get_stride()

    def samp(x, y):
        i = y * st + x * 4
        return (d[i + 2] / 255, d[i + 1] / 255, d[i] / 255)

    ctop, cbot = samp(x0 + 300, 2), samp(x0 + cw - 60, 1077)
    c.set_source_rgb(*ctop)
    c.rectangle(0, 0, VW, 1000)
    c.fill()
    c.set_source_rgb(*cbot)
    c.rectangle(0, 1000, VW, VH)
    c.fill()
    s = VW / cw
    bh = 1080 * s
    y0 = 1010 - bh / 2
    c.save()
    c.translate(0, y0)
    c.scale(s, s)
    c.rectangle(0, 0, cw, 1080)
    c.clip()
    c.set_source_surface(b, -x0, 0)
    c.paint()
    c.restore()
    for a0, a1, col0, col1 in ((y0, y0 + 80, 1, 0), (y0 + bh - 80, y0 + bh, 0, 1)):
        g = cairo.LinearGradient(0, a0, 0, a1)
        top = a0 < 1000
        col = ctop if top else cbot
        g.add_color_stop_rgba(0, *col, col0)
        g.add_color_stop_rgba(1, *col, col1)
        c.set_source(g)
        c.rectangle(0, a0, VW, a1 - a0)
        c.fill()
    bold(c, "STILL", VW / 2, 300, 170, F.CREAM, "c", 14)
    bold(c, "TWO CUPS", VW / 2, 470, 170, F.YEL, "c", 14)
    bold(c, "2", 790, 1040, 360, F.CREAM, "c", 16)
    F.tag_draw(c, 60, 110, 56, "DAY 40")
    F.text(c, "Small Win Films", VW / 2, 1800, 50, F.CREAM, 0.8)
    out.write_to_png(path)


if __name__ == "__main__":
    thumbnail(sys.argv[1])
    cover(sys.argv[2])
