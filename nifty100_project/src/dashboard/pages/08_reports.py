# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd

st.title("📄 Annual Reports & Filings")
st.markdown("Direct links to BSE (Bombay Stock Exchange) official company filings.")

@st.cache_data
def load_reports_data():
    return pd.DataFrame({
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank'],
        'bse_link': ['https://www.bseindia.com/stock-share-price/reliance-industries-ltd/reliance/500325/', 
                     'https://www.bseindia.com/stock-share-price/tata-consultancy-services-ltd/tcs/532540/',
                     'https://www.bseindia.com/stock-share-price/hdfc-bank-ltd/hdfcbank/500180/']
    })

df = load_reports_data()

st.subheader("Document Repository")
for index, row in df.iterrows():
    with st.expander(f"{row['ticker']} - {row['company_name']}"):
        st.write(f"**Latest Filings & Corporate Disclosures for {row['company_name']}**")
        st.markdown(f"[🔗 View Official BSE Page (Includes Annual Reports)]({row['bse_link']})")