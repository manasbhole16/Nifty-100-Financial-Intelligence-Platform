# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px

st.title("📈 Historical Trends Analysis")
st.markdown("Track Year-over-Year (YoY) performance across key financial metrics.")

@st.cache_data
def load_trend_data():
    return pd.DataFrame({
        'year': [2020, 2021, 2022, 2023, 2024] * 3,
        'ticker': ['RELIANCE']*5 + ['TCS']*5 + ['HDFCBANK']*5,
        'revenue': [500, 550, 620, 700, 850, 150, 165, 180, 210, 240, 120, 130, 145, 160, 190],
        'net_profit': [50, 60, 75, 90, 110, 30, 35, 42, 50, 58, 25, 28, 32, 38, 45]
    })

df = load_trend_data()
selected_ticker = st.selectbox("Select Company:", df['ticker'].unique())

ticker_data = df[df['ticker'] == selected_ticker]

fig = px.line(
    ticker_data, x='year', y=['revenue', 'net_profit'], 
    title=f"{selected_ticker} Revenue vs Net Profit (₹ Cr)",
    markers=True, labels={'value': 'Amount (₹ Cr)', 'variable': 'Metric'}
)
st.plotly_chart(fig, use_container_width=True)