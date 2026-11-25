# Money Map style log

Purpose: record the look and structure of every Money Map video so the next one is visibly and structurally different. Read this before designing any new Money Map video, and add an entry after each finished one.

Why: YouTube's inauthentic content rules demonetize channels whose uploads look template-made or repeat the same formula. A different colour scheme alone is not enough. Each video should differ in at least three of the six fields below from the previous two videos, and the research, script and angle must always be new. What stays constant is only the brand: the Money Map name, the route-M mark, "Follow the money." and sourced facts.

Project-wide rules (research before every topic, "research topic for <channel>", the policy and repetition gate, SEO-first upload packs, and hooks on every video) live in `claude/yt-stats/workflow.md`. Read it with this log.

Fields to log for each video
1. Look: background, palette, fonts, card or shape style.
2. Scene vocabulary: which visual devices carried the explanation.
3. Structure: how the story is ordered (chapters, case study, countdown, question and answer, timeline, etc.).
4. Hook type: conflict, shocking number, unexpected outcome, biggest question. Every video and every Short has one, built by the Hook rules in workflow.md; never the same hook type twice in a row.
5. Voice: Kokoro voice and speed.
6. Sound: music, effects.

## Delivery workflow for every new video (Kenny's standing rules)
0. Research the topic and run the policy and repetition gate (workflow.md). Write the hook first and name it at the top of the script.
1. Build the long video. Check facts against sources before building.
2. Run the vidIQ checks that matter (title scores, search demand for tags; thumbnail score once the video is live). When vidIQ has no credits, use the free `seo` and research commands in workflow.md.
3. Send the long video, its thumbnail and a txt upload pack (title, description with chapters and sources, tags, upload settings, SEO check).
4. Decide how many Shorts the video supports, build them (each with its own hook in the first 1 to 2 seconds), check their titles.
5. Resend everything: the long video and each Short, each with its cover and its own txt upload pack (one long plus two Shorts means three txt files).
6. Set or update the phone posting reminders for the long video and every Short, and move existing reminders whenever the posting plan changes.
7. Update the logs: add the entry to this style log (film-log.md for Small Win Films), update project memory, and save the engine, script and upload pack files to the Project.
8. Reply in the agreed format: short summary, bullet list of vidIQ or research results, credits used and left, what was logged, next step.

## Entries

### 1. Failed bank transfer (Short, posted 15 Nov 2026, later removed in the 17 Nov reset)
- Look: dark ledger board, gold and cream on near-black, one camera moving over a single board.
- Scene vocabulary: nodes and links, cash packets travelling, phone, timer, stamps.
- Structure: one transaction followed step by step.
- Hook: question ("Your bank debited you but they got nothing. Where is the money?").
- Voice: bm_fable.
- Sound: effects only, no music.
- Engine: Ledger Kit (ledger-kit-moneymap.zip).

### 2. Betting set (long 8:04 plus two Shorts, built 16 Nov 2026, not yet posted; held for release alongside a casinos video)
- Look: "Paper". Cream paper with grain, ink black, one red accent, green and gold support. Lora serif headlines, Inter labels. White cards with hard ink offset shadows. Dark inverted chapter and end cards.
- Scene vocabulary: big serif statements, stat cards with count-up, money moving between three cards with a coin flip, keyframed bar charts, row tables, parlay ticket with stamp, phone bet slip, numbered recap list.
- Structure: hook, then three numbered "moves" with chapter cards, recap list, end card.
- Hook: unexpected outcome ("You won your bet. The betting company still made money.").
- Voice: am_michael 0.95 (long, parlay Short), bm_george 0.98 (coin toss Short).
- Sound: narration, soft ticks, low thump on chapter cards, no music.
- Engine: claude/money-map-paper-engine/.

