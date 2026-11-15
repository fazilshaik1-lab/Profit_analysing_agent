
from agents.sourcing_agent import ask_sourcing_agent

question = (
    "Analyse wireless headphones for product sourcing "
    "in India. Search suppliers, compare retail prices, "
    "match the same product models, and calculate "
    "profitability only for reliable matches. "
    "Explain the results and assumptions."
)

response = ask_sourcing_agent(question)

print("\n===== GEMINI SOURCING AGENT RESPONSE =====\n")
print(response)
