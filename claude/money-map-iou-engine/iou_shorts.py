import cairo, json, os, sys, subprocess, math, hashlib
import numpy as np, soundfile as sf
from iou_common import *
from iou_engine import paper_card, treasury_icon, dollar_bill

VW, VH = 1080, 1920
CAP_Y = 1400
GAP, TAIL = 0.35, 2.4

SHORTS = {
    "A": dict(voice="bm_daniel", speed=0.96, vo="vo_sa", lines=[
        ("a_hook", 0, "The biggest foreign lender to America isn't China."),
        ("a_bars", 0, "Japan holds about one point oh six trillion dollars. The U.K., just under one trillion."),
        ("a_bars", 1, "China is third, with about five hundred and sixty-four billion. That's one point four percent of all U.S. debt."),
        ("a_china", 0, "And that's its lowest in more than eighteen years."),
        ("a_home", 0, "So who holds most of it? Americans, and their own government. More than three quarters is held inside the U.S."),
        ("a_end", 0, "Follow the money."),
    ]),
    "B": dict(voice="am_liam", speed=0.96, vo="vo_sb", lines=[
        ("b_hook", 0, "Social Security's savings are government I O Us."),
        ("b_flow", 0, "Payroll taxes come in. Benefits go out. Any extra must be lent to the Treasury."),
        ("b_special", 0, "In return, the fund gets a special government security. An I O U that earns interest."),
        ("b_stack", 0, "Its main retirement fund holds about two point three trillion dollars of them."),
        ("b_cash", 0, "When benefits are paid, it cashes some in, and the Treasury has to find the money, usually by borrowing it from the public."),
        ("b_end", 0, "It's part of the forty trillion dollar debt. Follow the money."),
    ]),
}
CAPS = {
    "A": ["The biggest foreign lender to America isn't China.", "Japan: about $1.06 trillion. The U.K.: just under $1 trillion.",
          "China is third: about $564 billion. That's 1.4% of all U.S. debt.", "And that's its lowest in more than 18 years.",
          "So who holds most of it? Americans, and their own government. More than three quarters is held inside the U.S.", "Follow the money."],
    "B": ["Social Security's savings are government IOUs.", "Payroll taxes come in. Benefits go out. Any extra must be lent to the Treasury.",
          "In return, the fund gets a special government security. An IOU that earns interest.", "Its main retirement fund holds about $2.3 trillion of them.",
          "When benefits are paid, it cashes some in, and the Treasury has to find the money, usually by borrowing it from the public.",
          "It's part of the $40 trillion debt. Follow the money."],
}


def chrome(c):
    logo(c, 40, 34, 0.6)
    txt(c, "MONEY MAP", 94, 76, 42, WHITE, LAB, "l")


# ---------------------------------------------------------------- Short A scenes
def a_hook(c, t, d, T):
    txt(c, "BIGGEST FOREIGN", 540, 330, 150, WHITE, LAB)
    txt(c, "LENDER TO AMERICA?", 540, 470, 150, AMBER, LAB)
    cert(c, 540, 930, 1.45, "CHINA", "$564 BILLION", -0.05, 1.0, 3141592, col=FOREIGN)
    stamp(c, 560, 950, "NOT CHINA", RED, e(T, 1.0, 1.5), 150, -0.2)


def a_bars(c, t, d, T, step):
    txt(c, "LARGEST FOREIGN HOLDERS", 540, 250, 92, WHITE, LAB)
    txt(c, "SEPT 2026, BILLIONS OF DOLLARS", 540, 318, 44, GREY, LAB)
    rows = [("JAPAN", 1063, "$1,063B", 0.10), ("UNITED KINGDOM", 986, "$986B", 0.55), ("CHINA", 564, "$564B", 0.0)]
    for i, (nm, v, lab, f0) in enumerate(rows):
        if i == 2 and step == 0:
            continue
        y = 440 + i * 290
        k = e(t / d, f0, f0 + 0.3) if step == 0 else (1.0 if i < 2 else e(t, 0.2, 1.2))
        txt(c, nm, 70, y + 10, 78, WHITE, LAB, "l", clamp(k * 3))
        rr(c, 70, y + 40, max(6, v * 0.85 * k), 150, 12)
        c.set_source_rgb(*(FOREIGN if i < 2 else (0.96, 0.55, 0.28)))
        c.fill()
        if k > 0.9:
            txt(c, lab, 70 + v * 0.85 - 20, y + 150, 90, WHITE if i < 2 else BLACK, LAB, "r")
    if step == 1:
        k = back(e(t, 1.4, 2.0))
        if k > 0:
            stamp(c, 760, 1230, "1.4% OF ALL U.S. DEBT", RED, e(t, 1.6, 2.1), 78, -0.04)


