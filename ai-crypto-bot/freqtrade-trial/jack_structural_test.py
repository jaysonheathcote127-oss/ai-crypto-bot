"""Frozen, explicitly approximate structural crypto experiment. No order API."""
import asyncio
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import ccxt.async_support as ccxt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'data/research/jack_structural'
START = pd.Timestamp('2026-07-14', tz='UTC')
SCORE = pd.Timestamp('2026-07-21', tz='UTC')
END = pd.Timestamp('2026-10-19', tz='UTC')
PAIRS = ('BTC-USDT', 'ETH-USDT')
COLS = ['open', 'high', 'low', 'close', 'volume']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = ['JACK_STRUCTURAL_EXPERIMENT.md', 'jack_structural_test.py', 'test_jack_structural.py']
    hashes = {p: digest(ROOT / p) for p in paths}
    dest = OUT / 'frozen_source.json'
    if dest.exists():
        if json.loads(dest.read_text()) != hashes:
            raise ValueError('Frozen source changed; stop rather than silently overwrite')
    else:
        dest.write_text(json.dumps(hashes, indent=2))


def validate(frame, start=START, end=END):
    expected = pd.date_range(start, end, freq='5min', inclusive='left')
    if not frame.index.equals(expected):
        raise ValueError('Missing, unordered, duplicate or misaligned candles')
    if not np.isfinite(frame[COLS].to_numpy()).all():
        raise ValueError('Nonfinite data')
    if (frame[COLS[:4]] <= 0).any().any() or (frame.volume < 0).any():
        raise ValueError('Invalid prices/volume')
    if (frame.high < frame[['open', 'close', 'low']].max(axis=1)).any() or (frame.low > frame[['open', 'close', 'high']].min(axis=1)).any():
        raise ValueError('Invalid OHLC')


async def download():
    freeze()
    ex = ccxt.okx({'enableRateLimit': True, 'timeout': 20000})
    async def one(pair):
        rawfile = OUT / f'{pair}-raw.json'
        if rawfile.exists():
            raw = json.loads(rawfile.read_text())
        else:
            cursor = int(END.timestamp() * 1000)
            raw = []
            for n in range(150):
                for attempt in range(3):
                    try:
                        response = await ex.public_get_market_history_candles(
                            {'instId': pair, 'bar': '5m', 'after': str(cursor), 'limit': '300'})
                        break
                    except Exception:
                        if attempt == 2:
                            raise
                        await asyncio.sleep(1)
                page = response['data']
                if not page:
                    raise ValueError('Empty public history page')
                oldest = min(int(r[0]) for r in page)
                if oldest >= cursor:
                    raise ValueError('Pagination failed to advance')
                raw.extend(page)
                cursor = oldest
                if n % 20 == 0:
                    print(pair, 'page', n + 1, pd.Timestamp(cursor, unit='ms', tz='UTC'), flush=True)
                if cursor <= int(START.timestamp() * 1000):
                    break
            else:
                raise ValueError('Public history page cap reached')
            rawfile.write_text(json.dumps(raw))
        selected = [r for r in raw if int(START.timestamp()*1000) <= int(r[0]) < int(END.timestamp()*1000)]
        if any(r[8] != '1' for r in selected):
            raise ValueError('Unconfirmed candle')
        frame = pd.DataFrame([[int(r[0]), *map(float, r[1:6])] for r in selected], columns=['date', *COLS])
        frame['date'] = pd.to_datetime(frame.date, unit='ms', utc=True)
        frame = frame.set_index('date').sort_index()
        validate(frame)
        frame.to_csv(OUT / f'{pair}-5m.csv')
        print(pair, 'validated', len(frame), flush=True)
    try:
        await asyncio.gather(*(one(p) for p in PAIRS))
    finally:
        await ex.close()
    manifest = {p.name: digest(p) for p in sorted(OUT.glob('*')) if p.suffix in ('.csv', '.json') and p.name != 'data_manifest.json'}
    (OUT / 'data_manifest.json').write_text(json.dumps(manifest, indent=2))


