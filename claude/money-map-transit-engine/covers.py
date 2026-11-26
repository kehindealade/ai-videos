import cairo
import shorts as SH, engine as E
from engine import txt, stamp
def mk(path, which):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920); c = cairo.Context(s)
    SH.bg(c)
    if which == 1:
        SH.coins_v(c, 0, 1)
        txt(c, "1 COIN SOLD.", 540, 1210, 120, E.INK, align="c")
        txt(c, "$500 GONE.", 540, 1340, 120, E.RED, align="c")
    else:
        txt(c, "$1,000", 540, 620, 200, E.GREEN, align="c")
        c.set_source_rgb(*E.INK); c.set_line_width(14)
        c.move_to(540, 690); c.line_to(540, 820); c.move_to(490, 770); c.line_to(540, 830); c.line_to(590, 770); c.stroke()
        txt(c, "$0", 540, 1060, 220, E.RED, align="c")
        stamp(c, 540, 1240, "IN 10 SECONDS", E.RED, 1, 80, -0.04)
    s.write_to_png(path)
mk("short-cover-500-never-existed-1080x1920.png", 1)
mk("short-cover-liquidated-1080x1920.png", 2)
