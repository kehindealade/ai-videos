import cairo, reel as R
F = R.F
s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1080, 1920)
c = cairo.Context(s)
R.CTX["hook"] = True
R.CTX["t"] = 9.0
R.S.vframe(c, "s1", 4.2 + 1.6, 230)
c.set_source_rgb(*F.FLOOR)
c.rectangle(0, 1400, 1080, 520)
c.fill()
F.text(c, "He tried 4 things", 540, 1500, 92, F.INK)
F.text(c, "to fix his bad day", 540, 1615, 92, F.CORAL)
s.write_to_png("reel-cover-bad-day-1080x1920.png")
