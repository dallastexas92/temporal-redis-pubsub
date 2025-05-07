# Temporal Streaming with Redis PubSub

A solution for real-time streaming output from Temporal workflows using Redis PubSub. This addresses the limitation that Temporal doesn't natively support streaming responses.

## Overview

This project demonstrates how to implement real-time streaming from Temporal workflows by using Redis PubSub as a communication channel. This demonstration focuses specifically on streaming text output to the CLI.

## How It Works

1. A Temporal workflow is defined that executes an activity
2. The activity streams its output to a Redis PubSub channel character by character
3. A client subscribes to the channel and displays the stream in real-time in the terminal
4. The workflow completes once all streaming is finished

## Requirements

- UV package manager (for dependency management)
- Python 3.10+
- Redis server
- Temporal server

## Installation

```bash
# Create a virtual environment using UV (recommended)
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies with UV
uv sync
```

## Usage

1. Start a Redis server in a separate terminal:
```bash
redis-server # Validate it's running in another terminal by running 'redi-cli ping' --> response should be 'pong'
```

2. Start a Temporal server in a separate terminal:
```bash
temporal server start-dev # Open the Temporal UI on localhost:8233
```

3. Run the code from the original virtual environment:
```bash
python redis_stream_llm.py
```

## Project Structure

- `redis_stream_llm.py`: Main application file containing the Temporal workflow, activity, and Redis PubSub implementation
- `pyproject.toml`: Project configuration file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT](LICENSE)
