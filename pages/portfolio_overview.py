import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.title("📊 Portfolio Overview")

@st.cache_data
def load_data():
    historical = pd.read_csv('data/historical_data.csv')
    current = pd.read_csv('data/current_stocks.csv')
    historical['Date'] = pd.to_datetime(historical['Date'])
    return historical, current

historical_df, current_df = load_data()

# Calculate additional metrics
total_inventory_value = (current_df['Current_Stock'] * current_df['Unit_Cost']).sum()
avg_unit_cost = current_df['Unit_Cost'].mean()
total_current_stock = current_df['Current_Stock'].sum()

# Sidebar for component selection and filters
st.sidebar.header("🔍 Filter Options")

# Component selector
all_components = ["All Components"] + sorted(current_df['Component_ID'].unique())
selected_component = st.sidebar.selectbox("Select Component", all_components)

# Category filter
all_categories = ["All Categories"] + sorted(current_df['Category'].unique())
selected_category = st.sidebar.selectbox("Filter by Category", all_categories)

# Cost range filter
min_cost, max_cost = st.sidebar.slider(
    "Filter by Unit Cost Range",
    min_value=float(current_df['Unit_Cost'].min()),
    max_value=float(current_df['Unit_Cost'].max()),
    value=(float(current_df['Unit_Cost'].min()), float(current_df['Unit_Cost'].max()))
)

# Apply filters
filtered_df = current_df.copy()
if selected_component != "All Components":
    filtered_df = filtered_df[filtered_df['Component_ID'] == selected_component]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
filtered_df = filtered_df[
    (filtered_df['Unit_Cost'] >= min_cost) & 
    (filtered_df['Unit_Cost'] <= max_cost)
]

# Main Dashboard - Key Metrics
st.header("📈 Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Components", len(current_df), 
              delta=f"{len(filtered_df)} filtered" if len(filtered_df) != len(current_df) else None)

with col2:
    st.metric("Total Categories", current_df['Category'].nunique())

with col3:
    st.metric("Total Inventory Value", f"${total_inventory_value:,.2f}")

with col4:
    st.metric("Average Unit Cost", f"${avg_unit_cost:.2f}")

# Component Details Section
if selected_component != "All Components":
    st.header(f"🔧 {selected_component} - Detailed Analysis")
    
    component_data = current_df[current_df['Component_ID'] == selected_component].iloc[0]
    historical_data = historical_df[historical_df['Component_ID'] == selected_component]
    
    if not historical_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Stock", f"{component_data['Current_Stock']} units")
        
        with col2:
            avg_demand = historical_data['Units_Used'].mean()
            st.metric("Avg Daily Demand", f"{avg_demand:.1f} units")
        
        with col3:
            st.metric("Unit Cost", f"${component_data['Unit_Cost']:.2f}")
        
        with col4:
            inventory_value = component_data['Current_Stock'] * component_data['Unit_Cost']
            st.metric("Inventory Value", f"${inventory_value:,.2f}")
        
        # Component-specific charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Demand trend for selected component
            fig_trend = px.line(historical_data.tail(90), x='Date', y='Units_Used',
                               title=f"Demand Trend - {selected_component} (Last 90 Days)",
                               template="plotly_white")
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col_chart2:
            # Stock level analysis
            stock_data = pd.DataFrame({
                'Metric': ['Current Stock', 'Avg Monthly Demand'],
                'Value': [component_data['Current_Stock'], avg_demand * 30]
            })
            fig_stock = px.bar(stock_data, x='Metric', y='Value',
                              title=f"Stock vs Demand - {selected_component}",
                              template="plotly_white")
            st.plotly_chart(fig_stock, use_container_width=True)

