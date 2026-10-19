# Regime-filtered relative strength — 19 October 2026

**Decision: no promotion. This fixed version fails the existing return/drawdown criteria.**

Exploratory tests on previously inspected history, not a new holdout. No parameters were tuned. All 17 saved OKX/USDT markets were retained. Four-hour BTC SMA200 controls risk-on; 30-bar returns rank the universe. Top five qualify for entry above their SMA50; positions exit below SMA50, outside ranks 1–9, or when the BTC filter fails. Signals execute at the next open.

$1,000 wallet, $100 entries, maximum five holdings, fixed 10% per-position stop. Base/stress costs are 0.15%/0.45% per side including an adverse fee-equivalent proxy, not an actual fill model.

| Period | Trades (each cost) | Base return | Stress return | Base drawdown | Stress drawdown |
|---|---:|---:|---:|---:|---:|
| Early: Oct 2024–Sep 2025 | 537 | +48.59% | +16.18% | 22.82% | 35.40% |
| Middle: Oct 2025–Mar 2026 | 127 | -11.61% | -19.21% | 16.08% | 22.98% |
| Recent: Apr–18 Oct 2026 | 287 | +2.32% | -14.93% | 20.88% | 28.77% |

Drawdowns include marked open positions. All periods exceeded 15% drawdown at both costs. The middle period lost at both costs, and the recent period lost under stress. Early base gains do not establish a robust edge.

## Benchmarks

50% invested / 50% cash to approximate the strategy’s maximum initial allocation; exposure is not volatility matched. Cash returned 0%. Each cell gives base / stress net return.

| Period | Strategy | BTC holding | Equal-weight holding |
|---|---:|---:|---:|
| Early | +48.59% / +16.18% | +39.78% / +39.24% | +51.14% / +50.53% |
| Middle | -11.61% / -19.21% | -20.16% / -20.33% | -25.60% / -25.74% |
| Recent | +2.32% / -14.93% | +9.95% / +9.59% | +14.97% / +14.58% |

## Verification and limits

15 research/observer/strategy tests passed, including three new checks covering cross-market future-price independence, deterministic ties/missing timestamps, and signal boundaries. Six Freqtrade backtests completed. No full Freqtrade lookahead/recursive audit was run for this rejected candidate; tests do not prove every engine execution path is unbiased.

Exact timestamp joins prevent forwarding stale ranks; missing universe data blocks entries and signals exits. Alphabetical ties, original-whitelist order for simultaneous entry allocation, and re-entry after stops are fixed protocol choices. No retrospective best-coin selection. Three early-period positions were force-exited at each cost; none in middle/recent.

Current-universe selection/survivorship bias remains. Four-hour OHLC cannot establish actual intrabar fills, market impact or depth. USDT peg and assumed fees remain unverified modelling assumptions. Historical pair precision/minimums are not reconstructed.

Protocol, strategy/config/evaluator and candle-file hashes are in `data/research/relative_strength/frozen_inputs.json`. Full metrics and 50%/100% benchmarks are in `data/research/relative_strength/summary.json`; engine ZIPs retain trades and wallet histories. Config remains credential-free paper research; no scheduler or trading service was started.

## Next step

Keep this specification/results frozen. Lower-timeframe structural sweep testing requires exact source rules and new data; further relative-strength ideas require a separate protocol and should not be optimized on a purported untouched holdout. Gemini’s document supplied a hypothesis, not independent empirical evidence.

## Continuity correction

The earlier Gemini handoff described the Discord screen as unfinished. A newer completed `outputs/discord-crypto-screen.md` and `data/research/discord_exploratory/summary.json` are now present. Neither Discord proxy qualified for promotion. That completed status supersedes the earlier handoff.

Implementation reference: [Freqtrade strategy customization](https://docs.freqtrade.io/en/stable/strategy-customization/).
