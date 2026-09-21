"""Run the browser contract against an isolated boardd plus the fake Monday.

Use this on a machine where the real Monday is installed: `run_browser.py` also
exercises her HTTP alarm client, which drags in the whole daemon dependency tree
(numpy, mlx, sounddevice) that a test venv has no business installing.

    ~/hqtv-venv/bin/python tests/run_contract.py

⚠️ Stop the real Monday first (`pkill -f "monday.app"`). The fake binds 8765 and
will refuse to start while she holds it, and NEVER point BOARD_URL at the live
boardd: the contract POSTs to /api/alarm and would wipe his real alarm.
Test venv: python3.12, `pip install -r tests/requirements.txt`, then
`playwright install chromium`.
"""
import os, socket, subprocess, sys, tempfile, time
from pathlib import Path

HQTV = Path.home() / "Desktop/Samuel-HQ/projects/hq-tv"
PROJECTS = HQTV.parent
LOG = Path("/tmp/fake-monday-inbox.jsonl")


def wait(port, proc, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if proc.poll() is not None:
            raise RuntimeError(f"port {port} process exited {proc.returncode}")
        with socket.socket() as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f"port {port} never opened")


with tempfile.TemporaryDirectory(prefix="hq-tv-contract-") as state:
    env = os.environ.copy()
    env.update(SAMUEL_HQ=str(Path.home() / "Desktop/Samuel-HQ"),
               BOARDD_TV_DIR=str(HQTV), BOARDD_STATE_DIR=state,
               BOARDD_PORT="8780", FAKE_MONDAY_LOG=str(LOG))
    LOG.write_text("", encoding="utf-8")
    boardd = subprocess.Popen([sys.executable, str(PROJECTS / "home-server/boardd/boardd.py")], env=env)
    monday = subprocess.Popen([sys.executable, str(HQTV / "tests/fake_monday.py")], env=env)
    try:
        wait(8780, boardd)
        wait(8765, monday)
        os.environ.update(BOARD_URL="http://127.0.0.1:8780/", EXPECT_MONDAY="1",
                          BOARDD_PORT="8780", FAKE_MONDAY_LOG=str(LOG))
        sys.path.insert(0, str(HQTV / "tests"))
        import browser_verify
        browser_verify.main()
        print("browser contract PASSED")
    finally:
        for p in (monday, boardd):
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: p.kill()
