import unittest
import numpy as np
import pandas as pd
from hourly_equity_audit import hourly_equity

class HourlyEquityTests(unittest.TestCase):
    def inputs(self):
        d=pd.date_range('2025-01-01',periods=4,freq='1h',tz='UTC')
        prices={'BTC/USDT':pd.Series([110.,80.,90.,90.],index=d)}
        t={'pair':'BTC/USDT','open_date':d[0].isoformat(),'close_date':d[2].isoformat(),
           'amount':1.,'open_rate':100.,'close_rate':90.,'fee_open':.01,'fee_close':.01}
        return d,prices,t

    def test_fees_cash_and_open_positions_reconcile(self):
        _,p,t=self.inputs();e=hourly_equity([t],p)
        np.testing.assert_allclose(e.equity,[1009.,979.,988.1,988.1])
        np.testing.assert_allclose(e.cash,[899.,899.,988.1,988.1])

    def test_same_hour_roundtrip_and_missing_active_marks(self):
        d,p,t=self.inputs();t['close_date']=t['open_date']
        e=hourly_equity([t],p)
        np.testing.assert_allclose(e.equity,[988.1]*4)
        t['close_date']=d[2].isoformat();p['BTC/USDT'].iloc[1]=np.nan
        with self.assertRaises(ValueError):hourly_equity([t],p)

if __name__=='__main__':unittest.main()
