# Earlier-history robustness extension — 19 October 2026

User requested continued research. Before viewing the new earlier candles or
results, freeze this extension. No new strategy, ranking horizon, signal cutoff,
position size, stop or market selection. Evaluate all three daily specifications,
not only the historical winner. Same 17 current OKX/USDT markets, $25 entries,
$1,000 initial wallet, five holdings, 10% stop, four-hour signals, one-hour execution
detail and both 0.15%/0.45% per-side assumed costs. No optimization.

Download 1 July 2023–1 October 2024 exclusive at four-hour and hourly resolution.
Score exactly 1 October 2023–1 October 2024 exclusive, using July–September for
warmup. Require complete history for every fixed pair. If any is missing or late
listed, block the full fixed-universe test; don't drop it or change dates to get
a result. Save failures as well. Data in a separate directory; never modify the
original source files or hashes. Same causal rolling calculations/next-open rules.

Validate complete timestamps, OHLC/volume and reconstructed hourly/four-hour
agreement (rtol=1e-5). Compare the Jul–Sep 2024 overlap against original saved
four-hour history. If candles differ, report a source revision and block merging
rather than silently picking one source. Combine exact matching overlap into a
separate datadir with the frozen later data; don't overwrite original datasets.

Run a second continuous wallet from 1 October 2023–19 October 2026 exclusive,
without year/segment resets, to measure path dependence and drawdown across the
extension and existing inspected periods. This is a consistency check, not another
independent sample. Compare cash/BTC/equal-weight at 12.5% initial investment to
match maximum initial five-$25 deployment; not volatility matched. Keep all results,
force exits, samples and failures. Independently reconstruct hourly-close equity
and reconcile final balances. Report earlier/full-period return and drawdown.

This earlier dataset was not previously used in our project calculations, but the
choice to extend history follows inspection of later results, and today's coin
selection still creates survivorship/selection bias. Call it an earlier-history
extension, NOT a newly pristine holdout or a forward test. No promotion, funded
orders or scheduler. Existing failed middle-period evidence remains; do not waive
it if older-history totals are attractive. Freeze source before download and
source/config/data hashes before backtests.
