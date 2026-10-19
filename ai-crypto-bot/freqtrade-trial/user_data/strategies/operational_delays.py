"""One fixed processing-lag stress, not a new selected trading strategy."""
from daily_relative_strength import DailyRelativeStrength
from absolute_momentum import DailyAbsoluteMomentum, DailySlowMomentum


class OneBarDelay:
    def populate_entry_trend(self, dataframe, metadata):
        df=super().populate_entry_trend(dataframe,metadata)
        df['enter_long']=df['enter_long'].shift(1,fill_value=0).astype(int)
        if 'enter_tag' in df:
            df['enter_tag']=df['enter_tag'].shift(1,fill_value='')
        return df

    def populate_exit_trend(self, dataframe, metadata):
        df=super().populate_exit_trend(dataframe,metadata)
        df['exit_long']=df['exit_long'].shift(1,fill_value=0).astype(int)
        if 'exit_tag' in df:
            df['exit_tag']=df['exit_tag'].shift(1,fill_value='')
        return df


class DelayedDailyControl(OneBarDelay,DailyRelativeStrength):
    pass

class DelayedDailyAbsolute(OneBarDelay,DailyAbsoluteMomentum):
    pass

class DelayedDailySlow(OneBarDelay,DailySlowMomentum):
    pass
