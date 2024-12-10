import os
import time
from random import uniform
from notion_client import Client
import openai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Notion and OpenAI clients
notion = Client(auth=NOTION_API_KEY)
openai.api_key = OPENAI_API_KEY

# Utility functions
def delay_with_jitter():
    """Add random delay to respect Notion's rate limits."""
    time.sleep(uniform(0.8, 1.2))

def fetch_notion_database(database_id):
    """Fetch tasks from a Notion database."""
    try:
        response = notion.databases.query(database_id=database_id)
        tasks = response.get('results', [])
        logger.info(f"Fetched {len(tasks)} tasks from the database.")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching database {database_id}: {e}")
        return []

def analyze_task_with_gpt(task_name):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that analyzes tasks."},
                {"role": "user", "content": f"Analyze the task: {task_name}"}
            ],
            max_tokens=150
        )
        message = response['choices'][0]['message']['content'].strip()
        # Parse the GPT response into impact and energy values as needed
        return parse_gpt_response(message)
    except Exception as e:
        logger.error(f"Error analyzing task with GPT: {e}")
        return None, None


def update_task_properties(task_id, properties):
    """Update task properties in Notion."""
    try:
        notion.pages.update(page_id=task_id, properties=properties)
        logger.info(f"Task {task_id} updated successfully.")
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")

def process_task(task):
    """Process an individual task."""
    task_id = task.get("id")
    properties = task.get("properties", {})

    if not properties:
        logger.warning(f"Task {task_id} has no properties. Skipping.")
        return

    # Skip completed or archived tasks
    status = properties.get('Status', {}).get('select', {}).get('name')
    if status in ['Completed', 'Archived']:
        logger.info(f"Skipping task {task_id} with status '{status}'.")
        return

    # Safely extract task name
    name_property = properties.get("Name", {}).get("title", [{}])
    name = name_property[0].get("text", {}).get("content", "Unnamed Task") if name_property else "Unnamed Task"

    # Debug logging for properties
    logger.info(f"Task Properties for '{name}': {list(properties.keys())}")

    # Safely extract Impact and Energy Required
    impact_property = properties.get("Impact", {})
    logger.info(f"Impact Property Raw: {impact_property}")

    # Safely extract impact name
    impact = (impact_property.get("select", {})['name'] 
              if impact_property.get("select") 
              else None)

    energy_property = properties.get("Energy Required", {})
    logger.info(f"Energy Property Raw: {energy_property}")

    # Safely extract energy name
    energy = (energy_property.get("select", {})['name'] 
              if energy_property.get("select") 
              else None)

    # Check for missing properties
    if not impact or not energy:
        logger.info(f"Task {task_id} ('{name}') is missing properties. Sending to GPT.")
        gpt_impact, gpt_energy = analyze_task_with_gpt(name)

        if gpt_impact or gpt_energy:
            update_properties = {}
            if gpt_impact:
                update_properties["Impact"] = {"select": {"name": gpt_impact}}
            if gpt_energy:
                update_properties["Energy Required"] = {"select": {"name": gpt_energy}}
            
            if update_properties:
                update_task_properties(task_id, update_properties)
                # Update local variables to reflect GPT suggestions
                impact = gpt_impact or impact
                energy = gpt_energy or energy
        else:
            logger.warning(f"GPT could not generate properties for task {task_id}.")

    # Optional: Log the final impact and energy for verification
    logger.info(f"Task '{name}': Impact = {impact}, Energy = {energy}")

# Main script
def main():
    logger.info("Fetching tasks from Notion...")
    tasks = fetch_notion_database(NOTION_DATABASE_ID)

    if not tasks:
        logger.warning("No tasks found or unable to retrieve tasks. Check database contents.")
        return

    logger.info(f"Processing {len(tasks)} tasks...")
    for task in tasks:
        process_task(task)
        delay_with_jitter()

    logger.info("Task processing completed.")

if __name__ == "__main__":
    main()
