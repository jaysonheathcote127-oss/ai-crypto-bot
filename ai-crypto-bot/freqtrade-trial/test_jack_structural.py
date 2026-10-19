import unittest
import numpy as np
import pandas as pd
from jack_structural_test import (features, resample, aligned_features, signals,
                                  simulate, exit_fill, session, validate, SCORE, PAIRS)


class StructuralTests(unittest.TestCase):
    def market(self, n=960):
        rng = np.random.default_rng(71)
        close = 100 + np.cumsum(rng.normal(0, .3, n))
        op = np.r_[100, close[:-1]]
        return pd.DataFrame({'open': op, 'high': np.maximum(op, close)+.2,
                             'low': np.minimum(op, close)-.2, 'close': close,
                             'volume': 100.}, index=pd.date_range(SCORE, periods=n, freq='5min'))

    def test_pivot_is_not_available_until_two_right_bars_close(self):
        frame = self.market(8)
        frame['high'] = [2., 3., 9., 3., 2., 3., 4., 3.]
        f = features(frame)
        self.assertTrue(f.pivot_high.iloc[:4].isna().all())
        self.assertEqual(f.pivot_high.iloc[4], 9.)

    def test_resample_does_not_publish_incomplete_higher_timeframe(self):
        f = self.market(11)
        self.assertEqual(len(resample(f, 60)), 0)
        self.assertEqual(resample(self.market(12), 60).index[0], SCORE+pd.Timedelta(hours=1))

    def test_prefix_and_future_shock_preserve_features_and_signals(self):
        f = self.market()
        cutoff = 719  # deliberately not aligned to a 15m/hour close
        full = aligned_features(f)
        prefix = aligned_features(f.iloc[:cutoff])
        pd.testing.assert_frame_equal(full.iloc[:cutoff], prefix)
        shocked = f.copy()
        shocked.iloc[cutoff:, :4] *= 5
        pd.testing.assert_frame_equal(full.iloc[:cutoff], aligned_features(shocked).iloc[:cutoff])
        a, _ = signals(f); b, _ = signals(f.iloc[:cutoff]); c, _ = signals(shocked)
        end = f.index[cutoff-1]+pd.Timedelta(minutes=5)
        pd.testing.assert_frame_equal(a[a.signal_time <= end].reset_index(drop=True), b.reset_index(drop=True))
        pd.testing.assert_frame_equal(a[a.signal_time <= end].reset_index(drop=True), c[c.signal_time <= end].reset_index(drop=True))

    def test_stop_wins_ambiguous_bar_and_gap_is_adverse(self):
        both = pd.Series({'open':100., 'high':125., 'low':85., 'close':110.})
        self.assertEqual(exit_fill(both, 90., 120.), (90., 'stop'))
        both['open'] = 80.
        self.assertEqual(exit_fill(both, 90., 120.), (80., 'gap_stop'))

    def fixture(self, lows=None):
        start = pd.Timestamp('2026-07-21 07:00', tz='UTC')
        index = pd.date_range(start, periods=3, freq='5min')
        frame = pd.DataFrame({'open':[100.,101.,101.], 'high':[101.,121.,102.],
                              'low': lows or [99.,100.,100.], 'close':[100.,120.,101.],
                              'volume':100.}, index=index)
        sig = pd.DataFrame([{'signal_time':start, 'model':'NC', 'stop':90.,
                             'target':120., 'be_trigger':200.}])
        return start, {p:frame.copy() for p in PAIRS}, {p:sig.copy() for p in PAIRS}

    def test_known_round_trip_fees_risk_and_simultaneous_pair_priority(self):
        start, frames, sigs = self.fixture()
        summary, trades, eq = simulate(frames, sigs, 'NC', .0015, start, start+pd.Timedelta(minutes=15))
        qty = 5 / (100*1.0015-90*.9985)
        expected = qty*(120*.9985-100*1.0015)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]['pair'], 'BTC-USDT')
        self.assertAlmostEqual(trades[0]['qty'], qty)
        self.assertAlmostEqual(summary['final_equity'], 1000+expected)
        self.assertAlmostEqual(trades[0]['initial_risk'], 5)
        self.assertAlmostEqual(summary['pnl_reconciliation_error'], 0)

    def test_entry_bar_can_stop_and_drawdown_includes_initial_equity(self):
        start, frames, sigs = self.fixture([85.,100.,100.])
        summary, trades, _ = simulate(frames, sigs, 'NC', .0015, start, start+pd.Timedelta(minutes=15))
        self.assertEqual(trades[0]['reason'], 'stop')
        self.assertAlmostEqual(summary['final_equity'], 995.)
        self.assertAlmostEqual(summary['close_drawdown_pct'], .5)

    def test_session_timezone_dst_and_weekend(self):
        self.assertTrue(session(pd.Timestamp('2026-07-21 07:00', tz='UTC')).startswith('London'))
        self.assertTrue(session(pd.Timestamp('2026-12-01 08:00', tz='UTC')).startswith('London'))
        self.assertTrue(session(pd.Timestamp('2026-07-21 13:00', tz='UTC')).startswith('NY'))
        self.assertIsNone(session(pd.Timestamp('2026-07-25 07:00', tz='UTC')))

    def test_missing_and_invalid_data_fail_closed(self):
        f = self.market(12)
        validate(f, f.index[0], f.index[-1]+pd.Timedelta(minutes=5))
        with self.assertRaises(ValueError):
            validate(f.iloc[:-1], f.index[0], f.index[-1]+pd.Timedelta(minutes=5))
        f.iloc[0, f.columns.get_loc('high')] = -1
        with self.assertRaises(ValueError):
            validate(f, f.index[0], f.index[-1]+pd.Timedelta(minutes=5))


if __name__ == '__main__':
    unittest.main()
