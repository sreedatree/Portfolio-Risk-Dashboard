from data_loader import load_prices

SECTORS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "JPM": "Financials",
    "JNJ": "Healthcare",
    "XOM": "Energy"
}

def calculate_returns(prices):
    return prices.pct_change().dropna()

def calculate_portfolio_returns(prices, weights):
    returns = calculate_returns(prices)
    return returns.dot(weights)

def calculate_portfolio_growth(prices, weights):
    portfolio_returns = calculate_portfolio_returns(prices, weights)
    return (1 + portfolio_returns).cumprod()

def calculate_correlation(prices):
    returns = calculate_returns(prices)
    return returns.corr()

def calculate_sector_allocation(stock_info, weights):
    """
    Calculate portfolio allocation by sector using
    live company information.
    """

    allocation = {}

    for stock, weight in zip(stock_info, weights):

        sector = stock["Sector"]

        if sector not in allocation:
            allocation[sector] = 0

        allocation[sector] += weight

    return allocation

def calculate_rolling_volatility(prices, weights, window=30):
    portfolio_returns = calculate_portfolio_returns(prices, weights)
    return portfolio_returns.rolling(window).std() * (252 ** 0.5)

import pandas as pd

def calculate_stock_performance(prices, tickers, weights):
    """
    Creates a summary table showing each stock's
    weight and total return over the selected period.
    """

    total_returns = (
        prices.iloc[-1] / prices.iloc[0] - 1
    )

    performance = pd.DataFrame({
        "Ticker": tickers,
        "Weight": weights,
        "Total Return": total_returns.values
    })

    return performance