# Discord-inspired crypto screen

Two fixed four-hour adaptations tested across 17 eligible coins from the saved top-100 snapshot. All periods are exploratory, previously inspected history. This does not reproduce the minute-chart gold strategy.

| Period | Candidate | Trades | Base return | Stressed return | Base/stressed wallet drawdown |
|---|---|---:|---:|---:|---:|
| Early: Oct 2024–Sep 2025 | SweepConfirm | 75 | -6.05% | -10.54% | 10.36% / 13.48% |
| Early: Oct 2024–Sep 2025 | SweepTrendConfirm | 21 | -4.23% | -5.48% | 9.29% / 10.04% |
| Middle: Oct 2025–Mar 2026 | SweepConfirm | 45 | 0.39% | -2.31% | 5.27% / 5.84% |
| Middle: Oct 2025–Mar 2026 | SweepTrendConfirm | 2 | 0.51% | 0.38% | 0.49% / 0.49% |
| Recent: Apr–18 Oct 2026 | SweepConfirm | 34 | -1.66% | -3.70% | 4.33% / 5.53% |
| Recent: Apr–18 Oct 2026 | SweepTrendConfirm | 9 | 0.60% | 0.06% | 1.60% / 1.78% |

## Decision

No promotion. The unfiltered candidate loses after stressed costs in every segment. The trend-filtered candidate loses in the early segment and has only two middle-period and nine recent-period trades, below the existing 30-trade validation minimum. The recent stressed gain is only about $0.62 on a $1,000 wallet. Do not choose winning coins retrospectively.

Twelve research/observer/strategy tests passed, including three new confirmation and prefix-causality checks. This is not a full Freqtrade lookahead or recursive audit; no candidate is being promoted.

Base costs: 0.15% each side; stress: 0.45% each side, including a fee-equivalent adverse-cost proxy. No actual order-book fill model. Fixed $100 entries, maximum five positions, 10% stop. Returns are portfolio returns, not individual trade returns. Four middle-period unfiltered trades and one filtered trade were force-exited at the segment boundary.

## Next evidence needed

Obtain the exact protected-swing and rejection rules, then predefine a separate 5m/15m study with sufficient warmup, liquid top-100 pairs, realistic spread/slippage assumptions, and unchanged rules across coins. Keep range and continuation models separate. New prospective data is required for an untouched evaluation. DXY/session assumptions from gold are not automatically transferable to 24/7 crypto.

Full aggregate results: `data/research/discord_exploratory/summary.json`. Per-coin portfolio contributions: `data/research/discord_exploratory/per_coin.csv`. Engine archives preserve all trades and wallet histories.
