import pandas as pd

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    data['SMA'] = data['close'].rolling(window=window).mean()
    data['StdDev'] = data['close'].rolling(window=window).std()
    data['UpperBand'] = data['SMA'] + (num_std_dev * data['StdDev'])
    data['LowerBand'] = data['SMA'] - (num_std_dev * data['StdDev'])
    return data
