"""Fixed earlier-year and longer continuous checks using isolated merged data."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
import pandas as pd
from evaluate_research import ROOT,drawdown,engine_timerange
from evaluate_low_exposure import extract,NAMES
from hourly_equity_audit import hourly_equity
OUT=ROOT/'data/research/history_extension'
DATA=OUT/'merged_data'
PERIODS={'earlier_year':('20231001-20241001','2023-10-01','2024-10-01'),
         'extended_continuous':('20231001-20261019','2023-10-01','2026-10-19')}


def benchmarks(frames,fee):
    result={'cash':{'return_pct':0.,'hourly_close_drawdown_pct':0.}}
    for name,pairs in [('BTC',['BTC/USDT']),('equal_weight',list(frames))]:
        equity=pd.Series(875.,index=next(iter(frames.values())).index)
        for pair in pairs:
            f=frames[pair];units=125/len(pairs)/(f.open.iloc[0]*(1+fee))
            value=units*f.close
            value=value.copy();value.iloc[-1]*=1-fee
            equity+=value
        result[name+'_12.5pct_invested']={'return_pct':(equity.iloc[-1]/1000-1)*100,
                                        'hourly_close_drawdown_pct':drawdown(equity)*100}
    return result


def main():
    manifest=json.loads((OUT/'data_manifest.json').read_text())
    if len(manifest['assets'])!=17 or any(a['status']!='complete' for a in manifest['assets'].values()):raise ValueError('Complete fixed universe required')
    freeze=OUT/'backtest_frozen_inputs.json'
    if freeze.exists():raise SystemExit('Existing backtest attempt; preserve and explicitly resolve partial execution')
    paths=[ROOT/p for p in ['HISTORY_EXTENSION_EXPERIMENT.md','extend_history.py','evaluate_history_extension.py',
                           'hourly_equity_audit.py','evaluate_low_exposure.py','evaluate_research.py',
                           'config.research.json','config.low_exposure.json','test_history_extension.py',
                           'user_data/strategies/research_baselines.py','user_data/strategies/regime_relative_strength.py',
                           'user_data/strategies/daily_relative_strength.py','user_data/strategies/absolute_momentum.py']]
    paths+=[OUT/'data_manifest.json']+sorted(DATA.glob('*.feather'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    freeze.write_text(json.dumps(hashes,indent=2))
    config=json.loads((ROOT/'config.research.json').read_text())
    if not config['dry_run'] or any(config['exchange'].get(k) for k in ('key','secret','password')):raise ValueError('Paper only')
    all_frames={p:pd.read_feather(DATA/(p.replace('/','_')+'-1h.feather')).set_index('date') for p in config['exchange']['pair_whitelist']}
    results={};references={}
    for period,(timerange,start,end) in PERIODS.items():
        frames={p:f.loc[(f.index>=pd.Timestamp(start,tz='UTC'))&(f.index<pd.Timestamp(end,tz='UTC'))] for p,f in all_frames.items()}
        prices={p:f.close for p,f in frames.items()}
        for cost,fee in [('base',.0015),('stress',.0045)]:
            folder=OUT/f'{period}_{cost}';folder.mkdir(exist_ok=True)
            cmd=[str(ROOT/'.venv/bin/freqtrade'),'backtesting','-c','config.research.json','-c','config.low_exposure.json',
                 '--userdir','user_data','--datadir',str(DATA),'--strategy-list',*NAMES,
                 '--timerange',engine_timerange(timerange),'--timeframe-detail','1h','--fee',str(fee),
                 '--cache','none','--backtest-directory',str(folder),'--no-color']
            print('Running',period,cost,flush=True)
            with (folder/'run.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            archive=sorted(folder.glob('*.zip'))[-1];key=period+'_'+cost;results[key]={}
            references[key]=benchmarks(frames,fee)
            for name in NAMES:
                d,w=extract(archive,name);e=hourly_equity(d['trades'],prices)
                if abs(e.equity.iloc[-1]-d['final_balance'])>1e-5:raise ValueError('Hourly cashflows do not reconcile')
                e.to_csv(folder/(name+'_hourly_close_equity.csv'),index_label='hour_open_utc')
                results[key][name]={'return_pct':d['profit_total']*100,'profit':d['profit_total_abs'],'final_balance':d['final_balance'],
                                    'trades':d['total_trades'],'hourly_close_drawdown_pct':drawdown(e.equity)*100,
                                    'engine_four_hour_open_drawdown_pct':drawdown(w.groupby('date').total_quote.sum())*100,
                                    'force_exits':sum(t['exit_reason']=='force_exit' for t in d['trades']),
                                    'hourly_final_difference':float(e.equity.iloc[-1]-d['final_balance']),
                                    'start':d['backtest_start'],'end':d['backtest_end'],
                                    'source_archive':str(archive.relative_to(ROOT))}
                print(name,results[key][name],flush=True)
            (OUT/'partial_results.json').write_text(json.dumps(results,indent=2))
    for path,h in hashes.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source/data drift')
    (OUT/'summary.json').write_text(json.dumps({'completed_at':datetime.now(timezone.utc).isoformat(),
           'status':'historical_extension_no_promotion','hashes':hashes,'results':results,'benchmarks':references,
           'warning':'Current-universe bias; extension chosen after later results; not an untouched holdout or forward evaluation.'},indent=2))

if __name__=='__main__':main()
