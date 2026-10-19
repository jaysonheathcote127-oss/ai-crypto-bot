# Predeclared Jack-informed structural crypto test — 19 October 2026

Scope: test an explicit mechanisation of the newly sourced rules, not claim to
replicate Jack's discretionary gold system. Freeze before downloading/scoring.
No parameter search, leverage, short selling, live orders, or promotion.

Source: ../../outputs/jack-savage-discord-research-2026-10-19.md and linked plan.
API: https://app.okx.com/docs-v5/en (GET market/history-candles).

Data: fixed BTC/USDT and ETH/USDT, public OKX spot 5m. Collect July 14 through
October 19 2026 00:00 UTC exclusive; score July 21 onward in three 30-day blocks
(July 21–August 20, August 20–September 19, September 19–October 19). This is
newly collected historical data after prior crypto research, not a holdout.
Fail on missing/invalid/duplicate/unconfirmed candles. Keep original source
JSON, normalised CSV, hashes and exact code/protocol hashes. Custom event-based
simulator for variable structural stops/targets; not a Freqtrade audit.

## Exact mechanical assumptions

All are fixed approximations where the sources are discretionary:
- Only completed candles. Resample 15m and 1h with UTC buckets and publish at
  bucket CLOSE. A pivot is a unique high/low against two bars each side; publish
  only at the close of the second right bar. Never backdate its availability.
- 15m trending context: close breaks a prior confirmed pivot high with >=50%
  of directional candle body above it, adverse wick <=20% of total range.
  Protected low = latest confirmed pivot low. State stays bullish until close
  below protected low; bearish counterpart tracked to avoid range classification
  during falling structure. BOS age limited to 16 completed 15m bars (4 hours).
  Inactive state = ranging. This is an operational state model, not an exact
  external/internal structure taxonomy or Jack's exhaustion classification.
- Range bounds: prior 20 completed 15m bars' min low/max high; width >=2 ATR15,
  >=3 separated boundary visits in total, at least one each edge, tolerance
  0.15 ATR15. Consecutive touches count once. These numbers are our assumptions.
- NC range long: 15m state ranging; 5m setup sweeps frozen lower bound then
  closes back inside; following 5m candle bullish, body >=50% total range,
  upper wick <=20%, close above setup close. Upper frozen range bound is target.
- Continuation long: bullish 15m BOS within 4h, also 5m close crosses its prior
  confirmed pivot high within 12 bars; setup sweeps protected 15m low and closes
  above; next 5m rejection as above. Target nearest already confirmed 15m/1h
  pivot high above rejection close. This substitutes confirmed highs for the
  source's discretionary weak structural targets; no claim they are equivalent.
- Both require a previously confirmed 1h pivot high above rejection close as
  directional target context, stop below min(sweep low, level) by 0.05 ATR5,
  and at least 1.3R at NEXT candle open. No trade if stop/target crossed already.
  1.3R follows updated plan; no alternate 1R run. DXY/divergence/EMA exit and
  discretionary risk entries excluded, not replaced with invented signals.
- No numeric widening/tuning after seeing results. Long-only spot explicitly
  excludes source shorts. BTC/ETH are fixed liquid-data candidates, not selected
  from test results. No coins selected by profitability.

## Portfolio/execution

Each model is a separate $1,000 wallet, one open position across BTC/ETH, BTC
priority for simultaneous signals, no averaging. 0.5% equity cash risk per trade
including round-trip fees at planned stop; cap notional at available cash.
This uses the updated live-risk lower bound, not the conflicting 2% course cap.
Base 0.15% per side; stress 0.45% per side inherited research assumptions, not
verified fee tiers. Market entry next 5m open, never rejection close.
Gapped stops fill at worse open; favourable target gaps fill at target, not open.
If both stop and target touched in one bar, stop first. Entry bar can stop out.
Move to fee-covering BE only after a completed close beyond the confirmed 5m
pivot high frozen at entry; change effective NEXT bar. This is a proxy for the
first internal break. Do not move stop backwards. No intrabar optimistic path.
Fixed structural target is the source default; no discretionary EMA trailing.
Force close at scored end; log reason. Five-minute-close equity/drawdown, not
tick/intrabar drawdown. Unrealised equity includes estimated liquidation fee.

Use indicator source default windows: Tokyo 08–10, London 07–09, New York
08:30–10:30 local, inclusive start/exclusive end (boundary difference from
indicator disclosed). Weekdays only, one new entry per local-date/session
globally per model. Already-open trades can run beyond session. Weekly/session
news filters unavailable; no assertion that historical high-impact news avoided.
Source window inconsistency retained in report; indicator defaults chosen once.

Report aggregate and monthly-block trades, net returns, profit factor, win/BE
counts, close-sampled drawdown, fees, R, pair attribution, exposure and signal
funnel. At least 30 trades per model plus positive results in every block at
both costs would only motivate further investigation, never establish income.
No untouched validation claim. Run causal prefix/future-shock checks, known-fill
accounting tests, stop/target conflict test and timezone/DST tests before results.
