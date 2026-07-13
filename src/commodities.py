import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


COMMODITIES = {
    "WTI Crude": {
        "ticker": "CL=F",
        "unit": "USD/barrel",
        "decimals": 2,
    },
    "ICE Brent": {
        "ticker": "BZ=F",
        "unit": "USD/barrel",
        "decimals": 2,
    },
    "Natural Gas": {
        "ticker": "NG=F",
        "unit": "USD/MMBtu",
        "decimals": 3,
    },
    "Copper": {
        "ticker": "HG=F",
        "unit": "USD/pound",
        "decimals": 3,
    },
    "Gold": {
        "ticker": "GC=F",
        "unit": "USD/troy ounce",
        "decimals": 2,
    },
    "Silver": {
        "ticker": "SI=F",
        "unit": "USD/troy ounce",
        "decimals": 2,
    },
}


@st.cache_data(ttl=900)
def fetch_commodity_data(
    ticker: str,
    period: str = "1y",
) -> pd.DataFrame:
    data = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
        multi_level_index=False,
    )

    if data.empty:
        return pd.DataFrame()

    return data.dropna(subset=["Close"])


def render_commodities_section() -> None:
    st.header("Global Commodity Prices")
    st.caption("Front-month futures contracts")

    histories = {}
    summaries = []

    for name, settings in COMMODITIES.items():
        history = fetch_commodity_data(settings["ticker"])

        if history.empty or len(history) < 2:
            continue

        histories[name] = history

        latest = float(history["Close"].iloc[-1])
        previous = float(history["Close"].iloc[-2])
        change_pct = ((latest / previous) - 1) * 100

        summaries.append(
            {
                "name": name,
                "price": latest,
                "change_pct": change_pct,
            }
        )

    if not summaries:
        st.warning("Commodity data could not be downloaded.")
        return

    first_row = st.columns(3)
    second_row = st.columns(3)
    metric_columns = first_row + second_row

    for column, summary in zip(metric_columns, summaries):
        settings = COMMODITIES[summary["name"]]

        with column:
            st.metric(
                label=summary["name"],
                value=(
                    f"${summary['price']:,.{settings['decimals']}f}"
                ),
                delta=f"{summary['change_pct']:+.2f}%",
            )

            st.caption(settings["unit"])

    st.subheader("Commodity Price History")

    selected = st.selectbox(
        "Select a commodity",
        options=list(histories.keys()),
    )

    chart_data = histories[selected].reset_index()

    figure = px.line(
        chart_data,
        x="Date",
        y="Close",
        title=f"{selected} — Front-Month Futures",
        labels={
            "Date": "Date",
            "Close": COMMODITIES[selected]["unit"],
        },
    )

    figure.update_layout(
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title=COMMODITIES[selected]["unit"],
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )