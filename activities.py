from temporalio import activity
import redis.asyncio as redis
import os
import json
import asyncio
from shared import LLMInput

@activity.defn
async def streamed_llm_activity(input: LLMInput) -> str:
    """Activity that calls Claude and streams the response via Redis PubSub."""
    # Initialize redis client
    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)), 
        decode_responses=True
    )
    
    try:
        # Import anthropic inside the activity
        import anthropic
        
        # Use anthropic client
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        print(f"Using Anthropic SDK version: {getattr(anthropic, '__version__', 'unknown')}")
        
        # Initialize complete response
        complete_response = ""
        
        # Use the current syntax for streaming from the documentation
        # Create a stream with stream=True parameter
        with client.messages.stream(
            model=input.model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": input.prompt}
            ]
        ) as stream:
            # Process each token as it arrives using text_stream for convenience
            for text in stream.text_stream:
                # Publish token to Redis
                await redis_client.publish(
                    input.channel,
                    json.dumps({
                        "chunk": text,
                        "is_final": False
                    })
                )
                
                # Accumulate for complete response
                complete_response += text
        
        # Send a final message
        await redis_client.publish(
            input.channel,
            json.dumps({
                "chunk": "",
                "is_final": True
            })
        )
        
        return complete_response
        
    except Exception as e:
        print(f"Activity error: {e}")
        # Publish error to Redis
        await redis_client.publish(
            input.channel,
            json.dumps({"error": str(e)})
        )
        raise
    finally:
        # Clean up Redis connection
        await redis_client.aclose()