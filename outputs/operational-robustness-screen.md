# Execution delay and allocation-priority sensitivity

19 October 2026. No new selected trading strategy or promotion. All periods inspected and today-universe selected. Same three daily rules, 17 markets, $25 simulated entries, $1,000 wallets, five slots, 10% stop, hourly execution and independent hourly-close equity. Both original cost assumptions (0.15%/0.45% per side) retained.

## Full continuous period after higher costs

October 2023–18 October 2026. Returns are cumulative totals across roughly three years, not annual rates. Delay shifts entry and exit signal eligibility by one four-hour bar; stoploss is never delayed. Reverse changes static pair priority only, not ranks or the eligible universe.

| Specification | Control return / drawdown | Delayed return / drawdown | Reverse-priority return / drawdown |
|---|---:|---:|---:|
| Daily control | +14.09% / 14.04% | +14.22% / 13.80% | +18.86% / 13.11% |
| Positive momentum | +16.60% / 12.77% | +16.59% / 12.59% | +18.62% / 13.00% |
| Slower momentum | +19.42% / 12.95% | +23.29% / 11.41% | +15.32% / 13.48% |

## Known losing segment after higher costs

1 October 2025–31 March 2026. Each run begins with a fresh wallet. These control runs match the $25 stake/hourly execution settings, so the stress comparisons do not rely on scaling an older $100 result.

| Specification | Control return / drawdown | Delayed return / drawdown | Reverse-priority return / drawdown |
|---|---:|---:|---:|
| Daily control | -3.18% / 3.73% | -3.18% / 4.50% | -3.74% / 4.28% |
| Positive momentum | -3.26% / 3.81% | -3.02% / 4.35% | -3.74% / 4.28% |
| Slower momentum | -3.51% / 4.42% | -3.99% / 4.92% | -3.54% / 4.45% |

## Every return scenario, including lower costs

| Window | Specification | Cost | Control | Delayed | Reverse priority |
|---|---|---|---:|---:|---:|
| extended | Daily control | base | +25.87% | +25.92% | +30.58% |
| extended | Daily control | stress | +14.09% | +14.22% | +18.86% |
| extended | Positive momentum | base | +28.48% | +28.42% | +30.52% |
| extended | Positive momentum | stress | +16.60% | +16.59% | +18.62% |
| extended | Slower momentum | base | +27.92% | +31.69% | +23.88% |
| extended | Slower momentum | stress | +19.42% | +23.29% | +15.32% |
| middle | Daily control | base | -2.27% | -2.24% | -2.77% |
| middle | Daily control | stress | -3.18% | -3.18% | -3.74% |
| middle | Positive momentum | base | -2.35% | -2.08% | -2.77% |
| middle | Positive momentum | stress | -3.26% | -3.02% | -3.74% |
| middle | Slower momentum | base | -2.82% | -3.29% | -2.86% |
| middle | Slower momentum | stress | -3.51% | -3.99% | -3.54% |

## Where reversed-priority differences came from

Shared entries are matched by pair and open timestamp. Added/removed entries describe a different simulated portfolio; do not retrospectively choose the profitable ones. Net P&L delta reconciles to added profits minus removed profits plus changed P&L on shared entries. All figures below are full-window higher-cost dollars.

| Specification | Removed entries / P&L | Added entries / P&L | Shared-entry P&L change | Total P&L change |
|---|---:|---:|---:|---:|
| Daily control | 201 / $+84.47 | 196 / $+132.17 | $+0.00 | $+47.69 |
| Positive momentum | 178 / $+65.29 | 179 / $+85.46 | $+0.00 | $+20.18 |
| Slower momentum | 64 / $+149.79 | 69 / $+108.81 | $+0.00 | $-40.98 |

## Interpretation

Full-window higher-cost return changes across the two fixed stresses ranged from -4.10 to +4.77 percentage points. Better delayed or reversed outcomes are sensitivity findings, not a basis to change production rules. Allocation order is part of the strategy specification because existing holdings can occupy slots while ranks change.

Known losing-window stressed returns ranged from -3.99% to -3.02% across all controls/stresses. Inspect that range alongside total returns; a stress that improves one period need not fix the model. Existing validation gates are unchanged.

A one-bar delay is a blind signal-processing stress, not a proposed safe execution method. It can enter on stale context and postpone a risk-off signal. Signals become eligible four hours later; with hourly detail, actual fills can occur within that eligible bar depending on slot availability and engine behaviour. Fixed stops remain active throughout.

No claim of live fills, historic order-book depth, account eligibility, fee-tier verification or independent out-of-sample returns. Current-universe bias and within-hour ambiguity remain. Do not search further order permutations or delay lengths to maximize these historical numbers.

## Verification and artifacts

29 combined checks passed, including two new delay/prefix/stop and order-independent-ranking tests. Ten new engine commands produced 30 new candidate/cost/window results; six full-window control results reused the exact verified earlier-extension archive. All frozen hashes matched. Every new final hourly-close balance reconciles to the engine within $0.00001, and trade-difference attribution also reconciles.

Sources: `OPERATIONAL_ROBUSTNESS_EXPERIMENT.md`, `evaluate_operational_robustness.py`, `user_data/strategies/operational_delays.py`, `config.reverse_priority.json`. Full summary, frozen hashes, engine ZIPs/logs, hourly equity CSVs and trade-difference attribution: `data/research/operational_robustness/`. Original strategies/configs/archives remain unchanged. No orders, scheduler or service introduced.
