"""Real-input causality and output accounting audit, plus a readable report."""
import json
import pandas as pd
from jack_structural_test import (ROOT, OUT, PAIRS, SCORE, END, digest, signals, session)


def main():
    source = ROOT/'audit_jack_structural.py'
    own = OUT/'audit_source_hash.json'
    expected = {source.name: digest(source)}
    if own.exists():
        assert json.loads(own.read_text()) == expected
    else:
        own.write_text(json.dumps(expected, indent=2))
    # This audit hash is created before the evaluator results are read.
    results = json.loads((OUT/'summary.json').read_text())
    audit = {'causality': {}, 'accounting': {}, 'scope': 'Custom simulator, no full Freqtrade engine audit'}
    for pair in PAIRS:
        f = pd.read_csv(OUT/f'{pair}-5m.csv', index_col='date', parse_dates=['date'])
        full, _ = signals(f)
        n = len(f)//2+1  # deliberately an arbitrary prefix, not a tuned breakpoint
        prefix, _ = signals(f.iloc[:n])
        cutoff = f.index[n-1]+pd.Timedelta(minutes=5)
        past = full[full.signal_time <= cutoff].reset_index(drop=True)
        pd.testing.assert_frame_equal(past, prefix.reset_index(drop=True))
        shock = f.copy()
        shock.iloc[n:, :4] *= 7
        changed, _ = signals(shock)
        pd.testing.assert_frame_equal(past, changed[changed.signal_time <= cutoff].reset_index(drop=True))
        audit['causality'][pair] = {'prefix_bars': n, 'prefix_signals': len(past),
                                    'prefix_equal': True, 'future_shock_equal': True}
    for r in results['results']:
        name = r['model']+('-base' if r['fee_per_side'] == .0015 else '-stress')
        path = OUT/f'{name}-trades.csv'
        if r['trades'] == 0:
            audit['accounting'][name] = {'trades': 0, 'reconciled': r['final_equity'] == 1000.}
            continue
        t = pd.read_csv(path, parse_dates=['entry_time', 'exit_time'])
        assert len(t) == r['trades']
        assert abs(t.pnl.sum()-(r['final_equity']-1000)) < 1e-7
        fee = r['fee_per_side']
        expected_pnl = t.qty*(t['exit']*(1-fee)-t.entry*(1+fee))
        assert (expected_pnl-t.pnl).abs().max() < 1e-7
        assert ((t.target-t.entry)/(t.entry-t.original_stop) >= 1.3-1e-10).all()
        keys = t.entry_time.map(session)
        assert keys.notna().all() and keys.is_unique
        assert (t.entry_time >= SCORE).all() and (t.exit_time <= END).all()
        assert (t.exit_time > t.entry_time).all()
        assert all(t.entry_time.iloc[i] >= t.exit_time.iloc[i-1] for i in range(1, len(t)))
        sigs = {p: pd.read_csv(OUT/f'{p}-signals.csv', parse_dates=['signal_time']) for p in PAIRS}
        for row in t.itertuples():
            s = sigs[row.pair]
            match = s[(s.model == r['model']) & (s.signal_time == row.entry_time)]
            assert len(match) == 1
            assert abs(match.iloc[0].stop-row.original_stop) < 1e-7
        audit['accounting'][name] = {'trades': len(t), 'reconciled': True,
                                    'cost_formula': True, 'session_unique': True,
                                    'entry_signal_match': True, 'minimum_rr': True}
    (OUT/'audit.json').write_text(json.dumps(audit, indent=2))
    lines = ['# Jack-informed intraday crypto test — 19 October 2026', '',
             'Completed a fixed-rule research test using the newly collected Discord material. '
             'This is a mechanised long-only BTC/ETH adaptation, not a reproduction of Jack’s discretionary gold trading.', '',
             'Scored 21 July–19 October 2026 (end exclusive), with seven days of warmup. '
             'Two models, one independent $1,000 wallet each, 0.5% planned equity risk including costs '
             'and a cash cap. No leverage, shorts, optimisation or live orders.', '',
             '| Model | Costs each side | Trades | Net return | 5m-close drawdown | Profit factor | Fees |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for r in results['results']:
        pf = f"{r['profit_factor']:.2f}" if r['profit_factor'] is not None else 'n/a'
        lines.append(f"| {r['model']} | {100*r['fee_per_side']:.2f}% | {r['trades']} | {r['return_pct']:+.2f}% | {r['close_drawdown_pct']:.2f}% | {pf} | ${r['fees']:.2f} |")
    lines += ['', 'NC = formed-range sweep and rejection; SBC = protected-structure continuation. '
              'Fees include the assumed adverse execution-cost allowance; they are not verified account fee tiers.', '',
              '| Model/cost | Jul 21–Aug 20 | Aug 20–Sep 19 | Sep 19–Oct 19 |',
              '|---|---:|---:|---:|']
    for r in results['results']:
        name = r['model']+(' base' if r['fee_per_side'] == .0015 else ' stress')
        lines.append('| '+name+' | '+' | '.join(f"{b['marked_return_pct']:+.2f}% ({b['closed_trades']} exits)" for b in r['blocks'])+' |')
    lines += ['', 'Block returns use the same continuous wallet and include unrealised positions marked at each boundary. '
              'They are not separate fresh-wallet tests, and this history is not an untouched holdout.', '',
              '## Interpretation', '']
    passed = []
    for model in ['NC', 'SBC']:
        group = [r for r in results['results'] if r['model'] == model]
        if all(r['trades'] >= 30 and r['return_pct'] > 0 and all(b['marked_return_pct'] > 0 for b in r['blocks']) for r in group):
            passed.append(model)
    if passed:
        lines.append('Models meeting the predeclared exploratory count/positive-block screen: '+', '.join(passed)+'. This only motivates further research; no promotion or income claim.')
    else:
        lines.append('Neither model meets the predeclared exploratory screen (at least 30 trades and positive returns in every block at both costs). No promotion. A small sample is insufficient evidence, not proof that Jack’s full system fails.')
    lines += ['', '## What was actually tested', '',
              '- Completed 5m entries with closed 15m/1h context; delayed confirmed pivots; sweep then a separate strong rejection candle; next-open entries; structural stops and targets; minimum 1.3R; fixed structural take-profit; next-bar cost-covering breakeven after an internal-break proxy.',
              '- One trade per market-local session, weekdays only, one concurrent position across BTC/ETH; BTC priority when both qualify. Indicator-default windows selected before results.',
              '- Stop-first handling when target and stop fall in the same bar, adverse gap fills, entry-bar stops and forced closure at the test end. Drawdown samples 5m closes and can miss intrabar lows.', '',
              '## What remains untested', '',
              '- Gold/FX, DXY, discretionary weak/protected structure, chart grading, divergence, shorts and historical news filtering. Confirmed pivot highs are a target proxy, not verified equivalents of Jack’s weak structure.',
              '- Pivot width, range lookback/touch tolerance, ATR buffer and BOS recency are fixed researcher assumptions. No thresholds were fitted to these returns.',
              '- Jack’s source conflicts (1R versus 1.3R, risk caps, EMA timeframe and sessions) remain unresolved. This pass chose explicit rules rather than combining conflicting versions.',
              '- Funding, leverage, tick execution, spreads/order-book liquidity, provider payout rules, taxes and withdrawals are not modelled. No earnings forecast follows from this test.', '',
              '## Validation and provenance', '',
              'Eight synthetic checks passed before results. Real-input prefix and future-shock signal checks passed on both pairs; output audit reconciles individual trade fee cashflows, ending balances, entry signals, minimum R and one-entry-per-session constraints. This is not an independent implementation or full engine audit.', '',
              f"Each pair contains {len(f):,} validated five-minute candles. Raw exchange JSON, normalised CSV, source/data SHA256 manifests, signals, trades, close-equity curves, summary and audit are in `ai-crypto-bot/freqtrade-trial/data/research/jack_structural/`.", '',
              'Protocol: `ai-crypto-bot/freqtrade-trial/JACK_STRUCTURAL_EXPERIMENT.md`. '
              'Source research: `outputs/jack-savage-discord-research-2026-10-19.md`. '
              'Public candle schema: [OKX API documentation](https://app.okx.com/docs-v5/en).', '',
              'Next useful step: resolve the source ambiguities and obtain labelled gold examples/data with DXY and news context, before claiming fidelity to the source strategy. Keep this adaptation frozen; do not tune it against the same period.']
    (ROOT.parents[1]/'outputs/jack-structural-test-report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
