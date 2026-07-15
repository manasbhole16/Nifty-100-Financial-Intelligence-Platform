# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import os

# 10 minute cache TTL for performance
CACHE_TTL = 600

# The folder where your previous sprint data is stored
DATA_DIR = "output/"

@st.cache_data(ttl=CACHE_TTL)
def get_companies():
    file_path = os.path.join(DATA_DIR, "companies.csv")
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_ratios(ticker, year=None):
    file_path = os.path.join(DATA_DIR, "financial_ratios.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'ticker' in df.columns:
            df = df[df['ticker'] == ticker]
        if year and 'year' in df.columns:
            df = df[df['year'] == year]
        return df
    return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_pl(ticker):
    file_path = os.path.join(DATA_DIR, "profit_loss.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df[df['ticker'] == ticker] if 'ticker' in df.columns else df
    return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_bs(ticker):
    file_path = os.path.join(DATA_DIR, "balance_sheet.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df[df['ticker'] == ticker] if 'ticker' in df.columns else df
    return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_cf(ticker):
    file_path = os.path.join(DATA_DIR, "cash_flow.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df[df['ticker'] == ticker] if 'ticker' in df.columns else df
    return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_sectors():
    file_path = os.path.join(DATA_DIR, "sectors.csv")
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_peers(group_name):
    file_path = os.path.join(DATA_DIR, "companies.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df[df['sub_sector'] == group_name] if 'sub_sector' in df.columns else df
    return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_valuation(ticker):
    file_path = os.path.join(DATA_DIR, "valuation_summary.xlsx")
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        return df[df['ticker'] == ticker] if 'ticker' in df.columns else df
    return pd.DataFrame()