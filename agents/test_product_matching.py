
from agents.sourcing_workflow import (
    find_product_matches,
    extract_supplier_model
)

supplier_data = {
    "products": [
        {
            "name": "JBL Tune 510BT Wireless Headphones",
            "price_amount": 1500,
            "currency": "INR",
            "min_order_quantity": 10,
            "url": "https://example.com/supplier",
            "supplier": {"name": "Demo Supplier"},
            "specifications": {
                "Product Specifications": {
                    "Model": "JBL Tune 510BT"
                }
            }
        },
        {
            "name": "boAt Rockerz 551 ANC",
            "price_amount": 1200,
            "currency": "INR",
            "min_order_quantity": 10,
            "url": "https://example.com/boat",
            "supplier": {"name": "Demo Boat Supplier"},
            "specifications": {
                "Product Specifications": {
                    "Model": "Rockerz 551 ANC"
                }
            }
        }
    ]
}

retail_data = {
    "offers": [
        {
            "title": "JBL Tune 510BT On Ear Wireless Headphones",
            "price": 2799,
            "currency": "INR",
            "store": "Demo Retail Store",
            "productUrl": "https://example.com/retail",
            "outOfStock": False
        },
        {
            "title": "boAt Rockerz Prime 415 Wireless Headphones",
            "price": 2099,
            "currency": "INR",
            "store": "Demo Retail Store",
            "productUrl": "https://example.com/boat-retail",
            "outOfStock": False
        }
    ]
}

matches = find_product_matches(supplier_data, retail_data)

print("Number of matches:", len(matches))

for match in matches:
    print(match)

test_supplier = {
    "name": "520BT Jbl Bluetooth Headphone",
    "specifications": {
        "Product Specifications": {
            "Color": "Black",
            "Warranty": "1 Year"
        }
    }
}

print(
    "Extracted supplier model:",
    extract_supplier_model(test_supplier)
)