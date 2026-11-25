import cairo, math, os, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter

VW, VH, FPS = 1080, 1920, 30
GOLD = (0.98, 0.78, 0.20)
WHITE = (1, 1, 1)
SR = 44100


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e(t, a, b):
    x = clamp((t - a) / max(1e-6, b - a))
    return x * x * (3 - 2 * x)


def back(x):
    x = clamp(x)
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(lerp(a, b, k) for a, b in zip(c1, c2))


def font(c, name, bold=True):
    c.select_font_face(name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)


def tw(c, s, size, f, bold=True):
    font(c, f, bold)
    c.set_font_size(size)
    return c.text_extents(s).width


def txt(c, s, x, y, size, col, f, align="c", a=1.0, bold=True, stroke=None, sw=10):
    font(c, f, bold)
    c.set_font_size(size)
    ex = c.text_extents(s)
    if align == "c":
        x -= ex.width / 2 + ex.x_bearing
    elif align == "r":
        x -= ex.width + ex.x_bearing
    c.move_to(x, y)
    if stroke:
        c.text_path(s)
        c.set_source_rgba(*stroke, a)
        c.set_line_width(sw)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgba(*col, a)
        c.fill()
    else:
        c.set_source_rgba(*col, a)
        c.show_text(s)
    c.new_path()
    return ex.width


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def logo(c, x, y, s, a, col=GOLD):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(0, 60), (0, 0), (30, 34), (60, 0), (60, 60)]
    c.set_line_width(12)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(*col, a)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    c.arc(60, 60, 13, 0, 2 * math.pi)
    c.set_source_rgba(0.12, 0.64, 0.36, a)
    c.fill()
    c.restore()


def ring(c, x, y, t, r0=50, r1=170, a0=0.5, w=8, col=(1, 1, 1)):
    if 0 <= t < 0.5:
        p = e(t, 0, 0.5)
        c.arc(x, y, r0 + (r1 - r0) * p, 0, 2 * math.pi)
        c.set_source_rgba(*col, a0 * (1 - p))
        c.set_line_width(w)
        c.stroke()


def money(v, cents=False):
    return ("$%s" % format(v, ",.2f")) if cents else ("$%s" % format(int(round(v)), ","))


def render(draw, dur, out, music_path, tag):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    tmp = tag + "_v.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))):
        c.save()
        draw(c, f / FPS)
        c.restore()
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    assert p.wait() == 0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", music_path, "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    os.remove(tmp)


def still(draw, T, path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    draw(c, T)
    surf.write_to_png(path)


def zones(png, out):
    from PIL import Image, ImageDraw
    im = Image.open(png).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, VW, 270], fill=(255, 0, 0, 90))
    d.rectangle([0, 1536, VW, VH], fill=(255, 0, 0, 90))
    d.rectangle([0, 1344, VW, 1536], fill=(255, 140, 0, 70))
    d.rectangle([VW - 65, 270, VW, 1536], fill=(255, 0, 0, 70))
    d.rectangle([0, 270, 65, 1536], fill=(255, 0, 0, 70))
    d.rectangle([960, 1000, VW - 65, 1344], fill=(255, 140, 0, 60))
    Image.alpha_composite(im, ov).convert("RGB").save(out)


def edge_check(png):
    from PIL import Image
    im = np.asarray(Image.open(png).convert("RGB")).astype(float)
    rows = [im[:6].mean(), im[-6:].mean(), im[:, :6].mean(), im[:, -6:].mean()]
    return [round(r, 1) for r in rows]


