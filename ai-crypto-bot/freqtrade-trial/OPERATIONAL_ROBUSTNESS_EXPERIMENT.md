# Execution delay and allocator sensitivity — 19 October 2026

User requested continued research. Freeze exactly two operational stress scenarios
for all three daily specifications; do not tune their signals or select a winner.
Use the isolated complete Jul 2023–Oct 2026 dataset from history_extension.

1. Delay both completed entry and exit signals by exactly one four-hour bar.
   A daily signal normally submitted at next 00:00 open instead executes at 04:00.
   No future prices or later confirmation are used. Both entry and exit tags move
   with their signals. Fixed stoploss remains active throughout, without delay.
   This is a blind processing-lag stress test, NOT a proposed live policy; it can
   act on stale context, including BTC risk-off, until the delayed exit arrives.
2. Reverse the existing 17-pair whitelist order, leaving the ranking's alphabetical
   tie-breaking and every signal calculation unchanged. This tests priority when
   limited slots are available; it is not a performance-driven coin selection.
   Same complete fixed universe; never drop a coin or dynamically sort by P&L.

Control uses unchanged original order and next-open execution. Evaluate two fixed
windows: Oct 2023–19 Oct 2026 exclusive continuous and the already known losing
Oct 2025–Apr 2026 segment. $1,000 wallet reset for each window, fixed $25 entries,
five slots, long-only spot, 10% stop, hourly execution detail. Both existing fee-
equivalent costs 0.15%/0.45% per side. Reuse the identical extended-window control
archive; execute a matching $25 hourly-detail control for the losing segment.
No extra delay lengths, random order seeds, parameter grid or subsequent tuning.

Record every scenario/candidate/window/cost result, trade counts/signature changes,
force exits, and return/drawdown deltas to matching controls. Independently mark
hourly-close equity and reconcile final balances. Preserve original archives,
config/source/data hashes and any failed runs. Scenario differences are correlated
and not independent trials. A better result under delay/order is sensitivity,
not a promoted strategy. Historical periods are all inspected, current-universe
biased and not untouched holdout. No orders, credentials, scheduler or service.
