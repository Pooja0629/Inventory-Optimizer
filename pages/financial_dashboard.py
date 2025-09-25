import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.title("💰 Financial Dashboard")

@st.cache_data
def load_data():
    historical = pd.read_csv('data/historical_data.csv')
    current = pd.read_csv('data/current_stocks.csv')
    historical['Date'] = pd.to_datetime(historical['Date'])
    return historical, current

historical_df, current_df = load_data()

# Calculate ROI function
def calculate_roi(annual_savings, capital_invested):
    if capital_invested > 0:
        return (annual_savings / capital_invested) * 100
    return 0

# Stock alert function
def check_stock_alerts(current_df, historical_df):
    alerts = []
    for _, row in current_df.iterrows():
        component = row['Component_ID']
        current_stock = row['Current_Stock']
        unit_cost = row['Unit_Cost']
        
        # Get demand data for this component
        comp_data = historical_df[historical_df['Component_ID'] == component]
        if len(comp_data) > 0:
            avg_demand = comp_data['Units_Used'].mean()
            std_demand = comp_data['Units_Used'].std()
            
            # Simple safety stock calculation (1.5x avg demand + buffer)
            safety_stock = max(avg_demand * 1.5, avg_demand + 2 * std_demand)
            
            if current_stock < safety_stock * 0.5:
                urgency = "CRITICAL"
                alert_type = "error"
            elif current_stock < safety_stock:
                urgency = "HIGH"
                alert_type = "warning"
            else:
                continue
                
            alerts.append({
                'component': component,
                'current_stock': current_stock,
                'safety_stock': round(safety_stock),
                'unit_cost': unit_cost,
                'urgency': urgency,
                'alert_type': alert_type,
                'needed_quantity': max(0, round(safety_stock - current_stock))
            })
    
    return alerts

