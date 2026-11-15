
import streamlit as st

# Import our live TradeIndia search function
from integrations.tradeindia import search_tradeindia
from integrations.priceinindia import compare_retail_prices

# --------------------------------
# SESSION STATE
# --------------------------------

if "supplier_results" not in st.session_state:
    st.session_state.supplier_results = []

if "retail_results" not in st.session_state:
    st.session_state.retail_results = {}

if "selected_supplier" not in st.session_state:
    st.session_state.selected_supplier = None

if "selected_retail_offer" not in st.session_state:
    st.session_state.selected_retail_offer = None


# --------------------------------
# APPLICATION CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Product Sourcing AI Agent",
    page_icon="📦",
    layout="wide"
)


# --------------------------------
# HELPER FUNCTION
# --------------------------------

def extract_products(data):
    """
    Find the product listings inside the API response.
    The API response may contain nested dictionaries.
    """

    if isinstance(data, list):
        if data and all(
            isinstance(item, dict)
            and "supplier" in item
            and ("name" in item or "title" in item)
            for item in data
        ):
            return data

        for item in data:
            result = extract_products(item)
            if result:
                return result

    elif isinstance(data, dict):
        for value in data.values():
            result = extract_products(value)
            if result:
                return result

    return []


# --------------------------------
# APPLICATION HEADER
# --------------------------------

st.title("Product Sourcing & Profitability AI Agent")

st.write(
    "Find products from suppliers, compare them "
    "with retail prices, and analyze profitability."
)

st.divider()


# --------------------------------
# TRADEINDIA PRODUCT SEARCH
# --------------------------------

st.subheader("TradeIndia Supplier Research")

product_name = st.text_input(
    "Enter product name",
    placeholder="Example: Wireless Bluetooth Headphones"
)



if st.button("Search TradeIndia Suppliers"):

    if product_name.strip():

        with st.spinner("Searching TradeIndia suppliers..."):

            api_response = search_tradeindia(product_name)

        if api_response:
            supplier_results = extract_products(api_response)

            if supplier_results:
                st.session_state.supplier_results = supplier_results
                st.session_state.selected_supplier = None

                st.success(
                    f"Found {len(supplier_results)} supplier products!"
                )
            else:
                st.session_state.supplier_results = []
                st.warning("No supplier products were found.")

        else:
            st.session_state.supplier_results = []
            st.error(
                "Unable to retrieve TradeIndia results. "
                "Check the Terminal for API errors."
            )

    else:
        st.warning("Please enter a product name.")


# Display stored supplier results

supplier_results = st.session_state.supplier_results

