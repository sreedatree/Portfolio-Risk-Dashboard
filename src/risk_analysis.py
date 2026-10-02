def generate_risk_analysis(metrics):
    """
    Generate plain-English interpretations of portfolio risk metrics.
    """

    analysis = []

    volatility = metrics["Volatility"]
    beta = metrics["Beta"]
    sharpe = metrics["Sharpe Ratio"]
    sortino = metrics["Sortino Ratio"]
    max_drawdown = metrics["Max Drawdown"]
    var = metrics["Value at Risk"]

    # Volatility
    if volatility < 0.15:
        volatility_text = "relatively low"
    elif volatility < 0.25:
        volatility_text = "moderate"
    else:
        volatility_text = "relatively high"

    analysis.append(
        f"**Volatility:** {volatility:.2%}. "
        f"Your portfolio has {volatility_text} historical volatility."
    )

    # Beta
    if beta < 0.8:
        beta_text = "less sensitive"
    elif beta <= 1.2:
        beta_text = "similarly sensitive"
    else:
        beta_text = "more sensitive"

    analysis.append(
        f"**Beta:** {beta:.2f}. "
        f"Your portfolio has historically been {beta_text} to overall market movements."
    )

    # Sharpe Ratio
    if sharpe >= 1:
        sharpe_text = "relatively strong"
    elif sharpe >= 0.5:
        sharpe_text = "moderate"
    else:
        sharpe_text = "relatively weak"

    analysis.append(
        f"**Sharpe Ratio:** {sharpe:.2f}. "
        f"Your risk-adjusted return has been {sharpe_text} based on this historical period."
    )

    # Sortino Ratio
    if sortino >= 1:
        sortino_text = "strong"
    elif sortino >= 0.5:
        sortino_text = "moderate"
    else:
        sortino_text = "weak"

    analysis.append(
        f"**Sortino Ratio:** {sortino:.2f}. "
        f"Your downside-risk-adjusted performance has been {sortino_text}."
    )

    # Maximum Drawdown
    analysis.append(
        f"**Maximum Drawdown:** {max_drawdown:.2%}. "
        "This represents the largest historical decline from a previous portfolio peak."
    )

    # Value at Risk
    analysis.append(
        f"**Value at Risk (95%):** {var:.2%}. "
        "Historically, approximately 95% of daily returns were better than this threshold."
    )

    return analysis