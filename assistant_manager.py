from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class AssistantManager:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_gpt_recommendation(self, tasks):
        """
        Get task recommendations from GPT-3.5-turbo
        
        Args:
            tasks (list): List of tasks from Notion
            
        Returns:
            str: GPT's recommendation
        """
        # Format tasks into a clear prompt
        task_list = "\n".join([f"- {task}" for task in tasks])
        prompt = f"""Please analyze these tasks and provide recommendations for prioritization:
        
        {task_list}
        
        Please consider urgency, importance, and dependencies between tasks."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using the more cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes tasks and provides prioritization recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting recommendation: {str(e)}"

    def get_mock_recommendation(self, tasks):
        """
        Get a mock recommendation for testing without using API credits
        """
        task_list = "\n".join([f"- {task}" for task in tasks])
        return f"""Here's a mock prioritization of your tasks:

1. Highest Priority: {tasks[0]} - This should be tackled first as it appears most urgent.
2. Medium Priority: {tasks[1]} - Can be worked on after the first task is complete.
3. Lower Priority: {tasks[2]} - Can be scheduled for later.

This is a mock response for testing purposes."""

# Example usage
if __name__ == "__main__":
    # Test the integration
    assistant = AssistantManager()
    sample_tasks = [
        "Update project documentation",
        "Fix OpenAI API integration",
        "Test Notion database connection"
    ]
    
    # Use this for testing without API calls
    print("\nMock Recommendation (for testing):")
    print(assistant.get_mock_recommendation(sample_tasks))
    
    # Uncomment this when ready to use the API
    # print("\nGPT Recommendation:")
    # print(assistant.get_gpt_recommendation(sample_tasks))