import sys, numpy as np, soundfile as sf
sys.argv = ["x"]
import importlib.util
full = open("sd_audio.py").read()
src = full.split("ds = vo(")[0] + "\n" + "def reverb" + full.split("def reverb")[1].split("wl, wr")[0]
g = {}
exec(src, g)
SR, MUS = g["SR"], g["MUS"]
D = 38.8
a0 = int(96.0 * SR)
n = int(D * SR)
ml = g["reverb"](MUS[0])[a0:a0 + n] * 0.4 + MUS[0][a0:a0 + n] * 0.75
mr = g["reverb"](MUS[1])[a0:a0 + n] * 0.4 + MUS[1][a0:a0 + n] * 0.75
g["FX"] = (np.zeros(g["N"]), np.zeros(g["N"]))
FX = g["FX"]
def fxp(fn, *a):
    fn.__globals__["FX"] = FX
    fn(*a)
for fn, args in ((g["buzz"], (0.0, 5.6, 0.42)), (g["click"], (0.0, 0.25, 900)), (g["ringback"], (0.1, 5.4)), (g["clunk"], (6.9, 0.45)),
                 (g["ringback"], (11.6, 14.4)), (g["buzz"], (11.6, 14.0, 0.2)), (g["clunk"], (16.7, 0.45)), (g["ringback"], (20.6, 22.3)), (g["clunk"], (22.3, 0.45)),
                 (g["buzz"], (23.6, 25.0, 0.35)), (g["ringback"], (27.0, 28.9)), (g["clunk"], (28.9, 0.5)), (g["tick"], (30.4, 33.8, 0.1)),
                 (g["dtmf"], (33.8, 7, 0.24, 0.08)), (g["buzz"], (34.4, 35.6, 0.42)), (g["clink"], (12.2,)), (g["clink"], (31.0,))):
    fxp(fn, *args)
for t in (7.0, 16.8, 22.4, 29.0):
    fxp(g["marker"], t, 0.09, 0.5)
fl, fr = FX[0][:n], FX[1][:n]
env = np.ones(n)
e0 = int(35.6 * SR)
env[e0:] = np.linspace(1, 0.35, n - e0)
outl = ml * 0.85 * env + fl
outr = mr * 0.85 * env + fr
pk = max(abs(outl).max(), abs(outr).max())
sf.write("short_audio.wav", np.stack([outl, outr], 1) / pk * 0.8, SR)
print("ok")
