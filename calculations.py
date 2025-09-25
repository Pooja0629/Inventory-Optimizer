import numpy as np
from scipy import stats

def calculate_safety_stock(demand_data, lead_time, service_level):
    """
    Calculate safety stock using statistical method:
    Safety Stock = Z * σ * sqrt(lead_time)
    Returns integer values for practical inventory management
    """
    try:
        if len(demand_data) == 0:
            return 0
            
        # Calculate standard deviation of demand
        std_demand = np.std(demand_data)
        
        # Z-score for service level
        z_score = stats.norm.ppf(service_level)
        
        # Safety stock formula
        safety_stock = z_score * std_demand * np.sqrt(lead_time)
        
        # Return as integer (rounded up for safety), minimum 1
        return max(1, int(np.ceil(safety_stock)))
    except Exception as e:
        print(f"Error in calculate_safety_stock: {e}")
        return 0


def calculate_optimal_inventory(forecast, lead_time, safety_stock):
    """
    Optimal inventory = Average demand during lead time + Safety stock
    Now properly handles numpy array from get_forecast()
    """
    try:
        # forecast should be a numpy array from get_forecast()
        if isinstance(forecast, np.ndarray) and len(forecast) >= lead_time:
            # Use average of next 'lead_time' days forecast
            demand_during_lead_time = np.mean(forecast[:lead_time]) * lead_time
        else:
            # Fallback: if forecast is not as expected, use simple calculation
            if hasattr(forecast, "__len__") and len(forecast) > 0:
                avg_demand = np.mean(forecast)
            else:
                avg_demand = forecast if isinstance(forecast, (int, float)) else 1
            demand_during_lead_time = avg_demand * lead_time

        # Return as integer
        optimal_inv = demand_during_lead_time + safety_stock
        return max(1, int(np.round(optimal_inv)))
    except Exception as e:
        print(f"Error in calculate_optimal_inventory: {e}")
        return 0


def calculate_order_quantity(optimal_inventory, current_stock):
    """
    Order quantity = Optimal inventory - Current stock
    Returns integer values, minimum 0
    """
    try:
        order_qty = optimal_inventory - current_stock
        return max(0, int(np.round(order_qty)))
    except Exception as e:
        print(f"Error in calculate_order_quantity: {e}")
        return 0


def estimate_old_method_inventory(demand_data):
    """
    Old method = average demand × 60 days (2 months buffer)
    """
    try:
        if len(demand_data) == 0:
            return 0
        old_inventory = np.mean(demand_data) * 60
        return max(1, int(np.round(old_inventory)))
    except Exception as e:
        print(f"Error in estimate_old_method_inventory: {e}")
        return 0


def calculate_cost_savings(optimal_inventory, old_method_inventory, unit_cost):
    """
    Cost savings calculations with practical rounding
    """
    try:
        inventory_reduction_units = old_method_inventory - optimal_inventory
        capital_released = inventory_reduction_units * unit_cost
        annual_savings = capital_released * 0.15
        
        if old_method_inventory > 0:
            inventory_reduction_percentage = (inventory_reduction_units / old_method_inventory) * 100
        else:
            inventory_reduction_percentage = 0

        return (
            int(np.round(annual_savings)),  # Whole dollars
            round(inventory_reduction_percentage, 1),  # 1 decimal for percentage
            int(np.round(capital_released))  # Whole dollars
        )
    except Exception as e:
        print(f"Error in calculate_cost_savings: {e}")
        return 0, 0, 0
