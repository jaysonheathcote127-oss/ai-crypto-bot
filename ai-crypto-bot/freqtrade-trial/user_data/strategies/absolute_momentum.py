"""Two predeclared exploratory hypotheses; MOMENTUM_ROBUSTNESS_EXPERIMENT.md."""
import numpy as np
import pandas as pd
from daily_relative_strength import DailyRelativeStrength
from research_baselines import ResearchBase


def momentum_panel(frames, lookback):
    returns = {}
    for pair in sorted(frames):
        f = frames[pair].sort_values('date').set_index('date')
        if not f.index.is_unique:
            raise ValueError('Duplicate candle timestamps')
        c = f['close'].replace([np.inf, -np.inf], np.nan)
        contiguous = f.index.to_series().diff().eq(pd.Timedelta(hours=4))
        valid = (contiguous.rolling(lookback).sum().eq(lookback)
                 & c.gt(0).rolling(lookback+1).sum().eq(lookback+1)
                 & f['volume'].gt(0))
        returns[pair] = (c / c.shift(lookback) - 1).where(valid)
    ret = pd.DataFrame(returns).replace([np.inf, -np.inf], np.nan)
    ranks = ret.rank(axis=1, ascending=False, method='first')
    btc = frames['BTC/USDT'].sort_values('date').set_index('date')['close']
    sma = btc.rolling(200, min_periods=200).mean()
    ready = ret.notna().all(axis=1) & sma.reindex(ret.index).notna()
    risk_on = ready & btc.reindex(ret.index).gt(sma.reindex(ret.index))
    return ret, ranks, ready, risk_on


class DailyAbsoluteMomentum(DailyRelativeStrength):
    momentum_lookback = 30

    def populate_indicators(self, dataframe, metadata):
        df = ResearchBase.populate_indicators(self, dataframe.copy(), metadata)
        frames = {p: self.dp.get_pair_dataframe(pair=p, timeframe=self.timeframe)
                  for p in self.config['exchange']['pair_whitelist']}
        ret, ranks, ready, risk_on = momentum_panel(frames, self.momentum_lookback)
        dates = df['date']
        df['rs_rank'] = dates.map(ranks[metadata['pair']])
        df['rs_momentum'] = dates.map(ret[metadata['pair']])
        df['rs_ready'] = dates.map(ready).fillna(False).astype(bool)
        df['rs_risk_on'] = dates.map(risk_on).fillna(False).astype(bool)
        return df

    def populate_entry_trend(self, dataframe, metadata):
        df = super().populate_entry_trend(dataframe, metadata)
        df.loc[~df['rs_momentum'].gt(0), 'enter_long'] = 0
        return df

    def populate_exit_trend(self, dataframe, metadata):
        df = super().populate_exit_trend(dataframe, metadata)
        df.loc[df['date'].dt.hour.eq(20) & df['rs_momentum'].le(0), 'exit_long'] = 1
        return df


class DailySlowMomentum(DailyAbsoluteMomentum):
    momentum_lookback = 120
