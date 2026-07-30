import pandas as pd
from data_loader import load_prices, load_market_data

def calculate_returns(prices):
    return prices.pct_change().dropna()

def calculate_portfolio_returns(prices, weights):
    returns = calculate_returns(prices)
    return returns.dot(weights)

def calculate_portfolio_growth(prices, weights, start_date=None, end_date=None):
    """
    Calculate normalized growth for both the portfolio and the SPY benchmark.
    """

    portfolio_returns = calculate_portfolio_returns(prices, weights)
    portfolio_growth = (1 + portfolio_returns).cumprod()

    if isinstance(portfolio_growth, pd.DataFrame):
        portfolio_growth = portfolio_growth.squeeze()

    market_prices = load_market_data(
        start_date=start_date,
        end_date=end_date
    )

    if isinstance(market_prices, pd.DataFrame):
        market_prices = market_prices.squeeze()

    benchmark_growth = market_prices / market_prices.iloc[0]

    return {
        "portfolio": portfolio_growth,
        "benchmark": benchmark_growth
    }

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