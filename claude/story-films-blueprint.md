# Story Films Blueprint (v1.2)

Paste this whole document into a new chat in this Project. Add one line at the end: either "Topic: <your topic>" or "Surprise me". Everything else is decided by the roll in Step 2.

## What you are making

An original 2D animated short film with no narrator, drawn entirely with code (flat vector shapes). No stock assets, no AI video or image model, no sampled audio. Tools: Python, pycairo for frames, numpy for audio, ffmpeg for encoding. CPU rendering is fine.

Main film: 16:9, 1920x1080, 30fps, 2.5 to 4 minutes.
Companion Short: 9:16, 1080x1920, 30 to 45 seconds, re-laid-out from the same scenes (not a crop), covering the hook and the spiral and ending on a question.

## Step 1: Read the log

Read `claude/film-log.md` in this Project if it exists. It holds the roll and the style fingerprint of every past film, plus a Lessons section that overrides this blueprint where they conflict. If it does not exist, treat the log as empty. If you cannot read it, stop and tell me instead of guessing.

## Step 2: Roll the film

Run real code to pick (Python `random`, seeded from the current timestamp). Do not choose by taste. Pick one item from each table below.

Reroll rules:
1. Reroll any pick that appears in the last 3 films in the log.
2. The new film must differ from each of the last 3 films in at least 7 of the 11 tables, and always in tables C, D, E and G.
3. If a pick clearly clashes with the topic, reroll that one table once.
4. If I gave a topic, skip table A.
5. After rolling, compare your planned look against every style fingerprint in the log (not only the last 3). The protagonist, the antagonist, the main colours and the melody must not resemble any past film. If they do, redesign before showing me the card.

A. Theme: procrastination, debt, comparing yourself to others, burnout, perfectionism, people-pleasing, overspending, clutter, sleep debt, saying yes to everything, fear of starting, holding a grudge, chasing status, never resting, avoiding a hard conversation, quitting too early.

B. Protagonist (roll each part separately):
- Body shape: round, tall rectangle, bean, pear, soft triangle, rounded square.
- Signature item: jumper, scarf, cap, glasses, apron, backpack, headwrap, tool belt.
- Life: student, market trader, nurse, delivery rider, tailor, teacher, cook, mechanic, new parent, retiree, farmer, musician.
- Vary gender, age (adults only) and skin tone from film to film.

C. Antagonist form: small creature that grows, household object that comes alive, shadow twin, cloud or fog, creeping vine, a pile that builds itself, a smooth-talking salesman, a mirror reflection, a slow leak of water, a sound wave or echo, a heavy coat, a second sun.

D. Setting (build at most 3 sets from it): one-room flat, market stall, bus commute, workshop, kitchen, rooftop, family compound, open-plan office, classroom, fishing jetty, greenhouse, lighthouse, night food stand, small farm.

E. Story variable (the one thing that changes gradually across the whole film): antagonist grows, room shrinks, clutter piles up, light temperature shifts, weather worsens, water level rises, plants wilt then regrow, clock speeds up, distance between two characters widens, the character sinks lower in frame, the window view changes season, cracks spread across a wall.

F. Meter (small, always on screen, reacts to every event, gets one full-screen moment): card stack, battery, coin jar, thermometer, fuel gauge, hourglass, potted plant, thread spool, candle, bridge planks, tally marks, water tank.

G. Story shape:
- Fall and climb: normal life, hook, spiral, bottom, slow climb, moral.
- Near miss: the spiral starts, the character catches it early, most of the film is the hard choice.
- Relapse: climb, slip, climb again.
- Two lives: the same day shown twice with one different choice.
- Reverse: open at the bottom, tell it backwards to the first small choice.
- The swap: the character gets out by helping someone else who is deeper in.
- Living with it: the antagonist never leaves, it just gets small enough to carry.

H. Palette: warm paper daylight, night indigo with amber, clay and sage, coastal teal and sand, dusty harmattan peach, soft pastel, ink on kraft paper, rainy slate with yellow.

I. Music: plucked marimba, soft piano tones, kalimba, pads with bells, guitar-like plucks, hand percussion with bass, music box, whistled lead. Also roll a tempo (70 to 120 bpm) and a key.

J. Text voice: third person past tense, second person ("you"), first person diary, day counter labels only, questions only, silent until the midpoint.

K. Ending: two-line moral on a title card, one-word title that gets crossed out and rewritten, the meter refilled with no words, the opening shot repeated with one change, a line handed to the viewer as a question.

## Step 3: Show me the film card and wait

