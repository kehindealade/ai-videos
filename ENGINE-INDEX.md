# Engine index

Every engine lives in claude/<name>/ with its upload packs. Newest first. Each README.txt in a folder has the full commands and gotchas. Never reuse an engine's look as is; copy the folder, then change look, palette, music, voice and layout (see the channel log).

General pattern: pycairo draws each frame, frames are piped to ffmpeg, audio is synthesised in numpy, then muxed with loudnorm. Long videos render in two parallel parts and are joined with the ffmpeg concat demuxer.

## Small Win Films

| Engine | What it made | Entry and command |
|---|---|---|
| sunday-call-engine | Film "Every Sunday at 6, She Called" 3:00 + Short | film.py render 0 90 p1.mp4 and 90 180 p2.mp4; sd_tts.py; sd_audio.py; short.py render out.mp4; thumbs.py |
| small-win-night-engine | Reel "Everybody goes out except me" (It's Not Just Me ep 3) | night_reel.py render silent.mp4 / cover / stills; ni_audio.py |
| small-win-wave-engine | Reel "Wave back at someone who wasn't waving" (ep 2) | wave_reel.py part F0 F1 out.mp4 / still / cover; wv_audio.py |
| small-win-chat-engine | Reel "Every group chat ever" (ep 1) | chat_reel.py render silent.mp4 / still / cover; gc_audio.py |
| christmas-engine | Film "She Never Knocked" 3:00 + 3 Shorts | film.py render t0 t1 out.mp4; audio.py; shorts.py render n out.mp4; mkaudio.py; thumbs.py |
| small-win-numbers-engine | Reel "3 alarms" (Numbers that say everything ep 1) | alarms3.py render out.mp4 / cover / sheet; piano_loop.py |
| unsent-engine | Film "31 Texts She Never Sent" + Short + Reel | film.py helpers, scenes.py, compose.py (16:9 and 9:16), audio.py, vert.py (Short and Reel cut lists), thumb.py, cover.py |
| two-cups-engine | Film "He Still Makes Two Cups" + Short + Reel | film.py, timeline.py, audio.py, short.py, render.sh, reel.py, vo.py, cover_reel.py, thumb.py, thumbs2.py |
| bad-day-engine | Film "Nothing Could Fix His Bad Day" + Short + Reel | film.py, timeline.py, audio.py, short.py, reel.py, vo.py, cover.py, thumbs.py, fp.py, short_cover.py |
| story-films-engine | Original story-film helpers and channel branding | brand.py (sprout logo), brand-fb.py (Facebook and YouTube branding), film.py |

## Money Map

| Engine | What it made | Entry and command |
|---|---|---|
| money-map-ram-engine | Short "Why Is RAM So Expensive?" (circuit board) | rm_tts.py; ram.py stills / cover / render out.mp4 / srt |
| money-map-reels-engine | Reels: 2027 tax brackets, rent, pay later hangover | tax.py, rent.py, pay.py: stills / cover / render out.mp4 (common.py synth) |
| money-map-city-engine | Long "How Credit Card Rewards Work" + 2 Shorts | tts.py cc_content vo; cc_mix.py; cc_engine.py render cc_content vo p0.mp4 0 2 (and 1 2); s3.py, s4.py Shorts; cb_tts.py Chatterbox. Needs ss_common.py, vcommon.py and tts.py from money-map-sheet-engine |
| money-map-sheet-engine | Long "How Social Security Works" + 2 Shorts | tts.py ss_content vo_long; ss_mix.py; ss_engine.py render ss_content vo_long p0.mp4 0 2; s1.py, s2.py; thumb.py |
| money-map-thanks-engine | Reel "Thanksgiving dinner for 10" | thanks.py render out.mp4 / cover / stills / music |
| money-map-iou-engine | Long "Who Owns the National Debt?" + 2 Shorts | tts.py iou_content vo_long; iou_mix.py; iou_engine.py render iou_content vo_long part0.mp4 0 2; iou_shorts.py tts / stills / render / srt A or B; covers.py |
| why-expensive-engine | Short "Why Is Printer Ink So Expensive?" (series runner) | ink.py tts / stills / render out.mp4 / cover / srt (wx_engine.py generic runner) |
| money-map-split-engine | Reel "Same money, two choices" ep 1 coffee | coffee.py render out.mp4 / cover / stills |
| money-map-bf-engine | Black Friday Short and Reel | bf_short.py tts / stills / render / cover / srt; bf_reel.py stills / render / cover |
| money-map-transit-engine | Long "Why Is Bitcoin Crashing?" + 2 Shorts + Reel | content.py data, engine.py renderer, tts.py, mix.py, shorts.py, mkshorts.py, tts_short.py, covers.py, thumb.py, fbreel.py |
| money-map-chalk-engine | Reel "Your $16 meal" (chalkboard) | reel.py |
| money-map-statement-engine | Long "How Banks Make Money" + 2 Shorts | stmt.py engine (python3 stmt.py info|stills|render banks|short_gap|short_coffee), banks.py script data, short_gap.py, short_coffee.py, thumb.py, cover_gap.py (writes to /home/claude/yts/, change the path). Kokoro is read from models/ next to stmt.py: ln -s /root/kokoro claude/money-map-statement-engine/models |
| money-map-paper-engine | Betting long + 2 Shorts (held, unposted) | engine.py info / stills / render long|short1|short2 out.mp4; content.py. Reads Kokoro from models/ next to engine.py, so symlink: ln -s /root/kokoro claude/money-map-paper-engine/models |

## Tools

| Tool | Use |
|---|---|
| claude/yt-stats/yt.py | Free YouTube research: suggest, outliers, trending, scan, seo, report (needs a fresh sign-in; see workflow.md Setup) |
| claude/yt-stats/thumbcheck.py | Thumbnail and cover safe-zone check: python3 thumbcheck.py thumb.png |
| tools/manifest.py | Rebuilds MANIFEST.md (which project files are copied or pending) |

Free YouTube autocomplete without sign-in: curl "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=<phrase>"
