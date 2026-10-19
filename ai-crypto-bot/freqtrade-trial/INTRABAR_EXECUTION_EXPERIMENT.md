# Hourly detail execution sensitivity — 19 October 2026

Follow-up verification, no new signal rules or selected winner. The $25-stake
continuous checks closely matched linear scaling but still relied on four-hour
intrabar assumptions. Test all three daily variants with one-hour execution detail
through Freqtrade --timeframe-detail 1h. Indicators/signals remain four-hour;
only simulated intrabar stop/exit paths gain resolution. Hourly OHLC still cannot
establish exact event order, real fills or order-book impact.

Download public OKX one-hour candles for all 17 fixed markets from 1 Oct 2024
through 19 Oct 2026 exclusive. Reject missing/duplicate/unordered hours, invalid
OHLC/volume and incomplete ranges. Persist successful files and a data manifest;
never fill gaps or quietly drop a market. Compare reconstructed four-hour OHLC
to the frozen four-hour source, reporting mismatches (relative tolerance 1e-5).
Any mismatch makes this a data-source sensitivity, not an isolated path test.

Freeze protocol/downloader before requests and strategy/evaluator/config/hourly
and original four-hour data hashes before engine runs. Use one continuous $1,000
wallet, $25 stakes, max five holdings, unchanged rules/stop, same whitelist order,
both 0.15%/0.45% cost levels. Report all candidates including negative outcomes
and differences to original four-hour-only execution. No promotion, new account,
real orders or scheduler. This is inspected historical data, not a fresh holdout.
