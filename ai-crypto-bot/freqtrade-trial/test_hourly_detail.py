import unittest
import numpy as np
import pandas as pd
from download_hourly_detail import validate,START,END

class HourlyDataTests(unittest.TestCase):
    def test_continuity_and_numeric_integrity(self):
        f=pd.DataFrame({'date':pd.date_range(START,END,freq='1h',inclusive='left'),'open':100.,'high':101.,'low':99.,'close':100.,'volume':1.})
        validate(f)
        with self.assertRaises(ValueError):validate(f.drop(index=40))
        for column,value in [('close',np.inf),('low',102.),('volume',-1.)]:
            bad=f.copy();bad.loc[40,column]=value
            with self.assertRaises(ValueError):validate(bad)

if __name__=='__main__':unittest.main()
