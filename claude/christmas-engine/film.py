import cairo, sys, os, subprocess, math
from xm import *
import xm

CAB = dict(show_win=True)


def sprout_card(c, a=1.0, lines=None, t=0.0, title=True):
    c.set_source_rgb(0.07, 0.15, 0.12)
    c.paint()
    cx, cy = W / 2, 400
    c.set_source_rgba(0.93, 0.70, 0.25, a)
    c.arc(cx, cy + 30, 120, math.pi, 2 * math.pi)
    c.fill()
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(7):
        ang = math.pi + (i + 0.5) * math.pi / 7
        c.move_to(cx + 140 * math.cos(ang), cy + 30 + 140 * math.sin(ang))
        c.line_to(cx + 195 * math.cos(ang), cy + 30 + 195 * math.sin(ang))
        c.stroke()
    c.set_source_rgba(0.97, 0.93, 0.82, a)
    c.rectangle(cx - 260, cy + 30, 520, 12)
    c.fill()
    c.set_source_rgba(0.40, 0.75, 0.38, a)
    c.set_line_width(14)
    c.move_to(cx, cy + 30)
    c.curve_to(cx, cy - 10, cx + 4, cy - 30, cx + 2, cy - 55)
    c.stroke()
    for sg in (-1, 1):
        c.new_path()
        c.move_to(cx + 2, cy - 40)
        c.curve_to(cx + sg * 30, cy - 100, cx + sg * 90, cy - 90, cx + sg * 92, cy - 70)
        c.curve_to(cx + sg * 70, cy - 30, cx + sg * 30, cy - 30, cx + 2, cy - 40)
        c.fill()
    if title:
        text(c, "Small Win Films", cx, 640, 100, (0.97, 0.93, 0.82), a)
    if lines:
        yy = 760
        for i, ln in enumerate(lines):
            text(c, ln, cx, yy + i * 80, 58 if i == 0 else 52, GOLD if i == 0 else (0.85, 0.9, 0.85), a)


def hud_state(T, year, knocked, big=None):
    return dict(year=year, knocked=knocked, big=big)


def S(t0, t1, fn):
    return (t0, t1, fn)


def s_open(c, T):
    tl = T
    xm.cabin(c, T, look=1.0, hand_k=0.15 + 0.05 * math.sin(T * 2.2), mood="sad")
    return dict(caps=[("Three Christmases. I never knocked.", 0.1, 3.9)], hud=(4, 0), zero=True)


def s_card1(c, T):
    xm.card(c, "Three years earlier.", e(T, 4.0, 4.4))
    return dict(card=True)


def s_wedding(c, T):
    xm.wedding(c, T)
    return dict(caps=[("He missed my wedding.", 7.3, 11.8)])


def s_phone(c, T):
    tl = T - 12
    xm.phone_close(c, T, e(tl, 1.8, 3.6))
    return dict(caps=[("I stopped answering.", 12.4, 16.8)])


def s_y1_drive(c, T):
    tl = T - 17
    cx = lerp(-380, 760, e(tl, 0.2, 5.2))
    xm.street(c, T, "tree", car_x=cx, brake=tl > 3.5)
    return dict(caps=[("Christmas Eve.", 17.3, 20.5)], hud=(1, 0))


def s_y1_park(c, T):
    tl = T - 24
    z = lerp(1.0, 2.3, e(tl, 3.0, 7.0))
    cx = lerp(W / 2, 1180, e(tl, 3.0, 7.0))
    cy = lerp(H / 2, 500, e(tl, 3.0, 7.0))
    xm.street(c, T, "tree", car_x=760, cam=(z, cx, cy))
    return dict(hud=(1, 0))


def s_y1_leave(c, T):
    tl = T - 31
    if tl < 3.2:
        hk = e(tl, 0.4, 1.6) * (1 - e(tl, 2.0, 2.9))
        xm.cabin(c, T, look=1.0, hand_state="reach", hand_k=hk, mood="worry", tear=0.2)
    else:
        k = e(tl, 3.2, 6.9)
        xm.street(c, T, "tree", car_x=lerp(760, 2500, k * k), brake=False)
    return dict(hud=(1, 0))


def s_y2(c, T):
    tl = T - 38
    z = lerp(1.0, 2.2, e(tl, 2.5, 9.0))
    cx = lerp(W / 2, 1180, e(tl, 2.5, 9.0))
    cy = lerp(H / 2, 500, e(tl, 2.5, 9.0))
    xm.street(c, T, "takeaway", car_x=760, cam=(z, cx, cy), snow_a=1.0)
    return dict(caps=[("Year two.", 38.3, 41.5)], hud=(2, 0))


