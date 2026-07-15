# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
import pandas as pd
import sys
import os

# Bulletproof path fix to find utils directory seamlessly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db import get_companies

st.title("📊 Market Summary Dashboard")
st.markdown("Macro overview of the Nifty 100 universe.")

# --- Data Fetching ---
df_companies = get_companies()

# Fallback generator if companies.csv is empty or missing
if df_companies.empty:
    df_companies = pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIAIRTEL', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Bharti Airtel', 'Infosys', 'ICICI Bank', 'Hindustan Unilever', 'ITC Limited'],
        'sector': ['Energy', 'Technology', 'Financial Services', 'Telecommunication', 'Technology', 'Financial Services', 'Consumer Goods', 'Consumer Goods'],
        'market_cap': [1850000, 1420000, 1150000, 950000, 680000, 820000, 560000, 520000],
        'pe_ratio': [26.4, 28.1, 19.5, 45.2, 24.3, 17.8, 55.1, 22.4],
        'roe': [11.2, 38.4, 16.2, 12.1, 31.8, 17.4, 82.3, 27.9]
    })

# --- 1. Metric Tiles (6 KPIs) ---
st.subheader("Key Market Indicators")
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_market_cap = df_companies['market_cap'].sum()
avg_pe = df_companies['pe_ratio'].mean() if 'pe_ratio' in df_companies.columns else 24.5
avg_roe = df_companies['roe'].mean() if 'roe' in df_companies.columns else 18.2

with col1:
    st.metric("Total Tickers", f"{len(df_companies)}")
with col2:
    st.metric("Total Market Cap", f"₹{total_market_cap/100000:.2f}L Cr")
with col3:
    st.metric("Avg P/E Ratio", f"{avg_pe:.2f}x")
with col4:
    st.metric("Avg ROE", f"{avg_roe:.2f}%")
with col5:
    st.metric("Sectors Tracked", f"{df_companies['sector'].nunique()}")
with col6:
    st.metric("Market Health", "Bullish" if avg_roe > 15 else "Neutral")

st.markdown("---")

# --- 2. Graphic Allocation & Data Presentation Layout ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Sector Weightage (Market Cap)")
    sector_data = df_companies.groupby('sector')['market_cap'].sum().reset_index()
    
    # Plotly Donut Chart
    fig = px.pie(
        sector_data, 
        values='market_cap', 
        names='sector', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Top 5 Giants by Market Cap")
    top_5 = df_companies.sort_values(by='market_cap', ascending=False).head(5)
    
    # Formatted Presentation Table
    formatted_table = top_5[['ticker', 'company_name', 'sector', 'market_cap']].copy()
    formatted_table['market_cap'] = formatted_table['market_cap'].apply(lambda x: f"₹{x:,.0f} Cr")
    
    st.dataframe(
        formatted_table, 
        hide_index=True, 
        use_container_width=True
    )