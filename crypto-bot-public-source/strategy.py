"""Moving-average crossover signals; no order execution."""

import pandas as pd


def generate_signals(candles, short_window=5, long_window=20):
    """Return a copy with averages and signals, using only past/current closes."""
    if not 1 <= short_window < long_window:
        raise ValueError("Windows must satisfy 1 <= short < long")
    if "close" not in candles or candles["close"].isna().any():
        raise ValueError("Candles require non-missing close prices")
    result = candles.copy()
    close = pd.to_numeric(result["close"], errors="raise")
    if not ((close > 0) & (close < float("inf"))).all():
        raise ValueError("Close prices must be finite and positive")
    result["short_ma"] = close.rolling(short_window).mean()
    result["long_ma"] = close.rolling(long_window).mean()
    difference = result["short_ma"] - result["long_ma"]
    previous = difference.shift(1)
    result["signal"] = "hold"
    result.loc[(difference > 0) & (previous <= 0), "signal"] = "buy"
    result.loc[(difference < 0) & (previous >= 0), "signal"] = "sell"
    return result
