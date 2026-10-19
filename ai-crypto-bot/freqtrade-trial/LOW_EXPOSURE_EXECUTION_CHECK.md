# Quarter-size execution check — 19 October 2026

Follow-up after the momentum robustness screen and arithmetic exposure scenarios.
This is a post-hoc implementation check, not a new selected strategy or untouched
experiment. No entry/exit changes. Include all three daily specifications, not
only the best past performer. One fixed lower stake: $25 rather than $100.
$1,000 wallet, five maximum concurrent trades, same 17 pairs, stop and all rules.
Initial maximum allocated stake $125; asset price changes can change exposure.

Run one continuous wallet 1 Oct 2024–19 Oct 2026 exclusive, at both fixed cost
levels 0.15% and 0.45% per side. Compare actual engine trades, returns and marked
wallet drawdowns against the previously reported quarter-size arithmetic paths.
Compare trade signatures (pair/open/close/reason) to detect min-order/capacity or
rounding changes. Preserve original configs; layered override only sets stake.
Freeze files before execution. No inference that lower size fixes negative middle
period expectation or passes existing selection. No orders or scheduler.
