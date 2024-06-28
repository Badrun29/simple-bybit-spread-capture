import ccxt.async_support as ccxt
import asyncio

async def place_order(exchange, symbol, side, price, size):
    try:
        order = await exchange.create_limit_order(symbol, side, size, price)
        return order
    except Exception as e:
        print(f"Failed to place {side} order: {e}")
        return None

async def place_orders(exchange, orders):
    tasks = [place_order(exchange, order['symbol'], order['side'], order['price'], order['size']) for order in orders]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Error occurred: {result}")
    return results

async def cancel_order(exchange, symbol, order_id):
    try:
        result = await exchange.cancel_order(order_id, symbol)
        return result
    except Exception as e:
        print(f"Failed to cancel order {order_id}: {e}")
        return None

async def get_open_orders(exchange, symbol):
    try:
        orders = await exchange.fetch_open_orders(symbol)
        return orders
    except Exception as e:
        print(f"Failed to fetch open orders: {e}")
        return []

async def get_market_price(exchange, symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']
    except Exception as e:
        print(f"Failed to fetch market price: {e}")
        return None, None

async def update_balance(exchange, symbol, current_balance, balance_history):
    try:
        balance = await exchange.fetch_balance()
        new_balance = balance['total']['USDT']  # Adjust according to your base currency
        balance_history.append(new_balance)
        return new_balance
    except Exception as e:
        print(f"Failed to update balance: {e}")
        return current_balance
