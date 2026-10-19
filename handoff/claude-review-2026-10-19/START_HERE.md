# Trading Bot — independent Claude review

Prepared 19 October 2026 (Europe/London) from the local Trading Bot workspace.
This is a research snapshot, not a trading deployment or a complete chat export.

## Request for Claude

Please critically audit this project, including its failed experiments. Establish
what the code and saved evidence actually support. Do not assume the author's
summaries, tests, source interpretations or profitability claims are correct.

1. Read this file, `memory/PROJECT_MEMORY.md`, the latest entries in
   `memory/CONVERSATION_LOG.md`, and `outputs/experiment-register.csv`.
2. Review methodology: current-survivor selection, repeated inspection of historical
   windows, overlapping trials, parameter selection, forced exits, concentration,
   passive comparisons, fees versus actual slippage, and absence of forward evidence.
3. Audit strategy timing and execution: closed candles, cross-sectional ranking,
   lookahead, daily scheduling, pivot confirmation, stop/target ambiguity, gap fills,
   fee-inclusive sizing, cash limits, allocation priority and delayed eligibility.
4. Reconcile returns, trade cashflows and equity. Distinguish four-hour-open wallet
   samples, hourly-close and five-minute-close drawdown; none captures intrabar lows.
   Check benchmark exposure and cumulative versus annual returns.
5. Check the Jack Savage source interpretation separately from the crypto proxies.
   Identify missing rules and contradictions; sparse proxy results cannot establish
   whether his full gold/DXY method works or whether he earns a living from it.
6. Review tests for missing cases and shared implementation errors. Run offline tests
   if your environment supports them. Clearly distinguish inspected code, reproduced
   results, reported validation and things you could not verify.
7. Rank findings by severity, cite exact paths/lines or result fields, explain the
   practical effect and propose concrete fixes. End with the smallest useful next
   experiment and whether any deployment is justified by the evidence.

Keep review read-only. Do not submit orders, start services, tune strategies or
download fresh data as part of reproducing this frozen snapshot.

## Current evidence and corrections

- No strategy has passed promotion. All scored historical periods have been
  inspected; no untouched holdout or dependable income claim is supported.
- The latest operational study reports 122 overlapping register rows across nine
  underlying strategy specifications. Stress adapters are labelled separately.
  `outputs/RESEARCH_STATUS.md` and `outputs/experiment-register-notes.md` still
  describe the earlier 86-row milestone; use the actual CSV and later log/report.
- Extended Oct 2023–18 Oct 2026 higher-cost totals at $25 stake / $1,000 wallet:
  daily control +14.0902%, positive daily +16.6004%, slower daily +19.4231%.
  Hourly-close drawdowns: 14.0352%, 12.7714%, 12.9461%. These span about three
  years. All variants still lost in the known Oct 2025–Mar 2026 segment.
- Operational delay/reversed allocation checks completed; all losing-window
  controls/stresses stayed negative. Allocation priority materially changes totals.
  See `outputs/operational-robustness-screen.md` and its saved research artifacts.
- Jack-informed 5m BTC/ETH adaptation: NC 3 trades, -0.9975% base / -1.4925125%
  stress; SBC zero in-session trades. Not a full discretionary-method replication.
- Observer has one valid baseline, not an ongoing forward record. No scheduler
  installed by this research. Do not infer later observations from elapsed time.
- Historical-universe feasibility files exist under
  `ai-crypto-bot/freqtrade-trial/data/research/historical_universe_audit/`.
  The saved summary verifies 20 historical ranking rows, 15 provisional assets,
  and only tiny accessibility probes. TON and MATIC probes returned instrument
  errors; POL has a separate response. This does not resolve survivorship bias,
  prove full history/liquidity, or constitute a point-in-time universe backtest.
- Memory and reports are summaries with uneven update times. Resolve disagreements
  against frozen protocols, actual source/data, completed result files and later
  correction entries. Identify discrepancies rather than silently choosing a story.

## Files and reading order

`CLAUDE_REVIEW_TEXT.md` is an upload-friendly concatenation of this brief, memory,
reports, protocols, Python source/tests and configs, labelled with original paths.
It omits bulk raw results/data and is not sufficient to independently reproduce
every number. The full ZIP contains the snapshot with original relative paths.

Start with these reports in `outputs/`:

- `operational-robustness-screen.md`, `history-extension-screen.md`
- `hourly-execution-check.md`, `low-exposure-execution-check.md`
- `momentum-robustness-screen.md`, `daily-relative-strength-screen.md`
- `relative-strength-diagnostics.md`, `top100-research-report.md`
- `jack-savage-discord-research-2026-10-19.md`, `jack-structural-test-report.md`
- `relative-strength-observation-status.md`, `experiment-register.csv`

The trial folder contains protocols (`*EXPERIMENT.md`), strategies in
`user_data/strategies/`, evaluator/audit/test scripts, `requirements.lock.txt`,
raw/normalised prices, run logs, engine result ZIPs, manifests, checksums, equity
CSV files and observer journals. Source material includes third-party course
excerpts; keep the repository private.

## Reproduction and scope

The local `.venv` is a symlink to a runtime outside this workspace. It is excluded
and will not work on another computer. Create a separate environment using
`requirements.lock.txt` and consult the relevant experiment/evaluator before
running anything. The documented native Apple Silicon setup is experimental.
Some scripts contain original absolute paths; identify/adjust a copy if necessary.
No new strategy tests or historical backtests were run while packaging.

The original BTC dashboard, login service and its external runtime are separate
and are not included. This pack contains everything available in this Trading Bot
workspace after excluding hidden/runtime/cache files and symlinks. It cannot
include inaccessible older chats, unreviewed Discord images/videos or external
services. The records are not verbatim transcripts or an independent backup.

`MANIFEST.json` lists packaged files with SHA256 hashes and exclusions. The ZIP
also carries this brief and the text pack. Credential-pattern and credential-field
checks are performed on snapshot text/JSON and nested engine archives; this is
a practical screening step, not a guarantee that arbitrary sensitive data is absent.
