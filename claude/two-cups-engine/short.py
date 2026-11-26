import cairo, math, os, sys, subprocess, wave
import numpy as np
import film as F
from timeline import TWO_T

VW, VH, FPS = 1080, 1920, 30
CUTS = [(0.0, 6.0, 250, 1100), (16.5, 21.0, 900, 1020), (21.0, 24.5, 330, 1100), (53.0, 59.0, 470, 1000),
        (84.0, 90.0, 440, 1020), (108.0, 113.0, 480, 1000)]
END = 6.0
END_SRC = 165.0
YC = 930

F.UI_ON = False
src = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
sc = cairo.Context(src)


def px(x, y):
    src.flush()
    d = src.get_data()
    st = src.get_stride()
    vals = []
    for dx in range(0, 600, 20):
        xx = min(1919, max(0, x + dx))
        i = y * st + xx * 4
        vals.append((d[i + 2] / 255, d[i + 1] / 255, d[i] / 255))
    vals.sort(key=lambda v: sum(v))
    return vals[len(vals) // 2]


def wrap(c, s, size, maxw):
    c.select_font_face(F.FONT)
    c.set_font_size(size)
    words, lines, cur = s.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if c.text_extents(nxt).width > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = nxt
    lines.append(cur)
    return lines


def layout(c, x0, cw):
    s = VW / cw
    bh = 1080 * s
    y0 = YC - bh / 2
    top = px(x0 + 100, 6)
    bot = px(x0 + 100, 1072)
    c.set_source_rgb(*top)
    c.rectangle(0, 0, VW, y0 + 2)
    c.fill()
    c.set_source_rgb(*bot)
    c.rectangle(0, y0 + bh - 2, VW, VH)
    c.fill()
    c.save()
    c.translate(0, y0)
    c.scale(s, s)
    c.rectangle(0, 0, cw, 1080)
    c.clip()
    c.set_source_surface(src, -x0, 0)
    c.paint()
    c.restore()
    g = cairo.LinearGradient(0, y0, 0, y0 + 60)
    g.add_color_stop_rgba(0, *top, 1)
    g.add_color_stop_rgba(1, *top, 0)
    c.set_source(g)
    c.rectangle(0, y0, VW, 60)
    c.fill()
    g = cairo.LinearGradient(0, y0 + bh - 60, 0, y0 + bh)
    g.add_color_stop_rgba(0, *bot, 0)
    g.add_color_stop_rgba(1, *bot, 1)
    c.set_source(g)
    c.rectangle(0, y0 + bh - 60, VW, 60)
    c.fill()
    g = cairo.LinearGradient(0, VH - 520, 0, VH)
    g.add_color_stop_rgba(0, 0.06, 0.07, 0.10, 0)
    g.add_color_stop_rgba(1, 0.06, 0.07, 0.10, 0.75)
    c.set_source(g)
    c.rectangle(0, VH - 520, VW, 520)
    c.fill()
    g = cairo.LinearGradient(0, 0, 0, 420)
    g.add_color_stop_rgba(0, 0.06, 0.07, 0.10, 0.45)
    g.add_color_stop_rgba(1, 0.06, 0.07, 0.10, 0)
    c.set_source(g)
    c.rectangle(0, 0, VW, 420)
    c.fill()


def overlay(c):
    if "tag" in F.UI:
        s, pop, alpha = F.UI["tag"]
        F.tag_draw(c, 60, 250, 54, s, pop, alpha)
    if "meter" in F.UI:
        n, alpha, bump, shownum = F.UI["meter"]
        F.meter_draw(c, 610, 150, 1.0, n, alpha, bump, shownum)
    if "two" in F.UI:
        t = F.UI["two"]
        if t < TWO_T + 0.8:
            f = F.ease(F.seg(t, TWO_T, TWO_T + 0.8))
            x = F.lerp(VW / 2, 815, f)
            y = F.lerp(1080, 300, f)
            sz = F.lerp(560, 112, f) * (1 + 0.18 * (1 - F.seg(t, 0, 0.18)))
            al = 1 if f < 0.9 else 1 - (f - 0.9) * 10
            F.text(c, "2", x + 9 * (1 - f), y + 11 * (1 - f), sz, F.INK, 0.45 * al)
            F.text(c, "2", x, y, sz, F.CREAM, al)
    for s, k, col in F.UI.get("caps", []):
        lines = wrap(c, s, 84, 940)
        y = 1660 - (len(lines) - 1) * 50
        for i, ln in enumerate(lines):
            yy = y + i * 100
            for dx, dy, al in ((0, 7, 0.4), (4, 5, 0.6), (-3, 5, 0.4)):
                F.text(c, ln, VW / 2 + dx, yy + dy, 84, F.INK, al * k)
            F.text(c, ln, VW / 2, yy, 84, col, k)


def vframe(c, T, x0, cw):
    F.frame(sc, T)
    layout(c, x0, cw)
    overlay(c)


def endcard(c, t):
    F.vgrad(c, 0, 0, VW, VH, F.SLATE_N, F.mix(F.SLATE_N, F.INK, 0.6))
    F.card_rain(c, t, 0.06)
    F.glow(c, VW / 2, 760, 600, 0.07, F.YEL)
    a = F.ease(F.seg(t, 0.05, 0.4))
    F.text(c, "Did he ever make", VW / 2, 700, 92, F.CREAM, a)
    F.text(c, "just one cup?", VW / 2, 812, 92, F.CREAM, a)
    b = F.ease(F.seg(t, 1.6, 2.1))
    F.text(c, "Full film on the channel", VW / 2, 1010, 64, F.YEL, b)
    k = F.ease(F.seg(t, 2.4, 3.0))
    F.sprout(c, VW / 2, 1230, 90, k)
    F.text(c, "Small Win Films", VW / 2, 1400, 52, F.CREAM, k)
    if t > END - 0.5:
        F.tint(c, (0, 0, 0), F.seg(t, END - 0.5, END))


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    tmp = out[:-4] + ".part.mp4"
    p = F.ff_writer(tmp, VW, VH)
    for a, b, x0, cw in CUTS:
        for i in range(int(round((b - a) * FPS))):
            vframe(c, a + i / FPS, x0, cw)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
    for i in range(int(round(END * FPS))):
        endcard(c, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(1)
    os.rename(tmp, out)


def audio(src_wav, out):
    w = wave.open(src_wav)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768
    segs = [(a, b - a) for a, b, _, _ in CUTS] + [(END_SRC, END)]
    total = sum(int(round(d * FPS)) for _, d in segs) * sr // FPS
    y = np.zeros((total + sr, 2))
    f = int(0.08 * sr)
    o = 0
    for k, (s0, d) in enumerate(segs):
        n = int(round(d * FPS)) * sr // FPS
        i0 = int(s0 * sr)
        lo = f if k > 0 else 0
        a0 = max(0, i0 - lo)
        seg = x[a0:i0 + n + f].copy()
        win = np.ones(len(seg))
        if k > 0:
            win[:2 * f] = np.linspace(0, 1, 2 * f)
        win[-2 * f:] = np.minimum(win[-2 * f:], np.linspace(1, 0, 2 * f))
        seg *= win[:, None]
        st = o - lo
        y[st:st + len(seg)] += seg
        o += n
    y = y[:total]
    fo = int(0.5 * sr)
    y[-fo:] *= np.linspace(1, 0, fo)[:, None]
    y = y / np.max(np.abs(y)) * 10 ** (-2.5 / 20)
    with wave.open(out, "wb") as ow:
        ow.setnchannels(2)
        ow.setsampwidth(2)
        ow.setframerate(sr)
        ow.writeframes((y * 32767).astype(np.int16).tobytes())


def stills(outdir, times):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for spec in times:
        if spec.startswith("end"):
            endcard(c, float(spec[3:]))
        else:
            T = float(spec)
            cut = [cc for cc in CUTS if cc[0] <= T < cc[1]][0]
            vframe(c, T, cut[2], cut[3])
        surf.write_to_png(os.path.join(outdir, "v_%s.png" % spec))


def strip(path, specs):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    cols = 8
    rows = (len(specs) + cols - 1) // cols
    sheet = cairo.ImageSurface(cairo.FORMAT_RGB24, 240 * cols, 427 * rows)
    s2 = cairo.Context(sheet)
    for i, spec in enumerate(specs):
        if spec.startswith("end"):
            endcard(c, float(spec[3:]))
        else:
            T = float(spec)
            cut = [cc for cc in CUTS if cc[0] <= T < cc[1]][0]
            vframe(c, T, cut[2], cut[3])
        surf.flush()
        s2.save()
        s2.translate((i % cols) * 240, (i // cols) * 427)
        s2.scale(240 / VW, 240 / VW)
        pat = cairo.SurfacePattern(surf)
        pat.set_filter(cairo.FILTER_BEST)
        s2.set_source(pat)
        s2.paint()
        s2.restore()
    sheet.write_to_png(path)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "strip":
        strip(sys.argv[2], sys.argv[3:])
    else:
        render(sys.argv[2])
        audio(sys.argv[3], sys.argv[4])
