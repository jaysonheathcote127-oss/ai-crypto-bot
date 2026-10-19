# Once-daily relative-strength decisions — 19 October 2026

**Outcome: an improvement over four-hour decisions in these inspected historical periods, but no promotion.**

After diagnosing the original results, froze one change: entries and rank/own-SMA exits only at the midnight UTC decision (20:00 four-hour candle close); BTC risk-off/missing-data exits still every four hours, with the existing stop active. The universe, lookbacks, sizing and cost assumptions stayed fixed. This tests decision cadence, not a switch to daily indicators. No parameter search.

| Period | Trades: original → daily | Daily base return | Daily stress return | Daily base drawdown | Daily stress drawdown |
|---|---:|---:|---:|---:|---:|
| Early | 537 → 313 | +66.92% | +47.91% | 23.91% | 30.23% |
| Middle | 127 → 61 | -9.09% | -12.72% | 11.64% | 14.83% |
| Recent | 287 → 153 | +10.00% | +0.78% | 15.00% | 19.24% |

The recent base drawdown is 15.001816%, which rounds to 15.00% but still exceeds the fixed 15% threshold. Early and recent stressed drawdowns also fail. Middle returns remain negative at both costs. Five early positions were force-exited at each cost; none in the other segments. Each segment starts with a fresh $1,000 wallet, so these returns must not be compounded as a continuous funded track record.

## Comparison after higher costs

50% invested / 50% cash passive benchmarks; not volatility matched.

| Period | Original | Daily decisions | BTC holding | Equal-weight holding |
|---|---:|---:|---:|---:|
| Early | +16.18% | +47.91% | +39.24% | +50.53% |
| Middle | -19.21% | -12.72% | -20.33% | -25.74% |
| Recent | -14.93% | +0.78% | +9.59% | +14.58% |

## What changed

Early gross price profit increased from $648.02 to $764.24; stressed friction deductions fell from $486.21 to $285.14. Thus the early improvement includes different trades and prices as well as lower costs; it is not just a fee reduction. Early median holding time increased from 20 to 48 hours. Middle median is 48 hours and recent median 64 hours.

Early top-five winning trades still contributed $653.11 of the $479.10 stressed net profit. Concentration remains: arithmetically subtracting those five leaves -$174.01, which is not a simulated portfolio result. Large winners are potentially useful, but their recurrence and advance identification are unestablished.

## Decision and next evidence

Keep the original and this cadence variant frozen as exploratory references. No service, paper-order pilot or funded deployment is promoted. Do not keep adding thresholds to preserve the early rally: existing post-hoc breadth/rising-BTC cohorts were inconsistent in later data.

The next useful milestone is prospective observation of unchanged signals/universe and obtaining exact structural rules for the separate Discord hypothesis. Fresh network observations and any scheduler are separate operational work; none was installed here. Do not interpret this completed historical experiment as ongoing unattended research.

## Validation and artifacts

16 automated checks passed across the existing research/observer/strategy suites plus daily schedule and immediate risk-off/missing-data exits. All six engine backtests completed. Attribution reconciled trade totals and gross-minus-cost arithmetic. Frozen hashes were rechecked after the runs and matched. No full Freqtrade lookahead/recursive audit was performed for this failed candidate.

Protocol: `DAILY_RELATIVE_STRENGTH_EXPERIMENT.md`. Strategy: `user_data/strategies/daily_relative_strength.py`. Runner: `evaluate_daily_relative_strength.py`. Full summary/hashes/archives: `data/research/daily_relative_strength/`. Trade attribution: `data/research/daily_relative_strength_diagnostics/`. Original-run diagnostic: `outputs/relative-strength-diagnostics.md`.

These are post-hoc tests on inspected, current-universe-biased four-hour data, with assumed fees plus a fee-equivalent adverse cost proxy. No historical depth/intrabar reconstruction or USDT depeg modelling.
