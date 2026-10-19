"""Fetch bounded, public historical OKX data; reject incomplete histories."""
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import ccxt.async_support as ccxt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "user_data/data/okx"
START = pd.Timestamp("2024-07-01", tz="UTC")
END = pd.Timestamp("2026-10-19", tz="UTC")
STEP = 4 * 60 * 60 * 1000


def validate(frame):
    expected = pd.date_range(START, END, freq="4h", inclusive="left")
    if not pd.DatetimeIndex(frame.date).as_unit("ms").equals(expected.as_unit("ms")):
        raise ValueError(f"Incomplete history: {len(frame)}/{len(expected)} bars; gaps or late listing")
    values = frame[["open", "high", "low", "close", "volume"]]
    if not np.isfinite(values.to_numpy()).all() or (values.volume < 0).any():
        raise ValueError("Nonfinite prices or invalid volume")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Nonpositive prices")
    if ((frame.high < frame[["open", "close", "low"]].max(axis=1))
            | (frame.low > frame[["open", "close", "high"]].min(axis=1))).any():
        raise ValueError("Invalid OHLC price ordering")


async def main():
    DATA.mkdir(parents=True, exist_ok=True)
    universe = json.loads((ROOT / "data/research/okx_validated_assets.json").read_text())
    selected = sorted([a for a in universe if a["eligible"]],
                      key=lambda a: a["rank"])[:20]
    if not selected:
        raise ValueError("No validated OKX assets")
    ex = ccxt.okx({"enableRateLimit": True, "timeout": 30000})
    await ex.load_markets()
    semaphore = asyncio.Semaphore(3)

    async def download(asset):
        pair = asset["selected"]["pair"]
        record = {"id": asset["id"], "rank": asset["rank"], "pair": pair}
        file = DATA / (pair.replace("/", "_") + "-4h.feather")
        async with semaphore:
            try:
                if file.exists():
                    frame = pd.read_feather(file)
                    validate(frame)
                else:
                    cursor, rows = int(START.timestamp() * 1000), []
                    end = int(END.timestamp() * 1000)
                    while cursor < end:
                        for retry in range(3):
                            try:
                                batch = await ex.fetch_ohlcv(pair, "4h", since=cursor, limit=300,
                                                            params={"type": "HistoryCandles"})
                                break
                            except ccxt.NetworkError:
                                if retry == 2:
                                    raise
                                await asyncio.sleep(2 * (retry + 1))
                        if not batch:
                            raise ValueError("No history at required start; not backfilled")
                        rows.extend(batch)
                        next_cursor = max(r[0] for r in batch) + STEP
                        if next_cursor <= cursor:
                            raise ValueError("Pagination did not advance")
                        cursor = next_cursor
                    frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
                    frame = frame.drop_duplicates("date").sort_values("date").reset_index(drop=True)
                    frame["date"] = pd.to_datetime(frame.date, unit="ms", utc=True)
                    frame = frame[(frame.date >= START) & (frame.date < END)].reset_index(drop=True)
                    validate(frame)
                    frame.to_feather(file)
                record.update(status="accepted", bars=len(frame), sha256=hashlib.sha256(file.read_bytes()).hexdigest())
            except Exception as error:
                record.update(status="excluded", reason=str(error))
            print(pair, record["status"], record.get("reason", record.get("bars")), flush=True)
            return record

    try:
        records = await asyncio.gather(*(download(asset) for asset in selected))
    finally:
        await ex.close()
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "start": START.isoformat(), "end_exclusive": END.isoformat(),
              "selection": "First 20 current eligible assets by market cap, without backfilling exclusions",
              "assets": records}
    (ROOT / "data/research/history_manifest.json").write_text(json.dumps(report, indent=2))
    accepted = [r["pair"] for r in records if r["status"] == "accepted"]
    if len(accepted) < 5:
        raise ValueError("Fewer than five valid assets; research cannot proceed")
    config = json.loads((ROOT / "config.paper.json").read_text())
    config.update(bot_name="top100-research", timeframe="4h", stake_currency="USDT",
                  fee=0.0015, dry_run=True)
    config["exchange"].update(name="okx", pair_whitelist=accepted)
    config["entry_pricing"]["price_side"] = "other"
    config["exit_pricing"]["price_side"] = "other"
    (ROOT / "config.research.json").write_text(json.dumps(config, indent=2) + "\n")
    print("Accepted", len(accepted), "of", len(records), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
