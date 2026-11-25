Money Map Reels engine (build plan 24 Nov, conversation 3; built 24 Nov 2026). Needs pycairo, numpy, scipy, soundfile, pillow, ffmpeg; fonts Montserrat, Roboto, Bitter, Open Sans, Fira Sans, Fira Sans Black.
common.py: drawing helpers, render(draw, dur, out, music, tag), still(), zones() safe-zone overlay, edge_check() full-bleed check, Track synth (pluck, bassn, marimba, epiano, pad, bell, kick, noise_hit, whoosh, riser, clack).
tax.py  (Reel A, 2027 tax brackets, Myth vs Math ep 1, 38.4 s at 100 bpm): banknote-bundle stack on a dark studio, coloured bank straps per bracket.
rent.py (Reel B, why is rent so expensive, 40.0 s at 96 bpm): apartment tower at dusk; the 10x10 window grid doubles as 100 renters.
pay.py  (Reel C, pay later hangover, 38.57 s at 112 bpm): full-screen generic phone app UI with notifications and a payment-date strip.
Each: python3 X.py stills T1 T2 ... | cover out.png | render out.mp4. All figures are constants at the top of each script; tax.py and pay.py assert their totals.
Lesson (24 Nov 2026): Kenny rejected a toy-brick green stud baseplate as "so bad"; avoid busy novelty textures as full backgrounds, prefer clean premium backgrounds with one strong object.
Safe band respected: key text y 300 to 1340, captions y 1130 to 1320.
