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
