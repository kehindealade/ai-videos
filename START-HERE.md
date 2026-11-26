# START HERE

This repo is the full export of Kenny's Claude project "AI Videos and YouTube" (exported 25 Nov 2026). Any AI or person can continue the work from it. Read this file first, then follow the reading order below.

## What this is

Two channels, every video drawn and scored entirely in code (Python, pycairo, numpy, ffmpeg). No stock footage, no AI video models, no sampled music.

1. Money Map (YouTube @moneymaphq01, plus a Money Map Facebook Page). Finance explainers: "how X makes money", "why is X so expensive", "myth vs math". Global audience, US dollars, US-first topics. Tagline "Follow the money." Narrated.
2. Small Win Films (YouTube @smallwinfilms001, plus a Small Win Films Facebook Page). Short animated story films about everyday adult life, no narrator, original code-made score, short on-screen lines. Tagline "Small stories. Small wins." Plus music-only relatable Reels (series "It's Not Just Me") and "Numbers that say everything" Reels.

Platforms: YouTube long, YouTube Shorts, Facebook Reels. Each platform gets its own video. No TikTok for now.

## Who you work for

Kenny (Kehinde Alade), based in Lagos, Nigeria. Senior backend engineer. All times in the docs are Lagos time (WAT, UTC+1) unless stated. His working preferences are in memory/preferences.md. The short version:

- Script first for Small Win Films; wait for his go before building.
- Give options when proposing stories or topics.
- Never repeat a design, voice, look, hook type or structure. Each channel's log lists what is used.
- No Nigerian names in any video. Adults only, no kids. No politics. Explain money, never advise.
- Thumbnails and covers are cliffhangers, never summaries.
- Vertical video is full bleed 9:16, text inside the safe band (y 300 to 1340 on 1080x1920).
- Every delivery: the video, thumbnail or cover, and one txt upload pack per video, then update the logs.
- Writing style for replies: plain and practical, no bold, no em dashes, no section headers in prose.

## Reading order

1. memory/preferences.md (how Kenny wants work delivered) and memory/video-kits.md (history of both channels)
2. claude/yt-stats/workflow.md (the master rules: research, policy and repetition gate, hooks, thumbnails, SEO, rules 1 to 10)
3. claude/analytics-lessons.md, claude/readability-and-retention-rules.md, claude/vertical-video-rules.md, claude/voice-rules.md, claude/upload-checklist.md
4. Channel log before any new video:
   - Money Map: claude/money-map-style-log.md, then entries 12 to 15 (claude/money-map-style-log-12-*.md to -15-*.md), claude/money-map-research.md
   - Small Win Films: claude/film-log.md (entries 5 to 9 merged in on 26 Nov 2026), claude/story-films-blueprint.md, claude/small-win-films-research.md
5. STATUS.md (what is posted, scheduled, built and still open) and claude/build-plan-2026-11-24.md (the current build plan)
6. ENGINE-INDEX.md (every engine and how to render it)
7. claude/qa-gate.md (the check every render must pass before upload; run python3 tools/qa.py)

## How a video gets made

1. Research the topic (workflow.md, "research topic for <channel>"), pass the policy and repetition gate.
2. Write the script with the hook named first. Small Win Films: send the script and wait for Kenny's go.
3. Copy the closest engine from ENGINE-INDEX.md into a new folder and change the look, palette, music, voice and layout so nothing repeats.
4. Voice (Money Map and spoken hooks): a never-used voice per voice-rules.md. Chatterbox Turbo is the default (Kenny found Kokoro alone too robotic), Kokoro builds the reference clip.
5. Render stills first, check the safe zones and the first 15 seconds, then render the video, then mux with the safe loudness chain in claude/qa-gate.md (about -16 LUFS, true peak below -1 dBTP).
5b. QA gate: python3 tools/qa.py OUT.mp4 COVER.png, answer the 9 manual checks from the phone-size sheets, fix and re-run until everything passes. Nothing is uploaded or called done before this.
6. Thumbnail or cover (cliffhanger), checked with claude/yt-stats/thumbcheck.py.
7. Upload pack txt per video (title, description, chapters, tags, SEO check, UPLOAD STEPS block).
8. Update the channel log, memory/ notes and this repo. Name files CHANNEL_platform_topic.

## Setup

Run ./setup.sh on a Linux machine or cloud VM (installs Python packages, ffmpeg, fonts and the Kokoro voice files). Or open render.ipynb in Google Colab to render from a phone. Requirements are in requirements.txt.

## Things not in this repo

- Rendered videos, thumbnails and covers (they were never saved to the project; re-render from the engines). Rendered files go to the Google Drive folder "AI videos" (subfolder Renders).
- claude/yt-stats/yt-signin.txt (OAuth secret and refresh token, deliberately excluded). To use claude/yt-stats/yt.py, Kenny signs in again: python3 yt.py auth-url, then exchange (steps in workflow.md, Setup).
- Full chat transcripts (Kenny can download them with Claude's data export). Decisions from those chats are recorded in the logs, plans and memory/ notes.
- Live connections: vidIQ, Google Calendar reminders. Reconnect them in the new tool.

MANIFEST.md lists every one of the 220 project files and whether it is copied, pending or excluded.