if supplier_results:

    st.subheader("Available Supplier Products")

    supplier_options = list(range(len(supplier_results)))

    selected_supplier_index = st.selectbox(
        "Select a supplier product",
        options=supplier_options,
        format_func=lambda i: (
            f"{supplier_results[i].get('name') or supplier_results[i].get('title', 'Unnamed Product')} "
            f"| {supplier_results[i].get('supplier', {}).get('name', 'Unknown Supplier')}"
        ),
        key="supplier_selection"
    )

    st.session_state.selected_supplier = supplier_results[
        selected_supplier_index
    ]

    # Display selected supplier product

    product = st.session_state.selected_supplier
    supplier = product.get("supplier") or {}

    st.divider()

    st.subheader(
        product.get("name")
        or product.get("title")
        or "Unnamed Product"
    )

    image_url = product.get("image")

    if image_url:
        st.image(image_url, width=180)

    st.write(
        product.get("description")
        or "No description available."
    )

    st.write(
        f"**Supplier:** {supplier.get('name', 'Not available')}"
    )

    st.write(
        f"**Location:** "
        f"{supplier.get('city', 'Not available')}, "
        f"{supplier.get('state', '')}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        price = product.get("price_amount")
        currency = product.get("currency") or "INR"

        st.metric(
            "Unit Price",
            f"{currency} {price:,.2f}"
            if price is not None
            else "Not available"
        )

    with col2:
        moq = product.get("min_order_quantity")

        st.metric(
            "Minimum Order Quantity",
            moq if moq is not None else "Not available"
        )

    with col3:
        trust_stamp = supplier.get("trust_stamp")

        st.metric(
            "TradeIndia Trust Stamp",
            "Yes" if trust_stamp else "No"
        )

    if price is not None and moq is not None:
        st.info(
            f"Estimated minimum product purchase: "
            f"{currency} {price * moq:,.2f}"
        )

    availability = product.get("in_stock")

    if availability is True:
        st.success("Product availability: In Stock")
    elif availability is False:
        st.warning("Product availability: Out of Stock")
    else:
        st.info("Product availability: Not specified")

    product_url = product.get("url")
    supplier_url = supplier.get("url")

    if product_url:
        st.markdown(
            f"[View Product on TradeIndia]({product_url})"
        )

    if supplier_url:
        st.markdown(
            f"[View Supplier Profile]({supplier_url})"
        )


# --------------------------------
# PRICEINDIA RETAIL PRICE COMPARISON
# --------------------------------

st.divider()

st.subheader("Retail Price Comparison")

retail_product = st.text_input(
    "Enter product to compare retail prices",
    placeholder="Example: boAt Rockerz 550",
    key="retail_product"
)

retail_brand = st.text_input(
    "Brand (optional)",
    placeholder="Example: boat",
    key="retail_brand"
)


if st.button("Compare Retail Prices"):

    if retail_product.strip():

        with st.spinner("Comparing retail prices across stores..."):

            retail_results = compare_retail_prices(
                retail_product,
                retail_brand.strip() or None
            )

        if retail_results:
            st.session_state.retail_results = retail_results
            st.session_state.selected_retail_offer = None

            st.success(
                f"Found {len(retail_results.get('offers', []))} retail offers!"
            )

        else:
            st.session_state.retail_results = {}
            st.error("Unable to retrieve retail prices.")

    else:
        st.warning("Please enter a product name.")


# Display stored retail offers

retail_results = st.session_state.retail_results

if retail_results:

    offers = retail_results.get("offers", [])
    best_price = retail_results.get("bestPrice")

    if offers:

        st.subheader("Available Retail Offers")

        if best_price is not None:
            st.metric(
                "Lowest Retail Price",
                f"₹{best_price:,.2f}"
            )

        retail_options = list(range(len(offers)))

        selected_retail_index = st.selectbox(
            "Select a retail product",
            options=retail_options,
            format_func=lambda i: (
                f"{offers[i].get('title', 'Unnamed Product')} "
                f"| {offers[i].get('store', 'Unknown Retailer')} "
                f"| ₹{offers[i].get('price', 0):,.2f}"
            ),
            key="retail_selection"
        )

        selected_offer = offers[selected_retail_index]

        st.session_state.selected_retail_offer = selected_offer

        st.divider()

        st.write(
            f"**Product:** {selected_offer.get('title', 'Not available')}"
        )

        st.metric(
            "Retail Price",
            f"₹{selected_offer.get('price', 0):,.2f}"
        )

        st.write(
            f"**Retailer:** {selected_offer.get('store', 'Not available')}"
        )

        if selected_offer.get("outOfStock"):
            st.warning("This retail listing is out of stock.")
        else:
            st.success("Listed as in stock.")

        if selected_offer.get("productUrl"):
            st.markdown(
                f"[View Retail Product]({selected_offer['productUrl']})"
            )

    else:
        st.warning("No retail offers were found.")


# --------------------------------
# LOAD SELECTED PRODUCTS INTO CALCULATOR
# --------------------------------

st.divider()

st.subheader("Automate Profitability Inputs")

st.write(
    "Load the selected TradeIndia supplier price, "
    "MOQ and PriceInIndia retail price into the calculator."
)


if st.button("Load Selected Prices into Calculator"):

    supplier = st.session_state.selected_supplier
    retail = st.session_state.selected_retail_offer

    if supplier is None:
        st.warning("Please select a TradeIndia supplier product.")

    elif retail is None:
        st.warning("Please select a retail product.")

    elif retail.get("outOfStock"):
        st.warning(
            "The selected retail product is out of stock. "
            "Please select an available listing."
        )

    else:
        supplier_price = supplier.get("price_amount")
        supplier_moq = supplier.get("min_order_quantity")
        retail_price = retail.get("price")

        try:
            supplier_price = float(supplier_price)
            retail_price = float(retail_price)
            supplier_moq = int(supplier_moq)

            if supplier_price <= 0 or retail_price <= 0 or supplier_moq <= 0:
                raise ValueError("Prices and MOQ must be positive.")

            st.session_state.supplier_price_input = supplier_price
            st.session_state.retail_price_input = retail_price
            st.session_state.moq_input = supplier_moq

            st.session_state["supplier_price_widget"] = supplier_price
            st.session_state["retail_price_widget"] = retail_price
            st.session_state["moq_widget"] = supplier_moq

            st.success(
                "Supplier price, retail price and MOQ loaded successfully!"
            )

        except (TypeError, ValueError):
            st.error(
                "Unable to load the selected values. "
                "The supplier price, retail price or MOQ may be missing "
                "or in an unsupported format."
            )

# --------------------------------
# PROFITABILITY CALCULATOR
# --------------------------------

st.divider()

st.header("Product Profitability Calculator")

st.write(
    "Estimate your profit after supplier costs, shipping, "
    "marketplace fees and other expenses."
)

st.subheader("1. Product and supplier details")

col1, col2 = st.columns(2)

with col1:
    supplier_price = st.number_input(
    "Supplier price per unit (₹)",
    min_value=0.0,
    value=1000.0,
    step=50.0,
    key="supplier_price_widget"
)
    
with col2:
    retail_price = st.number_input(
    "Retail selling price per unit (₹)",
    min_value=0.0,
    value=1500.0,
    step=50.0,
    key="retail_price_widget"
)

moq = st.number_input(
    "Minimum Order Quantity (MOQ)",
    min_value=1,
    value=10,
    step=1,
    key="moq_widget"
)

st.subheader("2. Additional business expenses")

col1, col2, col3 = st.columns(3)

with col1:
    shipping_cost = st.number_input(
        "Shipping cost per unit (₹)",
        min_value=0.0,
        value=50.0,
        step=10.0
    )

with col2:
    marketplace_fee_percent = st.number_input(
        "Marketplace fee (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0
    )

with col3:
    other_costs = st.number_input(
        "Other costs per unit (₹)",
        min_value=0.0,
        value=20.0,
        step=10.0
    )

st.divider()

# --------------------------------
# PROFIT CALCULATIONS
# --------------------------------

marketplace_fee = (
    retail_price * marketplace_fee_percent / 100
)

gross_profit_per_unit = (
    retail_price - supplier_price
)

total_cost_per_unit = (
    supplier_price
    + shipping_cost
    + marketplace_fee
    + other_costs
)

net_profit_per_unit = (
    retail_price - total_cost_per_unit
)

procurement_investment = (
    supplier_price + shipping_cost
) * moq

total_estimated_profit = (
    net_profit_per_unit * moq
)

profit_margin = (
    (net_profit_per_unit / retail_price) * 100
    if retail_price > 0
    else 0
)

roi = (
    (total_estimated_profit / procurement_investment) * 100
    if procurement_investment > 0
    else 0
)

from services.product_evaluator import evaluate_product

evaluation = evaluate_product(
    net_profit_per_unit,
    profit_margin,
    roi
)

decision = evaluation["decision"]
reason = evaluation["reason"]

# --------------------------------
# DISPLAY RESULTS
# --------------------------------

st.header("3. Profitability Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Gross Profit Per Unit",
        f"₹{gross_profit_per_unit:,.2f}"
    )

with col2:
    st.metric(
        "Estimated Net Profit Per Unit",
        f"₹{net_profit_per_unit:,.2f}",
        delta=(
            "Profitable"
            if net_profit_per_unit > 0
            else "Loss"
        )
    )

with col3:
    st.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%"
    )

