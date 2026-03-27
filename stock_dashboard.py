import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# ---------------- STOCK LIST ----------------
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# ---------------- FETCH DATA ----------------
def fetch_data(ticker, period):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval="1d",
            progress=False
        )

        if data is None or data.empty:
            return None

        data = data.dropna().reset_index()

        # Ensure Date column
        if "Date" not in data.columns:
            data.rename(columns={data.columns[0]: "Date"}, inplace=True)

        data["Date"] = pd.to_datetime(data["Date"])

        return data

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# ---------------- MARKET STATUS ----------------
def market_status():
    tz = pytz.timezone("US/Eastern")
    now = datetime.now(tz)

    open_time = now.replace(hour=9, minute=30, second=0)
    close_time = now.replace(hour=16, minute=0, second=0)

    if now.weekday() >= 5:
        return "🔴 Market Closed (Weekend)"
    elif open_time <= now <= close_time:
        return "🟢 Market Open"
    else:
        return "🔴 Market Closed"


# ---------------- UI ----------------
st.set_page_config(layout="wide")

st.title("📊 Real-Time Analytics Dashboard")
st.subheader("Time-Series Data Visualization")

# Sidebar
st.sidebar.header("Settings")

ticker = st.sidebar.selectbox("Select Asset", stocks)
period = st.sidebar.selectbox("Time Range", ["1mo", "3mo", "6mo", "1y"])
refresh_rate = st.sidebar.slider("Auto Refresh (seconds)", 5, 60, 10)

st.caption(f"Auto-refresh every {refresh_rate} seconds")

# ---------------- AUTO REFRESH (SAFE) ----------------
st_autorefresh(interval=refresh_rate * 1000, key="datarefresh")

# ---------------- MAIN ----------------
data = fetch_data(ticker, period)

if data is None:
    st.error("No data available")
else:
    # DEBUG (optional remove later)
    st.write("Rows:", len(data))

    # KPIs
    close = data["Close"].astype(float)

    last = float(close.iloc[-1])
    first = float(close.iloc[0])

    change = last - first
    pct = (change / first) * 100

    col1, col2 = st.columns(2)
    col1.metric(f"{ticker} Price", f"{last:.2f} USD", f"{change:.2f} ({pct:.2f}%)")
    col2.markdown(f"### {market_status()}")

    # ---------------- LINE CHART ----------------
    st.subheader("📈 Line Chart")

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=data["Date"],
        y=data["Close"].astype(float),
        mode="lines",
        name="Price"
    ))

    fig_line.update_layout(height=400)

    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- CANDLESTICK ----------------
    st.subheader("🕯️ Candlestick Chart")

    fig_candle = go.Figure()

    fig_candle.add_trace(go.Candlestick(
        x=data["Date"],
        open=data["Open"].astype(float),
        high=data["High"].astype(float),
        low=data["Low"].astype(float),
        close=data["Close"].astype(float)
    ))

    fig_candle.update_layout(height=500)

    st.plotly_chart(fig_candle, use_container_width=True)

    # Data table
    st.subheader("Recent Data")
    st.dataframe(data.tail())
