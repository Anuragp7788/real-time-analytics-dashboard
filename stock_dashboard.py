import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# ---------------- STOCK LIST ----------------
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# ---------------- FETCH DATA (FINAL FIX) ----------------
def fetch_data(ticker):
    try:
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period="6mo")   # STABLE METHOD

        if data.empty:
            return None

        data = data.reset_index()

        # Rename if needed
        if "Date" not in data.columns:
            data.rename(columns={"Datetime": "Date"}, inplace=True)

        data["Date"] = pd.to_datetime(data["Date"])

        # Ensure numeric
        cols = ["Open", "High", "Low", "Close"]
        for col in cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        data = data.dropna()

        return data

    except Exception as e:
        st.error(f"Fetch error: {e}")
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

ticker = st.selectbox("Select Asset", stocks)

refresh_rate = st.slider("Auto Refresh (seconds)", 5, 60, 10)

st.caption(f"Auto-refresh every {refresh_rate} sec")

# SAFE AUTO REFRESH
st_autorefresh(interval=refresh_rate * 1000, key="refresh")

# ---------------- MAIN ----------------
data = fetch_data(ticker)

if data is None or len(data) < 10:
    st.error("❌ Data not loading from API (try again)")
else:
    st.success("✅ Data Loaded Successfully")

    # DEBUG
    st.write("Rows:", len(data))

    # KPIs
    last = float(data["Close"].iloc[-1])
    first = float(data["Close"].iloc[0])

    change = last - first
    pct = (change / first) * 100

    col1, col2 = st.columns(2)
    col1.metric(f"{ticker} Price", f"{last:.2f}", f"{change:.2f} ({pct:.2f}%)")
    col2.markdown(f"### {market_status()}")

    # ---------------- LINE CHART ----------------
    st.subheader("📈 Line Chart")

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=data["Date"],
        y=data["Close"],
        mode="lines",
        name="Price"
    ))

    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- CANDLESTICK ----------------
    st.subheader("🕯️ Candlestick Chart")

    fig2 = go.Figure()

    fig2.add_trace(go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    ))

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(data.tail())
