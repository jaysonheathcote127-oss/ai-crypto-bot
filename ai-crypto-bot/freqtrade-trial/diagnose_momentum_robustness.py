"""Continuous equity, fixed exposure scenarios and reproducible research report."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
import pandas as pd
from evaluate_research import drawdown
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/momentum_robustness'
NAMES={'RegimeRelativeStrength':'Four-hour decisions','DailyRelativeStrength':'Daily decisions',
       'DailyAbsoluteMomentum':'Daily positive momentum','DailySlowMomentum':'Daily slower positive momentum'}


def main():
    s=json.loads((OUT/'summary.json').read_text())
    for p,h in s['hashes'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:
            raise ValueError('Frozen source or data changed: '+p)
    scenarios={}; monthly=[]
    for cost in ('base','stress'):
        scenarios[cost]={}
        for name,a in s['results']['continuous_'+cost].items():
            with zipfile.ZipFile(ROOT/a['source_archive']) as z:
                w=pd.read_feather(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('_'+name+'_wallet.feather')))))
                stats=next(json.loads(z.read(n)) for n in z.namelist() if n.endswith('.json') and '_config' not in n)['strategy'][name]
            t=pd.DataFrame(stats['trades'])
            if abs(t.profit_abs.sum()-a['profit'])>1e-5: raise ValueError('Profit sum mismatch')
            e=w.groupby('date').total_quote.sum().sort_index()
            e=pd.concat([e,pd.Series([a['final_balance']],index=[e.index[-1]+pd.Timedelta(seconds=1)])])
            e.to_csv(OUT/f'continuous_{cost}_{name}_equity.csv',header=['equity_usdt'])
            m=e.resample('ME').last()
            prior=m.shift(1);prior.iloc[0]=1000
            for when,ending in m.items():
                monthly.append({'strategy':name,'cost':cost,'month':when.strftime('%Y-%m'),'ending_equity':ending,
                                'net_change':ending-prior.loc[when],'return_pct':(ending/prior.loc[when]-1)*100})
            scenarios[cost][name]={}
            for fraction in (1.,.5,.25):
                scaled=1000+fraction*(e-1000)
                scenarios[cost][name][str(fraction)]={'arithmetic_return_pct':a['return_pct']*fraction,
                            'marked_drawdown_pct':drawdown(scaled)*100}
    (OUT/'exposure_scenarios.json').write_text(json.dumps(scenarios,indent=2))
    pd.DataFrame(monthly).to_csv(OUT/'continuous_monthly_marked_returns.csv',index=False)
    lines=['# Momentum robustness and continuous-wallet results','','19 October 2026. **No candidate qualifies for promotion.** Every historical period is already inspected. This is a bounded screen of two new hypotheses, not an out-of-sample demonstration.','','## What was tested','','Daily positive momentum adds a positive 30-bar return entry requirement and a daily exit at nonpositive momentum. The slower version uses 120 bars (20 days) for momentum/ranking instead of 30 bars (five days). Other indicators stay four-hour; entries and rank/own-SMA/momentum decisions are daily. BTC risk-off/missing-data exits remain every four hours. Same 17 pairs, $100 stakes, $1,000 wallet, five holdings, 10% stop, no leverage.','','No threshold sweep or new best-coin selection. Both hypotheses were recorded before these runs. The positive-momentum version was not selected as a trading strategy based on its highest historical total.','','## Separate period results','','Each segment begins with a fresh wallet. Return cells show base / higher-cost stress. Drawdown cells show marked wallet base / stress.','','| Candidate | Period | Trades | Net return | Drawdown |','|---|---|---:|---:|---:|']
    for p,label in [('development','Early'),('validation','Middle'),('holdout','Recent')]:
        for name in ('DailyAbsoluteMomentum','DailySlowMomentum'):
            a=s['results'][p+'_base'][name];b=s['results'][p+'_stress'][name]
            lines.append(f"| {NAMES[name]} | {label} | {a['trades']} | {a['return_pct']:+.2f}% / {b['return_pct']:+.2f}% | {a['marked_wallet_drawdown_pct']:.2f}% / {b['marked_wallet_drawdown_pct']:.2f}% |")
    lines+=['','Both lose in the middle segment at both costs, so neither passes existing positive-validation requirements. Early and recent stressed drawdowns also exceed 15%. The slower horizon reduces trades but does not remove the losing regime.','','## One continuous wallet','','1 October 2024 through 18 October 2026, without segment liquidations or resets. Fixed-dollar stakes, not constant-weight rebalancing. These actual engine runs are more informative than compounding the separately reset segments.','','| Specification | Trades | Base return | Stress return | Base drawdown | Stress drawdown |','|---|---:|---:|---:|---:|---:|']
    for name in NAMES:
        a=s['results']['continuous_base'][name];b=s['results']['continuous_stress'][name]
        lines.append(f"| {NAMES[name]} | {a['trades']} | {a['return_pct']:+.2f}% | {b['return_pct']:+.2f}% | {a['marked_wallet_drawdown_pct']:.2f}% | {b['marked_wallet_drawdown_pct']:.2f}% |")
    lines+=['','Continuous stressed passive references: 50% BTC / 50% cash returned +14.25%, with 35.46% marked drawdown; 50% equal-weight / 50% cash returned +4.20%, with 49.94% drawdown. Cash returned 0%. Strategy exposure varies and these comparisons are not volatility matched. All use today-selected assets; benchmark comparisons cannot remove that bias.','','The daily versions show a positive full-period result even under stress. However, the full-period total combines early gains with later losses; it does not eliminate the failed middle-period screen or establish future income. Four-hour-decision control loses under continuous stress.','','## Exposure arithmetic: risk reduction is not signal repair','','The protocol specified half-exposure arithmetic. An additional post-hoc quarter-exposure illustration is included explicitly as sensitivity, not an optimized sizing rule or a new candidate. Each scenario uses E_scaled=1000+fraction*(E_original-1000), including final settlement. It is not an execution backtest; exchange minimums, rounding, capacity and execution differences could matter. Smaller allocation cannot change the sign of a losing period.','','| Daily specification | Full stress return / drawdown | Half-exposure stress return / drawdown | Quarter-exposure stress return / drawdown |','|---|---:|---:|---:|']
    for name in list(NAMES)[1:]:
        vals=[]
        for f in ('1.0','0.5','0.25'):
            a=scenarios['stress'][name][f]; vals.append(f"{a['arithmetic_return_pct']:+.2f}% / {a['marked_drawdown_pct']:.2f}%")
        lines.append('| '+NAMES[name]+' | '+' | '.join(vals)+' |')
    lines+=['','Quarter exposure corresponds approximately to $25 rather than $100 entries, with at most $125 initial deployment in five positions. These smaller-allocation returns are not directly comparable to a 50%-invested passive benchmark. Passing a full-window drawdown scenario does not override segment losses or provide forward evidence.','','## Verification','','21 combined unit checks passed, including integrated full-universe truncated-history versus future-shocked indicators/signals, exact momentum horizons, invalid prices, daily schedules, and read-only observer synchronization/unfinished-candle checks. Eight engine commands produced 20 strategy/cost/period combinations: 12 new segmented results plus eight continuous controls/candidates. Frozen source/data hashes matched after execution; continuous trade profits reconcile to engine totals.','','No full single-pair Freqtrade lookahead pass is claimed: its documented equivalence assumption does not hold for cross-sectional ranking. [Official lookahead-analysis limitations](https://www.freqtrade.io/en/stable/lookahead-analysis/). Integrated prefix tests are useful evidence, not a complete proof. No historic order-book fills, intrabar paths or USDT depeg modelling. Costs remain assumed 0.15%/0.45% each side with a fee-equivalent adverse proxy.','','## Next evidence: fixed-universe observation','','A one-shot read-only observer records all four specifications with current candles/quotes, synchronization, source hashes and immutable raw inputs. Missing one market blocks the full ranking. First attempt correctly blocked because OKX capped candles at 300; v2 uses supported pagination and retains a separate manifest. Baseline bars predating the frozen forward start are labelled baseline_only. This is signal observation, not a paper portfolio or trading deployment; no automatic scheduler is installed. See `FORWARD_OBSERVATION.md` and the separate observation status report.','','## Artifacts','','Protocol: `MOMENTUM_ROBUSTNESS_EXPERIMENT.md`; strategies: `user_data/strategies/absolute_momentum.py`; evaluator: `evaluate_momentum_robustness.py`. Summary, frozen hashes, original engine ZIPs/logs, equity CSVs, monthly marked returns and exposure scenarios: `data/research/momentum_robustness/`. Diagnostics/report generator: `diagnose_momentum_robustness.py`.']
    (ROOT.parents[1]/'outputs/momentum-robustness-screen.md').write_text('\n'.join(lines)+'\n')
    print('Wrote report, equity/monthly CSVs and exposure scenarios; frozen hashes verified.')

if __name__=='__main__': main()
