import sys, math
import cairo
sys.path.insert(0, '.')
from iou_common import *


def stamp_big(c, x, y, s, label, ang=-0.2):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    font(c, LAB)
    c.set_font_size(110 * s)
    ext = c.text_extents(label)
    w, h = ext.width + 50 * s, 150 * s
    c.set_source_rgba(0.9, 0.18, 0.15, 1)
    c.set_line_width(10 * s)
    rr(c, -w / 2, -h / 2, w, h, 12 * s)
    c.stroke()
    c.set_source_rgba(0.9, 0.18, 0.15, 1)
    c.move_to(-ext.width / 2 - ext.x_bearing, h * 0.27)
    c.show_text(label)
    c.restore()


def thumb(out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    c = cairo.Context(s)
    draw_wall(c, 1280, 720)
    cert(c, 345, 400, 1.0, "CHINA", "$564 BILLION", -0.06, 1.0, 7001)
    stamp_big(c, 345, 400, 0.95, "NOT #1")
    txt(c, "WHO OWNS", 905, 190, 120, WHITE, LAB, "c", 1.0, stroke=(0, 0, 0), sw=14)
    txt(c, "THE $40T", 905, 330, 150, AMBER, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "DEBT?", 905, 470, 150, AMBER, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "IT'S NOT CHINA", 905, 590, 84, (0.95, 0.35, 0.3), LAB, "c", 1.0, stroke=(0, 0, 0), sw=12)
    s.write_to_png("thumb-who-owns-national-debt-1280x720.png")


def cover_a(out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920)
    c = cairo.Context(s)
    draw_wall(c, 1080, 1920)
    txt(c, "BIGGEST", 540, 440, 150, WHITE, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "FOREIGN LENDER", 540, 590, 130, AMBER, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "TO AMERICA?", 540, 730, 130, AMBER, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    cert(c, 540, 1060, 1.3, "CHINA", "$564 BILLION", -0.05, 1.0, 7002)
    stamp_big(c, 540, 1060, 1.3, "NOT #1")
    s.write_to_png(out)


def cover_b(out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920)
    c = cairo.Context(s)
    draw_wall(c, 1080, 1920)
    txt(c, "SOCIAL SECURITY'S", 540, 420, 120, WHITE, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "SAVINGS ARE", 540, 560, 140, WHITE, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    txt(c, "GOVERNMENT IOUs", 540, 720, 140, AMBER, LAB, "c", 1.0, stroke=(0, 0, 0), sw=16)
    cert(c, 540, 1080, 1.3, "SOCIAL SECURITY", "$2.3 TRILLION", 0.05, 1.0, 7003, col=TRUST)
    s.write_to_png(out)


thumb(0)
cover_a("short-cover-not-china-1080x1920.png")
cover_b("short-cover-social-security-1080x1920.png")
