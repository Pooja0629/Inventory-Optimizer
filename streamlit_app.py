import streamlit as st
from calculations import *
from model import get_forecast

st.set_page_config(
    page_title="AI Inventory Command Center",
    page_icon="📊",
    layout="wide"
)

st.title("🏭 AI Inventory Command Center")

st.markdown("""
Welcome to your **AI-powered Inventory Optimization System**.  

### 📑 Navigation
- 📈 Demand Analysis  
- 💰 Financial Dashboard  
- 📊 Portfolio Overview  
- 📋 Reports  

---
""")

st.info("👈 Use the sidebar to switch between different modules.")
