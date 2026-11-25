import cairo
from xm import *
import xm, shorts as SH, film as F

def outlined(c, s, x, y, size, col, align="c"):
    text(c, s, x, y, size, col, 1.0, align, FONT, outline=size * 0.16)

def thumb(path):
    big = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    cc = cairo.Context(big)
    xm.cabin(cc, 0.8, look=1.0, hand_k=0.18, mood="sad")
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    c = cairo.Context(out)
    c.scale(1280 / W, 720 / H)
    c.set_source_surface(big, 0, 0)
    c.paint()
    c.identity_matrix()
    g = cairo.LinearGradient(0, 0, 0, 260)
    g.add_color_stop_rgba(0, 0.02, 0.03, 0.08, 0.75)
    g.add_color_stop_rgba(1, 0.02, 0.03, 0.08, 0)
    c.set_source(g)
    c.rectangle(0, 0, 1280, 260)
    c.fill()
    outlined(c, "3 CHRISTMASES.", 800, 104, 80, GOLD)
    outlined(c, "NEVER KNOCKED.", 800, 194, 80, CREAM)
    out.write_to_png(path)

def cover(path, which):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920)
    c = cairo.Context(surf)
    if which == 1:
        SH.place(c, 0, 720, 1.0, custom=lambda cc: xm.cabin(cc, 0.8, look=1.0, hand_k=0.18, mood="sad"))
        l1, l2 = "3 YEARS.", "ONE DOOR."
    elif which == 2:
        SH.place(c, 0, 1400, 1.0, custom=lambda cc: xm.apartment(cc, 60, 3, maya_x=520))
        l1, l2 = "3 GIFTS.", "NEVER GIVEN."
    else:
        SH.place(c, 119.0, 1100, 1.0)
        l1, l2 = "YEAR 4.", "SHE KNOCKED."
    g = cairo.LinearGradient(0, 120, 0, 760)
    g.add_color_stop_rgba(0, 0.02, 0.03, 0.08, 0.7)
    g.add_color_stop_rgba(1, 0.02, 0.03, 0.08, 0)
    c.set_source(g)
    c.rectangle(0, 120, 1080, 640)
    c.fill()
    outlined(c, l1, 500, 420, 150, GOLD)
    outlined(c, l2, 500, 590, 150 if len(l2) < 11 else 120, CREAM)
    surf.write_to_png(path)

if __name__ == "__main__":
    thumb("thumb-christmas-animated-short-film.png")
    for i in (1, 2, 3):
        cover("cover-short-%d.png" % i, i)
    print("ok")
