import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excluded = {"claude/yt-stats/yt-signin.txt": "secret (OAuth client and refresh token), never committed"}
merged = {f: "merged into claude/film-log.md on 26 Nov 2026" for f in [
    "claude/film-log-5-she-never-knocked.md",
    "claude/film-log-6-relatable-reel-1-group-chat.md",
    "claude/film-log-7-relatable-reel-2-wrong-wave.md",
    "claude/film-log-8-relatable-reel-3-night-in.md",
    "claude/film-log-9-every-sunday-at-6.md",
]}
paths = [p.strip() for p in open(os.path.join(root, "tools", "project-file-list.txt")) if p.strip()]

rows = []
done = pending = 0
for p in sorted(paths):
    if p in excluded:
        rows.append(f"| {p} | excluded: {excluded[p]} |")
    elif p in merged:
        rows.append(f"| {p} | {merged[p]} |")
        done += 1
    elif os.path.exists(os.path.join(root, p)):
        rows.append(f"| {p} | copied |")
        done += 1
    else:
        rows.append(f"| {p} | pending |")
        pending += 1

out = [
    "# Manifest: every file from the Claude project \"AI Videos and YouTube\"",
    "",
    f"{len(paths)} files in the project. Copied: {done}. Pending: {pending}. Excluded: {len(excluded)}.",
    "Regenerate with: python3 tools/manifest.py",
    "",
    "| Path | Status |",
    "|---|---|",
] + rows
open(os.path.join(root, "MANIFEST.md"), "w").write("\n".join(out) + "\n")
print(f"copied {done}, pending {pending}, excluded {len(excluded)}")
if "--strict" in sys.argv and pending:
    sys.exit(1)
