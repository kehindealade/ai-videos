import sys, math, datetime, subprocess
import cairo
from gc_common import *

DUR = 38.0
YB = 1280
BS = 56

S1 = [(-1.0, 0, "we should hang out soon!!"), (1.0, 1, "YES omg"), (2.0, 2, "we need this"),
      (3.0, 3, "let's plan something"), (4.0, 4, "miss you guys"), (5.0, 5, "100%"),
      (6.2, 6, "long overdue lol"), (7.4, 7, "this time for real"), (9.0, 2, "what day works?")]
TYPING = [(10.2, 11.4, 1), (12.4, 13.6, 4), (14.6, 15.8, 6)]
S2 = [(22.5, -1, "12 MONTHS LATER"), (23.2, 0, "we should hang out soon!!"), (24.0, 1, "YES omg"),
      (24.6, 2, "we need this"), (25.2, 3, "let's plan something"), (25.8, 4, "miss you guys"),
      (26.4, 5, "100%"), (27.0, 7, "this time for real")]
PING_T = [0.0] + [m[0] for m in S1[1:]] + [m[0] for m in S2[1:]]
CAL0, CAL1 = 16.0, 21.0
BACK_AT = 21.0
S2_AT = 22.5
STAMP_AT = 30.0
END_AT = 34.4


def pitch_of(kind, size):
    return (size + 68 + 26) if kind != -1 else 120


def draw_bubble(c, x, ybot, sender, text, a, scale, first=False):
    size = BS + 8 if first else BS
    lines = ["we should hang", "out soon!!"] if first else [text]
    w = max(tw(c, l, size) for l in lines) + 2 * 40
    h = (size * 1.14 * len(lines)) + 68 - (0 if len(lines) == 1 else 10)
    col = lighten(AV_COL[sender], 0.45) if not first else AV_COL[0]
    c.save()
    c.translate(x + w / 2, ybot - h / 2)
    c.scale(scale, scale)
    c.translate(-(x + w / 2), -(ybot - h / 2))
    avatar(c, 100, ybot - 46, 46, sender, a)
    rrect(c, x, ybot - h, w, h, 46)
    c.set_source_rgba(*col, a)
    c.fill()
    for i, l in enumerate(lines):
        txt(c, l, x + 40, ybot - h + 34 + size * 0.82 + i * size * 1.14, size, INK, align="l", a=a)
    c.restore()


def draw_dots(c, x, ybot, sender, t, a, scale):
    w, h = 190, 120
    c.save()
    c.translate(x + w / 2, ybot - h / 2)
    c.scale(scale, scale)
    c.translate(-(x + w / 2), -(ybot - h / 2))
    avatar(c, 100, ybot - h / 2, 46, sender, a)
    rrect(c, x, ybot - h, w, h, 46)
    c.set_source_rgba(0.80, 0.82, 0.92, a)
    c.fill()
    for k in range(3):
        dy = -math.sin((t * 7) - k * 0.9) * 10
        c.arc(x + 50 + k * 45, ybot - h / 2 + dy, 12, 0, 2 * math.pi)
        c.set_source_rgba(*INK, a)
        c.fill()
    c.restore()


def draw_div(c, ybot, text, a, scale):
    w = tw(c, text, 50) + 80
    h = 90
    c.save()
    c.translate(540, ybot - h / 2)
    c.scale(scale, scale)
    rrect(c, -w / 2, -h / 2, w, h, 45)
    c.set_source_rgba(0.20, 0.24, 0.40, a)
    c.fill()
    txt(c, text, 0, 17, 50, WHITE, a=a)
    c.restore()


