import asyncio
import os
from temporalio.worker import Worker
from temporalio.client import Client
from dotenv import load_dotenv
from workflows import LLMStreamingWorkflow
from activities import streamed_llm_activity
from shared import TASK_QUEUE

# Load environment variables
load_dotenv()

async def main():
    # Connect to Temporal server
    client = await Client.connect(
        f"{os.getenv('TEMPORAL_HOST', 'localhost')}:{os.getenv('TEMPORAL_PORT', '7233')}"
    )
    
    # Create worker
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LLMStreamingWorkflow],
        activities=[streamed_llm_activity],
    )
    
    print(f"Worker started on task queue: {TASK_QUEUE}")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())