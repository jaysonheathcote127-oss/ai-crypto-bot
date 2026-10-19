# Historical alias/archive follow-up — 19 October 2026

Preserve the first historical-universe audit. Current saved identity validation
maps the TON asset ID to GRAM/USDT and Polygon to POL/USDT. Official OKX notices
confirm TON→GRAM ticker migration in June 2026 and MATIC→POL in September 2024.
A current alias does not automatically carry the old instrument's candle history.

Bounded data feasibility follow-up, no performance testing: request three historical
four-hour bars for GRAM at Jul 2023, Sep 2024 and Jun 17 2026; POL at Jul 2023;
TON at Jun 15 2026; MATIC at Sep 6 2024. Retain errors/empty responses too. Never
substitute the successor for the predecessor or fill gaps.

Separately test Binance's official downloadable spot archive for MATICUSDT July
2023 and September 2024, with published SHA256 checksum verification. These are
Binance candles, not OKX fills/data. Recovery establishes another archival source,
NOT permission to patch one venue's missing asset into another venue's portfolio.
Record first/last open and close timestamps and incomplete candle durations;
a delisting month need not be a complete calendar month. No purchases/accounts.

Sources:
- https://www.okx.com/en-gb/help/okx-to-support-ton-crypto-migration
- https://www.okx.com/en-gb/help/okx-completed-ton-token-migration
- https://www.okx.com/en-sg/help/okx-to-support-matic-token-migration
- https://github.com/binance/binance-public-data/blob/master/README.md
- https://www.binance.com/en/support/announcement/detail/6a6de383727f4659a3050f7982e1620f

This does not complete historical identities, as-of liquidity/spreads, delisting
policy or all required market histories. No historical-universe backtest yet.
