import cairo, json, os, sys, subprocess
import numpy as np, soundfile as sf
from wx_common import *

GAP, TAIL = 0.4, 2.1


def timeline(durs):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + GAP + (TAIL if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def load(EP):
    durs = json.load(open(os.path.join(EP.VODIR, "durs.json")))
    return timeline(durs)


def caption(c, s, a, y, size=62):
    ls = wrap(c, s, 900, size, CAPF)
    lh = size * 1.22
    y0 = y - (len(ls) - 1) * lh / 2
    for i, l in enumerate(ls):
        txt(c, l, VW / 2, y0 + i * lh, size, (1, 1, 1), CAPF, "c", a, stroke=(0.01, 0.05, 0.16), sw=14)


def frame(EP, c, tl, T, cap=True):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0.0, T - t0)
    name, _, capt = EP.LINES[i]
    EP.bg(c, T)
    EP.draw(c, name, t, d, T, i)
    last = i == len(tl) - 1
    if cap and not (last and t > d - TAIL):
        caption(c, capt, 1.0 if i == 0 else e(t, 0, 0.15), EP.CAP_Y)


def tts(EP):
    from kokoro_onnx import Kokoro
    k = Kokoro("/root/kokoro/kokoro-v1.0.onnx", "/root/kokoro/voices-v1.0.bin")
    os.makedirs(EP.VODIR, exist_ok=True)
    durs = []
    for i, (_, spoken, _) in enumerate(EP.LINES):
        a, sr = k.create(spoken, voice=EP.VOICE, speed=EP.SPEED, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 300): nz[-1] + 2000]
        sf.write(os.path.join(EP.VODIR, "%02d.wav" % i), a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open(os.path.join(EP.VODIR, "durs.json"), "w"))
    print([round(x, 2) for x in durs], round(sum(durs), 2))


def srt(EP, path):
    tl, total = load(EP)
    f = lambda s: "%02d:%02d:%02d,%03d" % (s // 3600, s // 60 % 60, int(s) % 60, int((s % 1) * 1000))
    with open(path, "w") as o:
        for i, ((t0, d), (_, _, capt)) in enumerate(zip(tl, EP.LINES)):
            o.write("%d\n%s --> %s\n%s\n\n" % (i + 1, f(t0 + 0.05), f(t0 + d - 0.05 - (TAIL if i == len(tl) - 1 else 0)), capt))


def render(EP, out):
    tl, total = load(EP)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "v.tmp.mp4"], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        frame(EP, c, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    sr = 24000
    n = int((total + 0.3) * sr)
    mix = np.zeros(n)
    tt = np.arange(n) / sr
    for fr, amp in EP.PAD:
        mix += 0.011 * amp * np.sin(2 * np.pi * fr * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * tt / 6))
    rng = np.random.RandomState(5)
    for i, (t0, dd) in enumerate(tl):
        a, _ = sf.read(os.path.join(EP.VODIR, "%02d.wav" % i))
        j = int((t0 + 0.02) * sr)
        mix[j:j + len(a)] += a[:n - j]
    EP.sfx(tl, mix, sr, rng)
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    sf.write("a.wav", mix.astype(np.float32), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "v.tmp.mp4", "-i", "a.wav", "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"], check=True)
    os.rename(out + ".tmp.mp4", out)
    print("ok", round(total, 2))


def stills(EP):
    tl, total = load(EP)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, (t0, d) in enumerate(tl):
        for k, off in enumerate((0.02, min(2.0, d - 0.3))):
            frame(EP, c, tl, t0 + off)
            surf.write_to_png("st_%02d_%d.png" % (i, k))
    frame(EP, c, tl, total - 0.4)
    surf.write_to_png("st_end.png")
    for s in range(15):
        frame(EP, c, tl, s + 0.02)
        surf.write_to_png("hs_%02d.png" % s)


def cover(EP, path):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    EP.cover(c)
    surf.write_to_png(path)


def main(EP):
    cmd = sys.argv[1]
    {"tts": lambda: tts(EP), "stills": lambda: stills(EP), "render": lambda: render(EP, sys.argv[2]),
     "cover": lambda: cover(EP, sys.argv[2]), "srt": lambda: srt(EP, sys.argv[2])}[cmd]()
