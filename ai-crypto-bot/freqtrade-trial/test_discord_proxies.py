import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "user_data/strategies"))
from discord_proxies import SweepConfirm, SweepTrendConfirm


class SweepTests(unittest.TestCase):
    def frame(self):
        df = pd.DataFrame({"open": [100.] * 320, "high": [102.] * 320,
                           "low": [98.] * 320, "close": [100.] * 320,
                           "volume": [100.] * 320})
        df.loc[305, ["open", "high", "low", "close"]] = [99, 101, 94, 100]
        df.loc[306, ["open", "high", "low", "close"]] = [100, 104, 99, 103]
        return df

    def signals(self, cls, frame):
        strategy = cls({})
        df = strategy.populate_indicators(frame.copy(), {})
        df = strategy.populate_entry_trend(df, {})
        return strategy.populate_exit_trend(df, {})

    def test_confirmation_requires_next_completed_bar(self):
        df = self.signals(SweepConfirm, self.frame())
        self.assertEqual(df.loc[305, "enter_long"], 0)
        self.assertEqual(df.loc[306, "enter_long"], 1)
        self.assertEqual(df.loc[307, "enter_long"], 0)

    def test_future_candles_cannot_change_past_signals(self):
        frame = self.frame()
        for cls in (SweepConfirm, SweepTrendConfirm):
            full = self.signals(cls, frame)
            prefix = self.signals(cls, frame.iloc[:307])
            for col in ("enter_long", "exit_long", "sweep_setup", "trend_context"):
                pd.testing.assert_series_equal(full[col].iloc[:307], prefix[col])

    def test_filter_rejects_flat_context(self):
        self.assertEqual(self.signals(SweepTrendConfirm, self.frame()).loc[306, "enter_long"], 0)


if __name__ == "__main__":
    unittest.main()
