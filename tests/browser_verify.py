from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("BOARD_URL", "http://127.0.0.1:8780/")
FAKE_MONDAY_LOG = Path(os.environ.get("FAKE_MONDAY_LOG", "/tmp/fake-monday-inbox.jsonl"))
EXPECT_MONDAY = os.environ.get("EXPECT_MONDAY") == "1"
SHOT_DIR = Path(__file__).resolve().parent / "shots"
VIEWPORTS = {
    "tv-1080": {"width": 1920, "height": 1080},
    "tv-720": {"width": 1280, "height": 720},
    "tablet": {"width": 1024, "height": 768},
}


def verify_page(browser, name, viewport):
    page = browser.new_page(viewport=viewport)
    console_errors = []

    def record_console(message):
        if message.type != "error":
            return
        text = message.text
        if "WebSocket connection" not in text:
            console_errors.append(text)

    page.on("console", record_console)
    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_function("document.querySelector('#stamp').textContent !== 'connecting'")

    assert page.locator("h1").inner_text() == "samuel hq"
    headings = page.locator(".panel > h2").all_inner_texts()
    assert headings == [
        "SYSTEMS",
        "TODAY",
        "ALERTS",
        "NOW WORKING",
    ], headings
    assert page.locator("#monday").is_visible()
    assert page.locator("#alarm").is_visible()
    # nine since the disk row landed (2026-09-21): both outages that year began
    # with no free space and nothing was watching the number
    names = page.locator("#sys .s .n").all_inner_texts()
    assert page.locator("#sys .s").count() == 9, names
    assert "disk" in names, names

    # the credential strip: the row that exists to make him act before he leaves
    assert page.locator("#conn").is_visible()
    summary = page.locator("#connSum").inner_text()
    assert summary and summary != "checking", summary
    for action in page.locator(".cc .ca").all_inner_texts():
        assert action.strip(), "a connection card with no action text"
    assert console_errors == [], console_errors

    if EXPECT_MONDAY:
        page.wait_for_function("document.querySelector('#veil').classList.contains('show')")
        page.wait_for_function("document.querySelector('#wState').textContent === 'speaking'")
        assert page.locator("#wHeard").inner_text() == "what is on the board"
        assert page.locator("#wReply").inner_text() == "Here is your live system view."

    # the X: it must end the turn, not just hide the card. Samuel, Sept 21:
    # "i dont want to say close out". Checked on the 1080 pass only, because the
    # later passes inherit a ringing alarm whose dialog sits above the card.
    if EXPECT_MONDAY and name == "tv-1080":
        close = page.locator("#wakeClose")
        assert close.is_visible()
        box = close.bounding_box()
        assert box and box["width"] >= 44 and box["height"] >= 44, box
        close.click()
        page.wait_for_function(
            "!document.querySelector('#veil').classList.contains('show')")
        sent = [json.loads(line) for line in
                FAKE_MONDAY_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert any(m.get("type") == "cancel" for m in sent), sent


    bounds = page.evaluate(
        """() => ({
          scrollWidth: document.documentElement.scrollWidth,
          scrollHeight: document.documentElement.scrollHeight,
          width: window.innerWidth,
          height: window.innerHeight,
          body: document.body.getBoundingClientRect().toJSON()
        })"""
    )
    assert bounds["scrollWidth"] <= bounds["width"]
    assert bounds["scrollHeight"] <= bounds["height"]
    assert bounds["body"]["right"] <= bounds["width"] + 1
    assert bounds["body"]["bottom"] <= bounds["height"] + 1

    # every viewport, not just 720: the connections strip starved this panel to
    # zero height at 1080 while the 720 assertion still passed
    today_bounds = page.locator("#today").bounding_box()
    assert today_bounds is not None
    assert today_bounds["height"] >= 120, (name, today_bounds)
    assert page.locator("#today .al").count() >= 1

    if name == "tv-1080":
        console_errors.clear()
        page.evaluate(
            """async () => {
              await fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled:true,time:'07:30',set_by:'browser test'})
              });
              await poll();
            }"""
        )
        page.wait_for_function("document.querySelector('#alarm').classList.contains('on')")
        assert page.locator("#alarmTime").inner_text() == "7:30 am"

        page.evaluate(
            """async () => {
              const now = new Date();
              const time = String(now.getHours()).padStart(2, '0') + ':' +
                String(now.getMinutes()).padStart(2, '0');
              await fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled:true,time:time,set_by:'browser test'})
              });
              await poll();
            }"""
        )
        page.wait_for_function("document.querySelector('#wakeAlarm').classList.contains('show')")
        assert page.locator("#wakeAlarmTitle").inner_text() == "good morning"
        assert "60m" not in page.locator("#alarmMeta").inner_text()
        SHOT_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SHOT_DIR / "alarm-wake.png"), full_page=True)
        page.locator("#wakeSnooze").click()
        page.wait_for_function("!document.querySelector('#wakeAlarm').classList.contains('show')")

        # Shared cancellation must clear a pending local snooze. The old state
        # used to re-ring even though boardd already said the alarm was off.
        page.evaluate(
            """async () => {
              await fetch('/api/alarm', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled:false,time:null,set_by:'browser test'})
              });
              await poll();
              snoozeUntil = Date.now() - 1;
              checkAlarm(new Date());
            }"""
        )
        assert not page.locator("#wakeAlarm").evaluate("node => node.classList.contains('show')")
        assert page.evaluate("snoozeUntil") == 0

        # Re-enable for the remaining interaction and persistence checks.
        page.evaluate(
            """async () => {
              const now = new Date();
              const time = String(now.getHours()).padStart(2, '0') + ':' +
                String(now.getMinutes()).padStart(2, '0');
              await fetch('/api/alarm', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled:true,time:time,set_by:'browser test'})
              });
              await poll();
            }"""
        )
        page.wait_for_function("document.querySelector('#wakeAlarm').classList.contains('show')")

        page.locator("#wakeDismiss").click()
        assert page.locator("#wakeAlarm").evaluate("node => node.classList.contains('show')")
        page.locator("#wakeDismiss").dispatch_event("pointerdown")
        page.wait_for_function("!document.querySelector('#wakeAlarm').classList.contains('show')")

        # The current occurrence stays dismissed through a same-minute reload.
        page.reload(wait_until="networkidle")
        page.wait_for_function("document.querySelector('#alarm').classList.contains('on')")
        assert not page.locator("#wakeAlarm").evaluate("node => node.classList.contains('show')")

        # An older asynchronous payload cannot reverse a newer alarm state.
        page.evaluate(
            """() => {
              const base = Date.now() + 10000;
              renderAlarm({enabled:true,time:'08:15',updated_at:new Date(base).toISOString()});
              renderAlarm({enabled:true,time:'06:45',updated_at:new Date(base - 1000).toISOString()});
            }"""
        )
        assert page.locator("#alarmTime").inner_text() == "8:15 am"
        page.evaluate("acceptedAlarmEpoch = 0")

        page.route("**/api/alarm", lambda route: route.abort())
        page.evaluate("poll()")
        page.wait_for_function("document.querySelector('#alarm').classList.contains('unavailable')")
        assert page.locator("#alarmTime").inner_text() == "alarm status unavailable"
        page.unroute("**/api/alarm")

        page.route("**/api/board", lambda route: route.abort())
        page.evaluate("poll()")
        page.wait_for_function(
            "document.querySelector('#stamp').textContent.includes('refresh failed')"
        )
        assert "showing last update" in page.locator("#stamp").inner_text()
        page.unroute("**/api/board")

        console_errors.clear()
        page.evaluate("poll()")
        page.wait_for_function(
            "!document.querySelector('#stamp').textContent.includes('refresh failed')"
        )
        page.wait_for_function("document.querySelector('#alarm').classList.contains('on')")

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOT_DIR / f"{name}.png"), full_page=True)
    unexpected = [text for text in console_errors if "net::ERR_FAILED" not in text]
    assert unexpected == [], unexpected
    page.close()


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        try:
            for name, viewport in VIEWPORTS.items():
                verify_page(browser, name, viewport)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
