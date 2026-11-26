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
- Thu 26 Nov: Black Friday Reel "50% OFF of what?" 15:00 (Money Map FB); "Everybody goes out except me" Reel 15:00 (Small Win FB)
- Fri 27 Nov: heartbreak Short 22:00 (YouTube); coffee Reel 14:00 (Money Map FB)
- Sun 29 Nov 16:00: "3 alarms" Reel (Small Win FB)
- Mon 30 Nov 18:00: printer ink Short (YouTube)
- Tue 1 Dec: national debt long 15:00 (YouTube); group chat Reel 23:00 (Small Win FB)
- Wed 2 Dec 18:00: debt Short A; Sat 5 Dec 15:00: debt Short B
- Thu 3 Dec 15:00: tax brackets Reel (Money Map FB)
- Sun 6 Dec 16:00: Christmas film "She Never Knocked"; its one Short Mon 7 Dec 18:00 (Short 1 "She Drove to His House Every Christmas Eve"). Shorts 2 and 3 held, not deleted (Kenny, 26 Nov 2026)
- Tue 8 Dec 15:00: RAM Short
- Wed 9 Dec 23:00: wrong wave Reel (Small Win FB)
- Thu 10 Dec 15:00: rent Reel (Money Map FB)
- Sun 13 Dec 16:00: Social Security long; Wed 16 Dec 01:00 its Short 1 (Short 2 held)
- Tue 15 Dec: credit card rewards long 15:00 (YouTube); "First paycheck" Reel 23:00 (Small Win FB, Numbers ep 2, rendered to Drive); Sun 20 Dec 16:00 credit card Short 2 (Short 1 held)
- Wed 16 Dec 13:00: "Every Sunday at 6, She Called" film; Fri 18 Dec 22:00 its Short
- Sun 27 Dec 16:00: pay later hangover Reel (Money Map FB)
- Held, unposted: betting set (long and two Shorts, Paper look), duplicate meal Reel (Kenny was told to delete it), $39 coffee Short (to reschedule)

## Open build work (claude/build-plan-2026-11-24.md)
- Conversation 8: Small Win Films "Numbers that say everything" eps 2 to 4. Ep 2 ("First paycheck") DONE 26 Nov 2026 (engine claude/small-win-paycheck-engine/, video + cover + pack in Drive AI videos/Renders, planned Tue 15 Dec 23:00 Small Win FB). Eps 3 (gym card, Thu 31 Dec 15:00) and 4 (last day, Tue 5 Jan 23:00) scripted, waiting for Kenny's go.
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

## Calendar to-do (Google Calendar not connected yet on 26 Nov 2026; do these as soon as it is)
- Delete the events for Christmas Short 2 (Wed 9 Dec 18:00) and Short 3 (Fri 11 Dec 22:00); keep Short 1 Mon 7 Dec 18:00.
- Check the events for the held Shorts (Social Security Short 2 Fri 18 Dec 22:00, credit card Short 1 Thu 17 Dec 01:00) and ask Kenny before deleting them.
- Add events for conversation 8 once built: ep 2 Tue 15 Dec 23:00, ep 3 Thu 31 Dec 15:00, ep 4 Tue 5 Jan 23:00 (Africa/Lagos, popup alerts, title "SmallWinFilms | Facebook Reel | Post: <title>").
- Check that every event listed under "Scheduled or planned" exists.

## Not yet confirmed by Kenny
- Which posts actually went live on 25 Nov and before (31 Texts film and Reel, Thanksgiving Reel, duplicate meal Reel deleted). The list above is still the plan as recorded.
