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

def query_gpt(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    # Fetch data from Notion
    data = fetch_notion_data(notion_database_id)

    # Extract tasks from the Notion database response
    tasks = []
    for result in data.get('results', []):
        task_name = result['properties']['Name']['title'][0]['text']['content']
        tasks.append(task_name)

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
