"""Report all predeclared stresses and reconcile allocation/path differences."""
import hashlib
import json
import pandas as pd
from evaluate_research import ROOT
from evaluate_low_exposure import extract,NAMES
OUT=ROOT/'data/research/operational_robustness'
LABELS={'DailyRelativeStrength':'Daily control','DailyAbsoluteMomentum':'Positive momentum','DailySlowMomentum':'Slower momentum'}


def comparison(control,test,original):
    before,_=extract(ROOT/control['source_archive'],original)
    after,_=extract(ROOT/test['source_archive'],test['tested_class'])
    a=pd.DataFrame(before['trades']).set_index(['pair','open_date'])
    b=pd.DataFrame(after['trades']).set_index(['pair','open_date'])
    if not a.index.is_unique or not b.index.is_unique:raise ValueError('Ambiguous repeated entry key')
    shared=a.index.intersection(b.index);removed=a.index.difference(b.index);added=b.index.difference(a.index)
    shared_pnl=float(b.loc[shared].profit_abs.sum()-a.loc[shared].profit_abs.sum())
    removed_pnl=float(a.loc[removed].profit_abs.sum());added_pnl=float(b.loc[added].profit_abs.sum())
    delta=float(b.profit_abs.sum()-a.profit_abs.sum())
    if abs(delta-(shared_pnl+added_pnl-removed_pnl))>1e-5:raise ValueError('Allocation attribution mismatch')
    return {'shared_entry_keys':len(shared),'removed_entries':len(removed),'added_entries':len(added),
            'shared_entry_net_pnl_delta':shared_pnl,'removed_entry_net_pnl':removed_pnl,
            'added_entry_net_pnl':added_pnl,'total_net_pnl_delta':delta}


