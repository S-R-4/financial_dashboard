import streamlit as st

from src.government_bonds import render_government_bonds_section
from src.commodities import render_commodities_section
from src.equities import render_equities_section
from src.foreign_exchange import render_fx_section

st.title("Expanded Markets")

render_government_bonds_section()
render_commodities_section()
render_equities_section()
render_fx_section()