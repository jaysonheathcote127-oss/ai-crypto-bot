"""Verify scaled exposure with the actual engine, without changing frozen runs."""
import hashlib
import io
import json
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
from evaluate_research import ROOT,drawdown,engine_timerange
OUT=ROOT/'data/research/low_exposure_check'
NAMES=['DailyRelativeStrength','DailyAbsoluteMomentum','DailySlowMomentum']


def extract(archive,name):
    with zipfile.ZipFile(archive) as z:
        d=next(json.loads(z.read(n)) for n in z.namelist() if n.endswith('.json') and '_config' not in n)['strategy'][name]
        w=pd.read_feather(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('_'+name+'_wallet.feather')))))
    return d,w


def signatures(d):
    return [(t['pair'],t['open_date'],t['close_date'],t['exit_reason']) for t in d['trades']]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen_inputs.json').exists(): raise SystemExit('Existing attempt; preserve artifacts')
    paths=[ROOT/p for p in ['LOW_EXPOSURE_EXECUTION_CHECK.md','config.low_exposure.json','config.research.json',
                           'evaluate_low_exposure.py','evaluate_research.py','user_data/strategies/absolute_momentum.py',
                           'user_data/strategies/daily_relative_strength.py','user_data/strategies/regime_relative_strength.py',
                           'user_data/strategies/research_baselines.py']]
    paths+=sorted((ROOT/'user_data/data/okx').glob('*-4h.feather'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/'frozen_inputs.json').write_text(json.dumps(hashes,indent=2))
    control=json.loads((ROOT/'data/research/momentum_robustness/summary.json').read_text())
    scenarios=json.loads((ROOT/'data/research/momentum_robustness/exposure_scenarios.json').read_text())
    results={}
    for cost,fee in [('base',.0015),('stress',.0045)]:
        folder=OUT/cost;folder.mkdir(exist_ok=True)
        cmd=[str(ROOT/'.venv/bin/freqtrade'),'backtesting','-c','config.research.json','-c','config.low_exposure.json',
             '--userdir','user_data','--strategy-list',*NAMES,'--timerange',engine_timerange('20241001-20261019'),
             '--fee',str(fee),'--cache','none','--backtest-directory',str(folder),'--no-color']
        print('Running',cost,flush=True)
        with (folder/'run.log').open('w') as log: subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        archive=sorted(folder.glob('*.zip'))[-1];results[cost]={}
        for name in NAMES:
            d,w=extract(archive,name)
            e=w.groupby('date').total_quote.sum().sort_index()
            e=pd.concat([e,pd.Series([d['final_balance']],index=[e.index[-1]+pd.Timedelta(seconds=1)])])
            prior,_=extract(ROOT/control['results']['continuous_'+cost][name]['source_archive'],name)
            scenario=scenarios[cost][name]['0.25']
            results[cost][name]={'return_pct':d['profit_total']*100,'marked_wallet_drawdown_pct':drawdown(e)*100,
                                'trades':d['total_trades'],'final_balance':d['final_balance'],
                                'trade_signatures_identical_to_100_stake':signatures(d)==signatures(prior),
                                'return_difference_from_arithmetic_pp':d['profit_total']*100-scenario['arithmetic_return_pct'],
                                'drawdown_difference_from_arithmetic_pp':drawdown(e)*100-scenario['marked_drawdown_pct'],
                                'source_archive':str(archive.relative_to(ROOT))}
            print(name,results[cost][name],flush=True)
    for p,h in hashes.items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h: raise ValueError('Source drift')
    (OUT/'summary.json').write_text(json.dumps({'completed_at':datetime.now(timezone.utc).isoformat(),
                 'status':'posthoc_execution_check_no_promotion','hashes':hashes,'results':results},indent=2))

if __name__=='__main__':main()
