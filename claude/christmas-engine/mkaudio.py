import subprocess, sys
SRC = "parts/audio_norm.wav"
def build(segs, out, tail):
    parts = []
    fc = []
    n = 0
    for (t, d) in segs + [tail]:
        fc.append("[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.12,afade=t=out:st=%.3f:d=0.18[a%d]" % (t, t + d, max(0, d - 0.18), n))
        parts.append("[a%d]" % n)
        n += 1
    fc.append("".join(parts) + "concat=n=%d:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=9[o]" % n)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000", out], check=True)
S1 = [(0.2, 3.3), (8.6, 2.0), (14.0, 1.6), (21.6, 2.6), (28.0, 2.7), (32.2, 2.4), (41.0, 3.0), (48.4, 2.2), (66.0, 2.4), (70.2, 2.4), (78.0, 3.0), (103.0, 3.8)]
S2 = [(27.0, 11.2), (76.0, 4.0), (93.0, 6.2), (103.5, 3.6)]
S3 = [(118.4, 3.4), (124.8, 3.2), (133.0, 6.6), (141.0, 5.0), (152.0, 6.0), (162.0, 6.0)]
tail = (171.0, 3.0)
build(S1, "a1.wav", tail)
build(S2, "a2.wav", tail)
build(S3, "a3.wav", tail)
print("ok")
