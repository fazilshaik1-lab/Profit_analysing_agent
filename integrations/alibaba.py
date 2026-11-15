
# Import sample supplier data
from data.mock_products import alibaba_products


def search_alibaba(product_name):
    """
    Search supplier products using sample Alibaba data.

    Args:
        product_name: Product name entered by the user.

    Returns:
        List of matching supplier products.
    """

    matching_products = []

    # Convert search input to lowercase
    search_term = product_name.lower()

    # Iterate through supplier products
    for product in alibaba_products:

        supplier_product_name = product["product_name"].lower()

        # Check whether search term exists in product name
        if search_term in supplier_product_name:

            matching_products.append(product)

    return matching_products
