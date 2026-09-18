# Samuel HQ.app

The board as a real app window instead of a browser tab. The installed bundle is at
`~/Applications/Samuel HQ.app`, outside this repo, so these two files are the parts
worth version control.

Samuel, Sept 18 2026: *"i want it to be the samuel HQ dashboard but somethig can
pop up"*. The board IS the interface. Monday does not get her own page; her wake
card is an overlay on this one, driven by her websocket.

## Rebuild

```bash
APP=~/Applications/"Samuel HQ.app"
mkdir -p "$APP/Contents/MacOS"
cp Info.plist "$APP/Contents/Info.plist"
cp SamuelHQ-launcher.sh "$APP/Contents/MacOS/SamuelHQ"
chmod +x "$APP/Contents/MacOS/SamuelHQ"
codesign --force --deep --sign - "$APP"
```

## What it does

1. Checks boardd on 8770. If it is down, kickstarts the launchd job and waits,
   rather than opening a window onto a dead port. If it stays down, it says so in
   an alert instead of showing a blank page.
2. Starts Monday.app if she is not already up. The board works without her and
   shows her as offline honestly, so this is a convenience, not a dependency.
3. Opens Chrome with `--app=` for a chromeless window (no tabs, no address bar,
   its own dock entry), on a dedicated `--user-data-dir` so the HQ window never
   inherits or disturbs Samuel's own tabs and logins.
4. Falls back to the default browser if Chrome is not installed.

## Related

- The page itself: `../TV13-live-board.html`
- Monday's bundle and its TCC story: `../../monday/app-bundle/README.md`
