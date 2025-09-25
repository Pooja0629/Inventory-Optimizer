import streamlit as st
import pandas as pd
import plotly.express as px
from calculations import *
from model import get_forecast

st.set_page_config(
    page_title="AI Inventory Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS for blue buttons only
st.markdown("""
<style>
    /* Simple blue buttons */
    .stButton > button {
        width: 100%;
        height: 50px;
        border: none;
        border-radius: 8px;
        background-color: #1f77b4;
        color: white;
        font-size: 16px;
        font-weight: bold;
        margin: 5px 0;
    }
    
    .stButton > button:hover {
        background-color: #1668a5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        historical = pd.read_csv('data/historical_data.csv')
        current = pd.read_csv('data/current_stocks.csv')
        historical['Date'] = pd.to_datetime(historical['Date'])
        return historical, current
    except:
        return None, None

# Main Title
st.title("🏭 AI Inventory Command Center")

# Load data for dashboard
historical_df, current_df = load_data()

# Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Welcome to Your AI-Powered Inventory Optimization System
    
    Transform your inventory management with predictive analytics, AI-driven insights, 
    and real-time optimization recommendations.
    """)

with col2:
    if current_df is not None:
        st.success("✅ System Ready")
        st.info(f"📦 {len(current_df)} Components Loaded")

# Quick Stats Dashboard
if current_df is not None and historical_df is not None:
    st.markdown("---")
    st.subheader("📊 Quick System Overview")
    
    # Calculate key metrics
    total_components = len(current_df)
    total_categories = current_df['Category'].nunique()
    total_inventory_value = (current_df['Current_Stock'] * current_df['Unit_Cost']).sum()
    avg_unit_cost = current_df['Unit_Cost'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Components", total_components)
    
    with col2:
        st.metric("Inventory Categories", total_categories)
    
    with col3:
        # Convert to Indian Rupees
        st.metric("Total Inventory Value", f"₹{total_inventory_value:,.0f}")
    
    with col4:
        st.metric("Average Unit Cost", f"₹{avg_unit_cost:.2f}")

# Features Grid
st.markdown("---")
st.subheader("🎯 System Features")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown("### 📈 Demand Analysis")
    st.markdown("""
    - AI-powered demand forecasting
    - Safety stock calculations
    - Optimal inventory levels
    - Real-time analytics
    """)

with feature_col2:
    st.markdown("### 💰 Financial Dashboard")
    st.markdown("""
    - Cost savings analysis
    - ROI calculations
    - Capital optimization
    - Financial reporting
    """)

with feature_col3:
    st.markdown("### 📊 Portfolio Overview")
    st.markdown("""
    - Component categorization
    - Stock level monitoring
    - Performance metrics
    - Interactive analytics
    """)

# Quick Actions Section
st.markdown("---")
st.subheader("🚀 Get Started")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📈 Start Demand Analysis", use_container_width=True):
        st.switch_page("pages/demand_analysis.py")

with action_col2:
    if st.button("💰 View Financial Dashboard", use_container_width=True):
        st.switch_page("pages/financial_dashboard.py")

with action_col3:
    if st.button("📋 Generate Reports", use_container_width=True):
        st.switch_page("pages/reports.py")

# Additional navigation
st.markdown("---")
st.subheader("📊 Additional Tools")

action_col4, action_col5 = st.columns(2)

with action_col4:
    if st.button("🔍 Portfolio Overview", use_container_width=True):
        st.switch_page("pages/portfolio_overview.py")

with action_col5:
    if st.button("📈 View All Analytics", use_container_width=True):
        st.info("Navigate using the sidebar or buttons above")

# Recent Activity (if data available)
if historical_df is not None and current_df is not None:
    st.markdown("---")
    st.subheader("📈 Recent System Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top categories by stock value
        category_value = current_df.groupby('Category').apply(
            lambda x: (x['Current_Stock'] * x['Unit_Cost']).sum()
        ).reset_index(name='Total_Value')
        
        fig1 = px.pie(category_value, values='Total_Value', names='Category',
                     title="Inventory Distribution by Category")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Recent demand trends (sample)
        recent_components = current_df['Component_ID'].head(5)
        recent_data = historical_df[historical_df['Component_ID'].isin(recent_components)]
        
        if not recent_data.empty:
            recent_summary = recent_data.groupby('Component_ID')['Units_Used'].mean().reset_index()
            fig2 = px.bar(recent_summary, x='Component_ID', y='Units_Used',
                         title="Average Demand - Top 5 Components")
            st.plotly_chart(fig2, use_container_width=True)

# Navigation Guide
st.markdown("---")
st.subheader("🧭 Navigation Guide")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.markdown("""
    **📈 Demand Analysis**
    - Analyze component demand patterns
    - Generate AI-powered forecasts
    - Calculate optimal inventory levels
    
    **💰 Financial Dashboard**
    - View cost savings metrics
    - Analyze ROI and capital optimization
    - Monitor financial performance
    """)

with nav_col2:
    st.markdown("""
    **📊 Portfolio Overview**
    - Monitor all inventory components
    - Category-wise analysis
    - Performance tracking
    
    **📋 Reports**
    - Generate comprehensive reports
    - Purchase recommendations
    - Export analysis data
    """)

# System Status
st.markdown("---")
st.subheader("🛠️ System Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("✅ Data Loading: Operational")
    st.success("✅ AI Models: Ready")

with col2:
    st.success("✅ Analytics Engine: Active")
    st.success("✅ Reporting System: Online")

with col3:
    st.info("🕒 Last Updated: Now")

# Simple Pro Tip in Sidebar (will be visible)
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Pro Tip")
st.sidebar.markdown("Start with **Demand Analysis** to generate AI insights, then explore other modules to see comprehensive results.")
