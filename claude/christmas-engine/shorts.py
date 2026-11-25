import cairo, sys, os, subprocess, math
from xm import *
import xm
import film as F

VW, VH = 1080, 1920
SCALE = VH / H


def scene_state(c, T):
    for t0, t1, fn in F.SCENES:
        if t0 <= T < t1:
            return fn(c, T)
    return {}


def place(c, T, fx, zoom=1.0, fy=None, custom=None):
    s = SCALE * zoom
    c.save()
    c.rectangle(0, 0, VW, VH)
    c.clip()
    c.set_source_rgb(*INK)
    c.paint()
    c.translate(VW / 2, VH / 2)
    c.scale(s, s)
    c.translate(-fx, -(H / 2 if fy is None else fy))
    if custom is not None:
        custom(c)
    else:
        scene_state(c, T)
    c.restore()


def plaque(c, lines, y, size=80, a=1.0, col=INK, bg=SNOW, w=980):
    n = len(lines)
    h = size * 1.25 * n + 50
    x = (VW - w) / 2
    c.set_source_rgba(0, 0, 0, 0.25 * a)
    rr(c, x + 6, y + 10, w, h, 38)
    c.fill()
    c.set_source_rgba(*bg, 0.96 * a)
    rr(c, x, y, w, h, 38)
    c.fill()
    for i, ln in enumerate(lines):
        col_i = col if i == 0 else BURG
        text(c, ln, VW / 2, y + 25 + size * 1.0 + i * size * 1.25, size, col_i, a)


def stamp(c, year, a=1.0, x=130, y=170):
    c.set_source_rgba(*CREAM, 0.95 * a)
    c.arc(x, y, 92, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*BURG, a)
    c.set_line_width(9)
    c.arc(x, y, 80, 0, 2 * math.pi)
    c.stroke()
    text(c, "YEAR", x, y - 26, 30, BURG, a, "c")
    text(c, str(year), x, y + 50, 84, INK, a, "c")


def knock_meter(c, n, a=1.0, x=VW - 60, y=120):
    for i in range(3):
        cx = x - 40 - i * 90
        c.set_source_rgba(*CREAM, 0.2 * a)
        c.arc(cx, y, 34, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*CREAM, a)
        c.set_line_width(6)
        c.arc(cx, y, 34, 0, 2 * math.pi)
        c.stroke()
        if i < n:
            c.set_source_rgba(*GOLD, a)
            c.arc(cx, y, 22, 0, 2 * math.pi)
            c.fill()
    text(c, "KNOCKS", x - 130, y + 80, 30, CREAM, a, "c")


def gift_meter(c, n, total=4, a=1.0):
    x0 = 70
    y = 150
    c.set_source_rgba(0.04, 0.06, 0.12, 0.7 * a)
    rr(c, x0 - 30, y - 70, 560, 170, 34)
    c.fill()
    text(c, "GIFTS NEVER GIVEN", x0, y - 20, 36, CREAM, a, "l")
    for i in range(total):
        cx = x0 + 40 + i * 120
        if i < n:
            g = GIFTS[i % 4]
            gift(c, cx, y + 80, 64, 52, g[0], g[1], tag=False)
        else:
            c.set_source_rgba(*CREAM, 0.35 * a)
            c.set_line_width(4)
            c.set_dash([8, 8])
            rr(c, cx - 32, y + 28, 64, 52, 6)
            c.stroke()
            c.set_dash([])


def cap9(c, s, a, y=1330, size=88):
    caption(c, s, a, VW / 2, y, size, 940)


def endcard(c, lines, a=1.0, t=0.0):
    F.sprout_card(c, 1.0, None, t)
    c.save()
    c.restore()
    snowfall(c, t, 50, 20, 0.5)
    yy = 1180
    for i, ln in enumerate(lines):
        text(c, ln, VW / 2, yy + i * 100, 66 if i == 0 else 56, GOLD if i == 0 else (0.88, 0.92, 0.88), a)