st.subheader("Investment and order analysis")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Minimum Procurement Investment",
        f"₹{procurement_investment:,.2f}"
    )

with col2:
    st.metric(
        "Estimated ROI",
        f"{roi:.2f}%"
    )

st.metric(
    "Estimated Total Profit for MOQ",
    f"₹{total_estimated_profit:,.2f}"
)

if net_profit_per_unit > 0:
    st.success(
        "This product shows an estimated profit "
        "based on the entered costs."
    )

elif net_profit_per_unit < 0:
    st.error(
        "This product shows an estimated loss. "
        "Review the supplier price and additional expenses."
    )

else:
    st.warning(
        "This product breaks even based on the entered costs."
    )

st.caption(
    "Assumptions: All MOQ units are sold at the entered retail price. "
    "Marketplace fees are calculated as a percentage of selling price. "
    "Taxes, returns, storage, advertising and other unentered expenses "
    "are excluded. ROI is calculated against supplier purchase price "
    "plus inbound shipping."
)

# --------------------------------
# SYSTEM STATUS
# --------------------------------

st.divider()

st.subheader("System Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "TradeIndia Integration",
        "Connected (Live API)"
    )

with col2:
    st.metric(
        "PriceInIndia Integration",
        "Connected (Tested)"
    )

with col3:
    st.metric(
        "AI Agent",
        "Connected (Gemini 2.5 Flash)"
    )
