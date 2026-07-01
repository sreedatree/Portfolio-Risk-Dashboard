import streamlit as st
import yfinance as yf

TICKERS = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

@st.cache_data
def load_prices(
    start_date="2022-01-01",
    end_date="2025-01-01"
):
    """Download portfolio stock prices."""

    prices = yf.download(
        TICKERS,
        start=start_date,
        end=end_date
    )["Close"]

    return prices

@st.cache_data
def load_market_data(
    start_date="2022-01-01",
    end_date="2025-01-01"
):
    """
    Download SPY ETF prices for market comparison.
    """

    market = yf.download(
        "SPY",
        start=start_date,
        end=end_date
    )["Close"]

    return market