
from agents.sourcing_agent import ask_sourcing_agent

question = """
Use the calculate_product_profitability function to calculate
the profitability of this product.

Supplier price per unit: ₹1,000
Retail selling price per unit: ₹1,500
Minimum order quantity: 10
Shipping cost per unit: ₹50
Marketplace fee: 10%
Other costs per unit: ₹20

Use the function to calculate the results.
Do not calculate the values yourself.

Explain:
1. Gross profit per unit
2. Net profit per unit
3. Profit margin
4. Total procurement investment
5. Total estimated profit for the MOQ
6. ROI
7. Final sourcing recommendation

Use the exact results returned by the function.
"""

answer = ask_sourcing_agent(question)

print("\n===== AI PROFITABILITY ANALYSIS =====\n")
print(answer)
