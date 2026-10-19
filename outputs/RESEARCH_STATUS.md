# Current research status — 19 October 2026

No strategy has passed promotion. The unchanged daily momentum rules now have
positive results in an additional earlier year, alongside the original profitable
and losing periods. That improves the historical evidence without establishing
a dependable trading income stream.

Earlier-history extension: same 17 markets and three daily rules, $25 simulated
entries, $1,000 wallet, five positions, hourly execution, 0.45% assumed cost each
side. All returns below are net cumulative totals for their stated windows.

| Specification | Oct 2023–Sep 2024 return | Oct 2023–18 Oct 2026 return | Extended hourly-close drawdown |
|---|---:|---:|---:|
| Daily control | +5.06% | +14.09% | 14.04% |
| Daily positive momentum | +5.01% | +16.60% | 12.77% |
| Daily slower positive momentum | +7.56% | +19.42% | 12.95% |

The extended window is roughly three years; these are not annual rates. At the
same 12.5% initial investment, BTC holding returned +25.23% with 21.46% drawdown.
The active rules sacrificed some BTC return for smaller historical drawdowns.
Exposure varies; comparison is not volatility matched. Early profits remain
concentrated, and the losing Oct 2025–Mar 2026 segment is still in the record.

All 17 earlier histories complete; no gaps, coin exclusions or date shifts.
Hourly/four-hour aggregation and the original-data overlap validated. Original
files remain intact. 27 combined checks passed; frozen hashes and hourly
cashflow/final balances reconcile. No trading promotion or real orders.

See the [earlier-history report](history-extension-screen.md),
[hourly execution report](hourly-execution-check.md),
[actual lower-size check](low-exposure-execution-check.md),
[momentum/continuous-wallet screen](momentum-robustness-screen.md), and
[original profit attribution](relative-strength-diagnostics.md).
The [experiment register](experiment-register.csv) includes 122 completed final
strategy/window/cost evaluations across nine specifications; these overlap and
are not independent trials. Earlier compatibility and superseded boundary runs
remain preserved separately.

A read-only fixed-17-market observer collected one valid baseline across all four
relative-strength specifications. BTC filter was off; no entry flags. Baseline is
not forward performance. First eligible new candle starts 19 October 16:00 UTC
and must complete at 20:00 UTC before observation. No scheduler or automatic
collection runs. See [observation status](relative-strength-observation-status.md).

These historical results still use today-selected survivors and all scored
periods have now been inspected. Future research should preserve the frozen
references and gather genuinely subsequent observations, not tune thresholds to
keep the winning historical months. Exact external structural definitions remain
necessary for another Discord-inspired strategy. Independent momentum references
are scoped in [evidence notes](momentum-evidence-notes.md).

Later completed checks: [operational sensitivity](operational-robustness-screen.md)
confirmed that all variants still lost in the middle window and that allocation
priority materially changes full-period results. The
[Jack-informed crypto test](jack-structural-test-report.md) produced only three
NC trades and zero in-session SBC trades, insufficient for promotion. The
[historical-universe feasibility audit](historical-universe-feasibility.md)
left survivor bias unresolved; no historical-universe backtest was completed.

Durable decisions/provenance: `memory/PROJECT_MEMORY.md` and append-only
`memory/CONVERSATION_LOG.md`; summaries, not a complete chat export.
