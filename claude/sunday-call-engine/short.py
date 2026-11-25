import cairo, sys, os, subprocess, math
from sd import *
import film as F

VW, VH = 1080, 1920
PH = 880
DIV0, DIV1 = PH, PH + 150
BOT = VH - DIV1


def panel(c, y, h, fn, fx=W / 2, fy=H / 2):
    s = h / H * 1.0
    c.save()
    c.rectangle(0, y, VW, h)
    c.clip()
    c.translate(VW / 2, y + h / 2)
    c.scale(s, s)
    c.translate(-fx, -fy)
    fn(c)
    c.restore()


def band(c, n, t, circ=1.0, pop=0.0, label="SUNDAY · 6:00 PM", nx=VW - 150):
    vgrad(c, 0, DIV0, VW, DIV1 - DIV0, PAPER, (0.94, 0.89, 0.81))
    c.set_source_rgb(*RED)
    c.rectangle(0, DIV0, VW, 8)
    c.rectangle(0, DIV1 - 8, VW, 8)
    c.fill()
    text(c, "MISSED SUNDAYS", 60, DIV0 + 72, 50, PLUM_D, 1.0, "l")
    text(c, label, 60, DIV0 + 120, 32, PLUM, 1.0, "l", FONTB)
    ps = 1 + 0.25 * math.sin(math.pi * clamp(pop))
    c.save()
    c.translate(nx, (DIV0 + DIV1) / 2)
    c.scale(ps, ps)
    text(c, str(n) if n is not None else "?", 0, 36, 104, INK, 1.0, "c")
    marker_circle(c, 0, 0, 62, 56, circ, 9, RED, 1.0, seed=n or 0)
    c.restore()


def hook(c, lines, a, y=600, size=82):
    if a <= 0.01:
        return
    c.select_font_face(FONT)
    c.set_font_size(size)
    w = max(c.text_extents(l).x_advance for l in lines) + 90
    h = size * 1.25 * len(lines) + 46
    x = (VW - w) / 2
    c.set_source_rgba(0, 0, 0, 0.25 * a)
    rr(c, x + 6, y + 10, w, h, 30)
    c.fill()
    c.set_source_rgba(*PAPER, 0.97 * a)
    rr(c, x, y, w, h, 30)
    c.fill()
    for i, ln in enumerate(lines):
        text(c, ln, VW / 2, y + 22 + size + i * size * 1.25, size, INK if i == 0 else RED, a)


def cap(c, s, a):
    if a <= 0.01:
        return
    c.select_font_face(FONT)
    c.set_font_size(70)
    w = c.text_extents(s).x_advance + 70
    c.set_source_rgba(0.08, 0.05, 0.08, 0.62 * a)
    rr(c, (VW - w) / 2, 1192, w, 110, 34)
    c.fill()
    caption(c, s, a, VW / 2, 1272, 70, 960)


def kit(T, **kw):
    return lambda cc: kitchen(cc, T, **kw)


