from data_loader import load_prices

# Portfolio weights
DEFAULT_WEIGHTS = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]

SECTORS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "JPM": "Financials",
    "JNJ": "Healthcare",
    "XOM": "Energy"
}


def calculate_returns(
        start_date="2022-01-01",
        end_date="2025-01-01"):
    """Calculate daily percentage returns for each stock."""
    prices = load_prices(start_date, end_date)
    return prices.pct_change().dropna()


def calculate_portfolio_returns(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None
):
    """Calculate weighted daily portfolio returns."""
    returns = calculate_returns(start_date, end_date)
    if weights is None:
        weights = DEFAULT_WEIGHTS
    return returns.dot(weights)


def calculate_portfolio_growth(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None
):
    """Calculate cumulative portfolio growth over time."""
    portfolio_returns = calculate_portfolio_returns(
    start_date,
    end_date,
    weights
)
    return (1 + portfolio_returns).cumprod()


def calculate_correlation(
        start_date="2022-01-01",
        end_date="2025-01-01"):
    """
    Calculate the correlation matrix of daily stock returns.
    """
    returns = calculate_returns(start_date, end_date)
    return returns.corr()

def calculate_sector_allocation(weights=None):
    """
    Calculate portfolio allocation by sector.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS

    tickers = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

    allocation = {}

    for ticker, weight in zip(tickers, weights):
        sector = SECTORS[ticker]

        if sector not in allocation:
            allocation[sector] = 0

        allocation[sector] += weight

    return allocation

def calculate_rolling_volatility(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None,
    window=30
):
    """
    Calculate rolling annualized volatility.
    """

    portfolio_returns = calculate_portfolio_returns(
        start_date,
        end_date,
        weights
    )

    rolling_vol = (
        portfolio_returns
        .rolling(window)
        .std()
        * (252 ** 0.5)
    )

    return rolling_vol

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