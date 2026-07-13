import streamlit as st

st.set_page_config(
    page_title="Financial Indicators Dashboard",
    layout="wide",
)

market_summary = st.Page(
    "pages/market_summary.py",
    title="Market Summary",
    #icon="insert",
)

expanded_markets = st.Page(
    "pages/expanded_markets.py",
    title="Expanded Markets",
    #icon="insert",
)

fx_signals = st.Page(
    "pages/fx_signals.py",
    title="FX Signals",
    #icon="insert",
)

pg = st.navigation([
    market_summary,
    expanded_markets,
    fx_signals,
])

pg.run()