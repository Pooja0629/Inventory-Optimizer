import numpy as np
from scipy import stats

def calculate_safety_stock(demand_data, lead_time, service_level):
    """
    Calculate safety stock using statistical method:
    Safety Stock = Z * σ * sqrt(lead_time / 30)
    """
    try:
        if len(demand_data) == 0:
            return 0
            
        avg_demand = np.mean(demand_data)   # not used in formula, but useful if needed later
        std_demand = np.std(demand_data)
        
        # Z-score for service level
        z_score = stats.norm.ppf(service_level)
        
        # Formula
        safety_stock = z_score * std_demand * np.sqrt(lead_time / 30)
        
        return max(0, round(safety_stock, 2))
    except Exception as e:
        print(f"Error in calculate_safety_stock: {e}")
        return 0


def calculate_optimal_inventory(forecast, lead_time, safety_stock):
    """
    Optimal inventory = Demand forecast during lead time + Safety stock
    forecast can be a single value (avg demand) or an array (forecasted series).
    """
    try:
        if hasattr(forecast, "__len__"):  # if forecast is iterable (array/list/series)
            demand_forecast = np.sum(forecast[:lead_time])
        else:  # if forecast is a single number
            demand_forecast = forecast * lead_time

        return round(demand_forecast + safety_stock, 2)
    except Exception as e:
        print(f"Error in calculate_optimal_inventory: {e}")
        return 0


def calculate_order_quantity(optimal_inventory, current_stock):
    """Order quantity = Optimal inventory - Current stock"""
    try:
        return max(0, round(optimal_inventory - current_stock, 2))
    except Exception as e:
        print(f"Error in calculate_order_quantity: {e}")
        return 0


def estimate_old_method_inventory(demand_data):
    """Old method = average demand × 2 (months)"""
    try:
        if len(demand_data) == 0:
            return 0
        return round(np.mean(demand_data) * 2, 2)
    except Exception as e:
        print(f"Error in estimate_old_method_inventory: {e}")
        return 0


def calculate_cost_savings(optimal_inventory, old_method_inventory, unit_cost):
    """
    Cost savings = (Old - Optimal) × unit_cost
    Annual savings = 15% of capital released
    """
    try:
        inventory_reduction = old_method_inventory - optimal_inventory
        capital_released = inventory_reduction * unit_cost
        annual_savings = capital_released * 0.15

        return (
            round(annual_savings, 2),
            round(inventory_reduction, 2),
            round(capital_released, 2),
        )
    except Exception as e:
        print(f"Error in calculate_cost_savings: {e}")
        return 0, 0, 0
