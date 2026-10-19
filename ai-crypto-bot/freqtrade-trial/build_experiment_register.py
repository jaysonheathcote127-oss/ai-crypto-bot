"""Expose every completed final research screen, not only attractive totals."""
import csv
import json
from collections import Counter
from evaluate_research import ROOT

SOURCES=[('baselines','evaluation_exclusive_boundaries/summary.json'),
         ('discord','discord_exploratory/summary.json'),('relative_strength','relative_strength/summary.json'),
         ('daily_cadence','daily_relative_strength/summary.json'),('momentum_robustness','momentum_robustness/summary.json'),
         ('low_exposure','low_exposure_check/summary.json'),('hourly_execution','hourly_execution_check/summary.json'),
         ('earlier_extension','history_extension/summary.json'),
         ('operational_sensitivity','operational_robustness/summary.json')]


def main():
    rows=[]
    audit=json.loads((ROOT/'data/research/hourly_execution_check/hourly_close_audit.json').read_text())
    for stage,relative in SOURCES:
        path=ROOT/'data/research'/relative
        if not path.exists():raise ValueError('Incomplete stage: '+stage)
        summary=json.loads(path.read_text())
        for window,items in summary['results'].items():
            for name,a in items.items():
                metric='hourly_close_drawdown_pct' if 'hourly_close_drawdown_pct' in a else 'marked_wallet_drawdown_pct'
                dd=a.get(metric)
                marking='hourly close reconstructed' if metric.startswith('hourly') else 'four-hour open engine capture'
                if stage=='hourly_execution':dd=audit[window][name]['hourly_close_drawdown_pct'];marking='hourly close reconstructed'
                rows.append({'stage':stage,'strategy':name,'tested_class':a.get('tested_class',name),'window_cost':window,'return_pct':a['return_pct'],
                             'drawdown_pct':dd,'marking':marking,'trades':a['trades'],
                             'status':'no_promotion','source':str(path.relative_to(ROOT)),
                             'note':'Overlapping inspected historical tests; not independent trials or forward performance'})
    destination=ROOT.parents[1]/'outputs/experiment-register.csv'
    with destination.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({'rows':len(rows),'unique_strategies':len(set(r['strategy'] for r in rows)),
                      'rows_by_stage':dict(Counter(r['stage'] for r in rows))},indent=2))

if __name__=='__main__':main()