def sprout9(c, lines, t=0.0, sub=None):
    c.set_source_rgb(0.07, 0.15, 0.12)
    c.paint()
    c.save()
    c.translate(VW / 2 - W / 2, 520 - 400)
    F.sprout_card(c, 1.0, None, t, False)
    c.restore()
    c.set_source_rgb(0.07, 0.15, 0.12)
    c.rectangle(0, 0, VW, 230)
    c.fill()
    c.rectangle(0, 940, VW, 980)
    c.fill()
    text(c, "Small Win Films", VW / 2, 1010, 92, (0.97, 0.93, 0.82), 1.0)
    for i, ln in enumerate(lines):
        text(c, ln, VW / 2, 1170 + i * 96, 64 if i == 0 else 54, GOLD if i == 0 else (0.88, 0.92, 0.88), 1.0)
    pill = "FOLLOW FOR THE NEXT FILM"
    c.select_font_face(FONT)
    c.set_font_size(46)
    w = c.text_extents(pill).x_advance + 80
    c.set_source_rgb(*GOLD)
    rr(c, (VW - w) / 2, 1440, w, 96, 48)
    c.fill()
    text(c, pill, VW / 2, 1505, 46, INK, 1.0)


# ------------------------------------------------------------- short 1
def seg_list_1():
    return [
        dict(T=0.2, d=3.3, fx=720, kind="film", hook=["3 CHRISTMASES.", "0 KNOCKS."], year=None),
        dict(T=8.6, d=2.0, fx=1015, kind="film", cap="He missed my wedding."),
        dict(T=14.0, d=1.6, fx=960, kind="film", cap="I stopped answering."),
        dict(T=21.6, d=2.6, fx=860, kind="film", year=1, cap="Christmas Eve."),
        dict(T=28.0, d=2.7, fx=960, kind="film", year=1),
        dict(T=32.2, d=2.4, fx=720, kind="film", year=1),
        dict(T=41.0, d=3.0, fx=960, kind="film", year=2, cap="Year two."),
        dict(T=48.4, d=2.2, fx=720, kind="film", year=2),
        dict(T=66.0, d=2.4, fx=720, kind="film", year=3, cap="Year three."),
        dict(T=70.2, d=2.4, fx=960, kind="film", year=3),
        dict(T=78.0, d=3.0, fx=900, kind="film", year=3),
        dict(T=103.0, d=3.8, fx=720, kind="film", year=4, cap="Year four?"),
    ]


def make_frame_1(c, t, segs):
    acc = 0.0
    for sg in segs:
        if acc <= t < acc + sg["d"]:
            tl = t - acc
            T = sg["T"] + tl
            place(c, T, sg["fx"], 1.0)
            if sg.get("hook"):
                plaque(c, sg["hook"], 250, 80, e(tl, 0.0, 0.25) * (1 - e(tl, sg["d"] - 0.3, sg["d"])))
            elif sg.get("year"):
                stamp(c, sg["year"], 1.0)
                knock_meter(c, 0, 1.0)
            if sg.get("cap"):
                cap9(c, sg["cap"], e(tl, 0.0, 0.3) * (1 - e(tl, sg["d"] - 0.3, sg["d"])))
            return
        acc += sg["d"]
    sprout9(c, ["Did she knock?", "Watch the full film: She Never Knocked"], t)


def total_1(segs):
    return sum(s["d"] for s in segs)



def fade(x, a, b):
    return e(x, 0.0, a) * (1 - e(x, b - a, b))


# ------------------------------------------------------------- short 2
def seg_list_2():
    return [
        dict(d=3.2, n=1, kind="cup", hook=["A GIFT EVERY YEAR.", "NEVER GIVEN."], year=1, anim=None, T=None),
        dict(d=4.0, n=1, kind="cup", year=2, anim=(0.4, 3.0), cap="Year two."),
        dict(d=4.0, n=2, kind="cup", year=3, anim=(0.4, 3.0), cap="Year three."),
        dict(d=4.0, kind="cab", year=3, T=76.0, cap="Her phone stayed silent."),
        dict(d=6.2, kind="film", year=4, T=93.0, fx=800, cap="Year four."),
        dict(d=3.6, kind="film", year=4, T=103.5, fx=720),
    ]


