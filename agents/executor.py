import re
from config import client, MODEL_NAME

class ExecutorAgent:
    def execute(self, task: str, feedback: str = None) -> str:
        prompt = "You are a precise execution agent. Solve the task perfectly.\n\n"
        
        if feedback:
            prompt += f"PREVIOUS ATTEMPT FAILED!\nFeedback: {feedback}\nFIX THE ERROR NOW.\n\n"
        
        prompt += f"Task: {task}"

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            
            # Detect rate limiting errors (429)
            if "429" in error_str or "Resource Exhausted" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                # Try to extract retry_delay from error message
                delay_match = re.search(r'retry in (\d+\.\d+|\d+) second', error_str)
                if delay_match:
                    delay = float(delay_match.group(1))
                    return f"[RATE_LIMIT_429] Error: {error_str[:100]} | Retry after {delay} seconds"
                else:
                    return f"[RATE_LIMIT_429] Error: {error_str[:100]} | Retry after 60 seconds (default)"
            
            # Generic execution error
            return f"[EXECUTION_ERROR] {error_str[:150]}"