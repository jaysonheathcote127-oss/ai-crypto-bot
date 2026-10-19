import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0, str(Path(__file__).resolve().parent / 'user_data/strategies'))
from regime_relative_strength import ranking_panel, RegimeRelativeStrength

class RelativeStrengthTests(unittest.TestCase):
    def frames(self):
        pairs = ['BTC/USDT'] + [f'COIN{i:02}/USDT' for i in range(16)]
        dates = pd.date_range('2024-01-01', periods=500, freq='4h', tz='UTC')
        return {p: pd.DataFrame({'date': dates, 'close': 100*np.exp(np.arange(500)*(.001+i*.0001)),
                                'volume': 100.}) for i, p in enumerate(pairs)}

    def test_future_changes_in_every_market_preserve_past(self):
        frames = self.frames()
        expected = ranking_panel({p: f.iloc[:400] for p, f in frames.items()})
        for pair in frames:
            changed = {p: f.copy() for p, f in frames.items()}
            changed[pair].loc[400:, 'close'] *= .001
            actual = ranking_panel(changed)
            for a, b in zip(expected, actual):
                assert_frame_equal(a.to_frame() if isinstance(a, pd.Series) else a,
                                   b.iloc[:400].to_frame() if isinstance(b, pd.Series) else b.iloc[:400])

    def test_ties_and_missing_candles(self):
        frames = self.frames()
        frames = {p: frames['BTC/USDT'].copy() for p in frames}
        ranks, ready, _ = ranking_panel(frames)
        self.assertEqual(ranks.iloc[-1].tolist(), list(range(1, 18)))
        frames['COIN00/USDT'] = frames['COIN00/USDT'].drop(index=300)
        _, ready, _ = ranking_panel(frames)
        self.assertFalse(ready.iloc[300:331].any())
        self.assertTrue(ready.iloc[331])

    def test_entry_exit_boundaries_and_unavailable_inputs(self):
        s = RegimeRelativeStrength({'exchange': {'pair_whitelist': list(self.frames())}})
        f = pd.DataFrame({'rs_rank': [5,6,9,10,1,1,1], 'rs_ready': [True]*5+[False,True],
                          'rs_risk_on': [True]*6+[False], 'close': [101,101,101,101,99,101,101],
                          'sma50': [100]*7, 'volume': [100]*7})
        f = s.populate_exit_trend(s.populate_entry_trend(f, {}), {})
        self.assertEqual(f.enter_long.tolist(), [1,0,0,0,0,0,0])
        self.assertEqual(f.exit_long.tolist(), [0,0,0,1,1,1,1])

if __name__ == '__main__':
    unittest.main()
