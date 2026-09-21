"""Deterministic Monday websocket used by the browser contract test.

It plays one scripted turn, then records whatever the face sends back, so the
test can prove the X button really cancels the turn instead of just hiding the
card. Inbound handling mirrors the real daemon: a cancel lands on idle.
"""

import json
import os
from pathlib import Path

from aiohttp import WSMsgType, web

INBOX = Path(os.environ.get("FAKE_MONDAY_LOG", "/tmp/fake-monday-inbox.jsonl"))


async def websocket(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_json({"type": "mic", "ok": True, "muted_until": None})
    await ws.send_json({"type": "state", "value": "listening"})
    await ws.send_json({"type": "transcript", "text": "what is on the board"})
    await ws.send_json({"type": "state", "value": "thinking"})
    await ws.send_json({"type": "reply", "text": "Here is your live system view."})

    async for message in ws:
        if message.type == WSMsgType.ERROR:
            break
        if message.type != WSMsgType.TEXT:
            continue
        try:
            data = json.loads(message.data)
        except ValueError:
            continue
        with INBOX.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(data) + "\n")
        if data.get("type") == "cancel":
            await ws.send_json({"type": "state", "value": "idle"})
        elif data.get("type") == "mute":
            minutes = data.get("minutes") or 0
            await ws.send_json({"type": "mic", "ok": not minutes,
                                "muted_until": "2026-09-21T09:00:00" if minutes else None})
    return ws


app = web.Application()
app.router.add_get("/ws", websocket)


if __name__ == "__main__":
    INBOX.write_text("", encoding="utf-8")
    web.run_app(app, host="127.0.0.1", port=8765, print=None)
