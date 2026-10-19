"""Check that observations reject bad data and label replay honestly."""
import asyncio
import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from observe_top100 import analyse, validate_quote, collect, save


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.now = pd.Timestamp("2026-10-19T00:00:00Z")
        dates = pd.date_range(end=self.now - pd.Timedelta(hours=4), periods=300, freq="4h")
        self.rows = [[int(t.timestamp() * 1000), 100., 101., 99., 100., 1000.] for t in dates]
        self.quote = {"last": 100., "bid": 99.99, "ask": 100.01,
                      "timestamp": int(self.now.timestamp() * 1000), "quoteVolume": 2_000_000.}

    def test_unfinished_candle_cannot_change_signals(self):
        incomplete = [int(self.now.timestamp() * 1000), 100., 1e8, 1., 1e8, 1e8]
        self.assertEqual(analyse(self.rows, self.now), analyse(self.rows + [incomplete], self.now))

    def test_missing_and_stale_candles_block_observation(self):
        with self.assertRaises(ValueError):
            analyse(self.rows[:-1], self.now)
        missing = self.rows[:150] + self.rows[151:]
        # Keep at least 300 rows so the gap check, rather than warmup, is exercised.
        missing.insert(0, [self.rows[0][0] - 14_400_000, 100., 101., 99., 100., 1000.])
        with self.assertRaisesRegex(ValueError, "Missing"):
            analyse(missing, self.now)
        with self.assertRaisesRegex(ValueError, "stale"):
            analyse(self.rows, self.now + pd.Timedelta(hours=9))

    def test_stale_future_wide_and_thin_quotes_block_observation(self):
        validate_quote(self.quote, self.now)
        for change in ({"timestamp": self.quote["timestamp"] - 121000},
                       {"timestamp": self.quote["timestamp"] + 11000},
                       {"ask": 102.}, {"quoteVolume": 999999.}, {"last": float("nan")}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_quote({**self.quote, **change}, self.now)

    def test_replay_is_explicit_and_all_100_assets_are_accounted_for(self):
        report = asyncio.run(collect(replay=True))
        self.assertEqual(report["mode"], "saved_data_replay")
        self.assertEqual(len(report["assets"]), 100)
        observed = [a for a in report["assets"] if a["status"] == "observed"]
        self.assertEqual(len(observed), 17)
        self.assertTrue(all(a["price"] is None and a["quote_at"] is None for a in observed))
        with tempfile.TemporaryDirectory() as folder:
            path1 = save(report, Path(folder))
            path2 = save(report, Path(folder))
            self.assertNotEqual(path1, path2)
            self.assertEqual(json.loads(path1.read_text())["mode"], "saved_data_replay")
            self.assertEqual(json.loads((Path(folder) / "latest.json").read_text())["mode"], "saved_data_replay")


if __name__ == "__main__":
    unittest.main(verbosity=2)
