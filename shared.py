from dataclasses import dataclass

# Define the task queue name to be used by both worker and client
TASK_QUEUE = "claude-streaming-queue"

# Define input dataclass
@dataclass
class LLMInput:
    """Input structure for LLM streaming activity."""
    prompt: str
    channel: str
    model: str = "claude-3-7-sonnet-20250219"