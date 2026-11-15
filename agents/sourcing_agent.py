
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from integrations.tradeindia import search_tradeindia
from integrations.priceinindia import compare_retail_prices


# Load API key
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")


# --------------------------------------------------
# TOOL 1: SEARCH TRADEINDIA SUPPLIERS
# --------------------------------------------------

def find_tradeindia_suppliers(product_name: str) -> str:
    """Search TradeIndia for suppliers matching a product name."""

    result = search_tradeindia(product_name)

    if result is None:
        return json.dumps({"error": "Supplier search failed."})

    return json.dumps(result, ensure_ascii=False, default=str)


# --------------------------------------------------
# TOOL 2: COMPARE INDIAN RETAIL PRICES
# --------------------------------------------------

def compare_indian_retail_prices(
    product_name: str,
    brand: str = ""
) -> str:
    """Compare retail prices across Indian online stores."""

    result = compare_retail_prices(
        product_name,
        brand=brand or None
    )

    if result is None:
        return json.dumps({
            "error": "Retail price comparison failed."
        })

    return json.dumps(result, ensure_ascii=False, default=str)


# --------------------------------------------------
# TOOL 3: CALCULATE PRODUCT PROFITABILITY
# --------------------------------------------------

def calculate_product_profitability(
    supplier_price: float,
    retail_price: float,
    moq: int,
    shipping_cost: float = 50,
    marketplace_fee_percent: float = 10,
    other_costs: float = 20
) -> str:
    """Calculate product profit, margin, ROI and sourcing recommendation.
    All prices are in Indian Rupees.
    """

    from services.product_evaluator import evaluate_product

    if supplier_price <= 0 or retail_price <= 0 or moq <= 0:
        return json.dumps({
            "error": "Supplier price, retail price and MOQ must be positive."
        })

    if shipping_cost < 0 or other_costs < 0:
        return json.dumps({
            "error": "Shipping and other costs cannot be negative."
        })

    if not 0 <= marketplace_fee_percent <= 100:
        return json.dumps({
            "error": "Marketplace fee must be between 0 and 100."
        })

    marketplace_fee = retail_price * marketplace_fee_percent / 100

    gross_profit_per_unit = retail_price - supplier_price

    total_cost_per_unit = (
        supplier_price
        + shipping_cost
        + marketplace_fee
        + other_costs
    )

    net_profit_per_unit = retail_price - total_cost_per_unit

    procurement_investment = (
        supplier_price + shipping_cost
    ) * moq

    total_estimated_profit = net_profit_per_unit * moq

    profit_margin = (
        net_profit_per_unit / retail_price
    ) * 100

    roi = (
        total_estimated_profit / procurement_investment
    ) * 100 if procurement_investment > 0 else 0

    evaluation = evaluate_product(
        net_profit_per_unit,
        profit_margin,
        roi
    )

    result = {
        "currency": "INR",
        "supplier_price_per_unit": round(supplier_price, 2),
        "retail_price_per_unit": round(retail_price, 2),
        "moq": moq,
        "shipping_cost_per_unit": round(shipping_cost, 2),
        "marketplace_fee_percent": marketplace_fee_percent,
        "marketplace_fee_per_unit": round(marketplace_fee, 2),
        "other_costs_per_unit": round(other_costs, 2),
        "gross_profit_per_unit": round(gross_profit_per_unit, 2),
        "net_profit_per_unit": round(net_profit_per_unit, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "procurement_investment": round(procurement_investment, 2),
        "total_estimated_profit": round(total_estimated_profit, 2),
        "roi_percent": round(roi, 2),
        "decision": evaluation["decision"],
        "reason": evaluation["reason"]
    }

    return json.dumps(result, ensure_ascii=False)


# --------------------------------------------------
# TOOL 4: COMPLETE PRODUCT SOURCING WORKFLOW
# --------------------------------------------------

def analyze_product_sourcing(
    product_name: str,
    brand: str = ""
) -> str:
    """Run the complete product sourcing workflow.
    Search suppliers, compare retail offers, match product models,
    and calculate profitability only for matched products.
    """

    # Import inside the function to avoid circular imports.
    from agents.sourcing_workflow import run_sourcing_workflow

    try:
        result = run_sourcing_workflow(
            product_name=product_name,
            brand=brand
        )

        return json.dumps(
            result,
            ensure_ascii=False,
            default=str
        )

    except Exception as error:
        return json.dumps({
            "error": "Complete product sourcing workflow failed.",
            "details": str(error)
        })


# --------------------------------------------------
# GEMINI AI AGENT
# --------------------------------------------------

def ask_sourcing_agent(question: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            api_version="v1beta"
        )
    )

    try:
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",

            config=types.GenerateContentConfig(

                system_instruction="""
                You are a product sourcing and profitability AI
                assistant for the Indian market.

                You have four tools:

                1. find_tradeindia_suppliers:
                   Search TradeIndia supplier listings.

                2. compare_indian_retail_prices:
                   Compare retail prices across Indian stores.

                3. calculate_product_profitability:
                   Calculate profitability using supplied prices.

                4. analyze_product_sourcing:
                   Run the complete sourcing workflow:
                   supplier search, retail comparison,
                   product matching and profitability calculation.

                IMPORTANT INSTRUCTIONS:

                - When a user requests a complete product sourcing
                  or profitability analysis, use
                  analyze_product_sourcing.

                - Do not separately search suppliers and retail
                  prices if the complete workflow is requested.

                - Only calculate profitability for products
                  returned as matches by the workflow.

                - Never assume two products are identical merely
                  because they belong to the same category.

                - Do not invent product models, supplier prices,
                  retail prices, MOQs or supplier details.

                - If no reliable product matches are found,
                  clearly explain that profitability could not
                  be calculated.

                - Explain the assumptions used in calculations,
                  including shipping, marketplace fees and
                  additional costs.

                - Treat profitability recommendations as
                  estimates, not guaranteed business outcomes.

                - Explain findings in simple language suitable
                  for an Indian product sourcing business.
                """,

                tools=[
                    find_tradeindia_suppliers,
                    compare_indian_retail_prices,
                    calculate_product_profitability,
                    analyze_product_sourcing
                ],

                temperature=0.2
            )
        )

        response = chat.send_message(question)

        return response.text or (
            "Gemini did not return a text response."
        )

    finally:
        client.close()
