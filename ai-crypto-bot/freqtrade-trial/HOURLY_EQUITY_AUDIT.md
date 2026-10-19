# Independent hourly-close equity audit — 19 October 2026

Inspection of installed Freqtrade optimize/backtesting.py time_pair_generator and
_capture_wallet shows wallet captures occur once per main candle at open prices,
even when hourly execution detail is enabled. Existing marked-wallet figures
are sampled four-hour-open marks, not continuous or hourly drawdown estimates.
They remain valid for that sampling convention; don't silently relabel them.

Reconstruct an additional equity series from each completed hourly-detail trade
ledger at each hourly candle close. Cash subtracts amount*open_rate*(1+fee_open)
at entry and receives amount*close_rate*(1-fee_close) at exit. Remaining units
are marked to the hourly close. Trade timestamps label the execution hour; treat
all recorded events within that hour as settled before its closing mark. This
is post-hoc accounting, not a trading signal or a new fill simulation. Check
final settlement against engine final balance. Entry fees are recognized on
entry; engine wallet accounting/sampling can differ.

Report hourly-close drawdown separately from engine-exported four-hour-open
sample drawdown. Neither captures within-hour lows or actual executable equity.
Full-period risk measures cannot repair failed segment expectations. Test the
accounting on known cashflows, same-hour entry/exits and missing active marks.
Do not alter previous frozen source/results.
