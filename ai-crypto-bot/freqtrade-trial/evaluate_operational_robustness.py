"""Predeclared processing-lag and allocator checks, not a strategy search."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
import pandas as pd
from evaluate_research import ROOT,drawdown,engine_timerange
from evaluate_low_exposure import extract,signatures,NAMES
from hourly_equity_audit import hourly_equity
OUT=ROOT/'data/research/operational_robustness'
DATA=ROOT/'data/research/history_extension/merged_data'
DELAYED={'DailyRelativeStrength':'DelayedDailyControl','DailyAbsoluteMomentum':'DelayedDailyAbsolute','DailySlowMomentum':'DelayedDailySlow'}
PERIODS={'extended':('20231001-20261019','2023-10-01','2026-10-19'),
         'middle':('20251001-20260401','2025-10-01','2026-04-01')}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen_inputs.json').exists():raise SystemExit('Existing attempt; preserve artifacts and resolve explicitly')
    reference_path=ROOT/'data/research/history_extension/summary.json'
    reference=json.loads(reference_path.read_text())
    for path,h in reference['hashes'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('Reference source drift: '+path)
    paths=[ROOT/p for p in ['OPERATIONAL_ROBUSTNESS_EXPERIMENT.md','evaluate_operational_robustness.py',
                           'test_operational_delays.py','config.reverse_priority.json','config.research.json','config.low_exposure.json',
                           'hourly_equity_audit.py','evaluate_low_exposure.py','evaluate_research.py',
                           'user_data/strategies/research_baselines.py','user_data/strategies/regime_relative_strength.py',
                           'user_data/strategies/daily_relative_strength.py','user_data/strategies/absolute_momentum.py',
                           'user_data/strategies/operational_delays.py']]+sorted(DATA.glob('*.feather'))+[reference_path]
    for cost in ('base','stress'):
        paths.append(ROOT/reference['results']['extended_continuous_'+cost][NAMES[0]]['source_archive'])
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/'frozen_inputs.json').write_text(json.dumps(hashes,indent=2))
    config=json.loads((ROOT/'config.research.json').read_text())
    if not config['dry_run'] or any(config['exchange'].get(k) for k in ('key','secret','password')):raise ValueError('Paper only')
    all_prices={p:pd.read_feather(DATA/(p.replace('/','_')+'-1h.feather')).set_index('date').close for p in config['exchange']['pair_whitelist']}
    results={};controls={}
    for period,(timerange,start,end) in PERIODS.items():
        prices={p:f[(f.index>=pd.Timestamp(start,tz='UTC'))&(f.index<pd.Timestamp(end,tz='UTC'))] for p,f in all_prices.items()}
        for cost,fee in [('base',.0015),('stress',.0045)]:
            for scenario in ('control','delay','reverse'):
                key=period+'_'+cost+'_'+scenario
                if scenario=='control' and period=='extended':
                    controls[(period,cost)]=reference['results']['extended_continuous_'+cost]
                    results[key]=controls[(period,cost)]
                    continue
                folder=OUT/key;folder.mkdir(exist_ok=True)
                names=[DELAYED[n] for n in NAMES] if scenario=='delay' else NAMES
                cmd=[str(ROOT/'.venv/bin/freqtrade'),'backtesting','-c','config.research.json','-c','config.low_exposure.json']
                if scenario=='reverse':cmd+=['-c','config.reverse_priority.json']
                cmd+=['--userdir','user_data','--datadir',str(DATA),'--strategy-list',*names,'--timerange',engine_timerange(timerange),
                      '--timeframe-detail','1h','--fee',str(fee),'--cache','none','--backtest-directory',str(folder),'--no-color']
                print('Running',key,flush=True)
                with (folder/'run.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
                archive=sorted(folder.glob('*.zip'))[-1];results[key]={}
                for original,name in zip(NAMES,names):
                    d,w=extract(archive,name);e=hourly_equity(d['trades'],prices)
                    if abs(e.equity.iloc[-1]-d['final_balance'])>1e-5:raise ValueError('Independent equity reconciliation failed')
                    e.to_csv(folder/(name+'_hourly_close_equity.csv'),index_label='hour_open_utc')
                    a={'tested_class':name,'return_pct':d['profit_total']*100,'trades':d['total_trades'],'final_balance':d['final_balance'],
                       'hourly_close_drawdown_pct':drawdown(e.equity)*100,'force_exits':sum(t['exit_reason']=='force_exit' for t in d['trades']),
                       'hourly_final_difference':float(e.equity.iloc[-1]-d['final_balance']),'source_archive':str(archive.relative_to(ROOT))}
                    if scenario!='control':
                        ref=controls[(period,cost)][original]
                        prior,_=extract(ROOT/ref['source_archive'],original)
                        a.update(return_delta_pp=a['return_pct']-ref['return_pct'],
                                 drawdown_delta_pp=a['hourly_close_drawdown_pct']-ref['hourly_close_drawdown_pct'],
                                 trade_signatures_identical_to_control=signatures(d)==signatures(prior))
                    results[key][original]=a
                    print(original,a,flush=True)
                if scenario=='control':controls[(period,cost)]=results[key]
                (OUT/'partial_results.json').write_text(json.dumps(results,indent=2))
    for path,h in hashes.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source drift')
    (OUT/'summary.json').write_text(json.dumps({'completed_at':datetime.now(timezone.utc).isoformat(),
         'status':'operational_stress_only_no_promotion','hashes':hashes,'results':results,
         'warning':'All periods inspected, current-universe bias; delay/reverse are sensitivity checks not selected strategies.'},indent=2))

if __name__=='__main__':main()
