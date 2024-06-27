from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Input

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(LSTM(units=50))
    model.add(Dense(1, activation='sigmoid'))  # Sigmoid activation for probability
    model.compile(optimizer='adam', loss='binary_crossentropy')  # Binary crossentropy for probability
    return model

def predict_probability(model, data, scaler, lookback_period):
    scaled_data = scaler.transform(data[['close', 'return', 'volatility', 'momentum', 'sma', 'ema']])
    X = scaled_data[-lookback_period:].reshape(1, lookback_period, 6)
    prediction = model.predict(X)
    probability = prediction[0][0]  # Extract probability
    return probability