# --------------------------------
# FINAL PRODUCT SOURCING SUMMARY
# --------------------------------

st.divider()

st.header("Final Product Sourcing Summary")

selected_supplier = st.session_state.selected_supplier
selected_retail = st.session_state.selected_retail_offer

if selected_supplier and selected_retail:

    supplier_details = selected_supplier.get("supplier") or {}

    st.subheader(
        selected_supplier.get("name")
        or selected_supplier.get("title")
        or "Selected Product"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Supplier",
            supplier_details.get("name", "Unknown")
        )

    with col2:
        st.metric(
            "Retailer",
            selected_retail.get("store", "Unknown")
        )

    with col3:
        st.metric(
            "Minimum Order Quantity",
            moq
        )

    st.divider()

    st.subheader("Commercial Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Supplier Price",
            f"₹{supplier_price:,.2f}"
        )

    with col2:
        st.metric(
            "Retail Price",
            f"₹{retail_price:,.2f}"
        )

    with col3:
        st.metric(
            "Procurement Investment",
            f"₹{procurement_investment:,.2f}"
        )

    st.subheader("Financial Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Net Profit Per Unit",
            f"₹{net_profit_per_unit:,.2f}"
        )

    with col2:
        st.metric(
            "Profit Margin",
            f"{profit_margin:.2f}%"
        )

    with col3:
        st.metric(
            "ROI",
            f"{roi:.2f}%"
        )

    st.divider()

    st.subheader("Final Sourcing Decision")

    if decision == "Recommended":
        st.success(f"Recommended: {reason}")

    elif decision == "Not Recommended":
        st.error(f"Not Recommended: {reason}")

    else:
        st.warning(f"{decision}: {reason}")

else:
    st.info(
        "Select a supplier product and retail offer, "
        "then load their prices into the calculator "
        "to generate the sourcing summary."
    )


# ==========================================
# GEMINI AI AGENT CHAT INTERFACE
# ==========================================

st.divider()

st.header("Ask the Product Sourcing AI Agent")

st.caption(
    "Ask questions about suppliers, retail prices, "
    "and product sourcing opportunities."
)

# Initialize chat history
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# Display previous messages
for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new question
if prompt := st.chat_input("Ask about a product or sourcing opportunity..."):

    st.session_state.agent_messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gemini is analysing your request..."):

            try:
                from agents.sourcing_agent import ask_sourcing_agent

                answer = ask_sourcing_agent(prompt)

                st.markdown(answer)

                st.session_state.agent_messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"Agent error: {error}")