class Track:
    def __init__(self, dur, seed=1):
        self.dur = dur
        self.n = int(dur * SR)
        self.tail = 4 * SR
        self.out = np.zeros(self.n + self.tail)
        self.rng = np.random.RandomState(seed)

    def put(self, sig, t0, g=1.0):
        j = int(t0 * SR)
        if j < 0 or j >= len(self.out):
            return
        k = min(len(sig), len(self.out) - j)
        self.out[j:j + k] += sig[:k] * g

    def save(self, path, lp=9500):
        out = self.out.copy()
        out[:self.tail] += out[self.n:self.n + self.tail]
        out = out[:self.n]
        b, a = butter(2, lp / (SR / 2), "low")
        out = lfilter(b, a, out)
        out /= np.abs(out).max() / 0.9
        sf.write(path, out.astype(np.float32), SR)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _x(d):
    return np.arange(int(d * SR)) / SR


def pluck(midi, vel=1.0, d=1.3, bright=1.0):
    x = _x(d)
    f = mtof(midi)
    s = np.zeros(len(x))
    for k in range(1, 7):
        s += (1.0 / k ** (1.15 / bright)) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * x) * np.exp(-x * (3.2 + 2.4 * k))
    return s * np.minimum(1, x / 0.002) * vel * 0.09


def bassn(midi, d, g=0.30):
    x = _x(d + 0.2)
    f = mtof(midi)
    s = np.sin(2 * np.pi * f * x) + 0.45 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 7)
    return s * np.minimum(1, x / 0.004) * np.exp(-x / (d * 0.8)) * g


def marimba(midi, vel=1.0):
    x = _x(0.8)
    f = mtof(midi)
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 8) + 0.3 * np.sin(2 * np.pi * 4 * f * x) * np.exp(-x * 26)
    return s * vel * 0.22


def epiano(midi, vel=1.0, d=1.6):
    x = _x(d)
    f = mtof(midi)
    s = np.sin(2 * np.pi * f * x + 0.6 * np.sin(2 * np.pi * f * x) * np.exp(-x * 3)) * np.exp(-x * 1.6)
    s += 0.25 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 4)
    return s * np.minimum(1, x / 0.004) * vel * 0.07


def pad(midis, d, g=0.05):
    x = _x(d)
    s = np.zeros(len(x))
    for m in midis:
        f = mtof(m)
        for det in (-0.003, 0.003):
            s += np.sin(2 * np.pi * f * (1 + det) * x) + 0.3 * np.sin(2 * np.pi * 2 * f * (1 + det) * x)
    env = np.minimum(1, x / 0.4) * np.minimum(1, (d - x) / 0.4)
    return s * env * g / len(midis)


def bell(f, d=0.7, g=0.1):
    x = _x(d)
    s = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 10) + 0.3 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 20)) * np.exp(-x * 7)
    return s * g


def kick(g=0.6):
    x = _x(0.35)
    return np.sin(2 * np.pi * (46 + 90 * np.exp(-x / 0.035)) * x) * np.exp(-x / 0.11) * g


def noise_hit(rng, d, lo, hi, dec, g):
    m = int(d * SR)
    if hi:
        b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    else:
        b, a = butter(2, lo / (SR / 2), "high")
    return lfilter(b, a, rng.randn(m)) * np.exp(-np.arange(m) / (dec * SR)) * g


def whoosh(rng, d=0.55, g=0.2):
    m = int(d * SR)
    xx = np.arange(m) / SR
    return lfilter(*butter(2, [500 / (SR / 2), 5000 / (SR / 2)], "band"), rng.randn(m)) * np.sin(np.pi * xx / d) ** 2 * g


def riser(rng, d=2.0, g=0.22):
    m = int(d * SR)
    x = np.arange(m) / SR
    return lfilter(*butter(2, [800 / (SR / 2), 6000 / (SR / 2)], "band"), rng.randn(m)) * (x / d) ** 2 * g


def clack(rng, g=0.5):
    m = int(0.09 * SR)
    x = np.arange(m) / SR
    s = noise_hit(rng, 0.09, 1800, 7000, 0.012, 1.0) + 0.6 * np.sin(2 * np.pi * 2400 * x) * np.exp(-x / 0.01)
    return s * g
