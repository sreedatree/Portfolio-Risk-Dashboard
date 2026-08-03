def generate_executive_summary(
    metrics,
    health,
    best_stock,
    largest_sector,
    largest_holding
):
    """
    Generate a concise executive summary of the portfolio.
    """

    if metrics["Annual Return"] >= 0.12:
        performance = "strong"
    elif metrics["Annual Return"] >= 0.05:
        performance = "moderate"
    else:
        performance = "weak"

    summary = (
        f"Your portfolio has generated {performance} historical returns while "
        f"maintaining {health['risk'].lower()} risk. "
        f"It currently earns an overall health grade of "
        f"{health['grade']} ({health['score']}/100). "
        f"{largest_sector[0]} is your largest sector exposure, "
        f"and {largest_holding['Ticker']} is your largest holding."
    )

    return {
        "summary": summary,
        "performance": performance,
        "best_stock": best_stock["Ticker"],
        "best_return": best_stock["Total Return"],
        "largest_sector": largest_sector[0],
        "sector_weight": largest_sector[1],
    }