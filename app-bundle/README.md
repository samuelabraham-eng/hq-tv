# Samuel HQ.app

The board as a real app on one monitor, not a browser tab. The installed bundle is
at `~/Applications/Samuel HQ.app`, outside this repo, so the three files here are
the parts worth version control.

Samuel, Sept 18 2026: *"i want it to be the samuel HQ dashboard but somethig can
pop up"*. The board IS the interface. Monday does not get her own page; her wake
card is an overlay on this one, driven by her websocket.

Samuel, Sept 24 2026: *"similar to how for fortnite i can put my fortnite on one
monitor and fullscreen it and still use my computer on the other"*.

## Why it is NOT fullscreen

macOS native fullscreen puts a window in its own Space. A Space takes the whole
Mac: click the other monitor and the system can swap away from it, Mission Control
fights it, and Cmd+Tab gets strange. That is the opposite of what he asked for.

So the window is:

- **borderless**, sized to the chosen screen's exact frame, edge to edge
- `.canJoinAllSpaces` so switching desktops on the laptop never blanks the board
- `.stationary` so it does not travel with him between Spaces
- `.fullScreenNone` so macOS never offers native fullscreen at all
- `hidesOnDeactivate = false` so it keeps drawing while he works elsewhere
- window level `.normal`, so he can still drop a window on that display

That combination is what makes it behave like a game on a second monitor.

## Choosing the display

The HQ icon in the menu bar (a small square) lists every attached display, with a
check on the one in use. The choice is remembered by display ID, with the display
name as a fallback, because display IDs are not stable across reboots on every
Mac. Unplug the monitor and it moves to what is left; plug it back in and it goes
home, on `didChangeScreenParametersNotification`.

Default with no saved choice: the widest display that is not `NSScreen.main`,
because the main one is the computer he is trying to keep using.

**Keep on top of that display** in the same menu raises it above the menu bar for
a true edge to edge kiosk. Off by default.

Since the window has no title bar, the menu bar item and Cmd+Q are the way out.
`KioskWindow` overrides `canBecomeKey` so a borderless window still takes the
keyboard, which Cmd+Q and the alarm's "press any button once" both need.

## Mirrored displays

⚠️ If the displays are MIRRORED, macOS reports them as one screen and this app
cannot put the board on one and leave the other free. Nothing in software fixes
that; mirroring has to come off in System Settings, Displays.

The app detects it and writes a red footer onto the board saying so, rather than
covering both screens with the same picture and pretending it worked. The test is
`CGDisplayIsInMirrorSet` alone. An earlier version also required
`CGDisplayMirrorsDisplay != 0` and silently never fired on this exact Mac, because
the LG is the MASTER of the mirror set so it mirrors nobody and returns 0.

## Rebuild

```bash
APP=~/Applications/"Samuel HQ.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp Info.plist "$APP/Contents/Info.plist"
swiftc -O -framework Cocoa -framework WebKit SamuelHQ.swift -o "$APP/Contents/MacOS/SamuelHQ"
codesign --force --deep --sign - "$APP"
```

Quit the running copy first (`pkill -f "Samuel HQ.app/Contents/MacOS/SamuelHQ"`),
or `open -a` just activates the old instance and the new binary never runs. That
wasted a verification pass on Sept 24.

## What it does on launch

1. Kickstarts `com.samuel.boardd` and waits for port 9770 rather than opening a
   window onto a dead port. If it stays down it says "starting the live board"
   instead of showing a blank page, and keeps retrying.
2. Starts Monday.app if she is not up. The board works without her and shows her
   as offline honestly, so this is a convenience, not a dependency.
3. Loads the board and, if the displays are mirrored, says so on it.

## Related

- The page itself: `../TV14-board.html`
- `SamuelHQ-launcher.sh` is the older Chrome `--app=` route, kept as a fallback
  for a machine with no built bundle
- Monday's bundle and its TCC story: `../../monday/app-bundle/README.md`
