"""Local dashboard and weekday 08:00–16:00 Europe/London paper bot."""

import argparse
import fcntl
import json
import secrets
import signal
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from live_bot import PaperBot, fetch_market, make_exchange

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    runtime = ROOT / "data/live"
    runtime.mkdir(parents=True, exist_ok=True)
    lock = (runtime / "runner.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.exit(1, "The paper bot is already running. Open http://127.0.0.1:8765\n")
    bot = PaperBot(runtime / "paper.sqlite3")
    token = secrets.token_urlsafe(32)
    origin = f"http://127.0.0.1:{args.port}"
    stop = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code, body, content_type="application/json"):
            payload = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(payload)

        def valid_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{args.port}"

        def do_GET(self):
            if not self.valid_host():
                return self.send(403, '{}')
            if self.path == "/":
                html = (ROOT / "dashboard/index.html").read_text().replace("__TOKEN__", token)
                return self.send(200, html, "text/html; charset=utf-8")
            if self.path == "/api/status":
                return self.send(200, json.dumps(bot.snapshot(datetime.now(timezone.utc))))
            return self.send(404, '{}')

        def do_POST(self):
            if (not self.valid_host() or self.headers.get("Origin") != origin
                    or not secrets.compare_digest(self.headers.get("X-Bot-Token", ""), token)):
                return self.send(403, '{}')
            if self.path == "/api/pause":
                bot.pause(datetime.now(timezone.utc))
            elif self.path == "/api/resume":
                bot.resume(datetime.now(timezone.utc))
            else:
                return self.send(404, '{}')
            return self.send(200, '{"ok":true}')

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)

    def worker():
        exchange = make_exchange()
        awake = None
        try:
            while not stop.is_set():
                active = bot.tick_schedule(datetime.now(timezone.utc))
                if active:
                    if sys.platform == "darwin" and awake is None:
                        # Prevent idle sleep only during work sessions; closing the lid still suspends.
                        awake = subprocess.Popen(["/usr/bin/caffeinate", "-i"])
                    try:
                        rows, ticker = fetch_market(exchange)
                        bot.apply_market(rows, ticker, datetime.now(timezone.utc))
                    except Exception as exc:
                        bot.failure(datetime.now(timezone.utc), exc)
                elif awake is not None:
                    awake.terminate()
                    awake.wait()
                    awake = None
                stop.wait(60 if active else 10)
        finally:
            if awake is not None:
                awake.terminate()
                awake.wait()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    def shutdown(*_):
        stop.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    print(f"Paper dashboard: {origin}\nSchedule: Mon–Fri 08:00–16:00 Europe/London", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        stop.set()
        server.server_close()
        thread.join(timeout=45)
        with bot.lock:
            bot.db.close()


if __name__ == "__main__":
    main()
