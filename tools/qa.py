import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

PHONE_W = 390
SAFE = (90, 300, 990, 1340)
CAPTION_BAND = (1100, 1300)
MIN_TEXT_PX = 48


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", path])
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    num, den = v["r_frame_rate"].split("/")
    return int(v["width"]), int(v["height"]), float(num) / float(den), float(d["format"]["duration"]), has_audio


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        return None, None
    j = json.loads(m.group(0))
    return float(j["input_i"]), float(j["input_tp"])


def grab(path, t, out):
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", out])
    return Image.open(out).convert("RGB")


def overlay(im):
    im = im.copy()
    w, h = im.size
    sx, sy = w / 1080, h / 1920
    d = ImageDraw.Draw(im, "RGBA")
    x0, y0, x1, y1 = SAFE
    d.rectangle([0, 0, w, y0 * sy], fill=(255, 0, 0, 70))
    d.rectangle([0, y1 * sy, w, h], fill=(255, 0, 0, 70))
    d.rectangle([0, y0 * sy, x0 * sx, y1 * sy], fill=(255, 0, 0, 70))
    d.rectangle([x1 * sx, y0 * sy, w, y1 * sy], fill=(255, 0, 0, 70))
    d.line([0, CAPTION_BAND[0] * sy, w, CAPTION_BAND[0] * sy], fill=(0, 200, 255, 200), width=2)
    d.line([0, CAPTION_BAND[1] * sy, w, CAPTION_BAND[1] * sy], fill=(0, 200, 255, 200), width=2)
    return im


def ruler(im, vertical):
    im = im.copy()
    w, h = im.size
    s = w / (1080 if vertical else 1920)
    px = MIN_TEXT_PX * s
    d = ImageDraw.Draw(im, "RGBA")
    x = w - 14
    d.rectangle([x - 4, 10, x + 4, 10 + px], fill=(255, 0, 255, 230))
    return im


def flat_run(lines):
    first = lines[0].mean(axis=0)
    n = 0
    for ln in lines:
        if ln.std(axis=0).max() > 6 or np.abs(ln.mean(axis=0) - first).max() > 8:
            break
        n += 1
    return n, first


def flat_edges(im):
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    found = []
    for name, lines, size in [
        ("top", a, h),
        ("bottom", a[::-1], h),
        ("left", a.transpose(1, 0, 2), w),
        ("right", a.transpose(1, 0, 2)[::-1], w),
    ]:
        n, col = flat_run(lines)
        if size * 0.025 <= n < size * 0.4:
            nxt = lines[n:n + 3].reshape(-1, 3)
            if np.abs(nxt.mean(axis=0) - col).max() > 25 and lines[n + 2].std(axis=0).max() < 12:
                found.append(name)
    return found


def sheet(images, cols, out):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    s = Image.new("RGB", (w * cols + 6 * (cols - 1), h * rows + 6 * (rows - 1)), (30, 30, 30))
    for i, im in enumerate(images):
        s.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    s.save(out)


def main():
    if len(sys.argv) < 2:
        print("usage: python3 tools/qa.py video.mp4 [cover.png]")
        sys.exit(1)
    path = sys.argv[1]
    cover = sys.argv[2] if len(sys.argv) > 2 else None
    name = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join("/tmp/qa", name)
    os.makedirs(out, exist_ok=True)

    w, h, fps, dur, has_audio = probe(path)
    vertical = h > w
    times = [float(t) for t in range(0, min(15, int(dur)))]
    t = 15.0
    while t < dur - 0.5:
        times.append(t)
        t += 3.0
    times.append(max(0.0, dur - 0.3))

    frames = [grab(path, t, os.path.join(out, f"f_{t:06.2f}.png")) for t in times]
    pw = PHONE_W if vertical else 640
    ph = int(pw * h / w)
    phone = [ruler(f.resize((pw, ph), Image.LANCZOS), vertical) for f in frames]
    sheet(phone[:15], 5, os.path.join(out, "1_opening_15s_phone.png"))
    sheet(phone[15:], 5, os.path.join(out, "2_rest_phone.png"))
    if vertical:
        sheet([overlay(p) for p in phone], 6, os.path.join(out, "3_safe_zone.png"))

    lines = []
    def add(status, msg):
        lines.append(f"{status}  {msg}")

    want = (1080, 1920) if vertical else (1920, 1080)
    add("PASS" if (w, h) == want else "FAIL", f"resolution {w}x{h} (want {want[0]}x{want[1]})")
    add("PASS" if abs(fps - 30) < 0.5 else "WARN", f"fps {fps:.2f}")
    add("INFO", f"duration {dur:.1f} s")
    if not has_audio:
        add("FAIL", "no audio stream")
    else:
        i, tp = loudness(path)
        if i is None:
            add("WARN", "could not measure loudness")
        else:
            add("PASS" if -17.5 <= i <= -14.5 else "FAIL", f"loudness {i:.1f} LUFS (want about -16)")
            add("PASS" if tp <= -1.0 else "FAIL", f"true peak {tp:.1f} dBTP (want below -1)")

    edge_hits = {}
    for t, f in zip(times, frames):
        for e in flat_edges(f):
            edge_hits.setdefault(e, []).append(t)
    if vertical:
        if edge_hits:
            for e, ts in edge_hits.items():
                add("WARN", f"flat {e} band that differs from the picture next to it at t={', '.join(f'{x:.0f}' for x in ts[:8])}: possible border bar, look at it")
        else:
            add("PASS", "no flat border bands found")

    if cover:
        c = Image.open(cover).convert("RGB")
        cw = PHONE_W if c.height > c.width else 320
        cp = c.resize((cw, int(cw * c.height / c.width)), Image.LANCZOS)
        cp.save(os.path.join(out, "4_cover_phone.png"))
        if c.height > c.width:
            overlay(cp).save(os.path.join(out, "5_cover_safe.png"))
        add("INFO", f"cover {c.width}x{c.height}")

    report = "\n".join(lines)
    manual = f"""
MANUAL CHECKS (open every sheet in {out} and answer each line yes or no with the time; any no is a fix):
1. Text size: the magenta bar on the right of each phone frame is the {MIN_TEXT_PX} px minimum. Is every word and number on screen at least that tall? List each piece of text that is smaller and its time.
2. Safe zone: is all essential text outside the red areas on 3_safe_zone.png, including during transitions?
3. Frame 1: does it move, pose a question or tension in 8 words or fewer, and match the cover?
4. Pace: does the picture change every 2 to 3 s (story films) or 3 to 5 s (Money Map) in the first 30 s?
5. Drawing errors: any floating limbs or feet, stray lines or shapes, overlapping objects, clipped text, wrong numbers or sums?
6. Full bleed: does the picture reach every edge in every frame, end card included (no bars, frames or inset windows)?
7. End card: does it name the next episode or ask the follow question, in text at least {MIN_TEXT_PX} px?
8. Cover: cliffhanger that does not give the answer, question block inside y 384 to 900, readable on 4_cover_phone.png?
9. Story: would a stranger understand it with the sound off?
"""
    with open(os.path.join(out, "report.txt"), "w") as f:
        f.write(report + "\n" + manual)
    print(report)
    print(manual)
    print("sheets in", out)


if __name__ == "__main__":
    main()
