# hq-tv

The Samuel HQ dashboard for a TV, an iPad, a phone, or a monitor. The current production
surface is `TV13-live-board.html`. It is served by `home-server/boardd`, which curates a
small JSON view from Samuel HQ and exposes the alarm contract. Monday connects directly to
the page over her local websocket.

- `TV13-live-board.html` is the live board and has no build step.
- `index.html` is the earlier standalone dashboard and alarm prototype.
- The private brain is never served as a directory. `boardd` returns only the fields the
  board knows how to display.
- The locked noir design in `DESIGN-LOCK.md` applies to the live surface.
- `app-bundle/SamuelHQ.swift` is the native macOS shell installed as `Samuel HQ.app`.
  It starts the local services and hosts the board in a real AppKit window.

## Live-board verification

The static suite guards design tokens, safe alarm rendering, honest failure states, semantic
alerts, and reduced motion. The browser suite launches Chrome against real `boardd`, tests
the alarm HTTP contract, simulates API failure and recovery, and verifies the Monday websocket
overlay at 1920x1080, 1280x720, and 1024x768. It also proves the shared alarm reaches the
full-screen wake state, snoozes, and requires a deliberate hold to dismiss.

Use the Python environment from the Monday daemon:

```sh
../monday/daemon/.venv/bin/python -m pytest -q
```

Run the browser suite with `../monday/daemon/.venv/bin/python tests/run_browser.py`. The runner
starts and stops both `boardd` and the deterministic websocket fixture in `tests/fake_monday.py`.
Before opening Chrome, it also sends a set and query through Monday's real alarm HTTP client.

## What works today
Live clock, a real alarm with a 30 minute sunrise ramp that uses the TV as a lamp, sound that
ramps rather than jump scares, question mark popovers on any number that needs explaining, a
"needs your word" strip for stale or unknown data, D-pad support for a Fire TV remote, and a
responsive layout down to a phone.

## Fire TV note
The screensaver can be set to Never in settings, but the sleep timer is separate, hidden, and
fixed at 20 minutes. It has to be disabled over ADB or the screen goes black regardless of
anything in this page.

## Tests

| Layer | Command |
|---|---|
| Source contract (fast, no browser) | `~/monday-venv/bin/python -m pytest tests/test_live_board.py -q` |
| Browser contract, 3 viewports | stop Monday, then `~/hqtv-venv/bin/python tests/run_contract.py` |

The browser pass drives a real chromium over an isolated boardd (temp state dir,
port 8780) and the scripted `fake_monday.py`, so it can ring the alarm, snooze it,
kill the board mid-poll and click the X on Monday's card without touching a single
live file. It caught two real defects on 2026-09-21: a nine row systems grid that
collapsed the TODAY panel to zero height at 720, and a card that swallowed clicks.
