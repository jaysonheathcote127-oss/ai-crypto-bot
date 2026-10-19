# Jack-informed intraday crypto test — 19 October 2026

Completed a fixed-rule research test using the newly collected Discord material. This is a mechanised long-only BTC/ETH adaptation, not a reproduction of Jack’s discretionary gold trading.

Scored 21 July–19 October 2026 (end exclusive), with seven days of warmup. Two models, one independent $1,000 wallet each, 0.5% planned equity risk including costs and a cash cap. No leverage, shorts, optimisation or live orders.

| Model | Costs each side | Trades | Net return | 5m-close drawdown | Profit factor | Fees |
|---|---:|---:|---:|---:|---:|---:|
| NC | 0.15% | 3 | -1.00% | 1.00% | 0.00 | $5.58 |
| NC | 0.45% | 3 | -1.49% | 1.49% | 0.00 | $9.55 |
| SBC | 0.15% | 0 | +0.00% | 0.00% | n/a | $0.00 |
| SBC | 0.45% | 0 | +0.00% | 0.00% | n/a | $0.00 |

NC = formed-range sweep and rejection; SBC = protected-structure continuation. Fees include the assumed adverse execution-cost allowance; they are not verified account fee tiers.

| Model/cost | Jul 21–Aug 20 | Aug 20–Sep 19 | Sep 19–Oct 19 |
|---|---:|---:|---:|
| NC base | -0.50% (1 exits) | -0.50% (2 exits) | +0.00% (0 exits) |
| NC stress | -0.50% (1 exits) | -1.00% (2 exits) | +0.00% (0 exits) |
| SBC base | +0.00% (0 exits) | +0.00% (0 exits) | +0.00% (0 exits) |
| SBC stress | +0.00% (0 exits) | +0.00% (0 exits) | +0.00% (0 exits) |

Block returns use the same continuous wallet and include unrealised positions marked at each boundary. They are not separate fresh-wallet tests, and this history is not an untouched holdout.

## Interpretation

Neither model meets the predeclared exploratory screen (at least 30 trades and positive returns in every block at both costs). No promotion. A small sample is insufficient evidence, not proof that Jack’s full system fails.

## What was actually tested

- Completed 5m entries with closed 15m/1h context; delayed confirmed pivots; sweep then a separate strong rejection candle; next-open entries; structural stops and targets; minimum 1.3R; fixed structural take-profit; next-bar cost-covering breakeven after an internal-break proxy.
- One trade per market-local session, weekdays only, one concurrent position across BTC/ETH; BTC priority when both qualify. Indicator-default windows selected before results.
- Stop-first handling when target and stop fall in the same bar, adverse gap fills, entry-bar stops and forced closure at the test end. Drawdown samples 5m closes and can miss intrabar lows.

## What remains untested

- Gold/FX, DXY, discretionary weak/protected structure, chart grading, divergence, shorts and historical news filtering. Confirmed pivot highs are a target proxy, not verified equivalents of Jack’s weak structure.
- Pivot width, range lookback/touch tolerance, ATR buffer and BOS recency are fixed researcher assumptions. No thresholds were fitted to these returns.
- Jack’s source conflicts (1R versus 1.3R, risk caps, EMA timeframe and sessions) remain unresolved. This pass chose explicit rules rather than combining conflicting versions.
- Funding, leverage, tick execution, spreads/order-book liquidity, provider payout rules, taxes and withdrawals are not modelled. No earnings forecast follows from this test.

## Validation and provenance

Eight synthetic checks passed before results. Real-input prefix and future-shock signal checks passed on both pairs; output audit reconciles individual trade fee cashflows, ending balances, entry signals, minimum R and one-entry-per-session constraints. This is not an independent implementation or full engine audit.

Each pair contains 27,936 validated five-minute candles. Raw exchange JSON, normalised CSV, source/data SHA256 manifests, signals, trades, close-equity curves, summary and audit are in `ai-crypto-bot/freqtrade-trial/data/research/jack_structural/`.

Protocol: `ai-crypto-bot/freqtrade-trial/JACK_STRUCTURAL_EXPERIMENT.md`. Source research: `outputs/jack-savage-discord-research-2026-10-19.md`. Public candle schema: [OKX API documentation](https://app.okx.com/docs-v5/en).

Next useful step: resolve the source ambiguities and obtain labelled gold examples/data with DXY and news context, before claiming fidelity to the source strategy. Keep this adaptation frozen; do not tune it against the same period.
