# Fixed research protocol — 19 October 2026

Written before examining the extended-history strategy results. No parameter
search, machine learning or third-party strategy download is part of this pass.
Use Freqtrade's engine, CCXT data access and TA-Lib indicators. The three simple
strategy rules are transparent research baselines, not claimed trading edges.

## Universe and data

Start with today's CoinGecko top 100. Cross-check asset IDs using CoinGecko
exchange tickers and active CCXT spot markets. Exclude stablecoins, wrapped
assets and liquid staking/restaking representations. Require a fresh, non-anomalous
pair quote, $1m reported 24-hour pair volume and spread no wider than 0.2%.
Kraken uses USD; OKX uses USDT. Quote currencies must not be mixed in a portfolio.
Regional account access is not established; public-data availability is not proof.

Use OKX's public historical candles for this research pass because Kraken's
recent OHLCV endpoint is limited. Data source is not a decision about a future
funded account. Select up to 20 eligible assets in market-cap order before
strategy results. Require complete continuous 4-hour history from 1 July 2024
through the last completed day, including at least 300 warmup bars before the
first scored period. Fail assets with gaps, invalid prices or short histories;
report all exclusions. Freeze the resulting list across all strategies/periods.

Today's membership and liquidity selection produce historical selection bias.
The holdout is time-separated, but cannot remove that universe bias. Findings
remain exploratory. Save daily universe snapshots for prospective testing.

## Rules fixed before results

1. Trend: SMA20 crosses above SMA50 while close > SMA200; exit on reverse cross
   or close < SMA200.
2. Momentum breakout: close crosses above the previous 20-bar high while above
   SMA200; exit below the previous 10-bar low or below SMA200.
3. Mean reversion: close < lower 20-bar, 2-standard-deviation Bollinger band and
   RSI14 < 30; exit at the middle band or RSI14 > 55.

All long-only spot, one position per asset, $1,000 starting simulated wallet,
$100 per entry, at most 5 concurrent holdings, 10% fixed stoploss, no leverage,
no averaging down, no ROI override, no hyperoptimization. 24/7 four-hour candles.
Signals execute no earlier than the next candle open in Freqtrade. An additional
fixed adverse 0.05% per-side cost is represented as a fee-equivalent deduction
(not an actual slippage/fill model).

## Periods and costs

- Development: 1 October 2024 to 1 October 2025 UTC.
- Validation: 1 October 2025 to 1 April 2026 UTC.
- Final held-out period: 1 April 2026 to 19 October 2026 UTC.
- Each period starts with a fresh wallet and no open positions. Force exits at
  segment end are disclosed. Warmup prices are available only for indicators.
- Base assumed fee 0.10% + cost proxy 0.05% = 0.15% per side.
- Stress assumed fee 0.40% + cost proxy 0.05% = 0.45% per side.
  These are assumptions, not verified fee tiers. USDT is treated as $1; depeg
  risk is not modelled.

Select at most one candidate using validation net return, only if validation
return is positive after base costs, drawdown <=15%, >=30 closed trades, and
stress return remains positive. Lock that choice before revealing holdout.
Require positive holdout net return and <=15% drawdown at both cost levels
before considering a forward paper pilot. A candidate must also pass causality,
lookahead and startup/recursive checks. No passing candidate means no promotion.
Compare cash, BTC holding and equal-weight holding of the same universe using
full and 50% invested exposure. These benchmarks help interpret opportunity cost;
the different exposure and selection bias must accompany any comparison.

No changes to the running BTC service or any exchange credentials are authorized
by this protocol. A research failure is a valid result; do not tune using holdout.

Implementation correction after the first execution: Freqtrade includes the
stop candle, so pass the last four-hour candle before each exclusive period end.
Initial artifacts remain in `evaluation/`; corrected runs are in
`evaluation_exclusive_boundaries/`. No strategy or selection threshold changed.
The original selection was none. Since holdout was already displayed, the rerun
is a technical correction, not a newly untouched holdout experiment.
