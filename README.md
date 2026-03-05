# AnnabanOS Enhanced

AnnabanOS Enhanced is an advanced multi-agent system framework that enables the creation, management, and interaction of intelligent agents in a simulated environment. This enhanced version builds upon the original AnnabanOS with additional features and improvements.

## Features

- **Advanced Agent Architecture**: Task agents, social agents, and conversational agents with improved capabilities
- **Multi-Agent Collectives**: Groups of agents that can collaborate on complex tasks
- **Enhanced Token Economy**: Sophisticated token management system with marketplace functionality
- **Virtual World Environment**: Spatial simulation with locations, objects, and agent movement
- **Structured Reflection System**: Improved Echo Loop for agent self-reflection and learning
- **Web Dashboard**: Modern web interface for monitoring and interacting with the system
- **Configuration System**: Flexible configuration options for customizing system behavior
- **Logging and Monitoring**: Comprehensive logging and monitoring capabilities

## System Architecture

AnnabanOS Enhanced consists of several key components:

1. **Agents**: Different types of agents with specialized capabilities
   - Task Agents: Focus on completing tasks and solving problems
   - Social Agents: Specialize in communication and relationship building
   - Conversational Agents: Interact with users through natural language

2. **Environment**: The shared space where agents exist and interact
   - Agent Registry: Keeps track of all agents in the system
   - Message Passing: Enables communication between agents
   - Event System: Broadcasts system-wide events

3. **Token Economy**: Economic system for resource allocation
   - Token Manager: Handles token creation, transfer, and accounting
   - Marketplace: Allows agents to exchange tokens for services

4. **Virtual World**: Spatial environment for agent interactions
   - Locations: Designated areas with specific properties
   - Objects: Interactive items in the environment
   - Movement System: Allows agents to navigate the world

5. **Echo Loop**: Reflection and learning mechanism
   - Journal: Records agent reflections and thoughts
   - Portfolio: Tracks achievements and skills
   - Structured Reflection: Guided self-improvement process

6. **Web Interface**: Dashboard for monitoring and control
   - Agent Management: View and manage agents
   - System Monitoring: Track system performance
   - Simulation Controls: Run and control simulations

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/faucetfan/AnnabanOS_Enhanced.git
cd AnnabanOS_Enhanced
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd web_app/frontend
npm install
```

### Running the System

1. Start the backend API:
```bash
cd web_app/backend
python app.py
```

2. Start the frontend development server:
```bash
cd web_app/frontend
npm start
```

3. Access the dashboard at http://localhost:3000

### Running a Simulation

You can run a simulation directly from the command line:

```bash
python main.py --cycles 5
```

Or use the web dashboard to run simulation cycles interactively.

## Documentation

Comprehensive documentation for public APIs, functions, and components is available in the `docs/` directory:

- [Docs Overview](docs/README.md)
- [Usage](docs/usage.md)
- [API Reference](docs/api.md)
- [AnnabanAI Components](docs/annabanai.md)
- [Agents](docs/agents.md)
- [Environment & Virtual World](docs/environment.md)
- [Token Economy](docs/token_economy.md)

## Configuration

The system can be configured using the `config/config.yaml` file. See the comments in the file for available options.

## Directory Structure

```
AnnabanOS_Enhanced/
├── agents/                 # Agent implementations
├── annabanai/              # Core AI components
├── config/                 # Configuration system
├── environment/            # Environment implementation
├── token_economy/          # Token economy system
├── utils/                  # Utility functions
├── web_app/                # Web interface
│   ├── backend/            # Flask API backend
│   └── frontend/           # React frontend
├── tests/                  # Test suite
├── demos/                  # Demo scripts
├── journal/                # Journal entries storage
├── portfolio/              # Portfolio items storage
├── main.py                 # Main entry point
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original AnnabanOS creators
- The open-source AI community

