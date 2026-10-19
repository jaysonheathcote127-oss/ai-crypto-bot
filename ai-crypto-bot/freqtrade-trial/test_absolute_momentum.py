import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parent/'user_data/strategies'))
from absolute_momentum import DailyAbsoluteMomentum, DailySlowMomentum, momentum_panel


class Provider:
    def __init__(self,frames): self.frames=frames
    def get_pair_dataframe(self,pair,timeframe): return self.frames[pair].copy()


class AbsoluteMomentumTests(unittest.TestCase):
    def frames(self,size=650):
        rng=np.random.default_rng(392)
        dates=pd.date_range('2024-01-01',periods=size,freq='4h',tz='UTC')
        pairs=['BTC/USDT']+[f'COIN{i:02}/USDT' for i in range(16)]
        frames={}
        for p in pairs:
            c=100*np.exp(np.cumsum(rng.normal(.001,.018,size)))
            frames[p]=pd.DataFrame({'date':dates,'open':c,'high':c*1.01,'low':c*.99,'close':c,'volume':100.})
        return frames

    def signals(self,cls,frames,pair):
        s=cls({'exchange':{'pair_whitelist':list(frames)}})
        s.dp=Provider(frames)
        f=s.populate_indicators(frames[pair].copy(),{'pair':pair})
        return s.populate_exit_trend(s.populate_entry_trend(f,{'pair':pair}),{'pair':pair})

    def test_full_universe_prefix_indicators_and_signals(self):
        f=self.frames()
        prefix={p:a.iloc[:500].copy() for p,a in f.items()}
        shock={p:a.copy() for p,a in f.items()}
        for a in shock.values(): a.loc[500:,['open','high','low','close']]*=100
        for cls in (DailyAbsoluteMomentum,DailySlowMomentum):
            entries=0
            for pair in f:
                a=self.signals(cls,prefix,pair)
                b=self.signals(cls,shock,pair).iloc[:500]
                assert_frame_equal(a,b)
                entries+=int(a.enter_long.sum())
            self.assertGreater(entries,0)

    def test_momentum_uses_exact_horizon_and_rejects_invalid_history(self):
        f=self.frames()
        for lookback in (30,120):
            ret,_,ready,_=momentum_panel(f,lookback)
            c=f['BTC/USDT'].close
            self.assertAlmostEqual(ret['BTC/USDT'].iloc[400],c.iloc[400]/c.iloc[400-lookback]-1)
            bad={p:a.copy() for p,a in f.items()}
            bad['COIN00/USDT'].loc[350,'close']=np.inf
            _,_,r,_=momentum_panel(bad,lookback)
            self.assertFalse(r.loc[f['BTC/USDT'].date.iloc[350:350+lookback+1]].any())
            self.assertTrue(ready.iloc[400])

    def test_absolute_boundaries_and_unscheduled_risk_exit(self):
        f=pd.DataFrame({'date':pd.to_datetime(['2025-01-01 20:00Z']*3+['2025-01-02 04:00Z']*2),
                        'rs_rank':[1]*5,'rs_ready':[True]*5,'rs_risk_on':[True]*4+[False],
                        'close':[101]*5,'sma50':[100]*5,'volume':[100]*5,'rs_momentum':[.01,0,-.01,-.01,.01]})
        for cls in (DailyAbsoluteMomentum,DailySlowMomentum):
            s=cls({'exchange':{'pair_whitelist':list(self.frames())}})
            self.assertEqual(s.populate_entry_trend(f.copy(),{}).enter_long.tolist(),[1,0,0,0,0])
            self.assertEqual(s.populate_exit_trend(f.copy(),{}).exit_long.tolist(),[0,1,1,0,1])

if __name__=='__main__': unittest.main()
