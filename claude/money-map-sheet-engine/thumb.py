import cairo, math
from ss_common import *

TW, TH = 1280, 720


def thumb(path, variant="A"):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, TW, TH)
    c = cairo.Context(s)
    c.set_source_rgb(*PAPER)
    c.paint()
    c.set_source_rgb(*GRID)
    c.set_line_width(1.5)
    for x in range(0, TW, 110):
        c.move_to(x + 0.5, 0)
        c.line_to(x + 0.5, TH)
    for y in range(0, TH, 46):
        c.move_to(0, y + 0.5)
        c.line_to(TW, y + 0.5)
    c.stroke()
    box(c, 0, 0, TW, 18, NAVY)
    for i, (pct, col, fc, y) in enumerate((("90¢", TEAL, TEAL_L, 110), ("15¢", CORAL, CORAL_L, 390))):
        shadow(c, 60, y, 560, 230, 10, 0.25, 10)
        box(c, 60, y, 200, 230, WHITE, 1, 0, GRID, 3)
        txt(c, "$1", 160, y + 150, 110, INK, HEAD, "c")
        box(c, 260, y, 360, 230, fc, 1, 0, GRID, 3)
        txt(c, pct, 440, y + 165, 150, col, HEAD, "c")
        if i == 0:
            rr(c, 257, y - 3, 366, 236, 2)
            c.set_source_rgb(*GOLD)
            c.set_line_width(8)
            c.stroke()
    circle(c, 700, 360, 70, GOLD)
    txt(c, "6x", 700, 384, 64, NAVY, HEAD, "c")
    box(c, 790, 70, 450, 330, NAVY, 1, 18)
    txt(c, "SAME", 1015, 190, 110, WHITE, HEAD, "c")
    txt(c, "DOLLAR?", 1015, 320, fit(c, "DOLLAR?", 110, 400, HEAD), GOLD, HEAD, "c")
    txt(c, "SOCIAL SECURITY", 1015, 470, fit(c, "SOCIAL SECURITY", 46, 420, HEAD), NAVY, HEAD, "c")
    txt(c, "=FORMULA( ? )", 1015, 535, 42, SOFT, MONO, "c")
    s.write_to_png(path)


if __name__ == "__main__":
    thumb("thumb_long.png")
