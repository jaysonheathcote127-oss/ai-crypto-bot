"""Validate current top-100 identities against CoinGecko exchange tickers."""
import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
import ccxt
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data/research"
BASE = "https://api.coingecko.com/api/v3/"


def fetch(path, **params):
    cache_key = hashlib.sha256(json.dumps([path, params], sort_keys=True).encode()).hexdigest()
    cache = OUT / ("api_" + cache_key + ".json")
    if cache.exists() and time.time() - cache.stat().st_mtime < 86400:
        return json.loads(cache.read_text())
    for attempt in range(6):
        try:
            response = requests.get(BASE + path, params=params, timeout=40)
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(10)
            continue
        if response.status_code == 429 and attempt < 5:
            print('CoinGecko rate limit; waiting 60 seconds', flush=True)
            time.sleep(60)
            continue
        response.raise_for_status()
        cache.write_text(json.dumps(response.json()))
        time.sleep(10)
        return response.json()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    snapshots = sorted((ROOT / "data/watchlists").glob("*.json"))
    snapshot = json.loads(snapshots[-1].read_text())
    coins = snapshot["top100"]
    ids = {c["id"] for c in coins}
    excluded = {}
    categories = ["stablecoins", "wrapped-tokens", "liquid-staking-tokens", "liquid-restaking-tokens"]
    for category in categories:
        cached = OUT / (category + ".json")
        rows = json.loads(cached.read_text()) if cached.exists() else fetch(
            "coins/markets", vs_currency="usd", category=category,
            order="market_cap_desc", per_page=250, page=1)
        cached.write_text(json.dumps(rows, indent=2))
        for row in rows:
            if row["id"] in ids:
                excluded.setdefault(row["id"], []).append(category)
        print("Category", category, "loaded", flush=True)
    results = {}
    for name, gecko in [("okx", "okex"), ("kraken", "kraken")]:
        exchange = getattr(ccxt, name)({"enableRateLimit": True, "timeout": 30000})
        markets = exchange.load_markets()
        tickers = []
        for page in range(1, 51):
            rows = fetch(f"exchanges/{gecko}/tickers", coin_ids=",".join(sorted(ids)),
                         order="base_target", page=page).get("tickers", [])
            tickers.extend(rows)
            print(name, "identity page", page, len(rows), flush=True)
            if len(rows) < 100:
                break
        else:
            raise ValueError(f"{name}: pagination limit reached; incomplete listings")
        (OUT / f"{name}_identity_tickers.json").write_text(json.dumps(tickers, indent=2))
        assets = []
        for coin in coins:
            candidates = []
            for ticker in tickers:
                if ticker.get("coin_id") != coin["id"] or ticker["target"] not in ("USD", "USDT", "USDC"):
                    continue
                symbol = f"{ticker['base']}/{ticker['target']}"
                market = markets.get(symbol)
                if not market or not market.get("spot") or market.get("active") is False:
                    continue
                volume = float(ticker.get("converted_volume", {}).get("usd") or 0)
                spread = ticker.get("bid_ask_spread_percentage")
                fresh = not ticker.get("is_stale", True) and not ticker.get("is_anomaly", True)
                candidates.append({"pair": symbol, "volume_usd_24h": volume,
                                   "spread_pct": spread, "fresh": fresh,
                                   "eligible": fresh and volume >= 1_000_000 and spread is not None and 0 <= spread <= 0.2})
            reasons = excluded.get(coin["id"], []).copy()
            eligible = [p for p in candidates if p["eligible"]]
            if not candidates:
                reasons.append("no_identity_verified_USD_USDT_USDC_spot_pair")
            elif not eligible:
                reasons.append("fails_current_liquidity_spread_or_freshness_filter")
            # Keep a single quote currency within each research portfolio.
            required_quote = "USD" if name == "kraken" else "USDT"
            compatible = [p for p in eligible if p["pair"].endswith('/' + required_quote)]
            if eligible and not compatible:
                reasons.append("no_eligible_" + required_quote + "_pair")
            chosen = max(compatible, key=lambda x: x["volume_usd_24h"]) if compatible and not reasons else None
            assets.append({"id": coin["id"], "name": coin["name"], "rank": coin["market_cap_rank"],
                           "eligible": chosen is not None, "selected": chosen,
                           "reasons": reasons, "verified_pairs": candidates})
        results[name] = assets
        # Save intermediate exchange results so completed work survives API outages.
        (OUT / f"{name}_validated_assets.json").write_text(json.dumps(assets, indent=2))
        print(name, "eligible", sum(a["eligible"] for a in assets), flush=True)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "ranking_snapshot": str(snapshots[-1].relative_to(ROOT)),
              "filters": {"min_pair_volume_usd_24h": 1_000_000, "max_spread_pct": 0.2,
                          "excluded_categories": categories},
              "limitations": ["Current rankings and liquidity introduce historical selection bias.",
                              "CoinGecko and exchange listings may lag; identity validated across these sources only.",
                              "Regional account access and trading fees are not verified."],
              "exchanges": results}
    (OUT / "validated_universe.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
