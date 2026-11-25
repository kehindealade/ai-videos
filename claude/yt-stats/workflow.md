# YouTube research and SEO workflow (free, replaces vidIQ when credits are out)

Set up 17 Nov 2026. Tool: `claude/yt-stats/yt.py` (Python standard library only, no installs). It uses Kenny's own Google Cloud project "yt-stats" (project number 173387542667) with YouTube Data API v3 and YouTube Analytics API enabled, a Desktop OAuth client, and read-only scopes. Use vidIQ as well when it has credits (it adds search volumes and title scores).

## RULES (Kenny, 17 Nov 2026; apply to every channel in this Project)

1. Before deciding the next video for Money Map OR Small Win Films, always do keyword research AND check what is trending right now, and show Kenny the findings with the proposed topics. Never pick a topic by feel.
2. TRIGGER: when Kenny says "research topic for <channel name>" (Money Map or Small Win Films), run the "Topic research" procedure below in full, without asking first.
3. Every topic, story and video must pass the "Policy and repetition gate" below. If a topic cannot be made clearly inside YouTube's rules, drop it or change the angle until it is, and say so. Never propose a topic or story that repeats an earlier one on either channel.
4. Every upload pack (long video and each Short) is written SEO-first: run `seo` for the video's main keyword, then write the title, description, tags and hashtags by the SEO rules below, and add an "SEO check" section to the upload pack listing the primary keyword, the secondary keywords and where each appears.
5. Every video gets a hook (long videos, Shorts, story films, explainers, both channels), built by the "Hook rules" below, and every script shown to Kenny names its hook in one line before the first scene.
6. Go for the keyword gap (added 17 Nov 2026 evening): pick keywords that people are searching and watching now (demand) but that few videos already target (low competition). Every topic proposed shows both a demand score and a competition level, and the shortlist is ranked by demand and low competition together. A keyword with high demand and high competition is only proposed with a clearly different angle, and is marked "crowded". Timely news topics are welcome when the story is confirmed by news sources, and must be posted within about a week, before the window closes.
7. Every thumbnail (long videos and Short covers, both channels, every Test & compare variant) is laid out by the "Thumbnail rules" below, and passes the thumbnail check before it is sent (added 18 Nov 2026).
8. Analytics lessons (added 21 Nov 2026): every new video on every platform (YouTube long, Shorts, Facebook Reels, TikTok) follows `claude/analytics-lessons.md`: dramatic first frame with on-screen question text, film cold opens of 5 seconds or less, phone-first framing and text, Reels and TikToks of 45 to 60 seconds with the payoff before 0:45, 2 or 3 Shorts per long video, evergreen searchable topics for Money Map long videos (news as Shorts and Reels only), a reason to follow on every end card, and the post-publish numbers logged against the baseline. Every script and build plan shown to Kenny states in one line how it meets these. Re-read the doc before planning or building any video, and add new lessons to it after each analytics review.
9. Upload checklist (added 21 Nov 2026): every YouTube upload (long video and each Short, both channels) follows `claude/upload-checklist.md`: file renamed to the primary keyword, clean first 8 seconds, no trending or licensed music in Shorts, desktop upload as Unlisted, language English (United States), not made for kids, wait for green Copyright and Ad suitability checks, then Scheduled at the posting-timetable slot. Every upload pack ends with an "UPLOAD STEPS" block filled in for that video. ASK FIRST (Kenny, 21 Nov 2026): the free steps are applied without asking, but before applying anything that would change a video's content (music, the opening 8 seconds, length), push a post past its timetable slot, conflict with another rule in this file, or that Claude judges major and unadvisable, ask Kenny one short question saying what would change and why it is unadvisable, and wait; in an unattended run keep the video as planned and put the question in the upload pack. The checklist's pay claims are mostly unproven, so never state them as fact in a pack or reply. The same doc has optional narration audio polish (quiet room-tone bed, uneven pacing), OK'd 22 Nov 2026 as long as it adds no generation runs or re-renders.
10. Voices (added 22 Nov 2026): every new video, Short, Reel or film hook that has a voice follows `claude/voice-rules.md`: a voice never used before on either channel, picked at random from the unused Kokoro voices (blend two voices when none are left), a different voice for each Short and each platform cut of the same video, and random, normal human expression in the delivery (random base speed, small per-line speed offsets, varied gaps, a mood tag per line, light natural fillers, no typed laughs or sounds). All of it is done in the single voice generation, with no extra generation runs or re-renders, and no re-voicing of videos already made. Log each video's voice in the channel's log and update the used list in the voice doc. Read the voice doc before writing any narrated script, since the script is shaped for it.

