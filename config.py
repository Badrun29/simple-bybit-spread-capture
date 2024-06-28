import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# Set up your Bybit API keys
api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

# Initialize the Bybit exchange
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

symbol = 'SOLUSDT'
lookback_period = 1  # Lookback period for LSTM
num_orders = 4  # Total number of orders to place
data_update_interval = 0.1  # Update historical data every 1 second

initial_balance = 525  # Example initial balance in USD
balance = initial_balance
balance_history = []
