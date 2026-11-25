Top-down table engine (Money Map Facebook Reel "Thanksgiving dinner cost", built 22 Nov 2026). Needs pycairo, numpy, scipy, soundfile, ffmpeg; fonts Poppins, Inter, DejaVu Sans Mono.
common.py: helpers. thanks.py: python3 thanks.py render out.mp4 | cover out.png | stills | music.
Timeline is beat-locked: 64 beats = 35.0 s loop (BEAT = DUR/64). D = dish list (positions, prices, drop times); change prices/labels there for a new year (assert checks the total). Panels: panel1 (vs last year), panel2 (turkey), panel3 (record). Tags and dishes are hidden during panels (dim 0.9).
Sprites are drawn once and cached (build()); music() is folk-style: plucked arpeggio, bass, stomp and clap, marimba melody, clinks synced to each dish drop. Look is logged as used.
v2 (22 Nov 2026): all text moved into the safe band per claude/readability-and-retention-rules.md (board y 320-450, caption card y 1170-1340, dishes y 480-1145, panels y 380-1340); zones(png,out) draws the overlay for checks.
