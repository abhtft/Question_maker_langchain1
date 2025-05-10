from openai import OpenAI
import os
import openai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Print the first few characters of the API key (for verification)
if api_key:
    print(f"API key loaded: {api_key[:5]}...")
else:
    print("No API key found!")

# Set up OpenAI client
client = openai.OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-4o",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
