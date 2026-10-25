# Calculate historical portfolio risk metrics using weighted daily returns.

from calculations import calculate_portfolio_returns
from data_loader import load_market_data


def calculate_beta(prices, start_date, end_date, weights):
    """
    Measure portfolio sensitivity to the S&P 500 (SPY) benchmark
    using covariance and market variance.
    """

    # Calculate the portfolio's weighted daily returns.
    portfolio_returns = calculate_portfolio_returns(prices, weights)

    # Load historical market prices for the selected analysis period.
    market_prices = load_market_data(
        start_date,
        end_date
    )

    # Convert market prices into daily percentage returns.
    market_returns = market_prices.pct_change().dropna()

    # Ensure the benchmark returns are represented as a Series.
    if hasattr(market_returns, "squeeze"):
        market_returns = market_returns.squeeze()

    # Align portfolio and benchmark returns using shared trading dates.
    portfolio_returns, market_returns = portfolio_returns.align(
        market_returns,
        join="inner"
    )

    # Beta = Covariance(Portfolio, Market) / Variance(Market).
    covariance = portfolio_returns.cov(market_returns)
    market_variance = market_returns.var()

    beta = covariance / market_variance

    return beta


def calculate_max_drawdown(prices, weights):
    """
    Calculate the largest historical percentage decline
    from a previous portfolio peak.
    """

    # Calculate weighted daily portfolio returns.
    portfolio_returns = calculate_portfolio_returns(prices, weights)

    # Convert daily returns into cumulative portfolio growth.
    portfolio_growth = (1 + portfolio_returns).cumprod()

    # Track the highest portfolio value reached up to each date.
    rolling_max = portfolio_growth.cummax()

    # Calculate the percentage decline from the previous peak.
    drawdown = (
        portfolio_growth - rolling_max
    ) / rolling_max

    # Return the most negative drawdown observed.
    return drawdown.min()


def calculate_sortino_ratio(prices, weights):
    """
    Calculate the Sortino ratio using downside volatility
    to evaluate risk-adjusted portfolio performance.
    """

    portfolio_returns = calculate_portfolio_returns(prices, weights)

    # Assume a 2% annual risk-free rate and 252 trading days per year.
    risk_free_rate = 0.02
    daily_risk_free_rate = risk_free_rate / 252

    # Calculate returns above or below the daily risk-free threshold.
    excess_returns = portfolio_returns - daily_risk_free_rate

    # Isolate returns that fall below the risk-free threshold.
    downside_returns = excess_returns[excess_returns < 0]

    # Annualize the standard deviation of downside returns.
    downside_deviation = downside_returns.std() * (252 ** 0.5)

    # Avoid division by zero when downside volatility is zero.
    if downside_deviation == 0:
        return 0

    # Convert average daily portfolio returns into an annualized return.
    annual_return = portfolio_returns.mean() * 252

    # Sortino Ratio = Excess Annual Return / Downside Deviation.
    return (annual_return - risk_free_rate) / downside_deviation


def calculate_value_at_risk(prices, weights, confidence_level=0.95):
    """
    Calculate historical Value at Risk (VaR) using the
    lower percentile of daily portfolio returns.
    """

    portfolio_returns = calculate_portfolio_returns(prices, weights)

    # At 95% confidence, use the fifth percentile of daily returns.
    # Approximately 5% of historical returns fall below this threshold.
    return portfolio_returns.quantile(1 - confidence_level)


def calculate_risk_metrics(prices, start_date, end_date, weights):
    """
    Calculate and combine key portfolio performance and risk metrics,
    including annual return, volatility, Sharpe ratio, beta,
    maximum drawdown, Sortino ratio, and Value at Risk.
    """

    # Calculate weighted daily portfolio returns.
    portfolio_returns = calculate_portfolio_returns(prices, weights)

    # Annualize average daily returns using 252 trading days.
    annual_return = portfolio_returns.mean() * 252

    # Annualize daily volatility using the square root of 252.
    volatility = portfolio_returns.std() * (252 ** 0.5)

    # Assume a 2% annual risk-free rate.
    risk_free_rate = 0.02

    # Sharpe Ratio = (Annual Return - Risk-Free Rate) / Volatility.
    sharpe_ratio = (annual_return - risk_free_rate) / volatility

    # Measure portfolio sensitivity relative to the market benchmark.
    beta = calculate_beta(prices, start_date, end_date, weights)

    # Calculate the portfolio's largest historical decline.
    max_drawdown = calculate_max_drawdown(prices, weights)

    # Evaluate performance relative to downside volatility.
    sortino_ratio = calculate_sortino_ratio(prices, weights)

    # Estimate the historical daily loss threshold at 95% confidence.
    value_at_risk = calculate_value_at_risk(
        prices,
        weights
    )

    # Return all calculated metrics for use throughout the dashboard.
    return {
        "Annual Return": annual_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Beta": beta,
        "Max Drawdown": max_drawdown,
        "Sortino Ratio": sortino_ratio,
        "Value at Risk": value_at_risk
    }