def s_y2b(c, T):
    tl = T - 47
    if tl < 4.6:
        hk = e(tl, 0.5, 3.0) * (1 - e(tl, 3.4, 4.4))
        xm.cabin(c, T, look=1.0, hand_state="reach", hand_k=hk, mood="worry", gifts=2, win="takeaway", tear=0.15)
    else:
        k = e(tl, 4.6, 8.8)
        xm.street(c, T, "takeaway", car_x=lerp(760, 2500, k * k), brake=False)
    return dict(hud=(2, 0))


def s_cup2(c, T):
    tl = T - 56
    n_static = 1
    xm.apartment(c, T, n_static, new_gift=e(tl, 1.2, 4.6), maya_x=520, carry=0)
    return dict(caps=[("I kept buying them.", 59.0, 64.4)])


def s_y3(c, T):
    tl = T - 65
    if tl < 4.2:
        rn = 1 - e(tl, 0.5, 3.6)
        xm.cabin(c, T, look=1.0, wiper=True, rainy=rn, gifts=3, win="phone", mood="sad")
    else:
        z = lerp(1.0, 2.2, e(tl, 4.6, 8.8))
        cx = lerp(W / 2, 1180, e(tl, 4.6, 8.8))
        cy = lerp(H / 2, 500, e(tl, 4.6, 8.8))
        xm.street(c, T, "phone", car_x=760, cam=(z, cx, cy))
    return dict(caps=[("Year three.", 65.3, 68.6)], hud=(3, 0))


def s_y3wait(c, T):
    tl = T - 74
    xm.cabin(c, T, look=1.0, gifts=3, win="phone", mood="sad", tear=e(tl, 3, 9), phone_dash=True, dash_phone_lit=0.0, wiper=False)
    return dict(hud=(3, 0))


def s_y3leave(c, T):
    tl = T - 84
    if tl < 3.5:
        k = e(tl, 0.0, 3.4)
        xm.street(c, T, "phone", car_x=lerp(760, 2500, k * k), brake=False)
    else:
        xm.apartment(c, T, 3, maya_x=470)
    return dict(hud=(3, 0))


def s_y4load(c, T):
    tl = T - 92
    if tl < 5.5:
        n = 3 if tl < 1.0 else (2 if tl < 1.8 else (1 if tl < 2.6 else 0))
        carry = 0 if tl < 1.0 else (1 if tl < 1.8 else (2 if tl < 2.6 else (3 if tl < 3.6 else 4)))
        xm.apartment(c, T, n, maya_x=lerp(560, 1050, e(tl, 3.8, 5.4)), carry=carry)
    else:
        k = e(tl, 5.5, 9.4)
        xm.street(c, T, "tree", car_x=lerp(-380, 760, k), brake=tl > 8.2)
    return dict(caps=[("Year four.", 92.3, 95.6)], hud=(4, 0))


def s_y4wait(c, T):
    tl = T - 102
    xm.cabin(c, T, look=1.0, gifts=4, win="tree", mood="worry", hand_k=0.1, tear=0.0)
    return dict(hud=(4, 0))


def s_walk(c, T):
    tl = T - 110
    mx = lerp(260, 760, e(tl, 0.5, 6.8))
    wk = None if tl > 6.9 else tl * 5.5
    xm.front(c, T, door=0.0, maya_x=(mx, 990, 0.9), gifts_in_arms=4, walk=wk)
    return dict(hud=(4, 0))


def s_knock(c, T):
    tl = T - 118
    xm.door_knock(c, tl)
    return dict(hud=(4, 1 if tl > 3.2 else 0), big=(e(tl, 2.9, 3.3) * (1 - e(tl, 5.0, 6.2)) if tl > 2.9 else 0, 1))


def s_open_door(c, T):
    tl = T - 125
    k = e(tl, 0.2, 1.8)
    zk = e(tl, 0, 7)
    xm.front(c, T, door=k, maya_x=(760, 990, 0.9), gifts_in_arms=4, dan=dict(x=990, y=900, s=0.62, arms="keys", keys=True, look=-0.6, gift=True) if k > 0.5 else None,
             zoom=(lerp(1.0, 1.3, zk), lerp(W / 2, 900, zk), lerp(H / 2, 600, zk)))
    return dict(hud=(4, 1))


def s_stare(c, T):
    tl = T - 132
    xm.stare(c, T, keys_k=e(tl, 0.8, 1.8))
    return dict(caps=[("I was driving to you.", 133.2, 139.6)], hud=(4, 1))


def s_wide(c, T):
    tl = T - 140
    xm.front(c, T, door=1.0, maya_x=(760, 990, 0.9), gifts_in_arms=4, dan=dict(x=990, y=900, s=0.62, arms="gift", look=-0.6, mood="joy", gift=False))
    return dict(caps=[("He'd waited by the phone every Christmas too.", 140.4, 149.4)], hud=(4, 1))


