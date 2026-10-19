"""Fetch public prices once and save a signal report. Never places orders."""

from pathlib import Path

import ccxt
import pandas as pd

from strategy import generate_signals

ROOT = Path(__file__).resolve().parent


def closed_candles(candles, now):
    """Coinbase timestamps mark candle opens; exclude the unfinished 5m bar."""
    return candles.loc[
        candles["timestamp"] + pd.Timedelta(minutes=5) <= now
    ].sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def main():
    exchange = ccxt.coinbase({"enableRateLimit": True})
    rows = exchange.fetch_ohlcv("BTC/USD", timeframe="5m", limit=100)
    candles = pd.DataFrame(
        rows, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    candles["timestamp"] = pd.to_datetime(candles["timestamp"], unit="ms", utc=True)
    candles = closed_candles(candles, pd.Timestamp.now(tz="UTC"))
    if len(candles) < 21:
        raise ValueError("Need at least 21 completed candles to check a crossover")
    report = generate_signals(candles)
    output = ROOT / "data" / "latest_signals.csv"
    output.parent.mkdir(exist_ok=True)
    report.to_csv(output, index=False)
    latest = report.iloc[-1]
    message = f"{latest['timestamp']} BTC/USD close={latest['close']:.2f} signal={latest['signal']}"
    log = ROOT / "logs" / "signals.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("a") as stream:
        stream.write(f"checked_at={pd.Timestamp.now(tz='UTC')} {message}\n")
    print(report.tail(10).to_string(index=False))
    print(f"\n{message}\nSaved {output}\nPaper mode: no orders placed.")


if __name__ == "__main__":
    main()
