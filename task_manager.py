from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv
import os

class TaskManager:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv('NOTION_API_KEY'))
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
    def fetch_tasks(self):
        """Fetch tasks from Notion database"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                sorts=[{
                    "property": "Created",
                    "direction": "descending"
                }]
            )
            
            tasks = []
            for page in response['results']:
                for prop_name, prop_data in page['properties'].items():
                    if prop_data['type'] == 'title':
                        if prop_data['title']:
                            task_title = prop_data['title'][0]['text']['content']
                            tasks.append(task_title)
                            break
            
            return tasks
        
        except Exception as e:
            print(f"Error fetching tasks: {str(e)}")
            return []

    def get_task_recommendations(self, tasks):
        """
        Get mock recommendations for task prioritization
        Later, this will use the real GPT API
        """
        if not tasks:
            return "No tasks found to analyze."
        
        recommendations = "Here's how I suggest prioritizing your tasks:\n\n"
        
        # Categorize tasks
        high_priority = tasks[:2]  # First 2 tasks as high priority
        medium_priority = tasks[2:4]  # Next 2 as medium
        low_priority = tasks[4:]  # Rest as low priority
        
        # Format recommendations
        if high_priority:
            recommendations += "🔥 High Priority (Do These First):\n"
            for task in high_priority:
                recommendations += f"- {task}\n"
            recommendations += "\n"
            
        if medium_priority:
            recommendations += "👉 Medium Priority (Schedule These):\n"
            for task in medium_priority:
                recommendations += f"- {task}\n"
            recommendations += "\n"
            
        if low_priority:
            recommendations += "📋 Lower Priority (Can Wait):\n"
            for task in low_priority:
                recommendations += f"- {task}\n"
                
        return recommendations

def main():
    # Initialize the task manager
    manager = TaskManager()
    
    # Fetch and process tasks
    print("\nFetching your tasks from Notion...")
    tasks = manager.fetch_tasks()
    
    if tasks:
        print(f"\nFound {len(tasks)} tasks!")
        print("\nAnalyzing and generating recommendations...")
        recommendations = manager.get_task_recommendations(tasks)
        print("\n" + recommendations)
    else:
        print("\nNo tasks found in the database.")

if __name__ == "__main__":
    main()