import cairo, math, sys
from film import *
import scenes as S
OLD = S.OLD
s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
c = cairo.Context(s)
c.save(); c.scale(1280 / 1920, 720 / 1080); room(c, 30, lamp=0.0, rain=0.5); c.restore()
tint(c, INK, 0.4)
c.save(); c.translate(270, 410); c.scale(2.75, 2.75)
c.set_source_rgb(*CARD); rr(c, -110, 80, 220, 140, 60); c.fill()
face(c, "cry", 0.9, 1.0, 1.0, 1.0, 0.6)
c.restore()
glow(c, 600, 700, 420, 0.35, GLOW)
phone_ui(c, 1005, 175, dict(mode="chat", old=OLD, draft="I miss you.", send=1.0), 0.1, 0.5)
c.select_font_face(FONT); c.set_font_size(124)
for i, (w, col) in enumerate((("UNSENT", CREAM),)):
    ex = c.text_extents(w)
    x, y = 468, 205
    c.move_to(x, y); c.text_path(w)
    c.set_source_rgb(0, 0, 0); c.set_line_width(18); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(*col); c.fill()
c.set_font_size(66)
c.move_to(474, 300); c.text_path("31 NIGHTS")
c.set_source_rgb(0, 0, 0); c.set_line_width(12); c.stroke_preserve(); c.set_source_rgb(*LAMP); c.fill()
s.write_to_png(sys.argv[1])
