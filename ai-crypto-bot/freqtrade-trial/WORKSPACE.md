# Research environment and continuity

Restored from GitHub on 19 October 2026. The active clone is `github-workspace/`
inside the older dashboard project. Run Git commands from this clone. Its parent
folder is a separate, earlier project; do not overwrite or delete it.

This clone now has its own ignored `.venv` at repository root, created with
Python 3.13 and installed using `requirements-research.txt`, then the complete
`ai-crypto-bot/freqtrade-trial/requirements.lock.txt`. It does not use the original
computer's external environment symlink. `pip check` passes.

From repository root, run the offline experiment tests with:

```sh
.venv/bin/python ai-crypto-bot/freqtrade-trial/run_offline_checks.py
```

Each test module runs in a separate interpreter. Importing `research_baselines`
loads an indicator library that adds `DataFrame.atr`; this conflicts with the
frozen structural experiment's `mid.atr` column access in a shared interpreter.
Combined unittest discovery fails one structural test; isolated structural tests
pass. This is an unresolved import-composition limitation of the frozen source,
not a strategy correction or evidence that combined discovery passed. Do not
silently edit frozen scripts or replace their manifests. A future revised
structural experiment should use explicit column indexing and a new source freeze.

The saved 17-market baseline was reproduced exactly, as were the saved BTC/ETH
structural signals, on this environment. Reproduction is not new forward evidence.

For a one-shot public observation, from repository root:

```sh
.venv/bin/python ai-crypto-bot/freqtrade-trial/observe_relative_strength.py
```

Only completed candles opening at/after 19 October 2026 16:00 UTC qualify for the
existing forward ledger. The first closes at 20:00 UTC (21:00 Europe/London).
Do not label an earlier run as forward evidence. No scheduler is installed.
The original dashboard/login service and private portfolio state are separate.
