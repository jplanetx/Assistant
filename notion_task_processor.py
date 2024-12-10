from dotenv import load_dotenv
import os
import openai
from notion_client import Client

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_API_KEY"))

def fetch_tasks(database_id):
    """Fetch tasks from the Notion database."""
    try:
        response = notion.databases.query(database_id=database_id)
        print("Tasks fetched successfully!")
        return response.get('results', [])
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

if __name__ == "__main__":
    # Replace 'your_database_id' with your actual Notion database ID
    database_id = os.getenv("NOTION_DATABASE_ID")
    tasks = fetch_tasks(database_id)
    print(f"Fetched {len(tasks)} tasks from the database.")
