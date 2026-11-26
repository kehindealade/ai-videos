# Instructions for AI agents working in this repo

Read START-HERE.md before doing anything. It explains the two channels (Money Map and Small Win Films), the reading order and how a video gets made.

Standing rules (full versions in memory/preferences.md and claude/yt-stats/workflow.md):

1. Kenny's own instructions in the chat come first. These docs record his past decisions.
2. Research before choosing any topic; every topic passes the policy and repetition gate in claude/yt-stats/workflow.md.
3. Small Win Films: send the full script and wait for his go before building. Give options when proposing.
4. Never repeat a design, look, voice, hook type or structure. Check the channel log first and add the new entry after.
5. No Nigerian names, no kids, no politics, no named real people, no financial advice as fact.
6. Thumbnails and covers are cliffhangers. Vertical video fills 9:16 edge to edge, text in the safe band.
7. Voices: a new voice for every video (claude/voice-rules.md). Chatterbox Turbo by default, Kokoro as the reference source or fallback.
8. Deliver the video, its thumbnail or cover, and one txt upload pack per video. Name files CHANNEL_platform_topic.
9. After each build, update the channel log, STATUS.md, the build plan status and memory/ notes, then commit.
10. Never commit secrets (OAuth files, tokens, API keys). .gitignore blocks the common names; check anyway.
11. Never commit rendered media (mp4, wav, png). Put renders in Google Drive "AI videos/Renders/<Channel>/<Platform>/<topic>/" (one subfolder per video/set so Renders stays organised).
12. Reply style: plain, practical, concrete examples, no bold, no em dashes, no headers in prose replies.
13. Ask Kenny before anything that changes a finished video's content, moves a post past its slot, or that you judge unadvisable.
14. QA gate: no video, Short, Reel or cover is uploaded or reported done until it passes claude/qa-gate.md (mux with the safe loudness chain, run python3 tools/qa.py, answer all 9 manual checks from the sheets, fix and re-run until everything passes). Paste the results in your reply.
15. Model tiering (limit management): use lower/faster models (Flash, Flash-Lite, Haiku, Sonnet) for mechanical and routine tasks (rendering existing engines, running tools/qa.py, Drive uploads/folders, API scheduling, upload packs, log updates), and reserve higher models (Pro, Opus) only for intensive creative/code tasks (new story scripts, new visual designs and pycairo engines from scratch).

Engines and render commands: ENGINE-INDEX.md. Current state: STATUS.md. Setup: setup.sh or render.ipynb.
16. Script intake: scripts written by Gemini arrive in Drive "AI videos/Scripts/<Channel>/Inbox" using claude/script-intake/SCRIPT-TEMPLATE.md. Build only files marked Status: APPROVED, run the gate first, then move to Built or Needs-changes. Details in claude/script-intake/README.md.
