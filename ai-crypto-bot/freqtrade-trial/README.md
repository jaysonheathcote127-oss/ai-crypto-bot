# Top-100 paper research trial

## Research completed and observer added

The extended research protocol is in `RESEARCH_PLAN.md`. Seventeen markets had
complete four-hour histories (5,040 candles each). All three fixed baselines
failed the validation criteria; none was promoted. Corrected results are in
`data/research/evaluation_exclusive_boundaries/summary.json`. The initial
inclusive-boundary run is retained separately for audit. Five research tests
and four observer tests pass.

`observe_top100.py` is a read-only observation tool. It has no portfolio or
order submission code. It accounts for the full 100-asset snapshot: 46 OKX
assets passed today's eligibility filters, while 54 are explicitly excluded.
This does not mean 100 assets are tradable. Raw entry/exit flags come from
baselines that failed validation; they are research observations only.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python observe_top100.py --replay-saved
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest test_research test_observer -v
```

The replay accounted for all 100 assets: 17 observed, 54 excluded and 29 without
saved replay data. Outputs are labelled `saved_data_replay` and stored in
`data/observations/replay/`; they contain no purported current quote.

For a fresh observation, network access must be available:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python observe_top100.py
```

Fresh mode requires a validated universe no older than 24 hours, completed
four-hour candles, a recent quote, and current liquidity/spread checks. Refresh
the universe using `refresh_watchlist.py` followed by `validate_universe.py`
when needed. Fresh outputs go to `data/observations/fresh/`, separated from
replay. JSON snapshots are immutable, a SQLite journal retains snapshots and
`latest.json`/`latest.csv` provide the most recent observation.

Fresh polling is not verified in the current project session because local
scripts cannot resolve network hosts under its permissions. No observer
scheduler or new background service is installed. The original BTC dashboard's
LaunchAgent was verified running independently.

This research copy lives in the Trading Bot workspace. Its `.venv` symlink
reuses the previously installed interpreter and packages. See `WORKSPACE.md`;
do not remove the original runtime or dashboard folder.

Discord source material was reviewed directly with user authorization.
`DISCORD_EXPERIMENT.md` defines two fixed four-hour crypto adaptations tested
across the 17 saved eligible markets. Results are in
`data/research/discord_exploratory/`; neither candidate is promoted. All periods
are exploratory, not fresh holdouts. Twelve tests now pass, including three
new signal timing/causality checks. See `../../outputs/discord-crypto-screen.md`.

## Original compatibility-trial record

Separate evaluation of Freqtrade 2026.9. The existing Coinbase paper dashboard
and its launch service remain the active paper bot. This trial is not a second
running trading service and has no exchange credentials.

## Verified on 19 October 2026

- Apple Silicon macOS 26.6.2, standalone Python 3.13.16.
- Native installation from PyPI succeeded; `freqtrade --version`, `pip check`,
  configuration validation through backtesting, and a five-market backtest passed.
- Freqtrade's official documentation recommends Docker on ARM64 and does not
  support this native configuration. Native execution is an experimental trial;
  use Docker as the preferred migration route if native reliability problems arise.
- Python runtime is at `../../work/python/` relative to this trial folder.
  Do not move/remove the runtime or virtual environment.
- CoinGecko top 100 by market capitalisation: provisional symbol-based matches
  for 80 assets on Kraken and 65 on OKX (USD/USDT/USDC spot markets combined).
  These counts include stablecoins and wrapped assets. They are not a validated
  trading universe; identity, liquidity and regional access still need checks.
- Five familiar identities were selected explicitly for the compatibility test:
  BTC, ETH, SOL, XRP and LINK, each against USD on Kraken.
- Downloaded 719 completed hourly bars per pair, with consecutive timestamps.
  Data spans 19 September to 19 October; 200 startup bars reduce the test period
  to 27 September–19 October 2026 (UTC).
- Reused Freqtrade's supplied `SampleStrategy` without editing it; timeframe
  overridden to one hour. This is a software test, not an endorsed strategy.
- $1,000 initial wallet, $100 stake, at most 5 open positions. Assumed 0.4% fee
  on each side, not a verified account tier. No additional slippage model.
- Result: 15 simulated trades; final balance $961.905; -$38.095 (-3.81%).
  Reported closed-trade drawdown 4.19%; wallet-balance drawdown 5.38%.
- Backtest is 24/7, unlike the old dashboard's weekday schedule. No historical
  top-100 membership or out-of-sample evaluation was performed. Results are not
  directly comparable to the running BTC dashboard.

## Reproduce

Run from this folder:

```sh
.venv/bin/python refresh_watchlist.py
.venv/bin/python fetch_trial_data.py
.venv/bin/freqtrade backtesting -c config.paper.json --userdir user_data --strategy SampleStrategy --timeframe 1h --fee 0.004 --cache none
```

Watchlist snapshots are saved with timestamps in `data/watchlists/`. Refresh is
manual for now; no daily refresh job is installed. The ranking is today's list,
not the membership that existed at each historical date. Historical strategy
selection must address this survivorship bias. Data and backtest results stay local.

`config.paper.json` has dry-run enabled, no API credentials, no remote API or
Telegram, and an initial stopped state. No trial bot or autostart is running.
Freqtrade itself also supports real trading: keep this trial paper-only.

## Next research milestone

1. Validate the coin identity mapping and filter stablecoins, wrapped duplicates,
   thin markets and missing data. Freeze dated, exchange-specific watchlists.
2. Obtain longer history. Kraken's recent OHLCV endpoint is limited; use its
   historical trade/download route or assess another supported data source.
3. Predefine simple trend and momentum candidates and compare on chronological
   train/validation/held-out periods with fees and slippage stress tests.
4. Compare against cash, BTC holding and an equal-weight eligible-coin benchmark.
5. Run lookahead/recursive checks and a bounded multi-coin dry-run only after a
   candidate passes those checks. Review the $100 sizing, total exposure, loss
   limits and 24/7 versus weekday schedule before promoting it to autostart.

Sources:
- https://www.freqtrade.io/en/stable/installation/
- https://www.freqtrade.io/en/stable/data-download/
- https://www.freqtrade.io/en/stable/configuration/
- https://docs.coingecko.com/reference/coins-markets
