import datetime

import streamlit as st
import yfinance as yf
from pandas_datareader import data as web


YAHOO_TICKERS = {
    # Energy
    "WTI": "CL=F",
    "Brent": "BZ=F",
    "Natural Gas": "NG=F",

    # Materials
    "Copper": "HG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",

    # Equities
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    
    # FX
    "EUR/USD": "EURUSD=X",
    "USD/JPY": "JPY=X",
    "GBP/USD": "GBPUSD=X",
    "DXY": "DX-Y.NYB",
}

FRED_SERIES = {
    "US 2Y": "DGS2",
    "US 10Y": "DGS10",
    "Italy 10Y": "IRLTLT01ITM156N",
    "Spain 10Y": "IRLTLT01ESM156N",
}


@st.cache_data(ttl=300)
def fetch_yahoo_snapshot():
    results = {}

    for name, ticker in YAHOO_TICKERS.items():
        try:
            data = yf.download(
                ticker,
                period="5d",
                interval="1d",
                auto_adjust=False,
                progress=False,
                multi_level_index=False,
            )

            if data.empty or "Close" not in data.columns:
                continue

            closes = data["Close"].dropna()

            if len(closes) < 2:
                continue

            current = float(closes.iloc[-1])
            previous = float(closes.iloc[-2])

            results[name] = {
                "value": current,
                "change": current - previous,
                "change_pct": ((current / previous) - 1) * 100,
            }

        except Exception:
            continue

    return results


@st.cache_data(ttl=3600)
def fetch_fred_snapshot():
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=400)

    results = {}

    for name, series_id in FRED_SERIES.items():
        try:
            data = web.DataReader(
                series_id,
                "fred",
                start_date,
                end_date,
            )

            values = data.iloc[:, 0].dropna()

            if len(values) < 2:
                continue

            current = float(values.iloc[-1])
            previous = float(values.iloc[-2])

            results[name] = {
                "value": current,
                "change": current - previous,
            }

        except Exception:
            continue

    return results


def calculate_brent_wti_spread(yahoo_data):
    if "Brent" not in yahoo_data or "WTI" not in yahoo_data:
        return None

    current_spread = (
        yahoo_data["Brent"]["value"]
        - yahoo_data["WTI"]["value"]
    )

    previous_brent = (
        yahoo_data["Brent"]["value"]
        - yahoo_data["Brent"]["change"]
    )

    previous_wti = (
        yahoo_data["WTI"]["value"]
        - yahoo_data["WTI"]["change"]
    )

    previous_spread = previous_brent - previous_wti

    return {
        "value": current_spread,
        "change": current_spread - previous_spread,
    }


def render_summary_section():
    st.subheader("Market Snapshot")

    yahoo_data = fetch_yahoo_snapshot()
    fred_data = fetch_fred_snapshot()
    spread = calculate_brent_wti_spread(yahoo_data)

# -----------------------------------------------------
# Row 1: Government bond yields
# -----------------------------------------------------

    st.caption("Government Bond Yields")

    rate_names = [
        "US 2Y",
        "US 10Y",
        "Italy 10Y",
        "Spain 10Y",
    ]

    rate_columns = st.columns(4)

    for column, name in zip(rate_columns, rate_names):
        data = fred_data.get(name)

        with column:
            if data:
                st.metric(
                    label=name,
                    value=f"{data['value']:.2f}%",
                    delta=f"{data['change']:+.2f} pts",
                    border=True,
                )
            else:
                st.metric(
                    label=name,
                    value="N/A",
                    border=True,
                )


    # -----------------------------------------------------
    # Row 2: Commodities
    # -----------------------------------------------------

    st.caption("Commodities")

    commodity_names = [
        "WTI",
        "Brent",
        "Brent − WTI",
        "Natural Gas",
    ]

    commodity_columns = st.columns(4)

    for column, name in zip(commodity_columns, commodity_names):
        with column:
            if name == "Brent − WTI":
                if spread:
                    st.metric(
                        label=name,
                        value=f"${spread['value']:,.2f}",
                        delta=f"${spread['change']:+.2f}",
                        border=True,
                    )
                else:
                    st.metric(
                        label=name,
                        value="N/A",
                        border=True,
                    )

            else:
                data = yahoo_data.get(name)

                if data:
                    st.metric(
                        label=name,
                        value=f"${data['value']:,.2f}",
                        delta=f"{data['change_pct']:+.2f}%",
                        border=True,
                    )
                else:
                    st.metric(
                        label=name,
                        value="N/A",
                        border=True,
                    )


    # -----------------------------------------------------
    # Row 3: Equity indexes
    # -----------------------------------------------------

    st.caption("Equity Indexes")

    index_names = [
        "S&P 500",
        "Nasdaq 100",
        "Dow Jones",
        "Russell 2000",
    ]

    index_columns = st.columns(4)

    for column, name in zip(index_columns, index_names):
        data = yahoo_data.get(name)

        with column:
            if data:
                st.metric(
                    label=name,
                    value=f"{data['value']:,.2f}",
                    delta=f"{data['change_pct']:+.2f}%",
                    border=True,
                )
            else:
                st.metric(
                    label=name,
                    value="N/A",
                    border=True,
                )


    # -----------------------------------------------------
    # Row 4: Foreign exchange
    # -----------------------------------------------------

    st.caption("Foreign Exchange")

    fx_names = [
        "EUR/USD",
        "USD/JPY",
        "GBP/USD",
        "DXY"
    ]

    fx_columns = st.columns(4)

    for column, name in zip(fx_columns, fx_names):
        data = yahoo_data.get(name)

        with column:
            if data:
                if name in {"EUR/USD", "GBP/USD"}:
                    formatted_value = f"{data['value']:.4f}"
                else:
                    formatted_value = f"{data['value']:.2f}"

                st.metric(
                    label=name,
                    value=formatted_value,
                    delta=f"{data['change_pct']:+.2f}%",
                    border=True,
                )
            else:
                st.metric(
                    label=name,
                    value="N/A",
                    border=True,
                )

    # -----------------------------------------------------
    # Row 5: Materials
    # -----------------------------------------------------

    st.caption("Materials")

    material_names = [
        "Copper",
        "Gold",
        "Silver",
        "Platinum",
    ]

    material_columns = st.columns(4)

    for column, name in zip(material_columns, material_names):
        data = yahoo_data.get(name)

        with column:
            if data:
                st.metric(
                    label=name,
                    value=f"${data['value']:,.2f}",
                    delta=f"{data['change_pct']:+.2f}%",
                    border=True,
                )
            else:
                st.metric(
                    label=name,
                    value="N/A",
                    border=True,
                )