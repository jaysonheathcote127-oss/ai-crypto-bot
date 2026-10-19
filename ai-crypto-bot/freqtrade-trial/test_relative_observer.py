import unittest
import numpy as np
import pandas as pd
from observe_relative_strength import analyse_universe


class RelativeObserverTests(unittest.TestCase):
    def inputs(self):
        dates=pd.date_range('2025-01-01',periods=310,freq='4h',tz='UTC')
        frames={}
        for i,p in enumerate(['BTC/USDT','ETH/USDT','SOL/USDT']):
            c=100*np.exp(np.arange(310)*(.001+i*.0001))
            frames[p]=[[int(d.timestamp()*1000),float(x),float(x*1.01),float(x*.99),float(x),100.] for d,x in zip(dates,c)]
        return frames,dates[-1]+pd.Timedelta(hours=4,minutes=5),{'exchange':{'pair_whitelist':list(frames)}}

    def test_unfinished_candles_cannot_change_fixed_universe_signals(self):
        rows,now,config=self.inputs()
        expected=analyse_universe(rows,now,config)
        changed={p:a+[[int(now.floor('4h').timestamp()*1000),1e9,1e9,1e9,1e9,100.]] for p,a in rows.items()}
        self.assertEqual(expected,analyse_universe(changed,now,config))
        self.assertEqual(len(expected),3)
        self.assertEqual(len(expected[0]['signals']),4)

    def test_missing_and_unsynchronized_pairs_reject_whole_snapshot(self):
        rows,now,config=self.inputs()
        missing={p:a for p,a in rows.items() if p!='ETH/USDT'}
        with self.assertRaises(KeyError): analyse_universe(missing,now,config)
        rows['ETH/USDT']=rows['ETH/USDT'][:-1]
        with self.assertRaisesRegex(ValueError,'differs'): analyse_universe(rows,now,config)

if __name__=='__main__': unittest.main()
