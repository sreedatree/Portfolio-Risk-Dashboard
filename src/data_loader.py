import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data
def load_prices(
    tickers,
    start_date="2022-01-01",
    end_date="2025-01-01"
):
    """Download usable closing prices in the requested ticker order.

    Reject incomplete downloads rather than silently dropping a holding or
    filling its missing returns with zero.
    """

    tickers = list(dict.fromkeys(ticker.strip().upper() for ticker in tickers if ticker.strip()))
    if not tickers:
        raise ValueError("Please enter at least one ticker.")

    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=True
    )

    if data.empty or "Close" not in data:
        raise ValueError(f"No data available for: {', '.join(tickers)}.")

    prices = data["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    prices = prices.reindex(columns=tickers).apply(pd.to_numeric, errors="coerce")
    prices = prices.where((prices > 0) & (prices < float("inf")))
    missing = prices.columns[prices.count() < 2].tolist()
    if missing:
        raise ValueError(f"No usable price data for: {', '.join(missing)} in the selected period.")

    # Use shared observations; do not invent prices across gaps or before listing.
    prices = prices.dropna().sort_index()
    if len(prices) < 2:
        raise ValueError("Not enough overlapping price data for the selected tickers and period.")

    return prices


@st.cache_data
def load_market_data(
    start_date="2022-01-01",
    end_date="2025-01-01"
):
    """
    Download adjusted closing prices for the SPY ETF to use as a benchmark against the portfolio.
    """

    return load_prices(["SPY"], start_date, end_date)
