from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

class EnhancedTaskManager:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv('NOTION_API_KEY'))
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
    def fetch_tasks(self):
        """Fetch tasks from Notion database"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id
            )
            
            tasks = []
            for page in response['results']:
                task = {}
                # Extract properties
                for prop_name, prop_data in page['properties'].items():
                    if prop_data['type'] == 'title' and prop_data['title']:
                        task['name'] = prop_data['title'][0]['text']['content']
                    elif prop_data['type'] == 'date' and prop_data.get('date'):
                        task['due_date'] = prop_data['date']['start']
                    elif prop_data['type'] == 'select' and prop_data.get('select'):
                        if prop_name.lower() == 'importance':
                            task['importance'] = prop_data['select']['name']
                        elif prop_name.lower() == 'urgency':
                            task['urgency'] = prop_data['select']['name']
                
                if task.get('name'):  # Only add if task has a name
                    tasks.append(task)
            
            return tasks
        
        except Exception as e:
            print(f"Error fetching tasks: {str(e)}")
            return []

    def categorize_eisenhower(self, tasks):
        """Categorize tasks using Eisenhower Matrix"""
        matrix = {
            'urgent_important': [],      # Do First
            'not_urgent_important': [],  # Schedule
            'urgent_not_important': [],  # Delegate
            'not_urgent_not_important': [] # Eliminate
        }
        
        for task in tasks:
            # Default to medium if not specified
            importance = task.get('importance', 'medium').lower()
            urgency = task.get('urgency', 'medium').lower()
            
            is_important = importance in ['high', 'important', 'yes']
            is_urgent = urgency in ['high', 'urgent', 'yes']
            
            if is_important and is_urgent:
                matrix['urgent_important'].append(task)
            elif is_important:
                matrix['not_urgent_important'].append(task)
            elif is_urgent:
                matrix['urgent_not_important'].append(task)
            else:
                matrix['not_urgent_not_important'].append(task)
                
        return matrix

    def format_recommendations(self, matrix):
        """Format task recommendations based on Eisenhower Matrix"""
        recommendations = "📊 Task Recommendations (Eisenhower Matrix)\n\n"
        
        # Do First (Urgent & Important)
        recommendations += "🔥 DO FIRST (Urgent & Important):\n"
        if matrix['urgent_important']:
            for task in matrix['urgent_important']:
                due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                recommendations += f"- {task['name']}{due_date}\n"
        else:
            recommendations += "- No tasks in this category\n"
        recommendations += "\n"
        
        # Schedule (Important, Not Urgent)
        recommendations += "📅 SCHEDULE (Important, Not Urgent):\n"
        if matrix['not_urgent_important']:
            for task in matrix['not_urgent_important']:
                due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                recommendations += f"- {task['name']}{due_date}\n"
        else:
            recommendations += "- No tasks in this category\n"
        recommendations += "\n"
        
        # Delegate (Urgent, Not Important)
        recommendations += "👥 DELEGATE (Urgent, Not Important):\n"
        if matrix['urgent_not_important']:
            for task in matrix['urgent_not_important']:
                due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                recommendations += f"- {task['name']}{due_date}\n"
        else:
            recommendations += "- No tasks in this category\n"
        recommendations += "\n"
        
        # Eliminate (Not Urgent, Not Important)
        recommendations += "⚠️ ELIMINATE/MINIMIZE (Not Urgent, Not Important):\n"
        if matrix['not_urgent_not_important']:
            for task in matrix['not_urgent_not_important']:
                due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                recommendations += f"- {task['name']}{due_date}\n"
        else:
            recommendations += "- No tasks in this category\n"
        
        return recommendations

def main():
    manager = EnhancedTaskManager()
    
    print("\nFetching your tasks from Notion...")
    tasks = manager.fetch_tasks()
    
    if tasks:
        print(f"\nFound {len(tasks)} tasks!")
        print("\nAnalyzing using Eisenhower Matrix...")
        matrix = manager.categorize_eisenhower(tasks)
        recommendations = manager.format_recommendations(matrix)
        print("\n" + recommendations)
    else:
        print("\nNo tasks found in the database.")

if __name__ == "__main__":
    main()