def make_frame_2(c, t, segs):
    acc = 0.0
    for sg in segs:
        if acc <= t < acc + sg["d"]:
            tl = t - acc
            if sg["kind"] == "cup":
                an = sg.get("anim")
                ng = sg["n"]
                k = e(tl, an[0], an[1]) if an else None
                place(c, 0, 1400, 1.0, custom=lambda cc: xm.apartment(cc, 60 + tl, ng, new_gift=k, maya_x=520))
                shown = ng + (1 if (k is not None and k > 0.95) else 0)
                gift_meter(c, shown)
            elif sg["kind"] == "cab":
                tr = sg["T"] + tl
                place(c, 0, 900, 1.0, custom=lambda cc: xm.cabin(cc, tr, look=1.0, gifts=3, win="phone", mood="sad", tear=0.6, phone_dash=True))
                gift_meter(c, 3)
            else:
                place(c, sg["T"] + tl, sg["fx"], 1.0)
                gift_meter(c, 4)
            if sg.get("year"):
                stamp(c, sg["year"], 1.0, x=VW - 140, y=420)
            if sg.get("hook"):
                plaque(c, sg["hook"], 560, 80, fade(tl, 0.25, sg["d"]))
            if sg.get("cap"):
                cap9(c, sg["cap"], fade(tl, 0.3, sg["d"]))
            return
        acc += sg["d"]
    sprout9(c, ["Did she ever give them?", "Watch: She Never Knocked"], t)


# ------------------------------------------------------------- short 3
def seg_list_3():
    return [
        dict(T=118.4, d=3.4, fx=1100, hook=["YEAR 4.", "I FINALLY KNOCKED."], big=True),
        dict(T=124.8, d=3.2, fx=980),
        dict(T=133.0, d=6.6, fx=(600, 1260), cap="I was driving to you."),
        dict(T=141.0, d=5.0, fx=900),
        dict(T=152.0, d=6.0, fx=900, cap="Neither of us went first."),
        dict(T=162.0, d=6.0, fx=1000, cap="This year, someone did."),
    ]


def make_frame_3(c, t, segs):
    acc = 0.0
    for i, sg in enumerate(segs):
        if acc <= t < acc + sg["d"]:
            tl = t - acc
            fx = sg["fx"]
            if isinstance(fx, tuple):
                fx = lerp(fx[0], fx[1], e(tl, 1.0, sg["d"] - 1.0))
            place(c, sg["T"] + tl, fx, 1.0)
            kn = 0 if i == 0 and tl < 2.7 else 1
            knock_meter(c, kn if i else (1 if tl > 2.7 else 0), 1.0)
            if sg.get("hook"):
                plaque(c, sg["hook"], 250, 80, fade(tl, 0.25, sg["d"]))
            if sg.get("cap"):
                cap9(c, sg["cap"], fade(tl, 0.3, sg["d"]))
            return
        acc += sg["d"]
    sprout9(c, ["Who knocked first?", "Watch: She Never Knocked"], t)


def pipe9(out):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)


SHORTS = {1: (seg_list_1, make_frame_1), 2: (seg_list_2, make_frame_2), 3: (seg_list_3, make_frame_3)}


def render(n, out):
    fl, ff = SHORTS[n]
    segs = fl()
    total = sum(s["d"] for s in segs) + 3.0
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = pipe9(out)
    for i in range(int(total * FPS)):
        c.set_source_rgb(0, 0, 0)
        c.paint()
        ff(c, i / FPS, segs)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    print("done", n, total, flush=True)


def stills(n, times, outdir):
    fl, ff = SHORTS[n]
    segs = fl()
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for t in times:
        c.set_source_rgb(0, 0, 0)
        c.paint()
        ff(c, t, segs)
        surf.write_to_png("%s/s%d_%05.1f.png" % (outdir, n, t))


if __name__ == "__main__":
    if sys.argv[1] == "render":
        render(int(sys.argv[2]), sys.argv[3])
    else:
        stills(int(sys.argv[2]), [float(x) for x in sys.argv[4:]], sys.argv[3])
