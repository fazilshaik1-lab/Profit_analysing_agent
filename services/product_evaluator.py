def evaluate_product(net_profit, profit_margin, roi):
    """
    Apply simple demo thresholds to the calculated product economics.
    These are configurable business assumptions, not marketplace rules.
    """

    if net_profit <= 0:
        return {
            "decision": "Not Recommended",
            "reason": "The product is currently loss-making."
        }

    if profit_margin < 10:
        return {
            "decision": "Low Profitability",
            "reason": "The profit margin is below the demo threshold of 10%."
        }

    if roi < 20:
        return {
            "decision": "Consider Carefully",
            "reason": "The ROI is below the demo threshold of 20%."
        }

    return {
        "decision": "Recommended",
        "reason": "The product meets the demo profitability thresholds."
    }
