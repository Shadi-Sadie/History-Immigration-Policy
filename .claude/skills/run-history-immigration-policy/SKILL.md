---
name: run-history-immigration-policy
description: Run, screenshot, and visually verify the History-Immigration-Policy web app. Use when asked to run, start, screenshot, or verify the word-to-law timeline, the D3 scroll-driven visualization, or any part of this interactive journalism piece.
---

This is a static web app — no build step. `word-to-law.html` is self-contained; the main interactive (`script.js` + `style.css`) needs a wrapping index HTML that hasn't been committed yet.

The driver at `.claude/skills/run-history-immigration-policy/driver.py` starts a Python HTTP server and launches `google-chrome --headless` with CDP on port 9222, then scrolls to a given pixel offset and captures a PNG.

## Prerequisites

```
python3 -m pip install websockets -q
# google-chrome is already at /usr/bin/google-chrome (Chrome 147)
```

No `xvfb-run` needed — Chrome headless runs without a display server.

## Run (agent path)

Take a screenshot at a specific scroll position (px from top):

```bash
python3 .claude/skills/run-history-immigration-policy/driver.py screenshot 2500 /tmp/tl-2500.png
```

The page's total scroll height is 12176 px. Useful reference points:

| Scroll px | What you see |
|---|---|
| 0 | Intro — "From the word to the law" title card |
| 2500 | Timeline overview begins — 1600s–1808 nodes |
| 5000 | Zoom phase — gold path, 1808–1875 zoomed in |
| 7300 | Zoom phase — McCarran-Walter Act card visible (1952) |
| 10000+ | Follow phase — late-20th-century policies |

Screenshot a sweep of the whole scroll range (10 frames):

```bash
python3 .claude/skills/run-history-immigration-policy/driver.py scroll-range 0 12000 1200 /tmp/sweep/
```

Screenshots land wherever you pass as the last argument. Default (no path arg) is `.claude/skills/run-history-immigration-policy/screenshots/scroll-<px>.png`.

## Run (human path)

```bash
python3 -m http.server 8000
# open http://localhost:8000/word-to-law.html in a browser
# scroll down to enter the timeline
```

## Gotchas

- **Scroll-driven D3 needs a 1.0 s settle** after `window.scrollTo` before screenshotting — the SVG path draw and node glow transitions take ~600 ms. The driver already waits; don't shorten it.
- **Port 9222 must be free.** If a prior run crashed without cleanup, `pkill -f remote-debugging-port=9222` before retrying.
- **Port 8743** is the HTTP server port used by the driver (not 8000, to avoid collisions with other dev servers).
- **The detail card only appears after the zoom phase** (~7000 px+). If you're looking for a specific policy card, scroll past 6500 px.
- **`chromium-cli` is not installed** — use `google-chrome --headless=new` directly as the driver does.
- **`--no-sandbox --disable-gpu`** are required in this container; the driver passes both.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No CDP page found` | Chrome didn't start in time; increase `time.sleep(2.0)` in driver.py |
| `Connection refused` on port 9222 | Port already occupied — `pkill -f remote-debugging-port=9222` |
| Blank/dark screenshot at scroll 0 | Normal — intro section is a full-viewport dark card; scroll to 2000+ |
| `ModuleNotFoundError: websockets` | `pip3 install websockets` |
