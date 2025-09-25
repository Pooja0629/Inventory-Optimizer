import sys
import os
import numpy as np
from scipy import stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

# Try importing calculations
try:
    from calculations import (
        calculate_safety_stock,
        calculate_optimal_inventory,
        calculate_order_quantity,
        estimate_old_method_inventory,
        calculate_cost_savings
    )
    print("✅ Successfully imported from calculations")
except ImportError as e:
    print(f"❌ Error importing from calculations: {e}")
    print(f"❌ Current working directory: {os.getcwd()}")
    print(f"❌ Files in parent directory: {os.listdir('..')}")

from model import get_forecast
import streamlit as st
import pandas as pd
import plotly.express as px

# Define the function at the TOP LEVEL (outside any other blocks)
def calculate_safety_stock(demand_data, lead_time, service_level):
    # Calculate standard deviation of demand
    demand_std = np.std(demand_data)
    
    # Z-score based on service level (example: 95% -> 1.65)
    z_score = stats.norm.ppf(service_level)
    
    # Safety stock formula
    safety_stock = z_score * demand_std * np.sqrt(lead_time)
    
    return safety_stock

# Streamlit App
st.title("📈 Demand Analysis")

@st.cache_data
def load_data():
    historical = pd.read_csv('data/historical_data.csv')
    current = pd.read_csv('data/current_stocks.csv')
    historical['Date'] = pd.to_datetime(historical['Date'])
    return historical, current

historical_df, current_df = load_data()

component = st.sidebar.selectbox("Component", sorted(historical_df['Component_ID'].unique()))
lead_time = st.sidebar.slider("Lead Time (days)", 7, 90, 30)
service_level = st.sidebar.slider("Service Level", 0.85, 0.99, 0.95)

comp_data = historical_df[historical_df['Component_ID'] == component]
current_stock = current_df[current_df['Component_ID'] == component]['Current_Stock'].values[0]
unit_cost = current_df[current_df['Component_ID'] == component]['Unit_Cost'].values[0]
category = current_df[current_df['Component_ID'] == component]['Category'].values[0]

col_left, col_right = st.columns([2, 1])

# Demand Forecast Charts
with col_left:
    st.subheader("📊 Demand Forecast")
    chart_type = st.selectbox("Chart Type", ["Line", "Area", "Bar"])
    chart_data = comp_data.tail(180)

    if chart_type == "Line":
        fig = px.line(chart_data, x='Date', y='Units_Used', template="ggplot2")
    elif chart_type == "Area":
        fig = px.area(chart_data, x='Date', y='Units_Used', template="ggplot2")
    else:
        fig = px.bar(chart_data, x='Date', y='Units_Used', template="ggplot2")

    st.plotly_chart(fig, use_container_width=True)

# AI Recommendations
with col_right:
    st.subheader("⚡ AI Recommendations")
    if st.button("🚀 Run AI Insights"):
        forecast = get_forecast(comp_data, periods=lead_time + 60)
        
        # Now CALL the function (don't define it here)
        safety_stock = calculate_safety_stock(comp_data['Units_Used'].values, lead_time, service_level)
        optimal_inventory = calculate_optimal_inventory(forecast, lead_time, safety_stock)
        order_quantity = calculate_order_quantity(optimal_inventory, current_stock)
        old_method_inventory = estimate_old_method_inventory(comp_data['Units_Used'].values)
        annual_savings, inventory_reduction, capital_released = calculate_cost_savings(
            optimal_inventory, old_method_inventory, unit_cost
        )

        st.session_state.results = {
            'optimal_inventory': optimal_inventory,
            'safety_stock': safety_stock,
            'order_quantity': order_quantity,
            'old_method_inventory': old_method_inventory,
            'annual_savings': annual_savings,
            'inventory_reduction': inventory_reduction,
            'capital_released': capital_released
        }
        st.success("✅ AI Analysis Complete!")
