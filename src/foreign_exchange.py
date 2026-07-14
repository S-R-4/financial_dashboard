import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

#dictionary
FX = {
    "US Dollar Index": {
        "ticker": "DX-Y.NYB",
        "unit": "Index",
        "decimals": 2,
    },

    "EUR/USD": {
        "ticker": "EURUSD=X",
        "unit": "Exchange Rate",
        "decimals": 4,
    },

    "USD/JPY": {
        "ticker": "JPY=X",
        "unit": "JPY per USD",
        "decimals": 2,
    },

    "GBP/USD": {
        "ticker": "GBPUSD=X",
        "unit": "Exchange Rate",
        "decimals": 4,
    },

    "USD/CHF": {
        "ticker": "CHF=X",
        "unit": "CHF per USD",
        "decimals": 4,
    },

    "AUD/USD": {
        "ticker": "AUDUSD=X",
        "unit": "Exchange Rate",
        "decimals": 4,
    },

    "USD/CAD": {
        "ticker": "CAD=X",
        "unit": "CAD per USD",
        "decimals": 4,
    },
}

@st.cache_data(ttl=900)
def fetch_fx_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download OHLC market data from Yahoo Finance.
    """

    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            multi_level_index=False,
        )

        if data.empty:
            return pd.DataFrame()

        required_columns = ["Open", "High", "Low", "Close"]

        if not all(column in data.columns for column in required_columns):
            return pd.DataFrame()

        return data.dropna(subset=required_columns)

    except Exception:
        return pd.DataFrame()


def render_fx_section() -> None:
    st.header("Global Forex")
    st.caption("Major foreign exchange pairings")

    histories = {}
    summaries = []

    for name, settings in FX.items():
        history = fetch_fx_data(settings["ticker"])

        if history.empty or len(history) < 2:
            continue

        histories[name] = history

        latest_close = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2])

        daily_change = latest_close - previous_close
        daily_change_pct = (daily_change / previous_close) * 100

        summaries.append(
            {
                "name": name,
                "price": latest_close,
                "change_pct": daily_change_pct,
            }
        )

    if not summaries:
        st.warning("Forex market data could not be downloaded.")
        return

    # Automatically create a 3-column metric grid
    cards_per_row = 3

    for i in range(0, len(summaries), cards_per_row):
        row = st.columns(cards_per_row)

        for column, summary in zip(
            row,
            summaries[i:i + cards_per_row],
        ):
            settings = FX[summary["name"]]

            with column:
                st.metric(
                    label=summary["name"],
                    value=(
                        f"{summary['price']:,.{settings['decimals']}f}"
                    ),
                    delta=f"{summary['change_pct']:+.2f}%",
                )

                st.caption(settings["unit"])

    st.subheader("Currency Price History")

    selected_currency = st.selectbox(
        "Select a currency pair",
        options=list(histories.keys()),
        key="currency_selector",
    )

    period = st.selectbox(
        "Chart period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        key="fx_period_selector",
    )

    selected_ticker = FX[selected_currency]["ticker"]

    chart_data = fetch_fx_data(
        ticker=selected_ticker,
        period=period,
    )

    if chart_data.empty:
        st.warning("Chart data could not be downloaded.")
        return

    candlestick = go.Figure(
        data=[
            go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name=selected_currency,
            )
        ]
    )

    candlestick.update_layout(
        title=f"{selected_currency} — Daily Candlestick Chart",
        xaxis_title=None,
        yaxis_title=FX[selected_currency]["unit"],
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        height=600,
    )

    st.plotly_chart(
        candlestick,
        width="stretch",
    )