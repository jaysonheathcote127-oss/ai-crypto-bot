"""Bounded primary-data feasibility probe, not a performance backtest."""
import asyncio
import csv
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import ccxt.async_support as ccxt
import pandas as pd
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/research/historical_universe_audit'
# Facts transcribed from explicit numbered rows in the cited dated snapshot.
ROWS=[(1,'Bitcoin','BTC','candidate'),(2,'Ethereum','ETH','candidate'),
      (3,'Tether USDt','USDT','stablecoin'),(4,'BNB','BNB','candidate'),(5,'XRP','XRP','candidate'),
      (6,'USD Coin','USDC','stablecoin'),(7,'Dogecoin','DOGE','candidate'),(8,'Cardano','ADA','candidate'),
      (9,'Solana','SOL','candidate'),(10,'Toncoin','TON','candidate'),(11,'TRON','TRX','candidate'),
      (12,'Dai','DAI','stablecoin'),(13,'Polkadot','DOT','candidate'),(14,'Polygon','MATIC','candidate'),
      (15,'Litecoin','LTC','candidate'),(16,'Shiba Inu','SHIB','candidate'),(17,'Wrapped Bitcoin','WBTC','wrapped'),
      (18,'Bitcoin Cash','BCH','candidate'),(19,'Chainlink','LINK','candidate'),(20,'TrueUSD','TUSD','stablecoin')]
SOURCE='https://coinmarketcap.com/historical/20230924/'


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen_inputs.json').exists():raise SystemExit('Existing audit attempt; preserve it')
    with (OUT/'historical_top20.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['rank','name','symbol','category']);w.writerows(ROWS)
    freeze={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['PIT_UNIVERSE_FEASIBILITY.md','audit_historical_universe.py']}
    freeze['data/research/historical_universe_audit/historical_top20.csv']=hashlib.sha256((OUT/'historical_top20.csv').read_bytes()).hexdigest()
    (OUT/'frozen_inputs.json').write_text(json.dumps(freeze,indent=2))
    ex=ccxt.okx({'enableRateLimit':True,'timeout':20000});sem=asyncio.Semaphore(3)
    records={};raw={}
    async def probe(symbol,date):
        async with sem:
            key=symbol+'_'+date
            since=int(pd.Timestamp(date,tz='UTC').timestamp()*1000)
            request={'instId':symbol+'-USDT','bar':ex.timeframes['4h'],'before':since-1,'after':since+3*4*3600000,'limit':3}
            try:
                response=await ex.public_get_market_history_candles(request)
                raw[key]={'request':request,'response':response}
                bars=response.get('data',[])
                timestamps=sorted(int(r[0]) for r in bars if since<=int(r[0])<since+3*4*3600000)
                records[key]={'status':'sample_available' if timestamps else 'no_sample_returned','sample_bars':len(timestamps),
                              'first_bar':pd.Timestamp(timestamps[0],unit='ms',tz='UTC').isoformat() if timestamps else None}
            except Exception as e:
                raw[key]={'request':request,'error':str(e)};records[key]={'status':'api_error','error':str(e)}
    try:
        await ex.load_markets()
        metadata={symbol:{'current_spot_pair_present':symbol+'/USDT' in ex.markets,
                          'current_active':ex.markets.get(symbol+'/USDT',{}).get('active'),
                          'current_list_time':ex.markets.get(symbol+'/USDT',{}).get('info',{}).get('listTime')}
                  for _,_,symbol,category in ROWS if category=='candidate'}
        await asyncio.gather(*(probe(symbol,date) for _,_,symbol,c in ROWS if c=='candidate' for date in ('2023-07-01','2024-09-01')),
                             probe('MATIC','2024-09-08'),probe('POL','2024-09-08'))
    finally:await ex.close()
    raw_bytes=json.dumps(raw,sort_keys=True,indent=2).encode();(OUT/'raw_probes.json').write_bytes(raw_bytes)
    summary={'retrieved_at':datetime.now(timezone.utc).isoformat(),'ranking_source':SOURCE,'ranking_date':'2023-09-24',
             'verified_ranked_rows':20,'provisional_nonstable_nonwrapped_assets':15,'metadata':metadata,'probes':records,
             'raw_sha256':hashlib.sha256(raw_bytes).hexdigest(),'status':'feasibility_only_no_universe_backtest',
             'limitations':['Only explicit top20 rows verified, not top100.','Current market metadata is not historical eligibility.',
                            'Sample candles do not prove full history, liquidity, spread or identity mapping.',
                            'MATIC/POL migration requires explicit instrument/event treatment; no silent substitution.']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'assets':15,'probe_counts':{state:sum(a['status']==state for a in records.values()) for state in ('sample_available','no_sample_returned','api_error')},
                      'MATIC':{k:v for k,v in records.items() if k.startswith(('MATIC','POL'))}},indent=2))

if __name__=='__main__':asyncio.run(main())
