# Crypto bot — paper research

This project reads public Coinbase BTC/USD five-minute candles and calculates
simple moving-average crossover signals. No account credentials are needed and
there is no code for placing orders. A signal is a research output, not a trade.

## Scheduled dashboard

Open http://127.0.0.1:8765 while the runner is active. The schedule is Monday
through Friday, 08:00–16:00 Europe/London, with UK daylight-saving adjustments.
The app checks this schedule locally; it does not need a Codex chat open.

```sh
.venv/bin/python live_dashboard.py
```

The dashboard shows a persistent $1,000 USD paper portfolio, current Coinbase
price, moving-average signal, portfolio chart, trade journal and activity feed.
It checks the public market once a minute; the page refreshes every five seconds.
The live portfolio is separate from offline replay results. Nothing connects to
your Coinbase or CoinSpot account. No real-trading mode exists.

Click **Enable browser alerts & sound**, allow notifications, then **Test alert**.
Alerts cover simulated trades, market errors/recovery and session start/stop.
The tab must remain open; browser throttling, macOS notification settings and
Focus mode may delay or suppress notifications. Alerts must be enabled again
after reloading or opening a new tab. This is not an email/SMS alert service.
Dashboard disconnections also generate an alert when the page detects them.

**Pause for today** stops new simulated trades until the next workday.
**Resume schedule** clears today's pause; it still respects the work hours.
Holdings persist overnight; this version does not liquidate at 16:00. Outside
sessions prices stop updating, so displayed valuation may be stale.

On the first market check after startup, session start, pause/resume or an error,
the bot only establishes a baseline. Later, a newly completed five-minute candle
can trigger a simulated fill at the currently observed Coinbase price, adjusted
for 0.05% adverse slippage and 0.1% hypothetical fees. This differs from the
offline replay's next-bar-opening model. No missed or historical signals are
filled after downtime. A new signal more than two minutes past candle close is
skipped. Quotes older than two minutes or incomplete/missing candles block fills.
The current all-in/all-out model assumes full liquidity and is for paper testing.

State, trades, alerts and valuation history are stored transactionally in
`data/live/paper.sqlite3`, excluded from Git. A process lock prevents two copies
of this runner trading the same portfolio. An interrupted database transaction
rolls back its trade and balance together. Portfolio data survives restarts.

### macOS startup

```sh
.venv/bin/python install_startup.py
```

This installs `~/Library/LaunchAgents/local.ai-crypto-bot.paper-dashboard.plist`
and starts the dashboard at login. Run only one copy: stop a manually launched
runner with Control+C before installing. Logs go to `logs/dashboard.log` and
`logs/dashboard-error.log`. Unexpected exits are restarted by macOS.

While a work session is active, `caffeinate -i` prevents idle system sleep.
Keep the Mac powered on, logged in and its lid open. The app cannot run while
the Mac is shut down, logged out, manually asleep, or closed. It resumes checks
when available and skips missed signals. Outside work hours it permits idle sleep;
the schedule takes effect when the Mac next wakes. It does not wake a sleeping Mac.

To unload the login service, use the command below; to prevent it starting at
future logins, move its plist out of `~/Library/LaunchAgents` using Finder.

```sh
launchctl bootout gui/$(id -u)/local.ai-crypto-bot.paper-dashboard
```

Do not move the project or its virtual environment while the service is installed.

## Run on your Mac

From this project folder, use the existing Python 3.13 environment:

```sh
.venv/bin/python market_data.py
.venv/bin/python run_signals.py
```

The original `market_data.py` is preserved. The new command fetches up to 100
candles, excludes unfinished candles, and prints the latest signals. It saves
`data/latest_signals.csv` (replaced each run) and appends checks to
`logs/signals.log`. These files stay local and are excluded from Git.
Network access is required for these commands; errors stop the run.

For a new environment: `python3.13 -m venv .venv`, then
`.venv/bin/python -m pip install -r requirements.txt`.

## Strategy assumptions

- Short average: 5 completed closes (25 minutes); long: 20 (100 minutes).
- Buy when the short average crosses from at/below to above the long average.
- Sell when it crosses from at/above to below. Otherwise hold.
- Both current and previous averages must exist: at least 21 completed bars.
- Calculations use only closes available at that point, without future prices.
- A sell signal closes an existing simulated holding; it never opens a short.
- This first version assumes consecutive five-minute candles. Missing intervals
  are not filled, so gaps make averages cover a longer period.

## Paper simulator

Run the offline replay after saving candles:

```sh
.venv/bin/python paper_trading.py
```

Each replay starts fresh with $1,000 USD and zero BTC. It recalculates signals
from the input prices, buys with available cash including fees, and sells the
entire holding on a sell signal. Repeated runs do not continue a live portfolio.
A signal at a completed candle close fills at the next candle open. A signal
on the last row has no fill. Inputs must be consecutive five-minute candles;
gaps, duplicates and unordered timestamps stop the replay.

Default hypothetical costs are 0.1% per trade and 0.05% adverse slippage per fill.
These are testing assumptions, not verified Coinbase or CoinSpot fees. Example:

```sh
.venv/bin/python paper_trading.py --cash 1000 --fee-rate 0.001 --slippage-rate 0.0005
```

Each run saves a separate folder in `data/paper_runs/` containing the input
snapshot, `trading_journal.csv`, `equity.csv` and `summary.json`. All stay local
and are excluded from Git. Equity values open BTC at the last close; it does
not deduct a hypothetical exit fee or force a final sale. Profit/loss includes
unrealised changes. There is no continuous background trading or account access.
The model assumes full fills and omits liquidity limits and exchange rounding.
The short sample is a mechanics check, not evidence of profitability.

## CoinSpot compatibility

CoinSpot offers public prices and authenticated trading APIs:
https://www.coinspot.com.au/v2/api . Its documented public endpoints do not list
historical OHLCV candles. The installed CCXT 4.5.88 CoinSpot adapter reports no
`fetchOHLCV` support. This simulator therefore continues using saved Coinbase
BTC/USD candles. It does not represent CoinSpot BTC/AUD prices, spreads or fees.
Future CoinSpot testing needs its own candle source/collector and cost model.
No API keys or CoinSpot account connection are used.

## Offline checks

```sh
.venv/bin/python -m unittest discover -s tests -v
```

See `DEVELOPMENT.md` for the local development record. Git tracks source and
documentation once you make commits; it does not automatically archive chats.

## Move to another computer

Install Git and Python 3.13, then clone this repository:

```sh
git clone https://github.com/jaysonheathcote127-oss/ai-crypto-bot.git
cd ai-crypto-bot
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python live_dashboard.py
```

Open http://127.0.0.1:8765 on the computer running the dashboard.
The current runner uses Unix `fcntl` locking and is intended for macOS/Linux.
On a Windows PC, use a Linux environment such as WSL with Python 3.13;
native Windows support requires adapting the process lock. The login installer
and `.command` launcher are Mac-specific. On Linux, run the Python command above.

GitHub contains source code and documentation. To preserve the existing paper
portfolio, stop the dashboard on the old computer before separately copying
`data/live/` to the same location on the new computer. Keep this database private.
Do not copy `.venv`; recreate it with the commands above. Offline research output
in `data/paper_runs/` can also be transferred separately if wanted.

For future code changes, commit and push from one computer, then run `git pull`
on the other before editing. Sign in to the same GitHub account to push changes.
