from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

class EnhancedTaskManager:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv('NOTION_API_KEY'))
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
    def calculate_urgency(self, due_date):
        """Calculate urgency based on due date"""
        if not due_date:
            return "medium"
            
        try:
            due = datetime.strptime(due_date.split('T')[0], '%Y-%m-%d')
            today = datetime.now()
            days_until_due = (due - today).days
            
            if days_until_due <= 3:  # Due within 3 days
                return "high"
            elif days_until_due <= 7:  # Due within a week
                return "medium"
            else:
                return "low"
        except:
            return "medium"

    def fetch_tasks(self):
        """Fetch tasks from Notion database"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Completed"
                    }
                }
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
                    elif prop_data['type'] == 'relation':
                        if prop_name.lower() == 'project':
                            task['project'] = prop_data['relation']
                
                if task.get('name'):
                    # Calculate urgency based on due date if not manually set
                    if not task.get('urgency') and task.get('due_date'):
                        task['urgency'] = self.calculate_urgency(task['due_date'])
                    tasks.append(task)
            
            return tasks
        
        except Exception as e:
            print(f"Error fetching tasks: {str(e)}")
            return []

    def suggest_importance_urgency(self, task_name):
        """Suggest importance/urgency based on task name keywords"""
        important_keywords = ['essential', 'critical', 'key', 'main', 'major', 'primary', 'deadline', 
                            'install', 'setup', 'configure', 'implement']
        urgent_keywords = ['asap', 'immediately', 'urgent', 'deadline', 'due', 'today', 'tomorrow']
        
        task_lower = task_name.lower()
        
        importance = 'high' if any(keyword in task_lower for keyword in important_keywords) else 'medium'
        urgency = 'high' if any(keyword in task_lower for keyword in urgent_keywords) else 'medium'
        
        return importance, urgency

    def categorize_eisenhower(self, tasks):
        """Categorize tasks using Eisenhower Matrix"""
        matrix = {
            'urgent_important': [],
            'not_urgent_important': [],
            'urgent_not_important': [],
            'not_urgent_not_important': []
        }
        
        for task in tasks:
            # If importance/urgency not set, suggest based on task name
            if not task.get('importance') or not task.get('urgency'):
                suggested_importance, suggested_urgency = self.suggest_importance_urgency(task['name'])
                task['importance'] = task.get('importance', suggested_importance)
                task['urgency'] = task.get('urgency', suggested_urgency)
            
            is_important = task['importance'].lower() in ['high', 'important', 'yes']
            is_urgent = task['urgency'].lower() in ['high', 'urgent', 'yes']
            
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
        
        sections = {
            'urgent_important': ('🔥 DO FIRST (Urgent & Important)', matrix['urgent_important']),
            'not_urgent_important': ('📅 SCHEDULE (Important, Not Urgent)', matrix['not_urgent_important']),
            'urgent_not_important': ('👥 DELEGATE (Urgent, Not Important)', matrix['urgent_not_important']),
            'not_urgent_not_important': ('⚠️ ELIMINATE/MINIMIZE (Not Urgent, Not Important)', matrix['not_urgent_not_important'])
        }
        
        for section_id, (title, tasks) in sections.items():
            recommendations += f"{title}:\n"
            if tasks:
                # Group tasks by auto-suggested vs. manually set
                auto_suggested = [t for t in tasks if not t.get('importance') or not t.get('urgency')]
                manually_set = [t for t in tasks if t.get('importance') and t.get('urgency')]
                
                # Print manually set tasks first
                for task in manually_set:
                    due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                    recommendations += f"- {task['name']}{due_date}\n"
                
                # Print auto-suggested tasks with a note
                if auto_suggested:
                    recommendations += "\nSuggested tasks (need priority setting):\n"
                    for task in auto_suggested:
                        due_date = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                        recommendations += f"- {task['name']}{due_date}\n"
            else:
                recommendations += "- No tasks in this category\n"
            recommendations += "\n"
        
        return recommendations

def main():
    manager = EnhancedTaskManager()
    
    print("\nFetching your tasks from Notion...")
    tasks = manager.fetch_tasks()
    
    if tasks:
        print(f"\nFound {len(tasks)} active tasks!")
        print("\nAnalyzing using Eisenhower Matrix...")
        matrix = manager.categorize_eisenhower(tasks)
        recommendations = manager.format_recommendations(matrix)
        print("\n" + recommendations)
    else:
        print("\nNo active tasks found in the database.")

if __name__ == "__main__":
    main()