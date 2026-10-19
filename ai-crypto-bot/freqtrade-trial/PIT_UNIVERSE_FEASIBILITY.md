# Historical-universe source feasibility audit — 19 October 2026

No trading/performance experiment in this step. Audit a primary dated ranking
source instead of inferring an old universe from today's survivors. Use the
24 September 2023 CoinMarketCap snapshot (seven calendar days before Oct 1);
only its first 20 explicit numbered rows were verified. Do not claim top-100
reconstruction or exact original publication timestamp. Source:
https://coinmarketcap.com/historical/20230924/

Save rank/name/symbol/category facts for those 20 rows, excluding four stablecoins
and one wrapped representation from a provisional 15-asset candidate set. A rank
record is not proof of venue identity, pair listing, executable liquidity or access.
Current OKX metadata is diagnostic only, not a criterion to omit disappeared coins.

Probe public OKX historical candles for all 15 exact symbol-USDT instrument IDs
at 1 July 2023 (warmup) and 1 September 2024 (before the documented migration).
Keep all successful/error responses. Three bars test accessibility only, not full
coverage or causal liquidity/spread eligibility. Extra MATIC/POL boundary probes
at 8 September 2024 document discontinuity; never stitch or replace silently.
Do not open accounts, buy API plans, use credentials or submit orders.

OKX's 29 Aug 2024 migration notice records MATIC spot delisting at 11:00 UTC on
7 Sep 2024 and account conversion to POL at 1:1 on 9 Sep. These are different
instruments and operational events; historical trading simulation must explicitly
model delisting/forced exits/conversion rather than use today's ticker list.
https://www.okx.com/en-sg/help/okx-to-support-matic-token-migration

No historical-universe backtest until identity/listing coverage, missing/delisted
asset handling, dated membership and historical execution assumptions are explicit.
Missing a disappeared asset is not permission to remove it from the sample.
Freeze audit source/list before requests. Preserve raw responses and provenance.
