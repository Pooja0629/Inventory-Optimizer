import streamlit as st
import pandas as pd
from datetime import datetime
import base64

st.title("📋 Reports")

def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

if 'results' in st.session_state:
    results = st.session_state.results
    report_data = pd.DataFrame({
        'Parameter': ['Optimal Inventory', 'Safety Stock', 'Order Quantity', 'Annual Savings'],
        'Value': [results['optimal_inventory'], results['safety_stock'], results['order_quantity'], results['annual_savings']]
    })
    st.dataframe(report_data)
    st.markdown(create_download_link(report_data, "report.csv"), unsafe_allow_html=True)
else:
    st.info("👆 Run AI insights in Demand Analysis first.")