## Hook rules (every video, every channel)

A hook here means: within the first 3 seconds the viewer sees something specific and real that makes them ask a question, and the video starts answering it. It does not mean clickbait, shouting or a promise the video does not keep.

All videos:
- Decide the thumbnail moment first. The video opens on that same moment (same picture, same number or word), so the click and the first second match.
- Second 0 is already moving, with a clear sound on frame 1. No logo, no "welcome back", no fade in from a blank colour, no slow scene-setting.
- The first line (spoken or on screen) states the problem, the tension or the surprising number in 8 words or fewer.
- In the first 30 seconds the picture changes every 3 to 5 seconds (every 2 to 3 seconds for story films, per claude/analytics-lessons.md). No idea is repeated in back-to-back beats in the first minute.
- Pay the hook off: the question raised in second 3 is answered by the end, and the title promises only what the video delivers.
- Before rendering, draw the first 15 seconds as a strip of stills (one per second) and check every rule above.

Story films (Small Win Films): cold open on the thumbnail moment for at most 5 seconds, then one plain card ("Six months earlier.") and the story in order; first shot is a close-up with the face at least a third of the frame height; the meter starts big in the centre, then shrinks to its corner. Quiet films still hook: a specific, strange-but-real detail ("I still make two cups.") rather than drama. Full details: lesson 13 in `claude/film-log.md` and the opening rules in `claude/story-films-blueprint.md`.

Explainers (Money Map): open with one of conflict, a shocking number, an unexpected outcome or the biggest question (logged as "Hook" in `claude/money-map-style-log.md`; never the same hook type twice in a row).

Shorts: the hook is the first 1 to 2 seconds and must work with the sound off (big on-screen text or an obvious action); the last line loops back to or answers the first.

Hook check after posting: the retention curve in `report` shows how many stayed past second 15 and second 30. If most leave in the first 15 seconds, the next video changes its hook type.

## Thumbnail rules (every thumbnail, every channel; added 18 Nov 2026)

How people look at a thumbnail: the eye goes to a face first (eyes within the face), then scans like reading, in a Z: top-left, across to top-right, then down to bottom-right. The click-or-skip decision takes under a second, and most viewers see the thumbnail small (phone feed, suggested list beside another video, or a TV seen from across the room).

Layout (1280x720 canvas):
- Left to right tells the story. The left side holds what the eye should meet first: the cause, the question or the "before" (usually the face with clear emotion). The right side holds the answer, the twist or the "after" (the object, the result, the text). Example: Two Cups A, sad face on the left, her empty chair and steaming cup plus "HER CUP" on the right.
- Text goes in the upper half, in one block (2 to 4 words, at least 90 px tall), on the side opposite the face or across the top. Text never covers the face. The text says something the title does not (see SEO rules).
- When a face looks sideways, it looks toward the text or the key object, never off the edge of the frame.
- One clear idea and at most three elements (face, object, text). The face fills at least a third of the height.

Danger zones (keep text, faces and the key object out):
- Bottom-right, about 260 x 110 px (x 1020 to 1280, y 610 to 720): YouTube's duration badge always covers it. Only background goes there.
- Top-right, about 70 x 70 px (x 1210 to 1280, y 0 to 70): the menu dots and queue icons on hover.
- The bottom edge, about 12 px: the red progress bar on watched videos.
- Keep a margin of about 40 px from every edge for all text.

Short covers (1080x1920): the same left-to-right order inside the centre, and the hook text in the upper-middle third, clear of the bottom 25% (title, channel name and buttons sit there) and the right edge (like, comment and share buttons).

Thumbnail check (before sending any thumbnail):
1. Render it, then run `python3 thumbcheck.py <thumb.png>` (in `claude/yt-stats/`, works for 1280x720 thumbnails and 1080x1920 Short covers). It writes `<name>-zones.png` (danger zones in red and orange, the 40 px text margin in cyan) and `<name>-320.png`. Look at the zones copy: nothing important inside them.
2. Look at the 320 px copy: the face, the emotion and the words still read in one second.
3. Read it left to right: does it tell the start and the end of the story, together with the title?
4. Variants for Test & compare change one thing at a time where possible (text, or which side the face is on), so the result teaches something. Left-to-right is the default, not a law: if a test shows the face-on-the-right version winning, log it in the channel's log and use that order for the next similar video.

## Policy and repetition gate (checked before proposing any topic, story or script)

YouTube's rules this gate follows (checked 17 Nov 2026; re-check the Help Centre if a topic is borderline):
- YPP "inauthentic content" (renamed from "repetitious content" on 15 Jul 2025): mass-produced, templated or repetitive videos are not eligible for monetization, however they are made. Original creative input is required.
- Advertiser-friendly content guidelines: sensitive subjects (death, grief, conflict, crime) can earn full ads when dramatized, non-graphic and not shocking. Graphic or shocking treatment gets limited or no ads.

Repetition checks (all must pass):
- The topic, story, person, place and angle are not already in `claude/film-log.md` (Small Win Films) or `claude/money-map-style-log.md` (Money Map), including unposted and deleted videos.
- The look, colours, music, structure, hook type and on-screen text style differ from earlier videos, as each log's rules require. No "same template, new topic".
- Titles, descriptions and tags are written new every time; no reused description text.
- Shorts are cut or made with new framing, not the same clip reposted.
- Avoid the crowded copycat pattern noted in research (e.g. "WORD | A Motivational Animated Short Film").

Monetization checks (all must pass):
- No suicide or self-harm, abuse, sexual content, drugs, weapons, graphic injury, real tragedies or named real people, hate or harassment, profanity.
- Death and grief: never show the moment of death, a body, illness detail or a funeral scene in close-up; tell the story after the loss, quietly. No infant or child death.
- Children: no story centred on minors or school life (risks "made for kids" and low ad rates); adults only.
- Money Map: no financial advice presented as fact, no gambling promotion, every figure sourced.
- Political topics (elections, parties, tariffs and similar) are skipped on both channels even when demand is high.
- No misleading titles, thumbnails or hooks; the title and the opening are what the video delivers.

State the gate result in one line whenever proposing topics or stories ("Gate: passes" or what was changed to make it pass). This lowers risk; YouTube makes the final call, so never promise monetization.

## Topic research (the "research topic for <channel>" procedure)

