"""Scheduled, persistent paper trading using public Coinbase data only."""

import json
import math
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import ccxt
import pandas as pd

from strategy import generate_signals

UTC = timezone.utc
UK = ZoneInfo("Europe/London")
FEE = 0.001
SLIPPAGE = 0.0005


def work_hours(now):
    local = now.astimezone(UK)
    return local.weekday() < 5 and 8 <= local.hour < 16


def stamp(now):
    return now.astimezone(UTC).isoformat()


class PaperBot:
    def __init__(self, path):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, time TEXT NOT NULL, kind TEXT NOT NULL, message TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY, time TEXT NOT NULL, candle TEXT UNIQUE NOT NULL,
                side TEXT NOT NULL, price REAL NOT NULL, amount REAL NOT NULL,
                fee REAL NOT NULL, cash REAL NOT NULL, btc REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS equity (
                id INTEGER PRIMARY KEY, time TEXT NOT NULL, price REAL NOT NULL, value REAL NOT NULL);
        """)
        row = self.db.execute("SELECT payload FROM state WHERE id=1").fetchone()
        self.state = json.loads(row[0]) if row else {
            "cash": 1000., "btc": 0., "initial_cash": 1000., "fees": 0.,
            "price": None, "price_at": None, "last_success": None,
            "last_candle": None, "signal": "hold", "short_ma": None,
            "long_ma": None, "paused_day": None, "error": None,
            "session_day": None, "last_check": None,
        }
        self.active = False
        # Always baseline on process restart: never fill missed signals retroactively.
        self.baseline = True
        self.save()

    def save(self):
        self.db.execute("INSERT OR REPLACE INTO state VALUES (1, ?)", (json.dumps(self.state),))
        self.db.commit()

    def event(self, now, kind, message):
        self.db.execute("INSERT INTO events(time,kind,message) VALUES (?,?,?)",
                        (stamp(now), kind, message))

    def scheduled(self, now):
        return work_hours(now) and self.state["paused_day"] != now.astimezone(UK).date().isoformat()

    def tick_schedule(self, now):
        with self.lock:
            active = self.scheduled(now)
            if active != self.active:
                self.active = active
                self.baseline = True
                if active:
                    self.state["session_day"] = now.astimezone(UK).date().isoformat()
                    self.event(now, "session", "Work session started. Paper mode; first check establishes a baseline.")
                else:
                    self.event(now, "session", "Work session stopped. Holdings preserved; no further simulated trades.")
                self.save()
            return active

    def pause(self, now):
        with self.lock:
            self.state["paused_day"] = now.astimezone(UK).date().isoformat()
            self.save()
            self.tick_schedule(now)

    def resume(self, now):
        with self.lock:
            self.state["paused_day"] = None
            self.save()
            self.tick_schedule(now)

    def failure(self, now, error):
        with self.lock:
            # Alert once per outage; retry silently until recovery.
            if self.state["error"] is None:
                self.event(now, "error", f"Market check failed: {str(error)[:240]}. Retrying each minute; no trade on failed data.")
            self.state["error"] = str(error)[:240]
            self.state["last_check"] = stamp(now)
            self.baseline = True
            self.save()

    def apply_market(self, rows, ticker, now):
        """Validate a snapshot and atomically apply at most one newly closed signal."""
        frame = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        frame["timestamp"] = pd.to_datetime(frame.timestamp, unit="ms", utc=True)
        frame = frame.loc[frame.timestamp + pd.Timedelta(minutes=5) <= pd.Timestamp(now)]
        # Reject bad input rather than silently correcting it.
        if len(frame) < 21 or frame.timestamp.isna().any():
            raise ValueError("Insufficient completed five-minute candles")
        if not frame.timestamp.diff().iloc[1:].eq(pd.Timedelta(minutes=5)).all():
            raise ValueError("Missing, duplicate or unordered market candles")
        report = generate_signals(frame)
        latest = report.iloc[-1]
        closed_at = latest.timestamp.to_pydatetime() + timedelta(minutes=5)
        if not timedelta(0) <= now - closed_at <= timedelta(minutes=6):
            raise ValueError("Completed candle data is stale")
        price = float(ticker["last"])
        quote_time = datetime.fromtimestamp(float(ticker["timestamp"]) / 1000, UTC)
        if not math.isfinite(price) or price <= 0 or not timedelta(seconds=-10) <= now - quote_time <= timedelta(minutes=2):
            raise ValueError("Current Coinbase price is invalid or stale")
        candle = latest.timestamp.isoformat()
        with self.lock:
            if not self.scheduled(now):
                return
            before = self.state.copy()
            try:
                if self.state["error"]:
                    self.event(now, "recovery", "Market data recovered. Re-establishing baseline before trading.")
                previous = self.state["last_candle"]
                is_new = previous is not None and candle > previous
                consecutive = previous is not None and latest.timestamp == pd.Timestamp(previous) + pd.Timedelta(minutes=5)
                side = str(latest.signal)
                # First check, gaps and recovery only observe; avoid historical fills.
                if not self.baseline and is_new and consecutive and now - closed_at <= timedelta(minutes=2):
                    self.fill(now, candle, side, price)
                elif is_new and not consecutive:
                    self.event(now, "warning", "Missed candles; skipped old signals and reset baseline.")
                self.state.update(price=price, price_at=stamp(quote_time), last_success=stamp(now),
                                  last_check=stamp(now), last_candle=candle, signal=side,
                                  short_ma=float(latest.short_ma), long_ma=float(latest.long_ma), error=None)
                self.db.execute("INSERT INTO equity(time,price,value) VALUES (?,?,?)",
                                (stamp(now), price, self.state["cash"] + self.state["btc"] * price))
                self.save()
                self.baseline = False
            except Exception:
                self.db.rollback()
                self.state = before
                raise

    def fill(self, now, candle, side, market_price):
        if self.db.execute("SELECT 1 FROM trades WHERE candle=?", (candle,)).fetchone():
            return
        cash, btc = self.state["cash"], self.state["btc"]
        if side == "buy" and btc == 0 and cash > 0:
            price = market_price * (1 + SLIPPAGE)
            notional = cash / (1 + FEE)
            fee = notional * FEE
            amount = notional / price
            cash, btc = 0., amount
        elif side == "sell" and btc > 0:
            price = market_price * (1 - SLIPPAGE)
            amount = btc
            fee = amount * price * FEE
            cash, btc = cash + amount * price - fee, 0.
        else:
            return
        self.db.execute("INSERT INTO trades(time,candle,side,price,amount,fee,cash,btc) VALUES (?,?,?,?,?,?,?,?)",
                        (stamp(now), candle, side, price, amount, fee, cash, btc))
        self.state.update(cash=cash, btc=btc, fees=self.state["fees"] + fee)
        self.event(now, "trade", f"Paper {side.upper()}: {amount:.8f} BTC at ${price:,.2f} USD; fee ${fee:.2f}.")

    def snapshot(self, now):
        with self.lock:
            result = self.state.copy()
            result["status"] = "running" if self.scheduled(now) else (
                "paused" if self.state["paused_day"] == now.astimezone(UK).date().isoformat() else "outside_hours")
            result["stale"] = self.state["last_success"] is None or (
                now - datetime.fromisoformat(self.state["last_success"]) > timedelta(minutes=3))
            result["equity"] = self.state["cash"] + self.state["btc"] * (self.state["price"] or 0)
            result["pnl"] = result["equity"] - self.state["initial_cash"]
            result["server_time"] = stamp(now)
            result["trades"] = [dict(row) for row in self.db.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 100")]
            result["trade_count"] = self.db.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
            result["events"] = [dict(row) for row in self.db.execute("SELECT * FROM events ORDER BY id DESC LIMIT 100")]
            result["history"] = [dict(row) for row in reversed(self.db.execute("SELECT * FROM equity ORDER BY id DESC LIMIT 480").fetchall())]
            return result


def fetch_market(exchange):
    rows = exchange.fetch_ohlcv("BTC/USD", timeframe="5m", limit=100)
    ticker = exchange.fetch_ticker("BTC/USD")
    return rows, ticker


def make_exchange():
    return ccxt.coinbase({"enableRateLimit": True, "timeout": 20000})
