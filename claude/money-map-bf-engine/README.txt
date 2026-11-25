Black Friday engine (Money Map, 21 Nov 2026). Needs pycairo, kokoro-onnx, soundfile, scipy, ffmpeg, Kokoro model in /root/kokoro.
bf_common.py: helpers. bf_short.py (tts, stills, render <out>, cover <png>, srt <file>): "shop window" Short, voice af_kore 0.98, lines in LINES.
bf_reel.py (stills, render <out>, cover <png>): "price-history line" music-only Reel, synthetic 96 bpm lo-fi loop, 30.0 s = 12 bars.
Run order for the Short: tts, render, cover, srt. Reel: render, cover. Edit LINES / price() to make another episode.
