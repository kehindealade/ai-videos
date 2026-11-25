MONEY MAP IOU ENGINE (long video 4 "Who owns the national debt", Shorts A and B)
Look: dark green vault wall, engraved cream I.O.U. certificates, brass ticker boards, four holder colours (trust gold, Fed blue, foreign red, others green), share bar top right.
Files: iou_common.py (wall, cert, helpers), iou_content.py (43 narration lines, chapters), iou_engine.py (scenes, render), iou_mix.py (SFX, audio, srt, chapters.json), tts.py (Kokoro cache), iou_shorts.py (Shorts A and B), covers.py (thumbnail and covers), upload packs.
Run: python3 tts.py iou_content vo_long; python3 iou_mix.py iou_content vo_long a.wav out.srt; render in 2 parts: python3 iou_engine.py render iou_content vo_long part0.mp4 0 2 (and part1 1 2) in parallel (about 9 min); concat, mux with a.wav and loudnorm.
Shorts: python3 iou_shorts.py tts|stills|render|srt A|B.
Voices: bm_lewis 0.92 (long), bm_daniel 0.96 (A), am_liam 0.96 (B).
Gotchas: Google font downloads for Old Standard, Libre Baskerville, Special Elite 404; use Cormorant SC, IBM Plex Serif, Saira ExtraCondensed, Poppins. txt() scales LAB font by 1.22. clink() needs equal-length arrays. fiscaldata API is unreachable from the shell, use web search. Check stills after every layout change (overlaps were common). Render part files are not playable until the process ends.
