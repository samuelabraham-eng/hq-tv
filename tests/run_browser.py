"""Run the cross-repository live-board browser contract locally."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT.parent
HQ = PROJECTS.parent


def wait_for_port(port: int, process: subprocess.Popen, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"service on port {port} exited with {process.returncode}")
        with socket.socket() as probe:
            probe.settimeout(0.1)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise TimeoutError(f"service did not open port {port}")


def stop(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="hq-tv-test-") as state_dir:
        env = os.environ.copy()
        env.update(
            {
                "SAMUEL_HQ": str(HQ),
                "BOARDD_TV_DIR": str(ROOT),
                "BOARDD_STATE_DIR": state_dir,
                "BOARDD_PORT": "8780",
                "BOARD_URL": "http://127.0.0.1:8780/",
                "EXPECT_MONDAY": "1",
            }
        )
        boardd = subprocess.Popen(
            [sys.executable, str(PROJECTS / "home-server" / "boardd" / "boardd.py")],
            env=env,
        )
        monday = subprocess.Popen([sys.executable, str(ROOT / "tests" / "fake_monday.py")])
        try:
            wait_for_port(8780, boardd)
            wait_for_port(8765, monday)
            os.environ.update(
                BOARD_URL=env["BOARD_URL"],
                EXPECT_MONDAY=env["EXPECT_MONDAY"],
            )
            import browser_verify

            browser_verify.main()
        finally:
            stop(monday)
            stop(boardd)


if __name__ == "__main__":
    main()
