"Why is it so expensive?" series engine (Money Map, 21 Nov 2026). Needs pycairo, kokoro-onnx, soundfile, scipy, numpy, ffmpeg, Kokoro model in /root/kokoro (see build-plan). Fonts: Anton and Poppins preinstalled; Share Tech Mono and Architects Daughter from raw.githubusercontent.com/google/fonts/main/ofl/sharetechmono/ and /architectsdaughter/ into ~/.fonts then fc-cache -f.
wx_common.py: helpers (text, wrap, draw-on polyline ln, dimension arrows dim, callout boxes, route-M logo).
wx_engine.py: generic runner. An episode module defines VODIR, VOICE, SPEED, CAP_Y, PAD, LINES [(scene, spoken, caption)], bg(c,T), draw(c,scene,t,d,T,i), cover(c), sfx(tl,mix,sr,rng).
ink.py: episode 1, printer ink, "blueprint" look. Run: python3 ink.py tts; stills (st_*.png and hs_*.png); render <out.mp4>; cover <png>; srt <file>.
Next episode: copy ink.py, new look (do NOT reuse blueprint), new LINES, scenes, cover, sfx; keep wx_common and wx_engine.
Gotchas: after stroke() use stroke_preserve() before clip(); keep captions at CAP_Y 1345 and notes above y 1200 so they clear the captions; no border or frame around the whole picture.
