import cairo, math, os, sys, subprocess, wave, json
import numpy as np
import short as S
F = S.F
from timeline import START

VW, VH, FPS = 1080, 1920, 30
VO = json.load(open("vo.json"))
HOOK = round(VO[-1][2] + 0.45, 2)
H0 = 4.2
CUTS = [("s1", H0, H0 + HOOK, 230), ("s1", H0 + HOOK, H0 + HOOK + 3.0, 230),
        ("s2", 0.6, 4.0, 500), ("s3", 0.8, 4.0, 380), ("s4", 6.0, 10.0, 520),
        ("s5", 1.0, 4.4, 400), ("s5", 8.4, 13.6, 60), ("s6", 1.0, 5.0, 300), ("s6", 8.0, 13.4, 300),
        ("s7", 2.2, 6.6, 440), ("s7", 10.2, 14.6, 150), ("s8", 0.6, 4.6, 320), ("s8", 9.2, 14.2, 320),
        ("s9", 2.6, 8.8, None), ("s10", 0.6, 4.4, 760), ("s10", 7.0, 11.0, 760),
        ("s11", 4.0, 8.4, 800), ("s11", 11.2, 14.4, 800), ("s12", 0.0, 8.5, None)]
CTX = {"hook": False, "t": 0.0}
_orig = F.frame


def _frame(c, name, t):
    _orig(c, name, t)
    m = F.UI.get("meter")
    if m and m[0] == "day":
        F.UI["meter"] = ("try", 0, "NO", 0, 0, t)
    if CTX["hook"]:
        ht = CTX["t"]
        F.UI["caps"] = []
        for s, a, b in VO:
            if a - 0.1 <= ht <= b + 0.15:
                k = F.ease(F.seg(ht, a - 0.1, a + 0.15)) * (1 - F.ease(F.seg(ht, b, b + 0.15)))
                F.UI["caps"].append((s, k, False))
        kc = VO[2][1]
        F.UI["meter"] = ("try", 0, "NO", F.seg(ht, kc, kc + 0.5) if kc <= ht < kc + 0.5 else 0, 0, t)


F.frame = _frame


def tries(c, t):
    c.set_source_rgb(*F.INK)
    c.paint()
    t = t + 2.6
    F.text(c, "THINGS I TRIED", VW / 2, 560, 58, F.CREAM, 0.6)
    for i, s in enumerate(F.TRIES):
        a = 0.5 + i * 0.8
        if t < a:
            continue
        k = F.ease(F.seg(t, a, a + 0.3))
        y = 760 + i * 170
        c.set_source_rgba(1, 1, 1, 0.07 * k)
        F.rrect(c, 60, y - 92, 960, 128, 28)
        c.fill()
        F.text(c, str(i + 1), 120, y, 66, F.AMBER, k)
        xa = 4.0 + i * 0.6
        done = F.seg(t, xa, xa + 0.25)
        wd = F.text(c, s, 180, y, 60, F.CREAM, k * (1 - 0.45 * done), "l")
        if done > 0:
            c.set_source_rgb(*F.CORAL)
            c.set_line_width(7)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(172, y - 21)
            c.line_to(172 + (wd + 16) * done, y - 21)
            c.stroke()
            c.save()
            c.translate(965, y - 21)
            s2 = 1 + 0.5 * math.sin(math.pi * done)
            c.scale(s2, s2)
            c.set_line_width(14)
            c.move_to(-22, -22)
            c.line_to(22, 22)
            c.move_to(22, -22)
            c.line_to(-22, 22)
            c.stroke()
            c.restore()
    a, b = 6.4, 9.7
    if t >= a:
        k = F.ease(F.seg(t, a, a + 0.35))
        F.text(c, "Four things.", VW / 2, 1560, 84, F.CREAM, k)
        F.text(c, "Nothing worked.", VW / 2, 1670, 84, F.CORAL, k)


def ending(c, t):
    D = 8.5
    c.set_source_rgb(*F.INK)
    c.paint()
    F.sprout(c, VW / 2, 560, 95, F.ease(F.seg(t, 0.3, 1.0)))
    a = F.ease(F.seg(t, 0.8, 1.2))
    F.text(c, "Not every day", VW / 2, 900, 90, F.CREAM, a)
    F.text(c, "can be saved.", VW / 2, 1010, 90, F.CREAM, a)
    b = F.ease(F.seg(t, 4.4, 4.8))
    F.text(c, "Some you", VW / 2, 1220, 108, F.AMBER, b)
    F.text(c, "just finish.", VW / 2, 1345, 108, F.AMBER, b)
    F.text(c, "Small Win Films", VW / 2, 1620, 50, F.CREAM, 0.55 * F.ease(F.seg(t, 6.0, 6.8)))
    F.tint(c, (0.03, 0.06, 0.08), max(1 - F.seg(t, 0, 0.3), F.seg(t, D - 1.0, D - 0.05)))


def draw(c, name, t, cx, ht=None):
    CTX["hook"] = ht is not None
    CTX["t"] = ht or 0.0
    if name == "s9":
        tries(c, t - 2.6)
    elif name == "s12":
        ending(c, t)
    else:
        S.vframe(c, name, t, cx)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for j, (name, a, b, cx) in enumerate(CUTS):
        for i in range(int(round((b - a) * FPS))):
            draw(c, name, a + i / FPS, cx, i / FPS if j == 0 else None)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(1)


def audio(out):
    w = wave.open("audio.wav")
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768
    parts = []
    fd = int(0.04 * sr)
    for name, a, b, _ in CUTS:
        i0 = int((START[name] + a) * sr)
        seg = x[i0:i0 + int(round((b - a) * FPS)) * sr // FPS].copy()
        seg[:fd] *= np.linspace(0, 1, fd)[:, None]
        seg[-fd:] *= np.linspace(1, 0, fd)[:, None]
        parts.append(seg)
    y = np.concatenate(parts)
    import soundfile as sf
    v, vsr = sf.read("vo.wav")
    idx = np.arange(int(len(v) * sr / vsr)) * vsr / sr
    v = np.interp(idx, np.arange(len(v)), v)
    n = len(v)
    duck = np.ones(len(y))
    hl = int(HOOK * sr)
    duck[:hl] = 0.10
    r = int(0.4 * sr)
    duck[hl - r:hl] = np.linspace(0.10, 1, r)
    y *= duck[:, None]
    v = np.tanh(v / np.sqrt(np.mean(v[v != 0] ** 2)) * 0.22 * 1.6) / 1.6
    y[:n] += v[:, None]
    f = int(1.0 * sr)
    y[-f:] *= np.linspace(1, 0, f)[:, None]
    y = y / np.max(np.abs(y)) * 0.89
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
        j, t = spec.split("@")
        name, a, b, cx = CUTS[int(j)]
        draw(c, name, a + float(t), cx, float(t) if int(j) == 0 else None)
        surf.write_to_png(os.path.join(outdir, "r%s_%s.png" % (j, t)))


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2], sys.argv[3:])
    else:
        print("total", round(sum(b - a for _, a, b, _ in CUTS), 2))
        render("reel_video.mp4")
        audio("reel_audio.wav")
