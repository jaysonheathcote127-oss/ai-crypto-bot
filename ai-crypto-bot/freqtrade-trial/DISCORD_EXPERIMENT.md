# Discord-inspired exploratory screen — 19 October 2026

Protocol recorded before running these candidates. User authorized reading Wifi
Money and trials across top-100 coins. This is a new, deliberately simplified
crypto hypothesis, not a reproduction or endorsement of the trader's strategy.

Sources read: savage's March 9 gold long (5m break, 15m confirmation, sweep,
rejection, breakeven at internal structure); June 26 range setup; April 16 loss
review (conflicting timeframes and invalid setup); September 24 discussion of
double confirmation and re-sweeps. Knowledge-vault terminology page confirms
NC = No Close, NC+S = No Close + a Sweep, FT = Forward Test. Precise protected
swing, divergence and rejection criteria remain incompletely specified.

https://discord.com/channels/1313357053175009290/1313511410550177802/1480541590106931312
https://discord.com/channels/1313357053175009290/1313511410550177802/1520040942806241320
https://discord.com/channels/1313357053175009290/1313511410550177802/1494204059148615761
https://app.notion.com/p/Trading-System-Terminology-Cheatsheet-29c49527fe408007a3a1d86f99a8dcea

## Fixed proxy rules

Use existing 17-market OKX/USDT spot universe and four-hour history. No new coin
selection based on performance. Long-only. Signal setup bar must sweep below
the previous 20 completed bars' minimum low, close back above that level, close
above its open, have lower wick at least twice its body, and close in the top
quarter of its range. On the immediately following completed bar, require a
close above the setup high. Execute at the next bar open through Freqtrade.

Compare exactly two candidates: SweepConfirm (rules above) and
SweepTrendConfirm (also require setup close above SMA200 and SMA50 above its
value six bars earlier). The trend filter is our proxy, not the trader's HTF
structure definition. No tuning. Exit when close falls below prior 10-bar low
or RSI14 exceeds 65. Fixed 10% stop, $100 entries, $1,000 wallet, maximum five
positions, no leverage or averaging. These inherited controls intentionally
isolate entries; structural stops/targets and breakeven are future experiments.

Run the same three chronological segments and both 0.15% and 0.45% per-side
cost assumptions as the original research. ALL segments are now inspected
historical data, including the former holdout. Name them early/middle/recent
in conclusions. No fresh out-of-sample claim or automatic promotion is allowed.
Today's universe creates selection/survivorship bias. Four-hour OHLC cannot
validate minute execution, spreads, slippage or intrabar paths. Report aggregate
and per-coin results, sample sizes and marked-wallet drawdown. Positive results
only nominate a hypothesis for causality checks and prospective observation.
