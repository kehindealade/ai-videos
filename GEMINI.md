# Gemini instructions

Follow AGENTS.md in this repo. It holds the standing rules for this project, and START-HERE.md explains the channels, the reading order and the pipeline.

Notes for Gemini (app, Gemini CLI, Antigravity, Jules):
- In the Gemini app, attach START-HERE.md, AGENTS.md, memory/preferences.md and the channel log you need from the Google Drive folder "AI videos", then ask.
- Rendering needs Python, pycairo and ffmpeg. The Gemini app cannot render; use Antigravity or Gemini CLI on a computer, Jules (cloud VM, works through this GitHub repo), Google Colab with render.ipynb, or the GitHub Actions workflow in .github/workflows/render.yml.
- Kokoro voice model files are not in the repo; setup.sh downloads them.