Before drawing anything, show me one short card: the title, the roll (A to K), a one-sentence story, and the beat list (one line per beat). I can swap any item. Also ask me for one real detail from my own life or something I have observed that fits the theme, and build it into the story. Do not start until I approve the card.

## Opening rules (the first 15 seconds)

Film 1 lost most viewers in its first 15 seconds. Every film must follow these:

1. Decide the thumbnail moment first, before writing the script. The film opens on that exact moment (same scene, light, pose and big number or word) for 3 to 5 seconds, then one plain card such as "40 days earlier." and the story runs in order from there.
2. Second 0 is already moving and already in trouble. No fade in from a blank colour, no calm establishing shot, no happy normal-life setup before the problem.
3. The first shot is a close-up: the character's face fills at least a third of the frame height. Go wide after.
4. Show the problem, do not only write it. The meter starts big in the centre for the first seconds, then shrinks into its corner.
5. A clear sound on frame 1 (a hit, a stop, a voice, a tick), not a soft intro.
6. In the first 30 seconds the picture changes every 3 to 5 seconds, and beats are 6 to 8 seconds. Longer beats are fine after the first minute.
7. Never repeat the same idea in back-to-back beats in the first minute.
8. Before rendering, draw the first 15 seconds as a strip of 15 stills (one per second) and check rules 1 to 7. The vertical Short follows the same rules.

## Fixed rules (never change these)

Story:
- Show the main idea in the first 5 seconds. No slow intro, no logo first.
- 10 to 14 beats of 10 to 18 seconds after the first minute (see Opening rules for the first 30 seconds).
- The antagonist always has a physical form, unless the log's Lessons say otherwise.
- The story variable must be readable with the sound off.

Visuals:
- One newly designed protagonist per film, built from the roll, with 5 expressions.
- At most 3 sets, relit per beat.
- Never use these devices: colours draining to grey, a dopamine line graph, a phone as the villain, a pale blob figure. They belong to another creator's film.
- No real people, brands, logos or existing characters.

Text:
- No narrator.
- On-screen lines of 8 words or fewer, each held at least 2.5 seconds, one idea at a time.
- Simple enough for a non-native English reader.

Sound:
- Compose new music in code for every film, following the arc (full, thinning, near silence at the lowest point, rebuilding). Never reuse a melody from a past film.
- Synthesized sound effects only.

Channel identity (the only things that stay the same across films):
- The same font, the same caption style and the same closing sign-off card.

## Monetization rules (YouTube)

1. No two films may feel like the same template with the topic swapped. The reroll rules above enforce this. If the card looks close to a past film, say so and reroll.
2. Every film needs my own input (the real detail from Step 3). Do not skip it.
3. Keep every topic advertiser-friendly. No self-harm, drugs, graphic injury, or medical or financial advice presented as fact.
4. Write a unique title, description and tags for each film. Never reuse description text between videos.
5. In descriptions, say the film is animated with code. Never claim it is hand-drawn.
6. Stylized animation does not need YouTube's altered-content label. If a film ever includes a realistic voice or image of a real person, stop and tell me.
7. The long film is the main upload because only long-form watch time counts toward the watch-hours route. The Short is for discovery and links to the long film.
8. Aim for 3 to 4 minutes when the story can carry it. Do not pad.

## Step 4: Style test

Make 3 full-size stills (the most crowded moments), the 15-still opening strip, and one 10-second clip with sound. Look at the stills yourself before sending. Wait for my approval.

## Step 5: Full film

- Draw a few frames per scene at full size and check them before rendering.
- Render one file per scene, join them, then add sound.
- Check the final file: duration, resolution, and that audio is present and not clipping.
- Then make the vertical Short from the same scene code.

## Step 6: Deliver

Send only:
1. The long film (mp4).
2. The Short (mp4).
3. The thumbnail, matching the opening shot.
4. An upload pack in the reply: title (under 60 characters), description, chapters, tags, and the Short's title.

## Step 7: Update the log (required, do this before you say the film is done)

Read `claude/film-log.md`, add a new entry at the end, and write the whole file back. Never delete or shorten older entries. Each entry holds:

1. Date and film title.
2. The roll: picks A to K.
3. Style fingerprint:
   - Protagonist: shape, clothing, colours, hair or headwear.
   - Antagonist: what it is, its shape and colour.
   - Sets: the 1 to 3 places and their key objects.
   - Colours: the 5 main hex codes.
   - Music: instrument, tempo, key, and the first 8 notes of the main melody.
   - Opening line and closing line of on-screen text.
4. The real detail I gave in Step 3.

Tell me in one line that the log was updated. If the write fails, tell me and paste the entry in the reply so I can save it myself.
