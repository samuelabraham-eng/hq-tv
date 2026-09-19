"""Deterministic Monday websocket used by the browser contract test."""

from aiohttp import WSMsgType, web


async def websocket(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_json({"type": "state", "value": "listening"})
    await ws.send_json({"type": "transcript", "text": "what is on the board"})
    await ws.send_json({"type": "state", "value": "thinking"})
    await ws.send_json({"type": "reply", "text": "Here is your live system view."})

    async for message in ws:
        if message.type == WSMsgType.ERROR:
            break
    return ws


app = web.Application()
app.router.add_get("/ws", websocket)


if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8765, print=None)
