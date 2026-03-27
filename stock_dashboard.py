import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Fetch data
def fetch_stock_data(ticker, period, interval):
    try:
        end_date = datetime.now()
        if period == '1wk':
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=int(period[:-1]))

        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

        if data.empty:
            st.error(f"No data found for {ticker}")
            return None

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Process data
def process_data(data):
    data.reset_index(inplace=True)
    data.rename(columns={'Date': 'Datetime'}, inplace=True)
    return data

# Calculate metrics (FIXED)
def calculate_metrics(data):
    close = data['Close']

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    close = close.dropna()

    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[0])

    change = last_close - prev_close
    pct_change = (change / prev_close) * 100

    high = float(data['High'].max())
    low = float(data['Low'].min())
    volume = int(data['Volume'].sum())

    return last_close, change, pct_change, high, low, volume

# Indicators (NO ta library)
def add_indicators(data):
    close = data['Close']

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    data['SMA_20'] = close.rolling(20).mean()
    data['EMA_20'] = close.ewm(span=20).mean()
    data['MA10'] = close.rolling(10).mean()

    return data

# UI
st.set_page_config(layout='wide')
st.title('Real-Time Analytics Dashboard')
st.subheader('Time-Series Data Analysis and Visualization')

# Sidebar
st.sidebar.header('Chart Parameters')
ticker = st.sidebar.text_input('Asset', 'AAPL')
time_period = st.sidebar.selectbox('Time Range', ['1d', '5d', '1mo', '3mo', '6mo', '1y'])
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])

interval_mapping = {
    '1d': '1m',
    '5d': '5m',
    '1mo': '1h',
    '3mo': '1d',
    '6mo': '1d',
    '1y': '1wk',
}

# Run app
if st.sidebar.button('Update'):
    data = fetch_stock_data(ticker, time_period, interval_mapping[time_period])

    if data is not None:
        data = process_data(data)
        data = add_indicators(data)

        last_close, change, pct_change, high, low, volume = calculate_metrics(data)

        # Metrics
        st.metric(f"{ticker} Price", f"{last_close:.2f} USD", f"{change:.2f} ({pct_change:.2f}%)")

        col1, col2, col3 = st.columns(3)
        col1.metric('High', f"{high:.2f}")
        col2.metric('Low', f"{low:.2f}")
        col3.metric('Volume', f"{volume:,}")

        # Chart
        fig = go.Figure()

        if chart_type == 'Candlestick':
            fig.add_trace(go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close']
            ))
        else:
            fig = px.line(data, x='Datetime', y='Close')

        # Indicators
        fig.add_trace(go.Scatter(x=data['Datetime'], y=data['SMA_20'], name='SMA 20'))
        fig.add_trace(go.Scatter(x=data['Datetime'], y=data['EMA_20'], name='EMA 20'))
        fig.add_trace(go.Scatter(x=data['Datetime'], y=data['MA10'], name='MA 10'))

        fig.update_layout(
            title=f"{ticker} Trend Analysis",
            xaxis_title='Time',
            yaxis_title='Value',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tables
        st.subheader('Historical Data')
        st.dataframe(data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']])

        st.subheader('Indicators')
        st.dataframe(data[['Datetime', 'SMA_20', 'EMA_20', 'MA10']])

# Sidebar info
st.sidebar.subheader('About')
st.sidebar.info('This dashboard analyzes time-series data and provides insights using visualization and indicators.')
