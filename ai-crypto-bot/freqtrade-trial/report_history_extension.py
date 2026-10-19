"""Readable earlier-history report plus descriptive trade attribution."""
import hashlib
import json
import pandas as pd
from evaluate_research import ROOT
from evaluate_low_exposure import extract,NAMES
OUT=ROOT/'data/research/history_extension'
LABELS={'DailyRelativeStrength':'Daily control','DailyAbsoluteMomentum':'Daily positive momentum','DailySlowMomentum':'Daily slower positive momentum'}


def main():
    s=json.loads((OUT/'summary.json').read_text());manifest=json.loads((OUT/'data_manifest.json').read_text())
    for path,h in s['hashes'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input drift: '+path)
    attribution={}
    for key,items in s['results'].items():
        attribution[key]={}
        for name,a in items.items():
            d,_=extract(ROOT/a['source_archive'],name);t=pd.DataFrame(d['trades'])
            if abs(t.profit_abs.sum()-a['profit'])>1e-5:raise ValueError('Attribution profit mismatch')
            t['exit_month']=pd.to_datetime(t.close_date,utc=True).dt.strftime('%Y-%m')
            coins=t.groupby('pair').agg(trades=('pair','size'),net_profit=('profit_abs','sum')).sort_values('net_profit',ascending=False)
            months=t.groupby('exit_month').agg(trades=('pair','size'),net_profit=('profit_abs','sum'))
            fees=(t.amount*(t.open_rate*t.fee_open+t.close_rate*t.fee_close)).sum()
            gross=(t.amount*(t.close_rate-t.open_rate)).sum()
            if abs(gross-fees-t.profit_abs.sum())>1e-5:raise ValueError('Fee reconciliation failed')
            attribution[key][name]={'net_profit':float(t.profit_abs.sum()),'gross_price_pnl':float(gross),
                                    'fee_proxy_paid':float(fees),'positive_coins':int(coins.net_profit.gt(0).sum()),
                                    'top_five_trades_profit':float(t.nlargest(5,'profit_abs').profit_abs.sum()),
                                    'coins':coins.reset_index().to_dict('records'),'exit_months':months.reset_index().to_dict('records')}
            coins.to_csv(OUT/(key+'_'+name+'_coins.csv'));months.to_csv(OUT/(key+'_'+name+'_exit_months.csv'))
    (OUT/'attribution.json').write_text(json.dumps(attribution,indent=2))
    lines=['# Earlier-history extension — 19 October 2026','','No strategy rules or coin selections changed. All three daily specifications were tested with $25 simulated entries, a $1,000 wallet, five maximum holdings, unchanged 10% stop, four-hour signals and hourly execution. Costs remain 0.15%/0.45% per side, including a fee-equivalent adverse-cost proxy. No promotion or real orders.','','## Earlier year: October 2023–September 2024','','July–September 2023 was indicator warmup. This year predates the strongest previously inspected rally. It was newly added to our calculations, but the decision to extend follows later-result inspection and uses today-selected survivors. It is an earlier-history robustness check, not an untouched holdout or forward test.','','| Specification | Trades | Base return | Stress return | Hourly-close base drawdown | Hourly-close stress drawdown |','|---|---:|---:|---:|---:|---:|']
    for name in NAMES:
        a=s['results']['earlier_year_base'][name];b=s['results']['earlier_year_stress'][name]
        lines.append(f"| {LABELS[name]} | {a['trades']} | {a['return_pct']:+.2f}% | {b['return_pct']:+.2f}% | {a['hourly_close_drawdown_pct']:.2f}% | {b['hourly_close_drawdown_pct']:.2f}% |")
    lines+=['','## Extended continuous wallet: October 2023–18 October 2026','','One wallet throughout, without year/segment resets. Returns are cumulative over approximately three years, not annual returns. The earlier and extended tests share data and are not independent samples.','','| Specification | Trades | Base return | Stress return | Hourly-close base drawdown | Hourly-close stress drawdown |','|---|---:|---:|---:|---:|---:|']
    for name in NAMES:
        a=s['results']['extended_continuous_base'][name];b=s['results']['extended_continuous_stress'][name]
        lines.append(f"| {LABELS[name]} | {a['trades']} | {a['return_pct']:+.2f}% | {b['return_pct']:+.2f}% | {a['hourly_close_drawdown_pct']:.2f}% | {b['hourly_close_drawdown_pct']:.2f}% |")
    lines+=['','## Passive references at comparable initial allocation','','Buy-and-hold starts 12.5% invested and 87.5% cash, matching five initial $25 strategy stakes in a $1,000 wallet. Strategy exposure varies and these are not volatility-matched. Fractional passive positions ignore individual minimum order sizes. These references include assumed entry/exit costs. Cash return is 0%. Cells show higher-cost return / hourly-close drawdown.','','| Period | BTC holding | Equal-weight holding |','|---|---:|---:|']
    for period,label in [('earlier_year','Earlier year'),('extended_continuous','Extended continuous')]:
        refs=s['benchmarks'][period+'_stress']; vals=[]
        for key in ('BTC_12.5pct_invested','equal_weight_12.5pct_invested'):
            r=refs[key];vals.append(f"{r['return_pct']:+.2f}% / {r['hourly_close_drawdown_pct']:.2f}%")
        lines.append('| '+label+' | '+' | '.join(vals)+' |')
    lines+=['','## Earlier-year attribution under higher costs','','| Specification | Net P&L | Gross price P&L | Cost deductions | Positive coins | Five largest winners |','|---|---:|---:|---:|---:|---:|']
    for name in NAMES:
        a=attribution['earlier_year_stress'][name]
        lines.append(f"| {LABELS[name]} | ${a['net_profit']:+.2f} | ${a['gross_price_pnl']:+.2f} | ${a['fee_proxy_paid']:.2f} | {a['positive_coins']}/17 | ${a['top_five_trades_profit']:+.2f} |")
    lines+=['','Largest-winner sums describe concentration, not a simulation without those trades. Exit-month attribution is separate from marked monthly returns; winners can span multiple months. Coins and trades share market conditions and are not independent observations.','','## Verification and limits','','All 17 pairs had complete earlier history: 2,748 four-hour bars and 10,992 hourly bars each. No gaps, market exclusions or date changes. Reconstructed earlier hourly OHLC matches four-hour source within rtol=1e-5. The 552-bar overlap per pair agrees with original four-hour history, including volume within that tolerance. Original datasets/configs were preserved; merged data is isolated under this experiment.','','27 combined unit checks passed, including three extension checks for coverage/aggregation, rejecting revised overlaps without mutating input, and charging both sides of passive benchmark fees. Four engine commands produced 12 strategy/cost/period results. Frozen hashes rechecked; trade profits/fees and independent hourly-close final balances reconcile. Earlier force exits and samples are retained in summary JSON.','','Hourly-close equity uses recorded execution-hour events and closing marks, recognizing entry/exit fees. It omits within-hour extremes and actual order-book fills. Engine exported wallet marks use four-hour opening prices; those measures are stored separately. No claim of a routine single-pair Freqtrade lookahead pass for a cross-sectional strategy.','','## Interpretation','','All three earlier-year stressed results were positive, so profitability is not confined to the previously inspected late-2024 rally. However, BTC holding at the same 12.5% initial allocation returned +16.60% in the earlier year, more than the strategies’ +5.01% to +7.56%, with 9.03% drawdown versus their 6.16% to 7.43%. The tradeoff includes lower exposure over time and different risk, not clear benchmark dominance.','','Across the extended continuous window, BTC returned +25.23% with 21.46% drawdown; the strategies returned +14.09% to +19.42% with 12.77% to 14.04% drawdown. The active rules reduced historical drawdown but also gave up some BTC return. These are not volatility-matched comparisons.','','Earlier-year profits remain concentrated: the five largest winners exceed total net P&L for all three versions, and only eight or nine of 17 coins were profitable under stress. That is descriptive evidence about a tail-dependent momentum payoff, not a reason to select those past winners.','','## Decision','','This extension adds evidence about another historical period; it does not erase the losing October 2025–March 2026 segment, remove current-universe survivorship bias, validate income reliability, or authorize promotion. All three specifications remain exploratory references. Keep rules/results frozen; do not select a coin/horizon retrospectively or change rejection thresholds to fit these totals. Genuinely subsequent observations remain necessary.','','Artifacts: `HISTORY_EXTENSION_EXPERIMENT.md`, `extend_history.py`, `evaluate_history_extension.py`, `report_history_extension.py`, and `data/research/history_extension/` (separate raw/merged data, manifests/hashes, engine archives/logs, independent equity CSVs, benchmarks and attribution). No automatic collection/trading service was installed.']
    (ROOT.parents[1]/'outputs/history-extension-screen.md').write_text('\n'.join(lines)+'\n')
    print('Earlier-history report and attribution saved; hashes and accounting verified.')

if __name__=='__main__':main()
