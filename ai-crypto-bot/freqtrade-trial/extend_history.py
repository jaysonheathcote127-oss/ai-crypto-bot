"""Separate earlier source collection and verified merge; never overwrite originals."""
import asyncio
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import ccxt.async_support as ccxt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/history_extension'
EARLY=OUT/'earlier_source';MERGED=OUT/'merged_data'
START=pd.Timestamp('2023-07-01',tz='UTC');END=pd.Timestamp('2024-10-01',tz='UTC')


def validate(frame,start,end,hours):
    expected=pd.date_range(start,end,freq=f'{hours}h',inclusive='left')
    if not pd.DatetimeIndex(frame.date).as_unit('ms').equals(expected.as_unit('ms')):
        raise ValueError('Missing/duplicate/unordered or incomplete history')
    n=frame[['open','high','low','close','volume']]
    if not np.isfinite(n.to_numpy()).all() or (frame.volume<0).any() or (frame[['open','high','low','close']]<=0).any().any():
        raise ValueError('Invalid historical prices or volume')
    if (frame.high<frame[['open','close','low']].max(axis=1)).any() or (frame.low>frame[['open','close','high']].min(axis=1)).any():
        raise ValueError('Invalid OHLC ordering')


def merge_verified(early,later,hours):
    a=early.set_index('date');b=later.set_index('date')
    overlap=a.index.intersection(b.index)
    if len(overlap) and not np.isclose(a.loc[overlap].to_numpy(),b.loc[overlap].to_numpy(),rtol=1e-5,atol=1e-10).all():
        raise ValueError('Earlier/later source revision in overlap; merge blocked')
    merged=pd.concat([early,later[later.date>early.date.iloc[-1]]],ignore_index=True)
    validate(merged,START,pd.Timestamp('2026-10-19',tz='UTC'),hours)
    return merged,len(overlap)


def aggregation(earlier):
    h=earlier['1h'].set_index('date').resample('4h').agg({'open':'first','high':'max','low':'min','close':'last'})
    f=earlier['4h'].set_index('date')
    if not h.index.equals(f.index):raise ValueError('Hourly aggregation coverage mismatch')
    mismatch={c:int((~np.isclose(h[c],f[c],rtol=1e-5,atol=1e-10)).sum()) for c in h.columns}
    if any(mismatch.values()):raise ValueError('Earlier hourly/four-hour OHLC mismatch: '+str(mismatch))
    return mismatch


async def main():
    EARLY.mkdir(parents=True,exist_ok=True);MERGED.mkdir(parents=True,exist_ok=True)
    paths=['HISTORY_EXTENSION_EXPERIMENT.md','extend_history.py','config.research.json']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    freeze=OUT/'download_frozen_inputs.json'
    if freeze.exists():
        if json.loads(freeze.read_text())!=hashes:raise ValueError('Frozen download source drift')
    else:freeze.write_text(json.dumps(hashes,indent=2))
    pairs=json.loads((ROOT/'config.research.json').read_text())['exchange']['pair_whitelist']
    ex=ccxt.okx({'enableRateLimit':True,'timeout':20000});sem=asyncio.Semaphore(3);records={}
    async def fetch(pair):
        async with sem:
            record={};earlier={}
            try:
                for tf,hours in [('4h',4),('1h',1)]:
                    name=pair.replace('/','_')+'-'+tf+'.feather';path=EARLY/name
                    if path.exists():f=pd.read_feather(path);validate(f,START,END,hours)
                    else:
                        cursor=int(START.timestamp()*1000);end=int(END.timestamp()*1000);step=hours*3600000;rows=[];calls=0
                        while cursor<end:
                            batch=None
                            for retry in range(3):
                                try:
                                    batch=await ex.fetch_ohlcv(pair,tf,since=cursor,limit=300,params={'type':'HistoryCandles'});break
                                except ccxt.NetworkError:
                                    if retry==2:raise
                                    await asyncio.sleep(retry+1)
                            if not batch:raise ValueError('Missing history at required date')
                            rows.extend(r for r in batch if cursor<=r[0]<end)
                            nxt=max(r[0] for r in batch)+step
                            if nxt<=cursor:raise ValueError('Pagination stalled')
                            cursor=nxt;calls+=1
                            if calls>150:raise ValueError('Page safety limit')
                        f=pd.DataFrame(rows,columns=['date','open','high','low','close','volume'])
                        f['date']=pd.to_datetime(f.date,unit='ms',utc=True);validate(f,START,END,hours)
                        f.to_feather(path)
                    earlier[tf]=f
                    record[tf]={'candles':len(f),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                record['aggregation_mismatches']=aggregation(earlier)
                for tf,hours in [('4h',4),('1h',1)]:
                    name=pair.replace('/','_')+'-'+tf+'.feather'
                    later=pd.read_feather(ROOT/'user_data/data/okx'/name)
                    merged,overlap=merge_verified(earlier[tf],later,hours)
                    destination=MERGED/name
                    if destination.exists():
                        existing=pd.read_feather(destination)
                        if not existing.equals(merged):raise ValueError('Existing merged dataset differs')
                    else:merged.to_feather(destination)
                    record[tf].update(merged_candles=len(merged),overlap_candles=overlap,
                                      merged_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
                record['status']='complete'
            except Exception as e:record.update(status='failed',error=str(e))
            records[pair]=record
            print(pair,json.dumps(record),flush=True)
            (OUT/'download_progress.json').write_text(json.dumps(records,indent=2))
    try:
        await ex.load_markets();await asyncio.gather(*(fetch(p) for p in pairs))
    finally:await ex.close()
    (OUT/'data_manifest.json').write_text(json.dumps({'earlier_start':START.isoformat(),'earlier_end_exclusive':END.isoformat(),'assets':records},indent=2))
    if len(records)!=len(pairs) or any(v['status']!='complete' for v in records.values()):raise SystemExit('Incomplete fixed-universe data; backtest blocked')

if __name__=='__main__':asyncio.run(main())
