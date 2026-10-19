# Experiment register scope

`experiment-register.csv` was generated from completed final research summaries,
including failures. It contains 122 strategy/window/cost rows across nine distinct
strategy specifications. These are overlapping scenarios, not 122 independent
hypothesis tests or evidence of a statistically significant edge.

Stages include corrected baselines, Discord proxies, original relative strength,
daily cadence, the two absolute/slower momentum variants, continuous controls,
actual smaller-stake execution, hourly detail, earlier-history extension and operational delay/allocation stresses.
Repeated controls, alternate fees, windows, sizing and execution resolutions are
labelled rather than counted as newly invented strategies. All statuses currently
record no promotion.

Drawdown marking is labelled per row. Original summaries use exported four-hour
opening-price marks; later independent audits use hourly closes. Neither measures
continuous intrabar executable equity. Returns for different start/end windows
must not be directly compounded or compared without their exposure assumptions.

The initial SampleStrategy compatibility trial and superseded inclusive-boundary
runs are retained separately, not included as final strategy-selection evidence.
The row source paths point to the exact completed summary used. Reproduce using
`ai-crypto-bot/freqtrade-trial/build_experiment_register.py`.
