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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
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
st.markdown('<div class="main-header">🏭 AI Inventory Command Center</div>', unsafe_allow_html=True)

# Load data for dashboard
historical_df, current_df = load_data()

# Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 🚀 Welcome to Your AI-Powered Inventory Optimization System
    
    Transform your inventory management with predictive analytics, AI-driven insights, 
    and real-time optimization recommendations. Reduce costs, improve service levels, 
    and make data-driven decisions.
    """)

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063512.png", width=150)
    if current_df is not None:
        st.success(f"✅ System Ready")
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
        st.metric("Total Inventory Value", f"${total_inventory_value:,.2f}")
    
    with col4:
        st.metric("Average Unit Cost", f"${avg_unit_cost:.2f}")

# Features Grid
st.markdown("---")
st.subheader("🎯 System Features")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Demand Analysis")
    st.markdown("""
    - AI-powered demand forecasting
    - Safety stock calculations
    - Optimal inventory levels
    - Real-time analytics
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with feature_col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 💰 Financial Dashboard")
    st.markdown("""
    - Cost savings analysis
    - ROI calculations
    - Capital optimization
    - Financial reporting
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with feature_col3:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Portfolio Overview")
    st.markdown("""
    - Component categorization
    - Stock level monitoring
    - Performance metrics
    - Interactive analytics
    """)
    st.markdown('</div>', unsafe_allow_html=True)

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
    ### 📑 Main Modules
    
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

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.success("✅ Data Loading: Operational")
    st.success("✅ AI Models: Ready")

with status_col2:
    st.success("✅ Analytics Engine: Active")
    st.success("✅ Reporting System: Online")

with status_col3:
    st.info("🕒 Last Updated: Now")
    st.info("📊 Data Source: CSV Files")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI Inventory Command Center • Powered by Streamlit • Optimizing Your Inventory Management</p>
</div>
""", unsafe_allow_html=True)

# Quick Tip
st.sidebar.markdown("---")
st.sidebar.info("💡 **Pro Tip:** Start with **Demand Analysis** to generate AI insights, then explore other modules to see comprehensive results.")
