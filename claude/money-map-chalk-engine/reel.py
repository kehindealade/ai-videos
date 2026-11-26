import cairo, math, random, json, os, sys, subprocess
import numpy as np, soundfile as sf

VW, VH, FPS = 1080, 1920, 30
HEAD = "Permanent Marker"
BODY = "Kalam"
BOARD = (0.13, 0.21, 0.18)
CHALK = (0.95, 0.94, 0.89)
YEL = (0.98, 0.86, 0.45)
PINK = (0.96, 0.62, 0.66)
BLUE = (0.55, 0.78, 0.94)
GREEN = (0.56, 0.90, 0.56)
WOOD = (0.45, 0.30, 0.18)
GOLD = (0.89, 0.70, 0.25)

VOICE, SPEED = "bf_isabella", 0.96
LINES = [
    ("hook", "You pay sixteen dollars for a meal. The restaurant keeps about eighty cents."),
    ("empty", "So where does the other fifteen dollars and twenty cents go?"),
    ("food", "About five twenty-eight goes on the food itself."),
    ("labor", "Another five twenty-eight pays the people who cook it and serve it."),
    ("other", "Four sixty-four covers rent, power, repairs, supplies and card fees."),
    ("profit", "What's left is about eighty cents. Five cents on every dollar, before tax."),
    ("costs", "And that was before prices jumped. Restaurant costs are up thirty-six percent since 2019."),
    ("menu", "Menu prices rose about the same, so most of that bigger bill just covers bigger costs."),
    ("loss", "And about four in ten restaurant owners say they didn't make a profit at all in 2025."),
    ("close", "So most of what you pay never reaches the owner. Follow the money."),
]
SL = [("FOOD", 0.33, YEL, "$5.28"), ("STAFF", 0.33, PINK, "$5.28"), ("RENT, POWER, FEES", 0.29, BLUE, "$4.64"), ("PROFIT", 0.05, GREEN, "80¢")]
START = 0.05 * math.pi
ORDER = ["hook", "empty", "food", "labor", "other", "profit", "costs", "menu", "loss", "close"]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return x * x * (3 - 2 * x)


def txt(c, s, x, y, size, col, font=HEAD, align="c", a=1.0):
    c.select_font_face(font)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.width / 2 + ex.x_bearing
    elif align == "r":
        x -= ex.width + ex.x_bearing
    c.move_to(x, y)
    c.set_source_rgba(*col, a)
    c.show_text(s)
    c.new_path()
    return ex.width


random.seed(2)
SMUDGE = [(random.uniform(0, VW), random.uniform(0, VH), random.uniform(60, 220), random.uniform(0.02, 0.05)) for _ in range(40)]


_BOARD = None


def board(c):
    global _BOARD
    if _BOARD is None:
        _BOARD = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
        board_raw(cairo.Context(_BOARD))
    c.set_source_surface(_BOARD, 0, 0)
    c.paint()


def board_raw(c):
    c.set_source_rgb(*BOARD)
    c.paint()
    for x, y, r, a in SMUDGE:
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        g.add_color_stop_rgba(0, 1, 1, 1, a)
        g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g)
        c.paint()
    txt(c, "MONEY MAP", 90, 130, 44, GOLD, align="l")
    txt(c, "· TODAY'S BILL", 360, 130, 36, CHALK, BODY, "l", 0.7)


def chalk_line(c, pts, col, w=8, k=1.0):
    c.set_source_rgba(*col, 0.92)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    n = max(2, int(len(pts) * k))
    c.move_to(*pts[0])
    for p in pts[1:n]:
        c.line_to(*p)
    c.stroke()


def plate(c, cx, cy, r, upto, t, step_t, pop=0.0):
    pts = [(cx + (r + 26) * math.cos(a), cy + (r + 26) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 120)]
    chalk_line(c, pts, CHALK, 6, 1.0)
    a0 = START
    for i, (lab, share, col, amt) in enumerate(SL):
        a1 = a0 + share * 2 * math.pi
        if i < upto or (i == upto and step_t is not None):
            k = 1.0 if i < upto else e(step_t, 0.1, 0.8)
            mid = (a0 + a1) / 2
            off = 60 * pop if lab == "PROFIT" else 0
            ox, oy = off * math.cos(mid), off * math.sin(mid)
            c.move_to(cx + ox, cy + oy)
            c.arc(cx + ox, cy + oy, r, a0, a0 + (a1 - a0) * k)
            c.close_path()
            c.set_source_rgba(*col, 0.85)
            c.fill_preserve()
            c.set_source_rgba(*BOARD, 1)
            c.set_line_width(6)
            c.stroke()
            if k > 0.95:
                rr_ = r * (0.62 if lab != "PROFIT" else 1.32)
                lx, ly = cx + ox + rr_ * math.cos(mid), cy + oy + rr_ * math.sin(mid)
                txt(c, amt, lx, ly + 18, 64 if lab != "PROFIT" else 70, BOARD if lab != "PROFIT" else GREEN)
        a0 = a1


