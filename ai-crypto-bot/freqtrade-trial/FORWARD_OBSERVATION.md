# Read-only fixed-universe forward observation

19 October 2026. Research observation only; none of these candidates has passed
promotion criteria. Observe all four relative-strength specifications without
selecting the historical winner. Fixed 17-pair universe from config.research.json;
not a claim to observe all top-100 coins, nor historical point-in-time membership.

One-shot public API collection: at least 300 continuous completed four-hour bars,
valid OHLC/volume, recent completed candle, synchronized latest timestamps across
all 17 pairs, active spot markets and current $1m volume / <=0.2% spread / <=2-minute
quote checks. Existing observe_top100 validators apply. An unavailable/ineligible
pair blocks the whole cross-sectional signal snapshot; do not silently rank a
smaller universe. Live account access and fee tiers are not established.

Append immutable source candles/quotes and signal snapshots with SHA256 source
hashes. Freeze strategy/config hashes in forward_manifest.json on first use;
subsequent source drift must abort, requiring a separately named experiment.
Manifest records actual UTC creation. At first collection the latest completed
bar may predate manifest creation; mark it baseline_only. Only candles starting
at or after the first four-hour boundary at/after manifest creation count as
forward observations. This avoids treating an already observed bar as new.
No order simulation, holdings, trades, P&L or recommendation is generated.
Raw entry/exit flags do not identify actions for an existing position.

No automatic polling or scheduler installed. Running the script once is a single
snapshot, not an unattended service or evidence of strategy profitability.
Preserve all blocked attempts too. Never label saved historical replay as fresh.

Implementation correction before any valid signals: OKX caps an individual candle
request at 300, leaving 299 completed bars if the current bar is present. The first
ledger correctly blocked all 17 markets. Preserve it as a failed attempt. Version 2
uses CCXT's supported two-page deterministic fetch (400 bars); it starts a new
manifest/ledger so the original source hash is never silently replaced.
