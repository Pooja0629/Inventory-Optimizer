# calculations.py
import numpy as np
from scipy import stats

def calculate_safety_stock(demand_data, lead_time, service_level):
    """
    Calculate safety stock using statistical method
    """
    try:
        # Calculate average demand and standard deviation
        avg_demand = np.mean(demand_data)
        std_demand = np.std(demand_data)
        
        # Calculate Z-score for service level
        z_score = stats.norm.ppf(service_level)
        
        # Safety stock formula
        safety_stock = z_score * std_demand * np.sqrt(lead_time/30)
        
        return max(0, round(safety_stock, 2))
    except:
        return 0

def calculate_optimal_inventory(forecast, lead_time, safety_stock):
    """Calculate optimal inventory level"""
    try:
        return round(forecast + safety_stock, 2)
    except:
        return 0

def calculate_order_quantity(optimal_inventory, current_stock):
    """Calculate order quantity needed"""
    try:
        return max(0, round(optimal_inventory - current_stock, 2))
    except:
        return 0

def estimate_old_method_inventory(demand_data):
    """Estimate inventory using old method (simple average)"""
    try:
        return round(np.mean(demand_data) * 2, 2)  # Simple multiplier method
    except:
        return 0

def calculate_cost_savings(optimal_inventory, old_method_inventory, unit_cost):
    """Calculate cost savings from optimized inventory"""
    try:
        inventory_reduction = old_method_inventory - optimal_inventory
        capital_released = inventory_reduction * unit_cost
        annual_savings = capital_released * 0.15  # Assuming 15% carrying cost
        
        return (round(annual_savings, 2), 
                round(inventory_reduction, 2), 
                round(capital_released, 2))
    except:
        return 0, 0, 0
