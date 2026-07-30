def calculate_health_score(metrics, sector_allocation, weights):
    """
    Calculate an overall portfolio health score out of 100.
    """

    score = 0
    insights = []

    # -----------------------------
    # Diversification
    # -----------------------------
    holdings = len(weights)

    if holdings >= 8:
        score += 20
        insights.append("✅ Excellent diversification.")
    elif holdings >= 5:
        score += 15
        insights.append("🟢 Good diversification.")
    elif holdings >= 3:
        score += 10
        insights.append("🟡 Moderate diversification.")
    else:
        score += 5
        insights.append("🔴 Portfolio is highly concentrated.")

    # -----------------------------
    # Concentration Risk
    # -----------------------------
    largest_weight = max(weights)

    if largest_weight <= 0.20:
        score += 20
        insights.append("✅ Holdings are well balanced.")
    elif largest_weight <= 0.30:
        score += 15
        insights.append("🟢 Slight concentration risk.")
    elif largest_weight <= 0.40:
        score += 10
        insights.append("🟡 One holding dominates the portfolio.")
    else:
        score += 5
        insights.append("🔴 High concentration risk.")

    # -----------------------------
    # Sector Diversification
    # -----------------------------
    largest_sector = max(sector_allocation.values())

    if largest_sector <= 0.35:
        score += 20
        insights.append("✅ Excellent sector balance.")
    elif largest_sector <= 0.50:
        score += 15
        insights.append("🟢 Good sector diversification.")
    elif largest_sector <= 0.65:
        score += 10
        insights.append("🟡 Heavy exposure to one sector.")
    else:
        score += 5
        insights.append("🔴 Sector concentration is high.")

    # -----------------------------
    # Volatility
    # -----------------------------
    vol = metrics["Volatility"]

    if vol < 0.15:
        score += 20
    elif vol < 0.25:
        score += 15
    elif vol < 0.35:
        score += 10
    else:
        score += 5

    # -----------------------------
    # Beta
    # -----------------------------
    beta = metrics["Beta"]

    if 0.9 <= beta <= 1.1:
        score += 20
    elif 0.75 <= beta <= 1.25:
        score += 15
    elif 0.5 <= beta <= 1.5:
        score += 10
    else:
        score += 5

    return score, insights