"""Post-hoc attribution of frozen runs; never rewrites original results."""
import json
import zipfile
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/relative_strength_diagnostics'

def analyze(experiment="relative_strength", strategy="RegimeRelativeStrength"):
    global OUT
    OUT=ROOT/"data/research"/(experiment+"_diagnostics")
    OUT.mkdir(parents=True,exist_ok=True)
    summary=json.loads((ROOT/'data/research'/experiment/'summary.json').read_text())
    frames={p:pd.read_feather(ROOT/'user_data/data/okx'/(p.replace('/','_')+'-4h.feather')).set_index('date') for p in json.loads((ROOT/'config.research.json').read_text())['exchange']['pair_whitelist']}
    btc=frames['BTC/USDT']['close']
    breadth=pd.concat({p:f['close'].gt(f['close'].rolling(50).mean()) for p,f in frames.items()},axis=1).mean(axis=1)
    context=pd.DataFrame({'btc_30bar_return':btc.pct_change(30),'btc_sma200_distance':btc/btc.rolling(200).mean()-1,'btc_sma200_rising':btc.rolling(200).mean().diff(6).gt(0),'breadth_above_sma50':breadth})
    all_trades=[]; stats={}
    for key,result in summary['results'].items():
        with zipfile.ZipFile(ROOT/result[strategy]['source_archive']) as z:
            d=next(json.loads(z.read(n)) for n in z.namelist() if n.endswith('.json') and '_config' not in n)['strategy'][strategy]
        t=pd.DataFrame(d['trades']); t['run']=key
        for c in ['open_date','close_date']: t[c]=pd.to_datetime(t[c],utc=True)
        t['signal_date']=t['open_date']-pd.Timedelta(hours=4)
        t=t.join(context,on='signal_date'); t['realized_month']=t['close_date'].dt.strftime('%Y-%m')
        t['gross_price_pnl']=t['amount']*(t['close_rate']-t['open_rate'])
        t['fee_proxy_paid']=t['amount']*(t['open_rate']*t['fee_open']+t['close_rate']*t['fee_close'])
        assert abs(t.profit_abs.sum()-d['profit_total_abs'])<1e-5
        assert (t.gross_price_pnl-t.fee_proxy_paid-t.profit_abs).abs().max()<1e-5
        coins=t.groupby('pair').agg(trades=('pair','size'),net_profit=('profit_abs','sum'),gross_price_pnl=('gross_price_pnl','sum'),fee_proxy_paid=('fee_proxy_paid','sum')).sort_values('net_profit',ascending=False)
        months=t.groupby('realized_month').agg(trades=('pair','size'),net_profit=('profit_abs','sum'))
        exits=t.groupby('exit_reason').agg(trades=('pair','size'),net_profit=('profit_abs','sum'))
        cohorts={}
        for name,mask in [('breadth_over_half',t.breadth_above_sma50>.5),('breadth_half_or_lower',t.breadth_above_sma50<=.5),('btc_sma200_rising',t.btc_sma200_rising.eq(True)),('btc_sma200_not_rising',t.btc_sma200_rising.eq(False))]:
            a=t[mask]; cohorts[name]={'trades':len(a),'net_profit':float(a.profit_abs.sum()),'mean_trade_return_pct':float(a.profit_ratio.mean()*100) if len(a) else None}
        top=t.nlargest(5,'profit_abs')
        stats[key]={'net_profit':float(t.profit_abs.sum()),'gross_price_pnl':float(t.gross_price_pnl.sum()),'fee_proxy_paid':float(t.fee_proxy_paid.sum()),'trades':len(t),'median_holding_hours':float(t.trade_duration.median()/60),'short_trades_under_24h':int(t.trade_duration.lt(1440).sum()),'short_trades_net_profit':float(t.loc[t.trade_duration.lt(1440),'profit_abs'].sum()),'positive_coins':int(coins.net_profit.gt(0).sum()),'positive_realized_months':int(months.net_profit.gt(0).sum()),'realized_months':len(months),'top5_trades_net_profit':float(top.profit_abs.sum()),'net_without_top5_trades_arithmetic':float(t.profit_abs.sum()-top.profit_abs.sum()),'top3_coins_net_profit':float(coins.net_profit.head(3).sum()),'coins':coins.reset_index().to_dict('records'),'months':months.reset_index().to_dict('records'),'exits':exits.reset_index().to_dict('records'),'entry_context_cohorts':cohorts}
        coins.to_csv(OUT/f'{key}_coins.csv'); months.to_csv(OUT/f'{key}_realized_months.csv'); all_trades.append(t.drop(columns=['orders']))
    pd.concat(all_trades,ignore_index=True).to_csv(OUT/'trades_with_entry_context.csv',index=False)
    (OUT/'summary.json').write_text(json.dumps(stats,indent=2))
    print(json.dumps({k:{a:b for a,b in v.items() if a not in ['coins','months','exits']} for k,v in stats.items()},indent=2))
    return stats
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiment',default='relative_strength')
    parser.add_argument('--strategy',default='RegimeRelativeStrength')
    args=parser.parse_args()
    analyze(args.experiment,args.strategy)
