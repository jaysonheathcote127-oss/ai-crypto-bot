import unittest

import pandas as pd

from paper_trading import simulate


def candles():
    return pd.DataFrame({"timestamp": pd.date_range("2026-10-19", periods=8, freq="5min", tz="UTC"),
                         "open": [10] * 8, "close": [3, 2, 1, 2, 3, 2, 1, 2]})


class PaperTests(unittest.TestCase):
    def test_next_open_fills_and_costs(self):
        trades, equity, summary = simulate(candles(), 1000, 0.01, 0.02, 2, 3)
        self.assertEqual(trades.side.tolist(), ["buy", "sell"])
        self.assertEqual(trades.fill_timestamp.tolist(), candles().timestamp.iloc[[5, 7]].tolist())
        self.assertAlmostEqual(trades.price_usd.iloc[0], 10.2)
        self.assertAlmostEqual(trades.price_usd.iloc[1], 9.8)
        expected_btc = 1000 / 1.01 / 10.2
        self.assertAlmostEqual(summary["final_cash_usd"], expected_btc * 9.8 * 0.99)
        self.assertEqual(summary["final_btc"], 0)
        self.assertTrue((equity.cash_usd >= 0).all())
        self.assertAlmostEqual(summary["fees_usd"], 1000 / 1.01 * .01 + expected_btc * 9.8 * .01)

    def test_final_signal_does_not_fill_without_next_bar(self):
        trades, _, summary = simulate(candles().iloc[:5], short_window=2, long_window=3)
        self.assertTrue(trades.empty)
        self.assertEqual(summary["final_equity_usd"], 1000)

    def test_sell_without_holdings_is_ignored(self):
        frame = candles()
        frame["close"] = [1, 2, 3, 2, 1, 1, 1, 1]
        trades, _, _ = simulate(frame, short_window=2, long_window=3)
        self.assertTrue(trades.empty)

    def test_gaps_duplicates_and_bad_prices_rejected(self):
        for column, value in [("timestamp", candles().timestamp.iloc[0]), ("open", -1), ("open", float("nan"))]:
            frame = candles()
            frame.loc[3, column] = value
            with self.assertRaises(ValueError):
                simulate(frame, short_window=2, long_window=3)

    def test_invalid_settings(self):
        for settings in [{"initial_cash": 0}, {"fee_rate": -1}, {"slippage_rate": float("inf")}]:
            with self.assertRaises(ValueError):
                simulate(candles(), short_window=2, long_window=3, **settings)

    def test_replay_is_repeatable(self):
        first = simulate(candles(), short_window=2, long_window=3)
        second = simulate(candles(), short_window=2, long_window=3)
        pd.testing.assert_frame_equal(first[0], second[0])
        self.assertEqual(first[2], second[2])
