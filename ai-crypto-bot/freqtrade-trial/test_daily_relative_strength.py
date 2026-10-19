import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent/'user_data/strategies'))
from daily_relative_strength import DailyRelativeStrength

class CadenceTests(unittest.TestCase):
    def test_entries_only_at_daily_decision_and_emergency_exits_always(self):
        s=DailyRelativeStrength({'exchange':{'pair_whitelist':[str(i) for i in range(17)]}})
        f=pd.DataFrame({'date':pd.to_datetime(['2025-01-01 00:00Z','2025-01-01 20:00Z','2025-01-02 04:00Z','2025-01-02 08:00Z']),
                        'rs_rank':[1]*4,'rs_ready':[True,True,True,False],
                        'rs_risk_on':[True,True,False,True],'close':[101]*4,'sma50':[100]*4,'volume':[100]*4})
        self.assertEqual(s.populate_entry_trend(f.copy(),{}).enter_long.tolist(),[0,1,0,0])
        f['rs_rank']=10
        self.assertEqual(s.populate_exit_trend(f.copy(),{}).exit_long.tolist(),[0,1,1,1])

if __name__=='__main__': unittest.main()
