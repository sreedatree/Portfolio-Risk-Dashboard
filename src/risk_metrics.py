from calculations import calculate_portfolio_returns
from data_loader import load_market_data

def calculate_beta(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None
):
    """
    Calculate portfolio beta relative to SPY.
    """

    portfolio_returns = calculate_portfolio_returns(
        start_date,
        end_date,
        weights
    )

    market_prices = load_market_data(
        start_date,
        end_date
    )

    market_returns = market_prices.pct_change().dropna()
    # Convert a one-column DataFrame returned by yfinance into a Series
    if hasattr(market_returns, "squeeze"):
        market_returns = market_returns.squeeze()

    portfolio_returns, market_returns = portfolio_returns.align(
        market_returns,
        join="inner"
    )

    covariance = portfolio_returns.cov(market_returns)

    market_variance = market_returns.var()

    beta = covariance / market_variance

    return beta

def calculate_max_drawdown(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None
):
    """
    Calculate the portfolio's maximum drawdown.
    """

    portfolio_returns = calculate_portfolio_returns(
        start_date,
        end_date,
        weights
    )

    portfolio_growth = (1 + portfolio_returns).cumprod()

    rolling_max = portfolio_growth.cummax()

    drawdown = (
        portfolio_growth - rolling_max
    ) / rolling_max

    return drawdown.min()


def calculate_risk_metrics(
    start_date="2022-01-01",
    end_date="2025-01-01",
    weights=None
):
    """Calculate annual return, volatility, and Sharpe ratio."""

    portfolio_returns = calculate_portfolio_returns(
    start_date,
    end_date,
    weights
)

    annual_return = portfolio_returns.mean() * 252
    volatility = portfolio_returns.std() * (252 ** 0.5)

    risk_free_rate = 0.02

    sharpe_ratio = (annual_return - risk_free_rate) / volatility

    beta = calculate_beta(
        start_date,
        end_date,
        weights
    )

    max_drawdown = calculate_max_drawdown(
    start_date,
    end_date,
    weights
)

    return {
        "Annual Return": annual_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Beta": beta,
        "Max Drawdown": max_drawdown
    }