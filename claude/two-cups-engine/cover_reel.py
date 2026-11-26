import cairo, sys
import reel as R
F = R.F

s = cairo.ImageSurface(cairo.FORMAT_RGB24, R.VW, R.VH)
c = cairo.Context(s)
R.reset()
F.scene_frame(R.sc, "cold", 5.0)
R.set_day(40, 0.0)
R.bg(c)
R.calendar(c, 0.0)
R.tally(c, 0.0, 0.6)
R.frame_scene(c, 330)


def line(txt, y, size, col):
    c.select_font_face(F.FONT)
    c.set_font_size(size)
    e = c.text_extents(txt)
    c.move_to(R.VW / 2 - e.width / 2 - e.x_bearing, y)
    c.text_path(txt)
    c.set_source_rgb(*R.INKD)
    c.set_line_width(14)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke_preserve()
    c.set_source_rgb(*col)
    c.fill()


line("2 CUPS.", 1660, 130, F.YEL)
line("HE LIVES ALONE.", 1800, 96, F.CREAM)
s.write_to_png(sys.argv[1] if len(sys.argv) > 1 else "reel-cover-two-cups-1080x1920.png")
