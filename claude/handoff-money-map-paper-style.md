# Handoff: Money Map "Paper" style, long betting video and two Shorts (16 Nov 2026)

Continues from handoff-ledger-kit.md. Read that for channel facts, policy notes and the older dark ledger-board kit.

## Why this exists
Kenny asked for the betting topic as a long video in a design different from the first Money Map video, so the channel does not look like one template repeated, and for the Shorts to be remade in the same new design. Research on 16 Nov also concluded: long form is the core of Money Map (income and watch hours), Shorts are the feeder; cut 2 to 3 Shorts from each long video.

## What was delivered (16 Nov 2026)
- how-betting-companies-make-money-LONG.mp4: 8:04, 1920x1080, 34 scenes, 1,189 words, voice am_michael at 0.95. Structure: hook, three "moves" (the price, the parlay, the limit), recap, end card teasing "who really pays for your credit card rewards".
- you-won-they-still-got-paid-SHORT.mp4: 0:58, 1080x1920, voice bm_george. The coin-toss cut. Replaces the old ledger-look betting Short planned for Tue 17 Nov (Kenny to confirm which he posts).
- why-apps-push-parlays-SHORT.mp4: 0:49, 1080x1920, voice am_michael. Parlay margin and New Jersey data.
- thumb-long.png: 1280x720, "YOU WON. THEY STILL GOT PAID."
- No sources line or made-by credit at the end (Kenny's rule). Small data attributions sit on the data scenes instead. Disclaimer "18+ · EXAMPLES ONLY · NOT BETTING ADVICE" on every frame. No operator named, no logos, no tips.
- Voices used so far on Money Map: bm_fable, am_puck, am_michael, bm_george. Next video should use a different one.
- Audio was checked for level only (about -17 dB mean), not listened to or transcribed. Pronunciation of "vig" and "parlay" is unverified.

## The Paper style (engine in claude/money-map-paper-engine/)
- Look: cream paper background with grain, ink black, one red accent, green and gold support; Lora Bold headlines, Inter for labels; white cards with a hard ink offset shadow; dark inverted cards for chapter numbers and the end card. Money Map route-M mark redrawn in code (brand_mark).
- engine.py: Python + pycairo, frames piped to ffmpeg, one mp4 per scene then concat with -c copy; 2 worker processes. The whole 8 minute video rendered in about 3 minutes on 2 cores. Same code draws 16:9 ("long") and 9:16 (any other name) through the Layout class.
- content.py: the script and visuals as data. Each scene is S(kind, tag, say=[lines], **params). Kinds: big, stats, flow (money moving between cards, coin flip), bars (keyframed), table, ticket (parlay slip with stamp), phone (bet slip with limit message), list, chapter, end.
- Timing needs no transcription: every narration line is synthesised separately with Kokoro, so line start and end are exact. Cues are strings like "2" (start of line 2), "2:word" (when that word is spoken, estimated by character position), "2:word#2" (second occurrence), "2:$" (end of line), with optional "+0.3" offsets.
- Numbers are written as digits in the script (they show in captions) and converted for speech through the SPOKEN list in content.py; the engine refuses to narrate if a digit or symbol has no spoken form.
- Commands: python engine.py info <name>; python engine.py stills <name> <folder> [scene numbers]; python engine.py render <name> <out.mp4>. Names: long, short1, short2.
- Setup: venv with kokoro-onnx, soundfile, numpy, pillow, pycairo; Kokoro model files in models/ from the kokoro-onnx GitHub release model-files-v1.0. Fonts needed: Lora, Inter.
- Sound: narration, a soft tick on reveals, a low thump on chapter cards. No music.

## Sources used for the betting facts
- American Gaming Association 2025: $166.9B wagered, $16.96B revenue (via track360.io and Legal Sports Report).
- Legal Sports Report: national hold about 6.9% in 2019 and 10.2% in 2025; New Jersey parlays 32% of handle and 65% of revenue over 12 months.
- Fox Sports "What is the vig": -110 pricing, 4.5 to 5% on spreads, heavy favourites 8 to 10%.
- Parlay margin by picks is worked from -110 pricing: 4.5%, 8.9%, 17.0%, 20.8% for 1, 2, 4, 5 picks; four tosses pay $160 fair and about $133 at the shop price on a $10 stake.
- InGame: UK Gambling Commission data, about 643,000 of nearly 15 million active accounts restricted (4.3%), about 47% of restricted accounts lifetime profitable (25% of unrestricted); Wyoming and BetMGM Massachusetts report about 1% or less limited.
- Bonus.com reporting CBS News: Massachusetts Gaming Commission found limits lowered for winning bettors and raised for losing bettors.
- Kambi tribal report (tribalgaming.com): parlays and live markets carry higher margins than straight bets.

## Policy notes from the 16 Nov research
- YouTube's inauthentic content guidance (July 2026) names three demonetized categories: generic or repetitive template-looking uploads; unsatisfying or off-putting formulas; AI personas posing as human experts on health, law, finance or politics. Money Map must explain how money works and never give advice as an expert.
- Since 1 Oct 2026 the Shorts feed gives less reach to re-upload channels; original Shorts are favoured.
- Varying the look between videos (ledger board, then Paper) is deliberate, to avoid the channel reading as one template.

## Open items
- Kenny has not yet reviewed these three videos.
- Which betting Short goes out on Tue 17 Nov (old ledger look or the new Paper one).
- When the long video is posted, link it from the Shorts with the related video option.
- Title, description and tags for the long video were given in chat on 16 Nov.
