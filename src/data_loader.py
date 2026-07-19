import streamlit as st
import yfinance as yf


@st.cache_data
def load_prices(
    tickers,
    start_date="2022-01-01",
    end_date="2025-01-01"
):
    """
    Download historical closing prices for a list of stock tickers.
    """

    prices = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False
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
        end=end_date,
        progress=False
    )["Close"]

    return market