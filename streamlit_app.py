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

# Custom CSS for better styling - FIXED BUTTON COLORS
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
    
    /* FIXED BUTTON STYLING - Remove white color */
    .stButton > button {
        width: 100%;
        height: 60px;
        border: none;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-size: 16px;
        font-weight: bold;
        margin: 10px 0;
        transition: all 0.3s ease;
        border: 2px solid #5a6fd8;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        color: white !important;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px #667eea;
        color: white !important;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Custom section headers */
    .section-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
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

# Main Title with enhanced styling
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;'>
    <h1 style='color: white; margin: 0; font-size: 3.5rem;'>🏭 AI Inventory Command Center</h1>
    <p style='color: white; font-size: 1.2rem; margin: 10px 0 0 0;'>Smart Inventory Optimization Powered by AI</p>
</div>
""", unsafe_allow_html=True)

# Load data for dashboard
historical_df, current_df = load_data()

# Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 🚀 Transform Your Inventory Management
    
    **AI-powered insights** to optimize your inventory levels, reduce costs, and improve operational efficiency. 
    Our system provides:
    
    - 📊 **Real-time analytics** and demand forecasting
    - 💰 **Cost optimization** and ROI calculations  
    - 📈 **Predictive insights** for better decision making
    - 🚀 **Automated recommendations** for inventory management
    """)

with col2:
    # Using a placeholder image - you can replace with your logo
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
        <div style='font-size: 4rem; margin-bottom: 10px;'>📦</div>
        <h3 style='margin: 0; color: #1f77b4;'>Inventory AI</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if current_df is not None:
        st.success(f"**✅ System Ready**")
        st.info(f"**📊 {len(current_df)} Components Loaded**")
        st.info(f"**🏷️ {current_df['Category'].nunique()} Categories**")

