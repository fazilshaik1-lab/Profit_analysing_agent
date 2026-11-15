
import requests
import os

from dotenv import load_dotenv


# Load credentials from the .env file
load_dotenv()


# Retrieve the API key
api_key = os.getenv("DEMO_API_KEY")


# Check whether the key exists
if not api_key:

    print("API key not found!")

else:

    print("API key loaded successfully.")

    # HTTP request headers
    headers = {
        "X-API-Key": api_key
    }

    # API query parameters
    params = {
        "keyword": "wireless headphones",
        "country": "India",
        "page": 1
    }

    # Testing API endpoint
    api_url = "https://httpbin.org/anything"

    # Send the GET request
    response = requests.get(
        api_url,
        headers=headers,
        params=params,
        timeout=20
    )

    # Process the response
    if response.status_code == 200:

        print("\nAPI request successful!")

        data = response.json()

        print("\nRequest URL:")
        print(data["url"])

        print("\nRequest Headers:")
        print(data["headers"])

        print("\nQuery Parameters:")
        print(data["args"])

    else:

        print("API request failed.")
        print("Status Code:", response.status_code)
