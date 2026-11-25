# Film Log

Read this before planning a new film. Never delete or shorten older film entries (the 17 Nov 2026 reset below was Kenny's own decision). Project-wide rules (research, policy and repetition gate, hooks, SEO) are in `claude/yt-stats/workflow.md`; topic research is in `claude/small-win-films-research.md`.

Reset on 17 Nov 2026: Kenny restarted Small Win Films from scratch. Film 1 ("For 40 Days, Nobody Stopped", market stall) was deleted from YouTube and film 2 ("I Tried 4 Things to Fix a Bad Day", mechanic) was never posted, so their entries were cleared at his request. Neither film should be posted later as is. The Lessons below were kept because they come from Kenny's feedback and film 1's real numbers.

## Never repeat a design (Kenny, 19 Nov 2026)

Every new video, Short, Reel, cover and thumbnail gets a design not used before: layout, overlays, counter style, hook voice and wording, end card and cover. Reusing an earlier Reel's or Short's layout counts as repeating. Check the "Designs used" list below before building, and add the new design to it after.

### Designs used (vertical cuts and covers)

- Two Cups YouTube Short (17 Nov): letterboxed crop band with sampled top/bottom fill, DAY pill top left, "CUPS MADE" box top right, captions at the bottom, end card "Did he ever make just one cup?" with centred sprout. Cover: scene with big text.
- Bad Day Facebook Reel (18 Nov): same letterboxed crop band and pill/box overlays as the Two Cups Short, am_onyx hook "My boss ruined my day at 8 am. So I tried four things to fix it. Keep count.", re-drawn four-things list, end card with centred sprout over two lines. Cover: scene on top, two-line title on a floor-coloured band below.
- 31 Texts She Never Sent Short and Reel (19 Nov): re-laid-out 9:16 scenes (compose.frame9) with phone-style status pills, af_nicole hook, ink end card with large sprout at the top and three lines. Covers: crying close-up scaled up with outlined two-line text (Short), same with a dark band (Reel).
- Two Cups Facebook Reel (19 Nov): tear-off calendar page top left (cream page, terracotta binding, two rings, big day number, the old page tears away on each new day, pages riffle 40 to 1 on "40 days earlier."); cup tally top right (two yellow cups over "CUPS EVERY MORNING", the second fades to a dashed outline on day 90); scene inside a rounded window with a cream border in the middle; captions on slate below; bm_george hook in two lines ("Every morning, I still make her tea. She's been gone forty days."), cups pulse on "tea"; end card lines inside the same window with the calendar on 90 and one cup, logo and name in a small row at the bottom. Cover: same calendar, tally and window with the cold-open close-up, "2 CUPS." (yellow) and "HE LIVES ALONE." outlined below (first version "SHE'S GONE. HE STILL MAKES HER TEA." was rejected by Kenny for giving the story away).
- "3 alarms" Facebook Reel (21 Nov, "Numbers that say everything" ep 1): no voice, solo piano. Full-bleed flat scenes drawn straight in 9:16 with no counters, pills, windows or calendar. A big phone close-up is the hook device (frame 1: three work alarms ON, a ping per alarm, text "He set 3 alarms for work." then the calendar "No events" and "0 for her birthday."), big rounded outlined text lines in the top third that fade in per beat ("8 pm.", "9 pm.", "10 pm.", "4 alarms.", "Late. But he showed up."), a wall clock for time passing, scenes cut between phone close-ups and room shots. End card: cream-to-apricot ground, sprout logo, "NUMBERS THAT SAY EVERYTHING / EPISODE 1 · 3 ALARMS", "FOLLOW FOR EPISODE 2" pill; loops to the phone. Cover: phone alarm list with "3 ALARMS." and "NOT ONE FOR HER." (no cake, no apology). Engine claude/small-win-numbers-engine/.

## Channel and setup

- Small Win Films, @smallwinfilms001, channel ID UCCBe1BbgfXj4pJqaY_jvg-A. Tagline "Small stories. Small wins." Logo: green sprout in front of an ochre rising sun with short rays, on a cream ground line, on dark green-ink (drawn by `sprout()` in `claude/story-films-engine/brand.py`).
- Channel description: "Small stories. Small wins. / Short animated films about everyday people, the moments that matter, and the little victories that change everything. / New films every week."
- Channel identity across films: font M PLUS Rounded 1c ExtraBold, captions centred at the bottom on a dark gradient band, closing card with the sprout logo and "Small Win Films". Everything else changes per film.
- Each film delivers: long film (1920x1080 mp4, file named after the search keyword), vertical Short (1080x1920 mp4, re-laid-out, not cropped), thumbnail (1280x720 png, matching the opening shot), Short cover (1080x1920 png), and one txt upload pack per video.
- Setup each session: `pip install --break-system-packages pycairo`; font files MPLUSRounded1c-ExtraBold.ttf (and Bold, Medium) from https://raw.githubusercontent.com/google/fonts/main/ofl/mplusrounded1c/ into ~/.fonts, then `fc-cache -f`. Start from the most recent engine (`claude/unsent-engine/`: film.py helpers, scenes.py per-scene functions returning phone/caption/meter state, compose.py 16:9 and 9:16 composers, audio.py piano-and-strings score, vert.py cut lists for the Short and the Facebook Reel; or `claude/two-cups-engine/`, or the older `claude/story-films-engine/`), then redesign character, sets, palette and music. Render one mp4 per scene across two processes on 2 cores, join with the ffmpeg concat demuxer, add audio with -c:v copy. A 3-minute film renders in about 5 minutes; the Short in under 2.
- The Two Cups engine uses the "Rounded Mplus 1c ExtraBold" font: RoundedMplus1c-ExtraBold.ttf from https://raw.githubusercontent.com/google/fonts/main/ofl/roundedmplus1c/ (github.com/.../raw links return 403 here). Kokoro voice files: kokoro-v1.0.onnx and voices-v1.0.bin from the thewh1teagle/kokoro-onnx GitHub release model-files-v1.0, into models/.
- Loudness: normalise the final film and Short to about -16 to -18 LUFS with true peak below -1 dBTP (ffmpeg loudnorm, then check). YouTube only turns loud videos down, so a quiet mix plays quiet. For Reels with a loud voice hook, run alimiter first, then two-pass loudnorm.
- Model use (Kenny, 17 Nov 2026): style tests can run on a cheaper model (Sonnet); full builds on the highest model available (Fable needs paid usage credits on his account; Opus otherwise). Claude checks the output by eye before sending.
- Save each new film's engine code and upload packs to the Project.

## Lessons from past films (these override the blueprint where they conflict)

1. Keep the story literal. No symbols or metaphors (no coat that stands for weight, no creature that stands for a habit). What is on screen is simply what happens.
2. The whole story must fit in one plain sentence a 10-year-old would understand.
3. Tell it in order, from the first day to the last. No reverse, no two timelines, no twist in how it is told. The only exception is the cold open in lesson 13.
4. One ordinary person, one ordinary place, one problem.
5. The antagonist does not need a physical form. The problem can just be the situation (no customers, bad weather, no money, a loss).
6. The meter must be a plain count or label of something real in the story (for example "Customers today: 0"), plus a day or time label.
7. When proposing films, give 3 options, each as one or two plain sentences. Do not show table picks unless asked.
8. The first on-screen line, inside the first 5 seconds, states the problem.
9. The tables in the blueprint are for variety in character, place, palette and music only. Do not let them add story devices.
10. Films do not have to end happily. Keep the ending honest but not hopeless (advertiser-friendly).
11. After Kenny picks a story, send him the full script (scene by scene, with every on-screen line) and wait for his go before drawing anything.
12. Target length is about 3 minutes (winning films in this niche run 3 to 5 minutes; only go to 7+ if the story has enough events).
13. Opening rules (added 17 Nov 2026 after film 1 averaged about 15 seconds of watch time from its first 26 views). The first 15 seconds decide whether people stay:
    a. Cold open: the first 3 to 5 seconds show the exact moment on the thumbnail (same scene, same light, same pose, same big number or word). Then one plain card such as "40 days earlier." and the story runs in order from there. Never open on a scene that looks different from the thumbnail.
    b. Second 0 is already moving and already in trouble. No fade in from a blank colour, no calm establishing shot, no happy normal-life setup before the problem.
    c. First shot is a close-up: the character's face fills at least a third of the frame height so it reads on a phone. Pull back to the wide shot after.
    d. The problem is shown, not only written: the meter starts big in the centre of the screen for the first seconds (for example a large "0"), then shrinks into its corner.
    e. A clear sound starts on frame 1 (a hit, a stop, a voice, a tick), not a soft intro.
    f. In the first 30 seconds, change the picture every 3 to 5 seconds (new shot, cut, or event) and keep beats to 6 to 8 seconds. Longer beats are fine after the first minute.
    g. Do not repeat the same idea in back-to-back beats in the first minute.
    h. Before rendering, Claude draws the first 15 seconds as a strip of stills (one per second) and checks rules a to g.
14. Topics come from research ("research topic for Small Win Films", see claude/yt-stats/workflow.md) and must pass its policy and repetition gate.
15. YouTube chapters need every chapter to be at least 10 seconds; fold short cards into the next chapter.
16. Emotional stories get an emotional soundtrack (Kenny, 19 Nov 2026): a real score with melody, chords and dynamics that follow the story (sparse at the start, a swell at the hardest moment, near silence before the turn, resolution at the end), on the YouTube film, the Short and the Facebook Reel. Only use thumbnails that make people want to watch (a clear emotional face, the story's object, 2 to 3 words).

18. Facebook Reels must fill the whole 9:16 screen edge to edge (19 Nov 2026). The Two Cups Reel, with the scene inside a bordered window with margins on every side, got Meta's warning "There are issues limiting the performance of your post" with Content quality marked down for bordered video; it had 162 views about 5 hours after posting. The Bad Day Reel (scene band running edge to edge, colour-filled above and below) showed "no issues". No inset frames, outlines, picture-in-picture windows or letterbox bars on Reels; overlays go on top of a full-bleed picture. Captions and 9:16 were marked as positives.
17. Thumbnails and covers are cliffhangers, never summaries (Kenny, said several times, last on 19 Nov 2026). The image and its words must open a question the video answers, and must not show or state the outcome, the cause of the problem, or the twist. Ways that work: a contradiction the viewer cannot resolve (two cups, he lives alone), an action frozen before it finishes, a number or count with no explanation, a reaction face without what caused it. Test before sending: if someone could tell the whole story from the thumbnail alone, redo it. The question must be answered early in the video (inside the hook) so retention holds.

## Films

### Reel series: "Numbers that say everything", episode 1 "3 alarms" (Facebook Reel only, 21 Nov 2026)

Facebook-only Reel for the Small Win Films Page, 0:40, 1080x1920, solo piano only, no voice, loops. Planned posting Sun 29 Nov 2026, 4:00 pm Lagos. Engine and pack in `claude/small-win-numbers-engine/` (alarms3.py, piano_loop.py, facebook-pack-3-alarms-reel.txt). Built on Sonnet in build conversation 2 (claude/build-plan-2026-11-21.md).

Story in one sentence: a husband sets three alarms for work but forgets his wife's birthday, and that night he sets a fourth alarm.

Picks:
- Characters (no names, no Nigerian names): husband in his late 30s, blue shirt with red lanyard and badge, medium-brown skin, short black hair; wife, yellow sweater, deep-brown skin, short natural hair.
- Sets: bedroom at dawn with a phone close-up, a sage kitchen with a window and a front door, a dusk dining room with a wall clock, table, cake with one candle and the wife's phone, the bed in the morning.
- Palette: apricot #F6C99B and blush #E9A7A0 (morning), sage kitchen, dusk plum #3B3358 and #261F42 with lamp gold #FFC978 (evening), cream, plum ink #3A2A3D, yellow, blue, red.
- Music: solo piano, G major, 72 bpm, 12 bars = 40.0 s so it loops; three high pings on the alarms (frame 1), calm arpeggios, sparse near-silence when the candle goes out, a single ping for the fourth alarm, a major bloom when he arrives with the cake; door slam, candle breath and chair thud effects. -15.5 LUFS.
- Device: the phone screen (alarm list, then empty calendar, then a fourth row typed "SAY SORRY. BUY CAKE.") is the hook and the loop point.
- Lines: He set 3 alarms for work. / 0 for her birthday. / 8 pm. / 9 pm. / 10 pm. / 4 alarms. / Late. / But he showed up.
- Hook: contradiction, text on frame 1. Gate: passes.
- Known weak spots: characters are front-on and mostly static; the seated poses and the walk-off are simple; Claude could not listen to the score, so Kenny should listen once.

### Film 4: 31 Texts She Never Sent (19 Nov 2026)

Title: "31 Texts She Never Sent | Short Film About Heartbreak". Length 3:00, 16:9, 1080p, 30 fps. YouTube Short 0:34 vertical. Facebook Reel 1:24 vertical with a voiceover hook. Built on Opus 19 Nov 2026. Planned posting (5:30 pm Lagos): film and Facebook Reel Wed 25 Nov, Short Fri 27 Nov; TikTok once the account exists. Engine and packs in `claude/unsent-engine/`.

Story in one sentence: after a breakup, a woman writes her ex a text every night and deletes it, and on night 32 she writes nothing.

Topic research: "short film about heartbreak" 6/7 High, competition Low (0 title matches, 15% big channels); autocomplete "texts i never sent" matches the title. Kenny picked heartbreak and approved option A ("Unsent") on 19 Nov 2026.

Picks:
- Protagonist: woman in her late 20s (first female lead), dark brown skin #6B4530, black twists to the shoulders, mustard cardigan #D9A040 over a cream tee, indigo trousers.
- Others: the ex David (seen from behind carrying a box, and in a party photo on her phone), her friend (terracotta headwrap, teal top, brings takeaway on night 7).
- Set: one small apartment at night: door on the left, plum sofa with coffee table, window with city lights and moon (rain on nights 12 and 31), chair with his grey hoodie, nightstand lamp, bed on the right; box of his things that ends up labelled DONATE by the door.
- Meter: phone-style status pill top right "WRITTEN n · SENT 0" in deep wine red (0, 1, 3, 7, 12, 20, 31); night pill top left (NIGHT 31 cold open, then 1, 3, 7, 12, 20, 31, 32).
- Phone UI insert (chat with David: "Home safe?" / "yes. night"): typing then backspacing letter by letter; party-photo screen on night 12; "Delete contact?" dialog and contact list on night 31.
- Palette: night indigo walls #29304F, floor #33293F, warm lamp #FAC26B, phone glow blue #8CBFFF, tears pale blue.
- Music (first emotional score on the channel): synthesized piano and soft strings with reverb, 66 bpm, A minor, progression Am F C G; motif E5 D5 C5 C5 A4 G4 C5 E5 D5 B4. Sparse single notes in the cold open, gentle arpeggios nights 1 to 7, strings swell and full melody on night 12 (rain), near silence during the long pause on night 31, then a turn to F C G C when she deletes the contact, warm major melody on night 32 and the end card. Effects: typing and delete clicks, door thud, knocks, tape, lamp clicks, rain, room tone. Film -15.4 LUFS.
- Opening line: "I wrote him 31 texts. I sent none." Then "31 nights earlier."
- All lines: I wrote him 31 texts. I sent none. / 31 nights earlier. / Night 1. He's gone. / Night 3. I still worry if he ate. / Night 7. / My friend said: don't text him. / Night 12. He looked happy. / I wrote a whole page. / Night 20. I packed what he left. / Night 31. I didn't send it. / Night 32. I wrote nothing. / It still hurts. / But tonight, I didn't write.
- Texts typed and deleted: Please come back. / Did you eat? / I'm fine. / (long message on night 12) / Do you want your hoodie back? / I miss you.
- Thumbnail: crying close-up on the left, "UNSENT" and "31 NIGHTS" top middle, phone with "I miss you." and a lit send button on the right (left-to-right rule).
- Facebook Reel: voiceover hook af_nicole 0.9 "I wrote him thirty-one texts. I sent none." over the cold open and card (music ducked, voice +2 dB), no voice after; AI label required.
- Known weak spots: characters are front-on only; no real sitting-down motion (cuts between poses); the friend and ex are simple figures; Claude could not listen to the score, so Kenny should listen once.

### Film 3: Two Cups (17 Nov 2026)

Title: "He Still Makes Two Cups | Short Film About Loss". Length 3:00, 16:9, 1080p, 30 fps. Short 0:37 vertical. Delivered 17 Nov 2026; planned posting Wed 18 Nov (film) and Fri 20 Nov (Short), 5:30 pm Lagos. Built on Opus (style test on Sonnet). Engine and upload packs in `claude/two-cups-engine/`.

Story in one sentence: an old man still makes two cups of tea every morning after his wife has died, pours her untouched cup into her plant, and on day 90 makes one cup and sits in her chair for the first time.

Topic research: "short film about loss", High 7/7, long film with a Short cut from it (small-win-films-research.md). Real detail: none given by Kenny; the plant watered with her tea is Claude's.

Picks:
- Protagonist: man in his 70s, rounded-square body, round glasses, retired.
- Antagonist: none (the loss itself).
- Sets: his kitchen (counter, glowing kettle, cup shelf, small table, wall clock), her mustard armchair by a rainy window with her potted plant on the sill, the front door at the kitchen side.
- Story variable: her plant goes from dry to flowered (watered with her cold tea). Rain on the window until day 90, then sun.
- Meter: "CUPS MADE" top right, 2 until day 90, then 1 (big centred "2" in the cold open). Day tag top left (DAY 40 cold open, then DAY 1, 2 to 7, 8, 14, 30, 40, 60, 90).
- Story shape: quiet slow climb after a loss, no setback.
- Palette: rainy slate with yellow.
- Music: guitar-like plucks, 87 bpm, B flat major.
- Text voice: day labels plus a few short lines.
- Ending: him sitting in her chair with one cup and the flowered plant, then a two-line card.

Style fingerprint:
- Protagonist: skin #77502F, short close-cropped white hair with receding temples, white moustache, round black glasses, grey-green cardigan #7B9084 over a cream shirt #F1EBDD, dark trousers #232830, slippers.
- Other people: neighbour woman in her 40s, skin #9A6A45, terracotta dress #B4583A, teal headwrap #2F6B6E with cream diamonds; brings soup on day 14, waves through the window on day 60.
- Colours: wall #5E6B78, dark wall #3E4852, floor #4A535C, rain sky #8C98A4, ink #1E242B, card slate #2A3139; yellow #F2C14E (cups, kettle glow, lamp, flower, sun); armchair #A39A63; leaves #5E9A66 / #86C47E, dry #7A6E3E.
- Music: plucked guitar; first 8 notes F4 D4 Bb3 Eb4 F4 G4 F4 D4. Sparse on day 1, near silence (rain and clock) on day 30, full with a low Bb when he sits in her chair on day 90. Effects: cup clink, kettle, pouring, knock, rain.
- Opening line: "I still make two cups."
- All lines: I still make two cups. / 40 days earlier. / Day 1. / The house is too quiet. / Day 8. / She loved this plant. / Someone sat in the quiet with me. / Day 90. / One cup. / You don't stop missing them. / You learn to sit with it.
- Thumbnail: close-up of him with two yellow cups, big "2", DAY 40 tag, "STILL TWO CUPS".
- Known weak spots: no sitting-down animation on day 90 (cuts to him seated); characters drawn front-on only; figures small in wide shots.

Facebook Reel (19 Nov 2026): vertical 1080x1920, 1:26, -15 LUFS, `reel.py`, `vo.py`, `cover_reel.py` and `facebook-pack-two-cups-reel.txt` in `claude/two-cups-engine/`. Built from the film's own scenes and score (cut list of 20 beats). Calendar design described under "Designs used". Hook: Kokoro bm_george at 0.9, "Every morning, I still make her tea. She's been gone forty days.", score ducked to 0.14 under the voice. AI label required. Posting Fri 20 Nov 2:00 pm Lagos on the Small Win Films Page (phone reminder set). A first draft that reused the Bad Day Reel's layout and voice was thrown away at Kenny's request.

### Film 2: Bad Day (posted on YouTube 17 Nov 2026)

Title: "Nothing Could Fix His Bad Day | Animated Short Film". Kenny chose to post it after all on 17 Nov 2026 evening (3:08, new cold open). Short "Boss Ruined His Day at 8 AM | Bad Day Short Film" (0:37). Engine and packs in `claude/bad-day-engine/` (README has the details).

Story in one sentence: a mechanic's boss shouts at him at 8 am, after work he tries four things to fix the day (favourite food, football with friends, favourite song, a long walk), none work, and he goes to bed.

Picks: mechanic in his 30s, pear body, teal overalls, coral cap; workshop, street, his room; palette coastal teal and sand with coral (#EDE0C4 sand, #2E8087 teal, #E8614D coral, #172933 ink, #BDD9D1 sea green, #F5B861 amber); hand drums, shaker, plucked bass and log drum, 72 bpm D minor, first 8 notes A4 F4 D4 E4 F4 A4 G4 F4; meter "MY DAY: FINE/RUINED" then "I TRIED 0-4 / BETTER? NO"; opening line "I tried four things. Nothing worked."; closing "Not every day can be saved. / Some you just finish."

Thumbnail test (18 Nov 2026): three new thumbnails for Test & compare (A boss "HIS DAY, RUINED", B "NONE WORKED", C "STILL NOT OKAY"), details in `claude/bad-day-engine/thumb-test-bad-day.txt`.

Facebook Reel cut (18 Nov 2026): vertical 1080x1920, 1:27 (`reel.py`, `vo.py`, `cover.py` in `claude/bad-day-engine/`). Kenny asked for Facebook versions to be vertical and shorter, with a voiceover only in the opening hook. Hook: Kokoro am_onyx says "My boss ruined my day at 8 am. So I tried four things to fix it. Keep count." with matching on-screen lines and the counter at 0 (meter forced to "I TRIED" from frame 1). Scene sound (including the boss shouting) ducked to 0.10 under the voice, and the voice is set about 2 dB louder than the rest of the Reel (Kenny said the first mix buried it). Each attempt keeps its start and its "didn't work" moment; the four-things list and ending were re-drawn for vertical. -15 LUFS. AI label required on Facebook and TikTok because of the realistic voice. Pack: `facebook-pack-bad-day-reel.txt`.

## Facebook versions (rule from 18 Nov 2026)

For Facebook Reels, each film gets a vertical cut of about 1:20 to 1:30 built from the film's own engine with a cut list (newest: `claude/two-cups-engine/reel.py` and `claude/unsent-engine/vert.py`; older: `claude/bad-day-engine/reel.py`): a 6 to 8 second hook with voiceover only at the start (Kokoro, a voice that fits the character and has not been used for a hook before), same words on screen, then the story trimmed to each beat's key moment, then the film's ending re-laid-out for vertical. Plus a 1080x1920 cover and one Facebook/TikTok pack. The vertical layout, overlays, end card and cover must be new for every Reel (see "Never repeat a design").

Since 21 Nov 2026 (analytics lessons): Facebook-only Reels are 40 to 60 seconds, text-led and music-only (series "Numbers that say everything", engine `claude/small-win-numbers-engine/`), with the payoff before 0:45 and an end card that names the series and asks to follow for the next episode.
