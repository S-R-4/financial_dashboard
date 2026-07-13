import datetime as dt

import pandas as pd
import plotly.express as px
import streamlit as st
from pandas_datareader import data as web


GOVERNMENT_BONDS = {
    "US 2-Year": {
        "series_id": "DGS2",
        "country": "United States",
        "maturity": "2-Year",
        "frequency": "Daily",
    },
    "US 10-Year": {
        "series_id": "DGS10",
        "country": "United States",
        "maturity": "10-Year",
        "frequency": "Daily",
    },
    "Germany 10-Year": {
        "series_id": "IRLTLT01DEM156N",
        "country": "Germany",
        "maturity": "10-Year",
        "frequency": "Monthly",
    },
    "Italy 10-Year": {
        "series_id": "IRLTLT01ITM156N",
        "country": "Italy",
        "maturity": "10-Year",
        "frequency": "Monthly",
    },
    "Spain 10-Year": {
        "series_id": "IRLTLT01ESM156N",
        "country": "Spain",
        "maturity": "10-Year",
        "frequency": "Monthly",
    },
    "UK 10-Year": {
        "series_id": "IRLTLT01GBM156N",
        "country": "United Kingdom",
        "maturity": "10-Year",
        "frequency": "Monthly",
    },
    "Japan 10-Year": {
        "series_id": "IRLTLT01JPM156N",
        "country": "Japan",
        "maturity": "10-Year",
        "frequency": "Monthly",
    },
}


@st.cache_data(ttl=3600)
def fetch_government_bond_yield(
    series_id: str,
    start_date: dt.datetime,
    end_date: dt.datetime,
) -> pd.DataFrame:
    """
    Download one government bond yield series from FRED.
    """

    try:
        bond_data = web.DataReader(
            series_id,
            "fred",
            start_date,
            end_date,
        )

        bond_data = bond_data.dropna()

        if bond_data.empty:
            return pd.DataFrame()

        bond_data.columns = ["Yield"]

        return bond_data

    except Exception:
        return pd.DataFrame()


def render_government_bonds_section() -> None:
    """
    Render government bond yield cards and an interactive chart.
    """

    st.header("Government Bond Yields")
    st.caption(
        "U.S. yields are daily. International 10-year benchmark "
        "yields are monthly OECD observations from FRED."
    )

    end_date = dt.datetime.today()
    start_date = end_date - dt.timedelta(days=365 * 5)

    bond_histories = {}
    bond_summaries = []

    for bond_name, bond_settings in GOVERNMENT_BONDS.items():
        history = fetch_government_bond_yield(
            series_id=bond_settings["series_id"],
            start_date=start_date,
            end_date=end_date,
        )

        if history.empty or len(history) < 2:
            continue

        bond_histories[bond_name] = history

        latest_yield = float(history["Yield"].iloc[-1])
        previous_yield = float(history["Yield"].iloc[-2])

        change_percentage_points = latest_yield - previous_yield
        change_basis_points = change_percentage_points * 100

        latest_date = history.index[-1]

        bond_summaries.append(
            {
                "name": bond_name,
                "yield": latest_yield,
                "change_bps": change_basis_points,
                "latest_date": latest_date,
                "frequency": bond_settings["frequency"],
            }
        )

    if not bond_summaries:
        st.warning("Government bond yield data could not be downloaded.")
        return

    # Seven bonds: first row of four, second row of three
    cards_per_row = 3

    for i in range(0, len(bond_summaries), cards_per_row):
        row = st.columns(cards_per_row)

        for column, summary in zip(
            row,
            bond_summaries[i:i + cards_per_row],
        ):
            with column:
                st.metric(
                    label=summary["name"],
                    value=f"{summary['yield']:.2f}%",
                    delta=f"{summary['change_bps']:+.1f} bps",
                )

                st.caption(
                    f"{summary['frequency']} · "
                    f"Through {summary['latest_date']:%b %Y}"
                )

    st.subheader("Yield History")

    selected_bond = st.selectbox(
        "Select a government bond",
        options=list(bond_histories.keys()),
        key="government_bond_selector",
    )

    selected_history = bond_histories[selected_bond].reset_index()
    selected_history.columns = ["Date", "Yield"]

    figure = px.line(
        selected_history,
        x="Date",
        y="Yield",
        title=f"{selected_bond} Government Bond Yield",
        labels={
            "Date": "Date",
            "Yield": "Yield (%)",
        },
    )

    figure.update_layout(
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title="Yield (%)",
    )

    figure.update_traces(
        hovertemplate="%{y:.2f}%<extra></extra>"
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )