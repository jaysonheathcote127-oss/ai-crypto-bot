
import ccxt
import pandas as pd


def main():
    exchange = ccxt.coinbase({
        "enableRateLimit": True,
    })

    symbol = "BTC/USD"
    timeframe = "5m"

    print(f"Fetching {symbol} candles from Coinbase...")

    candles = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=20,
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], unit="ms", utc=True
    )

    print("\nLatest 10 candles:")
    print(df.tail(10).to_string(index=False))

    latest = df.iloc[-1]

    print(f"\nLatest candle close: ${latest['close']:,.2f}")
    print("Market data retrieved successfully.")
    print("Paper trading only. No orders placed.")


if __name__ == "__main__":
    main()


