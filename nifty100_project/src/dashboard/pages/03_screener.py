# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd

st.title("🔍 Advanced Investment Screener")
st.markdown("Filter the Nifty 100 universe using custom financial thresholds.")

# --- Self-Contained Data Engine ---
@st.cache_data
def load_data():
    return pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIAIRTEL', 'INFY', 'ICICIBANK'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Bharti Airtel', 'Infosys', 'ICICI Bank'],
        'sector': ['Energy', 'Technology', 'Financial Services', 'Telecommunication', 'Technology', 'Financial Services'],
        'market_cap': [1850000, 1420000, 1150000, 950000, 680000, 820000],
        'pe_ratio': [26.4, 28.1, 19.5, 45.2, 24.3, 17.8],
        'roe': [11.2, 38.4, 16.2, 12.1, 31.8, 17.4],
        'dividend_yield': [0.8, 2.1, 1.2, 0.5, 2.5, 0.9],
        'debt_to_equity': [0.4, 0.0, 0.9, 1.4, 0.0, 1.1]
    })

df = load_data()

# --- Presets ---
st.sidebar.header("🎯 Quick Preset Screeners")
preset = st.sidebar.radio("Choose a strategy preset:", ["Custom Filters", "Value Investing", "High Growth Tech"])

min_pe, max_pe = 0.0, 100.0
min_roe = 0.0
max_de = 3.0

if preset == "Value Investing": 
    max_pe = 20.0
    min_roe = 15.0
elif preset == "High Growth Tech": 
    min_roe = 20.0

st.subheader("Filter Configurations")
with st.expander("Modify Metric Thresholds", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        pe_range = st.slider("P/E Ratio Range", 0.0, 100.0, (float(min_pe), float(max_pe)), 0.5)
        roe_input = st.slider("Minimum ROE (%)", 0.0, 100.0, float(min_roe), 0.5)
    with col2:
        de_input = st.slider("Maximum Debt-to-Equity", 0.0, 3.0, float(max_de), 0.1)

# Apply Filters
filtered_df = df[
    (df['pe_ratio'] >= pe_range[0]) & 
    (df['pe_ratio'] <= pe_range[1]) &
    (df['roe'] >= roe_input) & 
    (df['debt_to_equity'] <= de_input)
]

if preset == "High Growth Tech": 
    filtered_df = filtered_df[filtered_df['sector'] == 'Technology']

st.subheader(f"Screening Results ({len(filtered_df)} Companies Found)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)