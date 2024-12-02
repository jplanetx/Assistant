from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
import os

class EnhancedTaskManager:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv('NOTION_API_KEY'))
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        self.areas_database_id = os.getenv('NOTION_AREAS_DATABASE_ID')

    def calculate_urgency(self, due_date):
        """Calculate urgency based on due date"""
        if not due_date:
            return "medium"
            
        try:
            due_date = due_date.split('T')[0] if 'T' in due_date else due_date
            due = datetime.strptime(due_date, '%Y-%m-%d')
            today = datetime.now()
            days_until_due = (due - today).days
            
            if days_until_due <= 3:
                return "high"
            elif days_until_due <= 7:
                return "medium"
            else:
                return "low"
        except Exception as e:
            print(f"Error calculating urgency: {str(e)}")
            return "medium"

    def get_area_maslow_levels(self):
        """Fetch all areas and their Maslow levels"""
        try:
            response = self.notion.databases.query(database_id=self.areas_database_id)
            area_levels = {}
            
            for page in response['results']:
                area_id = page['id']
                try:
                    area_name = page['properties']['Name']['title'][0]['text']['content']
                except:
                    print(f"Warning: Could not get name for area {area_id}")
                    continue
                
                try:
                    maslow_prop = page['properties'].get('Maslow Level', {})
                    maslow_level = maslow_prop.get('select', {}).get('name', 'Uncategorized')
                except:
                    print(f"Warning: Could not get Maslow level for area {area_name}")
                    maslow_level = 'Uncategorized'
                
                area_levels[area_id] = {'name': area_name, 'level': maslow_level}
                print(f"Mapped area: {area_name} -> {maslow_level}")
            
            return area_levels
        except Exception as e:
            print(f"Error fetching areas: {str(e)}")
            return {}

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
            
            area_levels = self.get_area_maslow_levels()
            print(f"Found {len(area_levels)} areas with Maslow levels")
            tasks = []
            
            for page in response['results']:
                task = {}
                try:
                    for prop_name, prop_data in page['properties'].items():
                        if prop_data['type'] == 'title' and prop_name == 'Task':
                            title = prop_data.get('title', [])
                            if title:
                                task['name'] = title[0]['text']['content']
                        elif prop_data['type'] == 'date' and prop_data.get('date'):
                            task['due_date'] = prop_data['date']['start']
                        elif prop_data['type'] == 'select' and prop_data.get('select'):
                            if prop_name.lower() == 'importance':
                                task['importance'] = prop_data['select']['name']
                            elif prop_name.lower() == 'urgency':
                                task['urgency'] = prop_data['select']['name']
                        elif prop_data['type'] == 'relation' and prop_name == 'Areas':
                            area_ids = [rel['id'] for rel in prop_data['relation']]
                            if area_ids:
                                area_info = area_levels.get(area_ids[0], {})
                                task['area'] = area_info.get('name', 'Uncategorized')
                                task['maslow_level'] = area_info.get('level', 'Uncategorized')
                
                    if task.get('name'):
                        if not task.get('urgency') and task.get('due_date'):
                            task['urgency'] = self.calculate_urgency(task['due_date'])
                        tasks.append(task)
                except Exception as e:
                    print(f"Error processing task: {str(e)}")
                    continue
            
            return tasks
        except Exception as e:
            print(f"Error fetching tasks: {str(e)}")
            return []

    def analyze_task_distribution(self, tasks):
        """Analyze task distribution across Maslow levels"""
        distribution = defaultdict(int)
        total_tasks = len(tasks)
        
        for task in tasks:
            level = task.get('maslow_level', 'Uncategorized')
            distribution[level] += 1
        
        analysis = "\n📊 Task Distribution Analysis:\n"
        
        for level, count in distribution.items():
            percentage = (count / total_tasks) * 100 if total_tasks > 0 else 0
            analysis += f"\n{level}: {count} tasks ({percentage:.1f}%)"
        
        return analysis

    def generate_recommendations(self, tasks):
        """Generate prioritized task recommendations"""
        maslow_tasks = defaultdict(lambda: defaultdict(list))
        
        for task in tasks:
            level = task.get('maslow_level', 'Uncategorized')
            is_important = task.get('importance', '').lower() in ['high', 'important', 'yes']
            is_urgent = task.get('urgency', '').lower() in ['high', 'urgent', 'yes']
            
            if is_important and is_urgent:
                quadrant = 'urgent_important'
            elif is_important:
                quadrant = 'not_urgent_important'
            elif is_urgent:
                quadrant = 'urgent_not_important'
            else:
                quadrant = 'not_urgent_not_important'
                
            maslow_tasks[level][quadrant].append(task)
        
        recommendations = "🎯 Task Recommendations by Development Area\n\n"
        
        for level in maslow_tasks:
            if any(maslow_tasks[level].values()):
                recommendations += f"\n== {level} ==\n"
                
                if maslow_tasks[level]['urgent_important']:
                    recommendations += "\n🔥 Do First:\n"
                    for task in maslow_tasks[level]['urgent_important']:
                        due = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                        area = f" [{task.get('area', '')}]" if task.get('area') else ""
                        recommendations += f"- {task['name']}{area}{due}\n"
                
                if maslow_tasks[level]['not_urgent_important']:
                    recommendations += "\n📅 Schedule:\n"
                    for task in maslow_tasks[level]['not_urgent_important']:
                        due = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                        area = f" [{task.get('area', '')}]" if task.get('area') else ""
                        recommendations += f"- {task['name']}{area}{due}\n"
                
                other_tasks = maslow_tasks[level]['urgent_not_important'] + maslow_tasks[level]['not_urgent_not_important']
                if other_tasks:
                    recommendations += "\n📌 Also Consider:\n"
                    for task in other_tasks[:3]:
                        due = f" (Due: {task['due_date']})" if task.get('due_date') else ""
                        area = f" [{task.get('area', '')}]" if task.get('area') else ""
                        recommendations += f"- {task['name']}{area}{due}\n"
        
        return recommendations

def main():
    manager = EnhancedTaskManager()
    
    print("\nFetching your tasks from Notion...")
    tasks = manager.fetch_tasks()
    
    if tasks:
        print(f"\nFound {len(tasks)} active tasks!")
        
        distribution_analysis = manager.analyze_task_distribution(tasks)
        print(distribution_analysis)
        
        print("\nGenerating comprehensive recommendations...")
        recommendations = manager.generate_recommendations(tasks)
        print("\n" + recommendations)
    else:
        print("\nNo active tasks found in the database.")

if __name__ == "__main__":
    main()