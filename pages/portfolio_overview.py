import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Portfolio Overview")

@st.cache_data
def load_data():
    historical = pd.read_csv('data/historical_data.csv')
    current = pd.read_csv('data/current_stocks.csv')
    historical['Date'] = pd.to_datetime(historical['Date'])
    return historical, current

historical_df, current_df = load_data()

st.metric("Total Components", len(current_df))
st.metric("Total Categories", current_df['Category'].nunique())

fig1 = px.pie(current_df, values='Current_Stock', names='Category', template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)
