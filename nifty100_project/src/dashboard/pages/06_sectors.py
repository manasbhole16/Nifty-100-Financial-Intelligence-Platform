# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px

st.title("🧩 Sector Landscape")
st.markdown("Visualize the Nifty 100 universe through sector-wide bubble charts.")

@st.cache_data
def load_sector_data():
    return pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC', 'SBIN'],
        'sector': ['Energy', 'Technology', 'Financials', 'Technology', 'Consumer Goods', 'Financials'],
        'market_cap': [1850000, 1420000, 1150000, 680000, 520000, 480000],
        'pe_ratio': [26.4, 28.1, 19.5, 24.3, 22.4, 11.2],
        'roe': [11.2, 38.4, 16.2, 31.8, 27.9, 15.6]
    })

df = load_sector_data()

fig = px.scatter(
    df, x="pe_ratio", y="roe", size="market_cap", color="sector",
    hover_name="ticker", log_x=True, size_max=60,
    title="Sector Analysis: P/E Ratio vs ROE (Bubble Size = Market Cap)"
)
st.plotly_chart(fig, use_container_width=True)