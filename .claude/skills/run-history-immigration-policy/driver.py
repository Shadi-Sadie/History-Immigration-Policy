#!/usr/bin/env python3
"""
Driver for History-Immigration-Policy web app.
Usage:
  python3 driver.py screenshot [scroll_px] [output.png]
  python3 driver.py scroll-range [start_px] [end_px] [step_px] [out_dir]

Starts a local HTTP server, launches Chrome headless with CDP,
scrolls to the given position, and captures a screenshot.
"""
import asyncio, json, base64, subprocess, sys, time, os, signal, urllib.request
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent  # repo root
PORT = 8743
SCRATCHPAD = Path(__file__).parent / "screenshots"

async def cdp_session(ws_url):
    import websockets
    return websockets.connect(ws_url)

async def take_screenshot(scroll_px: int, out_path: Path):
    try:
        import websockets
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
        import websockets

    with urllib.request.urlopen("http://localhost:9222/json") as r:
        pages = json.loads(r.read())
    page = next((p for p in pages if p.get("webSocketDebuggerUrl") and "index.html" in p.get("url", "")), None) \
        or next((p for p in pages if p.get("webSocketDebuggerUrl") and p.get("type") == "page"), None) \
        or next((p for p in pages if p.get("webSocketDebuggerUrl")), None)
    if not page:
        raise RuntimeError("No CDP page found")

    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as ws:
        counter = [1]

        async def send(method, params=None):
            msg_id = counter[0]
            counter[0] += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        r = await send("Runtime.evaluate", {"expression": "document.documentElement.scrollHeight"})
        max_scroll = r["result"]["value"]
        actual = min(scroll_px, max_scroll)
        await send("Runtime.evaluate", {"expression": f"window.scrollTo(0, {actual})"})
        await asyncio.sleep(1.0)  # let scroll + D3 settle

        result = await send("Page.captureScreenshot", {"format": "png"})
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(result["data"]))
        print(f"Saved: {out_path}  (scroll={actual}/{max_scroll})")
        return max_scroll


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "screenshot"

    # Start HTTP server
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=str(REPO),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.5)

    # Start Chrome with CDP
    chrome_args = [
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--no-first-run",
        "--remote-debugging-port=9222",
        "--window-size=1400,900",
        f"http://localhost:{PORT}/index.html",
    ]
    chrome = subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3.5)

    try:
        if cmd == "screenshot":
            scroll_px = int(args[1]) if len(args) > 1 else 2500
            out = Path(args[2]) if len(args) > 2 else SCRATCHPAD / f"scroll-{scroll_px}.png"
            asyncio.run(take_screenshot(scroll_px, out))

        elif cmd == "scroll-range":
            start = int(args[1]) if len(args) > 1 else 0
            end   = int(args[2]) if len(args) > 2 else 8000
            step  = int(args[3]) if len(args) > 3 else 1000
            out_dir = Path(args[4]) if len(args) > 4 else SCRATCHPAD
            for px in range(start, end + 1, step):
                asyncio.run(take_screenshot(px, out_dir / f"scroll-{px:05d}.png"))

        else:
            print(__doc__)
    finally:
        chrome.terminate()
        server.terminate()


if __name__ == "__main__":
    main()
