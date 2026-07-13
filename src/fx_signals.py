import streamlit as st
import yfinance as yf

fx_signal_tickers = {
    "USD/JPY": "USDJPY=X",
    "AUD/JPY": "AUDJPY=X",
    "NZD/JPY": "NZDJPY=X",
    "EUR/USD": "EURUSD=X",
    "USD/CHF": "USDCHF=X",
    "USD/CNH": "USDCNH=X",
    "USD/MXN": "USDMXN=X",
    "USD/BRL": "USDBRL=X",
    "USD/KRW": "USDKRW=X",
    "USD/TWD": "USDTWD=X",
    "USD/ZAR": "USDZAR=X",
    "NOK/SEK": "NOKSEK=X",
    "CAD/JPY": "CADJPY=X",
}


fx_signal_explainers = {
    "USD/JPY": "Global risk sentiment and U.S. Treasury yields.",
    "AUD/JPY": "One of the clearest risk-on versus risk-off indicators.",
    "NZD/JPY": "Similar to AUD/JPY, but often more sensitive to global growth expectations.",
    "EUR/USD": "Broad U.S. dollar strength relative to Europe and the global macro environment.",
    "USD/CHF": "Safe-haven demand for the Swiss franc.",
    "USD/CNH": "China's economy, capital flows, and trade tensions.",
    "USD/MXN": "Emerging-market risk appetite and carry-trade demand.",
    "USD/BRL": "Commodity demand, Brazilian conditions, and emerging-market sentiment.",
    "USD/KRW": "The semiconductor cycle, Asian exports, and regional risk sentiment.",
    "USD/TWD": "Taiwanese technology exports and global semiconductor demand.",
    "USD/ZAR": "Global commodity demand and emerging-market risk appetite.",
    "NOK/SEK": "Oil exposure in Norway relative to broader European and Swedish growth.",
    "CAD/JPY": "Oil prices combined with global risk appetite.",
}

import time

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=900)
def fetch_fx_signal(
    ticker: str,
    period: str = "5d",
    interval: str = "5m",
) -> dict | None:

    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            multi_level_index=False,
            threads=False,
        )

        if data.empty:
            print(f"{ticker}: Yahoo returned an empty DataFrame")
            return None

        close = data["Close"].dropna()

        if len(close) < 2:
            print(f"{ticker}: fewer than two prices returned")
            return None

        current_value = float(close.iloc[-1])
        previous_value = float(close.iloc[-2])

        change_pct = (
            (current_value - previous_value)
            / previous_value
        ) * 100

        return {
            "value": current_value,
            "change_pct": change_pct,
        }

    except Exception as error:
        print(f"{ticker}: {type(error).__name__}: {error}")
        return None

def render_fx_signals() -> None:
    st.header("Currency Market Signals")

    st.caption(
        "Currency pairs can provide signals about risk appetite, "
        "interest rates, commodities, trade, and global growth."
    )

    pair_names = list(fx_signal_tickers.keys())

    for start_index in range(0, len(pair_names), 2):
        columns = st.columns(2)

        row_pairs = pair_names[start_index:start_index + 2]

        for column, pair in zip(columns, row_pairs):
            ticker = fx_signal_tickers[pair]
            explainer = fx_signal_explainers[pair]
            data = fetch_fx_signal(ticker)

            with column:
                with st.container(border=True):
                    metric_column, explainer_column = st.columns(
                        [1, 2],
                        vertical_alignment="center",
                    )

                    with metric_column:
                        st.markdown(f"#### {pair}")

                        if data:
                            st.metric(
                                label="Current Rate",
                                value=f"{data['value']:,.4f}",
                                delta=f"{data['change_pct']:+.2f}%",
                            )
                        else:
                            st.metric(
                                label="Current Rate",
                                value="N/A",
                            )

                    with explainer_column:
                    #     st.markdown("**What it often represents**")
                        st.markdown(f"### {explainer}")