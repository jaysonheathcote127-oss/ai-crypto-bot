# Development record

## 19 October 2026

- Resumed from the ChatGPT conversation “AI trading viability”.
- Inspected the existing Python 3.13.9 environment and `market_data.py`.
- Preserved the existing script; added a standalone signal calculation and runner.
- Kept the scope to public market data and signals, without credentials or orders.
- Added local data/log folders, dependency pins, and Git exclusions.
- Offline validation: `.venv/bin/python -m unittest discover -s tests -v`
  passed all 5 tests. Covered crossover direction and warm-up, flat prices,
  input validation, exclusion of unfinished candles, and independence from
  future prices.
- Live Coinbase retrieval was not run in this session; network integration and
  strategy profitability remain unverified. No simulated trades were executed.

### Paper simulator milestone

- User confirmed the public Coinbase signal run succeeded, then requested the
  paper simulator and asked about CoinSpot compatibility.
- Added offline replay with $1,000 USD starting cash, long-only all-in/all-out
  positions, next-bar opening fills, hypothetical 0.1% fees and 0.05% slippage.
- Added independent per-run input snapshots, trade journals, equity and summaries.
- All 11 offline tests passed, including cost arithmetic, next-bar execution,
  unfilled final signals, invalid input and reproducibility checks.
- Replayed the user's saved Coinbase data: 3 simulated trades, $998.11 final
  marked portfolio value, -$1.89 P/L and $2.99 fees. An open BTC position remains;
  final equity excludes hypothetical exit costs. This is not a profitability study.
- Report: `data/paper_runs/20261019T131024_4ecfe733/`.
- Checked official CoinSpot V2 documentation and the installed CCXT adapter:
  public prices and order APIs exist, but no historical candle endpoint is
  documented and this adapter has no fetchOHLCV support. CoinSpot integration
  is not implemented; Coinbase USD results are not CoinSpot AUD results.

### Scheduled live paper dashboard

- User requested continuous paper operation while working and a dashboard.
  Confirmed Monday–Friday 08:00–16:00 Europe/London, browser alerts and sound.
- Added a persistent SQLite portfolio independent of offline replays, a local
  HTTP dashboard, a single-runner lock and transactional trade/equity updates.
- Polls public Coinbase candles and ticker every minute during work hours.
  Newly closed crossovers fill at the observed current price with hypothetical
  costs. First checks, restarts, recovery and missing candles do not replay trades.
- Added stale-data checks, once-per-outage alerts, pause for today/resume, and
  browser notifications/sound requiring an open tab and browser permission.
- Dashboard binds only to 127.0.0.1:8765. Control requests require the page token,
  same origin and expected Host. All data remains local; no exchange credentials.
- Added macOS login-service installer and active-session idle-sleep prevention.
  User approved installation outside the workspace. Installed and verified
  `~/Library/LaunchAgents/local.ai-crypto-bot.paper-dashboard.plist`; dashboard
  responded successfully after the manually launched preview was stopped.
- All 19 automated tests passed. Tests include DST/schedule boundaries, restart
  persistence, duplicate prevention, stale/missing data, failure/recovery and
  transaction rollback. Python source compilation passed.
- Browser QA confirmed live public prices, rendering, pause/resume, chart and
  notification permission. Enabled notifications and sound and issued a test
  alert in the retained dashboard tab; actual delivery follows macOS settings.
- Verified fresh public prices after login-service launch. Portfolio remains
  $1,000 cash with no live-paper trades yet; waiting for a future crossover.
- Operational limits: Mac must be awake/logged in with lid open; no wake-on-time
  setup. Outside hours no price checks or automatic liquidation. Browser alerts
  require the tab open and re-enabling after reload. CoinSpot integration and
  actual-money trading remain unimplemented.
