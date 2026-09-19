from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("BOARD_URL", "http://127.0.0.1:8780/")
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
    assert page.locator("#sys .s").count() == 8
    assert console_errors == [], console_errors

    if EXPECT_MONDAY:
        page.wait_for_function("document.querySelector('#veil').classList.contains('show')")
        page.wait_for_function("document.querySelector('#wState').textContent === 'speaking'")
        assert page.locator("#wHeard").inner_text() == "what is on the board"
        assert page.locator("#wReply").inner_text() == "Here is your live system view."

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

    if name == "tv-720":
        today_bounds = page.locator("#today").bounding_box()
        assert today_bounds is not None
        assert today_bounds["height"] >= 120, today_bounds
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

        page.evaluate("fireAlarm()")
        page.wait_for_function("document.querySelector('#wakeAlarm').classList.contains('show')")
        page.locator("#wakeDismiss").click()
        assert page.locator("#wakeAlarm").evaluate("node => node.classList.contains('show')")
        page.locator("#wakeDismiss").dispatch_event("pointerdown")
        page.wait_for_function("!document.querySelector('#wakeAlarm').classList.contains('show')")

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
