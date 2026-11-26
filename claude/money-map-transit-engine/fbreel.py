import cairo, math, json, os, sys, subprocess
import numpy as np, soundfile as sf
import shorts as SH
import engine as E
from engine import txt, tw, rr, e, lerp, coin, stamp, token, card, logo, flap

VW, VH, FPS = 1080, 1920, 30
VOICE, SPEED = "am_fenrir", 0.95
LINES = [
    ("hook", "Bitcoin just lost more than a trillion dollars. So where did the money go?"),
    ("drop", "In October 2025, one bitcoin cost about $126,000. This month it touched $62,000."),
    ("say1", "First: most of that trillion was never cash."),
    ("coins", "Ten coins, last price $100: that's $1,000. One sells for $50, and now every coin is worth $50."),
    ("coins2", "Five hundred dollars gone, but only fifty dollars changed hands. Market value is just the last price, times every coin."),
    ("etf", "Second: real dollars went to the people who sold first. Investors pulled about $1.91 billion out of US bitcoin funds in seven trading days."),
    ("lev", "Third: forced sellers. Borrow $9,000 to bet $10,000, and a ten percent drop wipes out your own $1,000. The exchange sells automatically."),
    ("split", "Over one weekend, more than two billion dollars of bets were closed that way. The money went to traders on the other side, and to exchange fees."),
    ("stable", "Exchanges also earn a fee on every panic trade. And about $14.2 billion of stablecoins left crypto in a single month."),
    ("end", "So most of the trillion was a number. The real money went to a few very specific places. Not advice. Just follow the money."),
]


def hook(c, T):
    card(c, 80, 420, 920, 640, E.BOARD)
    txt(c, "ALL BITCOIN IN THE WORLD", 540, 520, 46, (0.6, 0.65, 0.72), align="c")
    if T < 1.0:
        txt(c, "$2.5T", 540, 760, 220, E.AMBERT, align="c")
    else:
        w = tw(c, "$1.23T", 220)
        flap(c, "$1.23T", 540 - w / 2, 760, 220, E.AMBERT, (T - 1.0) * 1.2, seed=3)
    txt(c, "−$1.2 TRILLION", 540, 930, 100, E.RED, align="c", alpha=e(T, 1.6, 2.0))
    stamp(c, 540, 1180, "WHO GOT IT?", E.RED, 1.0, 86, -0.06)


def drop(c, t):
    x0, y0, x1, y1 = 260, 430, 820, 1020
    E.station(c, x0, y0, 34, E.RED, (1, 1, 1), 12)
    txt(c, "OCT 2025", x0, y0 - 120, 44, E.INK2, align="c")
    txt(c, "$126,000", x0 + 40, y0 - 60, 80, E.INK, align="c")
    k = e(t, 0.2, 1.6)
    c.set_source_rgb(*E.RED)
    c.set_line_width(30)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x0, y0)
    c.line_to(lerp(x0, x1, k), lerp(y0, y1, k))
    c.stroke()
    E.station(c, x0, y0, 34, E.RED, (1, 1, 1), 12)
    if k >= 1:
        E.station(c, x1, y1, 34, E.RED, (1, 1, 1), 12)
        txt(c, "NOV 2026", x1 - 40, y1 + 100, 44, E.INK2, align="c")
        txt(c, "$62,000", x1 - 60, y1 + 170, 80, E.INK, align="c")
        stamp(c, 700, 620, "−51%", E.RED, e(t, 1.7, 2.1), 110)


def bigcard(c, t, num, sub1, sub2, col=E.RED):
    card(c, 80, 470, 920, 560, E.BOARD)
    w = tw(c, num, 150)
    flap(c, num, 540 - w / 2, 760, 150, col, t)
    txt(c, sub1, 540, 870, 50, (1, 1, 1), align="c", alpha=e(t, 0.6, 1.0))
    txt(c, sub2, 540, 940, 42, (0.7, 0.75, 0.82), align="c", alpha=e(t, 0.8, 1.2))


