import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
from paycheck_reel import (
    DUR, STAMP_TIMES, ENV_TEAR_T, SNIP_TIMES, SHOCK_T,
    CARD_SLIDE_T, PAID_STAMP_T, CIRCLE_T, END_T,
)

SR = 44100
N = int(round(SR * DUR))
rng = np.random.default_rng(20261215)
BARS = 18
BPM = BARS * 4 * 60.0 / DUR
BEAT = 60.0 / BPM
BAR = BEAT * 4


def nf(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def place(buf, sig, t, g=1.0):
    i = int(round(t * SR))
    if i < 0 or i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i] * g


def hp(x, f):
    b, a = butter(2, f / (SR / 2.0), "high")
    return lfilter(b, a, x)


def lp(x, f):
    b, a = butter(2, f / (SR / 2.0), "low")
    return lfilter(b, a, x)


def uke_pluck(midi, dur, vel=1.0):
    n = max(1, int(SR * dur))
    t = np.arange(n) / SR
    f = nf(midi)
    s = (
        np.sin(2 * np.pi * f * t)
        + 0.42 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.18)
        + 0.18 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.08)
    )
    env = np.minimum(1.0, t / 0.004) * np.exp(-t / 0.28) * np.minimum(1.0, (dur - t) / 0.02)
    return s * env * vel * 0.14


def upright_bass(midi, dur, vel=1.0):
    n = max(1, int(SR * dur))
    t = np.arange(n) / SR
    f = nf(midi)
    s = np.sin(2 * np.pi * f * t) + 0.32 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.22)
    env = np.minimum(1.0, t / 0.012) * np.exp(-t / 0.55) * np.minimum(1.0, (dur - t) / 0.04)
    return s * env * vel * 0.28


def whistle_note(midi, dur, vel=1.0):
    n = max(1, int(SR * dur))
    t = np.arange(n) / SR
    f0 = nf(midi)
    vib = 1.0 + 0.007 * np.sin(2 * np.pi * 5.6 * t) * np.minimum(1.0, t / 0.14)
    phase = 2 * np.pi * np.cumsum(f0 * vib) / SR
    tone = np.sin(phase) + 0.08 * np.sin(2 * phase)
    breath = lp(hp(rng.standard_normal(n), 1400), 4200) * 0.04
    env = np.minimum(1.0, t / 0.035) * np.minimum(1.0, (dur - t) / 0.06)
    return (tone + breath) * env * vel * 0.16


def soft_clap(vel=1.0):
    n = int(SR * 0.11)
    t = np.arange(n) / SR
    nz = lp(hp(rng.standard_normal(n), 1100), 3600)
    burst = np.exp(-t / 0.022) + 0.45 * np.exp(-np.maximum(0, t - 0.014) / 0.025)
    return nz * burst * vel * 0.18


def sfx_chunk_bell():
    # Mechanical time clock punch + crisp diner bell on frame 1
    n = int(SR * 0.85)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (62 + 85 * np.exp(-t / 0.035)) * t) * np.exp(-t / 0.09) * 0.65
    clack = lp(hp(rng.standard_normal(n), 600), 3200) * np.exp(-t / 0.018) * 0.45
    bt = np.maximum(0, t - 0.06)
    bell = (
        (np.sin(2 * np.pi * 1568 * bt) + 0.4 * np.sin(2 * np.pi * 3136 * bt))
        * np.exp(-bt / 0.24)
        * (t >= 0.06)
        * 0.35
    )
    return thud + clack + bell


def sfx_stamp():
    n = int(SR * 0.18)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (95 + 70 * np.exp(-t / 0.025)) * t) * np.exp(-t / 0.06) * 0.55
    s += lp(rng.standard_normal(n), 1800) * np.exp(-t / 0.015) * 0.28
    return s


def sfx_tear():
    n = int(SR * 0.32)
    t = np.arange(n) / SR
    nz = lp(hp(rng.standard_normal(n), 1800), 6500)
    env = np.minimum(1.0, t / 0.03) * np.exp(-t / 0.14) * (0.7 + 0.3 * np.sin(2 * np.pi * 36 * t))
    return nz * env * 0.35


def sfx_snip(pitch_hz):
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    # Scissor metal click + falling tone
    click = lp(hp(rng.standard_normal(n), 2800), 7500) * np.exp(-t / 0.015) * 0.45
    f = pitch_hz * (1.0 - 0.28 * np.minimum(1.0, t / 0.18))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.10) * 0.26
    return click + tone


def sfx_ding():
    n = int(SR * 1.1)
    t = np.arange(n) / SR
    s = (
        np.sin(2 * np.pi * 1046.5 * t)
        + 0.45 * np.sin(2 * np.pi * 2093.0 * t) * np.exp(-t / 0.3)
        + 0.22 * np.sin(2 * np.pi * 3136.0 * t) * np.exp(-t / 0.12)
    )
    return s * np.minimum(1.0, t / 0.003) * np.exp(-t / 0.38) * 0.42


