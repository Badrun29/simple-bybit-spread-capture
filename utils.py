def adjust_spread(volatility):
    base_spread = 0.008  # Base spread in USD
    max_spread = 0.05  # Maximum spread in USD
    spread = base_spread + (volatility * (max_spread - base_spread))
    return spread

def adjust_order_size(probability):
    base_size = 10  
    max_size = 40  
    size = base_size + (probability * (max_size - base_size))
    return size
