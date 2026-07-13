import streamlit as st
from src.summaries import render_summary_section

st.title("Financial Indicators Dashboard")

render_summary_section()