# Daily decision cadence experiment — 19 October 2026

Post-hoc hypothesis motivated by relative-strength attribution: median holding
20 hours, frequent losing short trades, substantial friction. One new variant,
no parameter search. All historical data remains inspected/exploratory.

Inherit every rule, pair, indicator and execution assumption from
RELATIVE_STRENGTH_EXPERIMENT.md except decision cadence. Entries and own-SMA50 /
rank exits are allowed only on candles opening at 20:00 UTC, which complete at
00:00 UTC; engine executes the following open. BTC risk-off or missing-data exits
remain active every four hours. The fixed 10% stop remains active every bar.
Ranking still uses four-hour bars and 30-bar returns, not daily returns. Same
17 pairs, $1,000 wallet, $100 stakes, max five positions, fixed whitelist priority,
next-open orders. No forced minimum holding period or retrospective trade removal.

Run original three exclusive segments and both 0.15%/0.45% per-side costs; compare
with the original strategy and unchanged passive benchmarks. Freeze source/data
hashes before results. No promotion based on these results; existing positive
return and <=15% drawdown expectations still apply. No real trading or scheduler.
