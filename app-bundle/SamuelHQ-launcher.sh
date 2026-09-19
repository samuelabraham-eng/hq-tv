#!/bin/bash
# Samuel HQ.app -- the dashboard as a real app window, not a browser tab.
#
# Samuel, Sept 18 2026: "i want it to be the samuel HQ dashboard but somethig can
# pop up". So the board IS the interface; Monday's wake card is an overlay on it.
# Chrome's --app= flag gives a chromeless window: no tabs, no address bar, its own
# dock entry. Nothing is installed and no server runs here -- boardd already
# serves the page, this only opens a window onto it.
set -u
BOARD="http://127.0.0.1:8770/"
PORT=8770
LOG="${HOME}/monday-runner/state/hq-app.log"
mkdir -p "$(dirname "$LOG")"
stamp(){ date '+%Y-%m-%d %H:%M:%S'; }

# boardd is launchd-owned (com.samuel.boardd, KeepAlive). If it is not answering,
# kick it and wait rather than opening a window onto a dead port.
if ! /usr/bin/nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1; then
  echo "$(stamp) boardd not answering, kickstarting" >> "$LOG"
  /bin/launchctl kickstart -k "gui/$(id -u)/com.samuel.boardd" >/dev/null 2>&1
  for _ in $(seq 1 20); do
    sleep 1
    /usr/bin/nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1 && break
  done
fi

if ! /usr/bin/nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1; then
  echo "$(stamp) FATAL: boardd still down on $PORT" >> "$LOG"
  /usr/bin/osascript -e 'display alert "Samuel HQ" message "The board service (boardd) is not running on port 8770." as critical' >/dev/null 2>&1
  exit 1
fi

# Monday is the voice lane. Start her if she is not up; she is a separate app so
# the board still works without her (it shows her as offline, honestly).
if ! /usr/bin/nc -z 127.0.0.1 8765 >/dev/null 2>&1; then
  echo "$(stamp) starting Monday alongside the board" >> "$LOG"
  /usr/bin/open "${HOME}/Applications/Monday.app" --args --background >/dev/null 2>&1
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
echo "$(stamp) opening the board" >> "$LOG"
if [ -x "$CHROME" ]; then
  # its own profile dir so the HQ window never inherits or disturbs his tabs
  exec "$CHROME" --app="$BOARD" \
       --user-data-dir="${HOME}/monday-runner/hq-chrome" \
       --window-size=1600,980 \
       --autoplay-policy=no-user-gesture-required \
       --no-first-run --no-default-browser-check
fi
# no Chrome: fall back to the default browser rather than failing
exec /usr/bin/open "$BOARD"
