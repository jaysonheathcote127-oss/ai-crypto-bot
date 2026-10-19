"""Read-only multi-coin research snapshots. Contains no portfolio or order code."""
import argparse
import asyncio
import csv
import json
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import ccxt.async_support as ccxt
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "user_data/strategies"))
from research_baselines import TrendBaseline, MomentumBaseline, ReversionBaseline

STRATEGIES = (TrendBaseline, MomentumBaseline, ReversionBaseline)


def analyse(rows, now):
    frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    frame["date"] = pd.to_datetime(frame.date, unit="ms", utc=True)
    frame = frame[frame.date + pd.Timedelta(hours=4) <= now].reset_index(drop=True)
    if len(frame) < 300:
        raise ValueError("Need at least 300 completed four-hour candles")
    if frame.date.isna().any() or not frame.date.diff().iloc[1:].eq(pd.Timedelta(hours=4)).all():
        raise ValueError("Missing, duplicate or unordered four-hour candles")
    if not pd.Timedelta(0) <= now - (frame.date.iloc[-1] + pd.Timedelta(hours=4)) <= pd.Timedelta(hours=4, minutes=5):
        raise ValueError("Latest completed candle is stale")
    numeric = frame[["open", "high", "low", "close", "volume"]]
    if not numeric.map(math.isfinite).all().all() or (frame.volume < 0).any():
        raise ValueError("Invalid numeric market data")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Nonpositive prices")
    if ((frame.high < frame[["open", "close", "low"]].max(axis=1))
            | (frame.low > frame[["open", "close", "high"]].min(axis=1))).any():
        raise ValueError("Invalid OHLC ordering")
    signals = {}
    for cls in STRATEGIES:
        strategy = cls({})
        values = strategy.populate_indicators(frame.copy(), {})
        values = strategy.populate_entry_trend(values, {})
        values = strategy.populate_exit_trend(values, {})
        last = values.iloc[-1]
        # Raw signals are independent research observations, never order instructions.
        signals[cls.__name__] = {"entry": bool(last.enter_long == 1), "exit": bool(last.exit_long == 1)}
    return {"completed_candle": frame.date.iloc[-1].isoformat(), "last_close": float(frame.close.iloc[-1]),
            "signals": signals}


def validate_quote(ticker, now):
    price, bid, ask = [float(ticker[key]) for key in ("last", "bid", "ask")]
    if not all(math.isfinite(v) and v > 0 for v in (price, bid, ask)) or ask < bid:
        raise ValueError("Invalid quote prices")
    quote_time = pd.Timestamp(float(ticker["timestamp"]), unit="ms", tz="UTC")
    if not pd.Timedelta(seconds=-10) <= now - quote_time <= pd.Timedelta(minutes=2):
        raise ValueError("Stale or future quote")
    spread = (ask - bid) / ((ask + bid) / 2) * 100
    volume = float(ticker["quoteVolume"])
    if not math.isfinite(volume) or volume < 1_000_000 or spread > .2:
        raise ValueError("Current quote fails liquidity/spread filter")
    return {"price": price, "quote_at": quote_time.isoformat(), "spread_pct": spread,
            "quote_volume_24h_usdt": volume}


def save(report, destination):
    destination.mkdir(parents=True, exist_ok=True)
    # Keep historical snapshots immutable and separate replay from fresh observations.
    name = report["observed_at"].replace(":", "").replace("+", "_")
    path = destination / (name + ".json")
    suffix = 1
    while path.exists():
        path = destination / (name + f"_{suffix}.json")
        suffix += 1
    with path.open("x") as file:
        json.dump(report, file, indent=2)
    latest = destination / "latest.json"
    temporary = destination / (f"latest.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(report, indent=2))
    temporary.replace(latest)
    with sqlite3.connect(destination / "observations.sqlite3") as db:
        db.execute("CREATE TABLE IF NOT EXISTS snapshots (path TEXT PRIMARY KEY, observed_at TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL)")
        db.execute("INSERT INTO snapshots VALUES (?,?,?,?)", (str(path.name), report["observed_at"], report["mode"], json.dumps(report)))
    with (destination / "latest.csv").open("w", newline="") as file:
        fields = ["rank", "coin_id", "pair", "status", "completed_candle", "last_close", "reason"]
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["assets"])
    return path


async def collect(replay):
    source = ROOT / "data/research/validated_universe.json"
    universe = json.loads(source.read_text())
    now = pd.Timestamp.now(tz="UTC") if not replay else pd.Timestamp("2026-10-19T00:00:00Z")
    if not replay:
        age = now - pd.Timestamp(universe["checked_at"])
        if not pd.Timedelta(0) <= age <= pd.Timedelta(days=1):
            raise ValueError("Refresh and validate the universe before live observation; it is over 24 hours old")
    exchange = None
    if not replay:
        exchange = ccxt.okx({"enableRateLimit": True, "timeout": 20000})
        await exchange.load_markets()
    semaphore = asyncio.Semaphore(3)

    async def observe(asset):
        record = {"rank": asset["rank"], "coin_id": asset["id"], "pair": ""}
        if not asset["eligible"]:
            return {**record, "status": "excluded", "reason": "; ".join(asset["reasons"])}
        pair = asset["selected"]["pair"]
        record["pair"] = pair
        async with semaphore:
            try:
                if replay:
                    path = ROOT / "user_data/data/okx" / (pair.replace("/", "_") + "-4h.feather")
                    if not path.exists():
                        return {**record, "status": "unavailable_in_replay", "reason": "No saved history; no live request attempted"}
                    frame = pd.read_feather(path).tail(300)
                    rows = [[int(row.date.timestamp() * 1000), row.open, row.high, row.low, row.close, row.volume]
                            for row in frame.itertuples()]
                    quote = {"price": None, "quote_at": None}
                else:
                    rows = await exchange.fetch_ohlcv(pair, "4h", limit=301)
                    ticker = await exchange.fetch_ticker(pair)
                    quote = validate_quote(ticker, pd.Timestamp.now(tz="UTC"))
                return {**record, "status": "observed", **analyse(rows, now), **quote}
            except Exception as error:
                return {**record, "status": "data_error", "reason": str(error)}

    try:
        assets = await asyncio.gather(*(observe(asset) for asset in universe["exchanges"]["okx"]))
    finally:
        if exchange is not None:
            await exchange.close()
    return {"mode": "saved_data_replay" if replay else "fresh_public_data", "observed_at": now.isoformat(),
            "collected_at": datetime.now(timezone.utc).isoformat(), "exchange": "okx",
            "universe_checked_at": universe["checked_at"], "assets": assets,
            "notice": "Raw research signals only. Strategies failed validation. No orders or paper fills are generated."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-saved", action="store_true", help="Offline saved-data check, explicitly separate from fresh observations")
    args = parser.parse_args()
    report = asyncio.run(collect(args.replay_saved))
    folder = ROOT / "data/observations" / ("replay" if args.replay_saved else "fresh")
    destination = save(report, folder)
    print(destination)
    counts = {}
    for asset in report["assets"]:
        counts[asset["status"]] = counts.get(asset["status"], 0) + 1
    print(json.dumps({"mode": report["mode"], "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
