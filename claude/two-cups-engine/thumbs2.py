import cairo, sys
import film as F
from thumb import bold, base

F.UI_ON = False
W, H = 1280, 720


def frame_surf(T):
    s = F.surf_new()
    c = cairo.Context(s)
    F.UI.clear()
    F.frame(c, T)
    return s


def paint_region(c, src, sx, sy, sw, sh, dx, dy, dw, dh):
    c.save()
    c.rectangle(dx, dy, dw, dh)
    c.clip()
    c.translate(dx, dy)
    c.scale(dw / sw, dh / sh)
    c.set_source_surface(src, -sx, -sy)
    c.paint()
    c.restore()


def shade(c, x0, x1, a0, a1):
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgba(0, 0.05, 0.06, 0.09, a0)
    g.add_color_stop_rgba(1, 0.05, 0.06, 0.09, a1)
    c.set_source(g)
    c.rectangle(0, 0, W, H)
    c.fill()


def v_her_cup(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    chair = frame_surf(27.0)
    paint_region(c, chair, 300, 124, 1620, 911, 360, 0, 1138, 640)
    paint_region(c, chair, 300, 124, 1620, 911, 330, 0, 1280, 720)
    face = base(1.55, 560, 430)
    c.save()
    c.rectangle(0, 0, 470, H)
    c.clip()
    paint_region(c, face, 120, 20, 1060, 1060, -225, 0, 720, 720)
    c.restore()
    c.set_source_rgb(*F.INK)
    c.rectangle(466, 0, 10, H)
    c.fill()
    bold(c, "HER CUP", 1205, 150, 124, F.YEL, "r", 12)
    out.write_to_png(path)


def v_every_morning(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    s = frame_surf(90.0)
    paint_region(c, s, 300, 175, 1600, 900, 0, 0, W, H)
    shade(c, 0, 700, 0.55, 0.0)
    bold(c, "EVERY", 50, 150, 120, F.CREAM, "l", 12)
    bold(c, "MORNING", 50, 275, 120, F.YEL, "l", 12)
    out.write_to_png(path)


def v_shes_gone(path):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(out)
    b = base(1.2, 820, 560)
    paint_region(c, b, 0, 0, 1920, 1080, -170, -40, W + 230, H + 130)
    shade(c, 600, W, 0.0, 0.65)
    bold(c, "SHE'S GONE.", 1205, 150, 96, F.CREAM, "r", 12)
    bold(c, "TWO CUPS.", 1205, 262, 96, F.YEL, "r", 12)
    out.write_to_png(path)


if __name__ == "__main__":
    d = sys.argv[1]
    v_her_cup(d + "/thumb-A-her-cup.png")
    v_every_morning(d + "/thumb-B-every-morning.png")
    v_shes_gone(d + "/thumb-C-shes-gone.png")