def s_inside_door(c, T):
    tl = T - 150
    g = 4 if tl < 3.0 else (2 if tl < 3.6 else 0)
    mx = lerp(760, 880, e(tl, 3.6, 6.0))
    zk = 1.4
    xm.front(c, T, door=1.0, maya_x=(mx, 990, 0.9), gifts_in_arms=g, dan=dict(x=990, y=900, s=0.62, arms="gift" if g else None, look=-0.6, mood="joy", mouth=0.6 * (0.5 + 0.5 * math.sin(T * 9))), maya_look=1.0, mood_m="joy", tear=0.8, back=False,
             zoom=(1.3, 900, 650))
    return dict(caps=[("Neither of us went first.", 150.5, 158.8)], hud=(4, 1))


def s_inside(c, T):
    xm.inside(c, T)
    return dict(caps=[("This year, someone did.", 160.5, 168.8)], hud=(4, 1))


def s_end(c, T):
    tl = T - 170
    sprout_card(c, 1.0, ["Next: the bus stop. 60 days. 0 words."], tl)
    return dict(card=True)


SCENES = [
    S(0, 4, s_open), S(4, 7, s_card1), S(7, 12, s_wedding), S(12, 17, s_phone), S(17, 24, s_y1_drive), S(24, 31, s_y1_park),
    S(31, 38, s_y1_leave), S(38, 47, s_y2), S(47, 56, s_y2b), S(56, 65, s_cup2), S(65, 74, s_y3), S(74, 84, s_y3wait),
    S(84, 92, s_y3leave), S(92, 102, s_y4load), S(102, 110, s_y4wait), S(110, 118, s_walk), S(118, 125, s_knock),
    S(125, 132, s_open_door), S(132, 140, s_stare), S(140, 150, s_wide), S(150, 160, s_inside_door), S(160, 170, s_inside), S(170, 180, s_end),
]


def draw_hud(c, T, year, knocked):
    a = 1.0
    if T < 3.6:
        a = e(T, 2.4, 3.6)
    if a > 0.01:
        x, y, w, h = 1380, 46, 480, 128
        c.set_source_rgba(0.03, 0.06, 0.07, 0.86 * a)
        rr(c, x, y, w, h, 20)
        c.fill()
        c.set_source_rgba(*GREEN, 0.55 * a)
        c.set_line_width(3)
        rr(c, x, y, w, h, 20)
        c.stroke()
        text(c, "CHRISTMAS EVE: YEAR %d" % year, x + 24, y + 48, 30, GREEN, a, "l", MONO)
        text(c, "KNOCKED: %d" % knocked, x + 24, y + 100, 40, GREEN, a, "l", MONO)


def draw_zero(c, T, n=0, a=1.0):
    c.set_source_rgba(0.02, 0.05, 0.06, 0.55 * a)
    rr(c, 1180, 190, 640, 700, 40)
    c.fill()
    glow(c, 1500, 540, 440, 0.25 * a, GREEN)
    text(c, str(n), 1500, 700, 600, GREEN, a, "c", MONO)
    text(c, "KNOCKED", 1500, 800, 70, GREEN, a, "c", MONO)


def frame(c, T):
    for t0, t1, fn in SCENES:
        if t0 <= T < t1 or (T >= 180 and t1 == 180):
            break
    st = fn(c, T)
    if st.get("card"):
        return st
    g = cairo.LinearGradient(0, H - 300, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    c.set_source(g)
    c.rectangle(0, H - 300, W, 300)
    c.fill()
    if st.get("hud"):
        draw_hud(c, T, *st["hud"])
    if st.get("zero"):
        a = 1 - e(T, 2.0, 3.2)
        if a > 0.01:
            draw_zero(c, T, 0, a)
    if st.get("big"):
        a, n = st["big"]
        if a > 0.01:
            draw_zero(c, T, n, a)
    for s, a, b in st.get("caps", []):
        if a <= T <= b:
            k = e(T, a, a + 0.3) * (1 - e(T, b - 0.3, b))
            caption(c, s, k, W / 2, H - 82, 76, 1560)
    return st


def pipe(out, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", "%dx%d" % (w, h), "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)


def render(t0, t1, out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    p = pipe(out, W, H)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for i in range(n0, n1):
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame(c, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    print("done", out, flush=True)


def stills(times, outdir):
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    for T in times:
        c.set_source_rgb(0, 0, 0)
        c.paint()
        frame(c, T)
        surf.write_to_png("%s/f_%06.2f.png" % (outdir, T))


if __name__ == "__main__":
    if sys.argv[1] == "render":
        render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "stills":
        stills([float(x) for x in sys.argv[3:]], sys.argv[2])
