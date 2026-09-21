# LOG, hq-tv

## 2026-09-19, native app and alarm failure-mode audit

- Replaced the visible Chrome wrapper with a signed native AppKit and WebKit `Samuel HQ.app`.
  It owns its Mac window, starts boardd and Monday, waits for readiness, and allows alarm
  audio without a first click.
- Persisted fired, dismissed, and snoozed wake state so reloads do not replay or lose an
  occurrence. Added a conservative five-minute wake catch-up after sleep or suspension.
- Fixed cancellation during snooze, which could previously re-ring after the shared alarm
  was already disabled.
- Ordered poll and websocket updates by `updated_at`, validated incoming alarm payloads,
  and made connection failure explicitly say the last confirmed alarm remains active.
- Prevented the HQ launcher from opening a second independent dashboard and made inactive
  alarm dialogs invisible to assistive technology.
- Made Monday's microphone state honest on the dashboard instead of claiming ready before
  the microphone was armed.

Verification: 17 static tests and the complete real-browser system contract passed.

## 2026-09-19, live board hardening

- Kept the locked noir skin and improved density, spacing, alarm readability, and panel shape.
- Replaced alert emoji and inferred tiers with explicit `severity` values from `boardd`.
- Made alarm and board HTTP failures visible without erasing last-known-good board content.
- Removed payload injection paths from alarm metadata by using text nodes only.
- Added reduced-motion behavior and an inline favicon to eliminate kiosk console noise.
- Fixed the 1280x720 layout that collapsed Today to zero height.
- Added static and real-browser contract tests across three screen sizes.
- Added a deterministic Monday websocket fixture that proves transcript and reply rendering.
- Removed an exact duplicate backup file after verifying its blob already exists in git history.

Verification at checkpoint: 9 static tests passed, plus Chrome checks at 1920x1080, 1280x720,
and 1024x768 against real `boardd` and the Monday websocket fixture.

## 2026-09-19, live alarm restored

- Found that TV13 displayed the shared alarm but had dropped the proven wake behavior from `index.html`.
- Restored the 30-minute warm dawn, struck-bell chime, full-screen wake card, nine-minute snooze,
  three-snooze cap, remote focus, audio readiness warning, and 1.6-second hold to dismiss.
- Alarm firing compares the local clock to the persisted `HH:MM`; it does not trust the display-only
  countdown hint, which rolls to tomorrow once the minute has begun.
- Added browser proof that a real alarm POST wakes the live board, snoozes, rejects a quick dismiss,
  and accepts a deliberate hold.

Verification at checkpoint: 12 static tests passed and the Chrome contract passed at all three sizes.
- Fixed a countdown rounding defect that could render `23h 60m`; the firing minute now reads `now`.
- Extended the system runner through Monday's real alarm client before browser verification, so
  the voice client, board service, and TV surface are proven in one command.

## 2026-09-21 — the connections strip, and an X that works

Samuel: *"make the systems watcher acc real like if it cant ping the turo system
or school system say it needs to sing in this live app needs to be connected to
everything and acc work correctly or its useles also neesd an X button the monday
stuff when monday doesnt work correctly and i dont want to say close out"*.

- **Connections strip** (`#conn`) between the alarm and the zones. Calm state is
  one line; when something needs him it becomes cards with the whole sentence,
  never an ellipsis. Data: `/api/board.connections`, from connwatch.
- **Systems detail stopped truncating.** "school LOGIN EXPIRED, sign..." was
  cutting off the half that tells him what to do. Two line clamp now.
- **X on Monday's card** plus Escape, plus a mute button. The X sends `cancel`
  over her websocket, so it ends the turn rather than only hiding the card.
- **Found by clicking, not by reading:** `.veil.show` never restored
  `pointer-events`, so the card swallowed every click and the X was decorative.
  Locked with a test.
- **Board unreachable** now says so in the strip instead of showing the last
  reading as if it were fresh.
- Tests: 29 in `tests/test_live_board.py`, all green.

### Same night, after the first pass
- Cards are for rows that need action. Unproven rows moved to a single line under
  the header, because the strip plus a ninth system row had starved the TODAY panel
  to zero height at 1080 (and 25px at 720). The browser contract now asserts TODAY
  keeps 120px on every viewport, not only 720.
- Systems render three across under 800px tall.
- Playwright is installed at `~/hqtv-venv` and `tests/run_contract.py` runs the
  contract against an isolated boardd plus the scripted fake Monday, which now
  records inbound messages so the X can be proven to cancel.
