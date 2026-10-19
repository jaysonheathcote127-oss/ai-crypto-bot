# Hourly execution and equity validation

19 October 2026. **All three daily versions retain positive full-period totals under hourly detail, but none passes the original segment-selection criteria.** No candidate promoted.

Tested unchanged rules with a $1,000 simulated wallet, $25 entries, five positions, fixed 10% stop and the same 17 OKX/USDT markets. Period: 1 October 2024–18 October 2026. These are roughly two-year total returns, not annual returns or income forecasts. All data was already inspected at four-hour resolution.

## Hourly-detail engine results

Signals stay four-hour and scheduled daily as specified. Stops/engine execution use one-hour detail. Base/stress cost assumptions remain 0.15%/0.45% each side.

| Specification | Trades | Base return | Stress return | Hourly-close base drawdown | Hourly-close stress drawdown |
|---|---:|---:|---:|---:|---:|
| Daily control | 524 | +17.65% | +9.73% | 9.50% | 14.53% |
| Daily positive momentum | 528 | +20.28% | +12.28% | 9.02% | 13.22% |
| Daily slower positive momentum | 365 | +17.68% | +12.14% | 10.52% | 13.69% |

At stressed costs, positive daily momentum ends at about $1,122.85 from $1,000; slower momentum about $1,121.42; daily control about $1,097.25. Do not select a historical winner from this close comparison or interpret $123 over two years as a reliable future income stream.

## Sensitivity to execution resolution

| Specification | Four-hour-only stress return | Hourly-detail stress return | Difference |
|---|---:|---:|---:|
| Daily control | +9.7249% | +9.7250% | +0.0001 pp |
| Daily positive momentum | +12.2844% | +12.2845% | +0.0001 pp |
| Daily slower positive momentum | +9.6742% | +12.1420% | +2.4678 pp |

The daily control and positive-momentum totals were effectively unchanged despite some exit timestamps moving. The slower version improved by 2.47 percentage points and executed 365 rather than 366 trades. All candidates were retained; no new tuning followed the hourly result. Hourly bars still cannot establish exact intrabar event order, real executable fills or market impact.

## Data quality

Downloaded 305,184 hourly candles: 17,952 per market, continuous across the full scored period. Every market passed exact expected timestamp coverage and numeric/OHLC/volume checks. Reconstructing four-hour open/high/low/close yielded zero mismatches to the original source at relative tolerance 1e-5. This supports treating the comparison as resolution sensitivity rather than a changed price dataset. No market was silently dropped or gap-filled.

## Drawdown accounting clarification

Installed Freqtrade source shows exported wallet captures occur at the main four-hour candle openings, even with hourly execution enabled. Earlier reports’ marked-wallet figures therefore describe four-hour-open samples; they are not continuous drawdowns. This audit keeps that convention separately and reconstructs a second hourly-close equity path directly from trade cashflows and hourly prices.

Entry/exit fees are charged with their respective recorded events. A trade timestamp denotes an execution hour; events in that hour are considered settled by its closing mark. The resulting final equity reconciles to engine final balance to within $0.000001 for every run. Both measures miss within-hour extremes, and differing marking/fee conventions can produce a slightly smaller or larger drawdown.

| Specification | Engine four-hour-open stress drawdown | Independent hourly-close stress drawdown |
|---|---:|---:|
| Daily control | 14.4898% | 14.5315% |
| Daily positive momentum | 13.1773% | 13.2185% |
| Daily slower positive momentum | 13.7009% | 13.6947% |

This clarifies the sampling convention without rewriting frozen reports. Smaller stakes explain much of the lower drawdown versus $100-entry experiments; they do not reverse losing middle-period performance. All three remain research specifications, and the original positive-middle-return gate is not waived because full-period totals look better.

## Verification and artifacts

24 unit checks passed across research, observer, strategy, hourly-data and independent-accounting suites. The new accounting tests cover entry fees/open holdings, settled trades, same-hour roundtrips and missing active marks. Frozen source/data hashes were rechecked and matched; actual hourly accounting reconciles to engine final balances.

Protocol/data manifest: `INTRABAR_EXECUTION_EXPERIMENT.md`, `data/research/hourly_detail/manifest.json`. Engine runner/results: `evaluate_hourly_execution.py`, `data/research/hourly_execution_check/`. Independent accounting: `HOURLY_EQUITY_AUDIT.md`, `hourly_equity_audit.py`, `hourly_close_audit.json` and per-run hourly equity CSVs.

The one-shot observer baseline is described in `outputs/relative-strength-observation-status.md`. No automatic polling, order simulation or live trading service is running. Future observations must use the frozen manifest and genuinely subsequent completed candles; the baseline itself is not forward evidence.
