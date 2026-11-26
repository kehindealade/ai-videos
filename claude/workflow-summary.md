# Video generation workflow summary (Money Map and Small Win Films)

Full standing rules live in AGENTS.md, memory/preferences.md, claude/yt-stats/workflow.md, claude/analytics-lessons.md, claude/readability-and-retention-rules.md, claude/vertical-video-rules.md, claude/voice-rules.md and claude/upload-checklist.md.

1. Topic research (per platform)
YouTube long, YouTube Shorts and Facebook Reels are planned separately because each platform works differently. Before picking a topic, run keyword research and a trend check using free YouTube autocomplete, claude/yt-stats/yt.py (when signed in), web search for news, and vidIQ when it has credits. Target the keyword gap: high or medium demand with low or medium competition. Every topic must pass the policy and repetition gate: not already in the channel log, adults only (no kids), no Nigerian names, no politics, no named real people, no graphic content, and Money Map explains mechanics without giving financial advice. Give options with demand, competition, format and gate result.

2. Script and approval
Write the script with the hook type and opening line named at the top. Frame 1 must already move, have a clear sound, and pose a question or tension in 8 words or fewer. For Money Map, re-verify every number against real sources on build day and shape spoken lines with mood tags and natural pauses. For Small Win Films, send the full scene-by-scene script and wait for Kenny's go before drawing anything.

3. New design and engine setup
Read the channel log first (claude/money-map-style-log.md plus entries 12 to 15, or claude/film-log.md) so nothing repeats: new look, palette, structure, hook type, counter style, music, end card and cover. Copy the closest engine folder from ENGINE-INDEX.md into a new folder and redesign it. Everything is generated in code: Python and pycairo for frames, numpy for original music and sound effects, ffmpeg for encoding. No stock footage, no AI video models, no sampled music.

4. Voice and audio
Money Map and any spoken hook use Chatterbox Turbo by default, with a never-used Kokoro voice or two-voice blend as the reference clip (never a real person's voice). Each video, Short and Reel gets its own voice, with varied line speeds and gaps by mood, plus an optional quiet room-tone bed. Small Win Films films and Reels are music only (unless a Reel hook uses a voice). Mix and loudness-normalise to about -16 LUFS with true peak below -1 dBTP. Kenny listens once before posting since the AI cannot hear the output.

5. Stills and pre-render checks
Before rendering the full video, render key stills and a 15-second opening strip (one frame per second). Check that frame 1 matches the thumbnail, the first 30 seconds change visuals every 3 to 5 seconds for Money Map and every 2 to 3 seconds for story films, and everything reads at 390 px phone width. For 9:16 vertical videos, check that the picture fills all 1080x1920 pixels edge to edge (no borders, frames or letterbox bars so Meta does not flag it), and run a safe-zone overlay confirming all essential text sits inside y 300 to 1340 and x 90 to 990 (captions at y 1100 to 1300), at least 48 px, max 32 characters per line, 2 lines, contrast at least 4.5:1.

6. Rendering and platform cuts
Render the video (long videos in two parallel parts joined with ffmpeg concat), then mux the normalised audio. Every long video gets one YouTube Short, re-laid-out for vertical with its own design, voice and loop (never a plain crop). Facebook Reels are built to tell the whole story on their own, 35 to 60 seconds with the payoff before 0:45, never pointing to a YouTube long video.

7. Thumbnail and cover
Design a cliffhanger that raises a question without showing the answer or ending. For 16:9 thumbnails, follow left-to-right scanning (face or cause on the left, object or tension on the right), 2 to 5 words that add to the title instead of repeating it, and check with claude/yt-stats/thumbcheck.py so nothing sits in the duration badge or menu zones and everything reads at 320 px. For 9:16 covers, put the question block in y 384 to 900 and verify with the safe-zone overlay.

8. SEO, file naming and upload packs
Run autocomplete or yt.py seo for the main keyword. Name delivered files CHANNEL_platform_topic. Create one txt upload pack per video containing the title (under 60 characters, primary keyword in the first 40), unique description (with chapters and sources for Money Map, and no "animated with code" line), tags, hashtags, pinned comment question, SEO check, and a filled-in UPLOAD STEPS block. Include an .srt caption file for narrated videos.

9. Delivery, storage and logs
Upload rendered mp4 and png files to the Google Drive folder "AI videos/Renders". Never commit media or secrets to GitHub. Update the channel log, voice-rules.md (if voiced), STATUS.md, the build plan, ENGINE-INDEX.md and memory notes, then commit and push code and docs to GitHub. Pick the earliest open slot from the approved US posting timetable (Lagos time, no Facebook on Saturday) and set phone reminders plus matching Google Calendar events in Africa/Lagos.

10. Uploading and analytics review
On YouTube, rename the file to the primary keyword, upload from desktop Studio as Unlisted, set English (United States) and not made for kids, use no licensed or trending audio on Shorts, wait for green Copyright and Ad suitability checks, then schedule at the timetable slot. Shorts go live after their long video so you can link the long as the Related video. On Facebook, upload the Reel manually with the custom cover, skip Facebook music, paste the caption and pin the first comment question (no engagement bait). About 48 hours after posting, check yt.py report plus Studio and Facebook screenshots, log retention, 3-second hold and search terms against the baseline in analytics-lessons.md, and apply what you learn to future videos without re-editing old ones.

Final rule: always ask Kenny before changing a finished video or moving a post off its slot.
