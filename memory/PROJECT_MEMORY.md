# Trading Bot project memory

Last updated: 2026-10-19 (Europe/London). Read `CONVERSATION_LOG.md` for provenance and earlier milestones. These are summaries, not complete transcripts or an independent backup.

## User requirements and scope

- Preserve decisions, evidence, corrections and next steps locally across chats.
- User repeatedly authorized continuing research without routine check-ins (“keep going dont stop”). A progress question does not cancel ongoing work.
- Scope is research/paper work. No real orders, credentials, funded deployment or new trading service introduced. No automatic scheduler installed. Original BTC dashboard is separate; current live state not rechecked.
- Residency/account eligibility are unestablished. Gemini's Australia/ASIC assertion was unsupported.
- Jack lead: identity now verified through Wifi Money Discord links as Jack Savage (`savage`). Income/performance remain unverified. Detailed source research: `outputs/jack-savage-discord-research-2026-10-19.md`.

## Environment

Research: `ai-crypto-bot/freqtrade-trial/`, Freqtrade/CCXT/TA-Lib. Current computer uses the restored `github-workspace/` Git clone with an independent root `.venv` (Python 3.13; full saved dependency lock installed). Original computer used an external environment symlink. Preserve the parent dashboard project. Native Apple Silicon setup remains experimental; experiment hashes remain frozen.

## Frozen research and decisions

- Three baseline strategies failed validation; `outputs/top100-research-report.md`.
- Completed Discord proxies also failed promotion; `outputs/discord-crypto-screen.md`. This newer completed status supersedes the original Gemini handoff's unfinished note.
- Original relative strength and daily-cadence follow-up: daily reduced turnover/improved results, but failed positive-middle-return/drawdown gates. `outputs/relative-strength-screen.md`, `daily-relative-strength-screen.md`.
- Attribution: early profits concentrated in November 2024 and XLM/HBAR/DOGE; top five trades exceeded total original profit. Breadth/rising-BTC cohorts inconsistent later. Exit-month attribution is not marked monthly return; subtraction of winners is not portfolio simulation. `outputs/relative-strength-diagnostics.md`.
- Two further predeclared candidates: positive 30-bar daily momentum and slower 120-bar daily momentum. Both middle segments negative at both costs. Continuous stressed returns: four-hour control -18.26%, daily control +38.90%, positive daily +49.14%, slower daily +38.70%; drawdowns 56.79%, 36.90%, 33.62%, 35.23%. No promotion. `outputs/momentum-robustness-screen.md`; trial `data/research/momentum_robustness/`.
- Actual $25-stake continuous checks confirmed arithmetic scaling with identical trade signatures: daily control stress +9.7249%/14.4898% drawdown; positive daily +12.2844%/13.1773%; slower daily +9.6742%/13.7922%. These are ~two-year TOTAL returns, not annual rates. Smaller stakes do not repair losing middle periods. `outputs/low-exposure-execution-check.md` and trial `data/research/low_exposure_check/`.
- All history is inspected/current-universe biased. No untouched holdout or stable income claim. Fee-equivalent adverse costs are not actual fills.

## Validation and observation

- 27 combined checks passed after the earlier-history extension, hourly-data and equity-accounting work. Integrated full-universe prefix/future-shock tests cover momentum signals. Routine single-pair Freqtrade lookahead equivalence is unsuitable for cross-sectional ranking; no full engine audit pass claimed.
- Read-only observer `observe_relative_strength.py` records all four specs for fixed 17 pairs. Valid baseline on 19 Oct 2026 14:59:37 UTC: 17 observed, BTC risk-off, no entries. `outputs/relative-strength-observation-status.md`.
- Baseline is not forward evidence. First eligible forward candle opens 16:00 UTC, completes 20:00 UTC. Source-frozen v2 ledger: `data/observations/relative_strength_forward_v2/`. Original failed single-page attempt preserved separately. No automatic polling runs.
- Primary-source abstract review supports momentum as a research phenomenon, not these exact rules: `outputs/momentum-evidence-notes.md`.

## Hourly execution verification completed

