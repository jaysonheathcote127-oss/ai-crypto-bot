import sys
import unittest
from pathlib import Path
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parent/'user_data/strategies'))
from operational_delays import DelayedDailyControl,DelayedDailyAbsolute,DelayedDailySlow
from absolute_momentum import momentum_panel

class OperationalTests(unittest.TestCase):
    def fixture(self):
        f=pd.DataFrame({'date':pd.date_range('2025-01-01',periods=12,freq='4h',tz='UTC'),
                        'close':101.,'sma50':100.,'volume':100.,'rs_rank':1.,'rs_ready':True,
                        'rs_risk_on':True,'rs_momentum':.01})
        f.loc[7,'rs_risk_on']=False
        return f

    def test_exact_four_hour_lag_for_all_signals_without_changing_stop(self):
        config={'exchange':{'pair_whitelist':[str(i) for i in range(17)]}}
        for cls in (DelayedDailyControl,DelayedDailyAbsolute,DelayedDailySlow):
            s=cls(config);f=self.fixture()
            a=s.populate_exit_trend(s.populate_entry_trend(f,{}),{})
            self.assertEqual(a.index[a.enter_long.eq(1)].tolist(),[6])
            self.assertEqual(a.index[a.exit_long.eq(1)].tolist(),[8])
            self.assertEqual(s.stoploss,-.1)
            self.assertTrue(a.loc[6,'enter_tag'])
            expected=s.populate_exit_trend(s.populate_entry_trend(self.fixture().iloc[:9].copy(),{}),{})
            assert_frame_equal(expected,a.iloc[:9])

    def test_reversing_pair_order_does_not_change_rank_or_alphabetical_ties(self):
        dates=pd.date_range('2024-01-01',periods=300,freq='4h',tz='UTC')
        frames={p:pd.DataFrame({'date':dates,'close':[100+i for i in range(300)],'volume':100.}) for p in ['BTC/USDT','XRP/USDT','ADA/USDT']}
        a=momentum_panel(frames,30);b=momentum_panel(dict(reversed(list(frames.items()))),30)
        for x,y in zip(a,b):
            assert_frame_equal(x.to_frame() if isinstance(x,pd.Series) else x,y.to_frame() if isinstance(y,pd.Series) else y)
        self.assertEqual(a[1].iloc[-1].to_dict(),{'ADA/USDT':1.,'BTC/USDT':2.,'XRP/USDT':3.})

if __name__=='__main__':unittest.main()
