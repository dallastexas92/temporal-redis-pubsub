import asyncio
import os
import json
import uuid
import redis.asyncio as redis
from temporalio.client import Client
from dotenv import load_dotenv
from workflows import LLMStreamingWorkflow
from shared import TASK_QUEUE

# Load environment variables
load_dotenv()

# Use a fixed channel name for easier debugging
FIXED_CHANNEL = "claude-stream-channel"

# Listen to Redis PubSub channel and print each chunk as it arrives
async def listen_to_pubsub(channel: str) -> str:
    # Connect to Redis
    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)), 
        decode_responses=True
    )
    
    try:
        # Subscribe to the channel
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        
        print(f"Subscribed to Redis channel: {channel}")
        print("Streaming response from Claude 3.7 Sonnet:")
        print("-" * 40)
        
        final_output = ""
        
        # Process messages as they arrive
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    
                    # Check for error
                    if "error" in data:
                        print(f"\nError: {data['error']}")
                        return ""
                    
                    # Process chunk - only print the new chunk
                    if "chunk" in data:
                        chunk = data["chunk"]
                        # Print the chunk without any carriage returns
                        print(chunk, end="", flush=True)
                        
                        # Keep track of the complete response
                        if "accumulated" in data:
                            final_output = data["accumulated"]
                        else:
                            final_output += chunk
                        
                        # Check for completion
                        if data.get("is_final", False):
                            print("\n" + "-" * 40)
                            await pubsub.unsubscribe()
                            return final_output
                
                except json.JSONDecodeError:
                    print(f"\nReceived invalid JSON: {message['data']}")
    
    finally:
        # Clean up
        try:
            await pubsub.unsubscribe()
        except:
            pass
        await redis_client.aclose()

async def main():
    # Get prompt from user
    print("\n===== Claude 3.7 Sonnet Streaming Demo =====")
    prompt = input("Enter your prompt: ")
    if not prompt.strip():
        prompt = "Explain quantum computing in simple terms."
        print(f"Using default prompt: \"{prompt}\"")
    
    # Generate unique workflow ID
    workflow_id = f"claude-streaming-{uuid.uuid4()}"
    
    # Use fixed channel name for easier monitoring
    channel = FIXED_CHANNEL
    
    # Connect to Temporal
    client = await Client.connect(
        f"{os.getenv('TEMPORAL_HOST', 'localhost')}:{os.getenv('TEMPORAL_PORT', '7233')}"
    )
    
    # Start Redis listener
    listener_task = asyncio.create_task(listen_to_pubsub(channel))
    
    # Execute the workflow
    print(f"Executing workflow on task queue: {TASK_QUEUE}")
    workflow_task = asyncio.create_task(
        client.execute_workflow(
            LLMStreamingWorkflow.run,
            id=workflow_id,
            task_queue=TASK_QUEUE,
            args=[prompt, channel, "claude-3-7-sonnet-20250219"]
        )
    )
    
    # Wait for both tasks to complete
    final_output = await listener_task
    result = await workflow_task
    
    print(f"\nWorkflow execution complete. Result length: {len(result)} characters")

if __name__ == "__main__":
    asyncio.run(main())