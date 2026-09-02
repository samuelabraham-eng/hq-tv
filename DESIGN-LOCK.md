# DESIGN-LOCK, hq-tv

Written Sept 1, 2026, at the start of TV13 (the live board build) because CURRENT.md
flagged that no lock existed. Authority: the approved noir skin that has carried every
TV build since the Aug 10 loop, read directly out of `index.html`.

## The skin (locked)

- Ground `#100e0c`, tile `#1a1512`, tile2 `#211b16`, hairline `#2a241d`
- Text bone `#f1ebdf`, secondary dim `#8a8073`
- Accent gold `#c9a96a` (accents and chips, never large fills), on-accent `#2b2208`
- Alert red `#d0402e`, ok green `#7e9b7a`
- Font: Plus Jakarta Sans (400/500/700/800), display headings bold lowercase
- Warm black, premium, calm, generous spacing. No gradients, no glassmorphism,
  no purple, no cold grays.

## Content vs skin authority

- SKIN: locked above. New pages reuse these tokens exactly.
- CONTENT: free to evolve (zones, tiles, data wiring). TV13's five-zone layout
  (systems, alerts, now working, today, Monday bar) was approved by Samuel from the
  Sept 1 mockup: "Layout approved, build it... I want it 100% done."
- Honesty rules ride every build: real data only, stale states shown as stale,
  no placeholder numbers presented as live (TV01's lesson).

Changes to the SKIN need Samuel's word. Changes to CONTENT follow the normal
build-code flow (registry in HQ memory/BUILD-CODES.md).
