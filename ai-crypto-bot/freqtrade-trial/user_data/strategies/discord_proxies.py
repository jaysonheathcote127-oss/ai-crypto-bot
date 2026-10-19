"""Exploratory adaptations only; see DISCORD_EXPERIMENT.md."""
from pandas import DataFrame
from research_baselines import ResearchBase


class SweepConfirm(ResearchBase):
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(dataframe, metadata)
        floor = df.low.shift(1).rolling(20).min()
        body = (df.close - df.open).abs()
        span = df.high - df.low
        lower_wick = df[["open", "close"]].min(axis=1) - df.low
        df["sweep_setup"] = ((df.low < floor) & (df.close > floor)
                             & (df.close > df.open) & (lower_wick >= 2 * body)
                             & (span > 0) & ((df.close - df.low) >= .75 * span))
        df["trend_context"] = (df.close > df.sma200) & (df.sma50 > df.sma50.shift(6))
        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe
        condition = (df.sweep_setup.shift(1, fill_value=False)
                     & (df.close > df.high.shift(1)) & (df.volume > 0))
        if self.__class__.__name__ == "SweepTrendConfirm":
            condition &= df.trend_context.shift(1, fill_value=False)
        df["enter_long"] = 0
        df.loc[condition, ["enter_long", "enter_tag"]] = (1, "sweep_rejection_confirmation")
        return df

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe.loc[(dataframe.close < dataframe.prior_low10)
                      | (dataframe["rsi"] > 65), "exit_long"] = 1
        return dataframe


class SweepTrendConfirm(SweepConfirm):
    pass
