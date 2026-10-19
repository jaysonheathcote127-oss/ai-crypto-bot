"""One-shot public-data research ledger; no order or portfolio code."""
import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
import ccxt.async_support as ccxt
import pandas as pd
from observe_top100 import analyse, validate_quote, save
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'user_data/strategies'))
from regime_relative_strength import RegimeRelativeStrength
from daily_relative_strength import DailyRelativeStrength
from absolute_momentum import DailyAbsoluteMomentum, DailySlowMomentum
CLASSES=(RegimeRelativeStrength,DailyRelativeStrength,DailyAbsoluteMomentum,DailySlowMomentum)
DEST=ROOT/'data/observations/relative_strength_forward_v2'

class Provider:
    def __init__(self,frames): self.frames=frames
    def get_pair_dataframe(self,pair,timeframe): return self.frames[pair].copy()


def analyse_universe(rows_by_pair,now,config):
    frames={}
    for pair in config['exchange']['pair_whitelist']:
        rows=rows_by_pair[pair]
        analyse(rows,now)  # Existing tested OHLC integrity/freshness validator.
        f=pd.DataFrame(rows,columns=['date','open','high','low','close','volume'])
        f['date']=pd.to_datetime(f['date'],unit='ms',utc=True)
        frames[pair]=f[f.date+pd.Timedelta(hours=4)<=now].reset_index(drop=True)
    last_dates={f.date.iloc[-1] for f in frames.values()}
    if len(last_dates)!=1:
        raise ValueError('Latest completed candle differs across the fixed universe')
    assets=[]
    for pair,f in frames.items():
        signals={}
        for cls in CLASSES:
            s=cls(config); s.dp=Provider(frames)
            a=s.populate_indicators(f.copy(),{'pair':pair})
            a=s.populate_exit_trend(s.populate_entry_trend(a,{'pair':pair}),{'pair':pair})
            row=a.iloc[-1]
            if not bool(row.rs_ready):
                raise ValueError('Fixed cross-sectional universe is not ready')
            signals[cls.__name__]={'entry':bool(row.enter_long==1),'exit':bool(row.exit_long==1),
                                   'rank':float(row.rs_rank),'btc_risk_on':bool(row.rs_risk_on)}
        assets.append({'pair':pair,'status':'observed','completed_candle':f.date.iloc[-1].isoformat(),
                       'last_close':float(f.close.iloc[-1]),'signals':signals})
    return assets


def manifest(config):
    DEST.mkdir(parents=True,exist_ok=True)
    paths=['FORWARD_OBSERVATION.md','config.research.json','observe_relative_strength.py','observe_top100.py',
           'user_data/strategies/research_baselines.py','user_data/strategies/regime_relative_strength.py',
           'user_data/strategies/daily_relative_strength.py','user_data/strategies/absolute_momentum.py']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    path=DEST/'forward_manifest.json'
    if path.exists():
        result=json.loads(path.read_text())
        if result['hashes']!=hashes:
            raise ValueError('Frozen forward-observer source drift; start a separately named experiment')
        return result
    now=pd.Timestamp.now(tz='UTC')
    result={'created_at':now.isoformat(),'first_forward_candle_open':now.ceil('4h').isoformat(),
            'hashes':hashes,'pairs':config['exchange']['pair_whitelist'],
            'notice':'Observation only, no candidate promoted; no orders or performance claims.'}
    with path.open('x') as f: json.dump(result,f,indent=2)
    return result


async def collect():
    config=json.loads((ROOT/'config.research.json').read_text())
    if not config['dry_run'] or any(config['exchange'].get(k) for k in ('key','secret','password')):
        raise ValueError('Only credential-free research allowed')
    frozen=manifest(config)
    ex=ccxt.okx({'enableRateLimit':True,'timeout':20000})
    raw={}; quotes={}; errors={}; semaphore=asyncio.Semaphore(3)
    async def fetch(pair):
        async with semaphore:
            try:
                market=ex.market(pair)
                if not market.get('active') or not market.get('spot'):
                    raise ValueError('Inactive or nonspot market')
                raw[pair]=await ex.fetch_ohlcv(pair,'4h',limit=400,params={'paginate':True,'paginationCalls':2})
                ticker=await ex.fetch_ticker(pair)
                quotes[pair]={'raw':ticker,'validated':validate_quote(ticker,pd.Timestamp.now(tz='UTC'))}
            except Exception as e:
                errors[pair]=str(e)
    try:
        await ex.load_markets()
        await asyncio.gather(*(fetch(p) for p in frozen['pairs']))
    except Exception as e:
        errors['universe']=str(e)
    finally:
        await ex.close()
    now=pd.Timestamp.now(tz='UTC')
    source={'candles':raw,'quotes':quotes,'errors':errors,'collected_at':now.isoformat()}
    encoded=json.dumps(source,sort_keys=True).encode()
    digest=hashlib.sha256(encoded).hexdigest()
    source_path=DEST/f'source_{digest}.json'
    if not source_path.exists():
        with source_path.open('xb') as f: f.write(encoded)
    assets=[]
    if not errors:
        try:
            assets=analyse_universe(raw,now,config)
            for a in assets:
                a.update(quotes[a['pair']]['validated'])
                a['phase']='forward' if pd.Timestamp(a['completed_candle'])>=pd.Timestamp(frozen['first_forward_candle_open']) else 'baseline_only'
        except Exception as e:
            errors['analysis']=str(e)
    if errors:
        assets=[{'pair':p,'status':'blocked','reason':errors.get(p,'Fixed-universe snapshot blocked; see errors')} for p in frozen['pairs']]
    report={'mode':'fresh_public_data','observed_at':now.isoformat(),'assets':assets,'errors':errors,
            'source_file':source_path.name,'source_sha256':digest,'manifest_created_at':frozen['created_at'],
            'notice':'Unpromoted research flags only; no orders, portfolio, fills or P&L.'}
    path=save(report,DEST)
    print(json.dumps({'snapshot':str(path),'counts':pd.Series([a['status'] for a in assets]).value_counts().to_dict(),'errors':errors},indent=2))

if __name__=='__main__':
    asyncio.run(collect())
