"""Independent hourly-close accounting from the frozen simulated trade ledger."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluate_research import ROOT,drawdown
from evaluate_low_exposure import extract,NAMES


def hourly_equity(trades,prices,initial=1000.):
    index=next(iter(prices.values())).index
    if not index.is_unique or not index.is_monotonic_increasing:raise ValueError('Invalid price index')
    cash_changes=np.zeros(len(index));holdings_value=np.zeros(len(index))
    for t in trades:
        start=pd.Timestamp(t['open_date']);end=pd.Timestamp(t['close_date'])
        if start not in index or end not in index:raise ValueError('Trade timestamp outside hourly grid')
        i=index.get_loc(start);j=index.get_loc(end)
        if j<i:raise ValueError('Exit before entry')
        cash_changes[i]-=t['amount']*t['open_rate']*(1+t['fee_open'])
        cash_changes[j]+=t['amount']*t['close_rate']*(1-t['fee_close'])
        if j>i:
            marks=prices[t['pair']].reindex(index[i:j])
            if not np.isfinite(marks).all() or (marks<=0).any():raise ValueError('Missing/invalid active hourly price')
            holdings_value[i:j]+=t['amount']*marks.to_numpy()
    cash=initial+cash_changes.cumsum()
    return pd.DataFrame({'cash':cash,'holdings_value':holdings_value,'equity':cash+holdings_value},index=index)


def main():
    out=ROOT/'data/research/hourly_execution_check'
    s=json.loads((out/'summary.json').read_text())
    config=json.loads((ROOT/'config.research.json').read_text())
    prices={p:pd.read_feather(ROOT/'user_data/data/okx'/(p.replace('/','_')+'-1h.feather')).set_index('date')['close']
            for p in config['exchange']['pair_whitelist']}
    results={}
    for cost in ('base','stress'):
        results[cost]={}
        for name in NAMES:
            a=s['results'][cost][name];d,_=extract(ROOT/a['source_archive'],name)
            e=hourly_equity(d['trades'],prices)
            if abs(e.equity.iloc[-1]-a['final_balance'])>1e-5:raise ValueError('Hourly ledger does not reconcile')
            results[cost][name]={'hourly_close_drawdown_pct':drawdown(e.equity)*100,
                                'engine_four_hour_open_drawdown_pct':a['marked_wallet_drawdown_pct'],
                                'minimum_cash':float(e.cash.min()),'final_equity':float(e.equity.iloc[-1]),
                                'final_equity_difference_from_engine':float(e.equity.iloc[-1]-a['final_balance'])}
            e.index.name='hour_open_utc'
            e.to_csv(out/f'{cost}_{name}_hourly_close_equity.csv')
    (out/'hourly_close_audit.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
