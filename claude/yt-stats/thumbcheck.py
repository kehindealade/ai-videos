import cairo, sys, os

ZONES_LONG = [(1020, 610, 260, 110, (1, 0, 0, 0.45)), (1210, 0, 70, 70, (1, 0.5, 0, 0.45)), (0, 708, 1280, 12, (1, 0, 0, 0.45))]
MARGIN = 40


def check(path):
    s = cairo.ImageSurface.create_from_png(path)
    W, H = s.get_width(), s.get_height()
    base = os.path.splitext(path)[0]
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    c.set_source_surface(s, 0, 0)
    c.paint()
    if W > H:
        k = W / 1280
        for x, y, w, h, col in ZONES_LONG:
            c.set_source_rgba(*col)
            c.rectangle(x * k, y * k, w * k, h * k)
            c.fill()
    else:
        k = W / 1080
        c.set_source_rgba(1, 0, 0, 0.4)
        c.rectangle(0, H * 0.75, W, H * 0.25)
        c.fill()
        c.rectangle(W - 160 * k, H * 0.45, 160 * k, H * 0.3)
        c.fill()
    c.set_source_rgba(0, 1, 1, 0.8)
    c.set_line_width(2)
    c.rectangle(MARGIN * k, MARGIN * k, W - 2 * MARGIN * k, H - 2 * MARGIN * k)
    c.stroke()
    out.write_to_png(base + "-zones.png")
    sw = 320
    sh = int(H * sw / W)
    small = cairo.ImageSurface(cairo.FORMAT_RGB24, sw, sh)
    c = cairo.Context(small)
    c.scale(sw / W, sh / H)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint()
    small.write_to_png(base + "-320.png")
    print(base + "-zones.png", base + "-320.png")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        check(p)
