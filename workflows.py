from temporalio import workflow
from datetime import timedelta
from shared import LLMInput

# Use unsafe.imports_passed_through to safely import the activity
with workflow.unsafe.imports_passed_through():
    from activities import streamed_llm_activity

@workflow.defn
class LLMStreamingWorkflow:
    @workflow.run
    async def run(self, prompt: str, channel: str, model: str = "claude-3-7-sonnet-20250219") -> str:
        """
        Execute the LLM streaming workflow.
        
        Args:
            prompt: The prompt to send to Claude
            channel: Redis PubSub channel for streaming results
            model: The Claude model to use
            
        Returns:
            The complete response from Claude
        """
        # Execute the activity
        return await workflow.execute_activity(
            streamed_llm_activity,
            LLMInput(prompt=prompt, channel=channel, model=model),
            start_to_close_timeout=timedelta(minutes=5),
        )