"""Freeze and execute the hourly-detail sensitivity for all daily candidates."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
import pandas as pd
from evaluate_research import ROOT,drawdown,engine_timerange
from evaluate_low_exposure import extract,signatures,NAMES
OUT=ROOT/'data/research/hourly_execution_check'


def main():
    manifest=json.loads((ROOT/'data/research/hourly_detail/manifest.json').read_text())
    if len(manifest['assets'])!=17 or any(a['status']!='complete' for a in manifest['assets'].values()):
        raise ValueError('Complete hourly fixed-universe data required')
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen_inputs.json').exists():raise SystemExit('Existing attempt; preserve artifacts')
    paths=[ROOT/p for p in ['INTRABAR_EXECUTION_EXPERIMENT.md','config.low_exposure.json','config.research.json',
                           'evaluate_hourly_execution.py','evaluate_low_exposure.py','evaluate_research.py',
                           'download_hourly_detail.py','data/research/hourly_detail/manifest.json',
                           'user_data/strategies/absolute_momentum.py','user_data/strategies/daily_relative_strength.py',
                           'user_data/strategies/regime_relative_strength.py','user_data/strategies/research_baselines.py']]
    paths+=sorted((ROOT/'user_data/data/okx').glob('*-4h.feather'))
    paths+=sorted((ROOT/'user_data/data/okx').glob('*-1h.feather'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/'frozen_inputs.json').write_text(json.dumps(hashes,indent=2))
    control=json.loads((ROOT/'data/research/low_exposure_check/summary.json').read_text())
    results={}
    for cost,fee in [('base',.0015),('stress',.0045)]:
        folder=OUT/cost;folder.mkdir(exist_ok=True)
        cmd=[str(ROOT/'.venv/bin/freqtrade'),'backtesting','-c','config.research.json','-c','config.low_exposure.json',
             '--userdir','user_data','--strategy-list',*NAMES,'--timerange',engine_timerange('20241001-20261019'),
             '--timeframe-detail','1h','--fee',str(fee),'--cache','none','--backtest-directory',str(folder),'--no-color']
        print('Running hourly execution',cost,flush=True)
        with (folder/'run.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        archive=sorted(folder.glob('*.zip'))[-1];results[cost]={}
        for name in NAMES:
            d,w=extract(archive,name)
            e=w.groupby('date').total_quote.sum().sort_index()
            e=pd.concat([e,pd.Series([d['final_balance']],index=[e.index[-1]+pd.Timedelta(seconds=1)])])
            prior,_=extract(ROOT/control['results'][cost][name]['source_archive'],name)
            before=control['results'][cost][name]
            results[cost][name]={'return_pct':d['profit_total']*100,'marked_wallet_drawdown_pct':drawdown(e)*100,
                                'trades':d['total_trades'],'final_balance':d['final_balance'],
                                'trade_signatures_identical_to_four_hour_execution':signatures(d)==signatures(prior),
                                'return_difference_from_four_hour_pp':d['profit_total']*100-before['return_pct'],
                                'drawdown_difference_from_four_hour_pp':drawdown(e)*100-before['marked_wallet_drawdown_pct'],
                                'source_archive':str(archive.relative_to(ROOT))}
            print(name,results[cost][name],flush=True)
    for p,h in hashes.items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Source drift')
    (OUT/'summary.json').write_text(json.dumps({'completed_at':datetime.now(timezone.utc).isoformat(),
                 'status':'posthoc_execution_sensitivity_no_promotion','hashes':hashes,'results':results,
                 'aggregation_checks':manifest['assets']},indent=2))

if __name__=='__main__':main()
