"""Snapshot today's top 100 and provisional exchange matches; no trading."""
import json
from datetime import datetime, timezone
from pathlib import Path
import ccxt
import requests

ROOT = Path(__file__).resolve().parent


def main():
    response = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={"vs_currency": "usd", "order": "market_cap_desc",
                "per_page": 100, "page": 1, "sparkline": "false"}, timeout=30)
    response.raise_for_status()
    coins = response.json()
    if not isinstance(coins, list) or len(coins) != 100:
        raise ValueError("Expected exactly 100 ranked assets; snapshot not saved")
    coverage = []
    for name in ("kraken", "okx"):
        try:
            exchange = getattr(ccxt, name)({"enableRateLimit": True, "timeout": 30000})
            markets = exchange.load_markets()
            assets = []
            for coin in coins:
                pairs = [symbol for symbol, market in markets.items()
                         if market.get("spot") and market.get("active") is not False
                         and market.get("base", "").lower() == coin["symbol"].lower()
                         and market.get("quote") in ("USD", "USDT", "USDC")]
                assets.append({"id": coin["id"], "symbol": coin["symbol"],
                               "rank": coin["market_cap_rank"], "pairs": pairs})
            coverage.append({"exchange": name, "assets": assets,
                             "matched_by_symbol": sum(bool(a["pairs"]) for a in assets)})
        except Exception as error:
            coverage.append({"exchange": name, "error": str(error)})
    now = datetime.now(timezone.utc)
    report = {"checked_at": now.isoformat(), "top100": coins, "coverage": coverage,
              "limitations": ["Symbol matches require identity validation.",
                              "Stablecoins and wrapped duplicates are not yet filtered.",
                              "Liquidity and regional eligibility are not verified.",
                              "This snapshot is not a historical top100 universe."]}
    folder = ROOT / "data/watchlists"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / (now.strftime("%Y%m%dT%H%M%S") + ".json")
    destination.write_text(json.dumps(report, indent=2))
    print(destination)
    for entry in coverage:
        print(entry["exchange"], entry.get("matched_by_symbol", entry.get("error")))


if __name__ == "__main__":
    main()
