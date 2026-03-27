import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import pytz

# ---------------- STOCK LIST ----------------
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# ---------------- FETCH DATA ----------------
def fetch_data(ticker, period):
    try:
        data = yf.download(ticker, period=period, progress=False)

        if data is None or data.empty:
            return None

        data.reset_index(inplace=True)

        # Ensure Date column exists
        if 'Date' not in data.columns:
            data.rename(columns={data.columns[0]: 'Date'}, inplace=True)

        return data
    except:
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

# ---------------- MAIN ----------------
data = fetch_data(ticker, period)

if data is None:
    st.error("No data available")
else:
    # Clean data
    data = data.dropna()

    # KPIs
    close = data["Close"]
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
        y=data["Close"],
        name="Price",
        mode="lines"
    ))

    fig_line.update_layout(height=400)

    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- CANDLESTICK ----------------
    st.subheader("🕯️ Candlestick Chart")

    fig_candle = go.Figure(data=[go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    )])

    fig_candle.update_layout(height=500)

    st.plotly_chart(fig_candle, use_container_width=True)

    # Data table
    st.subheader("Recent Data")
    st.dataframe(data.tail())

# ---------------- AUTO REFRESH ----------------
time.sleep(refresh_rate)
st.rerun()
