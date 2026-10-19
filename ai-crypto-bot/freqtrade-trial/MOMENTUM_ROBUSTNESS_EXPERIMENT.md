# Absolute momentum and continuity screen — 19 October 2026

User requested continued autonomous research. Predeclare exactly two new candidates,
not a parameter grid. All history has already been inspected, so none is held out.
Do not promote based solely on this screen or tune these rules after results.

Control: DailyRelativeStrength from DAILY_RELATIVE_STRENGTH_EXPERIMENT.md.
A: DailyAbsoluteMomentum. Same five-day/30-four-hour-bar ranking, plus own momentum
must be strictly positive for entry. At the daily decision also exit when own
30-bar momentum is <=0. This tests whether selecting the least weak declining
assets is harmful. All other control rules unchanged.
B: DailySlowMomentum. Same as A, but momentum/ranking uses 120 four-hour bars
(20 days), fixed as one materially slower horizon, not chosen by a search.
SMA50 and BTC SMA200 remain four-hour indicators. Neither is a daily macro filter.

Both: 17 fixed OKX/USDT spot markets; all required prices finite and positive;
positive volume at decision time; continuous timestamps through each lookback;
missing inputs block entries and trigger immediate exit. Same timestamp joins,
alphabetical ties, top five entries, top nine holding range, own SMA50 condition,
BTC-above-SMA200 gate. Entries and own-price/rank/momentum exits at midnight UTC
using completed 20:00 bars; missing-data/BTC risk-off every four hours. Stop -10%,
$100 stakes, $1,000 initial wallet, five positions, no leverage/averaging. Original
whitelist priority and re-entry behaviour retained. At equal own SMA50 no entry
or SMA exit; absolute momentum equality triggers exit. Next-open execution.

Execute both candidates in the existing three exclusive segments at base/stress
0.15%/0.45% each side. Also run original RegimeRelativeStrength, daily control,
and both candidates continuously from 1 Oct 2024 to 19 Oct 2026 exclusive, with
one wallet and no segment resets. This addresses previously omitted continuity;
it is not another unseen test. Full-window benchmark comparisons use the same
start/end. Preserve original results, source/data hashes before execution, all
metrics, force exits and failed runs. No scheduler, real orders or credentials.

Risk diagnostic: re-express the continuous marked equity path at half the dollar
exposure: E_half=1000+0.5*(E-1000). This is a linear arithmetic scenario, not an
engine rerun or volatility targeting. Smaller exposure cannot change P&L sign.
If cash constraints or order minimums bind, actual scaled execution may differ.

Existing expectations: middle >=30 trades, positive return at both costs,
marked-wallet drawdown <=15% at both costs; recent positive returns/drawdown <=15%
would still only motivate new forward evidence. Report every candidate, no
best-of-history selection. No claim of statistically independent coins/trades.
References: https://docs.freqtrade.io/en/latest/backtesting/
and https://www.freqtrade.io/en/stable/lookahead-analysis/ . Official lookahead
analysis assumes single-pair/full-pair equivalence, which cross-sectional rankings
violate; integrated full-universe prefix tests are required, not a misleading
single-pair audit pass.
