
import json
import re

from agents.sourcing_agent import (
    find_tradeindia_suppliers,
    compare_indian_retail_prices,
    calculate_product_profitability
)


# --------------------------------------------------
# 1. TEXT AND DATA HELPERS
# --------------------------------------------------

def normalize_text(value):
    """Normalize text for consistent product comparison."""

    if not value:
        return ""

    value = str(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def extract_list(data, possible_keys):
    """
    Find a list of products or offers inside an API response.

    Supports common nested API response structures.
    """

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in possible_keys:
        value = data.get(key)

        if isinstance(value, list):
            return value

    # Check nested response objects
    for value in data.values():
        if isinstance(value, dict):
            result = extract_list(value, possible_keys)

            if result:
                return result

    return []




def extract_supplier_model(supplier):
    """
    Extract a model identifier from supplier specifications.
    If unavailable, extract it from the product title.
    """

    specifications = supplier.get("specifications") or {}

    if isinstance(specifications, dict):
        product_specs = specifications.get(
            "Product Specifications", {}
        )

        if isinstance(product_specs, dict):
            model = product_specs.get("Model")

            if model:
                return normalize_text(model)

    product_name = (
        supplier.get("name")
        or supplier.get("title")
        or ""
    )

    return normalize_text(product_name)


def extract_model_identifier(value):
    """
    Extract recognizable model identifiers from product text.

    Examples:
    JBL Tune 510BT -> tune 510bt
    JBL 520BT -> 520bt
    boAt Rockerz 551 ANC -> rockerz 551
    """

    text = normalize_text(value)

    patterns = [
        r"\b(tune\s*\d+[a-z0-9]*)\b",
        r"\b(rockerz\s*\d+[a-z0-9]*)\b",
        r"\b(\d+[a-z]+\d*)\b",
        r"\b([a-z]+\d+[a-z0-9]*)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return normalize_text(match.group(1))

    return ""




def is_valid_positive_number(value):
    """Check whether a value is a valid positive number."""

    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


# --------------------------------------------------
# 2. PRODUCT MATCHING
# --------------------------------------------------


def find_product_matches(supplier_data, retail_data):
    """
    Match supplier and retail listings using model identifiers.

    Rejects listings when model identifiers are missing
    or do not agree.
    """

    suppliers = extract_list(
        supplier_data,
        ["products", "items", "results"]
    )

    offers = extract_list(
        retail_data,
        ["offers", "products", "items", "results"]
    )

    matches = []

    for supplier in suppliers:

        if not isinstance(supplier, dict):
            continue

        supplier_name = (
            supplier.get("name")
            or supplier.get("title")
            or ""
        )

        supplier_model = extract_supplier_model(supplier)

        supplier_identifier = extract_model_identifier(
            supplier_model
        )

        supplier_price = supplier.get("price_amount")
        moq = supplier.get("min_order_quantity")

        if not supplier_identifier:
            continue

        if not is_valid_positive_number(supplier_price):
            continue

        if not is_valid_positive_number(moq):
            continue

        if str(supplier.get("currency") or "").upper() != "INR":
            continue

        if supplier.get("in_stock") is False:
            continue

        supplier_brand = normalize_text(
            (supplier.get("specifications") or {})
            .get("TI SHOPPING", {})
            .get("Brand Name", "")
        )

        for offer in offers:

            if not isinstance(offer, dict):
                continue

            if offer.get("outOfStock", False):
                continue

            retail_title = offer.get("title", "")
            retail_price = offer.get("price")

            if not is_valid_positive_number(retail_price):
                continue

            if str(offer.get("currency") or "").upper() != "INR":
                continue

            retail_identifier = extract_model_identifier(
                retail_title
            )

            if not retail_identifier:
                continue

            # Model identifiers must agree exactly.
            if supplier_identifier != retail_identifier:
                continue

            retail_brand = normalize_text(
                offer.get("brand", "")
            )

            # Reject conflicting brand information.
            if supplier_brand and retail_brand:
                if supplier_brand != retail_brand:
                    continue

            supplier_details = supplier.get("supplier") or {}

            matches.append({
                "supplier_product": supplier_name,
                "supplier_model": supplier_identifier,
                "supplier_name": supplier_details.get("name"),
                "supplier_price": float(supplier_price),
                "moq": int(float(moq)),
                "retail_product": retail_title,
                "retail_model": retail_identifier,
                "retail_price": float(retail_price),
                "retail_store": offer.get("store"),
                "supplier_url": supplier.get("url"),
                "retail_url": offer.get("productUrl"),
                "match_type": "Model identifier match",
                "match_status": (
                    "Preliminary match - verify exact specifications"
                )
            })

    return matches



# --------------------------------------------------
# 3. PROFITABILITY CALCULATION
# --------------------------------------------------

def calculate_matched_profitability(matches):
    """
    Calculate profitability using validated listing prices
    and MOQ from each preliminary product match.
    """

    results = []

    for match in matches:

        calculation_response = calculate_product_profitability(
            supplier_price=match["supplier_price"],
            retail_price=match["retail_price"],
            moq=match["moq"]
        )

        try:
            calculation = json.loads(calculation_response)

        except (TypeError, json.JSONDecodeError):
            calculation = {
                "error": "Invalid profitability calculation response"
            }

        results.append({
            "product": match["supplier_product"],
            "supplier": match["supplier_name"],
            "retail_product": match["retail_product"],
            "retail_store": match["retail_store"],
            "supplier_price": match["supplier_price"],
            "retail_price": match["retail_price"],
            "moq": match["moq"],
            "match_status": match["match_status"],
            "supplier_url": match["supplier_url"],
            "retail_url": match["retail_url"],
            "profitability": calculation
        })

    return results


# --------------------------------------------------
# 4. MAIN SOURCING WORKFLOW
# --------------------------------------------------

def run_sourcing_workflow(product_name: str, brand: str = ""):
    """
    Complete product sourcing workflow:

    1. Search TradeIndia suppliers.
    2. Compare Indian retail prices.
    3. Match products using model identifiers.
    4. Calculate profitability for preliminary matches.
    5. Return a consolidated report.
    """

    if not product_name or not product_name.strip():
        return {
            "error": "Please provide a product name."
        }

    # Step 1: Supplier search
    try:
        supplier_response = find_tradeindia_suppliers(
            product_name
        )

        supplier_data = json.loads(supplier_response)

    except Exception as error:
        return {
            "error": "TradeIndia supplier search failed.",
            "details": str(error)
        }

    # Step 2: Retail price comparison
    try:
        retail_response = compare_indian_retail_prices(
            product_name,
            brand
        )

        retail_data = json.loads(retail_response)

    except Exception as error:
        return {
            "error": "Retail price comparison failed.",
            "details": str(error)
        }

    # Step 3: Extract listings
    suppliers = extract_list(
        supplier_data,
        ["products", "items", "results"]
    )

    offers = extract_list(
        retail_data,
        ["offers", "products", "items", "results"]
    )
    


    # Step 4: Match products
    matches = find_product_matches(
        supplier_data,
        retail_data
    )

    # Step 5: Calculate profitability
    profitability_results = calculate_matched_profitability(
        matches
    )

    # Step 6: Build final result
    if profitability_results:
        status = (
            "Profitability calculated for preliminary model matches. "
            "Verify product specifications and commercial terms."
        )

    else:
        status = (
            "No reliable model matches found. "
            "Profitability calculation skipped."
        )

    return {
        "product_searched": product_name,
        "brand": brand,
        "supplier_listings_found": len(suppliers),
        "retail_offers_found": len(offers),
        "number_of_matches": len(matches),
        "matches": matches,
        "profitability_results": profitability_results,
        "profitability_status": status,
        "calculation_assumptions": {
            "shipping_cost_per_unit": 50,
            "marketplace_fee_percent": 10,
            "other_costs_per_unit": 20,
            "currency": "INR"
        }
    }


# --------------------------------------------------
# 5. RUN DIRECTLY FROM TERMINAL
# --------------------------------------------------

if __name__ == "__main__":

    result = run_sourcing_workflow(
        product_name="wireless headphones"
    )

    print("\n===== PRODUCT SOURCING WORKFLOW =====\n")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
