
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Locate the .env file in the main project folder
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")


def search_tradeindia(product_name):
    """Search TradeIndia through the API.SH service."""

    api_key = os.getenv("APISH_KEY")

    if not api_key:
        raise ValueError("APISH_KEY is missing from the .env file.")

    api_url = "https://api.api.sh/tradeindia/v1/search"

    headers = {
        "x-api-key": api_key
    }

    params = {
        "q": product_name
    }

    try:
        response = requests.get(
            api_url,
            headers=headers,
            params=params,
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        print("TradeIndia API request failed:", error)

        if error.response is not None:
            print("API response:", error.response.text)

        return None


if __name__ == "__main__":
    results = search_tradeindia("wireless headphones")

    if results:
        import json
        print(json.dumps(results, indent=4, ensure_ascii=False))
