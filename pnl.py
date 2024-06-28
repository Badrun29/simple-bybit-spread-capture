import pandas as pd
import matplotlib.pyplot as plt

# Load trades data from CSV
trades_df = pd.read_csv('trades_log.csv')
trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])

# Calculate cumulative PnL
trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()

# Plotting the cumulative PnL
plt.figure(figsize=(10, 6))
plt.plot(trades_df['timestamp'], trades_df['cumulative_pnl'], marker='o', linestyle='-')
plt.xlabel('Time')
plt.ylabel('Cumulative PnL (USD)')
plt.title('Bot Cumulative PnL History')
plt.grid(True)
plt.show()
