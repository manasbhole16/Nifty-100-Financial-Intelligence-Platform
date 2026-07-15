# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px

st.title("💰 Capital Allocation")
st.markdown("Treemap visualization of market capitalization distribution.")

@st.cache_data
def load_capital_data():
    return pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC', 'SBIN'],
        'sector': ['Energy', 'Technology', 'Financials', 'Technology', 'Consumer Goods', 'Financials'],
        'market_cap': [1850000, 1420000, 1150000, 680000, 520000, 480000]
    })

df = load_capital_data()

fig = px.treemap(
    df, path=[px.Constant("Nifty 100"), 'sector', 'ticker'], values='market_cap',
    color='market_cap', color_continuous_scale='Viridis',
    title="Market Cap Treemap"
)
st.plotly_chart(fig, use_container_width=True)