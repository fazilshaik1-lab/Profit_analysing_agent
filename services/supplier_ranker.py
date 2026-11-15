import re


def _to_number(value):
    """Convert numeric values or simple currency/quantity strings to float."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = str(value).replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None


def rank_suppliers(supplier_products):
    """
    Rank supplier listings by minimum procurement investment (unit price × MOQ).
    Listings with missing or invalid price/MOQ are excluded.
    """

    ranked_products = []

    for product in supplier_products:
        supplier = product.get("supplier") or {}

        price = _to_number(
            product.get("price_amount", product.get("price"))
        )
        moq = _to_number(product.get("min_order_quantity"))

        if price is None or moq is None or price <= 0 or moq <= 0:
            continue

        moq = int(moq)
        investment = price * moq

        ranked_products.append({
            "product": product.get("name") or product.get("title") or "Unnamed product",
            "supplier": supplier.get("name") or "Unknown Supplier",
            "location": supplier.get("city") or supplier.get("state") or "Unknown",
            "unit_price": price,
            "moq": moq,
            "investment": investment,
            "trust_stamp": bool(supplier.get("trust_stamp")),
            "supplier_url": supplier.get("url")
        })

    ranked_products.sort(
        key=lambda item: (item["investment"], item["unit_price"])
    )

    return ranked_products
