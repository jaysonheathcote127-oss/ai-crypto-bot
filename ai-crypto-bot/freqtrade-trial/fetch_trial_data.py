"""Public Kraken candles for a small compatibility trial; never places orders."""
import json
from datetime import datetime, timezone
from pathlib import Path
import ccxt
import pandas as pd

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT / 'config.paper.json').read_text())
assert config['dry_run'] is True
exchange = ccxt.kraken({'enableRateLimit': True, 'timeout': 30000})
folder = ROOT / 'user_data/data/kraken'
folder.mkdir(parents=True, exist_ok=True)
report = []
for pair in config['exchange']['pair_whitelist']:
    rows = exchange.fetch_ohlcv(pair, '1h', limit=720)
    frame = pd.DataFrame(rows, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    frame['date'] = pd.to_datetime(frame['date'], unit='ms', utc=True)
    frame = frame[frame.date + pd.Timedelta(hours=1) <= pd.Timestamp.now(tz='UTC')].reset_index(drop=True)
    if len(frame) < 300 or not frame.date.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError(f'{pair}: insufficient or discontinuous data')
    frame.to_feather(folder / f"{pair.replace('/', '_')}-1h.feather")
    report.append({'pair': pair, 'completed_bars': len(frame), 'start': frame.date.iloc[0].isoformat(), 'end': frame.date.iloc[-1].isoformat()})
result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'data': report,
          'limitation': 'Recent candles only. Compatibility check, not strategy validation. No historic top100 membership reconstruction.'}
(ROOT / 'data_check.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
