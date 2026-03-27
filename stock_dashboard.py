import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# ---------------- FETCH DATA ----------------
def fetch_data(ticker, period, interval):
    try:
        end = datetime.now()
        start = end - timedelta(days=int(period[:-1]) if period[:-1].isdigit() else 30)
        data = yf.download(ticker, start=start, end=end, interval=interval)

        if data.empty:
            return None

        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
        return data

    except:
        return None


# ---------------- INDICATORS ----------------
def add_indicators(data):
    close = data['Close']

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    close = close.dropna()

    data['SMA_20'] = close.rolling(20).mean()
    data['EMA_20'] = close.ewm(span=20).mean()
    data['MA10'] = close.rolling(10).mean()

    return data


# ---------------- METRICS ----------------
def calculate_metrics(data):
    close = data['Close']

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    close = close.dropna()

    last = float(close.iloc[-1])
    first = float(close.iloc[0])

    change = last - first
    pct = (change / first) * 100

    high = float(data['High'].max())
    low = float(data['Low'].min())
    volume = int(data['Volume'].sum())

    return last, change, pct, high, low, volume


# ---------------- UI ----------------
st.set_page_config(layout="wide")

st.title("Real-Time Analytics Dashboard")
st.subheader("Time-Series Data Analysis and Visualization")

# Sidebar
st.sidebar.header("Settings")

ticker1 = st.sidebar.text_input("Primary Asset", "AAPL")
ticker2 = st.sidebar.text_input("Compare With (Optional)", "MSFT")

period = st.sidebar.selectbox("Time Range", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])

refresh_rate = st.sidebar.slider("Auto Refresh (seconds)", 5, 60, 10)

interval_map = {
    "1d": "1m",
    "5d": "5m",
    "1mo": "1h",
    "3mo": "1d",
    "6mo": "1d",
    "1y": "1wk",
}

st.caption(f"Auto-refreshing every {refresh_rate} seconds")

# ---------------- MAIN ----------------
data1 = fetch_data(ticker1, period, interval_map[period])

if data1 is None:
    st.error("Invalid primary asset")
else:
    data1 = add_indicators(data1)

    last, change, pct, high, low, volume = calculate_metrics(data1)

    # KPIs
    st.metric(f"{ticker1} Price", f"{last:.2f} USD", f"{change:.2f} ({pct:.2f}%)")

    col1, col2, col3 = st.columns(3)
    col1.metric("High", f"{high:.2f}")
    col2.metric("Low", f"{low:.2f}")
    col3.metric("Volume", f"{volume:,}")

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data1["Datetime"], y=data1["Close"], name=ticker1
    ))

    fig.add_trace(go.Scatter(
        x=data1["Datetime"], y=data1["SMA_20"], name="SMA 20"
    ))

    fig.add_trace(go.Scatter(
        x=data1["Datetime"], y=data1["EMA_20"], name="EMA 20"
    ))

    fig.add_trace(go.Scatter(
        x=data1["Datetime"], y=data1["MA10"], name="MA 10"
    ))

    # Comparison feature
    if ticker2:
        data2 = fetch_data(ticker2, period, interval_map[period])

        if data2 is not None:
            fig.add_trace(go.Scatter(
                x=data2["Datetime"], y=data2["Close"], name=ticker2
            ))

    fig.update_layout(
        title="Trend Analysis",
        xaxis_title="Time",
        yaxis_title="Value",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Data Table
    st.subheader("Historical Data")
    st.dataframe(data1[["Datetime", "Open", "High", "Low", "Close", "Volume"]])


# ---------------- AUTO REFRESH ----------------
time.sleep(refresh_rate)
st.rerun()
