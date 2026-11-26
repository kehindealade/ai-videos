import cairo, math, os, sys, subprocess, wave
import numpy as np
import film as F
from timeline import START

VW, VH, FPS = 1080, 1920, 30
CW = 1000
SC = VW / CW
Y0 = 420
CUTS = [("s1", 0.0, 9.4, 230), ("s4", 6.2, 9.8, 520), ("s5", 1.6, 4.6, 400), ("s5", 9.4, 13.4, 60),
        ("s6", 8.2, 12.8, 300), ("s7", 10.4, 14.0, 150), ("s8", 9.5, 13.3, 320)]
END = 4.6
F.DRAW_UI = False
F.dip = lambda *a, **k: None

src = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
sc = cairo.Context(src)


def px(x, y):
    src.flush()
    d = src.get_data()
    st = src.get_stride()
    vals = []
    for dx in range(0, 600, 20):
        i = y * st + (x + dx) * 4
        vals.append((d[i + 2] / 255, d[i + 1] / 255, d[i] / 255))
    vals.sort(key=lambda v: sum(v))
    return vals[len(vals) // 2]


def wrap(c, s, size, maxw):
    c.select_font_face(F.FONT)
    c.set_font_size(size)
    if ". " in s and c.text_extents(s).width > maxw:
        parts = [p if p.endswith(".") else p + "." for p in s.split(". ")]
        if all(c.text_extents(p).width <= maxw for p in parts):
            return parts
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


def lum(col):
    return 0.3 * col[0] + 0.59 * col[1] + 0.11 * col[2]


def vframe(c, name, t, cx):
    F.frame(sc, name, t)
    sky = px(cx + 200, 4)
    ground = px(cx + 200, 1074)
    c.set_source_rgb(*sky)
    c.rectangle(0, 0, VW, Y0 + 2)
    c.fill()
    c.set_source_rgb(*ground)
    c.rectangle(0, Y0 + 1080 * SC - 2, VW, VH)
    c.fill()
    c.save()
    c.translate(0, Y0)
    c.scale(SC, SC)
    c.rectangle(0, 0, CW, 1080)
    c.clip()
    c.set_source_surface(src, -cx, 0)
    c.paint()
    c.restore()
    g = cairo.LinearGradient(0, Y0 - 40, 0, Y0 + 60)
    g.add_color_stop_rgba(0, *sky, 1)
    g.add_color_stop_rgba(1, *sky, 0)
    c.set_source(g)
    c.rectangle(0, Y0 - 40, VW, 100)
    c.fill()
    if "tag" in F.UI:
        s, pop, dark = F.UI["tag"]
        F.tag_draw(c, 70, 300, 46, s, pop, lum(sky) < 0.45)
    if "meter" in F.UI:
        F.meter_draw(c, 570, 196, 1.1, *F.UI["meter"])
    gdark = lum(ground) < 0.5
    for s, k, dark in F.UI.get("caps", []):
        lines = wrap(c, s, 76, 900)
        y = 1560 - (len(lines) - 1) * 46
        for i, ln in enumerate(lines):
            yy = y + i * 92
            if gdark:
                F.text(c, ln, VW / 2, yy, 76, F.CREAM, k)
            else:
                F.text(c, ln, VW / 2 + 3, yy + 4, 76, F.CREAM, 0.7 * k)
                F.text(c, ln, VW / 2, yy, 76, F.INK, k)


def endcard(c, t):
    c.set_source_rgb(*F.INK)
    c.paint()
    k = F.ease(F.seg(t, 0.2, 0.8))
    F.sprout(c, VW / 2, 620, 110, k)
    a = F.ease(F.seg(t, 0.4, 0.9))
    F.text(c, "Did anything", VW / 2, 900, 92, F.CREAM, a)
    F.text(c, "work?", VW / 2, 1010, 92, F.CREAM, a)
    b = F.ease(F.seg(t, 1.4, 1.9))
    F.text(c, "Watch the full film", VW / 2, 1190, 64, F.AMBER, b)
    F.text(c, "Small Win Films", VW / 2, 1280, 50, F.CREAM, 0.6 * b)
    if t > END - 0.5:
        F.tint(c, (0.03, 0.06, 0.08), F.seg(t, END - 0.5, END))


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for name, a, b, cx in CUTS:
        for i in range(int(round((b - a) * FPS))):
            vframe(c, name, a + i / FPS, cx)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
    for i in range(int(END * FPS)):
        endcard(c, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(1)
    os.rename(tmp, out)


def audio(out):
    w = wave.open("audio.wav")
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768
    parts = []
    fd = int(0.03 * sr)
    for name, a, b, _ in CUTS + [("s12", 0.0, END, 0)]:
        i0 = int((START[name] + a) * sr)
        seg = x[i0:i0 + int(round((b - a) * FPS)) * sr // FPS].copy()
        seg[:fd] *= np.linspace(0, 1, fd)[:, None]
        seg[-fd:] *= np.linspace(1, 0, fd)[:, None]
        parts.append(seg)
    y = np.concatenate(parts)
    f = int(0.6 * sr)
    y[-f:] *= np.linspace(1, 0, f)[:, None]
    y = y / np.max(np.abs(y)) * 0.85
    o = wave.open(out, "wb")
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(sr)
    o.writeframes((y * 32767).astype(np.int16).tobytes())
    o.close()


def stills(outdir, specs):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for spec in specs:
        name, t, cx = spec.split("@")
        if name == "end":
            endcard(c, float(t))
        else:
            vframe(c, name, float(t), int(cx))
        surf.write_to_png(os.path.join(outdir, "v_%s_%s.png" % (name, t)))


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2], sys.argv[3:])
    else:
        render("short_video.mp4")
        audio("short_audio.wav")
