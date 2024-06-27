import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

async def fetch_historical_data(exchange, symbol, lookback_period):
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe='1s', limit=lookback_period + 1000)
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def add_features(data):
    data['return'] = data['close'].pct_change()
    data['volatility'] = data['close'].rolling(window=10).std()
    data['momentum'] = data['close'] / data['close'].shift(10) - 1
    data['sma'] = data['close'].rolling(window=10).mean()
    data['ema'] = data['close'].ewm(span=10).mean()
    data.dropna(inplace=True)
    return data

def prepare_lstm_data(data, lookback_period):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['close', 'return', 'volatility', 'momentum', 'sma', 'ema']])

    X, y = [], []
    for i in range(lookback_period, len(scaled_data)):
        X.append(scaled_data[i-lookback_period:i])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test, scaler
