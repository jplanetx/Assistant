import requests
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Database ID
notion_api_key = os.getenv('NOTION_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')

# Notion Headers
notion_headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_data(database_id):
    """Fetch data from the Notion database."""
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    response = requests.post(url, headers=notion_headers)
    return response.json()

def query_gpt(prompt):
    """Send a prompt to OpenAI GPT and return the response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    # Fetch data from Notion
    data = fetch_notion_data(notion_database_id)

    # Extract tasks from the Notion database response
    tasks = []
    for result in data.get('results', []):
        try:
            task_name = result['properties']['Name']['title'][0]['text']['content']
            tasks.append(task_name)
        except (KeyError, IndexError):
            continue  # Skip tasks with missing or invalid data

    # Check if there are tasks
    if not tasks:
        print("No tasks found in the Notion database.")
    else:
        # Format tasks into a prompt for ChatGPT
        task_prompt = f"Here are my tasks: {tasks}. What should I prioritize and how can I organize my day?"

        # Query ChatGPT for recommendations
        recommendations = query_gpt(task_prompt)

        # Print the recommendations
        print("GPT Recommendations:")
        print(recommendations)
