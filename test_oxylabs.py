# test_oxylabs.py

import os
import requests
from pprint import pprint
from dotenv import load_dotenv

# Load credentials from your .env file
load_dotenv()
OXY_USER = os.getenv("OXY_USER")
OXY_PASS = os.getenv("OXY_PASS")

# Check if credentials were loaded
if not OXY_USER or not OXY_PASS:
    raise ValueError("Oxylabs credentials not found in .env file.")

# Structure the payload for the API request
payload = {
    'source': 'universal',
    'url': 'https://sandbox.oxylabs.io/products', # Using the sandbox URL for a safe test
    'parse': True, # Ask Oxylabs to return structured JSON
    'render': 'html', # Enable JavaScript rendering for dynamic pages
}

# Define the API endpoint
api_url = 'https://realtime.oxylabs.io/v1/queries'

print(f"📡 Sending request to Oxylabs for URL: {payload['url']}")

try:
    # Make the POST request to the Oxylabs API
    response = requests.post(
        url=api_url,
        auth=(OXY_USER, OXY_PASS),
        json=payload,
        timeout=60 # Set a timeout for the request
    )

    # Raise an exception if the request was not successful (e.g., 401, 403, 500)
    response.raise_for_status()

    # Pretty-print the JSON response to the console
    print("✅ Request successful. API Response:")
    pprint(response.json())

except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred: {e}")
