# Earlier-history extension — 19 October 2026

No strategy rules or coin selections changed. All three daily specifications were tested with $25 simulated entries, a $1,000 wallet, five maximum holdings, unchanged 10% stop, four-hour signals and hourly execution. Costs remain 0.15%/0.45% per side, including a fee-equivalent adverse-cost proxy. No promotion or real orders.

## Earlier year: October 2023–September 2024

July–September 2023 was indicator warmup. This year predates the strongest previously inspected rally. It was newly added to our calculations, but the decision to extend follows later-result inspection and uses today-selected survivors. It is an earlier-history robustness check, not an untouched holdout or forward test.

| Specification | Trades | Base return | Stress return | Hourly-close base drawdown | Hourly-close stress drawdown |
|---|---:|---:|---:|---:|---:|
| Daily control | 253 | +8.89% | +5.06% | 5.02% | 6.36% |
| Daily positive momentum | 255 | +8.87% | +5.01% | 4.83% | 6.16% |
| Daily slower positive momentum | 195 | +10.52% | +7.56% | 6.34% | 7.43% |

## Extended continuous wallet: October 2023–18 October 2026

One wallet throughout, without year/segment resets. Returns are cumulative over approximately three years, not annual returns. The earlier and extended tests share data and are not independent samples.

| Specification | Trades | Base return | Stress return | Hourly-close base drawdown | Hourly-close stress drawdown |
|---|---:|---:|---:|---:|---:|
| Daily control | 779 | +25.87% | +14.09% | 8.92% | 14.04% |
| Daily positive momentum | 785 | +28.48% | +16.60% | 8.46% | 12.77% |
| Daily slower positive momentum | 560 | +27.92% | +19.42% | 9.74% | 12.95% |

## Passive references at comparable initial allocation

Buy-and-hold starts 12.5% invested and 87.5% cash, matching five initial $25 strategy stakes in a $1,000 wallet. Strategy exposure varies and these are not volatility-matched. Fractional passive positions ignore individual minimum order sizes. These references include assumed entry/exit costs. Cash return is 0%. Cells show higher-cost return / hourly-close drawdown.

| Period | BTC holding | Equal-weight holding |
|---|---:|---:|
| Earlier year | +16.60% / 9.03% | +15.90% / 16.62% |
| Extended continuous | +25.23% / 21.46% | +14.64% / 29.63% |

## Earlier-year attribution under higher costs

| Specification | Net P&L | Gross price P&L | Cost deductions | Positive coins | Five largest winners |
|---|---:|---:|---:|---:|---:|
| Daily control | $+50.64 | $+108.05 | $57.41 | 9/17 | $+81.89 |
| Daily positive momentum | $+50.14 | $+108.00 | $57.86 | 9/17 | $+81.50 |
| Daily slower positive momentum | $+75.57 | $+119.99 | $44.41 | 8/17 | $+109.01 |

Largest-winner sums describe concentration, not a simulation without those trades. Exit-month attribution is separate from marked monthly returns; winners can span multiple months. Coins and trades share market conditions and are not independent observations.

## Verification and limits

All 17 pairs had complete earlier history: 2,748 four-hour bars and 10,992 hourly bars each. No gaps, market exclusions or date changes. Reconstructed earlier hourly OHLC matches four-hour source within rtol=1e-5. The 552-bar overlap per pair agrees with original four-hour history, including volume within that tolerance. Original datasets/configs were preserved; merged data is isolated under this experiment.

27 combined unit checks passed, including three extension checks for coverage/aggregation, rejecting revised overlaps without mutating input, and charging both sides of passive benchmark fees. Four engine commands produced 12 strategy/cost/period results. Frozen hashes rechecked; trade profits/fees and independent hourly-close final balances reconcile. Earlier force exits and samples are retained in summary JSON.

Hourly-close equity uses recorded execution-hour events and closing marks, recognizing entry/exit fees. It omits within-hour extremes and actual order-book fills. Engine exported wallet marks use four-hour opening prices; those measures are stored separately. No claim of a routine single-pair Freqtrade lookahead pass for a cross-sectional strategy.

## Interpretation

All three earlier-year stressed results were positive, so profitability is not confined to the previously inspected late-2024 rally. However, BTC holding at the same 12.5% initial allocation returned +16.60% in the earlier year, more than the strategies’ +5.01% to +7.56%, with 9.03% drawdown versus their 6.16% to 7.43%. The tradeoff includes lower exposure over time and different risk, not clear benchmark dominance.

Across the extended continuous window, BTC returned +25.23% with 21.46% drawdown; the strategies returned +14.09% to +19.42% with 12.77% to 14.04% drawdown. The active rules reduced historical drawdown but also gave up some BTC return. These are not volatility-matched comparisons.

Earlier-year profits remain concentrated: the five largest winners exceed total net P&L for all three versions, and only eight or nine of 17 coins were profitable under stress. That is descriptive evidence about a tail-dependent momentum payoff, not a reason to select those past winners.

## Decision

This extension adds evidence about another historical period; it does not erase the losing October 2025–March 2026 segment, remove current-universe survivorship bias, validate income reliability, or authorize promotion. All three specifications remain exploratory references. Keep rules/results frozen; do not select a coin/horizon retrospectively or change rejection thresholds to fit these totals. Genuinely subsequent observations remain necessary.

Artifacts: `HISTORY_EXTENSION_EXPERIMENT.md`, `extend_history.py`, `evaluate_history_extension.py`, `report_history_extension.py`, and `data/research/history_extension/` (separate raw/merged data, manifests/hashes, engine archives/logs, independent equity CSVs, benchmarks and attribution). No automatic collection/trading service was installed.