def legend(c, upto):
    y = 1075
    for i, (lab, share, col, amt) in enumerate(SL[:upto]):
        c.set_source_rgba(*col, 0.9)
        c.arc(140, y - 16 + i * 58, 16, 0, 2 * math.pi)
        c.fill()
        txt(c, lab, 180, y + i * 58, 42, CHALK, BODY, "l")
        txt(c, "%d¢ of $1" % round(share * 100), VW - 110, y + i * 74, 46, col, BODY, "r")


def caption(c, s, k):
    c.select_font_face(BODY)
    c.set_font_size(58)
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.text_extents(trial).x_advance > 900 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    y0 = 1420 - (len(lines) - 1) * 34
    for i, ln in enumerate(lines):
        ex = c.text_extents(ln)
        c.move_to(VW / 2 - ex.width / 2 - ex.x_bearing, y0 + i * 70)
        c.text_path(ln)
        c.set_source_rgba(0, 0, 0, 0.55 * k)
        c.set_line_width(10)
        c.stroke_preserve()
        c.set_source_rgba(*CHALK, k)
        c.fill()


def bars(c, t, which):
    labs = [("COSTS", "+36%", "2019 TO 2026", PINK), ("MENU PRICES", "+36%", "FEB 2020 TO MAY 2026", YEL)]
    for i, (a, b, d, col) in enumerate(labs):
        if i > which:
            break
        k = e(t, 0.2, 1.2) if i == which else 1
        x = 170 + i * 420
        c.set_source_rgba(*CHALK, 0.5)
        c.rectangle(x, 950, 300, 8)
        c.fill()
        c.set_source_rgba(*col, 0.25)
        c.rectangle(x + 30, 950 - 380, 240, 380)
        c.fill()
        c.set_source_rgba(*col, 0.9)
        c.rectangle(x + 30, 950 - 380 - 140 * k, 240, 140 * k)
        c.fill()
        txt(c, b, x + 150, 520 - 140 * k, 92, col)
        txt(c, a, x + 150, 1030, 50, CHALK)
        txt(c, d, x + 150, 1090, 32, CHALK, BODY, a=0.7)
    if which == 1:
        txt(c, "SAME RISE. SAME TINY SLICE.", VW / 2, 250, 62, CHALK, a=e(t, 1.4, 1.9))


