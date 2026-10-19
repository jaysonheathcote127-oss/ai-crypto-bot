# Regime relative strength — frozen exploratory protocol, 19 October 2026

User authorized continuing Gemini's proposed experiment. One specification, no tuning.
All historical periods have already been inspected. No holdout or promotion claim.

Use the unchanged 17-market OKX USDT universe and saved four-hour data. Include BTC
in ranking. At each completed candle rank close/close.shift(30)-1 descending;
resolve exact ties alphabetically by pair. Top ceil(17/4)=5 qualify to enter when
own close > SMA50 and BTC close > BTC SMA200. Hold until rank > ceil(17/2)=9,
own close < SMA50, or BTC close <= BTC SMA200. Equality to own SMA50 does not
trigger exit but cannot enter. All 17 must have valid current and 30-bar-old
prices, continuous intervening four-hour timestamps and positive current volume;
BTC must have a valid SMA200. Otherwise block entries and signal exits.
No forward filling cross-sectional inputs. SMA200 is ~33 days, not a daily macro
filter; 30 bars is five days. Signals execute next open via Freqtrade.

Retain $1,000 wallet, fixed $100 stake, five maximum holdings, 10% per-position
stop, long-only spot, no leverage/averaging. Existing holdings are not rotated
merely to make room. Simultaneous entries use original whitelist order (a known
execution priority limitation), not rank priority. Re-entry after a stop is
allowed on a subsequent qualifying signal; no added cooldown. Intrabar stop
ordering and exchange constraints follow Freqtrade assumptions.

Reuse exclusive periods Oct 2024–Oct 2025 / Oct 2025–Apr 2026 / Apr–19 Oct 2026;
report as early/middle/recent. July–September 2024 is warmup. Fresh wallets and
force liquidation per segment. Base/stress costs 0.15%/0.45% per side; fee-equivalent
proxy, not simulated fills. Reuse cash and 50%/100% BTC/equal-weight benchmarks.
No optimization, new universe selection, scheduler, credentials or live orders.
Freeze protocol, strategy, config and data hashes before execution. Source hashes
replace a Git tag because this workspace is not a Git repository.

Historical success can only motivate a separately frozen prospective paper study.
Report all segments/costs, trades, marked-wallet drawdown and benchmark comparisons.
Check future-price independence across every pair, deterministic ties, missing
candles and actual entry/exit conditions before executing.

Implementation reference: https://docs.freqtrade.io/en/stable/strategy-customization/
DataProvider supplies full backtest history in populate methods; exact timestamp
alignment and backward-only rolling calculations are required to avoid leakage.
