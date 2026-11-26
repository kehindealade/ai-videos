---
name: posting-timetable
description: Kenny's posting timetable (Lagos time) for YouTube long, YouTube Shorts and Facebook Reels, and the rule for "schedule a post today"
sources: [chat]
aliases: [posting schedule, best time to post, timetable, posting calendar]
---

- [stated] asked (19 Nov 2026) for a timetable of best posting times for every day, for YouTube and Facebook, optimal to manageable, so that "schedule a post today" goes to the earliest best slot
- [stated] timetable (Lagos time, WAT; built from Buffer 2026 YouTube 1.8M videos and Facebook 14M posts, SocialPilot 2026 YouTube, Sprout Social 2026 Facebook; target viewers on US Eastern time, Lagos = New York + 6 h until 7 Mar 2027, then + 5 h until 1 Nov 2027, so subtract 1 h from every slot in that window):
  - Mon: YT long 15:00 | YT Short 18:00 (best 02:00 Tue, scheduled) | FB Reel 18:00
  - Tue: YT long 15:00 | YT Short 15:00 (best 01:00 Wed, scheduled) | FB Reel 14:00
  - Wed: YT long 13:00 | YT Short 18:00 (best 01:00 Thu, scheduled) | FB Reel 14:00 (best FB day)
  - Thu: YT long 13:00 (alt 23:00) | YT Short 01:00 Fri, scheduled | FB Reel 15:00 (Buffer's top FB slot)
  - Fri: YT long 18:00 | YT Short 22:00 (top Shorts slot of the week) | FB Reel 14:00
  - Sat: YT long 18:00 | YT Short 15:00 | FB: avoid (worst day; 12:00 only if it cannot wait)
  - Sun: YT long 16:00 (top long-form slot of the week) | YT Short 16:00 (best 01:00 Mon, scheduled) | FB Reel 16:00
- [stated] rule: when asked to schedule a post today, use today's slot for that platform and type; if it has passed or is under 30 minutes away, use the next day's slot; skip Saturday for Facebook; slots between 23:00 and 07:00 are set with the platform's scheduler (YouTube Studio or app Schedule, Meta Business Suite), never posted by hand
- [stated] same video on two platforms the same day: Facebook first, YouTube an hour later where the slots allow
- [stated] if a Page's or channel's own analytics later show a different main audience (for example mostly Nigeria), switch to those viewers' local times and update this file

- [stated] 26 Nov 2026: approved the new US posting slots from claude/series-plan-2026-11-24.md as proposed. They apply to every new post from Mon 7 Dec 2026; posts already scheduled keep their slots. Lagos time, US Eastern = Lagos minus 6 h until 7 Mar 2027, then minus 5 h until 1 Nov 2027:
  - YouTube long: Mon 20:00, Tue 20:00, Wed 21:00, Thu 21:00 (2 to 3 pm ET), Sat 14:00 (8 am ET), Sun 16:00 (10 am ET, kept). Wed and Thu 13:00 are retired for new posts.
  - YouTube Shorts: main evening lane Tue to Thu 01:00 to 02:00 next day (scheduler); Fri 22:00 (top); Sat 17:00 and Sat 01:00 Sun (new); West Coast lane 03:00 to 04:00 Lagos for evergreen Shorts only; avoid 09:00 to 13:00 Lagos.
  - Facebook Reels: Tue and Wed 23:00 to 00:00 (new evening lane), Thu 15:00 and Sun 16:00 (kept). Still no Saturday. The older weekday Facebook slots above are fallbacks only.
  - Kept: Facebook first, YouTube an hour later for the same video; Shorts after their long video. After 3 weeks compare first-hour views and US share per lane and switch to what wins.

- [stated] 26 Nov 2026: automated API scheduling and region/timezone targeting added to the workflow:
  - Always schedule directly after passing claude/qa-gate.md using tools/yt_upload.py (YouTube) and tools/fb_reels.py (Facebook Reels, 10 min to 29 days ahead) to the earliest open best slot (no Facebook on Saturday, Shorts after their long video, never two posts on the same channel and platform in one day).
  - Region and timezone targeting: default is US Eastern (ET), but if a video will perform better in another region (e.g. UK GMT/BST, Europe CET, Australia AEST, SE Asia PHT/SGT, or US-UK overlap), pick that region's best local peak slot (converted to Lagos WAT / UTC) and tweak language, spelling, currency, examples and search keywords to target that region (still keeping standing rules: no Nigerian names, no politics). Log the target region in the upload pack and verify viewer countries 48 hours after posting.
  - Reference local peak times (convert to Lagos WAT, UTC+1):
    - US Eastern (UTC-5 winter / UTC-4 summer): YT long 14:00-15:00 local (Sun 10:00), YT Shorts 19:00-20:00 (Fri 16:00), FB Reels 17:00-18:00 Tue/Wed or 09:00-10:00 Thu/Sun.
    - UK (UTC+0 winter / UTC+1 summer): YT long 14:00-16:00 local (15:00-17:00 WAT winter), YT Shorts 18:00-20:00 local (19:00-21:00 WAT), FB Reels 12:00-14:00 or 18:00 local.
    - US-UK overlap: 15:00-17:00 WAT (09:00-11:00 ET, 14:00-16:00 UK).
    - SE Asia / Philippines (UTC+8, Lagos +7 h): YT Shorts / FB Reels 19:00-21:00 local (12:00-14:00 WAT).
    - Australia East (UTC+10/+11): YT/FB evening 19:00-21:00 local (09:00-11:00 WAT).
- [stated] 26 Nov 2026: channel freshness / drought priority when scheduling: always check each channel and Page's last live post date and upcoming queue first; if a channel or Page has gone several days without a new post, priority is to get a new post out ASAP in the next best slot and target timezone instead of leaving a multi-day gap; also audit already-scheduled posts when optimising slots (asking Kenny before moving posts unless he explicitly asks to optimise the queue)
