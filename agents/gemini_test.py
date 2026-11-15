
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load the .env file from the project root
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the .env file.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain what a product sourcing AI agent does in two sentences."
)

print(response.text)

client.close()