def stack(c, t, msgs, typing, yb, tfade=1.0, seen_at=None, top=760):
    items = []
    for (tm, snd, tx) in msgs:
        if t >= tm:
            items.append(dict(k="div" if snd == -1 else "msg", t0=tm, t1=1e9, snd=snd, tx=tx))
    for (a0, a1, snd) in typing:
        if t >= a0:
            items.append(dict(k="dots", t0=a0, t1=a1, snd=snd, tx=""))
    items.sort(key=lambda d: d["t0"])
    ys = []
    tot = 0.0
    for i, it in enumerate(items):
        first = it["k"] == "msg" and it["tx"].startswith("we should")
        it["first"] = first
        it["pitch"] = 120 if it["k"] == "div" else ((64 * 1.14 * 2 + 68 - 10 + 26) if first else (BS + 68 + 26))
        if it["k"] == "dots":
            it["pitch"] = 146
    for it in items:
        pr = e(t, it['t0'], it['t0'] + 0.22)
        if it['k'] == 'dots':
            pr = pr * (1 - e(t, it['t1'], it['t1'] + 0.22))
        tot += it['pitch'] * pr
    yb = min(yb, top + tot)
    for i, it in enumerate(items):
        yb_i = yb
        for j in range(i + 1, len(items)):
            o = items[j]
            pr = e(t, o["t0"], o["t0"] + 0.22)
            if o["k"] == "dots":
                pr = pr * (1 - e(t, o["t1"], o["t1"] + 0.22))
            yb_i -= o["pitch"] * pr
        it["y"] = yb_i
    last = None
    for it in items:
        if it["k"] == "dots" and t > it["t1"] + 0.25:
            continue
        a = e(t, it["t0"], it["t0"] + 0.12) * tfade
        if it["k"] == "dots":
            a *= 1 - e(t, it["t1"], it["t1"] + 0.2)
        fy = it["y"] + it["pitch"] * (1 - e(t, it["t0"], it["t0"] + 0.22))
        a *= clamp((fy - 520) / 90)
        if a <= 0.01:
            continue
        sc = 0.85 + 0.15 * back((t - it["t0"]) / 0.3)
        if it["k"] == "msg":
            draw_bubble(c, 190, fy, it["snd"], it["tx"], a, sc, it["first"])
            last = it
        elif it["k"] == "div":
            draw_div(c, fy, it["tx"], a, sc)
        else:
            draw_dots(c, 190, fy, it["snd"], t, a, sc)
    if seen_at is not None and t >= seen_at and last is not None:
        txt(c, "Seen by 8", 190 + 6, yb + 52, 48, (0.62, 0.68, 0.85), f=B, align="l",
            a=e(t, seen_at, seen_at + 0.25) * tfade)


def bg(c):
    g = cairo.LinearGradient(0, 0, 0, VH)
    g.add_color_stop_rgb(0, *NAVY0)
    g.add_color_stop_rgb(1, *NAVY1)
    c.set_source(g)
    c.paint()


def header(c):
    c.set_source_rgba(0.075, 0.10, 0.20, 1)
    c.rectangle(0, 0, VW, 262)
    c.fill()
    c.set_source_rgba(0.20, 0.24, 0.40, 1)
    c.rectangle(0, 262, VW, 3)
    c.fill()
    txt(c, "9:41", 70, 64, 40, WHITE, f=B, align="l")
    rrect(c, 900, 36, 80, 36, 9)
    c.set_source_rgba(1, 1, 1, 0.9)
    c.fill()
    c.rectangle(982, 46, 8, 16)
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.9)
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(84, 150)
    c.line_to(54, 180)
    c.line_to(84, 210)
    c.stroke()
    for i in range(8):
        avatar(c, 150 + i * 52, 180, 34, i)
    txt(c, "The Crew", 600, 200, 60, WHITE, align="l")


def inputbar(c):
    rrect(c, 40, 1740, 1000, 120, 60)
    c.set_source_rgba(0.14, 0.17, 0.31, 1)
    c.fill()
    txt(c, "Message", 100, 1815, 50, (0.50, 0.56, 0.75), f=B, bold=False, align="l")
    c.arc(960, 1800, 42, 0, 2 * math.pi)
    c.set_source_rgba(*CORAL, 1)
    c.fill()
    c.set_source_rgba(*INK, 1)
    c.move_to(944, 1780)
    c.line_to(986, 1800)
    c.line_to(944, 1820)
    c.close_path()
    c.fill()


