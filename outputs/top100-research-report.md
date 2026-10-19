# Top-100 crypto research — 19 October 2026

**Decision: no strategy qualified for promotion. The existing BTC paper dashboard continues; no multi-coin trading service was started.**

## What was tested

Reused Freqtrade 2026.9, CCXT and TA-Lib. Wrote three fixed, unoptimized baseline rule sets; no strategy vendor or claimed profit record was assumed reliable.

Today's CoinGecko top 100 was matched by coin ID to exchange tickers and active spot markets. Excluded stablecoins, wrapped assets and liquid staking/restaking tokens. Required a fresh, non-anomalous quote, at least $1m reported pair volume over 24 hours and a spread no wider than 0.2%.

| Exchange | Eligible assets today | Portfolio quote |
|---|---:|---|
| OKX | 46 | USDT |
| KRAKEN | 30 | USD |

These are stricter counts than the initial 80/65 symbol matches. Public API availability does not establish whether an account in your region can trade these markets.

The first 20 eligible OKX assets by current market cap were selected before backtest results. Seventeen had complete history: 5,040 four-hour candles each, 1 July 2024 through 18 October 2026. ZEC, HYPE and GRAM were excluded for missing history at the required start; replacements were not added.

Accepted markets: BTC/USDT, ETH/USDT, BNB/USDT, XRP/USDT, SOL/USDT, TRX/USDT, DOGE/USDT, LINK/USDT, ADA/USDT, NEAR/USDT, XLM/USDT, BCH/USDT, LTC/USDT, UNI/USDT, AVAX/USDT, SUI/USDT, HBAR/USDT.

OKX was used as a public historical-data source because Kraken's recent candle endpoint is limited. This is not a decision to open or fund an OKX account.

## Results

Each period began with a separate $1,000 simulated wallet, $100 entries, at most five open positions, a 10% per-position stoploss and no leverage. Tests run 24/7 rather than the existing dashboard's weekday work schedule.

Base costs assume 0.10% fees plus a 0.05% per-side cost proxy. Stress costs assume 0.40% fees plus that proxy. The proxy is a fee-equivalent deduction, not an actual slippage simulation. Fees are assumptions, not verified account tiers.

| Approach | Development return | Validation return | Later held-out return | Later return, higher costs |
|---|---:|---:|---:|---:|
| Trend following | +50.69% | -15.88% | +18.41% | +13.37% |
| Momentum breakout | +21.09% | -14.76% | +10.96% | +2.03% |
| Mean reversion | -21.55% | -16.79% | -3.39% | -9.51% |

Development: 1 October 2024–30 September 2025. Validation: 1 October 2025–31 March 2026. Later period: 1 April–18 October 2026. Period end candles are exclusive; each segment liquidates remaining positions at its end.

Selection required positive validation results at both cost levels, at least 30 base-cost trades and no more than 15% marked-wallet drawdown. All three failed. The saved decision was **none before opening the held-out results**; the later gains do not reverse that decision.

| Approach | Validation drawdown | Later-period drawdown |
|---|---:|---:|
| Trend following | 17.95% | 8.97% |
| Momentum breakout | 16.86% | 11.48% |
| Mean reversion | 25.71% | 11.95% |

Drawdowns include marked open positions; they can be larger than the engine's closed-trade drawdown. A drawdown is the largest fall from a previous portfolio peak.

## Buy-and-hold comparison

Base-cost returns, with 50% invested to approximate the strategies' maximum initial allocation. These portfolios are not volatility matched, and strategy exposure varies over time.

| Benchmark | Development | Validation | Later period |
|---|---:|---:|---:|
| Cash | +0.00% | +0.00% | +0.00% |
| 50% BTC / 50% cash | +39.78% | -20.16% | +9.95% |
| 50% equal-weight eligible coins / 50% cash | +51.14% | -25.60% | +14.97% |

The full benchmark JSON also includes fully invested portfolios, cost stress and drawdowns. Buy-and-hold benchmarks assume USDT holds its dollar peg and deduct entry/exit costs.

## Verification and limits

- Five automated checks passed, including future-price independence, previous-bar breakout channels, rejection of price gaps/invalid OHLC data, nonoverlapping period boundaries and marked drawdown arithmetic.
- Freqtrade lookahead analysis checked 20 signals per strategy across the 17-market validation universe: no biased entries, exits or indicators detected. This is sampled evidence, not a proof for every possible market state.
- Freqtrade recursive analysis on BTC at startup lengths 199, 299, 300, 499 and 999 displayed indicator differences rounded to 0.000% and no indicator lookahead bias.
- Initial lookahead checks on only BTC/ETH/SOL had insufficient completed trades and were inconclusive; the completed checks used all 17 markets.
- Freqtrade includes its stop candle. An initial run overlapped one boundary candle. Original artifacts were retained, the command ranges were corrected, and the comparison was rerun without changing any strategy or threshold. No candidate passed either version. The rerun is a technical correction, not a newly untouched holdout.
- Today's coin membership and liquidity filters introduce historical selection/survivorship bias. Excluding incomplete histories adds another selection constraint. These results cannot establish a historical top-100 strategy's performance.
- Four-hour OHLC bars cannot establish intrabar event order or actual fills; order-book depth, historic exchange precision/limits, market impact and USDT depeg risk are not reconstructed.
- Native installation worked, but Freqtrade recommends Docker on Apple Silicon. This installation remains an experimental research environment.

## Next development direction

Keep these results frozen. Do not optimize these rules against the revealed holdout. The next useful work is prospective universe snapshots and observation of all eligible markets, followed by a separately documented experiment (for example a market-regime filter or relative-strength portfolio). Any such experiment must treat these historical periods as already inspected and reserve genuinely new forward data for evaluation.

No real orders, credentials, exchange accounts or new background trading services were introduced. The original paper portfolio remains independent.

## Sources

- [Freqtrade installation and ARM64 guidance](https://www.freqtrade.io/en/stable/installation/)
- [Freqtrade historical data](https://www.freqtrade.io/en/stable/data-download/)
- [Freqtrade lookahead analysis](https://www.freqtrade.io/en/stable/lookahead-analysis/)
- [Freqtrade recursive analysis](https://www.freqtrade.io/en/stable/recursive-analysis/)
- [CoinGecko market rankings](https://docs.coingecko.com/reference/coins-markets)
- [CoinGecko identity-linked exchange tickers](https://docs.coingecko.com/reference/exchanges-id-tickers)