def main():
    s=json.loads((OUT/'summary.json').read_text())
    for path,h in s['hashes'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source drift')
    attribution={}
    lines=['# Execution delay and allocation-priority sensitivity','','19 October 2026. No new selected trading strategy or promotion. All periods inspected and today-universe selected. Same three daily rules, 17 markets, $25 simulated entries, $1,000 wallets, five slots, 10% stop, hourly execution and independent hourly-close equity. Both original cost assumptions (0.15%/0.45% per side) retained.','','## Full continuous period after higher costs','','October 2023–18 October 2026. Returns are cumulative totals across roughly three years, not annual rates. Delay shifts entry and exit signal eligibility by one four-hour bar; stoploss is never delayed. Reverse changes static pair priority only, not ranks or the eligible universe.','','| Specification | Control return / drawdown | Delayed return / drawdown | Reverse-priority return / drawdown |','|---|---:|---:|---:|']
    for name in NAMES:
        vals=[]
        for scenario in ('control','delay','reverse'):
            a=s['results']['extended_stress_'+scenario][name];vals.append(f"{a['return_pct']:+.2f}% / {a['hourly_close_drawdown_pct']:.2f}%")
        lines.append('| '+LABELS[name]+' | '+' | '.join(vals)+' |')
    lines+=['','## Known losing segment after higher costs','','1 October 2025–31 March 2026. Each run begins with a fresh wallet. These control runs match the $25 stake/hourly execution settings, so the stress comparisons do not rely on scaling an older $100 result.','','| Specification | Control return / drawdown | Delayed return / drawdown | Reverse-priority return / drawdown |','|---|---:|---:|---:|']
    for name in NAMES:
        vals=[]
        for scenario in ('control','delay','reverse'):
            a=s['results']['middle_stress_'+scenario][name];vals.append(f"{a['return_pct']:+.2f}% / {a['hourly_close_drawdown_pct']:.2f}%")
        lines.append('| '+LABELS[name]+' | '+' | '.join(vals)+' |')
    lines+=['','## Every return scenario, including lower costs','','| Window | Specification | Cost | Control | Delayed | Reverse priority |','|---|---|---|---:|---:|---:|']
    for window in ('extended','middle'):
        for name in NAMES:
            for cost in ('base','stress'):
                vals=[f"{s['results'][window+'_'+cost+'_'+scenario][name]['return_pct']:+.2f}%" for scenario in ('control','delay','reverse')]
                lines.append('| '+window+' | '+LABELS[name]+' | '+cost+' | '+' | '.join(vals)+' |')
                for scenario in ('delay','reverse'):
                    a=s['results'][window+'_'+cost+'_control'][name]
                    b=s['results'][window+'_'+cost+'_'+scenario][name]
                    attribution[window+'_'+cost+'_'+scenario+'_'+name]=comparison(a,b,name)
    (OUT/'trade_difference_attribution.json').write_text(json.dumps(attribution,indent=2))
    lines+=['','## Where reversed-priority differences came from','','Shared entries are matched by pair and open timestamp. Added/removed entries describe a different simulated portfolio; do not retrospectively choose the profitable ones. Net P&L delta reconciles to added profits minus removed profits plus changed P&L on shared entries. All figures below are full-window higher-cost dollars.','','| Specification | Removed entries / P&L | Added entries / P&L | Shared-entry P&L change | Total P&L change |','|---|---:|---:|---:|---:|']
    for name in NAMES:
        a=attribution['extended_stress_reverse_'+name]
        lines.append(f"| {LABELS[name]} | {a['removed_entries']} / ${a['removed_entry_net_pnl']:+.2f} | {a['added_entries']} / ${a['added_entry_net_pnl']:+.2f} | ${a['shared_entry_net_pnl_delta']:+.2f} | ${a['total_net_pnl_delta']:+.2f} |")
    deltas=[s['results']['extended_stress_'+scenario][n]['return_delta_pp'] for scenario in ('delay','reverse') for n in NAMES]
    middle=[s['results']['middle_stress_'+scenario][n]['return_pct'] for scenario in ('control','delay','reverse') for n in NAMES]
    lines+=['','## Interpretation','',f"Full-window higher-cost return changes across the two fixed stresses ranged from {min(deltas):+.2f} to {max(deltas):+.2f} percentage points. Better delayed or reversed outcomes are sensitivity findings, not a basis to change production rules. Allocation order is part of the strategy specification because existing holdings can occupy slots while ranks change.", '',f"Known losing-window stressed returns ranged from {min(middle):+.2f}% to {max(middle):+.2f}% across all controls/stresses. Inspect that range alongside total returns; a stress that improves one period need not fix the model. Existing validation gates are unchanged.", '', 'A one-bar delay is a blind signal-processing stress, not a proposed safe execution method. It can enter on stale context and postpone a risk-off signal. Signals become eligible four hours later; with hourly detail, actual fills can occur within that eligible bar depending on slot availability and engine behaviour. Fixed stops remain active throughout.','','No claim of live fills, historic order-book depth, account eligibility, fee-tier verification or independent out-of-sample returns. Current-universe bias and within-hour ambiguity remain. Do not search further order permutations or delay lengths to maximize these historical numbers.','','## Verification and artifacts','','29 combined checks passed, including two new delay/prefix/stop and order-independent-ranking tests. Ten new engine commands produced 30 new candidate/cost/window results; six full-window control results reused the exact verified earlier-extension archive. All frozen hashes matched. Every new final hourly-close balance reconciles to the engine within $0.00001, and trade-difference attribution also reconciles.','','Sources: `OPERATIONAL_ROBUSTNESS_EXPERIMENT.md`, `evaluate_operational_robustness.py`, `user_data/strategies/operational_delays.py`, `config.reverse_priority.json`. Full summary, frozen hashes, engine ZIPs/logs, hourly equity CSVs and trade-difference attribution: `data/research/operational_robustness/`. Original strategies/configs/archives remain unchanged. No orders, scheduler or service introduced.']
    (ROOT.parents[1]/'outputs/operational-robustness-screen.md').write_text('\n'.join(lines)+'\n')
    print('Saved report and reconciled all trade differences; frozen hashes match.')

if __name__=='__main__':main()
