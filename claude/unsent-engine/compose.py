import cairo, math, sys, os, subprocess
from film import *
import scenes as S

SC = {n: (f, d) for n, f, d in S.SCENES}
_scratch = cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 4, 4))


def state(name, t):
    f, d = SC[name]
    return f(_scratch, clamp(t, 0, d - 1e-3))


def pill(c, x, y, s, size, fg, bg, align="l", a=1.0):
    c.select_font_face(FONT)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance + size * 1.4
    h = size * 1.7
    if align == "r":
        x -= w
    c.set_source_rgba(*bg, 0.82 * a)
    rr(c, x, y, w, h, h / 2)
    c.fill()
    text(c, s, x + size * 0.7, y + h * 0.68, size, fg, a, "l")


def meter_txt(n):
    return "WRITTEN %d  ·  SENT 0" % n


def caption(c, s, a, y, size, maxw):
    c.select_font_face(FONT)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance
    lines = [s]
    if w > maxw:
        words = s.split()
        best = len(words) // 2
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    for i, ln in enumerate(lines):
        yy = y + (i - (len(lines) - 1)) * size * 1.25
        text(c, ln, W_ if False else 0, 0, 1, INK, 0)
        c.select_font_face(FONT)
        c.set_font_size(size)
        ex = c.text_extents(ln)
        c.move_to(caption.cx - ex.width / 2 - ex.x_bearing, yy)
        c.text_path(ln)
        c.set_source_rgba(0, 0, 0, 0.55 * a)
        c.set_line_width(size * 0.16)
        c.stroke_preserve()
        c.set_source_rgba(*CREAM, a)
        c.fill()


caption.cx = W / 2
W_ = W


def phone_alpha(name, t):
    st = state(name, t)
    if not st.get("phone"):
        return 0.0, st
    a = 1.0
    for dt in (-0.25, 0.25):
        s2 = state(name, t + dt)
        if not s2.get("phone"):
            a = min(a, 0.5)
    return a, st


def frame16(c, name, t):
    f, d = SC[name]
    pa, st = phone_alpha(name, t)
    z, cx, cy = st.get("cam", (1.0, W / 2, H / 2))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)
    f(c, t)
    c.restore()
    if st.get("card"):
        return
    g = cairo.LinearGradient(0, H - 260, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    c.set_source(g)
    c.rectangle(0, H - 260, W, 260)
    c.fill()
    if st.get("phone") and pa > 0:
        side = st.get("side", "r")
        x = W - PH_W - 120 if side == "r" else 120
        c.push_group()
        phone_ui(c, x, 110, st["phone"], t)
        c.pop_group_to_source()
        c.paint_with_alpha(pa)
    if st.get("night"):
        pill(c, 60, 50, st["night"], 34, CREAM, INK)
    bm = st.get("big_meter", 0)
    if st.get("meter") is not None:
        if bm > 0.01:
            k = ease(bm)
            c.save()
            c.translate(lerp(W - 60, 1300, k), lerp(50, 40, k))
            c.scale(lerp(1, 2.2, k), lerp(1, 2.2, k))
            pill(c, 0, 0, meter_txt(st["meter"]), 34, CREAM, (0.45, 0.10, 0.18), "r")
            c.restore()
        else:
            pill(c, W - 60, 50, meter_txt(st["meter"]), 34, CREAM, (0.45, 0.10, 0.18), "r")
    caption.cx = W / 2
    for s, a, b in st.get("caps", []):
        if a <= t <= b:
            k = e(t, a, a + 0.35) * (1 - e(t, b - 0.3, b))
            caption(c, s, k, H - 70, 64, 1500)


VW, VH = 1080, 1920
CUT_START = -1.0


def frame9(c, name, t, extra=None):
    f, d = SC[name]
    pa, st = phone_alpha(name, t)
    z, cx, cy = st.get("cam", (1.0, W / 2, H / 2))
    s = 1.78 * max(1.0, z * 0.85)
    if name == "s0":
        cx, cy, s = 640, 780, 1.15
    c.save()
    c.rectangle(0, 0, VW, VH)
    c.clip()
    c.set_source_rgb(*INK)
    c.paint()
    if st.get("card"):
        c.translate(VW / 2, VH / 2)
        c.scale(1.0, 1.0)
        c.translate(-W / 2, -H / 2)
        f(c, t)
        c.restore()
        return st
    c.translate(VW / 2, VH * 0.47)
    c.scale(s, s)
    c.translate(-cx, -cy)
    f(c, t)
    c.restore()
    if st.get("phone") and pa > 0:
        c.set_source_rgba(0, 0, 0, 0.35 * pa)
        c.rectangle(0, 0, VW, VH)
        c.fill()
        c.push_group()
        phone_ui(c, (VW - PH_W * 0.95) / 2, 900, st["phone"], t, 0.95)
        c.pop_group_to_source()
        c.paint_with_alpha(pa)
    if st.get("night"):
        pill(c, 50, 150, st["night"], 40, CREAM, INK)
    if st.get("meter") is not None:
        pill(c, VW - 50, 150, meter_txt(st["meter"]), 34, CREAM, (0.45, 0.10, 0.18), "r")
    caption.cx = VW / 2
    for s_, a, b in st.get("caps", []):
        if a <= t <= b:
            k = (e(t, a, a + 0.35) if a > CUT_START + 0.05 else 1.0) * (1 - e(t, b - 0.3, b))
            caption(c, s_, k, 380, 62, 900)
    return st


def pipe(out, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (w, h), "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)


def render_film(names, outdir):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    for n in names:
        f, d = SC[n]
        p = pipe(os.path.join(outdir, n + ".mp4"), W, H)
        for i in range(int(d * FPS)):
            c.set_source_rgb(0, 0, 0)
            c.paint()
            frame16(c, n, i / FPS)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
        p.stdin.close()
        p.wait()
        print("done", n, flush=True)


def stills16(specs, outdir):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    os.makedirs(outdir, exist_ok=True)
    for n, t in specs:
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame16(c, n, t)
        surf.write_to_png(os.path.join(outdir, "%s_%05.1f.png" % (n, t)))


if __name__ == "__main__":
    if sys.argv[1] == "film":
        render_film(sys.argv[3:], sys.argv[2])
