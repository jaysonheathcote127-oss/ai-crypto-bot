"""Fixed cross-sectional experiment; see RELATIVE_STRENGTH_EXPERIMENT.md."""
import math
import numpy as np
import pandas as pd
from research_baselines import ResearchBase


def ranking_panel(frames):
    pairs = sorted(frames)
    returns, valid = {}, {}
    for pair in pairs:
        f = frames[pair].sort_values('date').set_index('date')
        if not f.index.is_unique:
            raise ValueError('Duplicate candle timestamps')
        c = f['close']
        continuous = f.index.to_series().diff().eq(pd.Timedelta(hours=4))
        valid[pair] = (continuous.rolling(30).sum().eq(30)
                       & c.gt(0) & c.shift(30).gt(0) & f['volume'].gt(0))
        returns[pair] = (c / c.shift(30) - 1).where(valid[pair])
    ret = pd.DataFrame(returns).replace([np.inf, -np.inf], np.nan)
    # Sorted columns make method='first' an alphabetical tie breaker.
    ranks = ret.rank(axis=1, ascending=False, method='first')
    btc = frames['BTC/USDT'].sort_values('date').set_index('date')['close']
    sma = btc.rolling(200, min_periods=200).mean()
    ready = ret.notna().all(axis=1) & sma.reindex(ret.index).notna()
    risk_on = ready & btc.reindex(ret.index).gt(sma.reindex(ret.index))
    return ranks, ready, risk_on


class RegimeRelativeStrength(ResearchBase):
    def informative_pairs(self):
        return [(p, self.timeframe) for p in self.config['exchange']['pair_whitelist']]

    def populate_indicators(self, dataframe, metadata):
        df = super().populate_indicators(dataframe.copy(), metadata)
        frames = {p: self.dp.get_pair_dataframe(pair=p, timeframe=self.timeframe)
                  for p in self.config['exchange']['pair_whitelist']}
        ranks, ready, risk_on = ranking_panel(frames)
        dates = df['date']
        df['rs_rank'] = dates.map(ranks[metadata['pair']])
        df['rs_ready'] = dates.map(ready).fillna(False).astype(bool)
        df['rs_risk_on'] = dates.map(risk_on).fillna(False).astype(bool)
        return df

    def populate_entry_trend(self, dataframe, metadata):
        df = dataframe
        top = math.ceil(len(self.config['exchange']['pair_whitelist']) / 4)
        df['enter_long'] = 0
        df.loc[df['rs_ready'] & df['rs_risk_on'] & df['rs_rank'].le(top)
               & df['close'].gt(df['sma50']) & df['volume'].gt(0),
               ['enter_long', 'enter_tag']] = (1, 'regime_relative_strength')
        return df

    def populate_exit_trend(self, dataframe, metadata):
        df = dataframe
        half = math.ceil(len(self.config['exchange']['pair_whitelist']) / 2)
        df['exit_long'] = 0
        df.loc[~df['rs_ready'] | ~df['rs_risk_on'] | df['rs_rank'].gt(half)
               | df['close'].lt(df['sma50']), 'exit_long'] = 1
        return df
