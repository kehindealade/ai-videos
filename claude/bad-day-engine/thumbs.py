import cairo, math, sys
import fp as F

W, H = 1280, 720


def big(c, s, x, y, size, col, align="l", stroke=14, font="Rounded Mplus 1c ExtraBold"):
    c.select_font_face(font)
    c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        x = x - e.width / 2 - e.x_bearing
    elif align == "r":
        x = x - e.width - e.x_bearing
    else:
        x = x - e.x_bearing
    c.save()
    c.move_to(x + 5, y + 7)
    c.text_path(s)
    c.set_source_rgba(0, 0, 0, 0.45)
    c.set_line_width(stroke)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke_preserve()
    c.fill()
    c.move_to(x, y)
    c.text_path(s)
    c.set_source_rgb(*F.INK)
    c.stroke_preserve()
    c.set_source_rgb(*col)
    c.fill()
    c.restore()
    return e.width


def vignette(c, a=0.55):
    g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 820)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.03, 0.06, 0.09, a)
    c.set_source(g)
    c.paint()


def cross(c, x, y, r, lw=18):
    c.save()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for col, w in ((F.INK, lw + 10), (F.CORAL, lw)):
        c.set_source_rgb(*col)
        c.set_line_width(w)
        c.move_to(x - r, y - r)
        c.line_to(x + r, y + r)
        c.move_to(x + r, y - r)
        c.line_to(x - r, y + r)
        c.stroke()
    c.restore()


def v_boss(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    c.save()
    c.scale(0.95, 0.95)
    c.translate(-380, -330)
    F.workshop(c, 8.0)
    c.restore()
    c.set_source_rgba(*F.CORAL, 0.18)
    c.paint()
    vignette(c, 0.6)
    F.figure(c, 330, 1010, 1.75, F.BOSS, face=1, mouth="open", point=(118, -330), lean=0.12)
    k = 1.0
    F.burst(c, 640, 250, 95)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(3):
        c.set_source_rgba(*F.CORAL, 1 - i * 0.25)
        c.set_line_width(12)
        c.move_to(560 + i * 18, 360 + i * 34)
        c.line_to(660 + i * 18, 360 + i * 34)
        c.stroke()
    c.save()
    c.translate(990, 1150)
    c.scale(2.15, 2.15)
    F.hero(c, x=0, y=0, mood="shock", face=-1, lean=0.06, shadow=False)
    c.restore()
    c.set_source_rgb(*F.INK)
    F.rrect(c, 36, 30, 250, 74, 37)
    c.fill()
    F.text(c, "8:00 AM", 161, 84, 50, F.CREAM)
    big(c, "HIS DAY,", 40, 600, 96, F.CREAM)
    big(c, "RUINED", 40, 690, 118, F.CORAL)
    out.write_to_png(path)


def card(c, x, y, w, h):
    c.set_source_rgba(1, 1, 1, 0.10)
    F.rrect(c, x, y, w, h, 26)
    c.fill()


def v_tried(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgb(0, *F.NSKY)
    g.add_color_stop_rgb(1, *F.NIGHT)
    c.set_source(g)
    c.paint()
    F.glow(c, 1000, 330, 520, 0.28)
    cw, ch = 250, 190
    cells = [(40, 180), (310, 180), (40, 390), (310, 390)]
    for x, y in cells:
        card(c, x, y, cw, ch)
    x, y = cells[0]
    c.save()
    c.translate(x + cw / 2, y + 125)
    c.scale(2.3, 2.3)
    F.plate(c, 0, 0)
    c.restore()
    x, y = cells[1]
    F.ball(c, x + cw / 2, y + ch / 2 + 4, 0.6, r=70)
    x, y = cells[2]
    F.note(c, x + cw / 2 - 34, y + 150, 3.0, 1.0, F.AMBER)
    x, y = cells[3]
    c.save()
    s = 0.3
    c.translate(x + cw / 2, y + ch - 12 - 860 * s)
    c.scale(s, s)
    F.lamp_post(c, 0, True)
    c.restore()
    c.save()
    c.translate(x + cw / 2 + 40, y + ch - 14)
    c.scale(0.3, 0.3)
    F.hero(c, x=0, y=0, mood="hurt", face=-1, walk=0.9, hang=1.0, shadow=False)
    c.restore()
    for x, y in cells:
        bx, by = x + cw - 34, y + 34
        c.set_source_rgb(*F.INK)
        c.arc(bx, by, 30, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*F.CORAL)
        c.arc(bx, by, 25, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*F.CREAM)
        c.set_line_width(7)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(bx - 10, by - 10)
        c.line_to(bx + 10, by + 10)
        c.move_to(bx + 10, by - 10)
        c.line_to(bx - 10, by + 10)
        c.stroke()
    c.save()
    c.translate(1000, 1180)
    c.scale(2.35, 2.35)
    F.hero(c, x=0, y=0, mood="hurt", face=-1, look=1.0, hang=1.0, lean=0.08, shadow=False)
    c.restore()
    vignette(c, 0.45)
    big(c, "HE TRIED 4 THINGS", 40, 130, 82, F.CREAM)
    big(c, "NONE WORKED", 40, 690, 100, F.CORAL)
    out.write_to_png(path)


def v_night(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    cam = 1800
    c.save()
    c.scale(0.95, 0.95)
    c.translate(-40, -240)
    F.street(c, cam, F.NSKY, 1.0, lit=1.0)
    F.tint(c, F.NIGHT, 0.45)
    F.glow(c, 2360 - cam, 360, 520, 0.55)
    c.save()
    c.rectangle(0, F.GY, F.W, 220)
    c.clip()
    g = cairo.RadialGradient(2360 - cam, F.GY + 30, 0, 2360 - cam, F.GY + 30, 380)
    g.add_color_stop_rgba(0, 1.0, 0.80, 0.45, 0.35)
    g.add_color_stop_rgba(1, 1.0, 0.80, 0.45, 0)
    c.set_source(g)
    c.paint()
    c.restore()
    c.restore()
    c.set_source_rgb(0.97, 0.95, 0.85)
    c.arc(1130, 110, 50, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgb(*F.mix(F.NSKY, F.NIGHT, 0.5))
    c.arc(1153, 96, 45, 0, 2 * math.pi)
    c.fill()
    c.save()
    c.translate(330, 1080)
    c.scale(1.9, 1.9)
    F.hero(c, x=0, y=0, mood="hurt", face=1, walk=0.9, hang=1.0, look=1.0, lean=0.07, shadow=False)
    c.restore()
    vignette(c, 0.55)
    big(c, "STILL", 1240, 300, 120, F.CREAM, "r")
    big(c, "NOT OKAY", 1240, 430, 120, F.AMBER, "r")
    out.write_to_png(path)


if __name__ == "__main__":
    d = sys.argv[1]
    v_boss(d + "/thumb-A-boss.png")
    v_tried(d + "/thumb-B-none-worked.png")
    v_night(d + "/thumb-C-still-not-okay.png")