def a_china(c, t, d, T):
    txt(c, "CHINA'S HOLDINGS", 540, 300, 110, WHITE, LAB)
    k = e(t, 0.3, d * 0.75)
    x0, y0, x1, y1 = 190, 600, 890, 1010
    line(c, [(x0, y0), (lerp(x0, x1, k), lerp(y0, y1, k))], FOREIGN, 20)
    circle(c, x0, y0, 26, WHITE, 1, FOREIGN, 10)
    txt(c, "2013", x0 + 20, y0 - 120, 62, GREY, LAB, "l")
    txt(c, "$1.3 TRILLION", x0 + 20, y0 - 50, 96, WHITE, LAB, "l")
    if k > 0.97:
        circle(c, x1, y1, 26, WHITE, 1, FOREIGN, 10)
        txt(c, "SEPT 2026", x1, y1 + 100, 62, GREY, LAB, "r")
        txt(c, "$564 BILLION", x1, y1 + 180, 96, WHITE, LAB, "r")


def a_home(c, t, d, T):
    txt(c, "WHO HOLDS IT?", 540, 270, 130, WHITE, LAB)
    x, y, w, h = 80, 420, 920, 190
    k = e(t, 0.3, 1.3)
    rr(c, x, y, w * 0.77 * k, h, 12)
    c.set_source_rgb(*OTHER)
    c.fill()
    rr(c, x + w * 0.77 * k + 6, y, max(2, w * 0.23 * k - 6), h, 12)
    c.set_source_rgb(*FOREIGN)
    c.fill()
    kk = e(t, 1.1, 1.6)
    txt(c, "77%", x + w * 0.38, y + 140, 130, BLACK, LAB, "c", kk)
    txt(c, "23%", x + w * 0.885, y + 140, 100, WHITE, LAB, "c", kk)
    txt(c, "INSIDE THE U.S.", x + w * 0.38, y + h + 70, 62, OTHER, LAB, "c", kk)
    txt(c, "ABROAD", x + w * 0.885, y + h + 70, 62, FOREIGN, LAB, "c", kk)
    k2 = e(t, d * 0.45, d * 0.6)
    pos = [(250, 1060), (540, 1060), (830, 1060)]
    for i, (x2, y2) in enumerate(pos):
        kq = back(e(t, d * 0.45 + i * 0.35, d * 0.45 + 0.5 + i * 0.35))
        if kq > 0:
            stack_bottom(c, x2, y2, [7, 5, 9][i], 0.5, "", "", HCOL[[0, 1, 3][i]], clamp(kq), 12, 20 + i, 1.0)
            nm = [("TRUST", "FUNDS"), ("THE", "FED"), ("BANKS, FUNDS", "SAVERS")][i]
            txt(c, nm[0], x2, y2 + 110, 40, HCOL[[0, 1, 3][i]], LAB, "c", clamp(kq))
            txt(c, nm[1], x2, y2 + 154, 40, HCOL[[0, 1, 3][i]], LAB, "c", clamp(kq))


def a_end(c, t, d, T):
    cert(c, 540, 700, 1.3, "CHINA", "1.4%", -0.04, 1.0, 3141592, col=FOREIGN)
    stamp(c, 560, 720, "NOT CHINA", RED, 1.0, 130, -0.2)
    txt(c, "FOLLOW THE MONEY.", 540, 1060, 118, WHITE, LAB, "c", e(t, 0.1, 0.5))
    k = back(e(t, 0.5, 1.0))
    rr(c, 540 - 330, 1130, 660, 100, 50)
    c.set_source_rgba(0.85, 0.16, 0.16, clamp(k))
    c.fill()
    txt(c, "FULL VIDEO: WHO DOES AMERICA OWE?", 540, 1198, 38, WHITE, LAB, "c", clamp(k))