def draw(c, tl, T):
    i = 0
    while i + 1 < len(tl) and T >= tl[i + 1][0]:
        i += 1
    t0, d = tl[i]
    t = max(0, T - t0)
    sc, line = LINES[i]
    SH.bg(c)
    if sc == "hook":
        hook(c, T)
    elif sc == "drop":
        drop(c, t)
    elif sc == "say1":
        txt(c, "1. NEVER CASH", 540, 760, 120, E.INK, align="c")
        txt(c, "A PRICE ON A SCREEN", 540, 880, 64, E.RED, align="c", alpha=e(t, 0.5, 1.0))
    elif sc == "coins":
        step = 1 if t < 2.6 else (2 if t < 4.4 else 3)
        SH.coins_v(c, t - (0 if step == 1 else 2.6 if step == 2 else 4.4), step)
    elif sc == "coins2":
        SH.coins_v(c, t, 4)
    elif sc == "etf":
        txt(c, "2. EARLY SELLERS", 540, 380, 90, E.INK, align="c")
        bigcard(c, t, "$1.91B", "OUT OF US BITCOIN FUNDS", "7 TRADING DAYS, NOV 5 TO 13", E.RED)
    elif sc == "lev":
        txt(c, "3. FORCED SELLERS", 540, 300, 90, E.INK, align="c")
        step = 1 if t < 2.2 else (2 if t < 4.0 else 4)
        SH.lev_v(c, t - (0 if step == 1 else 2.2 if step == 2 else 4.0), step)
    elif sc == "split":
        SH.split_v(c, t)
        txt(c, "$2B+ IN ONE WEEKEND", 540, 300, 80, E.RED, align="c")
    elif sc == "stable":
        txt(c, "4. PAID EITHER WAY", 540, 380, 90, E.INK, align="c")
        bigcard(c, t, "−$14.2B", "STABLECOINS LEFT CRYPTO", "IN 30 DAYS", E.RED)
    elif sc == "end":
        card(c, 90, 430, 900, 640, E.BOARD)
        txt(c, "MOSTLY A NUMBER.", 540, 600, 96, (1, 1, 1), align="c")
        txt(c, "THE REAL MONEY WENT", 540, 720, 64, E.AMBERT, align="c")
        txt(c, "TO A FEW PLACES.", 540, 800, 64, E.AMBERT, align="c")
        logo(c, 480, 870, 2.0, e(t, 3.0, 3.6))
        txt(c, "FOLLOW THE MONEY.", 540, 1035, 56, E.GOLD, align="c", alpha=e(t, 3.4, 4.0))
    SH.capt(c, line, 1.0 if i == 0 else e(t, 0, 0.2))
    txt(c, "Not financial advice. Sources in the caption.", 540, VH - 70, 28, E.INK2, font=E.BODY, align="c", bold=False)


def build(durs, gap=0.32):
    tl, t = [], 0.0
    for i, d in enumerate(durs):
        dd = d + gap + (1.6 if i == len(durs) - 1 else 0)
        tl.append((t, dd))
        t += dd
    return tl, t


def tts():
    from kokoro_onnx import Kokoro
    k = Kokoro('/root/kokoro/kokoro-v1.0.onnx', '/root/kokoro/voices-v1.0.bin')
    os.makedirs("fbvo", exist_ok=True)
    durs = []
    for i, (_, line) in enumerate(LINES):
        a, sr = k.create(line, voice=VOICE, speed=SPEED, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, nz[0] - 600): nz[-1] + 2400]
        sf.write("fbvo/%02d.wav" % i, a, sr)
        durs.append(len(a) / sr)
    json.dump(durs, open("fbvo/durs.json", "w"))
    print("speech", sum(durs))


def render(out, a=None, b=None, part="v"):
    durs = json.load(open("fbvo/durs.json"))
    tl, total = build(durs)
    n = int(total * FPS)
    a = 0 if a is None else int(a)
    b = n if b is None else min(n, int(b))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (VW, VH), "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b):
        draw(c, tl, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()


def audio(out):
    durs = json.load(open("fbvo/durs.json"))
    tl, total = build(durs)
    sr = 24000
    n = int((total + 0.3) * sr)
    mix = np.zeros(n)
    tt = np.arange(n) / sr
    for f, amp in ((110.0, 1), (164.8, 0.7), (220.0, 0.5)):
        mix += 0.010 * amp * np.sin(2 * np.pi * f * tt)
    for i, (t0, d) in enumerate(tl):
        x, _ = sf.read("fbvo/%02d.wav" % i)
        j = int((t0 + 0.05) * sr)
        mix[j:j + len(x)] += x[:n - j]
    m = int(0.35 * sr)
    k = np.arange(m) / sr
    mix[:m] += 0.5 * np.sin(2 * np.pi * (70 - 40 * k) * k) * np.exp(-k * 12)
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    sf.write(out, mix.astype(np.float32), sr)
    print("total", total)


def stills():
    durs = json.load(open("fbvo/durs.json"))
    tl, total = build(durs)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(surf)
    for i, (t0, d) in enumerate(tl):
        draw(c, tl, 0.02 if i == 0 else t0 + min(3.0, d - 0.1))
        surf.write_to_png("fb_%02d.png" % i)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "tts":
        tts()
    elif cmd == "stills":
        stills()
    elif cmd == "render":
        render(sys.argv[2], *(sys.argv[3:5]))
    elif cmd == "audio":
        audio(sys.argv[2])
