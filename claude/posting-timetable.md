# Posting timetable (Lagos time, WAT) — made 19 Nov 2026

Target viewers: US Eastern time (Lagos = New York + 6 h until 7 Mar 2027; from 8 Mar to 1 Nov 2027 subtract 1 h from every slot).
Sources: Buffer 2026 (YouTube 1.8M videos and Shorts; Facebook 14M posts), SocialPilot 2026 (YouTube 301k videos), Sprout Social 2026 (Facebook, 30k customers).

| Day | YouTube long | YouTube Short (by hand / best, scheduled) | Facebook Reel |
|---|---|---|---|
| Mon | 15:00 | 18:00 / 02:00 Tue | 18:00 |
| Tue | 15:00 | 15:00 / 01:00 Wed | 14:00 |
| Wed | 13:00 | 18:00 / 01:00 Thu | 14:00 (best FB day) |
| Thu | 13:00 (alt 23:00) | 01:00 Fri, scheduled | 15:00 (top FB slot) |
| Fri | 18:00 | 22:00 (top Shorts slot) | 14:00 |
| Sat | 18:00 | 15:00 | avoid (12:00 if it cannot wait) |
| Sun | 16:00 (top long slot) | 16:00 / 01:00 Mon | 16:00 |

Rule: "schedule a post today" = today's slot for that platform and type; if passed or under 30 min away, the next day's slot; no Facebook on Saturday; anything between 23:00 and 07:00 goes in the platform scheduler. Same video on both platforms: Facebook first, YouTube an hour later. Shorts go live after their long video so the long can be added as the Related video. YouTube Shorts that point to a long video are not posted on Facebook; each Facebook Reel must be complete on its own. Facebook Reels must fill the screen edge to edge (claude/vertical-video-rules.md).

Phone reminders and Google Calendar (aladeekehindee@gmail.com, events in Africa/Lagos) are always updated together.

Posted (19 Nov 2026):
- Money Map Facebook: Bitcoin Reel 15:00; $16 meal restaurant Reel about 23:00 (posted early, was planned Mon 23 18:00)
- Small Win Films Facebook: Two Cups Reel 17:35 (calendar design; Meta flagged bordered video, 162 views after ~5 h)
- Money Map YouTube: Why Is Bitcoin Crashing (long) 23:00

Current calendar (reminder + calendar event for each, updated 19 Nov 2026, 23:20):
- Fri 20 09:00: add the Bitcoin long as Related video on Bitcoin Short 1 ($500), which goes out 22:00 Fri (scheduled)
- Fri 20 10:00: check Post details on the Two Cups and $16 meal Facebook Reels (views, bordered-video warning), send screenshots
- Fri 20 22:00: Two Cups Short
- Tue 24 15:00: Bitcoin Short 2 (Liquidated), YouTube only
- Wed 25 13:00: 31 Texts She Never Sent on YouTube; Facebook Reel 14:00
- Fri 27 12:00: link the heartbreak film as Related video on the heartbreak Short (Short out 22:00, scheduled)
- Open slots: Money Map Facebook Mon 23 (restaurant Reel already posted); Small Win Films Facebook between Thu 19 and Wed 25
- Removed 19 Nov: Studio "edit 4 schedules" checklist, Bitcoin Facebook Reel 15:00 reminder, old Bad Day-only TikTok reminder, Mon 23 restaurant Reel reminder and calendar event (posted early)
- Unscheduled: Money Map $39 coffee Short (to be rescheduled); TikTok for both Reels once the account is set up (undated reminder only)

## New US slots, approved 26 Nov 2026 (apply from Mon 7 Dec 2026; already scheduled posts keep their slots)
  - YouTube long: Mon 20:00, Tue 20:00, Wed 21:00, Thu 21:00 (2 to 3 pm ET), Sat 14:00 (8 am ET), Sun 16:00 (10 am ET, kept). Wed and Thu 13:00 are retired for new posts.
  - YouTube Shorts: main evening lane Tue to Thu 01:00 to 02:00 next day (scheduler); Fri 22:00 (top); Sat 17:00 and Sat 01:00 Sun (new); West Coast lane 03:00 to 04:00 Lagos for evergreen Shorts only; avoid 09:00 to 13:00 Lagos.
  - Facebook Reels: Tue and Wed 23:00 to 00:00 (new evening lane), Thu 15:00 and Sun 16:00 (kept). Still no Saturday. The older weekday Facebook slots above are fallbacks only.
  - Kept: Facebook first, YouTube an hour later for the same video; Shorts after their long video. After 3 weeks compare first-hour views and US share per lane and switch to what wins.

## Automated scheduling and region/timezone targeting (added 26 Nov 2026)

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