SEGS = [
    dict(d=3.0, top=lambda T: (lambda cc: gran_close(cc, T, "soft", -0.3, ring=1.0, dusk=0.1), 900), bot=lambda T: (lambda cc: table_close(cc, T, "down", 1.0, py=700), 700), n=0, hook=["SHE CALLED EVERY", "SUNDAY AT 6."]),
    dict(d=2.6, top=lambda T: (lambda cc: gran_close(cc, T, "soft", -0.3, ring=1.0, dusk=0.1), 900), bot=lambda T: (lambda cc: table_close(cc, T, "incoming", 1.0, py=700), 700), n=0, hook=["HE LET IT RING."]),
    dict(d=3.0, top=lambda T: (lambda cc: hangup_close(cc, T, e(T, 0.2, 1.4)), 1040), bot=lambda T: (lambda cc: apt(cc, T, "desk", 1.0, "incoming", look=0.3), 820), n=1, tick=1.4, cap="Week 1."),
    dict(d=3.0, top=lambda T: (kit(T, who="sit", dusk=0.15, cups=1, mood="calm"), 900), bot=lambda T: (lambda cc: office(cc, T), 1100), n=1, cap="He meant to call back.", label="MONDAY"),
    dict(d=3.0, top=lambda T: (kit(T, who="sit", dusk=0.1, cups=2, cup2_k=e(T, 0.4, 2.0), mood="soft"), 1000), bot=lambda T: (lambda cc: apt(cc, T, "call", 1.0, "incoming"), 820), n=1, cap="Week 2."),
    dict(d=3.0, top=lambda T: (kit(T, who="sit", dusk=0.25, cups=2, cup2_k=1 - e(T, 0.3, 2.2), mood="sad"), 1000), bot=lambda T: (lambda cc: table_close(cc, T, "missed", 0.0, lock=("SUNDAY", "7:30"), note=("MISSED CALL", "GRANDMA", "Sunday 6:00 PM"), py=700), 700), n=2, tick=2.2, cap="She put his cup back."),
    dict(d=3.0, top=lambda T: (lambda cc: (kitchen_bg(cc, T, 0.2, 0.14 * (1 - e(T, 0.8, 2.2))), gran(cc, 900, 1030, 0.92, -0.6, "soft", T, "reach", k=e(T, 0.3, 1.0) * (1 - e(T, 2.3, 2.9))), kitchen_table(cc, 1, 1.0, True, T, x0=760)), 850), bot=lambda T: (lambda cc: apt(cc, T, "sleep", 1.0), 960), n=2, cap="Week 3."),
    dict(d=3.0, top=lambda T: (lambda cc: gran_close(cc, T, "sad", -0.2, ring=1.0 if T < 1.8 else 0.0, dusk=0.4), 900), bot=lambda T: (lambda cc: son_close(cc, T, "calm", -0.3, 0.4, up=-0.6), 800), n=3, tick=1.8),
    dict(d=3.4, top=lambda T: (kit(T, who="sit", dusk=0.3, cups=2, cup2_k=e(T, 0.2, 1.6), mood="soft"), 1000), bot=lambda T: (lambda cc: table_close(cc, T, "incoming", 1.0, flip=(lambda f: f if abs(f) > 0.04 else -0.04)(math.cos(math.pi * e(T, 1.4, 2.2))), py=700), 700), n=3, cap="Week 4."),
    dict(d=3.4, top=lambda T: (lambda cc: gran_close(cc, T, "worry", -0.3, ring=1.0 if T < 2.0 else 0.0, dusk=0.45), 900), bot=lambda T: (lambda cc: son_close(cc, T, "worry", 0.0, 0.5, up=-0.7), 800), n=4, tick=2.0, cap="She left his cup out."),
    dict(d=3.4, top=lambda T: (kit(T, who="sit", dusk=0.5, cups=2, mood="sad"), 1000), bot=lambda T: (lambda cc: table_close(cc, T, "missed", 0.0, lock=("SUNDAY", "5:59" if T < 2.4 else "6:00"), hand_k=1.0, py=700), 700), n=4, cap="Week 5."),
    dict(d=1.8, top=lambda T: (lambda cc: keypad_close(cc, T, math.sin(math.pi * ((T / 0.24) % 1)), min(10, int(T / 0.24) + 3)), 900), bot=lambda T: (lambda cc: table_close(cc, T, "incoming", 1.0, py=700), 700), n=4, label="SUNDAY · 6:00 PM", cap="6:00 PM."),
]
END = 3.2


def total():
    return sum(s["d"] for s in SEGS) + END


def end9(c, t):
    F.end_card(c, t, VW, VH, True)
    c.set_source_rgb(*PAPER)
    c.rectangle(0, 860, VW, 520)
    c.fill()
    text(c, "Week 5.", VW / 2, 960, 76, PLUM_D)
    text(c, "Does he pick up?", VW / 2, 1110, 80, INK)
    marker_circle(c, VW / 2, 1086, 430, 88, e(t, 0.2, 1.2), 9, RED, 1.0, 4)
    pill = "WATCH THE FULL FILM"
    c.select_font_face(FONT)
    c.set_font_size(46)
    w = c.text_extents(pill).x_advance + 80
    c.set_source_rgb(*PLUM)
    rr(c, (VW - w) / 2, 1250, w, 96, 48)
    c.fill()
    text(c, pill, VW / 2, 1314, 46, CREAM)


def frame9(c, t):
    acc = 0.0
    for sg in SEGS:
        if acc <= t < acc + sg["d"]:
            tl = t - acc
            fn, fx = sg["top"](tl)
            panel(c, 0, PH, fn, fx)
            fn, fx = sg["bot"](tl)
            panel(c, DIV1, BOT, fn, fx)
            n = sg["n"]
            circ, pop = 1.0, 0.0
            if sg.get("tick") is not None:
                if tl < sg["tick"]:
                    n -= 1
                else:
                    circ, pop = e(tl, sg["tick"], sg["tick"] + 0.6), e(tl, sg["tick"], sg["tick"] + 0.45)
            band(c, n, t, circ, pop, sg.get("label", "SUNDAY · 6:00 PM"))
            if sg.get("hook"):
                hook(c, sg["hook"], e(tl, 0.0, 0.15) * (1 - e(tl, sg["d"] - 0.2, sg["d"])))
            if sg.get("cap"):
                cap(c, sg["cap"], e(tl, 0.0, 0.2) * (1 - e(tl, sg["d"] - 0.2, sg["d"])))
            return
        acc += sg["d"]
    end9(c, t - acc)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(total() * FPS)):
        c.save()
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame9(c, i / FPS)
        c.restore()
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    print("done", total(), flush=True)


def stills(times, outdir):
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for t in times:
        c.save()
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame9(c, t)
        c.restore()
        surf.write_to_png("%s/s_%05.1f.png" % (outdir, t))


if __name__ == "__main__":
    if sys.argv[1] == "render":
        render(sys.argv[2])
    else:
        stills([float(x) for x in sys.argv[3:]], sys.argv[2])
