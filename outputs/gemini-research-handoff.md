# Crypto trading bot: context and independent research brief

Prepared 19 October 2026 from the local project files. This is a handoff for Gemini, not a new assessment of current markets. Historical figures below are saved experimental results, not independently reproduced for this handoff.

## What we are trying to do

We are developing and researching a crypto paper-trading system with Codex. The aim is to find objectively specified, testable approaches across eligible assets in the crypto top 100, assess them realistically, and only consider a forward paper pilot if evidence warrants it. No profitable edge has been established. We are also exploring whether ideas from a Discord trader who mainly discusses gold can be translated into explicit crypto rules.

An existing BTC paper dashboard is separate from the newer multi-coin research. Project notes identify it as a Coinbase paper dashboard with a weekday work schedule and a LaunchAgent. It remains in the original Codex folder and depends on that folder's Python runtime. The notes say its service was previously verified running; its present live state was not rechecked for this handoff. No funded trading, exchange credentials, or new multi-coin background trading service was introduced by the research.

## Software and project structure

- Research stack: Freqtrade 2026.9, CCXT, TA-Lib, Python 3.13.16 on Apple Silicon macOS.
- Native installation passed compatibility checks, but the project records that Freqtrade recommends Docker on ARM64. Native operation is experimental.
- Current workspace: `Trading Bot/ai-crypto-bot/freqtrade-trial/`.
- The `.venv` is a symlink to the original research environment. Do not remove or relocate the original dashboard/runtime folder.
- Important files: `RESEARCH_PLAN.md`, `DISCORD_EXPERIMENT.md`, `user_data/strategies/research_baselines.py`, `user_data/strategies/discord_proxies.py`, `evaluate_research.py`, `evaluate_discord.py`, `validate_universe.py`, `observe_top100.py`.
- Saved main report: `outputs/top100-research-report.md`. Corrected detailed results: `data/research/evaluation_exclusive_boundaries/summary.json` inside the trial folder.

## Universe and historical data

Started with the 19 October 2026 CoinGecko top 100. Matched coin identities against CoinGecko exchange tickers and active CCXT spot markets, rather than trusting symbols alone. Excluded stablecoins, wrapped coins, and liquid staking/restaking representations. Eligibility required a fresh, non-anomalous quote, at least $1m reported 24-hour pair volume, and spread no wider than 0.2%.

Saved counts: 46 eligible assets on OKX using USDT; 30 on Kraken using USD. Initial loose symbol matches of 65/80 were superseded by these stricter counts. These counts do not establish regional account eligibility or executable liquidity.

Used OKX public historical candles because Kraken's recent OHLCV endpoint was limiting. This was a data-source choice, not a decision to fund OKX. Selected the first 20 eligible assets by current market cap before strategy results; 17 had complete history, each with 5,040 four-hour candles from 1 July 2024 through 18 October 2026. ZEC, HYPE, and GRAM failed the required history start and were not replaced.

Accepted pairs, all against USDT: BTC, ETH, BNB, XRP, SOL, TRX, DOGE, LINK, ADA, NEAR, XLM, BCH, LTC, UNI, AVAX, SUI, HBAR.

Critical limitation: using today's membership, liquidity, and surviving complete histories introduces selection/survivorship bias. This is not a reconstruction of the historical top 100.

## Completed baseline experiment

Three transparent rules were fixed before results, with no parameter search or machine learning:

1. Trend: SMA20 crosses above SMA50 while close is above SMA200. Exit on reverse cross or close below SMA200.
2. Momentum: close crosses above the previous 20-bar high while above SMA200. Exit below the previous 10-bar low or below SMA200.
3. Mean reversion: close below the lower 20-bar, two-standard-deviation Bollinger band and RSI14 below 30. Exit at the middle band or RSI14 above 55.

Shared setup: long-only spot, four-hour candles, 24/7; $1,000 simulated wallet; $100 entries; maximum five concurrent positions; one position per asset; fixed 10% per-position stop; no leverage, averaging down, ROI override, or hyperoptimization. Execution no earlier than the next candle open. Each segment starts with a new wallet and liquidates remaining positions at its end.

Base cost: 0.15% per side, consisting of assumed 0.10% fees plus a 0.05% adverse cost proxy. Stress: 0.45% per side, consisting of assumed 0.40% fees plus the same proxy. The proxy is a fee-equivalent deduction, not an actual fill/slippage model. Fee tiers were not verified. USDT was treated as $1.

Periods, with exclusive end dates:

- Development: 1 October 2024–1 October 2025 UTC.
- Validation: 1 October 2025–1 April 2026 UTC.
- Former holdout: 1 April 2026–19 October 2026 UTC.

| Strategy | Development net | Validation net | Former holdout net | Former holdout stress net |
|---|---:|---:|---:|---:|
| Trend | +50.69% | -15.88% | +18.41% | +13.37% |
| Momentum | +21.09% | -14.76% | +10.96% | +2.03% |
| Mean reversion | -21.55% | -16.79% | -3.39% | -9.51% |

Validation marked-wallet drawdowns: trend 17.95%, momentum 16.86%, mean reversion 25.71%. Former holdout drawdowns: 8.97%, 11.48%, 11.95% respectively.

Selection required positive validation return at both cost levels, at least 30 base-cost closed trades, and at most 15% marked-wallet drawdown. All three failed. The saved selection was **none before the holdout was opened**. Later positive returns do not justify reversing that decision. No strategy was promoted.

Base-cost benchmarks with 50% invested and 50% cash:

| Benchmark | Development | Validation | Former holdout |
|---|---:|---:|---:|
| Cash | 0% | 0% | 0% |
| BTC | +39.78% | -20.16% | +9.95% |
| Equal-weight accepted universe | +51.14% | -25.60% | +14.97% |

These comparisons are not volatility matched; strategy exposure changes over time.

Recorded checks: five research checks and four observer checks passed; sampled Freqtrade lookahead analysis detected no biased entries/exits/indicators across the 17 markets; BTC recursive checks displayed differences rounded to 0.000% across tested startup lengths. These are limited checks, not proof of correctness in every state.

An initial run accidentally included a period boundary candle because of Freqtrade stop-date semantics. Corrected runs use nonoverlapping boundaries and preserve original artifacts. No candidate passed either version. The corrected rerun is not a newly untouched holdout: the later data had already been viewed.

## Read-only multi-coin observer

`observe_top100.py` records research signals and has no portfolio or order-submission code. Saved replay accounted for all 100 assets: 17 observed, 54 excluded, and 29 eligible but without saved replay data. Replay outputs are explicitly labelled `saved_data_replay`; they are not current market quotes.

Fresh mode checks universe age (maximum 24 hours), completed candles, quote freshness, liquidity and spread. It saves immutable JSON snapshots, a SQLite journal, and latest JSON/CSV views. Fresh network polling was not verified in the saved project notes because of network restrictions. No observer scheduler is installed. Signals come from failed baseline strategies and are observations, not trading recommendations.

## Discord-inspired work: newest experiment, unfinished

The newer `DISCORD_EXPERIMENT.md` records reading Wifi Money material from a trader called savage: a March 9 gold long, June 26 range setup, April 16 loss review, and September 24 discussion of double confirmation/re-sweeps. Notes define NC as No Close, NC+S as No Close + a Sweep, and FT as Forward Test. Exact protected swing, divergence, rejection, and higher-timeframe structure rules remain incompletely specified.

Source references recorded in the project:

- https://discord.com/channels/1313357053175009290/1313511410550177802/1480541590106931312
- https://discord.com/channels/1313357053175009290/1313511410550177802/1520040942806241320
- https://discord.com/channels/1313357053175009290/1313511410550177802/1494204059148615761
- https://app.notion.com/p/Trading-System-Terminology-Cheatsheet-29c49527fe408007a3a1d86f99a8dcea

These may require access. Do not assume Gemini can read them or infer missing rules from their titles. Older README/intake notes still say Discord material is awaiting receipt; that is stale relative to the newer experiment protocol.

Two simplified crypto proxies were coded, not a faithful reproduction of the trader:

1. **SweepConfirm:** a completed setup bar trades below the minimum low of the preceding 20 completed bars, closes back above that level and above its open, has a lower wick at least twice its body, and closes in the top quarter of its range. The immediately following bar must close above the setup high. Entry occurs at the next open.
2. **SweepTrendConfirm:** same setup, plus setup close above SMA200 and SMA50 above its value six bars earlier.

Both exit below the previous 10-bar low or when RSI14 exceeds 65. They inherit the fixed 10% stop and baseline sizing/cost assumptions. Structural stops, targets and breakeven management are not implemented; the trend filter is our proxy for context, not the trader's actual higher-timeframe definition.

The plan reuses the same 17 markets and historical periods. All periods must now be called inspected exploratory data; there is no fresh out-of-sample claim or automatic promotion.

Current artifact status: a frozen-input file and first-run log exist, but no completed Discord experiment summary exists. The saved first run failed with a pandas attribute-access TypeError in the RSI exit expression. Current source uses bracket access for that column, but a successful rerun is not evidenced by the saved outputs. Do not report performance for these proxies yet.

## What I want Gemini to research independently

Please challenge this project, including the assumptions and methodology. Do not take the reported results as evidence that a profitable bot already exists. Use dated primary sources where possible and distinguish evidence, inference, and speculation.

1. Evaluate whether liquidity-sweep/rejection/confirmation ideas have credible empirical support in liquid crypto spot markets, after realistic costs. Separate discretionary terminology from reproducible rules and selected trade examples from full records.
2. Propose precise, causal definitions for sweep, rejection, protected swing, higher-timeframe structure, confirmation and invalidation. Explain what chart data is required and where definitions could introduce hindsight or repainting.
3. Investigate transfer from gold to 24/7 crypto: session effects, weekends, exchange fragmentation, spot versus derivatives volume, volatility, spread, and execution assumptions. Do not copy gold leverage or contract sizing.
4. Critique the research design: today's-universe bias, missing histories, sample size, cross-coin dependence, multiple testing, regime dependence, period liquidation, mark-to-market drawdown and comparison with passive exposure. Propose practical improvements.
5. Research suitable historical data and point-in-time universe sources, their coverage, cost, licensing and quality. Assess whether four-hour candles are adequate for these ideas or whether lower-timeframe data is necessary.
6. Assess realistic exchange fees, spread, order limits and account eligibility for a prospective UK-based user. UK relevance is suggested by the workspace timezone, not confirmed residency. Verify current rules and do not infer eligibility from public API access.
7. Recommend a small number of materially distinct next hypotheses, such as regime filters or relative-strength portfolios, ranked by evidence and testing effort. Avoid a broad parameter hunt over already inspected history.
8. Design a prospective paper protocol: frozen rules, dated universe snapshots, genuinely new data, minimum observation requirements, cost stress, benchmark comparison, risk limits, rejection criteria, and explicit promotion gates. Distinguish observation from order simulation.

Desired output: a critical assessment, sources with dates/links, unanswered questions, and a prioritized research plan with specific testable hypotheses. Do not promise returns, invent Discord rules, or treat the previously revealed historical period as an untouched holdout.
