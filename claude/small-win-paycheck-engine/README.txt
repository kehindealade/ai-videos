"Numbers that say everything" Episode 2: First paycheck (Small Win Films, Facebook Reel only, built 26 Nov 2026).

Requirements: pycairo, numpy, scipy, soundfile, Pillow, ffmpeg.
Fonts (download into ~/.fonts and run fc-cache -f):
- Fredoka: https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf
- Courier Prime Bold: https://raw.githubusercontent.com/google/fonts/main/ofl/courierprime/CourierPrime-Bold.ttf
- Courier Prime Regular: https://raw.githubusercontent.com/google/fonts/main/ofl/courierprime/CourierPrime-Regular.ttf

Commands (run from this folder):
- Preview stills (15s strip, safe-zone sheet, cover): python3 paycheck_reel.py stills
- Cover (1080x1920): python3 paycheck_reel.py cover /tmp/SmallWinFilms_facebook-reel-cover_first-paycheck.png
- Score and SFX: python3 pc_audio.py
- Silent video: python3 paycheck_reel.py render /tmp/paycheck_silent.mp4
- Final mux with loudness normalisation (-16 LUFS, true peak <= -1.5 dBTP):
  ffmpeg -y -i /tmp/paycheck_silent.mp4 -i mix_raw.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "loudnorm=I=-16:TP=-1.5:LRA=11" -shortest -movflags +faststart /tmp/SmallWinFilms_facebook-reel_first-paycheck.mp4
