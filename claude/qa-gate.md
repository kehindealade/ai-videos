# QA gate: no video is delivered until it passes

Added 26 Nov 2026 after the First paycheck Reel shipped to Drive with pay stub text under 48 px, floating feet on the bus, a stray line in the envelope scene, a frame 1 without a question, teal bars on the end card and a true peak of 0.0 dBTP. Every rule it broke was already written down. What was missing was a gate that forces the check. This is that gate.

## When

After the final mux, before uploading to Drive, before writing "done" anywhere, and again after every fix.

## Steps

1. Mux with the safe loudness chain (one pass loudnorm alone lets AAC overshoot to 0 dBTP):
   ffmpeg -y -i silent.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.79:level=false" -shortest -movflags +faststart OUT.mp4
2. Run: python3 tools/qa.py OUT.mp4 COVER.png
   It prints automatic checks (resolution, fps, loudness, true peak, border bars) and writes phone-size sheets to /tmp/qa/<name>/.
3. Any FAIL is fixed before going on. Any WARN is looked at and explained in one line.
4. Review as if someone else built it. Open every sheet with the image viewer, not from memory of the code. Answer each of the 9 manual checks in report.txt with yes or no and the time. The magenta bar on each phone frame is the 48 px minimum: any text shorter than it is a fail, including pay stub rows, labels, receipts, end card lines and small print that carries the story.
5. Fix every no, re-render, run qa.py again, re-check. Repeat until all pass.
6. Only then upload to Drive. In the reply to Kenny, paste the automatic lines and the 9 answers, and send the opening and safe-zone sheets with the Drive links.

## Optional second reviewer

For a new series, a new engine or anything Kenny will post soon, start a fresh conversation (a different model if possible) with: "Review the render in Drive AI videos/Renders/<file> against claude/qa-gate.md. Do not fix anything. List every failure with its time." Fix what it finds.

## Things the eye check keeps missing

- Small print inside props (stubs, receipts, phone screens, labels) that the story depends on.
- Limbs, feet and props that detach when a character sits or moves.
- Leftover helper shapes and lines from layout.
- Text that leaves the safe zone only during a slide or zoom transition.
- End cards and covers with coloured bands that read as borders.
- Running totals that do not add up on screen.
