# Script intake (Gemini writes, Antigravity builds)

Drive layout (AI videos / Scripts /): Money Map and Small Win Films, each with Inbox, Built, Needs-changes.
Folder IDs: Scripts 1AL0cVt2gd7YsZ95miN9y9ywqN19ZOs4i
  Money Map Inbox 1VKMgJdj0jc6ycAmFCUxO6iNN0E3Q7XL2, Built 1vRfpv0dXgpQsT1BcPNzxjV8H3_IKkvkD, Needs-changes 1QvKstVOZrTnefGs_nr1wgwPan-9EAwKA
  Small Win Films Inbox 1ZLPJUu39hPNwCKEvBDti1sQ-_mztjbw4, Built 10i8RrAB2O8ml_98aV5r7Ny3GI_X_h4wk, Needs-changes 1vrqJliyQqpjoFN-YOEmtv6sdvQjYg1X5

Flow
1. Gemini writes a script from SCRIPT-TEMPLATE.md into the channel's Inbox with Status: DRAFT.
2. Kenny reads it, edits if needed, sets Status: APPROVED.
3. Kenny sends the agent: "Build the approved scripts in Drive."
4. The agent: lists both Inboxes (gdrive readonly ls <id>), downloads only files whose Status is APPROVED, runs the policy and repetition gate in claude/yt-stats/workflow.md against the channel log, then
   - passes: builds with the right engine, runs claude/qa-gate.md, delivers, updates logs, moves the script to Built.
   - fails or unclear: moves it to Needs-changes with a short reason added at the top, and tells Kenny.
5. Scripts with Status DRAFT are never built. Small Win Films scripts still wait for Kenny's go, which is the APPROVED line.
6. The agent never edits a script's story. It only flags problems.
