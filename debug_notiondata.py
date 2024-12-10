tasks = fetch_notion_database(NOTION_DATABASE_ID)
if not tasks:
    print("No tasks found or unable to retrieve tasks. Check database contents.")
else:
    print(f"Sample task: {tasks[0]}")

