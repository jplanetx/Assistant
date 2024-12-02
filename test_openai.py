import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def test_openai_api():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, OpenAI!"}
            ]
        )
        print("API Response:", response['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_openai_api()
