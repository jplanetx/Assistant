# Notion Task Assistant

A Python-based personal assistant that integrates with Notion to provide intelligent task management using a combination of proven frameworks:
- Eisenhower Matrix for priority management
- Maslow's Hierarchy for personal development alignment
- ADD-friendly task organization

## Features

### Core Functionality
- 📊 Task prioritization using Eisenhower Matrix
- 🔄 Integration with Notion databases
- 🎯 Smart task recommendations
- 📈 Personal development tracking through Maslow's Hierarchy

### Key Features
- Two-way database relations for clean data structure
- Energy level-based task suggestions
- Impact tracking for better priority management
- Flexible project categorization

## Setup

### Prerequisites
- Python 3.8+
- Notion account with API access
- OpenAI API key (for GPT integration)

### Installation
1. Clone the repository
```bash
git clone [your-repository-url]
cd notion-task-assistant
```

2. Install required packages
```bash
pip install notion-client python-dotenv openai
```

3. Create a `.env` file in the project root with:
```
NOTION_API_KEY=your-notion-api-key
NOTION_DATABASE_ID=your-tasks-database-id
NOTION_AREAS_DATABASE_ID=your-areas-database-id
OPENAI_API_KEY=your-openai-api-key
```

### Notion Setup
1. Create required databases in Notion:
   - Tasks
   - Projects
   - Areas

2. Set up database properties:
   - Tasks: Importance, Urgency, Impact Level, Energy Required
   - Projects: Type (Strategic/Maintenance/Quick Win)
   - Areas: Maslow Level

## Usage

Run the main task manager:
```bash
python enhanced_manager.py
```

## Project Structure
```
.
├── enhanced_manager.py    # Main implementation
├── task_manager.py       # Basic task management
└── notion_test.py        # Connection testing
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Built with Notion API
- Inspired by the Eisenhower Matrix
- Structured around Maslow's Hierarchy of Needs
- Designed for ADD-friendly task management

## Future Development
- [ ] AI-powered task categorization
- [ ] Energy level-based recommendations
- [ ] Automated project suggestions
- [ ] Enhanced visualization of task distribution

## Contact
- **Developer**: Jason Lopez
- **GitHub**: [@jplanetx](https://github.com/jplanetx)
- **Email**: jplanetx@gmail.com
- **Project Repository**: [notion-task-assistant](https://github.com/jplanetx/notion-task-assistant)