def people(c, t):
    for i in range(10):
        x = 150 + (i % 5) * 195
        y = 620 + (i // 5) * 330
        lost = i < 4
        col = PINK if lost else CHALK
        c.set_source_rgba(*col, 0.9)
        c.set_line_width(9)
        c.arc(x, y - 110, 38, 0, 2 * math.pi)
        c.stroke()
        c.move_to(x, y - 70)
        c.line_to(x, y + 30)
        c.move_to(x - 55, y - 30)
        c.line_to(x + 55, y - 30)
        c.move_to(x, y + 30)
        c.line_to(x - 40, y + 110)
        c.move_to(x, y + 30)
        c.line_to(x + 40, y + 110)
        c.stroke()
        if lost and t > 0.4 + i * 0.25:
            c.set_source_rgba(*PINK, 1)
            c.set_line_width(12)
            c.move_to(x - 70, y - 160)
            c.line_to(x + 70, y + 130)
            c.stroke()
    txt(c, "4 IN 10: NO PROFIT IN 2025", VW / 2, 380, 66, PINK, a=e(t, 1.2, 1.7))


def logo(c, x, y, s, a):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(*GOLD, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    c.arc(60, 60, 13, 0, 2 * math.pi)
    c.set_source_rgba(0.12, 0.64, 0.36, a)
    c.fill()
    c.restore()


def draw(c, tl, T):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0, T - t0)
    sc, line = LINES[i]
    board(c)
    cx, cy, r = VW / 2, 690, 280
    if sc == "hook":
        txt(c, "MEAL .............. $16", VW / 2, 300, 72, CHALK)
        plate(c, cx, cy, r, 4, t, None, 1.0)
        txt(c, "THEY KEEP 80¢", VW / 2, 1220, 96, GREEN)
    elif sc == "empty":
        txt(c, "$15.20 GOES WHERE?", VW / 2, 300, 76, CHALK)
        plate(c, cx, cy, r, 0, t, None)
    elif sc in ("food", "labor", "other", "profit"):
        n = ORDER.index(sc) - 2
        txt(c, "YOUR $16 MEAL", VW / 2, 300, 76, CHALK)
        plate(c, cx, cy, r, n, t, t, e(t, 0.6, 1.2) if sc == "profit" else 0)
        legend(c, n + 1 if t > 0.8 else n)
    elif sc == "costs":
        bars(c, t, 0)
    elif sc == "menu":
        bars(c, t, 1)
    elif sc == "loss":
        people(c, t)
    elif sc == "close":
        txt(c, "MOST OF YOUR BILL", VW / 2, 520, 84, CHALK, a=e(t, 0, 0.5))
        txt(c, "NEVER REACHES", VW / 2, 640, 84, CHALK, a=e(t, 0.3, 0.8))
        txt(c, "THE OWNER.", VW / 2, 760, 100, GREEN, a=e(t, 0.6, 1.1))
        logo(c, VW / 2 - 90, 900, 3.0, e(t, 2.0, 2.6))
        txt(c, "FOLLOW THE MONEY.", VW / 2, 1200, 70, GOLD, a=e(t, 2.4, 3.0))
    caption(c, line, 1.0 if i == 0 else e(t, 0, 0.2))
    txt(c, "Cost split: National Restaurant Association, typical independent US restaurant", VW / 2, VH - 80, 26, CHALK, BODY, a=0.55)


def build(durs, gap=0.35):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + gap + (1.8 if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def tts(out="vo"):
    from kokoro_onnx import Kokoro
    k = Kokoro('/root/kokoro/kokoro-v1.0.onnx', '/root/kokoro/voices-v1.0.bin')
    os.makedirs(out, exist_ok=True)
    durs = []
    for i, (_, line) in enumerate(LINES):
        a, sr = k.create(line, voice=VOICE, speed=SPEED, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 600): nz[-1] + 2400]
        sf.write(os.path.join(out, "%02d.wav" % i), a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open(os.path.join(out, "durs.json"), "w"))


def render(out):
    durs = json.load(open("vo/durs.json"))
    tl, total = build(durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "v.mp4"], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        draw(c, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    sr = 24000
    n = int((total + 0.3) * sr)
    mix = np.zeros(n)
    rng = np.random.RandomState(4)
    tt = np.arange(n) / sr
    for f, amp in ((110.0, 1), (164.8, 0.7), (220.0, 0.5), (261.6, 0.4)):
        mix += 0.010 * amp * np.sin(2 * np.pi * f * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * tt / 7))
    for i, (t0, dd) in enumerate(tl):
        a, _ = sf.read("vo/%02d.wav" % i)
        j = int((t0 + 0.05) * sr)
        mix[j:j + len(a)] += a[:n - j]
        m = int(0.35 * sr)
        sc = rng.randn(m) * np.exp(-np.arange(m) / (0.12 * sr)) * 0.025
        sc = sc - np.convolve(sc, np.ones(5) / 5, mode="same")
        mix[j:j + m] += sc[:n - j]
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    sf.write("a.wav", mix.astype(np.float32), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "v.mp4", "-i", "a.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print("ok", total)


def stills():
    durs = json.load(open("vo/durs.json"))
    tl, total = build(durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, (t0, d) in enumerate(tl):
        T = 0.02 if i == 0 else t0 + min(2.0, d - 0.1)
        draw(c, tl, T)
        surf.write_to_png("st_%02d.png" % i)


def cover(path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    board(c)
    txt(c, "YOU PAY $16.", VW / 2, 330, 110, CHALK)
    plate(c, VW / 2, 740, 300, 0, 0, None)
    txt(c, "?", VW / 2, 840, 300, YEL)
    txt(c, "THEY KEEP 80¢.", VW / 2, 1240, 100, GREEN)
    txt(c, "WHERE'S THE REST?", VW / 2, 1380, 92, CHALK)
    surf.write_to_png(path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "tts":
        tts()
    elif cmd == "stills":
        stills()
    elif cmd == "render":
        render(sys.argv[2])
    elif cmd == "cover":
        cover(sys.argv[2])
