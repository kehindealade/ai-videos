import cairo, math
from sd import *
import short as SH


def thumb(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    c = cairo.Context(surf)
    c.scale(1280 / W, 720 / H)
    vgrad(c, 0, 0, W, H, TEAL, TEAL_D)
    city_window(c, 40, 40, 520, 380, 3.0)
    c.save()
    c.translate(560, 640)
    c.scale(3.5, 3.5)
    c.set_source_rgb(*RUST)
    c.new_path()
    c.move_to(-170, 340)
    c.curve_to(-150, 140, -100, 92, -60, 82)
    c.line_to(60, 82)
    c.curve_to(100, 92, 150, 140, 170, 340)
    c.close_path()
    c.fill()
    c.set_source_rgb(*CREAM)
    c.new_path()
    c.move_to(-34, 80)
    c.line_to(0, 130)
    c.line_to(34, 80)
    c.close_path()
    c.fill()
    face(c, SON_SKIN, "son", "worry", 0.9, 1.0, 0.0, 0.0, 0.0, -0.3)
    c.restore()
    glow(c, 1300, 760, 700, 0.45, GLOW)
    smartphone(c, 1360, 690, 0.95, "incoming", 1.0, 0.12, 0.3)
    for i in range(3):
        c.set_source_rgba(*GLOW, 0.5 - 0.13 * i)
        c.set_line_width(12)
        c.arc(1360, 690, 340 + 50 * i, -0.9, -0.35)
        c.stroke()
        c.arc(1360, 690, 340 + 50 * i, math.pi + 0.35, math.pi + 0.9)
        c.stroke()
    c.select_font_face(FONT)
    c.set_font_size(150)
    tx = 1080
    for i, (s, col) in enumerate((("HE LET", CREAM), ("IT RING.", MUST))):
        y = 190 + i * 160
        c.move_to(tx, y)
        c.text_path(s)
        c.set_source_rgba(0, 0, 0, 0.8)
        c.set_line_width(22)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgb(*col)
        c.fill()
    surf.write_to_png(path)


def cover(path):
    VW, VH = 1080, 1920
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    SH.panel(c, 0, SH.PH, lambda cc: gran_close(cc, 1.0, "worry", -0.3, ring=1.0, dusk=0.3), 900)
    SH.panel(c, SH.DIV1, SH.BOT, lambda cc: table_close(cc, 0.4, "incoming", 1.0, py=330), 700)
    SH.band(c, None, 0.0, nx=780)
    SH.hook(c, ["EVERY SUNDAY AT 6.", "HE LET IT RING."], 1.0, 600, 76)
    surf.write_to_png(path)


if __name__ == "__main__":
    thumb("thumb.png")
    cover("cover.png")
