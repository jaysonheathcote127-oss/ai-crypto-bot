# Momentum robustness and continuous-wallet results

19 October 2026. **No candidate qualifies for promotion.** Every historical period is already inspected. This is a bounded screen of two new hypotheses, not an out-of-sample demonstration.

## What was tested

Daily positive momentum adds a positive 30-bar return entry requirement and a daily exit at nonpositive momentum. The slower version uses 120 bars (20 days) for momentum/ranking instead of 30 bars (five days). Other indicators stay four-hour; entries and rank/own-SMA/momentum decisions are daily. BTC risk-off/missing-data exits remain every four hours. Same 17 pairs, $100 stakes, $1,000 wallet, five holdings, 10% stop, no leverage.

No threshold sweep or new best-coin selection. Both hypotheses were recorded before these runs. The positive-momentum version was not selected as a trading strategy based on its highest historical total.

## Separate period results

Each segment begins with a fresh wallet. Return cells show base / higher-cost stress. Drawdown cells show marked wallet base / stress.

| Candidate | Period | Trades | Net return | Drawdown |
|---|---|---:|---:|---:|
| Daily positive momentum | Early | 309 | +75.56% / +56.76% | 22.74% / 28.94% |
| Daily slower positive momentum | Early | 205 | +63.57% / +51.06% | 26.78% / 29.67% |
| Daily positive momentum | Middle | 61 | -9.39% / -13.03% | 11.74% / 15.13% |
| Daily slower positive momentum | Middle | 47 | -11.27% / -14.06% | 14.44% / 17.08% |
| Daily positive momentum | Recent | 161 | +12.16% / +2.45% | 15.80% / 20.44% |
| Daily slower positive momentum | Recent | 116 | +7.91% / +0.92% | 13.66% / 16.53% |

Both lose in the middle segment at both costs, so neither passes existing positive-validation requirements. Early and recent stressed drawdowns also exceed 15%. The slower horizon reduces trades but does not remove the losing regime.

## One continuous wallet

1 October 2024 through 18 October 2026, without segment liquidations or resets. Fixed-dollar stakes, not constant-weight rebalancing. These actual engine runs are more informative than compounding the separately reset segments.

| Specification | Trades | Base return | Stress return | Base drawdown | Stress drawdown |
|---|---:|---:|---:|---:|---:|
| Four-hour decisions | 950 | +38.94% | -18.26% | 28.17% | 56.79% |
| Daily decisions | 524 | +70.60% | +38.90% | 23.91% | 36.90% |
| Daily positive momentum | 528 | +81.11% | +49.14% | 22.74% | 33.62% |
| Daily slower positive momentum | 366 | +60.87% | +38.70% | 26.78% | 35.23% |

Continuous stressed passive references: 50% BTC / 50% cash returned +14.25%, with 35.46% marked drawdown; 50% equal-weight / 50% cash returned +4.20%, with 49.94% drawdown. Cash returned 0%. Strategy exposure varies and these comparisons are not volatility matched. All use today-selected assets; benchmark comparisons cannot remove that bias.

The daily versions show a positive full-period result even under stress. However, the full-period total combines early gains with later losses; it does not eliminate the failed middle-period screen or establish future income. Four-hour-decision control loses under continuous stress.

## Exposure arithmetic: risk reduction is not signal repair

The protocol specified half-exposure arithmetic. An additional post-hoc quarter-exposure illustration is included explicitly as sensitivity, not an optimized sizing rule or a new candidate. Each scenario uses E_scaled=1000+fraction*(E_original-1000), including final settlement. It is not an execution backtest; exchange minimums, rounding, capacity and execution differences could matter. Smaller allocation cannot change the sign of a losing period.

| Daily specification | Full stress return / drawdown | Half-exposure stress return / drawdown | Quarter-exposure stress return / drawdown |
|---|---:|---:|---:|
| Daily decisions | +38.90% / 36.90% | +19.45% / 24.35% | +9.72% / 14.49% |
| Daily positive momentum | +49.14% / 33.62% | +24.57% / 22.16% | +12.28% / 13.18% |
| Daily slower positive momentum | +38.70% / 35.23% | +19.35% / 23.21% | +9.67% / 13.79% |

Quarter exposure corresponds approximately to $25 rather than $100 entries, with at most $125 initial deployment in five positions. These smaller-allocation returns are not directly comparable to a 50%-invested passive benchmark. Passing a full-window drawdown scenario does not override segment losses or provide forward evidence.

## Verification

21 combined unit checks passed, including integrated full-universe truncated-history versus future-shocked indicators/signals, exact momentum horizons, invalid prices, daily schedules, and read-only observer synchronization/unfinished-candle checks. Eight engine commands produced 20 strategy/cost/period combinations: 12 new segmented results plus eight continuous controls/candidates. Frozen source/data hashes matched after execution; continuous trade profits reconcile to engine totals.

No full single-pair Freqtrade lookahead pass is claimed: its documented equivalence assumption does not hold for cross-sectional ranking. [Official lookahead-analysis limitations](https://www.freqtrade.io/en/stable/lookahead-analysis/). Integrated prefix tests are useful evidence, not a complete proof. No historic order-book fills, intrabar paths or USDT depeg modelling. Costs remain assumed 0.15%/0.45% each side with a fee-equivalent adverse proxy.

## Next evidence: fixed-universe observation

A one-shot read-only observer records all four specifications with current candles/quotes, synchronization, source hashes and immutable raw inputs. Missing one market blocks the full ranking. First attempt correctly blocked because OKX capped candles at 300; v2 uses supported pagination and retains a separate manifest. Baseline bars predating the frozen forward start are labelled baseline_only. This is signal observation, not a paper portfolio or trading deployment; no automatic scheduler is installed. See `FORWARD_OBSERVATION.md` and the separate observation status report.

## Artifacts

Protocol: `MOMENTUM_ROBUSTNESS_EXPERIMENT.md`; strategies: `user_data/strategies/absolute_momentum.py`; evaluator: `evaluate_momentum_robustness.py`. Summary, frozen hashes, original engine ZIPs/logs, equity CSVs, monthly marked returns and exposure scenarios: `data/research/momentum_robustness/`. Diagnostics/report generator: `diagnose_momentum_robustness.py`.
