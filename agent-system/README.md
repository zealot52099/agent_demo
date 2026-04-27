# Agent System

This project implements an agent system that processes user queries and interacts with various skills and APIs to provide relevant responses.

## Project Structure

```
agent-system
├── src
│   ├── main.py               # Entry point of the application
│   ├── agent                  # Contains agent-related logic
│   │   ├── __init__.py
│   │   ├── agent.py           # Manages user input and inference
│   │   └── inference.py       # Handles inference logic and API requests
│   ├── skills                 # Contains skill management
│   │   ├── __init__.py
│   │   ├── registry.py        # Manages skill registration and retrieval
│   │   └── skill_search.py    # Searches for relevant skills based on queries
│   ├── prompts                # Contains prompt templates
│   │   ├── __init__.py
│   │   └── templates.py       # Generates prompt templates for inference
│   ├── api                    # Contains API definitions
│   │   ├── __init__.py
│   │   └── definitions.py     # API definitions and structures
│   └── utils                  # Contains utility functions
│       ├── __init__.py
│       └── helpers.py         # Assists with various tasks
├── configs                    # Configuration files
│   ├── skills.json           # Skill configurations and descriptions
│   └── api_catalog.json      # Catalog of APIs available for the agent
├── tests                      # Contains unit tests
│   ├── test_agent.py         # Tests for agent functionality
│   └── test_skill_search.py   # Tests for skill search functionality
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd agent-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

- The agent system listens for user queries and processes them using the defined skills and APIs.
- Users can interact with the system through the command line or any specified interface.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.