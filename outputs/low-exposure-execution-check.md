# Actual $25-stake execution checks

19 October 2026. Continuous 1 October 2024–18 October 2026. **Not annual returns. No candidate promoted.**

Tested all three daily specifications at $25 simulated entries, compared with $100-stake controls. Starting wallet $1,000, maximum five holdings, unchanged stops/rules, and fixed 17-market OKX/USDT research universe. At entry prices, five stakes deploy at most $125 initially; market gains can increase subsequent exposure. This was a post-hoc sizing verification, not an optimized strategy selected from uninspected data.

| Specification | Trades | Base return | Stress return | Base marked drawdown | Stress marked drawdown |
|---|---:|---:|---:|---:|---:|
| Daily control | 524 | +17.65% | +9.72% | 9.50% | 14.49% |
| Daily positive momentum | 528 | +20.28% | +12.28% | 9.02% | 13.18% |
| Daily slower positive momentum | 366 | +15.22% | +9.67% | 10.56% | 13.79% |

All six actual engine runs retained identical trade signatures (pair, open, close, exit reason) to their $100-stake continuous controls. Differences from quarter-size arithmetic were <=0.000113 percentage points in return and <=0.000082 percentage points in marked drawdown, consistent with small amount/price rounding effects. This check found no binding order-minimum or available-capital differences at $25 under the engine assumptions. Actual exchange fill feasibility remains unverified.

The positive-momentum version turned $1,000 into about $1,122.84 after higher costs over the full period. That positive combined total includes a profitable early regime and a losing middle regime. Reducing stake limits dollar losses; it does not reverse a negative expectation or establish dependable income. Selecting this version because of its highest historical total would introduce selection bias.

All historical periods were already viewed. Costs are assumed 0.15% and 0.45% per side, including a fee-equivalent adverse cost proxy; no true order-book slippage model. Current-universe selection and USDT assumptions remain. Four-hour execution assumptions are being checked separately with one-hour detail.

Artifacts: `LOW_EXPOSURE_EXECUTION_CHECK.md`, `config.low_exposure.json`, `evaluate_low_exposure.py`, and `data/research/low_exposure_check/` (frozen hashes, both engine ZIPs/logs and summary). No original research config was modified; the new config is a layered stake override. No real orders or scheduler.