- All 305,184 hourly candles validated; all 17 markets' reconstructed four-hour OHLC match frozen source within declared tolerance. Six hourly-detail strategy/cost results completed at $25 stake.
- Full-period hourly-detail stress returns: daily control +9.7250%, positive daily +12.2845%, slower daily +12.1420%. Total returns across ~2 years, not annual. No promotion; losing middle segments remain.
- Source inspection clarified exported wallet marks are four-hour-open samples even with hourly execution. Separate hourly-close cashflow audit reconciled all final balances within $0.000001. Stress hourly-close drawdowns 14.5315%, 13.2185%, 13.6947% respectively; neither marking convention captures within-hour lows.
- Reports: `outputs/hourly-execution-check.md`, `outputs/low-exposure-execution-check.md`; full artifacts under trial `data/research/hourly_execution_check/` and `hourly_detail/`. Accounting code/protocol: `hourly_equity_audit.py`, `HOURLY_EQUITY_AUDIT.md`. All frozen hashes checked.
- Next useful evidence is genuinely subsequent observation of frozen specifications and exact external structural source rules, not unrestricted historical threshold fitting. First eligible forward bar has not completed at the last work milestone. No autonomous polling or future-run guarantee.

## Jack Savage Discord research (19 October)

- User requested gathering as much Discord information as possible. Read-only pass scanned 17 recap search pages (December 2024–September 2026), resources/vault, selected questions/charts, updated FX plan and core course lessons. Not a full server export; most chart attachments/videos and other course stages remain unreviewed.
- Report: `outputs/jack-savage-discord-research-2026-10-19.md`; saved indicator Markdown source: `outputs/jack-3sl-indicator-source-2026-10-19.md`.
- Conditions-based NC ranging and protected-structure continuation models use multiple timeframes, weak structural targets, rejection confirmation, structural stops, graded risk, sessions/news. Source conflicts include 1R/1.3R, account/grade risk, EMA/divergence timeframe and fixed AEST vs market-local indicator windows. Do not silently resolve them.
- Recaps mix live, challenge, FT and missed trades; payout eligibility is not receipt. September messages mention sales income/replenishing live account. Neither stable living income nor lack of profitability is established.
- Existing 4H crypto Discord experiment explicitly uses simplified proxies, not this full method. No strategy/live-trading changes made in this pass.

## Earlier-history extension completed

- User again authorized continuing; rules/coins remained fixed. Added Jul 2023–Oct 2024 source, scored Oct 2023–Sep 2024 and one longer continuous Oct 2023–18 Oct 2026 wallet. All 17 histories complete; no date changes/exclusions. Overlap and hourly/four-hour aggregation agree within declared tolerance. Original files untouched.
- Earlier-year stressed return/drawdown: daily control +5.0636%/6.3571%; positive daily +5.0143%/6.1598%; slower daily +7.5573%/7.4296%. Full extended stressed totals over ~3 years: +14.0902%/14.0352%, +16.6004%/12.7714%, +19.4231%/12.9461%, respectively. Not annual rates.
- At 12.5% initial investment, extended BTC holding returned +25.2265% with 21.4562% drawdown. Active specs reduced drawdown but gave up BTC return; not volatility matched. Earlier-year profits still concentrated in five big trades and 8–9 profitable coins.
- No promotion: losing middle segment remains; current-universe bias and post-inspection extension choice prevent untouched-holdout claims. 27 checks passed, four engine commands completed, frozen hashes and accounting reconciled.
- Report `outputs/history-extension-screen.md`; full isolated data/results under trial `data/research/history_extension/`. Register `outputs/experiment-register.csv`: 86 overlapping final strategy/window/cost results across nine specs, not independent trials. Raw superseded/compatibility artifacts remain separately preserved.

## Jack-informed intraday test completed

- User asked to test sourced Discord rules. Fixed long-only BTC/ETH adaptation at 5m, closed 15m/1h context; not a faithful gold/DXY replication. Protocol: trial `JACK_STRUCTURAL_EXPERIMENT.md`; code `jack_structural_test.py`, `test_jack_structural.py`, `audit_jack_structural.py`.
- Collected and validated 27,936 five-minute candles per pair (14 July–19 October 2026 exclusive), scored 21 July onward. Frozen sources/data and outputs under trial `data/research/jack_structural/`.
- NC range: 3 trades; base -0.9975% (2 losses, 1 BE), stress -1.4925125% (3 losses). SBC continuation: zero in-session trades at either cost. $1,000 wallets, 0.5% planned cost-inclusive risk, cash cap, costs 0.15%/0.45% each side. Too few trades to assess; no promotion or income inference; not evidence that Jack's full method fails.
- Eight unit tests passed, actual-input prefix/future-shock signal checks passed for both pairs, trade/equity/fee/session audit reconciled. Report `outputs/jack-structural-test-report.md`. No tuning after results. Remaining: source ambiguities and labelled gold/DXY/news data for fidelity, most chart/video review incomplete. No orders/services.

