import requests
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Database ID
notion_api_key = os.getenv('NOTION_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')


# Notion Headers
notion_headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_data(database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    response = requests.post(url, headers=notion_headers)
    return response.json()

if __name__ == '__main__':
    data = fetch_notion_data(notion_database_id)
    print(data)
