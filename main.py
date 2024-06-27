import asyncio
import pandas as pd
from config import exchange, symbol, lookback_period, num_orders, data_update_interval, balance, balance_history
from data_handler import fetch_historical_data, add_features, prepare_lstm_data
from model import build_lstm_model, predict_probability
from trading import get_market_price, place_order, cancel_order, get_open_orders, update_balance
from utils import adjust_spread, adjust_order_size

async def run_bot(model, scaler):
    last_data_update = 0
    historical_data = await fetch_historical_data(exchange, symbol, lookback_period)
    
    try:
        while True:
            current_time = asyncio.get_event_loop().time()
            if current_time - last_data_update > data_update_interval:
                historical_data = await fetch_historical_data(exchange, symbol, lookback_period)
                last_data_update = current_time
            
            bid, ask = await get_market_price(exchange, symbol)
            data_with_features = add_features(historical_data)
            probability = predict_probability(model, data_with_features, scaler, lookback_period)

            mid_price = (bid + ask) / 2
            volatility = data_with_features['volatility'].iloc[-1]
            current_spread = adjust_spread(volatility)
            step_size = current_spread / num_orders

            open_orders = await get_open_orders(exchange, symbol)
            await asyncio.gather(*(cancel_order(exchange, symbol, order['id']) for order in open_orders))

            tasks = []
            for i in range(num_orders):
                buy_price = mid_price - step_size * (i + 1)
                sell_price = mid_price + step_size * (i + 1)
                order_size = adjust_order_size(probability)
                if probability > 0.5:
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'buy', buy_price, order_size)))
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'sell', sell_price, order_size)))
                else:
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'sell', sell_price, order_size)))
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'buy', buy_price, order_size)))

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1)  # Short sleep to prevent overwhelming the exchange

            global balance
            balance = await update_balance(exchange, symbol, balance, balance_history)  # Update balance based on closed orders

    except Exception as e:
        print(f"Error: {e}")
        await asyncio.sleep(1)
        await run_bot(model, scaler)

async def main():
    historical_data = await fetch_historical_data(exchange, symbol, lookback_period)
    data_with_features = add_features(historical_data)
    X_train, X_test, y_train, y_test, scaler = prepare_lstm_data(data_with_features, lookback_period)

    lstm_model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    lstm_model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

    # Run the trading bot
    await run_bot(lstm_model, scaler)

    # Print balance growth statistics
    balance_df = pd.DataFrame(balance_history, columns=['Balance'])
    print(balance_df)

if __name__ == "__main__":
    asyncio.run(main())
