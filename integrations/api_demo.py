
import requests

# External API endpoint
api_url = "https://jsonplaceholder.typicode.com/posts/1"

# Send an HTTP GET request
response = requests.get(api_url, timeout=15)

# Check whether the request was successful
if response.status_code == 200:

    print("API request successful!")

    # Convert JSON response into Python dictionary
    data = response.json()

    print("\nAPI Response:")
    print(data)

    print("\nIndividual fields:")

    print("User ID:", data["userId"])
    print("Post ID:", data["id"])
    print("Title:", data["title"])
    print("Body:", data["body"])

else:

    print("API request failed.")
    print("Status Code:", response.status_code)