## Cross-computer continuity

- User chose existing https://github.com/jaysonheathcote127-oss/ai-crypto-bot; explicitly authorized uploading while public and will change visibility later.
- Initial 659-file upload succeeded on 19 October 2026, remote main advanced from original 9ea6c20 to 10d8cad. Existing history and research checkpoint are both ancestors. Code, protocols, memory, logs, reports, datasets and result archives included.
- AGENTS.md requires fetch/pull before work and reviewed commit/push at milestones; CROSS_COMPUTER.md gives clone/setup/handoff instructions. This is not background autosync.
- Full chat transcripts, external services/runtimes, credentials, environments, ignored SQLite files and caches are excluded. Windows runtime untested.
- Initial push authenticated via official GitHub CLI temporary device login. Auto-review rejected copying auth state into .git; that action did not run. Future durable setup should use standard GitHub CLI installation/login per computer. No repository credential storage configured.

## Latest operational and source audits

- Delay/order sensitivity completed; 29 selected research/observer checks passed. Full-window stress returns remained positive, but reversed allocation priority changed totals -4.10 to +4.77 pp. All middle-window controls/stresses lost (-3.99% to -3.02%). No best order/delay selected. `outputs/operational-robustness-screen.md`; register now 122 overlapping rows across nine underlying specs.
- Historical-universe feasibility report: `outputs/historical-universe-feasibility.md`. First20 ranked snapshot rows only; not top100. Old TON/MATIC public OKX probes fail, and GRAM/POL do not return requested earlier samples. Alternative Binance MATIC archives recovered/checksummed, but not mixed into OKX. Sep 2024 last bar shortened to three hours. Current-survivor bias unresolved; no historical-universe backtest.

## GitHub upload validation

- Local checkpoint 8520954, merge preserving original remote history 523dd00, handoff instructions 10d8cad. All 659 tracked files matched committed blob bytes before upload; no tracked symlinks or external .venv. Research files preserve exact bytes across operating systems.
- User completed device authorization; initial push succeeded. Fresh independent clone passed git fsck --full; commit 181b131 and complete tree matched local exactly, with 659 tracked files and clean local working tree. Do not infer complete chat transcripts or an older research Git history existed.

## Restored-computer verification (19 October 2026)

- GitHub main `bad62b1` restored with all 659 tracked files; fast-forward pull confirmed current before work. Git integrity passed. Current active clone is `github-workspace/` inside the earlier dashboard folder.
- Installed independent environment with pinned direct requirements plus full research lock; `pip check` passed. Reproduced all four specifications' saved baseline for 17 markets and both structural signal files (BTC 19, ETH 10) exactly; all eight observer source hashes match.
- Full shared-process discovery: 36 passed, one structural error. Importing research_baselines adds DataFrame.atr through its indicator dependency; frozen mid.atr column access then resolves to a function. Isolated structural checks pass. Added run_offline_checks.py: all 37 checks across 12 separate module processes passed. Frozen code unchanged; shared-process compatibility issue remains explicit in WORKSPACE.md.
- Updated stale RESEARCH_STATUS and register notes from 86 to verified 122 overlapping rows across nine underlying specifications; included latest operational/structural/universe findings.
- First eligible forward candle closes 19 October at 20:00 UTC / 21:00 BST. Still pending at this session's checkpoint; no fresh snapshot, order, scheduler or promotion created. Next useful step: one-shot frozen observer after close, preserving all blocked attempts and avoiding forward-profit claims.

- Sync pending: automatic approval review rejected publishing this continuation checkpoint to public main. Local commit is saved; push did not run. Explicit user approval requested; last fetched remote is bad62b1.
