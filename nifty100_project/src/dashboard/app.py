# pyrefly: ignore [missing-import]
import streamlit as st

st.set_page_config(page_title="Nifty 100 Analytics", layout="wide", initial_sidebar_state="expanded")

def main():
    st.title("Welcome to Nifty 100 Analytics")
    st.markdown("""
    **N100 Financial Intelligence Platform**
    
    Please use the sidebar to navigate through the analytical modules:
    * **Home:** Market summary and KPIs
    * **Profile:** Deep dive into individual companies
    * **Screener:** Filter companies by financial metrics
    * **Peers:** Compare companies against their sector groups
    """)

if __name__ == "__main__":
    main()