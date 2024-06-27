async def get_market_price(exchange, symbol):
    ticker = await exchange.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']

async def place_order(exchange, symbol, side, price, size):
    try:
        if side == 'buy':
            return await exchange.create_limit_buy_order(symbol, size, price)
        elif side == 'sell':
            return await exchange.create_limit_sell_order(symbol, size, price)
    except Exception as e:
        print(f"Error placing order: {e}")

async def cancel_order(exchange, symbol, order_id):
    try:
        return await exchange.cancel_order(order_id, symbol)
    except Exception as e:
        print(f"Error canceling order: {e}")

async def get_open_orders(exchange, symbol):
    try:
        return await exchange.fetch_open_orders(symbol)
    except Exception as e:
        print(f"Error fetching open orders: {e}")
        return []

async def get_closed_orders(exchange, symbol):
    try:
        return await exchange.fetch_closed_orders(symbol)
    except Exception as e:
        print(f"Error fetching closed orders: {e}")
        return []

async def update_balance(exchange, symbol, balance, balance_history):
    closed_orders = await get_closed_orders(exchange, symbol)
    pnl = 0
    for order in closed_orders:
        if order['side'] == 'buy':
            pnl += (order['price'] - order['average']) * order['filled']
        else:
            pnl += (order['average'] - order['price']) * order['filled']
    balance += pnl
    balance_history.append(balance)
    return balance
