import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


EQUITIES = {
    "S&P 500": {
        "ticker": "^GSPC",
        "unit": "Index points",
        "decimals": 2,
    },
    "Nasdaq Composite": {
        "ticker": "^IXIC",
        "unit": "Index points",
        "decimals": 2,
    },
    "Dow Jones Industrial Average": {
        "ticker": "^DJI",
        "unit": "Index points",
        "decimals": 2,
    },
    "Russell 2000": {
        "ticker": "^RUT",
        "unit": "Index points",
        "decimals": 2,
    },
    "VIX": {
        "ticker": "^VIX",
        "unit": "Index points",
        "decimals": 2,
    },
}


@st.cache_data(ttl=900)
def fetch_equity_data(
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


def render_equities_section() -> None:
    st.header("Global Equity Markets")
    st.caption("Major U.S. equity indexes and market volatility")

    histories = {}
    summaries = []

    for name, settings in EQUITIES.items():
        history = fetch_equity_data(settings["ticker"])

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
        st.warning("Equity market data could not be downloaded.")
        return

    # Automatically create a 3-column metric grid
    cards_per_row = 3

    for i in range(0, len(summaries), cards_per_row):
        row = st.columns(cards_per_row)

        for column, summary in zip(
            row,
            summaries[i:i + cards_per_row],
        ):
            settings = EQUITIES[summary["name"]]

            with column:
                st.metric(
                    label=summary["name"],
                    value=(
                        f"{summary['price']:,.{settings['decimals']}f}"
                    ),
                    delta=f"{summary['change_pct']:+.2f}%",
                )

                st.caption(settings["unit"])

    st.subheader("Equity Price History")

    selected_equity = st.selectbox(
        "Select an equity index",
        options=list(histories.keys()),
        key="equity_selector",
    )

    period = st.selectbox(
        "Chart period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        key="equity_period_selector",
    )

    selected_ticker = EQUITIES[selected_equity]["ticker"]

    chart_data = fetch_equity_data(
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
                name=selected_equity,
            )
        ]
    )

    candlestick.update_layout(
        title=f"{selected_equity} — Daily Candlestick Chart",
        xaxis_title=None,
        yaxis_title=EQUITIES[selected_equity]["unit"],
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        height=600,
    )

    st.plotly_chart(
        candlestick,
        use_container_width=True,
    )