# Readability and retention rules (vertical video, Reels, Shorts, thumbnails, covers)

Written 22 Nov 2026 after Kenny said the Thanksgiving Reel's caption card and cover were hard to read because the text sat at the top. Applies to every new video, Short, Reel, cover and thumbnail on both channels. It supersedes the "upper-middle third" wording for Short covers in claude/yt-stats/workflow.md and adds to claude/vertical-video-rules.md and claude/analytics-lessons.md. Do not re-edit videos already made.

## What went wrong

The Thanksgiving Reel put its headline card at y 95 to 285 of 1920 (5% to 15% from the top) and the cover did the same. Meta's unified 9:16 safe zone (March 2026) reserves about the top 14% (about 270 px), the bottom 20 to 35% and about 6% on each side for the app's own interface. The text sat under the profile and title area.

## 1. Where text goes on a 1080x1920 vertical video

- Safe band for ALL essential text (headline, caption, numbers, prices, calls to action): y 300 to 1340, x 90 to 990. One guide gives a readable band of 20% to 70% from the top (y 384 to 1344); Meta's zones are top 14%, bottom 20 to 35%, sides 6%.
- Best spots: counters and big numbers y 300 to 520; the main caption or headline card y 1100 to 1300 (57% to 68% from the top), like the classic caption position; a cover's question block y 384 to 900.
- Never essential text in the top 270 px (profile, title, follow button), the bottom 400 px (caption, buttons, audio), or the right 70 px; keep x under 960 below y 1000 (like, comment and share buttons).
- Decoration (wordmark, leaves, plates) may sit in the danger zones; information may not.
- Check every key frame with the safe-zone overlay (draw the zones in red on a still) and at phone size (about 390 px wide) before rendering. Preview on a real phone when possible; desktop previews hide the overlap.

## 2. Making text readable

- Font: bold sans-serif, never script or decorative. At 1080x1920 the minimum for captions and headlines is 48 px, 52 to 60 px is typical; Kenny's cards use 58 to 78 px.
- Maximum 32 characters per line and 2 lines on screen at once; one or two short sentences per caption chunk.
- Contrast at least 4.5:1 between text and its background (WCAG AA). Light text on a dark semi-transparent or solid box, or dark text on a light card. Put a box behind text whenever the picture behind is busy. Check coloured text: orange on cream failed (3:1), so use deep red-brown (about 5:1).
- Timing: each caption shows at least 1.2 s, fades in over about 0.2 s, reading speed 160 to 180 words per minute; sync to audio within 100 ms when narrated.
- One idea per screen. Text says something the picture does not.
- Sound-off first: a Reel must make sense with the sound off (one guide claims over 85% of social video is watched without sound; uncited, so treat it as direction, not fact).

## 3. Thumbnails and covers: how people look

- Eye tracking (ETRA 2018, thumbnails vs title text): people gave nearly twice as much attention to the thumbnail as to the title and looked at the image first. So the picture must carry the pull and the text must be a few words.
- vidIQ study of 500 breakout thumbnails (June 2026, long-form, channels over 10k subs): 69% a human face (80% of the top 50), 89% face or high contrast, 72% had overlay text, median 5 words, 1 to 3 words the most common bucket (24%). Caveats from vidIQ itself: correlation, not proof; breakouts succeed for many reasons.
- Other guides agree: 3 to 5 words that add to the title instead of repeating it, large bold sans-serif, contrast at least 4.5:1, one clear idea, leave room for text, expressive faces looking toward the text or key object.
- Curiosity gap (the mechanism behind clicks): show what is known, hide what the viewer wants to know. The cover raises a question the video answers early; it never shows the answer. Accurate intrigue wins; confusion and false promises lose.
- Our standing rules still apply: left to right story, text opposite the face, cliffhanger covers, duration-badge danger zones for 16:9 thumbnails (claude/yt-stats/workflow.md, Thumbnail rules).
- For 9:16 covers and first frames: the question or claim in 3 to 5 words, in the band of section 1, in a high-contrast box, with the picture of the thing the question is about; the answer (number, name, twist) is blank or masked ("$??.??").
- No face-based claims for Money Map unless a face exists; use the object people recognise at 320 px (turkey, receipt, coin) as the focal point.

## 4. Retention techniques (short-form)

- The decision to stay or swipe is made in about 1.5 to 3 seconds. Frame 1 must already move and already pose the question.
- Hook archetypes: curiosity gap, pattern interrupt, bold claim, relatable pain point, visual shock. Start mid-thought or mid-action; verb first.
- Open loops: raise a question, delay the answer, and open a second loop before closing the first ("the turkey is 40%... now watch the rest").
- Pattern interrupt every few seconds: a new object, a counter jump, a punch-in of about 10%, a sound.
- Make the ending flow into the beginning so it loops (seamless loops raise replays).
- Pay off the hook before the viewer's patience ends: in Reels before 0:20 for the main answer, with extra context after.
- A claim from Facebook research that 65% of people who watch 3 seconds continue to 10 seconds (30 seconds: 45%) is repeated by blogs without a primary source; use it only as direction. Kenny's own Reels data (3-second hold 22% to 27%, claude/analytics-lessons.md) is the real baseline.
- Retention beats length: tighten, cut silence, no repeated beats.

## 5. Pre-delivery check (add to every build)

1. Safe-zone overlay image of the first frame, the cover, and one frame per text state: no essential text outside the band.
2. Phone-size (about 390 px wide) look at the cover and first frame: can the headline be read in one second?
3. Contrast pairs at least 4.5:1; fonts at least 48 px for captions; at most 32 characters per line, 2 lines.
4. The cover and the first frame ask a question and show no answer; the hook is 8 words or fewer.
5. Text and cover add curiosity rather than repeat the caption or title.

## Sources (checked 22 Nov 2026)

- Meta safe zones, unified 9:16: blog.adnabu.com/meta-ads/meta-safe-zones and billo.app (Meta Ads Safe Zones 2026)
- Facebook Reels caption best practices (band 20% to 70%, 48 px minimum, 32 characters, 2 lines, box behind busy areas): opus.pro/blog/facebook-reels-caption-subtitle-best-practices
- Eye tracking: Yangandul, Paryani, Le and Jain, ETRA 2018, "How many words is a picture worth?" (zenodo.org/records/3754785)
- vidIQ thumbnail study, July 2026: vidiq.com/research/youtube-thumbnail-study ; vidIQ thumbnail tips: vidiq.com/blog/post/youtube-thumbnail-tips ; contrast ratio: vidiq.com/vi/blog/post/youtube-custom-thumbnails-ctr
- Curiosity gap and text complementing the title: starnow.com article quoting Alter; storyblocks.com; metricool.com
- Hooks and retention: capcut.com short-form hook patterns (June 2026), adamconnell.me/improve-video-retention-social-media, dev.to hook engineering (2026), captions.ai video hooks
