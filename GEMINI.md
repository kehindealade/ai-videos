# Gemini instructions

Follow AGENTS.md in this repo. It holds the standing rules for this project, and START-HERE.md explains the channels, the reading order and the pipeline.

Notes for Gemini (app, Gemini CLI, Antigravity):
- In the Gemini app, attach START-HERE.md, AGENTS.md, memory/preferences.md and the channel log you need from the Google Drive folder "AI videos", then ask.
- Rendering needs Python, pycairo and ffmpeg. The Gemini app cannot render; use an Antigravity Remote Agent (cloud VM, start it from antigravity.google.com on a phone, attach this GitHub repo; Jules shuts down on 31 Dec 2026), Antigravity or Gemini CLI on a computer, Google Colab with render.ipynb, or the GitHub Actions workflow in .github/workflows/render.yml.
- Kokoro voice model files are not in the repo; setup.sh downloads them.
- In a remote agent, run bash setup.sh first. Commit code and docs only; renders go to the Drive folder "AI videos/Renders".
