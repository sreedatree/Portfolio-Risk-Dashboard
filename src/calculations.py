# Portfolio calculation utilities for returns, growth, risk, and allocation.

import pandas as pd
from data_loader import load_prices, load_market_data


def calculate_returns(prices):
    """Calculate daily percentage returns for each stock, excluding missing rows."""
    return prices.pct_change().dropna()


def calculate_portfolio_returns(prices, weights):
    """Calculate weighted daily portfolio returns from individual stock returns."""
    returns = calculate_returns(prices)
    return returns.dot(weights)


def calculate_portfolio_growth(prices, weights, start_date=None, end_date=None):
    """Calculate cumulative portfolio growth alongside normalized SPY growth."""

    # Compound daily weighted returns into a cumulative growth series.
    portfolio_returns = calculate_portfolio_returns(prices, weights)
    portfolio_growth = (1 + portfolio_returns).cumprod()

    if isinstance(portfolio_growth, pd.DataFrame):
        portfolio_growth = portfolio_growth.squeeze()

    # Retrieve benchmark prices for the same selected date range.
    market_prices = load_market_data(
        start_date=start_date,
        end_date=end_date
    )

    if isinstance(market_prices, pd.DataFrame):
        market_prices = market_prices.squeeze()

    # Normalize the benchmark to a starting value of 1 for comparison.
    benchmark_growth = market_prices / market_prices.iloc[0]

    return {
        "portfolio": portfolio_growth,
        "benchmark": benchmark_growth
    }


def calculate_portfolio_comparison(prices_a, weights_a, prices_b, weights_b):
    """Compare total return, annualized volatility, Sharpe ratio, and drawdown."""

    returns_a = calculate_portfolio_returns(prices_a, weights_a)
    returns_b = calculate_portfolio_returns(prices_b, weights_b)

    portfolio_growth_a = (1 + returns_a).cumprod()
    portfolio_growth_b = (1 + returns_b).cumprod()

    total_return_a = portfolio_growth_a.iloc[-1] - 1
    total_return_b = portfolio_growth_b.iloc[-1] - 1

    # Annualize daily volatility using approximately 252 trading days per year.
    volatility_a = returns_a.std() * (252 ** 0.5)
    volatility_b = returns_b.std() * (252 ** 0.5)

    # Estimate annualized Sharpe ratios from daily returns (no risk-free adjustment).
    sharpe_a = (returns_a.mean() / returns_a.std()) * (252 ** 0.5)
    sharpe_b = (returns_b.mean() / returns_b.std()) * (252 ** 0.5)

    # Measure each portfolio's largest decline from its prior cumulative peak.
    max_drawdown_a = (
        portfolio_growth_a / portfolio_growth_a.cummax() - 1
    ).min()

    max_drawdown_b = (
        portfolio_growth_b / portfolio_growth_b.cummax() - 1
    ).min()

    return pd.DataFrame({
        "Metric": [
            "Total Return",
            "Volatility",
            "Sharpe Ratio",
            "Max Drawdown"
        ],
        "Portfolio A": [
            total_return_a,
            volatility_a,
            sharpe_a,
            max_drawdown_a
        ],
        "Portfolio B": [
            total_return_b,
            volatility_b,
            sharpe_b,
            max_drawdown_b
        ]
    })


def calculate_correlation(prices):
    """Return the correlation matrix of stock daily returns."""
    returns = calculate_returns(prices)
    return returns.corr()


def calculate_sector_allocation(stock_info, weights):
    """Aggregate portfolio weights by each stock's reported sector."""

    allocation = {}

    for stock, weight in zip(stock_info, weights):

        sector = stock["Sector"]

        if sector not in allocation:
            allocation[sector] = 0

        # Sum weights when multiple holdings belong to the same sector.
        allocation[sector] += weight

    return allocation


def calculate_rolling_volatility(prices, weights, window=30):
    """Calculate annualized rolling portfolio volatility over a trading-day window."""
    portfolio_returns = calculate_portfolio_returns(prices, weights)
    return portfolio_returns.rolling(window).std() * (252 ** 0.5)


def calculate_stock_performance(prices, tickers, weights):
    """Build a holdings table containing tickers, weights, and total returns."""

    # Measure each stock's price change from the first to the last observation.
    total_returns = (
        prices.iloc[-1] / prices.iloc[0] - 1
    )

    performance = pd.DataFrame({
        "Ticker": tickers,
        "Weight": weights,
        "Total Return": total_returns.values
    })

    return performance