"""Financial data integrity and signal causality checks."""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "user_data/strategies"))
from research_baselines import TrendBaseline, MomentumBaseline, ReversionBaseline
from download_research import validate, START, END
from evaluate_research import engine_timerange, drawdown


class ResearchTests(unittest.TestCase):
    def test_engine_periods_do_not_share_a_boundary_candle(self):
        self.assertEqual(engine_timerange("20241001-20251001"), "20241001-20250930T2000")
        self.assertEqual(engine_timerange("20251001-20260401"), "20251001-20260331T2000")
        self.assertEqual(engine_timerange("20260401-20261019"), "20260401-20261018T2000")

    def test_marked_drawdown_includes_open_position_losses(self):
        self.assertAlmostEqual(drawdown(pd.Series([1100., 880., 1000.])), .2)
        self.assertAlmostEqual(drawdown(pd.Series([900., 950.])), .1)

    def frame(self, size=1300):
        rng = np.random.default_rng(427)
        close = 100 * np.exp(np.cumsum(rng.normal(0, .025, size)))
        return pd.DataFrame({"date": pd.date_range("2024-01-01", periods=size, freq="4h", tz="UTC"),
                             "open": close, "high": close * 1.01, "low": close * .99,
                             "close": close, "volume": np.ones(size) * 100})

    def signals(self, cls, frame):
        strategy = cls({})
        frame = strategy.populate_indicators(frame.copy(), {})
        frame = strategy.populate_entry_trend(frame, {})
        return strategy.populate_exit_trend(frame, {})

    def test_future_prices_do_not_change_past_indicators_or_signals(self):
        frame = self.frame()
        for cls in (TrendBaseline, MomentumBaseline, ReversionBaseline):
            with self.subTest(strategy=cls.__name__):
                prefix = self.signals(cls, frame.iloc[:1000])
                shocked = frame.copy()
                shocked.loc[1000:, ["open", "high", "low", "close"]] *= 100
                full = self.signals(cls, shocked).iloc[:1000]
                assert_frame_equal(prefix, full)
                self.assertGreater(int(self.signals(cls, frame).enter_long.sum()), 0)

    def test_breakout_channel_excludes_current_high(self):
        frame = self.frame()
        frame.loc[500, "high"] = 1e12
        indicators = MomentumBaseline({}).populate_indicators(frame, {})
        self.assertEqual(indicators.loc[500, "prior_high20"], frame.loc[480:499, "high"].max())
        self.assertEqual(indicators.loc[501, "prior_high20"], 1e12)

    def test_history_gaps_and_bad_prices_are_rejected(self):
        dates = pd.date_range(START, END, freq="4h", inclusive="left")
        frame = pd.DataFrame({"date": dates, "open": 100., "high": 101., "low": 99., "close": 100., "volume": 1.})
        validate(frame)
        with self.assertRaises(ValueError):
            validate(frame.drop(index=400).reset_index(drop=True))
        for column, value in [("close", np.nan), ("low", 102.), ("volume", -1.)]:
            bad = frame.copy()
            bad.loc[300, column] = value
            with self.subTest(column=column), self.assertRaises(ValueError):
                validate(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
