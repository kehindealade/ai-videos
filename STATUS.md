# Status (as of 26 Nov 2026)

Sources: claude/build-plan-2026-11-21.md, claude/build-plan-2026-11-24.md, memory/video-kits.md, memory/youtube-title-plan.md. Times are Lagos (WAT). Check YouTube Studio and Facebook for what actually went live; this is the plan as last recorded.

## Posted
- Money Map YouTube: How Banks Make Money (long, 17 Nov), Why Is Bitcoin Crashing (long, 19 Nov), Bitcoin Short 1 (20 Nov, scheduled).
- Money Map Facebook: Bitcoin Reel and $16 meal Reel (19 Nov), Thanksgiving Reel (22 Nov, planned).
- Small Win Films YouTube: Nothing Could Fix His Bad Day (17 Nov), He Still Makes Two Cups (18 Nov), Two Cups Short (20 Nov).
- Small Win Films Facebook: Two Cups Reel (19 Nov).

## Scheduled or planned (built, not yet live on 25 Nov)
- Tue 24 Nov 15:00: Bitcoin Short 2 "Liquidated" (YouTube)
- Wed 25 Nov: 31 Texts She Never Sent film (YouTube 13:00) and Reel (Facebook 14:00 or after 17:30); Black Friday Short (YouTube 18:00)
- Thu 26 Nov: Black Friday Reel "50% OFF of what?" 15:00 (Money Map FB); "First paycheck" Reel (v2-qa, Numbers ep 2) 15:00 (Small Win FB, scheduled via API)
- Fri 27 Nov: "Everybody goes out except me" Reel 15:00 (Small Win FB, scheduled via API); coffee Reel 16:00 (Money Map FB, moved from 14:00); heartbreak Short 22:00 (Small Win YT); printer ink Short 22:00 (Money Map YT, moved from Mon 30 Nov)
- Sun 29 Nov 16:00: "3 alarms" Reel (Small Win FB, scheduled via API)
- Tue 1 Dec: national debt long 20:00 (Money Map YT, moved from 15:00); group chat Reel 23:00 (Small Win FB, scheduled via API)
- Thu 3 Dec 01:00: debt Short A (Money Map YT, moved from Wed 2 Dec 18:00); Sat 5 Dec 17:00: debt Short B (Money Map YT, moved from 15:00)
- Thu 3 Dec 15:00: tax brackets Reel (Money Map FB); "Wave back at someone who wasn't waving" Reel 15:00 (Small Win FB, scheduled via API, moved from Wed 9 Dec)
- Sat 28 Nov 17:00: Two Cups Short (Small Win YT, EEBA9t7TRa4, uploaded and scheduled via API)
- Sun 6 Dec 16:00: Christmas film "She Never Knocked" (Small Win YT, ArNDjYgSFME, uploaded and scheduled via API with thumbnail); Tue 8 Dec 01:00 its Short 1 "She Drove to His House Every Christmas Eve" (03QiAzUZifc, uploaded and scheduled via API). Shorts 2 and 3 held, not deleted (Kenny, 26 Nov 2026)
- Tue 8 Dec 15:00: RAM Short
- Thu 10 Dec 15:00: rent Reel (Money Map FB)
- Sun 13 Dec 16:00: Social Security long; Wed 16 Dec 01:00 its Short 1 (Short 2 held)
- Tue 15 Dec: credit card rewards long 15:00 (YouTube); "First paycheck" Reel 23:00 (Small Win FB, Numbers ep 2, rendered to Drive); Sun 20 Dec 16:00 credit card Short 2 (Short 1 held)
- Wed 16 Dec 13:00: "Every Sunday at 6, She Called" film; Fri 18 Dec 22:00 its Short
- Sun 27 Dec 16:00: pay later hangover Reel (Money Map FB)
- Held, unposted: betting set (long and two Shorts, Paper look), duplicate meal Reel (Kenny was told to delete it), $39 coffee Short (to reschedule)

## Open build work (claude/build-plan-2026-11-24.md)
- Conversation 8: Small Win Films "Numbers that say everything" eps 2 to 4. Ep 2 ("First paycheck") fixed and PASSED claude/qa-gate.md on 26 Nov 2026 (-16.6 LUFS, -1.9 dBTP, all 9 manual checks yes; waiting for Kenny's go to upload the fixed render to Drive AI videos/Renders; planned Tue 15 Dec 23:00 Small Win FB). Eps 3 (gym card, Thu 31 Dec 15:00) and 4 (last day, Tue 5 Jan 23:00) scripted, waiting for Kenny's go.
- Conversation 9: three standalone Small Win Films Shorts (email rewritten six times, bus stop bench, moving out). Scripts need resending for Kenny's go. Not started.
- Conversation 5 (optional): "How Mortgage Rates Work" long plus one Short. Not started.
- "Why is it so expensive?" ep 3 cars (promised on the RAM end card), Lego last.
- Facebook Christmas Reel (optional).
- Done 26 Nov 2026: film-log entries 5 to 9 merged into claude/film-log.md; new US posting slots approved (memory/posting-timetable.md), used for every new post from Mon 7 Dec; workflow.md rules 8 and 10 and analytics-lessons rule 5 updated to the one-Short and Chatterbox rules.

## Known gaps
- story-films-engine/film.py imports timeline.py, which was never saved to the Project. ENGINE-INDEX.md gives a stand-in that renders the scenes without whistle notes.
- Engines that need Chatterbox (for example money-map-ram-engine) only render after setup with WITH_CHATTERBOX=1 and the two float32 patches in that engine's README.
- yt-stats sign-in: token excluded from the export; sign in again, and set the OAuth consent screen to In production so tokens stop expiring weekly.
- vidIQ credits 0 until 17 Dec 2026.
- Claude could not listen to any score or voice; Kenny should listen once to each.

## Calendar (done by Claude through the Google Calendar connector, 26 Nov 2026)
- Deleted the events for Christmas Short 2 (Wed 9 Dec 18:00) and Short 3 (Fri 11 Dec 22:00); Short 1 Mon 7 Dec 18:00 kept.
- Added Numbers ep 2 Tue 15 Dec 23:00, ep 3 Thu 31 Dec 15:00, ep 4 Tue 5 Jan 23:00 (Africa/Lagos, popups at 30 and 0 min).
- Every item from 26 Nov onward under "Scheduled or planned" has an event, except the heartbreak Short (Fri 27 Nov): the calendar has only "Link heartbreak film as Related video" at 12:00, no 22:00 post event.
- Still open, ask Kenny: the held Shorts still have events (Social Security Short 2 "Social Security Tax Explained" Fri 18 Dec 22:00, credit card Short 1 "Credit Card Minimum Payment" Thu 17 Dec 01:00). Delete them or keep?
- Antigravity has no calendar connection; calendar changes are made by Kenny or by Claude until one is connected.

## Not yet confirmed by Kenny
- Which posts actually went live on 25 Nov and before (31 Texts film and Reel, Thanksgiving Reel, duplicate meal Reel deleted). The list above is still the plan as recorded.