# Quick Stats Dashboard
if current_df is not None and historical_df is not None:
    st.markdown("---")
    st.markdown('<div class="section-header"><h2>📊 System Overview</h2></div>', unsafe_allow_html=True)
    
    # Calculate key metrics
    total_components = len(current_df)
    total_categories = current_df['Category'].nunique()
    total_inventory_value = (current_df['Current_Stock'] * current_df['Unit_Cost']).sum()
    avg_unit_cost = current_df['Unit_Cost'].mean()
    total_stock_units = current_df['Current_Stock'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ff7f0e, #ff9e4a); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h3 style='margin: 0; font-size: 2.5rem;'>{total_components}</h3>
            <p style='margin: 0;'>Total Components</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #2ca02c, #4cd84c); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h3 style='margin: 0; font-size: 2.5rem;'>${total_inventory_value:,.0f}</h3>
            <p style='margin: 0;'>Inventory Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #d62728, #ff6b6b); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h3 style='margin: 0; font-size: 2.5rem;'>{total_categories}</h3>
            <p style='margin: 0;'>Categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #9467bd, #b894e6); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h3 style='margin: 0; font-size: 2.5rem;'>{total_stock_units:,}</h3>
            <p style='margin: 0;'>Total Units</p>
        </div>
        """, unsafe_allow_html=True)

# Features Grid
st.markdown("---")
st.markdown('<div class="section-header"><h2>🎯 Core Features</h2></div>', unsafe_allow_html=True)

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown("""
    <div style='background: #ffffff; padding: 25px; border-radius: 15px; border-left: 5px solid #ff7f0e; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h3 style='color: #ff7f0e; margin-top: 0;'>📈 Demand Analysis</h3>
        <ul style='color: #333;'>
            <li>AI-powered demand forecasting</li>
            <li>Safety stock calculations</li>
            <li>Optimal inventory levels</li>
            <li>Real-time analytics</li>
            <li>Trend analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div style='background: #ffffff; padding: 25px; border-radius: 15px; border-left: 5px solid #2ca02c; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h3 style='color: #2ca02c; margin-top: 0;'>💰 Financial Dashboard</h3>
        <ul style='color: #333;'>
            <li>Cost savings analysis</li>
            <li>ROI calculations</li>
            <li>Capital optimization</li>
            <li>Financial reporting</li>
            <li>Budget planning</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div style='background: #ffffff; padding: 25px; border-radius: 15px; border-left: 5px solid #1f77b4; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h3 style='color: #1f77b4; margin-top: 0;'>📊 Portfolio Overview</h3>
        <ul style='color: #333;'>
            <li>Component categorization</li>
            <li>Stock level monitoring</li>
            <li>Performance metrics</li>
            <li>Interactive analytics</li>
            <li>Health monitoring</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Quick Actions Section
st.markdown("---")
st.markdown('<div class="section-header"><h2>🚀 Get Started</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div style='background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h4 style='color: #333; text-align: center;'>Choose your starting point to begin optimizing your inventory:</h4>
</div>
""", unsafe_allow_html=True)

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📈 Start Demand Analysis", use_container_width=True, key="demand_btn"):
        st.switch_page("pages/demand_analysis.py")

with action_col2:
    if st.button("💰 View Financial Dashboard", use_container_width=True, key="finance_btn"):
        st.switch_page("pages/financial_dashboard.py")

with action_col3:
    if st.button("📋 Generate Reports", use_container_width=True, key="reports_btn"):
        st.switch_page("pages/reports.py")

# Additional action buttons
st.markdown("---")
st.markdown('<div style="text-align: center; margin: 20px 0;"><h3>📊 Additional Tools</h3></div>', unsafe_allow_html=True)

action_col4, action_col5, action_col6 = st.columns(3)

with action_col4:
    if st.button("🔍 Portfolio Overview", use_container_width=True, key="portfolio_btn"):
        st.switch_page("pages/portfolio_overview.py")

with action_col5:
    if st.button("⚙️ System Settings", use_container_width=True, key="settings_btn"):
        st.info("System settings page coming soon!")

with action_col6:
    if st.button("📚 User Guide", use_container_width=True, key="guide_btn"):
        st.info("User guide and documentation coming soon!")

# Recent Activity (if data available)
if historical_df is not None and current_df is not None:
    st.markdown("---")
    st.markdown('<div class="section-header"><h2>📈 System Insights</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top categories by stock value
        category_value = current_df.groupby('Category').apply(
            lambda x: (x['Current_Stock'] * x['Unit_Cost']).sum()
        ).reset_index(name='Total_Value')
        
        fig1 = px.pie(category_value, values='Total_Value', names='Category',
                     title="💰 Inventory Value by Category",
                     template="plotly_white",
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Component value distribution
        top_components = current_df.nlargest(10, 'Current_Stock')
        fig2 = px.bar(top_components, x='Component_ID', y='Current_Stock',
                     color='Category',
                     title="📦 Top 10 Components by Stock Level",
                     template="plotly_white")
        fig2.update_layout(xaxis_title="Component ID", yaxis_title="Stock Units")
        st.plotly_chart(fig2, use_container_width=True)

# System Status
st.markdown("---")
st.markdown('<div class="section-header"><h2>🛠️ System Status</h2></div>', unsafe_allow_html=True)

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.success("""
    **✅ Data Loading**  
    Operational
    """)

with status_col2:
    st.success("""
    **🤖 AI Models**  
    Ready for Analysis
    """)

with status_col3:
    st.success("""
    **📊 Analytics Engine**  
    Active & Monitoring
    """)

with status_col4:
    st.success("""
    **📋 Reporting System**  
    Online
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
    <h4 style='margin: 0; color: #333;'>AI Inventory Command Center</h4>
    <p style='margin: 5px 0;'>Powered by Streamlit • Optimizing Inventory Management</p>
    <p style='margin: 0; font-size: 0.9em;'>System Version 2.0 • Last Updated: 2024</p>
</div>
""", unsafe_allow_html=True)

# Quick Tip in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 4px solid #2196f3;'>
    <h4>💡 Pro Tip</h4>
    <p style='margin: 0; font-size: 0.9em;'>Start with <strong>Demand Analysis</strong> to generate AI insights, then explore other modules for comprehensive results.</p>
</div>
""", unsafe_allow_html=True)
