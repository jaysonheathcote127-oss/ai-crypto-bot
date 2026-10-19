# Relative-strength observation status

Collected 19 October 2026 15:59:37 BST. Source and manifest hashes verified.

**17 of 17 fixed research markets observed; no entries across all four specifications.** BTC risk-on was false at the latest synchronized completed candle. Exit flags are research conditions, not instructions to sell a position. There is no portfolio or order simulation here.

Latest candle opened 19 October 2026 09:00:00 BST. Every row is `baseline_only`, because this candle predates the frozen forward start.

Manifest created 19 October 2026 15:59:31 BST. The first eligible forward candle opens 19 October 2026 17:00:00 BST and must complete four hours later before it can be recorded. A single baseline snapshot establishes no forward performance.

Data checks: >=300 completed continuous candles, valid OHLC/volume, synchronized latest timestamps, active spot markets and current quote freshness, >=$1m 24-hour pair quote volume, <=0.2% spread. One missing/failed pair blocks the cross-sectional snapshot rather than shrinking the universe. Quotes and candles come from public OKX APIs; account eligibility, fees and fills are unverified.

The first version failed closed on all 17 markets because a single OKX request returned at most 300 candles, including one unfinished bar. Preserved under `data/observations/relative_strength_forward/`. The corrected observer uses supported CCXT pagination and a separate source-frozen ledger under `data/observations/relative_strength_forward_v2/`.

Raw sources are immutable JSON with SHA256 checks, snapshots append to a SQLite journal, and latest JSON/CSV views are available. First manifest fixes source hashes and observation start; source drift causes a failure requiring a separately named experiment. No replay data is represented as current.

No scheduler or continuous collection is running. The script is `observe_relative_strength.py`; this report describes one completed request. None of the four observed strategies is promoted.
