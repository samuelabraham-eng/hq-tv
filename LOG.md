# LOG, hq-tv

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