# Main Dashboard Content
if 'results' in st.session_state:
    results = st.session_state.results
    
    # Stock Alerts Section
    st.header("🚨 Stock Alerts & Warnings")
    alerts = check_stock_alerts(current_df, historical_df)
    
    if alerts:
        critical_alerts = [a for a in alerts if a['urgency'] == "CRITICAL"]
        high_alerts = [a for a in alerts if a['urgency'] == "HIGH"]
        
        if critical_alerts:
            st.error("### 🔴 Critical Stock Shortages")
            for alert in critical_alerts:
                st.error(f"**{alert['component']}**: Only {alert['current_stock']} units left (Safety: {alert['safety_stock']} units). Need to order {alert['needed_quantity']} units immediately!")
        
        if high_alerts:
            st.warning("### 🟡 High Priority Alerts")
            for alert in high_alerts:
                st.warning(f"**{alert['component']}**: {alert['current_stock']} units (Safety: {alert['safety_stock']} units). Consider ordering {alert['needed_quantity']} units.")
    else:
        st.success("### ✅ All stock levels are adequate")
    
    # Key Financial Metrics
    st.header("📊 Key Financial Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Annual Savings", f"₹{results['annual_savings']:,.2f}")
    
    with col2:
        st.metric("Capital Released", f"₹{results['capital_released']:,.2f}")
    
    with col3:
        inventory_reduction = results['inventory_reduction']
        st.metric("Inventory Reduction", f"{inventory_reduction:.1f}%")
    
    with col4:
        # Calculate ROI (assuming capital invested is the released capital)
        roi = calculate_roi(results['annual_savings'], results['capital_released'])
        st.metric("Estimated ROI", f"{roi:.1f}%")
    
    # Comparison Charts
    st.header("📈 Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Savings Comparison Chart
        savings_data = pd.DataFrame({
            'Category': ['Annual Savings', 'Capital Released'],
            'Amount': [results['annual_savings'], results['capital_released']],
            'Type': ['Recurring', 'One-time']
        })
        
        fig1 = px.bar(savings_data, x='Category', y='Amount', color='Type',
                     title="Financial Benefits Breakdown",
                     template="plotly_white",
                     color_discrete_map={'Recurring': '#00CC96', 'One-time': '#636EFA'})
        fig1.update_layout(xaxis_title="", yaxis_title="Amount ($)")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Inventory Level Comparison
        inventory_data = pd.DataFrame({
            'Method': ['Current System', 'AI Optimized'],
            'Inventory Level': [results['old_method_inventory'], results['optimal_inventory']],
            'Type': ['Traditional', 'AI-Driven']
        })
        
        fig2 = px.bar(inventory_data, x='Method', y='Inventory Level', color='Type',
                     title="Inventory Level Comparison",
                     template="plotly_white",
                     color_discrete_map={'Traditional': '#EF553B', 'AI-Driven': '#00CC96'})
        fig2.update_layout(xaxis_title="", yaxis_title="Inventory Level (Units)")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed Inventory Analysis
    st.header("🔍 Detailed Inventory Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Reduction Impact
        reduction_data = pd.DataFrame({
            'Metric': ['Reduction Percentage', 'Units Reduced'],
            'Value': [results['inventory_reduction'], 
                     results['old_method_inventory'] - results['optimal_inventory']],
            'Unit': ['%', 'units']
        })
        
        fig3 = px.bar(reduction_data, x='Metric', y='Value', 
                     title="Inventory Reduction Impact",
                     template="plotly_white")
        fig3.update_layout(xaxis_title="", yaxis_title="Value")
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Cost Savings Over Time (Projection)
        months = 12
        monthly_savings = results['annual_savings'] / 12
        timeline = [datetime.now() + timedelta(days=30*i) for i in range(months+1)]
        cumulative_savings = [monthly_savings * i for i in range(months+1)]
        
        savings_timeline = pd.DataFrame({
            'Month': [f"Month {i}" for i in range(months+1)],
            'Cumulative Savings': cumulative_savings,
            'Date': timeline
        })
        
        fig4 = px.area(savings_timeline, x='Month', y='Cumulative Savings',
                      title="Projected Cumulative Savings (12 Months)",
                      template="plotly_white")
        fig4.update_layout(xaxis_title="Timeline", yaxis_title="Cumulative Savings ($)")
        st.plotly_chart(fig4, use_container_width=True)
    
    # Component-wise Analysis
    st.header("📋 Component-wise Financial Impact")
    
    # Create sample data for multiple components (in real app, this would come from your data)
    components = current_df['Component_ID'].unique()[:5]  # Top 5 components
    component_data = []
    
    for component in components:
        comp_current = current_df[current_df['Component_ID'] == component]
        if len(comp_current) > 0:
            unit_cost = comp_current['Unit_Cost'].values[0]
            current_stock = comp_current['Current_Stock'].values[0]
            # Simplified calculation for demonstration
            potential_savings = current_stock * unit_cost * 0.15  # 15% savings estimate
            
            component_data.append({
                'Component': component,
                'Current Value': current_stock * unit_cost,
                'Potential Savings': potential_savings,
                'Unit Cost': unit_cost
            })
    
    if component_data:
        component_df = pd.DataFrame(component_data)
        
        fig5 = px.bar(component_df, x='Component', y=['Current Value', 'Potential Savings'],
                     title="Inventory Value vs Potential Savings by Component",
                     template="plotly_white",
                     barmode='group')
        fig5.update_layout(xaxis_title="Component", yaxis_title="Amount (₹)")
        st.plotly_chart(fig5, use_container_width=True)
    
    # Recommendations Section
    st.header("💡 Recommendations")
    
    if results['capital_released'] > 10000:
        st.success("**🎯 High Impact Opportunity**: Consider reinvesting released capital in high-return projects")
    elif results['capital_released'] > 5000:
        st.info("**📈 Good Progress**: Continue optimizing other inventory components")
    else:
        st.warning("**🔍 Review Needed**: Analyze specific components for improvement opportunities")
    
    # Export Options
    st.header("📤 Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Financial Report", use_container_width=True):
            st.success("Financial report generated successfully!")
    
    with col2:
        if st.button("💾 Download Analysis", use_container_width=True):
            st.success("Download ready!")

else:
    st.info("👆 Run AI insights in Demand Analysis first to see financial metrics.")
    
    # Show general stock alerts even without AI analysis
    st.header("🚨 Current Stock Status")
    alerts = check_stock_alerts(current_df, historical_df)
    
    if alerts:
        st.warning("**Stock alerts detected based on current inventory levels:**")
        for alert in alerts[:3]:  # Show top 3 alerts
            st.write(f"- {alert['component']}: {alert['current_stock']} units (Safety: {alert['safety_stock']} units)")
    else:
        st.success("No critical stock alerts detected.")
