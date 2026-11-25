# Upload checklist (every YouTube upload, both channels)

Added 21 Nov 2026. Source: a Twitter thread about Shorts pay that Kenny shared. Claude checked it against YouTube's help pages; most of its pay claims are unproven, but the steps cost nothing, so Kenny decided to follow them on every upload. Follow the steps below, and do not repeat the thread's pay claims as fact in any pack or reply.

## Ask first (Kenny, 21 Nov 2026)

Apply these changes to future videos only as follows.

Do without asking (free, no effect on the video itself): step 1 file name, step 4 desktop upload, step 5 Unlisted first, step 6 language and "not made for kids", step 7 waiting for green checks when the slot allows, step 8 scheduling at the timetable slot, steps 9 and 10, and the UPLOAD STEPS block in every pack.

Ask Kenny first, with one short question that says what would change and why it is unadvisable, and wait for his answer:
- Anything that changes a video's content: removing or replacing the music, trimming or rewording the first 8 seconds (step 2) when that would weaken the hook or the story, changing the length, or using a licensed or trending track because the concept needs it (step 3).
- Anything that would push a post later than its timetable slot, for example the checks are not green by the slot, a yellow icon needs a review, or the upload cannot be done the day before.
- Anything in this checklist that conflicts with another standing rule (hook rules, script-first for Small Win Films, never repeat a design, analytics lessons).
- Anything else from this checklist that Claude judges major and unadvisable for that video. When unsure, ask.

In a scheduled or unattended run, do not make a content change: write the question into the upload pack instead and keep the video as planned.

## Steps

Before uploading
1. File name: rename the video file to the primary keyword (for example how-visa-makes-money.mp4, short-film-about-loss.mp4). Evidence that it helps: none found. Free to do.
2. First 8 seconds clean: no profanity, weapons, blood or graphic detail (the Policy and repetition gate in claude/yt-stats/workflow.md already bans these; this just double-checks the opening). Ad suitability reviews the whole video, so this is a cheap safety margin, not a proven rule. If a fix would change the opening, ask first (see above).
3. Audio: never add a trending or licensed track from YouTube's audio button to a Short. YouTube documents that each licensed track cuts the share of that Short's revenue that reaches the Creator Pool (1 track = half, 2 tracks = one third). Use the original voiceover, the film's own code-made music, or a YouTube Audio Library track kept quiet under the voice. Whether Audio Library tracks trigger the carve-out is not confirmed.

Uploading
4. Upload from desktop YouTube Studio, not the phone app, because the Checks step (copyright and ad suitability) is part of the desktop upload flow. If it has to be the phone, still upload as Unlisted and look at the monetization icon in Studio before making it public.
5. Visibility: Unlisted first. (YouTube may review Private videos too, so Unlisted is a habit, not a rule.)
6. Show more: Video language English (United States); "No, it's not made for kids"; keep the other settings from the SEO rules in claude/yt-stats/workflow.md (caption language English, category, altered content No).
7. Wait for the Checks page to show green on Copyright and Ad suitability. YouTube says the ad suitability check usually takes under 20 minutes, at most 1 hour, and up to 24 hours when a human review is added. So upload at least a few hours before the slot, ideally the day before. If a yellow icon appears, use Request review and tell Kenny.
8. Switch the video to Scheduled at the slot from topics/posting-timetable.md in project memory (the thread's 11am or 4pm EST is 17:00 or 22:00 Lagos, which the timetable already uses on some days). The timetable stays the authority. Shorts still go live after their long video so the long can be set as Related video.

After going public
9. In Studio's content list, confirm the monetization icon is green or request a review if yellow.
10. Once a video has data (48 hours or later), note the viewer countries and the Shorts RPM in the channel's log (film-log.md or money-map-style-log.md), so we can see over time whether this routine changes anything.

## Every upload pack carries these steps

Each txt upload pack (long video and each Short) ends with an "UPLOAD STEPS" block listing steps 1 to 9 with the video's own file name, language, slot and the audio note filled in, plus any "ask first" question that is still open.

## Optional narration audio polish (Money Map and any video with a synthetic voice; Kenny OK'd 22 Nov 2026, on the condition it does not make generation heavier or use up his limits)

This is only for how the narration sounds. It does not protect monetization: YouTube's policy is about templated, repetitive or low-value content, not about how the audio is made, so never describe it as monetization protection.

- Room tone: in the final audio mix, add a very quiet room-tone bed (about -45 to -50 dB) under the voice, so the gaps between words are not dead silence. Make it in the same mix step from a synthetic filtered-noise source (for example ffmpeg anoisesrc with a low-pass filter, or numpy), so nothing is downloaded and it adds one extra input to a mix that already runs. Do not re-render or re-mix videos already made.
- Pacing: shape it in the script text before the single voice generation: vary sentence length, use commas, line breaks and "..." for uneven pauses. No extra voice generations, no re-runs. If the voice tool has a stability or variation setting, use a middle value instead of the maximum.
- Skip: breath-sound inserts, speed-up and pitch-shift tricks (extra work, and they can make the voice worse). Do not add them unless Kenny asks.
- If any of this would take extra generation runs, extra renders or noticeably more usage, skip it for that video and say so.

## Not adopted

- The thread's "make every video 54 to 58 seconds" rule. YouTube pays Shorts from a pool split by each creator's share of engaged views per country, not by watch time, so length does not multiply pay, and padding a story hurts retention. Length stays set by the story and by claude/analytics-lessons.md (Reels and TikToks 45 to 60 seconds, payoff before 0:45). Kenny can override this.
- A second thread's AI-voice "detector" tricks (-50 dB room tone as a way to pass review, 1.03x speed plus 1 semitone shift as a way to change a voice "fingerprint"): no evidence YouTube detects voices by silence or audio hash. Only the harmless polish above was kept.

## What actually drives Shorts pay (YouTube's Shorts monetization policies page, checked 21 Nov 2026)

- Shorts feed ad revenue is pooled per country each month, music licensing is taken out, the rest is split by share of engaged views, and the creator keeps 45% of the allocation.
- So viewer country and music use matter most; ads do not run on the Short itself, so there is no per-video ad auction.
- The page states that from 1 Feb 2027 a channel needs at least 10 million qualified Shorts views in the last 90 days to earn a share of the Creator Pool and Premium revenue. Re-check the page before relying on it.
