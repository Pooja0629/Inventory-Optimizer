import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import numpy as np
from io import BytesIO

st.title("📋 Inventory Optimization Reports")

@st.cache_data
def load_data():
    historical = pd.read_csv('data/historical_data.csv')
    current = pd.read_csv('data/current_stocks.csv')
    historical['Date'] = pd.to_datetime(historical['Date'])
    return historical, current

historical_df, current_df = load_data()

def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

def generate_comprehensive_report(current_df, historical_df, specific_component=None):
    report_data = []
    analysis_date = datetime.now().strftime('%Y-%m-%d')
    
    components_to_analyze = current_df['Component_ID'].unique()
    if specific_component:
        components_to_analyze = [specific_component]
    
    for component in components_to_analyze:
        comp_data = current_df[current_df['Component_ID'] == component]
        if len(comp_data) == 0:
            continue
            
        comp_row = comp_data.iloc[0]
        current_stock = comp_row['Current_Stock']
        unit_cost = comp_row['Unit_Cost']
        category = comp_row['Category']
        
        # Get historical data for calculations
        hist_data = historical_df[historical_df['Component_ID'] == component]
        if len(hist_data) == 0:
            continue
            
        # Calculate basic metrics
        avg_daily_demand = hist_data['Units_Used'].mean()
        demand_std = hist_data['Units_Used'].std()
        lead_time = 30  # Default lead time
        
        # Safety stock calculation (simplified)
        z_score = 1.65  # 95% service level
        safety_stock = z_score * demand_std * np.sqrt(lead_time) if not np.isnan(demand_std) else avg_daily_demand * 1.5
        
        # Optimal inventory calculation
        optimal_inventory = max(safety_stock * 2, avg_daily_demand * 45)  # 45 days coverage
        
        # Order quantity calculation
        order_quantity = max(0, optimal_inventory - current_stock)
        
        # Stock status
        if current_stock < safety_stock * 0.5:
            status = "CRITICAL"
            priority = "HIGH"
            action = "IMMEDIATE ORDER REQUIRED"
        elif current_stock < safety_stock:
            status = "LOW"
            priority = "MEDIUM"
            action = "PLAN ORDER"
        elif current_stock < optimal_inventory:
            status = "ADEQUATE"
            priority = "LOW"
            action = "MONITOR"
        else:
            status = "EXCESS"
            priority = "LOW"
            action = "REDUCE STOCK"
        
        # Cost calculations
        current_inventory_value = current_stock * unit_cost
        optimal_inventory_value = optimal_inventory * unit_cost
        potential_savings = current_inventory_value - optimal_inventory_value
        
        report_data.append({
            'Component_ID': component,
            'Category': category,
            'Analysis_Date': analysis_date,
            'Current_Stock': current_stock,
            'Unit_Cost': unit_cost,
            'Current_Inventory_Value': current_inventory_value,
            'Avg_Daily_Demand': round(avg_daily_demand, 2),
            'Demand_Std_Dev': round(demand_std, 2) if not np.isnan(demand_std) else 0,
            'Safety_Stock': round(safety_stock),
            'Optimal_Inventory_Level': round(optimal_inventory),
            'Recommended_Order_Quantity': round(order_quantity),
            'Lead_Time_Days': lead_time,
            'Stock_Status': status,
            'Priority_Level': priority,
            'Recommended_Action': action,
            'Optimal_Inventory_Value': round(optimal_inventory_value, 2),
            'Potential_Cost_Savings': round(max(0, potential_savings), 2),
            'Service_Level_Target': '95%'
        })
    
    return pd.DataFrame(report_data)

# Main Report Interface
st.header("📊 Generate Comprehensive Reports")

# Report Type Selection
report_type = st.radio("Select Report Type:", 
                      ["Single Component Report", "Full Portfolio Report"],
                      horizontal=True)

if report_type == "Single Component Report":
    component = st.selectbox("Select Component:", 
                           ["All Components"] + sorted(current_df['Component_ID'].unique()))
    if component != "All Components":
        specific_component = component
    else:
        specific_component = None
else:
    specific_component = None

if st.button("🚀 Generate Report", type="primary"):
    with st.spinner("Generating comprehensive inventory analysis report..."):
        report_df = generate_comprehensive_report(current_df, historical_df, specific_component)
        
        if not report_df.empty:
            st.session_state.current_report = report_df
            st.success(f"✅ Report generated successfully! Analyzed {len(report_df)} components.")

