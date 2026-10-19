"""Bounded public hourly-data collection and continuity/aggregation checks."""
import asyncio
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import ccxt.async_support as ccxt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/hourly_detail'
START=pd.Timestamp('2024-10-01',tz='UTC'); END=pd.Timestamp('2026-10-19',tz='UTC')


def validate(frame):
    expected=pd.date_range(START,END,freq='1h',inclusive='left')
    if not pd.DatetimeIndex(frame.date).equals(expected):
        raise ValueError('Missing/duplicate/unordered or incomplete hourly history')
    n=frame[['open','high','low','close','volume']]
    if not np.isfinite(n.to_numpy()).all() or (frame.volume<0).any() or (frame[['open','high','low','close']]<=0).any().any():
        raise ValueError('Invalid hourly prices/volume')
    if (frame.high<frame[['open','close','low']].max(axis=1)).any() or (frame.low>frame[['open','close','high']].min(axis=1)).any():
        raise ValueError('Invalid hourly OHLC order')


def aggregate_check(frame,pair):
    hourly=frame.set_index('date').resample('4h').agg({'open':'first','high':'max','low':'min','close':'last'})
    original=pd.read_feather(ROOT/'user_data/data/okx'/(pair.replace('/','_')+'-4h.feather')).set_index('date')
    original=original.reindex(hourly.index)
    diffs={c:int((~np.isclose(hourly[c],original[c],rtol=1e-5,atol=1e-10)).sum()) for c in ['open','high','low','close']}
    return {'mismatched_four_hour_values':diffs,'rows':len(hourly)}


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frozen=OUT/'download_frozen_inputs.json'
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['INTRABAR_EXECUTION_EXPERIMENT.md','download_hourly_detail.py','config.research.json']}
    if frozen.exists():
        if json.loads(frozen.read_text())!=hashes: raise ValueError('Downloader source drift')
    else:
        frozen.write_text(json.dumps(hashes,indent=2))
    pairs=json.loads((ROOT/'config.research.json').read_text())['exchange']['pair_whitelist']
    ex=ccxt.okx({'enableRateLimit':True,'timeout':20000})
    semaphore=asyncio.Semaphore(3); results={}
    async def fetch(pair):
        async with semaphore:
            destination=ROOT/'user_data/data/okx'/(pair.replace('/','_')+'-1h.feather')
            try:
                if destination.exists():
                    frame=pd.read_feather(destination);validate(frame)
                else:
                    cursor=int(START.timestamp()*1000);end=int(END.timestamp()*1000); rows=[]; calls=0
                    while cursor<end:
                        batch=await ex.fetch_ohlcv(pair,'1h',since=cursor,limit=300)
                        calls+=1
                        if not batch: raise ValueError('Empty hourly page')
                        selected=[r for r in batch if cursor<=r[0]<end]
                        rows.extend(selected)
                        next_cursor=max(r[0] for r in batch)+3600000
                        if next_cursor<=cursor: raise ValueError('Pagination made no progress')
                        cursor=next_cursor
                        if calls%30==0: print(pair,'pages',calls,'through',pd.Timestamp(cursor,unit='ms',tz='UTC').isoformat(),flush=True)
                        if calls>250: raise ValueError('Hourly page safety limit reached')
                    frame=pd.DataFrame(rows,columns=['date','open','high','low','close','volume'])
                    frame['date']=pd.to_datetime(frame.date,unit='ms',utc=True)
                    validate(frame)
                    temporary=OUT/(pair.replace('/','_')+'.feather')
                    frame.to_feather(temporary);temporary.rename(destination)
                results[pair]={'status':'complete','candles':len(frame),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),**aggregate_check(frame,pair)}
                print(pair,'complete',results[pair],flush=True)
            except Exception as error:
                results[pair]={'status':'failed','error':str(error)}
                print(pair,'FAILED',str(error),flush=True)
            (OUT/'progress.json').write_text(json.dumps(results,indent=2))
    try:
        await ex.load_markets()
        await asyncio.gather(*(fetch(p) for p in pairs))
    finally: await ex.close()
    (OUT/'manifest.json').write_text(json.dumps({'start':START.isoformat(),'end_exclusive':END.isoformat(),'assets':results},indent=2))
    if any(v['status']!='complete' for v in results.values()) or len(results)!=len(pairs): raise SystemExit('Hourly data incomplete; do not run detail backtest')

if __name__=='__main__':asyncio.run(main())
