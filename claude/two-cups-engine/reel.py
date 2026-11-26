import cairo, math, os, sys, subprocess, wave, json
import numpy as np
import film as F
from timeline import START, TWO_T

VW, VH, FPS = 1080, 1920, 30
YC = 930
VO = json.load(open("vo.json"))
HOOK = round(VO[-1][2] + 0.45, 2)
CUTS = [("cold", 0.0, HOOK, 330, 1100), ("card", 0.0, 2.0, 410, 1100),
        ("day1", 4.0, 7.3, 420, 1100), ("day1", 8.5, 13.0, 860, 1100), ("day1", 13.0, 17.0, 450, 1100),
        ("day1", 17.5, 21.5, 450, 1100), ("days", 0.0, 4.8, 520, 1100),
        ("day8", 0.8, 5.3, 600, 1100), ("day8", 8.5, 15.0, 520, 1100),
        ("day14", 4.0, 8.4, 660, 1100), ("day14", 15.0, 19.7, 590, 1100),
        ("day30", 10.5, 13.5, 620, 1100), ("day40", 0.0, 4.5, 510, 1100), ("day40", 10.0, 13.0, 430, 1100),
        ("day60", 6.0, 9.0, 700, 1100), ("day60", 13.5, 18.5, 580, 1100),
        ("day90", 7.8, 10.4, 420, 1100), ("day90", 12.6, 14.8, 450, 1100), ("day90", 22.6, 29.1, 350, 1100),
        ("end", 0.0, 7.5, 0, 0)]
END_SRC = START["close"]

F.UI_ON = False
src = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080)
sc = cairo.Context(src)


CAL = {"n": None, "prev": None, "tc": -9.0, "dur": 0.45, "cups": 2, "tcup": -9.0}
FX, FY, FW, FH = 40, 520, 1000, 980
INKD = (0.11, 0.13, 0.16)
BIND = F.hx("B4583A")


def reset():
    CAL.update(n=None, prev=None, tc=-9.0, cups=2, tcup=-9.0)


def set_day(n, T, dur=0.45):
    if CAL["n"] is None:
        CAL["n"] = n
    elif n != CAL["n"]:
        CAL["prev"], CAL["n"], CAL["tc"], CAL["dur"] = CAL["n"], n, T, dur


def set_cups(k, T):
    if k != CAL["cups"]:
        CAL["cups"], CAL["tcup"] = k, T


def page(c, x, y, w, h, n, alpha=1.0):
    c.set_source_rgba(0, 0, 0, 0.3 * alpha)
    F.rrect(c, x + 6, y + 10, w, h, 22)
    c.fill()
    c.set_source_rgba(*F.CREAM, alpha)
    F.rrect(c, x, y, w, h, 22)
    c.fill()
    c.set_source_rgba(*BIND, alpha)
    c.save()
    F.rrect(c, x, y, w, h, 22)
    c.clip()
    c.rectangle(x, y, w, 70)
    c.fill()
    c.restore()
    F.text(c, "DAY", x + w / 2, y + 50, 40, F.CREAM, alpha)
    sz = 220 if n < 100 else 170
    F.text(c, str(n), x + w / 2, y + h - 52, sz, F.INK, alpha)
    c.set_source_rgba(0, 0, 0, 0.12 * alpha)
    c.set_line_width(2)
    c.set_dash([6, 6])
    c.move_to(x + 16, y + 74)
    c.line_to(x + w - 16, y + 74)
    c.stroke()
    c.set_dash([])


