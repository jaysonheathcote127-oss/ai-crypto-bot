import unittest

import pandas as pd

from run_signals import closed_candles
from strategy import generate_signals


class StrategyTests(unittest.TestCase):
    def test_crossovers_and_warmup(self):
        frame = pd.DataFrame({"close": [3, 2, 1, 2, 3, 2, 1]})
        result = generate_signals(frame, 2, 3)
        self.assertEqual(result.signal.tolist(), ["hold"] * 4 + ["buy", "hold", "sell"])
        self.assertEqual(frame.columns.tolist(), ["close"])

    def test_no_signal_on_first_average_or_flat_prices(self):
        self.assertTrue((generate_signals(pd.DataFrame({"close": [2] * 30})).signal == "hold").all())

    def test_future_prices_do_not_change_past_signals(self):
        frame = pd.DataFrame({"close": [3, 2, 1, 2, 3, 2, 1]})
        pd.testing.assert_frame_equal(generate_signals(frame, 2, 3).iloc[:5], generate_signals(frame.iloc[:5], 2, 3))

    def test_bad_inputs(self):
        for price in [None, -1, float("inf"), "invalid"]:
            with self.assertRaises((ValueError, TypeError)):
                generate_signals(pd.DataFrame({"close": [price]}))
        with self.assertRaises(ValueError):
            generate_signals(pd.DataFrame({"close": [1]}), 20, 5)

    def test_excludes_open_candle(self):
        times = pd.to_datetime(["2026-10-19T12:00Z", "2026-10-19T12:05Z"], utc=True)
        result = closed_candles(pd.DataFrame({"timestamp": times}), pd.Timestamp("2026-10-19T12:07Z"))
        self.assertEqual(result.timestamp.tolist(), [times[0]])


if __name__ == "__main__":
    unittest.main()
