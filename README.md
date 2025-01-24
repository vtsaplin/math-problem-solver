# Math Problem Solver

A demo project showcasing CrewAI's capabilities in solving mathematical challenges using AI agents with code interpretation. This project implements a feedback loop system where one agent solves problems using Python code execution while another validates the results.

## Features

- Demonstrates CrewAI's agent collaboration system
- Showcases code interpreter tool integration
- Implements feedback loop validation architecture
- Provides real-time solution verification
- Handles multiple solution attempts automatically

## Installation

1. Clone the repository
2. Install uv using Homebrew (recommended):
```bash
brew install uv
```

3. Create a `.env` file with your OpenAI API key:
```bash
AZURE_API_KEY=...
AZURE_API_BASE=...
AZURE_API_VERSION=...
OPENAI_API_KEY=...
OTEL_SDK_DISABLED=true
CREWAI_TELEMETRY_OPT_OUT=true

```

4. Run the application (uv will automatically handle virtual environment and dependencies):
```bash
uv run app.py
```

## How It Works

This showcase demonstrates CrewAI's capabilities through two specialized AI agents:
1. **Math Problem Solver**: Uses code interpretation to solve math problems programmatically
2. **Math Result Validator**: Reviews solutions and provides structured feedback

The feedback loop workflow:
1. Problem is submitted to the solver agent
2. Solver executes Python code to compute the solution
3. Validator agent reviews and provides VALID/INVALID feedback
4. System automatically retries with different approaches if invalid
5. Process continues until a valid solution is found or max attempts reached

This architecture demonstrates CrewAI's ability to:
- Execute real Python code for problem-solving
- Implement multi-agent validation systems
- Handle complex feedback loops
- Manage state across multiple solution attempts

## Response Format

The solver returns a dictionary containing:
- `result`: The computed solution
- `feedback`: Validation feedback
- `attempts`: Number of attempts made
- `status`: Final status ("success" or "failed")

## Requirements

- Python ≥ 3.12
- CrewAI ≥ 0.98.0
- CrewAI Tools ≥ 0.32.1

## License

MIT
