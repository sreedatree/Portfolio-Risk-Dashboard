import streamlit as st
import yfinance as yf


@st.cache_data
def get_stock_info(tickers):
    """
    Returns company information for a list of tickers.
    """

    stock_data = []

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info

            stock_data.append({
                "Ticker": ticker,
                "Company": info.get("longName", ticker),
                "Sector": info.get("sector", "Unknown"),
                "Industry": info.get("industry", "Unknown")
            })

        except Exception:
            stock_data.append({
                "Ticker": ticker,
                "Company": "Invalid Ticker",
                "Sector": "Unknown",
                "Industry": "Unknown"
            })

    return stock_data