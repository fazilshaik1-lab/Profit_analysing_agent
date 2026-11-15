
import json

from agents.sourcing_workflow import (
    calculate_matched_profitability
)

# Mock matched product
matches = [
    {
        "supplier_product": "JBL Tune 510BT Wireless Headphones",
        "supplier_name": "Demo Supplier",
        "supplier_price": 1500,
        "moq": 10,
        "retail_product": "JBL Tune 510BT On Ear Wireless Headphones",
        "retail_price": 2799,
        "retail_store": "Demo Retail Store",
        "supplier_url": "https://example.com/supplier",
        "retail_url": "https://example.com/retail",
        "match_type": "Model match",
        "match_status": "Preliminary match"
    }
]

results = calculate_matched_profitability(matches)

print("\n===== PROFITABILITY TEST =====\n")

print(
    json.dumps(
        results,
        indent=4,
        ensure_ascii=False
    )
)
