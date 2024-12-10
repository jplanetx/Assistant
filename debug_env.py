import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Print environment variables
print(f"NOTION_API_KEY: {os.getenv('NOTION_API_KEY')}")
print(f"NOTION_DATABASE_ID: {os.getenv('NOTION_DATABASE_ID')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")