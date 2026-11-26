import cairo, math, sys
import engine as E
W, H = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
c = cairo.Context(s)
c.save(); c.scale(W / 1920, H / 1080); E.background(c); c.restore()
c.set_source_rgb(*E.RED); c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND)
c.move_to(-40, 150); c.line_to(250, 220); c.line_to(520, 640); c.line_to(700, 760); c.stroke()
E.station(c, 250, 220, 30, E.RED, E.WHITE, 14)
c.save(); c.translate(330, 420); c.rotate(-0.25)
E.coin(c, 0, 0, 205, E.ORANGE)
c.set_source_rgb(0.75,0.42,0.05); c.set_line_width(9); c.set_line_join(cairo.LINE_JOIN_MITER)
c.move_to(-30, -210); c.line_to(10, -90); c.line_to(-40, 10); c.line_to(30, 110); c.line_to(-10, 210); c.stroke()
c.restore()
E.card(c, 650, 70, 590, 380, E.BOARD)
E.txt(c, "SINCE OCT 2025", 690, 150, 54, (0.65, 0.7, 0.78))
E.txt(c, "−$1.2 TRILLION", 690, 278, 98, E.AMBERT)
E.stamp(c, 945, 385, "WHO GOT IT?", E.RED, 1, 74, -0.06)
s.write_to_png(sys.argv[1])