def resample(frame, minutes):
    # Source indexes are bar opens; resampled values become available at close.
    result = frame.resample(f'{minutes}min', label='left', closed='left').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
    count = frame.close.resample(f'{minutes}min').count()
    result = result[count == minutes // 5]
    result.index += pd.Timedelta(minutes=minutes)
    return result


def rejection(o, h, l, c):
    span = h - l
    return span > 0 and c > o and (c - o) >= .5 * span and h - c <= .2 * span


def features(frame):
    f = frame.copy()
    tr = pd.concat([f.high-f.low, (f.high-f.close.shift()).abs(), (f.low-f.close.shift()).abs()], axis=1).max(axis=1)
    f['atr'] = tr.rolling(14).mean()
    h, l = f.high.to_numpy(), f.low.to_numpy()
    ph = np.full(len(f), np.nan); pl = ph.copy()
    for i in range(4, len(f)):
        # Pivot at i-2 is first observable NOW, after both right bars have closed.
        if h[i-2] == max(h[i-4:i+1]) and np.sum(h[i-4:i+1] == h[i-2]) == 1:
            ph[i] = h[i-2]
        if l[i-2] == min(l[i-4:i+1]) and np.sum(l[i-4:i+1] == l[i-2]) == 1:
            pl[i] = l[i-2]
    f['pivot_high'] = pd.Series(ph, index=f.index).ffill()
    f['pivot_low'] = pd.Series(pl, index=f.index).ffill()
    prior_high = f.pivot_high.shift()
    prior_low = f.pivot_low.shift()
    span = f.high-f.low
    bull = ((f.close > f.open) & (f.close > prior_high) & (f.open <= prior_high)
            & ((f.close-prior_high) >= .5*(f.close-f.open)) & ((f.high-f.close) <= .2*span))
    bear = ((f.close < f.open) & (f.close < prior_low) & (f.open >= prior_low)
            & ((prior_low-f.close) >= .5*(f.open-f.close)) & ((f.close-f.low) <= .2*span))
    f['bull_bos'] = bull
    state = 0; protected = np.nan; last_bos = -10000
    states = []; levels = []; ages = []
    for i in range(len(f)):
        if state == 1 and f.close.iloc[i] < protected or state == -1 and f.close.iloc[i] > protected:
            state = 0
        if bull.iloc[i] and np.isfinite(prior_low.iloc[i]):
            state, protected, last_bos = 1, float(prior_low.iloc[i]), i
        elif bear.iloc[i] and np.isfinite(prior_high.iloc[i]):
            state, protected, last_bos = -1, float(prior_high.iloc[i]), i
        states.append(state); levels.append(protected); ages.append(i-last_bos)
    f['state'] = states; f['protected'] = levels; f['bos_age'] = ages
    return f


def aligned_features(frame):
    closeframe = frame.copy()
    closeframe.index += pd.Timedelta(minutes=5)
    base = features(closeframe)
    mid = features(resample(frame, 15))
    hourly = features(resample(frame, 60))
    mid['range_low'] = mid.low.shift().rolling(20).min()
    mid['range_high'] = mid.high.shift().rolling(20).max()
    visits = np.zeros(len(mid))
    for i in range(20, len(mid)):
        win = mid.iloc[i-20:i]
        tolerance = .15 * mid.atr.iloc[i-1]
        lows = (win.low <= mid.range_low.iloc[i]+tolerance).to_numpy()
        highs = (win.high >= mid.range_high.iloc[i]-tolerance).to_numpy()
        nl = int(np.sum(lows & ~np.r_[False, lows[:-1]]))
        nh = int(np.sum(highs & ~np.r_[False, highs[:-1]]))
        visits[i] = nl+nh if nl >= 1 and nh >= 1 else 0
    mid['visits'] = visits
    mid['range_atr'] = mid.atr.shift()
    # Join only completed higher-timeframe candles, no forward/backward leakage.
    for label, other in [('m', mid), ('h', hourly)]:
        base = base.join(other.add_prefix(label+'_').reindex(base.index, method='ffill'))
    base['recent_bos5'] = base.bull_bos.rolling(12, min_periods=1).max().astype(bool)
    return base


def signals(frame):
    f = aligned_features(frame)
    rows = []
    funnel = {'closed_bars': len(f), 'range_sweeps': 0, 'trend_sweeps': 0, 'rejection_context_pass': 0}
    for i in range(1, len(f)):
        setup, conf = f.iloc[i-1], f.iloc[i]
        if not rejection(conf.open, conf.high, conf.low, conf.close) or conf.close <= setup.close:
            continue
        if not (np.isfinite(setup.atr) and np.isfinite(conf.h_pivot_high) and conf.h_pivot_high > conf.close):
            continue
        for model in ['NC', 'SBC']:
            if model == 'NC':
                level = setup.m_range_low
                if not (setup.m_state == 0 and setup.m_visits >= 3 and
                        setup.m_range_high-level >= 2*setup.m_range_atr):
                    continue
                target = setup.m_range_high
            else:
                level = setup.m_protected
                if not (setup.m_state == 1 and setup.m_bos_age <= 16 and setup.recent_bos5):
                    continue
                candidates = [x for x in [conf.m_pivot_high, conf.h_pivot_high] if np.isfinite(x) and x > conf.close]
                if not candidates:
                    continue
                target = min(candidates)
            if not (np.isfinite(level) and setup.low < level and setup.close > level):
                continue
            funnel['range_sweeps' if model == 'NC' else 'trend_sweeps'] += 1
            stop = min(level, setup.low)-.05*setup.atr
            rows.append({'signal_time': f.index[i], 'model': model, 'stop': stop,
                         'target': target, 'be_trigger': conf.pivot_high})
            funnel['rejection_context_pass'] += 1
    return pd.DataFrame(rows, columns=['signal_time', 'model', 'stop', 'target', 'be_trigger']), funnel


def session(t):
    for name, tz, start, end in [('Asia', 'Asia/Tokyo', 480, 600),
                                ('London', 'Europe/London', 420, 540),
                                ('NY', 'America/New_York', 510, 630)]:
        local = t.tz_convert(ZoneInfo(tz))
        minutes = local.hour*60+local.minute
        if local.weekday() < 5 and start <= minutes < end:
            return f'{name}:{local.date()}'
    return None


def exit_fill(bar, stop, target):
    if bar.open <= stop:
        return float(bar.open), 'gap_stop'
    if bar.low <= stop:
        return stop, 'stop'
    if bar.high >= target:
        return target, 'target'
    return None


def simulate(frames, allsignals, model, fee, start=SCORE, end=END):
    cash = 1000.; pos = None; trades = []; marks = []; used = set()
    lookup = {pair: {r.signal_time: r for r in sig[sig.model == model].itertuples()} for pair, sig in allsignals.items()}
    rejected = {'outside_session': 0, 'session_used': 0, 'position_open': 0, 'rr_or_gap': 0}
    def close(t, price, reason):
        nonlocal cash, pos
        proceeds = pos['qty']*price*(1-fee)
        pnl = proceeds-pos['cost']
        cash += proceeds
        trades.append({**pos, 'exit_time': t, 'exit': price, 'reason': reason, 'pnl': pnl,
                       'fees': pos['qty']*pos['entry']*fee+pos['qty']*price*fee,
                       'net_r': pnl/pos['initial_risk']})
        pos = None
    for t in pd.date_range(start, end, freq='5min', inclusive='left'):
        # Signals at t use only data whose candles closed at or before t.
        for pair in PAIRS:
            sig = lookup[pair].get(t)
            if sig is None:
                continue
            key = session(t)
            if key is None:
                rejected['outside_session'] += 1; continue
            if key in used:
                rejected['session_used'] += 1; continue
            if pos is not None:
                rejected['position_open'] += 1; continue
            price = float(frames[pair].loc[t, 'open'])
            if not (sig.stop < price < sig.target) or (sig.target-price)/(price-sig.stop) < 1.3:
                rejected['rr_or_gap'] += 1; continue
            unit_risk = price*(1+fee)-sig.stop*(1-fee)
            qty = min(.005*cash/unit_risk, cash/(price*(1+fee)))
            risk = qty*unit_risk
            cost = qty*price*(1+fee)
            pos = {'pair': pair, 'entry_time': t, 'entry': price, 'qty': qty,
                   'cost': cost, 'stop': float(sig.stop), 'original_stop': float(sig.stop),
                   'target': float(sig.target), 'be_trigger': float(sig.be_trigger),
                   'initial_risk': risk, 'notional': qty*price, 'be_moved': False}
            cash -= cost; used.add(key)
        if pos is not None:
            bar = frames[pos['pair']].loc[t]
            result = exit_fill(bar, pos['stop'], pos['target'])
            if result:
                close(t+pd.Timedelta(minutes=5), *result)
            elif np.isfinite(pos['be_trigger']) and bar.close > pos['be_trigger']:
                # Observed only at bar close: applies to the NEXT loop/bar.
                be = pos['entry']*(1+fee)/(1-fee)
                if pos['stop'] < be < bar.close:
                    pos['stop'] = be; pos['be_moved'] = True
        mark = cash
        if pos:
            mark += pos['qty']*frames[pos['pair']].loc[t, 'close']*(1-fee)
        marks.append({'date': t+pd.Timedelta(minutes=5), 'equity': mark,
                      'exposed': pos is not None})
    if pos:
        last = end-pd.Timedelta(minutes=5)
        close(end, float(frames[pos['pair']].loc[last, 'close']), 'end_of_test')
        marks[-1]['equity'] = cash; marks[-1]['exposed'] = False
    equity = pd.DataFrame(marks).set_index('date')
    # Include starting cash so early losses count towards peak drawdown.
    curve = np.r_[1000., equity.equity.to_numpy()]
    dd = 1-curve/np.maximum.accumulate(curve)
    wins = sum(t['pnl'] > 1e-8 for t in trades)
    losses = sum(t['pnl'] < -1e-8 for t in trades)
    grosswin = sum(max(0, t['pnl']) for t in trades)
    grossloss = -sum(min(0, t['pnl']) for t in trades)
    blocks = []
    previous = 1000.
    for a, b in [(SCORE, pd.Timestamp('2026-08-20', tz='UTC')),
                 (pd.Timestamp('2026-08-20', tz='UTC'), pd.Timestamp('2026-09-19', tz='UTC')),
                 (pd.Timestamp('2026-09-19', tz='UTC'), END)]:
        if a < start or b > end:
            continue
        balance = float(equity.loc[b, 'equity'])
        blocks.append({'start': str(a), 'end': str(b), 'marked_return_pct': 100*(balance/previous-1),
                       'closed_trades': sum(a < t['exit_time'] <= b for t in trades)})
        previous = balance
    summary = {'model': model, 'fee_per_side': fee, 'trades': len(trades), 'wins': wins,
               'losses': losses, 'breakeven': len(trades)-wins-losses,
               'return_pct': 100*(cash/1000-1), 'final_equity': cash,
               'close_drawdown_pct': 100*float(max(dd)), 'fees': sum(t['fees'] for t in trades),
               'profit_factor': grosswin/grossloss if grossloss else None,
               'mean_net_r': float(np.mean([t['net_r'] for t in trades])) if trades else None,
               'exposure_pct': 100*float(equity.exposed.mean()), 'blocks': blocks,
               'pair_pnl': {p: sum(t['pnl'] for t in trades if t['pair'] == p) for p in PAIRS},
               'rejections': rejected,
               'pnl_reconciliation_error': cash-1000-sum(t['pnl'] for t in trades)}
    return summary, trades, equity


def run():
    freeze()
    manifest = json.loads((OUT/'data_manifest.json').read_text())
    for name, expected in manifest.items():
        if digest(OUT/name) != expected:
            raise ValueError('Frozen data changed: '+name)
    frames = {}; sigs = {}; funnels = {}
    for pair in PAIRS:
        frame = pd.read_csv(OUT/f'{pair}-5m.csv', index_col='date', parse_dates=['date'])
        validate(frame)
        frames[pair] = frame
        sigs[pair], funnels[pair] = signals(frame)
        sigs[pair].to_csv(OUT/f'{pair}-signals.csv', index=False)
    results = []
    for model in ['NC', 'SBC']:
        for label, fee in [('base', .0015), ('stress', .0045)]:
            summary, trades, equity = simulate(frames, sigs, model, fee)
            label = f'{model}-{label}'
            pd.DataFrame(trades).to_csv(OUT/f'{label}-trades.csv', index=False)
            equity.to_csv(OUT/f'{label}-equity.csv')
            results.append(summary)
            print(label, json.dumps(summary), flush=True)
    (OUT/'summary.json').write_text(json.dumps({'funnel': funnels, 'results': results}, indent=2))


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['download']:
        asyncio.run(download())
    elif sys.argv[1:] == ['run']:
        run()
    else:
        raise SystemExit('Use download or run; public-data research only')