def pill(c, t, label="0", shake_times=()):
    sx = 0.0
    hit = 0.0
    for st in shake_times:
        d = t - st
        if 0 <= d < 0.5:
            sx += math.sin(d * 55) * 14 * (1 - d / 0.5)
            hit = max(hit, 1 - d / 0.5)
    w, h = 640, 96
    x, y = 540 - w / 2 + sx, 318
    rrect(c, x, y, w, h, 48)
    c.set_source_rgba(0.04, 0.05, 0.11, 0.96)
    c.fill()
    rrect(c, x, y, w, h, 48)
    col = (CORAL[0], CORAL[1] * (1 - 0.3 * hit), CORAL[2] * (1 - 0.3 * hit))
    c.set_source_rgba(*col, 1)
    c.set_line_width(6)
    c.stroke()
    s1 = "PLANS MADE:"
    w1 = tw(c, s1, 54)
    w2 = tw(c, label, 66)
    gap = 16
    sx0 = 540 - (w1 + gap + w2) / 2 + sx
    txt(c, s1, sx0, 318 + 66, 54, WHITE, align="l")
    txt(c, label, sx0 + w1 + gap, 318 + 70, 66, (1.0, 0.45 + 0.2 * (1 - hit), 0.40 + 0.2 * (1 - hit)), align="l")


def card(c, lines, a, y0=450, size=84, col=WHITE):
    n = len(lines)
    ls = min(size, int(860 / max(tw(c, l, 100) / 100 for l in lines)))
    h = 60 + n * (ls * 1.12)
    rrect(c, 90, y0, 900, h, 38)
    c.set_source_rgba(0.04, 0.05, 0.11, 0.90 * a)
    c.fill()
    for i, l in enumerate(lines):
        txt(c, l, 540, y0 + 40 + ls * 0.95 + i * ls * 1.12, ls, col, a=a)
    return h


