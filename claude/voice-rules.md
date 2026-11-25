# Voice rules (every narrated video, Short and Reel, both channels)

Added 22 Nov 2026 at Kenny's request: add random, normal human expression and emotion to the voices, and stop reusing the same voices. Applies to all new videos from now on. Do not re-voice videos already made.

Two voice engines are allowed (Kenny, 22 Nov 2026: toggle between them on demand and use whichever is best, no need to ask):
- Kokoro (kokoro-onnx, offline, voice name plus speed per line; the engines' tts.py files already accept a per-line voice and speed). Default, fast on CPU, best for long narration. No emotion controls, so expression comes from the script text, per-line speed and gaps.
- Chatterbox Turbo (free, MIT, 350M parameters; pip install chatterbox-tts; from chatterbox.tts_turbo import ChatterboxTurboTTS). More expressive: it performs text tags such as [laugh], [chuckle], [sigh], [cough] and natural reactions. It needs a 5 to 10 second reference clip to set the voice and it watermarks its output. The project is archived (retired Aug 2026) but the code and weights stay free on GitHub and HuggingFace.

Expression is done inside the single voice generation we already run, so it adds no extra generation, no extra renders and almost no extra usage.

## 0. Which engine to use

- Choose per video, Short or Reel, whichever suits it best; Claude decides and states the choice in the build log.
- Kokoro: long narration, anything over about 90 seconds of speech, and any case where speed or usage matters.
- Chatterbox Turbo: short voice lines where expression matters most (Short and Reel hooks and narration, a spoken film hook), about 90 seconds of speech or less per video.
- The workspace has only 2 CPU cores, 7 GB RAM and no GPU (checked 22 Nov 2026), so Chatterbox may run several times slower than the audio length. First time it is used, run a speed test on one line and write the result here (compute seconds per audio second). If it is too slow for the video at hand, use Kokoro. Chatterbox's speed claims are for GPUs, so do not assume them.
- Respect Kenny's rule on limits: if Chatterbox would take many extra runs, a long wait or noticeably more usage, use Kokoro for that video.
- If the Chatterbox download or run fails, switch to Kokoro without asking.
- Keep the model's cache between videos in the same conversation; generate each line once.
- A video keeps one engine and one voice from start to end (a Short and its long video are separate videos and may use different engines).

## 1. A new voice for every video

- Every new long video, Short, Reel hook or film hook gets its own voice. Never reuse a voice that is already logged, and never use the same voice for a long video and the Shorts cut from it (Money Map already did this: bm_lewis, bm_daniel, am_liam).
- Pick at random, not by habit: build the list of Kokoro voices from the voices file (k.get_voices() or the keys in voices-v1.0.bin), remove every voice in the used list below, and choose with Python's random.choice. Do not choose "the nicest" one each time.
- Character voices that do not fit narration (am_santa) and whisper voices (af_nicole: about 1.75 words a second, a 30-second script ran 57 seconds, tested 24 Nov 2026) are left out of the random pick for explainers; am_adam is Kokoro's weakest male voice and is left out too.
- Chatterbox voices: make the reference clip from a Kokoro voice picked the same way (about 10 seconds of a script line, never a real person's voice or any recording of a real person), so the Chatterbox voice is tied to that unused Kokoro voice. Log it as "chatterbox ref <kokoro voice>" and add the Kokoro voice to the used list. Never clone or imitate a real person's voice.
- When the unused list gets short or empty, make a new voice by blending two voices: take the two style vectors (k.get_voice_style(name)), mix them with a random weight between 0.3 and 0.7, and pass the blended array as the voice (for Chatterbox, build the reference clip from the blend). Verify the call works in the installed kokoro-onnx version before relying on it. A blend counts as a new voice and is logged as "a+b weight". Never repeat a blend with the same pair at a similar weight.
- Log the voice, engine, base speed and any blend in the channel's log in the same entry as the video: "Voices" line in claude/money-map-style-log.md (Money Map) or the film's entry in claude/film-log.md (Small Win Films), and in the upload pack's credits line only if the pack lists one. Update the used list below too.
- Facebook Reels and TikTok cuts of a video also get their own voice (a different one from the YouTube version).

Used so far (do not reuse; from the logs, updated 24 Nov 2026 after the Sunday-call film): af_alloy, af_aoede, af_bella, af_heart, af_jessica, am_echo (as Chatterbox ref), bf_lily (as Chatterbox ref), blend af_bella+bf_emma 0.42 (Chatterbox ref), blend bm_fable+am_michael 0.66 (Chatterbox ref, RAM Short), blend bm_george+am_fenrir 0.40 (Chatterbox ref, grandson line in "Every Sunday at 6"), blend bf_alice+bf_emma 0.36 (Chatterbox ref, grandmother's laugh in "Every Sunday at 6"), af_kore, af_nova, af_river, af_sarah, af_sky, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, bf_alice, bf_emma, bf_isabella, bm_daniel, bm_fable, bm_george, bm_lewis.

Kokoro voices not yet used (check against the voices file before use): none of the good fits; blend two voices for every new reference; af_nicole, am_adam, am_santa (poor fits, see above). Pick from the good fits at random; when they run out, blend two voices (the next video after am_echo and bf_lily are used).

Chatterbox speed test result (24 Nov 2026): about 3.2 s of compute per second of audio on this 2-core CPU (9.5 s line in 30 s). Needs two float32 patches after pip install (see style log entry 13). Kenny found Kokoro-only voices too robotic (24 Nov 2026): use Chatterbox Turbo by default for all narration, long videos included, with Kokoro only as the reference-clip source or a fallback if Chatterbox fails.

## 2. Normal human expression and emotion (random, light, natural)

Goal: the voice sounds like a person talking, not a reader. Keep it subtle and varied; a different pattern in every video, so no video has the same rhythm.

- Speed: each video gets a random base speed between 0.90 and 1.00 (Kokoro). Each line then gets a small random offset of up to about 0.04 either way: slightly slower on heavy, closing or reveal lines (minus 0.03 to 0.05), slightly quicker on short punchy or excited lines (plus 0.02 to 0.04). Keep every line between 0.85 and 1.08. The hook line stays clear and a touch quicker.
- Gaps between lines: use a different random gap each time, between about 0.25 and 0.60 seconds, instead of one fixed number. Longer before a reveal or a number, shorter inside a quick list. Where an engine has one fixed gap value, change it to a per-line list when next building with that engine (done in claude/money-map-sheet-engine/: each line carries its own speed and gap from its mood).
- Mood tag per line: while writing the script give each line one of: curious, surprised, calm, serious, warm, amused. The tag decides the speed offset and the text shaping below. Mix them; do not give every line the same mood.
- Text shaping (what both engines respond to):
  - contractions and plain spoken wording ("that's", "here's the thing")
  - commas for small breaths, "..." for a hesitation, "?" for real questions, and at most one "!" in a whole video
  - one or two short natural reactions or fillers per minute at most ("Huh.", "Okay, so...", "Honestly,", "Right?"), placed where a person would say them, never stacked
  - an occasional light self-correction ("well, almost") when it fits the script
  - numbers stay spelled out the way the engine already requires (no digits, $ or % in spoken lines)
- Chatterbox only: the tags [chuckle], [laugh], [sigh] and similar may be used sparingly (at most two or three in a whole video) where a person would really react, and the emotion setting stays in a natural range (do not push it to theatrical). Never use them with Kokoro: it reads them as words.
- Tone by channel: Money Map is curious, conversational and confident. Small Win Films stays quiet and sincere; on grief and loss never use jokes, laughs, amused moods or excited speed, in line with the Policy gate.
- Do not type laughs, sighs or sounds as words ("haha", "sigh", "ahh") for either engine, and no breath-sound inserts (decided 22 Nov 2026).
- Limits: Kokoro cannot do big emotion, shouting or crying, so its expression stays modest; use Chatterbox when a video needs more.
- No re-generation to "improve emotion". Write the script shaped from the start, generate once. If a line sounds wrong, redo only that line.

## 3. Check before delivery

1. The voice is not in the used list; the log entry names the voice and engine.
2. The script lines carry mood tags and the speeds and gaps vary (print them in the build log; not all identical).
3. No more than two fillers per minute, one "!" at most, no typed sounds, Chatterbox tags only with Chatterbox and only a few.
4. Phone-size check of captions still matches the spoken words (captions are written from the shaped text).
