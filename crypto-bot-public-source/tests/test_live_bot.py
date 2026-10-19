import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from live_bot import PaperBot, work_hours

UTC = timezone.utc
NOW = datetime(2026, 10, 19, 9, 0, 30, tzinfo=UTC)


def market(now, prices=None):
    end = now.replace(second=0, microsecond=0) - timedelta(minutes=5)
    end -= timedelta(minutes=end.minute % 5)
    closes = prices or [100.] * 22
    rows = []
    for i, price in enumerate(closes):
        opened = end - timedelta(minutes=5 * (len(closes) - 1 - i))
        rows.append([int(opened.timestamp() * 1000), price, price, price, price, 1])
    return rows, {"last": 100., "timestamp": now.timestamp() * 1000}


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "paper.sqlite3"
        self.bot = PaperBot(self.path)

    def tearDown(self):
        self.bot.db.close()
        self.temp.cleanup()

    def test_schedule_boundaries_dst_weekend(self):
        for date, active in [("2026-10-19T06:59:00+00:00", False),
                             ("2026-10-19T07:00:00+00:00", True),
                             ("2026-10-19T15:00:00+00:00", False),
                             ("2026-10-24T09:00:00+00:00", False),
                             ("2026-10-26T07:59:00+00:00", False),
                             ("2026-10-26T08:00:00+00:00", True)]:
            self.assertEqual(work_hours(datetime.fromisoformat(date)), active)

    def apply(self, now, closes=None):
        self.bot.tick_schedule(now)
        self.bot.apply_market(*market(now, closes), now)

    def test_baseline_then_buy_only_once_and_persist(self):
        self.apply(NOW)
        later = NOW + timedelta(minutes=5)
        closes = [100.] * 21 + [110.]
        self.apply(later, closes)
        state = self.bot.snapshot(later)
        self.assertEqual(state["trade_count"], 1)
        self.assertEqual(state["cash"], 0)
        self.assertAlmostEqual(state["btc"], 1000 / 1.001 / 100.05)
        self.apply(later, closes)
        self.assertEqual(self.bot.snapshot(later)["trade_count"], 1)
        self.bot.db.close()
        self.bot = PaperBot(self.path)
        self.apply(later, closes)
        self.assertEqual(self.bot.snapshot(later)["trade_count"], 1)
        self.assertAlmostEqual(self.bot.state["btc"], state["btc"])

    def test_first_check_does_not_trade_historical_cross(self):
        self.apply(NOW, [100.] * 21 + [110.])
        self.assertEqual(self.bot.snapshot(NOW)["trade_count"], 0)

    def test_normal_four_minutes_after_close_is_not_stale(self):
        now = NOW.replace(minute=4)
        self.apply(now)
        self.assertIsNone(self.bot.state["error"])

    def test_stale_quote_and_missing_bars_rejected(self):
        rows, ticker = market(NOW)
        ticker["timestamp"] -= 300000
        with self.assertRaises(ValueError):
            self.bot.apply_market(rows, ticker, NOW)
        rows, ticker = market(NOW)
        rows.pop(10)
        with self.assertRaises(ValueError):
            self.bot.apply_market(rows, ticker, NOW)

    def test_pausing_blocks_trades_and_resets_baseline(self):
        self.apply(NOW)
        self.bot.pause(NOW)
        later = NOW + timedelta(minutes=5)
        self.apply(later, [100.] * 21 + [110.])
        self.assertEqual(self.bot.snapshot(later)["status"], "paused")
        self.assertEqual(self.bot.snapshot(later)["trade_count"], 0)
        self.bot.resume(later)
        self.apply(later, [100.] * 21 + [110.])
        self.assertEqual(self.bot.snapshot(later)["trade_count"], 0)

    def test_failure_alert_once_and_recovery_skips_signal(self):
        self.apply(NOW)
        self.bot.failure(NOW, "offline")
        self.bot.failure(NOW, "still offline")
        later = NOW + timedelta(minutes=5)
        self.apply(later, [100.] * 21 + [110.])
        snapshot = self.bot.snapshot(later)
        self.assertEqual(len([e for e in snapshot["events"] if e["kind"] == "error"]), 1)
        self.assertEqual(snapshot["trade_count"], 0)
        self.assertIsNone(snapshot["error"])

    def test_database_failure_rolls_back_balance_and_trade(self):
        self.apply(NOW)
        self.bot.db.execute("CREATE TRIGGER reject_equity BEFORE INSERT ON equity BEGIN SELECT RAISE(ABORT, 'disk failure'); END")
        self.bot.db.commit()
        later = NOW + timedelta(minutes=5)
        with self.assertRaises(Exception):
            self.apply(later, [100.] * 21 + [110.])
        self.assertEqual(self.bot.state["cash"], 1000)
        self.assertEqual(self.bot.snapshot(later)["trade_count"], 0)
