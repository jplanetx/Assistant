import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Ensure you're specifying the correct model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"},
        ],
    )
    print(response["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Error during ChatCompletion: {e}")
