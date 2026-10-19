"""Fixed candidates plus continuous runs, all explicitly exploratory."""
import hashlib
import json
from datetime import datetime, timezone
import evaluate_research as engine


def main():
    engine.OUT = engine.ROOT / 'data/research/momentum_robustness'
    engine.STRATEGIES = ['DailyAbsoluteMomentum', 'DailySlowMomentum']
    engine.OUT.mkdir(parents=True, exist_ok=True)
    if (engine.OUT / 'frozen_inputs.json').exists():
        raise SystemExit('An attempt already exists; preserve it and explicitly resolve incomplete runs.')
    config = json.loads((engine.ROOT / 'config.research.json').read_text())
    if not config['dry_run'] or any(config['exchange'].get(k) for k in ('key','secret','password')):
        raise ValueError('Credential-free paper research only')
    paths = [engine.ROOT / p for p in [
        'MOMENTUM_ROBUSTNESS_EXPERIMENT.md','RELATIVE_STRENGTH_EXPERIMENT.md',
        'DAILY_RELATIVE_STRENGTH_EXPERIMENT.md','evaluate_momentum_robustness.py',
        'evaluate_research.py','config.research.json','test_absolute_momentum.py',
        'user_data/strategies/absolute_momentum.py','user_data/strategies/daily_relative_strength.py',
        'user_data/strategies/regime_relative_strength.py','user_data/strategies/research_baselines.py']]
    paths += sorted((engine.ROOT / 'user_data/data/okx').glob('*-4h.feather'))
    hashes = {str(p.relative_to(engine.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (engine.OUT / 'frozen_inputs.json').write_text(json.dumps(hashes,indent=2))
    results = {}
    for period in list(engine.PERIODS):
        for cost in engine.COSTS:
            results[f'{period}_{cost}'] = engine.run(period,cost)
            (engine.OUT/'partial_results.json').write_text(json.dumps(results,indent=2))
    engine.PERIODS['continuous'] = '20241001-20261019'
    engine.STRATEGIES = ['RegimeRelativeStrength','DailyRelativeStrength','DailyAbsoluteMomentum','DailySlowMomentum']
    for cost in engine.COSTS:
        results[f'continuous_{cost}'] = engine.run('continuous',cost)
        (engine.OUT/'partial_results.json').write_text(json.dumps(results,indent=2))
    summary = {'completed_at':datetime.now(timezone.utc).isoformat(),
               'status':'exploratory_only_no_promotion','hashes':hashes,'results':results,
               'benchmarks':engine.benchmarks(config),
               'warning':'All historical periods previously inspected; no fresh holdout; current-universe selection bias.'}
    (engine.OUT/'summary.json').write_text(json.dumps(summary,indent=2))

if __name__=='__main__': main()
