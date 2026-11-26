import cairo, json, sys, subprocess, numpy as np, soundfile as sf
from film import *
import compose as C
import scenes as S
from audio import OFF

VW, VH = 1080, 1920

SHORT = [("s4", 1.8, 6.8), ("s4", 7.4, 17.0), ("s4", 19.0, 21.8), ("s6", 1.0, 5.5), ("s6", 13.0, 21.2), ("endS", 0, 4.0)]
REEL = [("s0", 0, 5), ("s0b", 0, 2), ("s1", 3.0, 9.4), ("s1", 10.0, 15.6), ("s2", 6.0, 13.0), ("s3", 6.0, 11.4), ("s4", 1.8, 6.8), ("s4", 7.4, 15.5),
        ("s4", 19.0, 22.5), ("s5", 1.0, 6.8), ("s6", 1.0, 5.0), ("s6", 13.0, 24.5), ("s7", 8.6, 14.4), ("endR", 0, 8.4)]


def endv(c, t, kind):
    c.set_source_rgb(*INK)
    c.paint()
    S.sprout(c, VW / 2, 520, 1.5, e(t, 0.2, 0.8))
    if kind == "endS":
        text(c, "Full film on the channel:", VW / 2, 860, 54, CREAM, e(t, 0.2, 0.6))
        text(c, "31 Texts She Never Sent", VW / 2, 960, 66, LAMP, e(t, 0.4, 0.8))
    else:
        text(c, "It still hurts.", VW / 2, 860, 84, CREAM, e(t, 0.2, 0.9))
        text(c, "But tonight,", VW / 2, 1000, 84, LAMP, e(t, 2.0, 2.7))
        text(c, "I didn't write.", VW / 2, 1100, 84, LAMP, e(t, 2.0, 2.7))
        text(c, "Small Win Films", VW / 2, 1280, 40, CREAM, 0.6 * e(t, 4.0, 4.8))


def hook_overlay(c, T):
    if T < 5.0:
        k = 1.0 - e(T, 4.6, 5.0)
        c.set_source_rgba(0, 0, 0, 0.0)


def render(cuts, out, fps=30):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for name, a, b in cuts:
        C.CUT_START = a
        for i in range(int(round((b - a) * fps))):
            t = a + i / fps
            c.set_source_rgb(0, 0, 0)
            c.paint()
            if name.startswith("end"):
                endv(c, t, name)
            else:
                C.frame9(c, name, t)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()


def still(cuts, T, path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    acc = 0
    for name, a, b in cuts:
        if T < acc + (b - a):
            C.CUT_START = a
            t = a + T - acc
            if name.startswith("end"):
                endv(c, t, name)
            else:
                C.frame9(c, name, t)
            break
        acc += b - a
    surf.write_to_png(path)


def audio(cuts, src, out, vo=None):
    a, sr = sf.read(src)
    segs = []
    xf = int(0.12 * sr)
    for name, s0, s1 in cuts:
        if name == "endS":
            st, en = 168.0, 172.0
        elif name == "endR":
            st, en = 160.6, 169.0
        else:
            st, en = OFF[name] + s0, OFF[name] + s1
        seg = a[int(st * sr):int(en * sr)].copy()
        seg[:xf] *= np.linspace(0, 1, xf)[:, None]
        seg[-xf:] *= np.linspace(1, 0, xf)[:, None]
        segs.append(seg)
    mix = np.concatenate(segs)
    if vo:
        v, vsr = sf.read(vo)
        if v.ndim == 1:
            v = np.stack([v, v], 1)
        idx = (np.arange(int(len(v) * sr / vsr)) * vsr / sr).astype(int)
        v = v[idx]
        n = min(len(v) + int(0.3 * sr), len(mix))
        duck = np.ones(len(mix))
        duck[:n] = 0.3
        ramp = int(0.4 * sr)
        duck[n:n + ramp] = np.linspace(0.3, 1, ramp)
        mix = mix * duck[:, None]
        j = int(0.15 * sr)
        mix[j:j + len(v)] += v[:len(mix) - j] * 1.26 * (np.abs(mix).max() / max(1e-9, np.abs(v).max()) * 1.0)
    mix /= max(1e-9, np.abs(mix).max()) / 0.9
    sf.write(out, mix.astype(np.float32), sr)


if __name__ == "__main__":
    which = sys.argv[1]
    cuts = SHORT if which == "short" else REEL
    render(cuts, which + "_v.mp4")