def sfx_paid_thump():
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (55 + 90 * np.exp(-t / 0.04)) * t) * np.exp(-t / 0.14) * 0.72
    s += lp(rng.standard_normal(n), 1400) * np.exp(-t / 0.02) * 0.38
    return s


# C major progression: C - G - Am - F (warm, upbeat diner feel)
CHORDS = [
    (48, [60, 64, 67, 72]),  # C
    (43, [59, 62, 67, 71]),  # G
    (45, [60, 64, 69, 72]),  # Am
    (41, [60, 65, 69, 72]),  # F
]

# Original 4-bar whistle motif (MIDI notes, beat offset, duration in beats)
MOTIF = [
    (0.0, 76, 0.75), (0.75, 79, 0.75), (1.5, 81, 0.5), (2.0, 79, 1.0), (3.0, 76, 0.75),
    (4.0, 74, 0.75), (4.75, 76, 0.75), (5.5, 79, 1.5), (7.0, 74, 0.75),
    (8.0, 72, 0.75), (8.75, 76, 0.75), (9.5, 79, 0.5), (10.0, 76, 1.0), (11.0, 72, 0.75),
    (12.0, 74, 1.0), (13.0, 76, 0.75), (13.75, 72, 1.75),
]


def build_music():
    uke = np.zeros(N)
    bs = np.zeros(N)
    cl = np.zeros(N)
    wh = np.zeros(N)

    for bar in range(BARS):
        root, notes = CHORDS[bar % 4]
        t0 = bar * BAR
        # Ukulele strum pattern: 1, 2&, 3&, 4
        for off, vel in ((0.0, 1.0), (1.5, 0.72), (2.5, 0.85), (3.5, 0.65)):
            for k, nt in enumerate(notes):
                place(uke, uke_pluck(nt, BEAT * 0.9, vel), t0 + off * BEAT + k * 0.011)
        # Upright bass on 1 and 3
        place(bs, upright_bass(root, BEAT * 1.8, 1.0), t0)
        place(bs, upright_bass(root + 7 if bar % 2 == 0 else root - 5, BEAT * 1.6, 0.85), t0 + 2 * BEAT)
        # Soft claps on 2 and 4
        place(cl, soft_clap(0.85), t0 + 1 * BEAT)
        place(cl, soft_clap(0.95), t0 + 3 * BEAT)

    # Whistle melody during work montage (bars 1..4) and dinner warmth (bars 11..15)
    for start_bar in (1, 11):
        base = start_bar * BAR
        for off, midi, d in MOTIF:
            place(wh, whistle_note(midi, d * BEAT, 1.0), base + off * BEAT)

    t = np.arange(N) / SR

    def gate(a, b, r=0.12):
        return np.clip((t - a) / r, 0, 1) * np.clip((b - t) / r, 0, 1)

    # Drop to bass-only during tax deductions (11.0 to 18.0)
    tax_dip = gate(11.0, 18.0, 0.25)
    uke_g = 1.0 - 0.88 * tax_dip
    cl_g = (1.0 - tax_dip) * (1.0 - gate(END_T, DUR, 0.2))
    wh_g = 1.0 - tax_dip

    out = uke * uke_g + bs * 1.0 + cl * cl_g + wh * wh_g
    # Warm resolving C major chord on end card
    for k, nt in enumerate((60, 64, 67, 72, 76)):
        place(out, uke_pluck(nt, 2.4, 1.15), END_T + k * 0.03)
    place(out, upright_bass(48, 3.0, 1.1), END_T)
    out *= np.clip((DUR - t) / 0.18, 0, 1)
    return out


def build_sfx():
    s = np.zeros(N)
    # Frame 1 time clock chunk + bell
    place(s, sfx_chunk_bell(), 0.0, 0.95)
    # Shift stamps
    for st in STAMP_TIMES:
        place(s, sfx_stamp(), st, 0.85)
    # Envelope tear
    place(s, sfx_tear(), ENV_TEAR_T, 0.9)
    # Four falling-pitch scissor snips
    for idx, st in enumerate(SNIP_TIMES):
        place(s, sfx_snip(540 - idx * 65), st, 0.9)
    # Register ding on card slide + PAID stamp thump
    place(s, sfx_ding(), CARD_SLIDE_T + 0.35, 0.9)
    place(s, sfx_paid_thump(), PAID_STAMP_T, 0.95)
    # Gentle chime on end card
    place(s, sfx_ding(), END_T + 0.05, 0.55)
    # Subtle loop cue at very end
    place(s, sfx_stamp(), DUR - 0.12, 0.35)
    return s


if __name__ == "__main__":
    mix = build_music() * 0.88 + build_sfx() * 0.92
    peak = max(1e-6, float(np.abs(mix).max()))
    mix = mix / peak * 0.82
    sf.write("mix_raw.wav", mix.astype(np.float32), SR)
    print(f"mix_raw.wav written: {DUR:.3f}s, {BPM:.2f} bpm")
