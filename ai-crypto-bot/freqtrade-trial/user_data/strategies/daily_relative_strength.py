"""Single fixed cadence variant; see DAILY_RELATIVE_STRENGTH_EXPERIMENT.md."""
from regime_relative_strength import RegimeRelativeStrength


class DailyRelativeStrength(RegimeRelativeStrength):
    def populate_entry_trend(self, dataframe, metadata):
        df = super().populate_entry_trend(dataframe, metadata)
        df.loc[df['date'].dt.hour.ne(20), 'enter_long'] = 0
        return df

    def populate_exit_trend(self, dataframe, metadata):
        df = super().populate_exit_trend(dataframe, metadata)
        # Missing input/BTC risk-off always exits; rank/own SMA exits daily.
        scheduled = df['date'].dt.hour.eq(20)
        emergency = ~df['rs_ready'] | ~df['rs_risk_on']
        df.loc[~scheduled & ~emergency, 'exit_long'] = 0
        return df
