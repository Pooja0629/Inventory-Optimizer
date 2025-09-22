import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💰 Financial Dashboard")

if 'results' in st.session_state:
    results = st.session_state.results

    col1, col2 = st.columns(2)
    with col1:
        savings_data = pd.DataFrame({
            'Category': ['Annual Savings', 'Capital Released'],
            'Amount': [results['annual_savings'], results['capital_released']]
        })
        fig1 = px.bar(savings_data, x='Category', y='Amount', template="seaborn")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        inventory_data = pd.DataFrame({
            'Method': ['Old System', 'AI Optimized'],
            'Inventory': [results['old_method_inventory'], results['optimal_inventory']]
        })
        fig2 = px.bar(inventory_data, x='Method', y='Inventory', template="seaborn")
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("👆 Run AI insights in Demand Analysis first.")