1. Set up (see Setup) and read the channel's research doc and log: Small Win Films → `claude/small-win-films-research.md` and `claude/film-log.md`; Money Map → `claude/money-map-research.md` and `claude/money-map-style-log.md`. Also read `claude/analytics-lessons.md`. Skip topics already made, and note topics an earlier scan already marked crowded or weak.
2. Find what people are typing right now (free, no quota): run `suggest` on broad pattern phrases for the channel's lane, not only on exact topics. Money Map patterns: "how makes money", "how does make money", "how do they make money", "why is so expensive", "who pays for", "where does the money go", "the business of". Small Win Films patterns: "short film about", "animated short film", "relatable animation". Note any phrase that looks timely (a product, a price spike, a news event); these are the trend candidates.
3. Build 15 to 25 seed phrases: start from `claude/yt-stats/seeds-<smallwin|moneymap>.txt`, drop ones already made, add the trend candidates from step 2, and add evergreen keywords known to have demand and low competition (from vidIQ when it has credits, or earlier research in the channel's research doc). Seeds must be phrases people type (e.g. "short film about loss", "how dollar stores make money"). Save the list as `seeds-<channel>-<date>.txt`. Keep it to about 25 seeds or fewer so a scan plus the seo runs stay inside the daily quota.
4. Run `python3 yt.py scan <label> <seeds file>` (about 205 quota units per seed). For each seed it measures:
   - Demand:
     - autocomplete depth (how many suggestions the phrase has),
     - small-channel wins in the last 12 months (videos with 3x or more their channel's average and at least 1,000 views, channels under 50k subscribers), split long and Shorts,
     - what is hot now (top views per hour in the last 14 days), split long and Shorts.
   - Competition (added 17 Nov 2026):
     - title match: how many of the top 50 results from the last 12 months already have the keyword's main words in their title (saturation),
     - big share: the share of the top 20 results from channels over 500k subscribers (how hard it is to outrank).
     - Competition level: Low = title match 12 or under AND big share 25% or under; High = title match 30 or more OR big share 50% or more; Medium = everything else.
   It prints a demand score out of 7, a confidence level (High 6 to 7, Medium 4 to 5, Low 0 to 3), the competition level with both numbers, and a format suggestion, and saves `out/scan_<file>.csv` with the best example videos.
5. Read the result as a gap table:
   - Best: High or Medium demand with Low or Medium competition.
   - A gap inside a keyword: if small channels win only with Shorts and no small-channel long video wins exist (or the reverse), the missing format is the opening. Say so.
   - Crowded: High demand and High competition. Propose only with a clearly different angle, marked "crowded". If one breakout video has recently made many channels copy its exact title phrase (a sudden jump in title match), treat the phrase as saturated.
   - Weak: Low demand. Drop, whatever the competition.
6. Sanity-check each result by hand: drop seeds whose wins are off-topic noise (music, sport, game clips, kids' content, unrelated news, meme clips, look-alike words such as travel visas for "visa"), and adjust the format when the examples say otherwise.
7. Confirm every timely topic with a web search of recent news before proposing it (the story must be real, current and sourceable), and note how long the window is likely to stay open. Per claude/analytics-lessons.md, news topics on Money Map are proposed as Shorts and Reels unless the scan shows low competition for a long video.
8. Run every remaining topic through the Policy and repetition gate. Drop or re-angle any that fail.
9. For the top 2 or 3, run `python3 yt.py seo <label> "<keyword>"`. If it returns 0 videos, try the closest autocomplete wording (e.g. "how dollar stores make money" instead of "how dollar tree makes money").
10. Reply to Kenny with 4 to 8 topics, best first, ranked by demand and low competition together. For each: the topic, demand (High, Medium or Low, with the score), competition (Low, Medium or High, with the title match and big share), the format (Short, long video with Shorts cut from it, or a Shorts series), the evidence in one line (autocomplete phrase, best small-channel win with its multiple, what is hot now, and for timely topics the news behind it), the gap if there is one, a one-line angle in the channel's style with its hook (Money Map: a hook type different from the last video's), and the gate result. Then list what changed from earlier plans (topics now crowded, dropped or skipped by the gate, with the reason). Then recommend one and wait for his pick.
11. Save the full scan results, the shortlist and the seo notes into the channel's research doc in the Project, save any change to yt.py back to the Project, and update project memory.

## Setup in a new chat

1. Copy `claude/yt-stats/yt.py` and `claude/yt-stats/yt-signin.txt` from the Project into one working folder. The script unpacks the client and saved sign-ins from yt-signin.txt by itself. No sign-in needed.
2. Saved sign-ins (labels): `smallwin` = Small Win Films (@smallwinfilms001). Money Map is not signed in yet. Any label works for research commands (suggest, outliers, trending, scan, seo); only `report` needs the channel's own label.
3. To add a channel: `python3 yt.py auth-url`, Kenny opens the link with the account that owns the channel and pastes back the "http://localhost/?code=..." address, then `python3 yt.py exchange <label> '<pasted address>'`. Then rebuild yt-signin.txt (`{"client": <client.json>, "tokens": {label: {"refresh_token": ...}}}`) and save it back to the Project at the same path.
4. If Kenny revokes access (myaccount.google.com/permissions) or resets the client, sign in again.

Quota: 10,000 units a day per project. A scan costs about 205 units per seed, a report about 20, an outlier search about 105, a trending search about 101, an seo run about 101, a trending chart 1. Autocomplete is free. A 22-seed scan plus four seo runs used about 4,900 units on 17 Nov 2026.

## Commands

- `suggest "<seed>"`: YouTube autocomplete, expanded with a to z and why/how/what/is. No volumes.
- `outliers <label> "<topic>" <max channel subs> long|short [months]`: top 50 results, each video's views divided by its channel's average ("outlier_x").
- `trending <label> ALL x "<topic>"`: videos on the topic from the last 14 days, by views per hour.
- `trending <label> <region> <film|people|entertainment|education|howto|comedy|all>`: YouTube's trending chart for a country and category. As of 17 Nov 2026 the category charts return "not found" (YouTube retired them); use `trending <label> ALL x "<topic>"` and the scan's "hot now" instead.
- `scan <label> <seeds file>`: the topic research scorer described above (demand score, competition level with title match and big share, format, examples).
- `seo <label> "<primary keyword>" [region]`: the top 25 ranking videos' most used tags (weighted by views), title words and phrases, how many use chapters, median description length, plus autocomplete around the keyword.
- `report <label> [start] [end]`: own-channel analytics (see After posting). Note (21 Nov 2026): the per-video query with likes and shares returned "query not supported"; per-video works with views, estimatedMinutesWatched, averageViewDuration, averageViewPercentage, subscribersGained. Analytics data lags about 2 to 3 days, so use Kenny's Studio screenshots for the newest days.

## SEO rules

- Ignore off-topic noise in the seo tags (for example news, politics, comedy, streamer clip or horror tags from unrelated videos that rank for the same words).
- Primary keyword: the top autocomplete phrase that fits the video (e.g. "how visa makes money", "short film about loss", "relatable animation"). Prefer the wording with the lowest competition when two wordings have similar demand.
- Title: primary keyword (or its closest natural wording) in the first 40 characters, total under 60 characters, plus a hook or number that matches the video. No claims the video does not deliver (misleading metadata breaks YouTube policy). Do not copy a phrase the scan marked saturated word for word.
- Description: the first two lines (about 150 characters) contain the primary keyword and the promise, since search shows them. Then 150 to 300 words in plain sentences using 2 to 4 secondary keywords from autocomplete and the seo output once or twice each. Then chapters for long videos (first at 0:00, at least 3, each at least 10 seconds, names that contain keywords). Money Map adds sources. End with 2 or 3 hashtags; the first 3 show above the title. No keyword lists or repetition (keyword stuffing breaks YouTube policy).
- Tags: 10 to 15 tags, under 500 characters in total. First tag = exact primary keyword. Then autocomplete variations, then the relevant top tags from the seo output, then the channel name. No tags unrelated to the video.
- Hashtags: 2 or 3, relevant only. Shorts add #shorts.
- File name: rename the video file to the primary keyword before upload (e.g. how-visa-makes-money.mp4); this is step 1 of `claude/upload-checklist.md`, which also covers the rest of the upload routine (rule 9).
- Captions: upload an .srt with the video when there is narration (Money Map). Write it from the script and its timings.
- Thumbnail text: different words from the title; together they tell the story. The thumbnail shows the hook moment the video opens on. Layout follows the Thumbnail rules above.
- Playlist: add the video to a playlist named with a broad keyword (e.g. "How Companies Make Money", "Relatable Animated Short Films").
- Pinned comment: a question about the video's topic to start replies.
- Settings: language English, caption language English, category (Money Map: Education; Small Win Films: Film & Animation), not made for kids, altered content No.

## Titles

- Model titles on the highest outlier_x and trending titles (same promise, different words) and the SEO rules above. Score with vidIQ when it has credits.
- After posting, use YouTube Studio "Test & compare" (free) to A/B test titles or thumbnails.

## After posting

- 48 hours after a video goes up, run `python3 yt.py report <label> <start> <end>`. Files land in `out/<label>/`: videos, per_video, daily, traffic, search_terms, countries, devices, content_type and one retention curve per video.
- Read retention first (does the hook hold past 15 and 30 seconds), then traffic and search terms (which words found it). Feed the search terms back into the next video's SEO and the next scan's seeds. Log in money-map-style-log.md or film-log.md, and compare against the baseline in claude/analytics-lessons.md (add new lessons there). Also note the viewer countries and Shorts RPM (upload-checklist step 10).
- When a Test & compare finishes, log the winning thumbnail and what made it different (text, side of the face, colour) in the channel's log, and apply it to the Thumbnail rules if it holds twice.

## Not covered

- Thumbnail click rate, Shorts stayed versus swiped, and all Facebook numbers (3-second views, 1-minute views, follows): Kenny sends YouTube Studio and Facebook screenshots.
- Search volume numbers and title or thumbnail scores: vidIQ only. When vidIQ has credits, add its keyword research (volume and competition score) for the top picks and use it to confirm the free competition level.
