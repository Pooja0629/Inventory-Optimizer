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

# Sidebar - Component Selection and Details
st.sidebar.header("🔧 Component Selection")
component = st.sidebar.selectbox("Select Component", sorted(historical_df['Component_ID'].unique()))

# Get component data
comp_data = historical_df[historical_df['Component_ID'] == component]
current_stock = current_df[current_df['Component_ID'] == component]['Current_Stock'].values[0]
unit_cost = current_df[current_df['Component_ID'] == component]['Unit_Cost'].values[0]
category = current_df[current_df['Component_ID'] == component]['Category'].values[0]
avg_daily_demand = comp_data['Units_Used'].mean()

# Display Component Details in Sidebar
st.sidebar.header("📊 Component Details")
st.sidebar.metric("Current Stock", f"{current_stock} units")
st.sidebar.metric("Average Daily Demand", f"{avg_daily_demand:.2f} units")
st.sidebar.metric("Unit Cost", f"${unit_cost:.2f}")
st.sidebar.metric("Category", category)

# Configuration Parameters
st.sidebar.header("⚙️ Configuration")
lead_time = st.sidebar.slider("Lead Time (days)", 7, 90, 30)
service_level = st.sidebar.slider("Service Level", 0.85, 0.99, 0.95)

# Main Content Area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📊 Demand Forecast")
    
    # Time Frame Selection
    time_frame = st.selectbox("Select Time Frame", 
                             ["Last 30 days", "Last 90 days", "Last 180 days", "Last 365 days", "All Time"])
    
    # Convert to days
    time_map = {
        "Last 30 days": 30, 
        "Last 90 days": 90, 
        "Last 180 days": 180, 
        "Last 365 days": 365, 
        "All Time": None
    }
    selected_days = time_map[time_frame]
    
    if selected_days:
        chart_data = comp_data.tail(selected_days)
    else:
        chart_data = comp_data
    
    # Chart Type Selection
    chart_type = st.radio("Chart Type", ["Line", "Area", "Bar"], horizontal=True)
    
    if chart_type == "Line":
        fig = px.line(chart_data, x='Date', y='Units_Used', 
                     title=f"Demand Forecast for {component} - {time_frame}",
                     template="plotly_white")
    elif chart_type == "Area":
        fig = px.area(chart_data, x='Date', y='Units_Used',
                     title=f"Demand Forecast for {component} - {time_frame}",
                     template="plotly_white")
    else:
        fig = px.bar(chart_data, x='Date', y='Units_Used',
                    title=f"Demand Forecast for {component} - {time_frame}",
                    template="plotly_white")
    
    fig.update_layout(xaxis_title="Date", yaxis_title="Units Used")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⚡ AI Insights")
    
    if st.button("🚀 Generate AI Insights", type="primary", use_container_width=True):
        with st.spinner("Analyzing demand patterns and calculating optimal inventory..."):
            try:
                # Generate forecast
                forecast = get_forecast(comp_data, periods=lead_time + 60)
                
                # Calculate metrics
                safety_stock = calculate_safety_stock(comp_data['Units_Used'].values, lead_time, service_level)
                optimal_inventory = calculate_optimal_inventory(forecast, lead_time, safety_stock)
                order_quantity = calculate_order_quantity(optimal_inventory, current_stock)
                old_method_inventory = estimate_old_method_inventory(comp_data['Units_Used'].values)
                annual_savings, inventory_reduction, capital_released = calculate_cost_savings(
                    optimal_inventory, old_method_inventory, unit_cost
                )

                # Store results in session state
                st.session_state.results = {
                    'optimal_inventory': optimal_inventory,
                    'safety_stock': safety_stock,
                    'order_quantity': order_quantity,
                    'old_method_inventory': old_method_inventory,
                    'annual_savings': annual_savings,
                    'inventory_reduction': inventory_reduction,
                    'capital_released': capital_released,
                    'component': component,
                    'unit_cost': unit_cost
                }
                
                st.success("✅ AI Analysis Complete!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
    
    # Display Results if available
    if 'results' in st.session_state and st.session_state.results.get('component') == component:
        results = st.session_state.results
        
        st.subheader("📋 Analysis Results")
        
        # Key Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Optimal Inventory", f"{results['optimal_inventory']:.0f} units")
            st.metric("Safety Stock", f"{results['safety_stock']:.0f} units")
            st.metric("Order Quantity", f"{results['order_quantity']:.0f} units")
        
        with col2:
            st.metric("Annual Savings", f"${results['annual_savings']:,.2f}")
            st.metric("Inventory Reduction", f"{results['inventory_reduction']:.1f}%")
            st.metric("Capital Released", f"${results['capital_released']:,.2f}")
        
        # Stock Status Warning
        if current_stock < results['safety_stock']:
            st.error(f"🚨 **Warning**: {component} is understocked! Current stock ({current_stock}) is below safety stock ({results['safety_stock']:.0f})")
        elif current_stock < results['optimal_inventory']:
            st.warning(f"⚠️ **Notice**: {component} stock level is below optimal. Consider replenishment.")
        else:
            st.success(f"✅ **Good**: {component} stock level is adequate.")
        
        # Quick Actions
        st.subheader("🚀 Recommended Actions")
        if results['order_quantity'] > 0:
            st.info(f"**Purchase Recommendation**: Order {results['order_quantity']:.0f} units of {component} at ${unit_cost:.2f} each")
        else:
            st.info("**No immediate action needed**: Current stock levels are sufficient")

# Additional Statistics
st.subheader("📈 Component Statistics")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1:
    st.metric("Total Usage (All Time)", f"{comp_data['Units_Used'].sum():.0f} units")
with stat_col2:
    st.metric("Peak Daily Demand", f"{comp_data['Units_Used'].max():.0f} units")
with stat_col3:
    st.metric("Demand Variability", f"{comp_data['Units_Used'].std():.2f}")
with stat_col4:
    st.metric("Service Level Target", f"{service_level*100:.0f}%")
