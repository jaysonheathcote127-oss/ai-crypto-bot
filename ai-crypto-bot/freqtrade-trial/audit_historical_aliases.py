"""Public archive recovery and alias probes, kept separate from trading results."""
import asyncio
import hashlib
import io
import json
import urllib.request
import zipfile
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import ccxt.async_support as ccxt
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/historical_alias_followup'


def archive_probe(month):
    name='MATICUSDT-4h-'+month+'.zip'
    url='https://data.binance.vision/data/spot/monthly/klines/MATICUSDT/4h/'+name
    try:
        with urllib.request.urlopen(url,timeout=30) as r:blob=r.read()
        with urllib.request.urlopen(url+'.CHECKSUM',timeout=30) as r:checksum=r.read()
        published=checksum.decode().split()[0];actual=hashlib.sha256(blob).hexdigest()
        if published!=actual:raise ValueError('Published SHA256 mismatch')
        (OUT/name).write_bytes(blob);(OUT/(name+'.CHECKSUM')).write_bytes(checksum)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            members=z.namelist()
            if len(members)!=1:raise ValueError('Unexpected archive members')
            csv=z.read(members[0]);(OUT/(name+'.csv')).write_bytes(csv)
        f=pd.read_csv(io.BytesIO(csv),header=None)
        if f.shape[1]!=12:raise ValueError('Unexpected Binance spot kline schema')
        f=f.apply(pd.to_numeric,errors='raise')
        if not np.isfinite(f.to_numpy()).all():raise ValueError('Nonfinite archive data')
        unit='us' if int(f.iloc[0,0])>10**14 else 'ms'
        dates=pd.to_datetime(f[0],unit=unit,utc=True)
        if not dates.is_unique or not dates.diff().iloc[1:].eq(pd.Timedelta(hours=4)).all():raise ValueError('Archive timestamp discontinuity')
        o,h,l,c=f[1],f[2],f[3],f[4]
        if (f[[1,2,3,4]]<=0).any().any() or (f[5]<0).any() or (h<pd.concat([o,l,c],axis=1).max(axis=1)).any() or (l>pd.concat([o,h,c],axis=1).min(axis=1)).any():raise ValueError('Invalid archive OHLC/volume')
        close_dates=pd.to_datetime(f[6],unit=unit,utc=True)
        tick=pd.Timedelta(microseconds=1) if unit=='us' else pd.Timedelta(milliseconds=1)
        partial=(close_dates-dates+tick).ne(pd.Timedelta(hours=4))
        return {'status':'verified_archive','url':url,'published_sha256':published,'actual_sha256':actual,
                'candles':len(f),'first_open':dates.iloc[0].isoformat(),'last_open':dates.iloc[-1].isoformat(),
                'last_close_time':close_dates.iloc[-1].isoformat(),'nonstandard_duration_bars':int(partial.sum()),
                'venue':'Binance spot','notice':'Not an OKX replacement or complete-universe backtest.'}
    except Exception as e:return {'status':'failed','url':url,'error':str(e)}


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen_inputs.json').exists():raise SystemExit('Preserve existing attempt')
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['PIT_ALIAS_FOLLOWUP.md','audit_historical_aliases.py']}
    (OUT/'frozen_inputs.json').write_text(json.dumps(hashes,indent=2))
    ex=ccxt.okx({'enableRateLimit':True,'timeout':20000});probes={}
    try:
        for symbol,date in [('GRAM','2023-07-01'),('GRAM','2024-09-01'),('GRAM','2026-06-17'),('POL','2023-07-01'),('TON','2026-06-15'),('MATIC','2024-09-06')]:
            ms=int(pd.Timestamp(date,tz='UTC').timestamp()*1000)
            request={'instId':symbol+'-USDT','bar':ex.timeframes['4h'],'before':ms-1,'after':ms+12*3600000,'limit':3}
            try:
                response=await ex.public_get_market_history_candles(request)
                bars=response.get('data',[])
                probes[symbol+'_'+date]={'request':request,'response':response,'status':'sample_available' if bars else 'no_sample_returned'}
            except Exception as e:probes[symbol+'_'+date]={'request':request,'status':'api_error','error':str(e)}
    finally:await ex.close()
    archives={month:await asyncio.to_thread(archive_probe,month) for month in ('2023-07','2024-09')}
    result={'retrieved_at':datetime.now(timezone.utc).isoformat(),'hashes':hashes,'alias_probes':probes,'archives':archives,
            'status':'feasibility_only_no_performance_results','historical_universe_ready':False}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'aliases':{k:v['status'] for k,v in probes.items()},'archives':archives},indent=2))

if __name__=='__main__':asyncio.run(main())
