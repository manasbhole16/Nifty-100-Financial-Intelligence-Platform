# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

st.title("⚔️ Competitor Peer Comparison Engine")
st.markdown("Perform side-by-side benchmarking against sector peers.")

# --- Self-Contained Data Engine (Bypasses all import errors) ---
@st.cache_data
def load_data():
    return pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIAIRTEL', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Bharti Airtel', 'Infosys', 'ICICI Bank', 'Hindustan Unilever', 'ITC Limited'],
        'sector': ['Energy', 'Technology', 'Financial Services', 'Telecommunication', 'Technology', 'Financial Services', 'Consumer Goods', 'Consumer Goods'],
        'pe_ratio': [26.4, 28.1, 19.5, 45.2, 24.3, 17.8, 55.1, 22.4],
        'roe': [11.2, 38.4, 16.2, 12.1, 31.8, 17.4, 82.3, 27.9],
        'debt_to_equity': [0.4, 0.0, 0.9, 1.4, 0.0, 1.1, 0.0, 0.0],
        'net_profit_margin': [12.5, 19.8, 18.2, 8.4, 16.5, 17.1, 22.3, 28.6],
        'sales_growth': [14.2, 8.5, 12.1, 22.4, 6.8, 15.3, 5.1, 9.4]
    })

df = load_data()

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    primary_ticker = st.selectbox("Select Target Company:", df['ticker'].tolist(), index=0)
with col_sel2:
    peer_options = df[df['ticker'] != primary_ticker]['ticker'].tolist()
    compare_tickers = st.multiselect("Select Peer Competitors to Compare:", peer_options, default=[peer_options[0]] if peer_options else [])

all_selected_tickers = [primary_ticker] + compare_tickers
compare_df = df[df['ticker'].isin(all_selected_tickers)].copy()

st.markdown("---")
st.subheader("Visual Structural Multi-Metric Benchmarking (Radar)")

radar_metrics = ['pe_ratio', 'roe', 'net_profit_margin', 'sales_growth']
categories = ['P/E Ratio', 'ROE (%)', 'Net Profit Margin (%)', 'Sales Growth (%)']

fig = go.Figure()
for index, row in compare_df.iterrows():
    values = [row[m] for m in radar_metrics] + [row[radar_metrics[0]]]
    fig.add_trace(go.Scatterpolar(r=values, theta=categories + [categories[0]], fill='toself', name=row['ticker']))

fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, margin=dict(t=30, b=30, l=30, r=30))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Metric Comparison Data Matrix")
matrix_df = compare_df[['ticker', 'company_name', 'sector', 'pe_ratio', 'roe', 'debt_to_equity', 'net_profit_margin']].copy()
matrix_df.columns = ['Ticker', 'Company Name', 'Sector', 'P/E Ratio', 'ROE %', 'Debt/Equity', 'Net Margin %']
st.dataframe(matrix_df, use_container_width=True, hide_index=True)