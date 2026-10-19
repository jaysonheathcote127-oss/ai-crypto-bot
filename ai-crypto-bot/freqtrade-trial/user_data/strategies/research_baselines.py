"""Fixed, unoptimized research baselines. See RESEARCH_PLAN.md."""
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy
from technical import qtpylib


class ResearchBase(IStrategy):
    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "4h"
    startup_candle_count = 300
    process_only_new_candles = True
    stoploss = -0.10
    minimal_roi = {}
    trailing_stop = False
    use_exit_signal = True
    exit_profit_only = False
    position_adjustment_enable = False
    order_types = {"entry": "market", "exit": "market", "stoploss": "market", "stoploss_on_exchange": False}
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma50"] = ta.SMA(dataframe, timeperiod=50)
        dataframe["sma200"] = ta.SMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        bands = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_lower"] = bands["lowerband"]
        dataframe["bb_middle"] = bands["middleband"]
        # Prior completed bars only: today's candle is excluded from the channel.
        dataframe["prior_high20"] = dataframe.high.shift(1).rolling(20).max()
        dataframe["prior_low10"] = dataframe.low.shift(1).rolling(10).min()
        return dataframe


class TrendBaseline(ResearchBase):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe.loc[(qtpylib.crossed_above(dataframe.sma20, dataframe.sma50))
                      & (dataframe.close > dataframe.sma200) & (dataframe.volume > 0),
                      ["enter_long", "enter_tag"]] = (1, "trend_cross")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe.loc[qtpylib.crossed_below(dataframe.sma20, dataframe.sma50)
                      | (dataframe.close < dataframe.sma200), "exit_long"] = 1
        return dataframe


class MomentumBaseline(ResearchBase):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe.loc[qtpylib.crossed_above(dataframe.close, dataframe.prior_high20)
                      & (dataframe.close > dataframe.sma200) & (dataframe.volume > 0),
                      ["enter_long", "enter_tag"]] = (1, "channel_breakout")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe.loc[(dataframe.close < dataframe.prior_low10)
                      | (dataframe.close < dataframe.sma200), "exit_long"] = 1
        return dataframe


class ReversionBaseline(ResearchBase):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe.loc[(dataframe.close < dataframe.bb_lower) & (dataframe["rsi"] < 30)
                      & (dataframe.volume > 0), ["enter_long", "enter_tag"]] = (1, "oversold")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe.loc[(dataframe.close >= dataframe.bb_middle)
                      | (dataframe["rsi"] > 55), "exit_long"] = 1
        return dataframe
