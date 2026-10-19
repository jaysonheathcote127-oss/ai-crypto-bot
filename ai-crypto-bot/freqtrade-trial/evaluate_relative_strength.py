"""Preserve a single frozen exploratory relative-strength experiment."""
import hashlib
import json
from datetime import datetime, timezone
import evaluate_research as engine


def main():
    engine.OUT = engine.ROOT / 'data/research/relative_strength'
    engine.STRATEGIES = ['RegimeRelativeStrength']
    engine.OUT.mkdir(parents=True, exist_ok=True)
    if (engine.OUT / 'summary.json').exists():
        raise SystemExit('Completed experiment exists; preserve it.')
    config = json.loads((engine.ROOT / 'config.research.json').read_text())
    assert config['dry_run'] and not config['exchange'].get('key') and not config['exchange'].get('secret')
    paths = [engine.ROOT / p for p in ['RELATIVE_STRENGTH_EXPERIMENT.md',
             'user_data/strategies/regime_relative_strength.py', 'config.research.json',
             'evaluate_relative_strength.py', 'evaluate_research.py']]
    paths += sorted((engine.ROOT / 'user_data/data/okx').glob('*-4h.feather'))
    hashes = {str(p.relative_to(engine.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (engine.OUT / 'frozen_inputs.json').write_text(json.dumps(hashes, indent=2))
    results = {f'{period}_{cost}': engine.run(period, cost)
               for period in engine.PERIODS for cost in engine.COSTS}
    summary = {'completed_at': datetime.now(timezone.utc).isoformat(),
               'status': 'exploratory_only_no_promotion', 'hashes': hashes,
               'results': results, 'benchmarks': engine.benchmarks(config),
               'warning': 'Previously inspected history, current-universe bias, fee proxy is not actual fills.'}
    (engine.OUT / 'summary.json').write_text(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
