import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# ---------------- STOCK LIST ----------------
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# ---------------- FETCH DATA ----------------
def fetch_data(ticker, period):
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            return None
        data.reset_index(inplace=True)
        return data
    except:
        return None

# ---------------- INDICATORS ----------------
def add_indicators(data):
    close = data["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    data["SMA20"] = close.rolling(20).mean()
    data["EMA20"] = close.ewm(span=20).mean()

    return data

# ---------------- METRICS ----------------
def calculate_metrics(data):
    close = data["Close"].dropna()

    last = float(close.iloc[-1])
    first = float(close.iloc[0])

    change = last - first
    pct = (change / first) * 100

    return last, change, pct

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
    data = add_indicators(data)

    last, change, pct = calculate_metrics(data)

    # KPI
    st.metric(f"{ticker} Price", f"{last:.2f} USD", f"{change:.2f} ({pct:.2f}%)")

    # ---------------- CHART ----------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["Date"],
        y=data["Close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(
        x=data["Date"],
        y=data["SMA20"],
        name="SMA20"
    ))

    fig.add_trace(go.Scatter(
        x=data["Date"],
        y=data["EMA20"],
        name="EMA20"
    ))

    fig.update_layout(
        title="Price Trend",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.subheader("Recent Data")
    st.dataframe(data.tail())

# ---------------- AUTO REFRESH ----------------
time.sleep(refresh_rate)
st.rerun()
