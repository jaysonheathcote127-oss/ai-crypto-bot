"""Offline candle replay. Contains no exchange connection or order API."""

import argparse
import json
import math
from pathlib import Path
from uuid import uuid4

import pandas as pd

from strategy import generate_signals

ROOT = Path(__file__).resolve().parent
TRADE_COLUMNS = ["signal_timestamp", "fill_timestamp", "side", "price_usd",
                 "btc_amount", "fee_usd", "cash_usd", "btc_balance"]


def simulate(candles, initial_cash=1000.0, fee_rate=0.001, slippage_rate=0.0005,
             short_window=5, long_window=20):
    """Replay long-only, all-in/all-out trades at the next consecutive bar open."""
    if not math.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError("Starting cash must be positive and finite")
    if any(not math.isfinite(x) or not 0 <= x < 1 for x in (fee_rate, slippage_rate)):
        raise ValueError("Fee and slippage rates must be finite and between 0 and 1")
    frame = candles.copy()
    if not {"timestamp", "open", "close"}.issubset(frame.columns):
        raise ValueError("Input needs timestamp, open and close columns")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    if frame.timestamp.isna().any() or len(frame) < long_window + 1:
        raise ValueError("Need valid timestamps and at least long_window + 1 candles")
    if not frame.timestamp.diff().iloc[1:].eq(pd.Timedelta(minutes=5)).all():
        raise ValueError("Candles must be ordered, unique and exactly five minutes apart")
    frame["open"] = pd.to_numeric(frame["open"], errors="raise")
    if not ((frame.open > 0) & (frame.open < float("inf"))).all():
        raise ValueError("Opening prices must be positive and finite")
    frame = generate_signals(frame, short_window, long_window).reset_index(drop=True)
    cash, btc, total_fees = initial_cash, 0.0, 0.0
    trades, equity = [], []
    for i, row in frame.iterrows():
        signal = frame.iloc[i - 1]["signal"] if i else "hold"
        if (signal == "buy" and btc == 0) or (signal == "sell" and btc > 0):
            price = float(row["open"]) * (1 + slippage_rate if signal == "buy" else 1 - slippage_rate)
            if signal == "buy":
                notional = cash / (1 + fee_rate)
                fee = notional * fee_rate
                amount = notional / price
                btc, cash = amount, 0.0
            else:
                amount = btc
                notional = amount * price
                fee = notional * fee_rate
                cash, btc = cash + notional - fee, 0.0
            total_fees += fee
            trades.append([frame.iloc[i - 1]["timestamp"], row["timestamp"], signal,
                           price, amount, fee, cash, btc])
        equity.append({"timestamp": row["timestamp"], "cash_usd": cash,
                       "btc_balance": btc, "equity_usd": cash + btc * float(row["close"])})
    final_value = equity[-1]["equity_usd"]
    summary = {"mode": "offline_replay", "exchange": "coinbase", "symbol": "BTC/USD",
               "initial_cash_usd": initial_cash, "final_cash_usd": cash,
               "final_btc": btc, "final_equity_usd": final_value,
               "pnl_usd": final_value - initial_cash,
               "return_percent": (final_value / initial_cash - 1) * 100,
               "fees_usd": total_fees, "trade_count": len(trades),
               "fee_rate": fee_rate, "slippage_rate": slippage_rate,
               "short_window": short_window, "long_window": long_window,
               "start": str(frame.timestamp.iloc[0]), "end": str(frame.timestamp.iloc[-1])}
    return pd.DataFrame(trades, columns=TRADE_COLUMNS), pd.DataFrame(equity), summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/latest_signals.csv")
    parser.add_argument("--cash", type=float, default=1000)
    parser.add_argument("--fee-rate", type=float, default=0.001)
    parser.add_argument("--slippage-rate", type=float, default=0.0005)
    args = parser.parse_args()
    try:
        candles = pd.read_csv(args.input)
        trades, equity, summary = simulate(candles, args.cash, args.fee_rate, args.slippage_rate)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Cannot run simulation: {exc}\nRun run_signals.py to save fresh candles first.\n")
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%S") + "_" + uuid4().hex[:8]
    output = ROOT / "data/paper_runs" / run_id
    output.mkdir(parents=True, exist_ok=False)
    candles.to_csv(output / "input.csv", index=False)
    trades.to_csv(output / "trading_journal.csv", index=False)
    equity.to_csv(output / "equity.csv", index=False)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Offline paper replay — Coinbase BTC/USD; no real orders")
    print(f"Starting cash: ${args.cash:,.2f} USD")
    print(f"Final cash: ${summary['final_cash_usd']:,.2f}; BTC: {summary['final_btc']:.8f}")
    print(f"Portfolio value: ${summary['final_equity_usd']:,.2f} USD")
    print(f"Profit/loss: ${summary['pnl_usd']:,.2f}; fees: ${summary['fees_usd']:,.2f}")
    print(f"Simulated trades: {len(trades)}\nSaved report: {output}")
    print("Each run starts fresh. Open BTC is valued at the last close, without a closing fee.")


if __name__ == "__main__":
    main()
