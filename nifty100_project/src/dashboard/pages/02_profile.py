# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
import pandas as pd
import numpy as np
from utils.db import get_companies, get_ratios, get_pl, get_bs, get_cf

st.title("🏢 Corporate Deep-Dive Profile")

# --- Data Fetching ---
df_companies = get_companies()
if df_companies.empty:
    df_companies = pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Infosys'],
        'sector': ['Energy', 'Technology', 'Financial Services', 'Technology']
    })

# --- Searchable Dropdown Selector ---
ticker_options = df_companies['ticker'].tolist()
selected_ticker = st.selectbox("Search and Select Ticker:", ticker_options)

# Get selected company data
comp_info = df_companies[df_companies['ticker'] == selected_ticker].iloc[0]

# --- 10-Year Historical Data Fallback Mocking ---
years = [str(y) for y in range(2017, 2027)]
df_hist = get_pl(selected_ticker)

if df_hist.empty or len(df_hist) < 3:
    # Build clean synthetic 10-year growth records for testing stability
    np.random.seed(seed=sum(ord(c) for c in selected_ticker))
    base_rev = np.random.randint(40000, 120000)
    rev_growth = np.random.uniform(0.06, 0.15, size=10)
    
    revenue = []
    curr = base_rev
    for g in rev_growth:
        curr = curr * (1 + g)
        revenue.append(curr)
        
    net_profit = [r * np.random.uniform(0.10, 0.22) for r in revenue]
    roe_vals = [np.random.uniform(12, 32) for _ in range(10)]
    debt_equity = [np.random.uniform(0.1, 1.8) for _ in range(10)]
    
    df_hist = pd.DataFrame({
        'year': years,
        'revenue': revenue,
        'net_profit': net_profit,
        'roe': roe_vals,
        'debt_to_equity': debt_equity
    })

# --- 1. Company Profile Info Card ---
st.markdown("### Profile Card")
card_col1, card_col2, card_col3 = st.columns(3)
with card_col1:
    st.info(f"**Company Name:**\n\n{comp_info['company_name']}")
with card_col2:
    st.success(f"**Ticker Symbol:**\n\n{comp_info['ticker']}")
with card_col3:
    st.warning(f"**Primary Sector:**\n\n{comp_info['sector']}")

st.markdown("---")

# --- 2. System Intelligence Badges (Pros & Cons) ---
st.subheader("Platform Diagnostic Insights")
latest_metrics = df_hist.iloc[-1]

pro_col, con_col = st.columns(2)

with pro_col:
    st.markdown("**Stabilities & Health (Pros)**")
    if latest_metrics['roe'] > 15:
        st.write("🟢 **High Return Efficiency:** Return on Equity sits securely above the 15% index standard.")
    if latest_metrics['debt_to_equity'] < 1.0:
        st.write("🟢 **Conservative Leverage:** Debt-to-Equity is safely below 1.0x, mitigating financial strain.")
    if df_hist['revenue'].iloc[-1] > df_hist['revenue'].iloc[0]:
        st.write("🟢 **Long-Term Scaling:** Core top-line operations show compound structural growth.")

with con_col:
    st.markdown("**Risks & Vulnerabilities (Cons)**")
    if latest_metrics['roe'] <= 15:
        st.write("🔴 **Capital Efficiency Slowdown:** Capital utilization returns are underperforming optimal standards.")
    if latest_metrics['debt_to_equity'] >= 1.0:
        st.write("🔴 **Aggressive Borrowing:** High balance sheet leverage increases vulnerability during downturns.")
    if df_hist['net_profit'].iloc[-1] < df_hist['net_profit'].iloc[-2]:
        st.write("🔴 **Earning Deceleration:** Short-term bottom-line contraction recorded in the latest period.")

st.markdown("---")

# --- 3. 10-Year Trend Visualization Visuals ---
st.subheader("10-Year Historical Financial Visualizations")
tab1, tab2 = st.columns(2)

with tab1:
    # Revenue vs Profit Trends
    fig_growth = px.line(
        df_hist, x='year', y=['revenue', 'net_profit'],
        title="Income Progression Vector (Revenue vs Net Profit)",
        markers=True, labels={'value': 'Amount (₹ Cr)', 'variable': 'Metric'}
    )
    fig_growth.update_layout(legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_growth, use_container_width=True)

with tab2:
    # Efficiency metrics
    fig_eff = px.line(
        df_hist, x='year', y='roe',
        title="Capital Return Trajectory (Return on Equity %)",
        markers=True, color_discrete_sequence=['#2ca02c']
    )
    st.plotly_chart(fig_eff, use_container_width=True)