# Display Report if Available
if 'current_report' in st.session_state:
    report_df = st.session_state.current_report
    
    # Summary Metrics
    st.header("📈 Report Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_components = len(report_df)
        st.metric("Components Analyzed", total_components)
    
    with col2:
        critical_items = len(report_df[report_df['Priority_Level'] == 'HIGH'])
        st.metric("Critical Items", critical_items)
    
    with col3:
        total_savings = report_df['Potential_Cost_Savings'].sum()
        st.metric("Total Potential Savings", f"${total_savings:,.2f}")
    
    with col4:
        avg_optimization = ((report_df['Current_Stock'] - report_df['Optimal_Inventory_Level']).mean() / report_df['Current_Stock'].mean() * 100) if report_df['Current_Stock'].mean() > 0 else 0
        st.metric("Avg Optimization", f"{avg_optimization:.1f}%")
    
    # Detailed Report Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Purchase Recommendations", "📊 Summary Analysis", "🚨 Priority Actions", "📈 Cost Analysis"])
    
    with tab1:
        st.subheader("🛒 Purchase Recommendations")
        
        # Filter for items needing ordering
        order_items = report_df[report_df['Recommended_Order_Quantity'] > 0]
        
        if not order_items.empty:
            purchase_df = order_items[['Component_ID', 'Category', 'Current_Stock', 'Safety_Stock', 
                                     'Recommended_Order_Quantity', 'Unit_Cost', 'Priority_Level']].copy()
            purchase_df['Total_Cost'] = purchase_df['Recommended_Order_Quantity'] * purchase_df['Unit_Cost']
            purchase_df = purchase_df.sort_values('Priority_Level', ascending=False)
            
            st.dataframe(purchase_df, use_container_width=True)
            
            # Purchase summary
            total_order_quantity = purchase_df['Recommended_Order_Quantity'].sum()
            total_order_cost = purchase_df['Total_Cost'].sum()
            
            st.info(f"**📦 Total Order Recommendation:** {total_order_quantity:,} units across {len(purchase_df)} components")
            st.info(f"**💰 Estimated Order Cost:** ${total_order_cost:,.2f}")
        else:
            st.success("✅ No purchase recommendations - all stock levels are adequate!")
    
    with tab2:
        st.subheader("📊 Inventory Summary")
        
        # Display full report with filtering options
        st.dataframe(report_df, use_container_width=True)
        
        # Summary statistics
        st.subheader("📈 Key Statistics")
        
        stat_col1, stat_col2 = st.columns(2)
        
        with stat_col1:
            st.write("**Stock Status Distribution:**")
            status_counts = report_df['Stock_Status'].value_counts()
            for status, count in status_counts.items():
                st.write(f"- {status}: {count} components")
            
            st.write("**Priority Level Summary:**")
            priority_counts = report_df['Priority_Level'].value_counts()
            for priority, count in priority_counts.items():
                st.write(f"- {priority}: {count} components")
        
        with stat_col2:
            st.write("**Category-wise Analysis:**")
            category_summary = report_df.groupby('Category').agg({
                'Current_Stock': 'sum',
                'Potential_Cost_Savings': 'sum',
                'Component_ID': 'count'
            }).rename(columns={'Component_ID': 'Count'})
            st.dataframe(category_summary, use_container_width=True)
    
    with tab3:
        st.subheader("🚨 Priority Action Items")
        
        # Critical items
        critical_items = report_df[report_df['Priority_Level'] == 'HIGH']
        if not critical_items.empty:
            st.error("**🔴 CRITICAL ITEMS - IMMEDIATE ACTION REQUIRED**")
            for _, item in critical_items.iterrows():
                st.error(f"""
                **{item['Component_ID']}** ({item['Category']})
                - Current Stock: {item['Current_Stock']} units
                - Safety Stock: {item['Safety_Stock']} units
                - Order Required: {item['Recommended_Order_Quantity']} units
                - Action: {item['Recommended_Action']}
                """)
        
        # Medium priority items
        medium_items = report_df[report_df['Priority_Level'] == 'MEDIUM']
        if not medium_items.empty:
            st.warning("**🟡 MEDIUM PRIORITY ITEMS - PLAN ACTION**")
            for _, item in medium_items.head(3).iterrows():  # Show top 3
                st.warning(f"""
                **{item['Component_ID']}** - Order {item['Recommended_Order_Quantity']} units
                """)
    
    with tab4:
        st.subheader("💰 Cost Optimization Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost savings potential
            savings_data = report_df.nlargest(10, 'Potential_Cost_Savings')
            if not savings_data.empty:
                fig_savings = px.bar(savings_data, x='Component_ID', y='Potential_Cost_Savings',
                                    title="Top 10 Cost Savings Opportunities",
                                    template="plotly_white")
                st.plotly_chart(fig_savings, use_container_width=True)
        
        with col2:
            # Current vs Optimal inventory value comparison
            current_total = report_df['Current_Inventory_Value'].sum()
            optimal_total = report_df['Optimal_Inventory_Value'].sum()
            
            comparison_data = pd.DataFrame({
                'Type': ['Current Inventory', 'Optimal Inventory'],
                'Value': [current_total, optimal_total]
            })
            
            fig_comparison = px.bar(comparison_data, x='Type', y='Value',
                                  title="Current vs Optimal Inventory Value",
                                  template="plotly_white")
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Download Section
    st.header("📤 Export Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Full report download
        st.markdown(create_download_link(report_df, "comprehensive_inventory_report.csv"), 
                   unsafe_allow_html=True)
    
    with col2:
        # Purchase recommendations only
        if 'purchase_df' in locals():
            st.markdown(create_download_link(purchase_df, "purchase_recommendations.csv"), 
                       unsafe_allow_html=True)
        else:
            st.info("No purchase recommendations")
    
    with col3:
        # Critical items report
        critical_report = report_df[report_df['Priority_Level'] == 'HIGH']
        if not critical_report.empty:
            st.markdown(create_download_link(critical_report, "critical_items_report.csv"), 
                       unsafe_allow_html=True)
    
    # Report Generation Date
    st.write(f"*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

else:
    st.info("👆 Click 'Generate Report' to create comprehensive inventory analysis reports")
    
    # Quick preview of available components
    st.subheader("Available Components for Analysis")
    st.write(f"**Total components in system:** {len(current_df)}")
    st.write(f"**Categories:** {', '.join(current_df['Category'].unique())}")
    
    # Show sample data
    if st.checkbox("Show sample component data"):
        st.dataframe(current_df[['Component_ID', 'Category', 'Current_Stock', 'Unit_Cost']].head(10))
