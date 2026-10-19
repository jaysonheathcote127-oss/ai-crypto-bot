# Historical-universe feasibility findings — 19 October 2026

**The current-survivor limitation is not resolved. No historical-universe backtest was run.**

A dated source is available: the [24 September 2023 CoinMarketCap snapshot](https://coinmarketcap.com/historical/20230924/). We verified only its first 20 numbered rows, yielding 15 provisional candidates after stablecoin/wrapper exclusions. This is not a top-100 reconstruction or verified venue eligibility.

## Public OKX probes

The bounded audit made 32 three-candle history requests. Twenty-seven returned samples; five rejected the instrument ID. TON and MATIC failed at both earlier dates; an extra MATIC request also failed. Current market metadata lacks those exact spot symbols. Successful sample requests do not establish full coverage, historical depth/spreads, or account access.

Saved metadata identifies successor tickers GRAM and POL. Follow-up requests returned no requested 2023/2024 history under GRAM and no requested 2023 history under POL. A post-migration GRAM request succeeded. Old TON/MATIC requests still failed. Raw requests/responses are retained rather than quietly omitting the assets.

Official event evidence:

- [OKX MATIC migration notice](https://www.okx.com/en-sg/help/okx-to-support-matic-token-migration) documents September 2024 delisting and conversion.
- [OKX TON migration notice](https://www.okx.com/en-gb/help/okx-to-support-ton-crypto-migration) documents June 2026 ticker migration; [completion notice](https://www.okx.com/en-gb/help/okx-completed-ton-token-migration) gives the GRAM listing schedule.

These records explain why present-day ticker availability cannot stand in for historical coverage. They do not justify splicing successor candles over inaccessible predecessor periods.

## Recovered alternative-venue archive

[Binance's official public-data repository](https://github.com/binance/binance-public-data/blob/master/README.md) documents downloadable spot files and integrity checks. Two MATIC archives were downloaded and verified against their published SHA256 checksums:

| Archive | Four-hour rows | First open UTC | Last open UTC | Finding |
|---|---:|---|---|---|
| July 2023 | 186 | 1 July 00:00 | 31 July 20:00 | Complete calendar month |
| September 2024 | 55 | 1 September 00:00 | 10 September 00:00 | Last bar ends 02:59:59.999; only three hours |

The observed partial final candle matches the timing issue raised by [Binance's MATIC delisting announcement](https://www.binance.com/en/support/announcement/detail/6a6de383727f4659a3050f7982e1620f). Both archives passed continuity and numeric/OHLC/volume checks for their returned rows. September is not a complete month and its last candle must not be treated as four full hours.

This recovers a useful source, but it is Binance data. No Binance prices were inserted into the OKX research portfolio. That would introduce venue and event-policy differences requiring a separately specified experiment.

## Consequences and next requirements

Current-survivor filtering is operationally convenient but can hide migrated/delisted instruments. A defensible historical study needs a dated membership record, verified asset identities, historical venue listing/delisting events, explicit treatment of interruptions/conversions, and complete appropriately labelled data. Rank inclusion alone does not prove tradability or liquidity.

Do not drop inaccessible old assets, substitute modern symbols, fill delisting gaps, or choose the date/universe after seeing strategy profits. Public archive recovery is promising, but full single-venue coverage and event handling remain unfinished. No accounts, purchases, credentials, orders, scheduler or strategy changes were introduced by these audits.

Artifacts in `ai-crypto-bot/freqtrade-trial/`:

- `PIT_UNIVERSE_FEASIBILITY.md`, `audit_historical_universe.py`, `data/research/historical_universe_audit/`: frozen source/list, historical rank CSV, raw probes and summary.
- `PIT_ALIAS_FOLLOWUP.md`, `audit_historical_aliases.py`, `data/research/historical_alias_followup/`: alias responses, immutable archive ZIPs/CSVs/checksums and summary.

These are source-feasibility findings, not new performance results. The existing momentum results remain exploratory and unpromoted.