def calendar(c, T):
    x, y, w, h = 70, 96, 380, 360
    n = CAL["n"] if CAL["n"] is not None else 40
    for k in (2, 1):
        c.set_source_rgba(*F.mix(F.CREAM, F.SLATE_N, 0.25 + 0.2 * k), 1)
        F.rrect(c, x + 4 * k, y + 8 * k, w, h, 22)
        c.fill()
    page(c, x, y, w, h, n)
    u = (T - CAL["tc"]) / CAL["dur"]
    if CAL["prev"] is not None and 0 <= u < 1:
        k = F.ease(u)
        c.save()
        c.translate(x, y + 70)
        c.rotate(-0.55 * k)
        c.translate(-x, -(y + 70) + 260 * k * k)
        page(c, x, y, w, h, CAL["prev"], 1 - k * k)
        c.restore()
    for rx in (x + 90, x + w - 90):
        c.set_source_rgb(*F.STEEL)
        c.arc(rx, y + 4, 13, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(*INKD)
        c.arc(rx, y + 4, 6, 0, 2 * math.pi)
        c.fill()


def tally(c, T, glow_k=0.0):
    F.text(c, "CUPS EVERY MORNING", 770, 488, 34, F.CREAM, 0.75)
    gone = F.ease(F.seg(T, CAL["tcup"], CAL["tcup"] + 0.6)) if CAL["cups"] == 1 else 0.0
    for i, cx in enumerate((660, 880)):
        a = 1.0 - 0.8 * gone if i == 1 else 1.0
        c.push_group()
        F.cup(c, cx, 400, 1.25 + 0.12 * glow_k, T, CAL["cups"] == 2 or i == 0, 0.0, 0.3 + 0.3 * glow_k, 1.1 * i,
              tea=not (i == 1 and gone > 0.5), sa=0.8)
        c.pop_group_to_source()
        c.paint_with_alpha(a)
        if i == 1 and gone > 0:
            c.set_source_rgba(*F.CREAM, 0.6 * gone)
            c.set_line_width(4)
            c.set_dash([10, 8])
            F.rrect(c, cx - 82, 260, 164, 150, 30)
            c.stroke()
            c.set_dash([])


def bg(c):
    F.vgrad(c, 0, 0, VW, VH, F.mix(F.SLATE_N, F.WALL, 0.25), INKD)


def frame_scene(c, x0):
    cw = 1100
    s = FW / cw
    ch = FH / s
    ys = max(0, (1080 - ch) / 2)
    c.set_source_rgba(0, 0, 0, 0.4)
    F.rrect(c, FX + 8, FY + 14, FW, FH, 40)
    c.fill()
    c.save()
    F.rrect(c, FX, FY, FW, FH, 40)
    c.clip()
    c.translate(FX, FY)
    c.scale(s, s)
    c.set_source_surface(src, -x0, -ys)
    c.paint()
    c.restore()
    c.set_source_rgba(*F.CREAM, 0.85)
    c.set_line_width(6)
    F.rrect(c, FX, FY, FW, FH, 40)
    c.stroke()


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


def caps(c, items):
    for s, k, col in items:
        lines = wrap(c, s, 72, 960)
        y = 1680 - (len(lines) - 1) * 44
        for i, ln in enumerate(lines):
            yy = y + i * 88
            F.text(c, ln, VW / 2 + 3, yy + 6, 72, (0, 0, 0), 0.5 * k)
            F.text(c, ln, VW / 2, yy, 72, col, k)


def hook_caps(T):
    out = []
    for s, a, b in VO:
        if a - 0.1 <= T <= b + 0.15:
            out.append((s, F.ease(F.seg(T, a - 0.1, a + 0.15)) * (1 - F.ease(F.seg(T, b, b + 0.15))), F.CREAM))
    return out


def ending(c, t, T):
    D = 7.5
    bg(c)
    calendar(c, T)
    tally(c, T)
    c.set_source_rgb(*F.SLATE_N)
    F.rrect(c, FX, FY, FW, FH, 40)
    c.fill()
    c.set_source_rgba(*F.CREAM, 0.85)
    c.set_line_width(6)
    F.rrect(c, FX, FY, FW, FH, 40)
    c.stroke()
    F.glow(c, VW / 2, FY + FH / 2, 520, 0.08, F.YEL)
    a = F.ease(F.seg(t, 0.4, 1.0))
    F.text(c, "You don't stop", VW / 2, FY + 330, 88, F.CREAM, a)
    F.text(c, "missing them.", VW / 2, FY + 440, 88, F.CREAM, a)
    b = F.ease(F.seg(t, 2.9, 3.5))
    F.text(c, "You learn to", VW / 2, FY + 620, 98, F.YEL, b)
    F.text(c, "sit with it.", VW / 2, FY + 735, 98, F.YEL, b)
    k = F.ease(F.seg(t, 4.6, 5.3))
    F.sprout(c, 380, 1700, 46, k)
    F.text(c, "Small Win Films", 450, 1716, 46, F.CREAM, 0.7 * k, "l")
    F.tint(c, (0.03, 0.04, 0.06), max(1 - F.seg(t, 0, 0.3), F.seg(t, D - 1.0, D - 0.05)))


def draw(c, cut, t, T, hook_t=None):
    name, a, b, x0, cw = cut
    if name == "end":
        set_day(90, T)
        ending(c, t, T)
        return
    F.scene_frame(sc, name, t)
    if name == "card":
        set_day(max(1, int(round(F.lerp(40, 1, F.ease(F.seg(t - a, 0.0, 1.6)))))), T, 0.1)
    elif "tag" in F.UI:
        set_day(int(F.UI["tag"][0].split()[1]), T)
    if "meter" in F.UI:
        set_cups(F.UI["meter"][0], T)
    bg(c)
    gk = F.pulse(hook_t, 1.9, 0.6) if hook_t is not None else 0.0
    calendar(c, T)
    tally(c, T, gk)
    frame_scene(c, x0)
    caps(c, hook_caps(hook_t) if hook_t is not None else F.UI.get("caps", []))


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = F.ff_writer(out, VW, VH)
    reset()
    T = 0.0
    for j, cut in enumerate(CUTS):
        a, b = cut[1], cut[2]
        for i in range(int(round((b - a) * FPS))):
            draw(c, cut, a + i / FPS, T, i / FPS if j == 0 else None)
            T += 1 / FPS
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
    for name, a, b, _, _ in CUTS:
        base = END_SRC if name == "end" else START[name]
        n = int(round((b - a) * FPS)) * sr // FPS
        i0 = int((base + a) * sr)
        seg = x[i0:i0 + n].copy()
        if len(seg) < n:
            seg = np.vstack([seg, np.zeros((n - len(seg), 2))])
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
    duck[:hl] = 0.14
    r = int(0.5 * sr)
    duck[hl - r:hl] = np.linspace(0.14, 1, r)
    y *= duck[:, None]
    v = np.tanh(v / np.sqrt(np.mean(v[v != 0] ** 2)) * 0.22 * 1.6) / 1.6
    y[:n] += v[:, None]
    f = int(1.2 * sr)
    y[-f:] *= np.linspace(1, 0, f)[:, None]
    y = y / np.max(np.abs(y)) * 0.89
    o = wave.open(out, "wb")
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(sr)
    o.writeframes((y * 32767).astype(np.int16).tobytes())
    o.close()


def find(T):
    acc = 0.0
    for j, cut in enumerate(CUTS):
        d = cut[2] - cut[1]
        if T < acc + d:
            return j, cut, T - acc
        acc += d
    return len(CUTS) - 1, CUTS[-1], CUTS[-1][2] - CUTS[-1][1] - 0.01


def stills(outdir, times):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for T in times:
        j, cut, u = find(float(T))
        reset()
        draw(c, cut, cut[1] + u, float(T), u if j == 0 else None)
        surf.write_to_png(os.path.join(outdir, "r_%05.1f.png" % float(T)))


def sheet(path, times, cols=6):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    rows = (len(times) + cols - 1) // cols
    sh = cairo.ImageSurface(cairo.FORMAT_RGB24, 270 * cols, 480 * rows)
    s2 = cairo.Context(sh)
    for i, T in enumerate(times):
        j, cut, u = find(float(T))
        reset()
        draw(c, cut, cut[1] + u, float(T), u if j == 0 else None)
        surf.flush()
        s2.save()
        s2.translate((i % cols) * 270, (i // cols) * 480)
        s2.scale(0.25, 0.25)
        s2.set_source_surface(surf, 0, 0)
        s2.paint()
        s2.restore()
        F.text(s2, "%.1f" % float(T), (i % cols) * 270 + 40, (i // cols) * 480 + 30, 22, F.YEL)
    sh.write_to_png(path)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "sheet":
        sheet(sys.argv[2], sys.argv[3:])
    else:
        print("total", round(sum(b - a for _, a, b, _, _ in CUTS), 2))
        render("reel_video.mp4")
        audio("reel_audio.wav")
