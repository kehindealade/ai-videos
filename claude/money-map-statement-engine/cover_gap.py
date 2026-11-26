import cairo, math

W, H = 1080, 1920
DESK = (0.86, 0.87, 0.89)
SHEET = (1.0, 1.0, 0.99)
NAVY = (0.10, 0.17, 0.32)
GREEN = (0.10, 0.50, 0.30)
RED = (0.80, 0.18, 0.16)
MUTED = (0.45, 0.48, 0.55)
HL = (1.0, 0.90, 0.30)
GOLD = (0.78, 0.59, 0.18)
CREAM = (0.95, 0.93, 0.88)


def font(c, name, bold, size):
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def text(c, s, x, y, size, name, bold, col, align="l"):
    font(c, name, bold, size)
    w = c.text_extents(s).x_advance
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    c.set_source_rgb(*col)
    c.move_to(x, y)
    c.show_text(s)
    c.new_path()
    return w


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def mark(c, x, y, s):
    rrect(c, x, y, s, s, s * 0.22)
    c.set_source_rgb(*NAVY)
    c.fill()
    pts = [(0.2, 0.76), (0.2, 0.28), (0.5, 0.58), (0.8, 0.28), (0.8, 0.62)]
    c.set_line_width(s * 0.085)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgb(*GOLD)
    c.move_to(x + pts[0][0] * s, y + pts[0][1] * s)
    for px, py in pts[1:]:
        c.line_to(x + px * s, y + py * s)
    c.stroke()
    for px, py in pts[:-1]:
        c.arc(x + px * s, y + py * s, s * 0.055, 0, 7)
        c.set_source_rgb(*CREAM)
        c.fill()
    c.arc(x + 0.8 * s, y + 0.74 * s, s * 0.12, 0, 7)
    c.set_source_rgb(*GREEN)
    c.fill()


s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
c = cairo.Context(s)
c.set_source_rgb(*DESK)
c.paint()

text(c, "YOUR BANK PAYS YOU", W / 2, 300, 74, "Poppins", True, NAVY, "c")

c.save()
c.translate(90, 400)
c.rotate(-0.03)
rrect(c, 14, 14, 900, 900, 14)
c.set_source_rgba(0, 0, 0, 0.18)
c.fill()
rrect(c, 0, 0, 900, 900, 14)
c.set_source_rgb(*SHEET)
c.fill()
mark(c, 40, 40, 84)
text(c, "YOUR SAVINGS · 1 YEAR", 146, 100, 38, "Poppins", True, NAVY)
c.set_source_rgb(*NAVY)
c.rectangle(40, 160, 820, 6)
c.fill()
text(c, "DEPOSIT", 46, 270, 48, "DejaVu Sans Mono", False, NAVY)
text(c, "$1,000", 856, 270, 58, "DejaVu Sans Mono", True, NAVY, "r")
text(c, "INTEREST", 46, 430, 48, "DejaVu Sans Mono", False, NAVY)
c.set_source_rgba(*HL, 0.85)
c.rectangle(480, 340, 390, 120)
c.fill()
text(c, "$3.80", 856, 440, 112, "DejaVu Sans Mono", True, GREEN, "r")
c.set_source_rgb(*MUTED)
c.set_dash([6, 10])
c.set_line_width(4)
c.move_to(40, 520)
c.line_to(860, 520)
c.stroke()
c.set_dash([])
text(c, "BANK CHARGES", 46, 660, 48, "DejaVu Sans Mono", False, NAVY)
text(c, "$210", 856, 690, 150, "DejaVu Sans Mono", True, RED, "r")
text(c, "same $1,000 on a credit card", 46, 820, 40, "Poppins", False, MUTED)
c.restore()

text(c, "SAME MONEY.", W / 2, 1520, 128, "Poppins", True, NAVY, "c")
pw, ph = 600, 120
rrect(c, W / 2 - pw / 2, 1590, pw, ph, ph / 2)
c.set_source_rgb(*RED)
c.fill()
text(c, "WHO GETS PAID?", W / 2, 1672, 58, "Poppins", True, SHEET, "c")
s.write_to_png("/home/claude/yts/cover-how-banks-make-money-from-savings-short.png")
