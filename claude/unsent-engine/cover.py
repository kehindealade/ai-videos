import cairo, sys
from film import *
import scenes as S
def cover(path, l1, l2, band=False, sz=110):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920); c = cairo.Context(s)
    c.save(); c.translate(540, 900); c.scale(1.6, 1.6); c.translate(-1000, -560); room(c, 30, lamp=0.0, rain=0.6); c.restore()
    tint(c, INK, 0.35)
    c.save(); c.translate(540, 560); c.scale(3.1, 3.1)
    c.set_source_rgb(*CARD); rr(c, -95, 70, 190, 90, 40); c.fill()
    face(c, "cry", 0.9, 1.0, 0.6, 1.0, 0.6); c.restore()
    glow(c, 540, 1000, 600, 0.3, GLOW)
    y0 = 1210 if band else 1060
    if band:
        c.set_source_rgb(*INK); c.rectangle(0, 1090, 1080, 830); c.fill()
    c.select_font_face(FONT)
    for i, (w, col, sz) in enumerate(((l1, CREAM, sz), (l2, LAMP, sz))):
        c.set_font_size(sz); ex = c.text_extents(w)
        c.move_to(540 - ex.width / 2 - ex.x_bearing, y0 + i * 130); c.text_path(w)
        c.set_source_rgb(0, 0, 0); c.set_line_width(16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*col); c.fill()
    s.write_to_png(path)
cover("short-cover-heartbreak-1080x1920.png", "31 TEXTS.", "0 SENT.")
cover("reel-cover-heartbreak-1080x1920.png", "She wrote 31 texts.", "She sent none.", True, 88)