# ---------------------------------------------------------------- Short B scenes
def b_hook(c, t, d, T):
    txt(c, "SOCIAL SECURITY'S", 540, 300, 140, WHITE, LAB)
    txt(c, "SAVINGS ARE", 540, 430, 140, WHITE, LAB)
    brass(c, 140, 520, 800, 520, 18, 14)
    txt(c, "TRUST FUND", 540, 600, 60, AMBER, LAB)
    for i in range(10):
        cert(c, 260 + (i % 5) * 140, 740 + (i // 5) * 150, 0.28, "", "", 0, 1.0, 6000 + i)
    stamp(c, 540, 1220, "GOVERNMENT I.O.U.s", RED, e(T, 0.9, 1.4), 110, -0.05)


def b_flow(c, t, d, T):
    f = t / d
    paper_card(c, 70, 300, 300, 190, e(f, 0, 0.1))
    txt(c, "PAYCHECK", 220, 355, 36, INKG, LAB, "c", e(f, 0, 0.1))
    txt(c, "PAYROLL TAX", 220, 450, 42, RED, LAB, "c", e(f, 0, 0.1))
    arrow(c, 390, 400, 460, 400, WHITE, 8, e(f, 0.05, 0.2))
    brass(c, 470, 290, 330, 220, 14, 12)
    txt(c, "TRUST", 635, 385, 54, AMBER, LAB)
    txt(c, "FUND", 635, 445, 54, AMBER, LAB)
    arrow(c, 820, 400, 900, 400, WHITE, 8, e(f, 0.3, 0.45))
    person(c, 980, 440, 1.5, (0.9, 0.9, 0.85), e(f, 0.3, 0.42))
    txt(c, "BENEFITS", 970, 540, 36, WHITE, LAB, "c", e(f, 0.3, 0.45))
    txt(c, "TAXES IN", 280, 275, 40, WHITE, LAB, "c", e(f, 0.1, 0.25))
    k = e(f, 0.55, 0.78)
    arrow(c, 635, 540, 635, 800, TRUST, 10, k)
    treasury_icon(c, 635, 880, 1.2, WHITE, k)
    txt(c, "THE EXTRA IS LENT", 635, 1080, 70, TRUST, LAB, "c", e(f, 0.6, 0.8))


def b_special(c, t, d, T):
    f = t / d
    treasury_icon(c, 240, 520, 1.3, WHITE)
    brass(c, 600, 380, 380, 260, 14, 12)
    txt(c, "TRUST", 790, 490, 56, AMBER, LAB)
    txt(c, "FUND", 790, 550, 56, AMBER, LAB)
    k = e(f, 0.2, 0.6)
    cert(c, lerp(300, 770, k), lerp(540, 330, k) - math.sin(k * math.pi) * 40, 0.55, "SPECIAL SECURITY", "", 0.08, 1.0, 5001)
    txt(c, "SPECIAL", 540, 860, 130, AMBER, LAB, "c", e(f, 0.4, 0.6))
    txt(c, "GOVERNMENT I.O.U.", 540, 980, 104, WHITE, LAB, "c", e(f, 0.45, 0.65))
    k2 = e(f, 0.7, 0.95)
    txt(c, "+ INTEREST", 540, 1110, 100, OTHER, LAB, "c", k2)


def b_stack(c, t, d, T):
    g = e(t, 0.1, 1.4)
    txt(c, "MAIN RETIREMENT FUND", 540, 280, 100, WHITE, LAB)
    stack_bottom(c, 540, 1230, 14, 1.5, "SOCIAL SECURITY", "", TRUST, 1.0, 17, 4100, g)
    txt(c, "$2.3 TRILLION", 540, 440, 180, AMBER, LAB, "c", e(t, 0.3, 0.9))
    txt(c, "IN I.O.U.s", 540, 530, 84, WHITE, LAB, "c", e(t, 0.5, 1.1))


def b_cash(c, t, d, T):
    f = t / d
    brass(c, 90, 300, 360, 220, 14, 12)
    txt(c, "TRUST FUND", 270, 420, 52, AMBER, LAB)
    treasury_icon(c, 540, 820, 1.3, WHITE)
    person(c, 920, 780, 1.6, (0.9, 0.9, 0.85))
    txt(c, "THE PUBLIC", 920, 880, 40, WHITE, LAB, "c")
    k = e(f, 0.1, 0.35)
    if k < 1:
        cert(c, lerp(270, 520, k), lerp(540, 730, k), 0.34, "", "", 0.1, 1.0, 7001)
    txt(c, "CASHES IN SOME", 270, 600, 56, WHITE, LAB, "c", e(f, 0.1, 0.25))
    k2 = e(f, 0.45, 0.68)
    if 0 < k2 < 1:
        coin(c, lerp(900, 600, k2), 790 - math.sin(k2 * math.pi) * 70, 34)
    txt(c, "TREASURY BORROWS CASH", 540, 1040, 66, AMBER, LAB, "c", e(f, 0.45, 0.62))
    txt(c, "FROM THE PUBLIC", 540, 1110, 66, AMBER, LAB, "c", e(f, 0.5, 0.65))
    k3 = e(f, 0.72, 0.95)
    if 0 < k3 < 1:
        coin(c, lerp(500, 270, k3), lerp(760, 540, k3) - math.sin(k3 * math.pi) * 40, 34)


def b_end(c, t, d, T):
    brass(c, 90, 280, 900, 330, 18, 14)
    txt(c, "NATIONAL DEBT", 540, 380, 52, GREY, LAB)
    txt(c, "$40.7 TRILLION", 540, 540, 150, AMBER, LAB)
    txt(c, "OWED TO TRUST FUNDS, THE FED,", 540, 740, 52, WHITE, LAB, "c", e(t, 0.4, 0.9))
    txt(c, "FOREIGN HOLDERS AND EVERYONE ELSE", 540, 810, 52, WHITE, LAB, "c", e(t, 0.7, 1.2))
    txt(c, "FOLLOW THE MONEY.", 540, 1010, 118, WHITE, LAB, "c", e(t, 1.1, 1.6))
    k = back(e(t, 1.5, 2.0))
    rr(c, 540 - 330, 1090, 660, 100, 50)
    c.set_source_rgba(0.85, 0.16, 0.16, clamp(k))
    c.fill()
    txt(c, "FULL VIDEO: WHO DOES AMERICA OWE?", 540, 1158, 38, WHITE, LAB, "c", clamp(k))


SC = dict(a_hook=a_hook, a_bars=a_bars, a_china=a_china, a_home=a_home, a_end=a_end,
          b_hook=b_hook, b_flow=b_flow, b_special=b_special, b_stack=b_stack, b_cash=b_cash, b_end=b_end)


def wrap(c, s, maxw, size):
    font(c, POP)
    c.set_font_size(size)
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if c.text_extents(t).x_advance > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def caption(c, s, a, y=CAP_Y, size=54):
    ls = wrap(c, s, 960, size)
    lh = size * 1.22
    y0 = y - (len(ls) - 1) * lh / 2
    for i, l in enumerate(ls):
        txt(c, l, VW / 2, y0 + i * lh, size, (1, 1, 1), POP, "c", a, stroke=(0.02, 0.08, 0.06), sw=12)


def timeline(durs):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + GAP + (TAIL if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def frame(name, c, tl, T, cap=True):
    S = SHORTS[name]
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0.0, T - t0)
    sc, step, _ = S["lines"][i]
    draw_wall(c, VW, VH)
    f = SC[sc]
    if sc == "a_bars":
        f(c, t, d, T, step)
    else:
        f(c, t, d, T)
    chrome(c)
    last = i == len(tl) - 1
    if cap and not (last and t > d - TAIL + 0.3):
        caption(c, CAPS[name][i], 1.0 if i == 0 else e(t, 0, 0.12))


def load(name):
    S = SHORTS[name]
    durs = json.load(open(os.path.join(S["vo"], "durs.json")))
    return timeline(durs)


def tts(name):
    from kokoro_onnx import Kokoro
    S = SHORTS[name]
    k = Kokoro("/root/kokoro/kokoro-v1.0.onnx", "/root/kokoro/voices-v1.0.bin")
    os.makedirs(S["vo"], exist_ok=True)
    durs = []
    for i, (_, _, spoken) in enumerate(S["lines"]):
        a, sr = k.create(spoken, voice=S["voice"], speed=S["speed"], lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 300): nz[-1] + 2000]
        sf.write(os.path.join(S["vo"], "%02d.wav" % i), a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open(os.path.join(S["vo"], "durs.json"), "w"))
    print(name, [round(x, 2) for x in durs], round(sum(durs) + GAP * len(durs) + TAIL, 1))


def srt(name, path):
    tl, total = load(name)
    f = lambda s: "%02d:%02d:%02d,%03d" % (s // 3600, s // 60 % 60, int(s) % 60, int((s % 1) * 1000))
    with open(path, "w") as o:
        for i, ((t0, d), cap) in enumerate(zip(tl, CAPS[name])):
            o.write("%d\n%s --> %s\n%s\n\n" % (i + 1, f(t0 + 0.05), f(t0 + d - 0.05 - (TAIL if i == len(tl) - 1 else 0)), cap))


def render(name, out):
    import iou_mix as M
    S = SHORTS[name]
    tl, total = load(name)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "v_%s.tmp.mp4" % name], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        frame(name, c, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    sr = M.SR
    n = int((total + 0.3) * sr)
    mix = np.zeros(n)
    fx = np.zeros(n)

    def put(buf, x, at, g=1.0):
        a = int(at * sr)
        if a < 0 or a >= n:
            return
        b = min(n, a + len(x))
        buf[a:b] += x[:b - a] * g

    put(fx, M.thump(0.6), 0.0)
    for k in range(8):
        put(fx, M.tick(k), 0.05 + k * 0.045)
    for i, (t0, dd) in enumerate(tl):
        a, srr = sf.read(os.path.join(S["vo"], "%02d.wav" % i))
        put(mix, a, t0 + 0.02)
        sc = S["lines"][i][0]
        if i > 0:
            put(fx, M.rustle(i), t0 + 0.03)
        if sc in ("a_hook",):
            put(fx, M.thump(0.7), 1.2)
        if sc == "b_hook":
            put(fx, M.thump(0.7), 1.1)
        if sc == "a_bars":
            for j in range(3):
                put(fx, M.tick(j + 9), t0 + 0.4 + j * 0.5)
        if sc in ("b_cash",):
            put(fx, M.clink(1), t0 + dd * 0.5)
            put(fx, M.clink(2), t0 + dd * 0.8)
        if sc in ("a_end", "b_end"):
            put(fx, M.chime(), t0 + 0.2, 0.9)
    bed = M.pad(total + 0.3)[:n]
    mix = mix + fx * 0.9 + bed
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    sf.write("a_%s.wav" % name, mix.astype(np.float32), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "v_%s.tmp.mp4" % name, "-i", "a_%s.wav" % name, "-af", "loudnorm=I=-15:TP=-1.5", "-ar", "48000",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print("ok", round(total, 2))


def stills(name, outdir="st_short"):
    tl, total = load(name)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    os.makedirs(outdir, exist_ok=True)
    for i, (t0, d) in enumerate(tl):
        for k, off in enumerate((0.05, min(2.0, d - 0.3))):
            frame(name, c, tl, t0 + off)
            surf.write_to_png("%s/%s_%02d_%d.png" % (outdir, name, i, k))


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    {"tts": lambda: tts(name), "stills": lambda: stills(name), "render": lambda: render(name, sys.argv[3]), "srt": lambda: srt(name, sys.argv[3])}[cmd]()
