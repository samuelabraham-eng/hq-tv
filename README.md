# hq-tv

The Samuel HQ dashboard for a TV, an iPad, a phone, or a monitor. One file, no build step,
no dependencies beyond a webfont.

- `index.html` is the whole app.
- Data lives in the `DATA` object at the top of the script. It is hand written for now and is
  honest about what it does not know. Phase 3 swaps it for a fetch of a curated file generated
  out of the private `samuel-hq` repo. Nothing else has to change.
- **Never point this at the private brain directly.** Only curated, safe fields leave HQ.

## What works today
Live clock, a real alarm with a 25 minute sunrise ramp that uses the TV as a lamp, sound that
ramps rather than jump scares, question mark popovers on any number that needs explaining, a
"needs your word" strip for stale or unknown data, D-pad support for a Fire TV remote, and a
responsive layout down to a phone.

## Fire TV note
The screensaver can be set to Never in settings, but the sleep timer is separate, hidden, and
fixed at 20 minutes. It has to be disabled over ADB or the screen goes black regardless of
anything in this page.