# Interactive Charts Section
st.header("📊 Interactive Portfolio Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["Category Distribution", "Cost Analysis", "Stock Levels", "Performance Metrics"])

with tab1:
    # Category Distribution Pie Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category_stock = filtered_df.groupby('Category')['Current_Stock'].sum().reset_index()
        fig_pie = px.pie(category_stock, values='Current_Stock', names='Category',
                        title="Inventory Distribution by Category",
                        template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Category Summary")
        for category in category_stock.nlargest(5, 'Current_Stock')['Category']:
            stock = category_stock[category_stock['Category'] == category]['Current_Stock'].values[0]
            st.write(f"**{category}**: {stock:,} units")

with tab2:
    # Unit Cost Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost distribution histogram
        fig_cost_hist = px.histogram(filtered_df, x='Unit_Cost', 
                                    title="Unit Cost Distribution",
                                    template="plotly_white",
                                    nbins=20)
        fig_cost_hist.update_layout(xaxis_title="Unit Cost ($)", yaxis_title="Number of Components")
        st.plotly_chart(fig_cost_hist, use_container_width=True)
    
    with col2:
        # Top 10 most expensive components
        top_expensive = filtered_df.nlargest(10, 'Unit_Cost')
        fig_expensive = px.bar(top_expensive, x='Component_ID', y='Unit_Cost',
                              title="Top 10 Most Expensive Components",
                              template="plotly_white")
        fig_expensive.update_layout(xaxis_title="Component", yaxis_title="Unit Cost ($)")
        st.plotly_chart(fig_expensive, use_container_width=True)

with tab3:
    # Stock Level Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Current stock levels by component
        top_stock = filtered_df.nlargest(15, 'Current_Stock')
        fig_stock_levels = px.bar(top_stock, x='Component_ID', y='Current_Stock',
                                 color='Category',
                                 title="Top 15 Components by Stock Level",
                                 template="plotly_white")
        fig_stock_levels.update_layout(xaxis_title="Component", yaxis_title="Current Stock")
        st.plotly_chart(fig_stock_levels, use_container_width=True)
    
    with col2:
        # Stock value analysis
        filtered_df['Inventory_Value'] = filtered_df['Current_Stock'] * filtered_df['Unit_Cost']
        top_value = filtered_df.nlargest(10, 'Inventory_Value')
        fig_value = px.bar(top_value, x='Component_ID', y='Inventory_Value',
                          color='Category',
                          title="Top 10 Components by Inventory Value",
                          template="plotly_white")
        fig_value.update_layout(xaxis_title="Component", yaxis_title="Inventory Value ($)")
        st.plotly_chart(fig_value, use_container_width=True)

with tab4:
    # Performance Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # ABC Analysis (simplified)
        filtered_df['Value_Contribution'] = filtered_df['Inventory_Value'] / filtered_df['Inventory_Value'].sum() * 100
        abc_analysis = filtered_df.nlargest(20, 'Value_Contribution')
        
        fig_abc = px.bar(abc_analysis, x='Component_ID', y='Value_Contribution',
                        color='Category',
                        title="Top 20 Components by Value Contribution (%)",
                        template="plotly_white")
        fig_abc.update_layout(xaxis_title="Component", yaxis_title="Value Contribution (%)")
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col2:
        # Stock turnover potential (simplified)
        turnover_data = []
        for _, row in filtered_df.iterrows():
            component = row['Component_ID']
            comp_historical = historical_df[historical_df['Component_ID'] == component]
            if not comp_historical.empty:
                avg_demand = comp_historical['Units_Used'].mean()
                turnover_ratio = avg_demand / row['Current_Stock'] if row['Current_Stock'] > 0 else 0
                turnover_data.append({
                    'Component': component,
                    'Turnover_Ratio': turnover_ratio,
                    'Category': row['Category']
                })
        
        if turnover_data:
            turnover_df = pd.DataFrame(turnover_data)
            top_turnover = turnover_df.nlargest(10, 'Turnover_Ratio')
            fig_turnover = px.bar(top_turnover, x='Component', y='Turnover_Ratio',
                                 color='Category',
                                 title="Top 10 Components by Turnover Potential",
                                 template="plotly_white")
            fig_turnover.update_layout(xaxis_title="Component", yaxis_title="Turnover Ratio")
            st.plotly_chart(fig_turnover, use_container_width=True)

# Quick Actions Section
st.header("🚀 Quick Actions & Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Top Recommendations")
    
    # Identify components needing attention
    low_stock_components = filtered_df.nsmallest(3, 'Current_Stock')
    high_value_components = filtered_df.nlargest(3, 'Inventory_Value')
    
    st.info("**Low Stock Alert:**")
    for _, comp in low_stock_components.iterrows():
        st.write(f"- {comp['Component_ID']}: {comp['Current_Stock']} units")
    
    st.info("**High Value Components:**")
    for _, comp in high_value_components.iterrows():
        st.write(f"- {comp['Component_ID']}: ${comp['Inventory_Value']:,.2f}")

with col2:
    st.subheader("📈 Portfolio Health")
    
    # Calculate portfolio health metrics
    avg_stock_level = filtered_df['Current_Stock'].mean()
    stock_variability = filtered_df['Current_Stock'].std() / avg_stock_level if avg_stock_level > 0 else 0
    
    health_score = max(0, 100 - (stock_variability * 50))  # Simplified health score
    
    st.metric("Portfolio Health Score", f"{health_score:.0f}/100")
    
    if health_score >= 80:
        st.success("✅ Portfolio is well-balanced")
    elif health_score >= 60:
        st.warning("⚠️ Some components need attention")
    else:
        st.error("🔴 Significant optimization needed")

# Export and Summary
st.header("📤 Portfolio Summary")

if st.button("📊 Generate Portfolio Report", use_container_width=True):
    st.success(f"Portfolio report generated for {len(filtered_df)} components!")
    
# Show filtered results count
if len(filtered_df) != len(current_df):
    st.info(f"Showing {len(filtered_df)} of {len(current_df)} components based on your filters")