def calendar(c, t):
    k = int((t - CAL0) / 0.4)
    k = max(0, min(11, k))
    f = ((t - CAL0) % 0.4) / 0.4
    for idx, off in ((k, 0.0), (k + 1, 1.0)):
        pass
    def page(idx, dy):
        c.save()
        c.translate(0, dy)
        c.rectangle(0, 0, VW, VH)
        c.clip()
        c.set_source_rgb(0.97, 0.94, 0.86)
        c.paint()
        c.set_source_rgb(0.84, 0.26, 0.24)
        c.rectangle(0, 0, VW, 640)
        c.fill()
        mn = datetime.date(2027, idx + 1, 1).strftime("%B").upper()
        txt(c, mn, 540, 585, 140 if len(mn) < 8 else 116, (1, 1, 1))
        first = datetime.date(2027, idx + 1, 1).weekday()
        nd = ((datetime.date(2027, idx + 2, 1) if idx < 11 else datetime.date(2028, 1, 1)) - datetime.date(2027, idx + 1, 1)).days
        for d in range(nd):
            pos = first + d
            cx = 150 + (pos % 7) * 130
            cy = 750 + (pos // 7) * 105
            txt(c, str(d + 1), cx, cy + 20, 56, (0.20, 0.17, 0.22))
        c.restore()
    page(k, 0)
    if k < 11 and f > 0.7:
        g = e(f, 0.7, 1.0)
        page(k + 1, VH * (1 - g))


def endcard(c, t):
    a = e(t, END_AT, END_AT + 0.25)
    c.set_source_rgba(0.04, 0.05, 0.11, 0.94 * a)
    c.paint()
    sprout(c, 540, 640, 1.5, a)
    txt(c, "IT'S NOT", 540, 880, 120, GOLD, a=a)
    txt(c, "JUST ME", 540, 1010, 120, GOLD, a=a)
    txt(c, "EPISODE 1  ·  THE GROUP CHAT", 540, 1100, 50, WHITE, a=a)
    w = 760
    rrect(c, 540 - w / 2, 1160, w, 120, 60)
    c.set_source_rgba(*GOLD, a)
    c.fill()
    txt(c, "FOLLOW FOR EPISODE 2", 540, 1238, 56, INK, a=a)


def frame(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(s)
    bg(c)
    tp = max([p for p in PING_T if p <= t] + [-9])
    z = 1 + 0.03 * math.exp(-(t - tp) / 0.16)
    c.save()
    c.translate(540, 780)
    c.scale(z, z)
    c.translate(-540, -780)
    if t < S2_AT:
        stack(c, t, S1, TYPING, YB, 1.0, seen_at=BACK_AT)
    else:
        stack(c, t, S2, [], YB, 1.0)
    c.restore()
    header(c)
    inputbar(c)
    shakes = [w[1] for w in TYPING] + [BACK_AT + 0.3, 29.0]
    if CAL0 <= t < BACK_AT:
        calendar(c, t)
    if t < STAMP_AT:
        pill(c, t, "0", shakes)
    if t < 3.4 or (S2_AT + 0.8 <= t < S2_AT + 0.8):
        a = e(t, 0.0, 0.01) * (1 - e(t, 3.0, 3.4))
        card(c, ["EVERY GROUP", "CHAT EVER"], a)
    if STAMP_AT <= t:
        c.set_source_rgba(0.03, 0.04, 0.09, 0.93 * e(t, STAMP_AT, STAMP_AT + 0.2))
        c.paint()
        if t < END_AT:
            pill(c, t, "0", [])
        for i, (wd, ty) in enumerate((("EVERY.", 800), ("SINGLE.", 1010), ("YEAR.", 1220))):
            t0 = STAMP_AT + 0.3 + i * 0.85
            if t >= t0:
                sc = 1 + 0.6 * (1 - back((t - t0) / 0.25)) if t - t0 < 0.25 else 1
                col = CORAL if wd == "YEAR." else WHITE
                c.save()
                c.translate(540, ty)
                c.scale(sc, sc)
                txt(c, wd, 0, 0, 200, col, a=e(t, t0, t0 + 0.08) * (1 - e(t, END_AT - 0.15, END_AT)))
                c.restore()
    if t >= END_AT:
        endcard(c, t)
    return s


def cover():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(s)
    bg(c)
    msgs = [(0, 0, "we should hang out soon!!"), (0, 1, "YES omg")]
    stack(c, 99, msgs, [(0, 1e9, 5)], 1340, 1.0, top=815)
    header(c)
    inputbar(c)
    c.set_source_rgba(0.03, 0.04, 0.09, 0.0)
    card(c, ["EVERY GROUP", "CHAT EVER"], 1.0, y0=400, size=104)
    w, h = 700, 96
    rrect(c, 540 - w / 2, 706, w, h, 55)
    c.set_source_rgba(0.04, 0.05, 0.11, 0.96)
    c.fill()
    rrect(c, 540 - w / 2, 706, w, h, 55)
    c.set_source_rgba(*CORAL, 1)
    c.set_line_width(7)
    c.stroke()
    w1 = tw(c, "PLANS MADE:", 60)
    w2 = tw(c, "?", 76)
    x0 = 540 - (w1 + 16 + w2) / 2
    txt(c, "PLANS MADE:", x0, 706 + 75, 60, WHITE, align="l")
    txt(c, "?", x0 + w1 + 16, 706 + 80, 76, GOLD, align="l")
    return s


def render(out, t0=0.0, t1=DUR):
    n = int(round(DUR * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        s = frame(i / FPS)
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2])
    elif cmd == "still":
        frame(float(sys.argv[2])).write_to_png(sys.argv[3])
    elif cmd == "cover":
        cover().write_to_png(sys.argv[2])
