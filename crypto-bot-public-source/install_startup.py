"""Install this project's scheduled paper dashboard as a macOS login service."""

import os
import json
from pathlib import Path
import plistlib
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
LABEL = "local.ai-crypto-bot.paper-dashboard"


def main():
    target = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
    target.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    config = {
        "Label": LABEL,
        "ProgramArguments": [str(ROOT / ".venv/bin/python"), str(ROOT / "live_dashboard.py")],
        "WorkingDirectory": str(ROOT), "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False}, "ThrottleInterval": 30,
        "StandardOutPath": str(ROOT / "logs/dashboard.log"),
        "StandardErrorPath": str(ROOT / "logs/dashboard-error.log"),
    }
    if target.exists():
        if plistlib.loads(target.read_bytes()) != config:
            raise SystemExit(f"Existing startup config differs; review {target} before changing it.")
    else:
        target.write_bytes(plistlib.dumps(config))
    domain = f"gui/{os.getuid()}"
    existing = subprocess.run(["launchctl", "print", f"{domain}/{LABEL}"], capture_output=True)
    if existing.returncode != 0:
        subprocess.run(["launchctl", "bootstrap", domain, str(target)], check=True)
    print(f"Installed login service: {target}\nDashboard: http://127.0.0.1:8765")
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8765/api/status", timeout=2) as response:
                status = json.load(response)
            print(f"Verified dashboard response: {status['status']}; paper cash ${status['cash']:.2f}; BTC {status['btc']:.8f}")
            return
        except (OSError, ValueError):
            time.sleep(1)
    raise SystemExit("Login service installed, but dashboard did not respond. Check logs/dashboard-error.log.")


if __name__ == "__main__":
    main()
