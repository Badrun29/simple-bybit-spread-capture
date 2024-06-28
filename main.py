import asyncio
import pandas as pd
from config import exchange, symbol, lookback_period, num_orders, data_update_interval, balance, balance_history
from data_handler import fetch_historical_data, add_features, prepare_lstm_data
from model import build_lstm_model, predict_probability
from trading import get_market_price, place_order, cancel_order, get_open_orders, update_balance
from utils import adjust_spread, adjust_order_size
from datetime import datetime

class InventoryManager:
    def __init__(self):
        self.position = 0
        self.entry_price = 0
        self.stop_loss_price = 0
        self.trailing_stop_loss = 0
        self.trades = []

    def update_position(self, size, side, price):
        if side == 'buy':
            self.position += size
            self.entry_price = price
        elif side == 'sell':
            self.position -= size
            self.entry_price = price

    def set_stop_loss(self, price, is_trailing=False):
        if is_trailing:
            if self.position > 0 and price > self.trailing_stop_loss:
                self.trailing_stop_loss = price
            elif self.position < 0 and price < self.trailing_stop_loss:
                self.trailing_stop_loss = price
        else:
            self.stop_loss_price = price

    def get_position(self):
        return self.position

    def get_entry_price(self):
        return self.entry_price

    def get_stop_loss_price(self):
        return self.stop_loss_price

    def get_trailing_stop_loss(self):
        return self.trailing_stop_loss

inventory_manager = InventoryManager()

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

            # Adjust order sizes based on the volatility and number of orders
            order_sizes = adjust_order_size(volatility, num_orders)

            tasks = []
            for i in range(num_orders):
                buy_price = mid_price - step_size * (i + 1)
                sell_price = mid_price + step_size * (i + 1)
                order_size = order_sizes[i]
                
                if probability > 0.5:
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'buy', buy_price, order_size)))
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'sell', sell_price, order_size)))
                    inventory_manager.update_position(order_size, 'buy', buy_price)
                else:
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'sell', sell_price, order_size)))
                    tasks.append(asyncio.create_task(place_order(exchange, symbol, 'buy', buy_price, order_size)))
                    inventory_manager.update_position(order_size, 'sell', sell_price)

            await asyncio.gather(*tasks)
            await asyncio.sleep(0)  # Short sleep to prevent overwhelming the exchange

            global balance
            balance = await update_balance(exchange, symbol, balance, balance_history)  # Update balance based on closed orders

            # Check and update stop loss and trailing stop loss
            current_price = mid_price  # Assume mid_price as the current price
            if inventory_manager.get_position() > 0:
                inventory_manager.set_stop_loss(inventory_manager.get_entry_price() * 0.99)  # 1% stop loss
                inventory_manager.set_stop_loss(current_price * 0.99, is_trailing=True)  # 1% trailing stop
            elif inventory_manager.get_position() < 0:
                inventory_manager.set_stop_loss(inventory_manager.get_entry_price() * 1.01)  # 1% stop loss
                inventory_manager.set_stop_loss(current_price * 1.01, is_trailing=True)  # 1% trailing stop

            # Close position based on stop loss
            if inventory_manager.get_position() > 0 and current_price <= inventory_manager.get_stop_loss_price():
                close_size = abs(inventory_manager.get_position())
                await place_order(exchange, symbol, 'sell', current_price, close_size)
                pnl = (current_price - inventory_manager.get_entry_price()) * close_size
                inventory_manager.log_trade(datetime.now(), 'sell', close_size, current_price, pnl)
                inventory_manager.update_position(-close_size, 'sell', current_price)
            elif inventory_manager.get_position() < 0 and current_price >= inventory_manager.get_stop_loss_price():
                close_size = abs(inventory_manager.get_position())
                await place_order(exchange, symbol, 'buy', current_price, close_size)
                pnl = (inventory_manager.get_entry_price() - current_price) * close_size
                inventory_manager.log_trade(datetime.now(), 'buy', close_size, current_price, pnl)
                inventory_manager.update_position(-close_size, 'buy', current_price)

    except Exception as e:
        print(f"Error: {e}")
        await asyncio.sleep(0)
        await run_bot(model, scaler)

async def main():
    historical_data = await fetch_historical_data(exchange, symbol, lookback_period)
    data_with_features = add_features(historical_data)
    X_train, X_test, y_train, y_test, scaler = prepare_lstm_data(data_with_features, lookback_period)

    lstm_model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    lstm_model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

    # Run the trading bot
    await run_bot(lstm_model, scaler)

if __name__ == "__main__":
    asyncio.run(main())
