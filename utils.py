def adjust_spread(volatility):
    base_spread = 0.4  # Base spread in USD
    max_spread = 0.8  # Maximum spread in USD
    spread = base_spread + (volatility * (max_spread - base_spread))
    return spread

def adjust_order_size(probability, num_orders):
    base_size = 3.5  
    max_size = 5  
    total_size = base_size + (probability * (max_size - base_size))
    
    # Define ratios for increasing order sizes (example: [0.2, 0.3, 0.5])
    ratios = [i/sum(range(1, num_orders+1)) for i in range(1, num_orders+1)]
    
    # Compute sizes based on provided ratios
    order_sizes = [total_size * ratio for ratio in ratios]
    return order_sizes
