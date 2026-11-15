
import asyncio
from mcp import Client

MCP_URL = "https://mcp.priceinindia.website/mcp"


async def _compare_prices(product_name, brand=None):

    async with Client(MCP_URL) as client:

        arguments = {
            "query": product_name
        }

        if brand:
            arguments["brand"] = brand

        result = await client.call_tool(
            "compare_prices",
            arguments
        )

        return getattr(result, "structured_content", None)


def compare_retail_prices(product_name, brand=None):
    """
    Search PriceInIndia and return retail price comparisons.
    """

    try:
        return asyncio.run(
            _compare_prices(product_name, brand)
        )

    except Exception as error:
        print("PriceInIndia error:", error)
        return None
