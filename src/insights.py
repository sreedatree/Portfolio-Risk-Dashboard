def generate_insights(metrics, sector_allocation):
    insights = []

    # Annual Return
    if metrics["Annual Return"] > 0.15:
        insights.append(
            f"📈 Annual return was {metrics['Annual Return']:.2%}, indicating strong historical performance."
        )
    else:
        insights.append(
            f"📈 Annual return was {metrics['Annual Return']:.2%}."
        )

    # Beta
    if metrics["Beta"] > 1:
        insights.append(
            f"⚠️ Beta of {metrics['Beta']:.2f} suggests the portfolio is more volatile than the overall market."
        )
    else:
        insights.append(
            f"✅ Beta of {metrics['Beta']:.2f} suggests the portfolio is less volatile than the market."
        )

    # Drawdown
    insights.append(
        f"📉 Maximum drawdown was {metrics['Max Drawdown']:.2%}."
    )

    # Largest sector
    largest_sector = max(
        sector_allocation,
        key=sector_allocation.get
    )

    largest_weight = sector_allocation[largest_sector]

    insights.append(
        f"💼 {largest_sector} represents {largest_weight:.1%} of the portfolio."
    )

    return insights