### 3. How Banks Make Money (long 8:18 plus two Shorts, built 17 Nov 2026)
- Posting plan (phone reminders set, 5:30 pm Lagos): long video Tue 17 Nov, Short 1 Thu 19 Nov, Short 2 Sat 21 Nov.
- Look: "Statement". Cool grey desk background; a punched paper bank statement fixed on the left third for the whole video (Money Map header, navy column bar ENTRY / YOU / THE BANK); explainer panel on the right. Navy ink, green for money to you, red for the bank's take, yellow highlighter marker for emphasis. Poppins headlines, DejaVu Sans Mono for figures and entries. Rounded slips with soft drop shadows, no chapter cards (a navy tab label names each section instead).
- Scene vocabulary: statement lines typing in and getting highlighted or struck through; mono number slips with count-up; an IOU slip and crossed-out vault; a split bar (kept ready vs sent to work); a car leaving and returning to a parking spot against a clock (the borrowed-car analogy) and a noon "everyone wants their keys" grid; a vertical rate ruler with a SPREAD bracket; a torn-edge receipt that grows line by line with a total; a three-node card swipe with a slice flying to the issuing bank; a number that grows from $1,000 to a trillion; a red CLOSED stamp.
- Structure: follow one $1,000 deposit for one year; the statement fills line by line as each way the bank earns appears (4 ways), then a failure case (Silicon Valley Bank), then the year added up on the statement's total line. No numbered chapter cards, no recap list.
- Hook: shocking number contrast ("$3.80 for you, $210 for the bank, same money").
- Voice: af_heart 0.88 (first female voice on the channel).
- Sound: narration, soft paper clicks on reveals, a two-note chime when a statement line posts, no music.
- Engine: claude/money-map-statement-engine/ (stmt.py engine, banks.py script data, thumb.py thumbnail, short_gap.py and short_coffee.py for the Shorts).
- Thumbnail: tilted statement slip with "$3.80" highlighted green and "$210" in red, "SAME MONEY." and a red "WHO GETS PAID?" tab.
- Title chosen with vidIQ: "How Banks Make Money From Your Savings (It's Not What You Think)" scored 99.
- Shorts (vertical 1080x1920, the Statement look in a portrait layout: brand bar on top, a short statement showing only the rows that Short needs, panel below, captions raised to clear YouTube's overlay, end card says FULL VIDEO and names the long video; stmt.set_portrait picks the rows):
  - Short 1 "The gap" (0:47, voice bf_emma 0.95): $3.80 vs $210, rate ruler, SPREAD bracket, "counting on you not to check". Title "Your Bank Pays You $3.80. It Charges $210 for the Same Money." (vidIQ 86).
  - Short 2 "The $39 coffee" (0:45, voice am_eric 0.98): hook line, coffee receipt growing to $39, nine years of interest, $2.96B, who pays. Title "Why Overdraft Fees Hit Broke People Hardest" (vidIQ 93).

### 4. Why Is Bitcoin Crashing? Where Did $1 Trillion Go? (long 8:12 plus two Shorts, built 19 Nov 2026)
- Topic research: "why is bitcoin crashing" 7/7 High demand, competition Medium (16 of 50, 45%); timely (BTC ~$62,000 mid-Nov 2026, ~50% below the Oct 2025 peak). Kenny picked it from claude/topic-research-2026-11-19.md.
- Posting plan (5:30 pm Lagos): long Sat 21 Nov (same day as the already scheduled $39 coffee Short), Short 1 Tue 24 Nov, Short 2 Thu 26 Nov.
- Look: "Transit map". Pale blue-grey city map (faint street grid, park blocks, a river along the bottom); thick coloured metro lines (ink start, red, blue, orange, purple, green end); white stations with coloured rings; dark departure boards with amber split-flap figures; transit sign plates (dark plate, coloured edge stripe). Barlow Condensed Bold headings, Barlow body. Top bar: Money Map mark plus a 6-station progress line that lights up per stop.
- Scene vocabulary: departure board flipping $2.5T to $1.23T; a red falling line between two stations with a "-51%" stamp; the full metro map drawn line by line with a "$" train moving stop to stop; ten orange coins with price tags and a total card (one coin sold at $50); MARKET VALUE = LAST PRICE x EVERY COIN formula with a crossed-out vault; seller and buyer stations with coin and cash swapping; ETF flow line (broker app, fund, bitcoin); red outflow bars for 7 days; leverage stack of $1,000 blocks (yours green, borrowed grey) with a LIQUIDATED stamp and a clock; split lines to traders, exchange fee and insurance fund; falling dominoes with a live price board; V-shaped flash-crash line; fear gauge at 10; toll-gate exchange taking fees from coins in both directions; stablecoin $1 tokens leaving a dashed crypto zone; recap map lighting each station; route-M end card.
- Structure: hook, a "before we board" section answering why it fell (3 numbered pressure cards), then a route with 4 stops (sign plate for each), then "end of the line" recap on the map. No numbered recap list.
- Hook: biggest question ("Bitcoin just lost more than a trillion dollars. So where did the money go?"); frame 1 is the departure board, matching the thumbnail.
- Voice: am_fenrir 0.93 (am_adam was planned but is Kokoro's weakest male voice). Shorts: af_bella 0.98 (Short 1), af_sarah 0.98 (Short 2).
- Sound: narration, a two-note station chime and whoosh on each stop sign, split-flap ticks on boards, whoosh on map moves, low thumps on stamps, and a very quiet ambient pad under everything (first Money Map video with a music bed).
- Thumbnail: cracked orange bitcoin coin on a falling red line (left), dark board with "SINCE OCT 2025", "-$1.2 TRILLION" in amber and a red "WHO GOT IT?" stamp (right).
- Shorts (vertical, map-paper background, Money Map mark top left, captions burned in at mid-height, full-video end card):
  - Short 1 "The $500 that never existed" (0:35): ten coins in two rows, one sold at $50, total counts down, "ONLY $50 MOVED". Hook: unexpected outcome. Title "Why Bitcoin "Lost" $1 Trillion (It Wasn't Cash)".
  - Short 2 "Liquidated in seconds" (0:35): $1,000 to $0, leverage stack, LIQUIDATED stamp, split to traders and exchange fee, $2B+ board. Hook: conflict. Title "How Bitcoin Traders Get Liquidated in Seconds".
- Engine: claude/money-map-transit-engine/ (content.py script data, engine.py scenes and renderer, tts.py cached narration, mix.py audio and .srt, thumb.py, shorts.py and mkshorts.py, covers.py).
- vidIQ: 0 credits (renew 17 Dec); research and SEO used the free yt-stats workflow.

### 5. "Your $16 meal" Facebook Reel (0:48, built 19 Nov 2026)
- Facebook-first Reel for the Money Map Page (also usable as a YouTube Short). Topic from claude/facebook-reel-research-2026-11-19.md ("how restaurants make money", 6/7 High, competition Medium).
- Look: "Chalkboard menu". Dark green chalkboard in a wooden frame with chalk smudges; Permanent Marker headings, Kalam body and captions; pastel chalk yellow, pink, blue and green; Money Map wordmark in gold top left.
- Scene vocabulary: chalk bill line "MEAL ...... $16"; a plate drawn as a pie with slices filling one by one (food, staff, rent/power/fees, profit) and the 80c profit slice pulled out; chalk legend with cents per dollar; two chalk bars (+36% costs, +36% menu prices); ten chalk stick figures with four crossed out; closing chalk statement and route-M mark.
- Structure: one bill broken into its slices, then "since 2019" context, then the close.
- Hook: shocking number ("You pay sixteen dollars for a meal. The restaurant keeps about eighty cents.").
- Voice: bf_isabella 0.96. Sound: narration, chalk scratch on each new line, very quiet low pad.
- Source: National Restaurant Association, 8 Jul 2026 (cost split per $1, costs +36% 2019 to 2026, menu prices +36%, 42% not profitable in 2025).
- Engine: claude/money-map-chalk-engine/reel.py. Pack: facebook-pack-restaurant-reel.txt.

### 6. Black Friday Short "Are Black Friday Deals Real?" (0:29, built 21 Nov 2026, post Wed 25 Nov 6 pm Lagos)
- Look: "Shop window". Night-street gradient with bokeh and glass reflection streaks edge to edge; a red BLACK FRIDAY banner with chasing bulbs across the top; swinging cream price tag on a string; Poppins Bold headlines, Inter small labels, DejaVu Sans Mono for counters.
- Scene vocabulary: swinging price tag (WAS $139, NOW $119) with a circle then strike-through; a 52-week price strip lighting up green (same or cheaper), amber, red sale weeks, with a DAY counter to 365; 83% count-up; TV with DOORBUSTER burst and a falling stock count; shopping cart filling with full-price extras; red countdown clock; torn-edge "EXAMPLE BASKET" receipt with a NET: +$73 SPENT bar; yellow sticky note "CHECK THE PRICE HISTORY"; gold route-M end card with a FOLLOW FOR MORE pill.
- Structure: hook, evidence (Which? tracked a year, 83%), three numbered reasons the store still wins, receipt, sticky-note close.
- Hook: unexpected outcome ("This Black Friday deal isn't the cheapest price of the year.").
- Voice: af_kore 0.98. Sound: narration, whoosh on each scene, receipt ticks, quiet low pad, no music.
- Source: Which? (UK), 175 products, 83% cheaper or equal at least once outside the four-week sale (published Nov 2025).
- Engine: claude/money-map-bf-engine/bf_short.py (+ bf_common.py). Pack: upload-pack-black-friday-short.txt.

### 7. Black Friday Facebook Reel "50% OFF of what?" (0:30, music only, built 21 Nov 2026, post Thu 26 Nov 3 pm Lagos)
- Look: "Price-history line". Light cool-white graph paper edge to edge, slate ink, red accent; a plain grey speaker on a shelf with a red 50% OFF sticker; monitor-style price line with a pulsing leading dot and a live $ readout pill; navy text cards for the 83% card and the end card.
- Scene vocabulary: sticker slap with impact ring; price line drawn month by month ($60 flat, $100 October bump, $50 November, $49 January); "50% OFF!" popup; the October bump glowing red; 83% count-up card; end card with route-M mark.
- Structure: hook, price line story told as text cues (JAN TO SEP, OCTOBER, NOVEMBER, JANUARY), the $100 "was" price lasted 4 weeks, Which? card, "check the price history" close. Loops.
- Hook: conflict ("STORE SAYS: 50% OFF / PRICE HISTORY SAYS:").
- Voice: none. Sound: synthetic lo-fi loop, 96 bpm, 12 bars = exactly 30.0 s so it loops; kick/snare/hat, bass, Rhodes-style chords; thump on the sticker slap, chime at 8 s, whoosh at 20 s.
- Engine: claude/money-map-bf-engine/bf_reel.py. Pack: facebook-pack-black-friday-reel.txt.
- Full-bleed check passed (edge pixels are scene background; no border).

### 8. "Same money, two choices" episode 1, coffee (Facebook Reel, 0:36, music only, built 21 Nov 2026, post Fri 27 Nov 2 pm Lagos)
- Look: "Split screen". Two full-height columns edge to edge: warm orange café on the left (striped awning, chalk menu "COFFEE $5", wood counter) and cool teal home kitchen on the right (window with a "$0.60 a cup" sticky note, coffee machine with steam, tiled counter); a thin white divider down the middle; Poppins Bold headlines, DejaVu Sans Mono for counters, navy ink, gold accent. Simple front-on figures (café side frowns from day 150, home side smiles).
- Scene vocabulary: big white money counters over each column ($0 vs $60 on frame 1 with an impact ring, then counting up), a DAY n OF 250 WORKDAYS chip that pulses every 50 days, gold coin stacks side by side on the counters (one disc per $25, a coin flying from each person into its stack), a dashed line and double arrow for the gap, a navy "$1,040 APART. SAME COFFEE." banner, an end card where the two colours fill the whole screen.
- Structure: question hook, year of workdays played as a race (250 days over 19 s), freeze and reveal at 0:24, end card with series name, next episode and follow line. Loops.
- Hook: biggest question ("SAME COFFEE. 1 YEAR. WHO SPENDS MORE?").
- Voice: none. Sound: synthetic loop, 100 bpm, 15 bars = exactly 36.0 s; e-piano chords, bass, shaker, rim and kick from bar 5, marimba melody from bar 5 (octave doubled in bar 10), coin clinks synced to every coin landing (dense on the left, sparse on the right), riser into the reveal at 24.0 s.
- Numbers (labelled example prices, not advice): café $5 x 250 = $1,250; home $60 machine + $0.60 x 250 = $210; gap $1,040.
- Engine: claude/money-map-split-engine/coffee.py (+ common.py, README). Pack: facebook-pack-coffee-reel.txt. Full-bleed check passed.
- Next episodes (new look each time): phone every year vs every 3 years; 4 streaming services vs 1; delivery app vs pickup.

### 9. "Why is printer ink so expensive?" Short (series "Why is it so expensive?" ep 1, 0:25, built 21 Nov 2026, post Mon 30 Nov 6 pm Lagos)
- Look: "Blueprint". Deep blue gradient with a drafting grid edge to edge (minor lines every 40 px, major every 200), white line-art drawings that draw themselves on, cyan dimension arrows, yellow and red callout boxes; Anton headlines, Share Tech Mono labels, Poppins captions.
- Scene vocabulary: cartridge line drawing with centre line, ink window and chip contacts; $40.22 PER OUNCE callout with leader; racing horizontal bars (steak $3.41, Scotch $13.01, ink $40.22) with a 3x badge; printer line drawing with SOLD FOR $70 and BUILD COST (EST.) ~$120 callouts and a -$50 stamp; "razor = printer, blades = ink" rows with cartridges and coins dropping; chip magnifier bubble with a mirrored wrong cartridge bouncing off the slot (NO FIT); stacking REFILL blocks passing a dashed printer-price line; "NOT JUST INK: A BUSINESS MODEL" stamp; end card with EP. 2 teaser and FOLLOW pill.
- Structure: shocking-number race, then four numbered "figures" (printer cost, razor and blades, chip lock-in, refills pass the printer price), stamp close that repeats the opening cartridge so the Short loops.
- Hook: shocking number ("Per ounce, this ink costs three times more than aged Scotch."). Script hook (silver) dropped because silver now costs more per ounce than the ink.
- Voice: af_aoede 0.98.
- Sound: narration, plotter-sweep noise at each scene start, ticks while bars grow, coin clinks, a lock click and thunk on the chip scene, a low thump on stamps, very quiet F-major pad (87, 131, 220 Hz), chime at the end card.
- Sources: Techlicious (1 Jan 2025) per-ounce table; Consumer Reports / IHS Markit ($70 printer, about $120 to build, undated); Techlicious (ink cost can pass printer price in 1 to 2 years).
- Engine: claude/why-expensive-engine/ (wx_common.py helpers, wx_engine.py runner, ink.py episode). Pack: upload-pack-printer-ink-short.txt. Full-bleed check passed.
- Next episodes in the series (new look each time, never blueprint again): Lego, RAM.

### 10. "Who Owns the National Debt? It's Not China" (long 8:18 plus two Shorts, built 21 Nov 2026; long Tue 1 Dec 3 pm, Short A Wed 2 Dec 6 pm, Short B Sat 5 Dec 3 pm Lagos)
- Look: "IOU wall". Dark green vault wall of riveted panels edge to edge; engraved cream I.O.U. certificates with guilloche borders and a brass seal; brass-framed black ticker boards; four holder colours (trust funds gold, Fed blue, foreign holders red, everyone else green); a share bar at the top right that fills as each holder is revealed; brass chapter plaques. Cormorant SC for certificate headings, IBM Plex Serif for amounts, Saira ExtraCondensed for labels and big numbers, Poppins for Short captions.
- Scene vocabulary: a wall of blank certificates; a stamped CHINA certificate with a 1.4% donut; people row "$119,000 each"; stacks of certificates per holder; trust fund bar with GOVERNMENT OWES GOVERNMENT stamp; two-bar GDP comparison; Fed vault with a rate gauge and a Fed holdings area chart; foreign holders bars (Japan, U.K.), China's line from $1.3T to $564B, the myth card (#1 China then, #1 Japan now), Belgium and Cayman cards; ship carrying goods and dollars; tiles for banks, funds, pensions, insurers, state governments and people; a retirement pie; bills, notes and bonds lengths; rolled-over certificate cycle; auction chain; 3.4% rate board; interest-flow coins to all four; final pie and 77/23 split; check-it-yourself boards; end card.
- Structure: myth versus reality. A hook with the China myth, then four holders in order (government trust funds, the Fed, foreign holders, everyone else), how it is paid back, and a closing pie with sources to check. Eight chapter plaques.
- Hook: unexpected outcome ("China holds most of it?" answered by 1.4%).
- Voice: bm_lewis 0.92 (long), bm_daniel 0.96 (Short A), am_liam 0.96 (Short B).
- Sound: narration, soft chimes, ticks, thumps, rustle and clinks per scene, quiet pad bed.
- Shorts (1080x1920, same wall look, Poppins captions burned in at y 1400): A "Not China" (0:30) hook "BIGGEST FOREIGN LENDER TO AMERICA?" with a NOT CHINA stamp, Japan $1,063B, U.K. $986B, China $564B 1.4%, 77% held inside the U.S.; B "Social Security IOUs" (0:32) trust fund of certificates, special securities, $2.3T main retirement fund, cashing in, $40.7T debt.
- Figures (18 Nov 2026 Debt to the Penny): $40.7T total; trust funds $7.8T (19%); Fed $4.6T (11%); foreign $9.2T (23%); others about $19.1T (47%); Japan $1,063B; U.K. $986B; China $564B (1.4%). Gate: neutral on the debt, no verdict, no party.
- Engine: claude/money-map-iou-engine/ (iou_common.py, iou_content.py, iou_engine.py, iou_mix.py, tts.py, iou_shorts.py, covers.py, README with gotchas). Packs for all three videos are in that folder.

### 11. "Thanksgiving dinner for 10" Facebook Reel (0:35, music only, built 22 Nov 2026, post Sun 22 Nov 5 pm Lagos)
- Look: "Top-down table". Dark walnut planks edge to edge, cream linen runner with orange edge stripes, ten plates on orange napkins down both sides, autumn leaves and pumpkins; flat top-down dishes (turkey platter, stuffing, sweet potatoes, rolls, peas, cranberries, veggie tray, pie, milk, shakers); kraft price tags with a hole; dark-brown "THE BILL" board with cream mono digits; cream tent-style card for the headline; Poppins Bold, DejaVu Sans Mono.
- Scene vocabulary: dishes dropping onto the table with shadow and impact ring, a price tag popping on each, running bill; board locking with a gold ring; $5.86 kraft discs popping on all ten plates; dimmed table with three panels (horizontal bars 2025 vs 2026 with +6%, turkey price tags with +10%, vertical bars 2022 record vs 2026 with 8.5% below); orange leaf end card.
- Structure: guess-the-bill hook, turkey alone (40%), sides and pie added one by one, total and per-person payoff at 0:15 to 0:19, three context panels, end card. Loops.
- Hook: challenge / guess ("THANKSGIVING FOR 10. GUESS THE BILL."; board rolls random numbers on frame 1). Cover: "10 PEOPLE. ONE DINNER. HOW MUCH?" with $??.??, no prices.
- Voice: none. Sound: folk loop at 109.7 bpm, 64 beats = exactly 35.0 s; plucked arpeggio, bass, stomp, clap and marimba melody from bar 5, clink and thud on every dish landing, chime at the lock, ascending marimba on the plates, whoosh per panel.
- Source: AFBF 41st Thanksgiving survey, 18 Nov 2026 ($58.63, $5.86 each, +6% on $55.18, turkey $23.68 up from $21.50, 2022 record $64.05). Source goes in the first comment, not on the end card.
- Engine: claude/money-map-thanks-engine/. Pack: facebook-pack-thanksgiving-reel.txt. Full-bleed check passed.

## Used so far (do not repeat next)
- Looks: dark ledger board; cream paper editorial; bank statement with side panel (and its vertical version for Shorts); transit map with departure boards; chalkboard menu (Facebook Reel); night shop window with price tag (Short); light price-history graph with speaker (Reel); warm and cool split-screen kitchens with coin stacks (Reel); blueprint drafting grid with callouts (Short); dark green vault wall with engraved I.O.U. certificates (long and Shorts); top-down Thanksgiving table with kraft price tags (Reel).
- Structures: single transaction walk-through; three numbered moves with recap; follow one deposit for a year with a running statement; why-it-fell cards then a route with 4 stops and a map recap; evidence then three numbered reasons then receipt (Short); one line story told in text cues (Reel); two-column race with a freeze and reveal (Reel); number race then four numbered figures with a stamp close (Short); myth versus reality with four holders revealed one by one and a closing pie (long); items dropped one by one into a running total, then three context panels (Reel).
- Hook types in order: question; unexpected outcome; shocking number; biggest question; shocking number (restaurant Reel); unexpected outcome (Black Friday Short); conflict (Black Friday Reel); biggest question (coffee Reel); shocking number (printer ink Short); unexpected outcome (US debt long and Shorts); guess-the-bill challenge (Thanksgiving Reel). Next should not be a guess challenge.
- Voices: bm_fable, am_puck (old betting Short, never posted), am_michael, bm_george, af_heart, bf_emma, am_eric, am_fenrir, af_bella, af_sarah, bf_isabella, af_kore (Black Friday Short), af_aoede (printer ink Short), bm_lewis (US debt long), bm_daniel (Short A), am_liam (Short B). The three music-only Reels had no voice.

## Ideas not yet used
- Looks: isometric city blocks; newspaper front page; spreadsheet grid; toy-brick (for the Lego episode); circuit board or memory chip (for the RAM episode).
- Structures: a day in the life of a branch; balance sheet built line by line; ranking from smallest to biggest income stream; timeline through history; follow one transaction across companies (fits Visa).
- Voices: any Kokoro voice not listed above (best remaining quality: af_nicole).

## Channel direction (17 Nov 2026 reset)
- Money Map restarts with searched "how X makes money" topics, long form 10 to 15 minutes as the main product, one or two Shorts cut from each.
- First five planned: How Banks Make Money; How Visa Makes Money; How Netflix Makes Money; How Luxury Hotels Make Money From Empty Rooms; How Casinos Make Money (betting set released that week). Revised 19 Nov 2026 by research: Visa, Netflix and hotels now crowded; Bitcoin crash made instead.
- Global audience, dollars, no country hashtags or country-only tags.
- Small Win Films was off hold again from 17 Nov 2026 afternoon, restarted from scratch with research-picked topics (see claude/small-win-films-research.md).
