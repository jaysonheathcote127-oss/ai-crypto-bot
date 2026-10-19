# Where the early relative-strength return came from

19 October 2026. Post-hoc diagnosis of frozen historical experiments. No new independent evaluation.

## Findings

The early period made $485.95 at base costs and $161.80 under stress on a $1,000 simulated wallet. The gains were concentrated, while frequent unsuccessful trades consumed much of the gross price profit. This makes the early return a research lead, not an established income source.

- November 2024 realised $624.46; the rest of the early period combined realised -$138.52. These are profits grouped by exit month, not monthly marked portfolio returns: winners can span more than one month.
- The five biggest winning trades contributed $622.96. Subtracting those profits arithmetically leaves -$137.01. This is a concentration diagnostic, not a rerun without those trades.
- XLM, HBAR and DOGE together contributed $542.27, more than the total net profit. Nine of 17 coins were positive at base costs; six under stress. Selecting those coins retrospectively would bias the experiment.
- Early gross price P&L was $648.02. Assumed friction cost $162.07 at base and $486.21 under stress. Here the two cost runs executed the same trades, so their difference can be directly reconciled to the fee-equivalent deductions.
- Median holding time was 20 hours in all three segments. In the early period, 274 trades held under 24 hours lost $509.26 at base costs. Their eventual holding duration cannot be known at entry, so we cannot simply filter those losing trades out.
- Only four of 12 early exit-month totals were positive. Rare large winners may be a feature of trend following; concentration alone does not demonstrate a defect. It does mean these data contain few independent examples of success.

## Early coin contributions

| Coin | Trades | Base net profit |
|---|---:|---:|
| XLM/USDT | 19 | $+327.08 |
| HBAR/USDT | 20 | $+114.19 |
| DOGE/USDT | 30 | $+101.00 |
| XRP/USDT | 34 | $+76.13 |
| SUI/USDT | 43 | $+45.63 |
| LINK/USDT | 25 | $+27.47 |
| ETH/USDT | 43 | $+23.66 |
| UNI/USDT | 34 | $+5.99 |
| BNB/USDT | 30 | $+5.43 |
| ADA/USDT | 27 | $-4.35 |
| BTC/USDT | 37 | $-7.69 |
| BCH/USDT | 32 | $-7.77 |
| LTC/USDT | 32 | $-21.54 |
| SOL/USDT | 33 | $-31.59 |
| TRX/USDT | 38 | $-34.62 |
| NEAR/USDT | 27 | $-42.67 |
| AVAX/USDT | 33 | $-90.41 |

## Do simple regime descriptions explain the later losses?

These descriptive cohorts use only information available at the signal candle, four hours before the recorded entry open. They partition existing trades, not newly simulated filtered portfolios. Removing entries would change subsequent available capacity and allocation. Cohort findings are post-hoc and correlated across coins.

| Entry context | Early stress P&L (trades) | Middle stress P&L (trades) | Recent stress P&L (trades) |
|---|---:|---:|---:|
| More than half the universe above SMA50 | $+340.90 (287) | $-143.42 (79) | $-187.41 (127) |
| Half or fewer above SMA50 | $-179.09 (250) | $-48.67 (48) | $+38.10 (160) |
| BTC SMA200 rising over six bars | $+320.33 (424) | $-166.01 (85) | $-168.33 (242) |
| BTC SMA200 flat/falling over six bars | $-158.52 (113) | $-26.07 (42) | $+19.02 (45) |

Broad participation and rising BTC SMA200 accompanied early profits, but those same entry cohorts lost in both later segments under stress. Adding either filter is not supported as a general fix by this attribution. No filter thresholds were searched.

## Bounded next experiment

Test one change to reduce decision frequency: entries and rank/own-SMA exits once daily, with BTC risk-off/missing-data exits and the stop retained every four hours. All other rules and both cost levels stay fixed. This is a causal decision schedule, unlike filtering trades by their later duration. The result can improve or worsen returns: less frequent exits can also increase losses. See `DAILY_RELATIVE_STRENGTH_EXPERIMENT.md` and the separate daily-cadence report.

No live orders, credentials, scheduler or funded allocation were introduced. Do not choose a profitable historical month as a trading rule. Truly new forward data is still required.

## Reproducibility

`analyze_relative_strength.py` reads the original engine trade archives, reconciles summed trade P&L to engine totals, and checks price P&L minus recorded cost deductions equals net trade P&L. Outputs are in `data/research/relative_strength_diagnostics/`: coin and exit-month CSVs, trade-level entry context, and summary JSON. Original experiments are unchanged.
