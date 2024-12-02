from notion_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

def test_notion_connection():
    try:
        # Initialize the client
        notion = Client(auth=os.getenv('NOTION_API_KEY'))
        
        # Try to query the database
        database_id = os.getenv('NOTION_DATABASE_ID')
        response = notion.databases.query(database_id=database_id)
        
        # Print first few items to verify content
        print("\nSuccessfully connected to Notion!")
        print("\nFirst few tasks found:")
        for page in response['results'][:3]:  # Show first 3 items
            # Get the title/name property (assumes there's a 'Name' property)
            title_prop = None
            for prop_name, prop_data in page['properties'].items():
                if prop_data['type'] == 'title':
                    if prop_data['title']:
                        title_prop = prop_data['title'][0]['text']['content']
                        break
            
            if title_prop:
                print(f"- {title_prop}")
            
        return True
        
    except Exception as e:
        print(f"\nError connecting to Notion: {str(e)}")
        return False

if __name__ == "__main__":
    test_notion_connection()