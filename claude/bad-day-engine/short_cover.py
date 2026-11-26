import cairo, math, sys
import fp as F
from thumbs import big, vignette

W, H = 1080, 1920


def cover(path):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.save()
    c.scale(1.9, 1.9)
    c.translate(-520, -160)
    F.workshop(c, 8.0)
    c.restore()
    c.set_source_rgba(*F.CORAL, 0.16)
    c.paint()
    g = cairo.RadialGradient(W / 2, H * 0.45, 300, W / 2, H * 0.45, 1200)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.03, 0.06, 0.09, 0.65)
    c.set_source(g)
    c.paint()
    F.figure(c, 260, 720, 1.4, F.BOSS, face=1, mouth="open", point=(150, -380), lean=0.14)
    F.burst(c, 700, 250, 105)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(3):
        c.set_source_rgba(*F.CORAL, 1 - i * 0.25)
        c.set_line_width(14)
        c.move_to(620 + i * 22, 390 + i * 40)
        c.line_to(750 + i * 22, 390 + i * 40)
        c.stroke()
    c.save()
    c.translate(540, 2470)
    c.scale(3.2, 3.2)
    F.hero(c, x=0, y=0, mood="shock", face=-1, lean=0.05, shadow=False)
    c.restore()
    big(c, "RUINED", 540, 880, 190, F.CORAL, "c", 22)
    big(c, "BEFORE 9 AM", 540, 985, 88, F.CREAM, "c", 16)
    s.write_to_png(path)


cover(sys.argv[1])
