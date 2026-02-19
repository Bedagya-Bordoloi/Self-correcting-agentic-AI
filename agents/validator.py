import json
import re
from config import client, MODEL_NAME
from utils.types import ValidationResult, ErrorType
from utils.helpers import clean_json_string

class ValidatorAgent:
    def __init__(self):
        # We use the shared client from config.py
        pass

    def _extract_retry_delay(self, error_str: str) -> float:
        """Extract retry delay in seconds from error messages."""
        # Look for patterns like "retry in 51.630 seconds" or "retry in 60 seconds"
        delay_match = re.search(r'retry in (\d+\.\d+|\d+) second', error_str, re.IGNORECASE)
        if delay_match:
            return float(delay_match.group(1))
        return 60.0  # default to 60 seconds if not found

    def validate(self, task: str, result: str) -> ValidationResult:
        """
        Use Gemini to evaluate the agent's output and return structured validation.
        Returns JSON-parsed ValidationResult with score, error_type, feedback.
        Detects rate limiting errors and returns appropriate retry delay.
        """
        
        # First, check if the result itself indicates a rate limit error
        if "[RATE_LIMIT_429]" in result:
            retry_delay = self._extract_retry_delay(result)
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.RATE_LIMIT,
                feedback=f"API rate limited. Please wait {retry_delay:.1f} seconds before retrying.",
                retry_delay_seconds=retry_delay
            )
        
        # Check for other execution errors
        if "[EXECUTION_ERROR]" in result:
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.TOOL,
                feedback=result,
                retry_delay_seconds=0.0
            )

        prompt = f"""
You are a strict and precise QA Validator for an autonomous agent system.

Task description:
{task}

Agent's output:
{result}

Your job:
1. Carefully compare the output against the task requirements.
2. Assign a failure score:
   - 0.0 = perfect / no issues
   - 0.1–0.3 = minor issues
   - 0.4–0.7 = significant problems
   - 0.8–1.0 = complete failure or irrelevant
3. Classify the primary error type (choose exactly one):
   - "none"              → no detectable error
   - "semantic"          → logical, factual, or reasoning mistake
   - "tool"              → tool misuse, syntax error, API misuse
   - "constraint"        → violates output format, length, style, or rules
   - "hallucination"     → invented facts or information not supported by task

Return **ONLY** valid JSON with these exact keys (no markdown, no extra text):
{{
  "score": <float between 0.0 and 1.0>,
  "error_type": "<one of the five strings above>",
  "reasoning": "<very short 1-sentence explanation>"
}}
"""

        try:
            # For google-genai library, pass config directly to the request
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            # Clean and parse the response
            cleaned = clean_json_string(response.text)
            data = json.loads(cleaned)

            # Safely extract and normalize
            score = float(data.get("score", 1.0))
            error_type_str = data.get("error_type", "none").lower().strip()

            try:
                error_type = ErrorType(error_type_str)
            except ValueError:
                error_type = ErrorType.SEMANTIC  # fallback

            reasoning = data.get("reasoning", "No reasoning provided").strip()

            return ValidationResult(
                is_valid=(score < 0.2),
                score=score,
                error_type=error_type,
                feedback=reasoning,
                retry_delay_seconds=0.0
            )

        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.TOOL,
                feedback=f"Validator failed to parse JSON response: {str(e)}",
                retry_delay_seconds=0.0
            )

        except Exception as e:
            error_str = str(e)
            
            # Detect rate limiting in validator's own API call
            if "429" in error_str or "Resource Exhausted" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                retry_delay = self._extract_retry_delay(error_str)
                return ValidationResult(
                    is_valid=False,
                    score=1.0,
                    error_type=ErrorType.RATE_LIMIT,
                    feedback=f"Validator rate limited. Please wait {retry_delay:.1f} seconds before retrying.",
                    retry_delay_seconds=retry_delay
                )
            
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.TOOL,
                feedback=f"Validator crashed: {type(e).__name__}: {str(e)[:100]}",
                retry_delay_seconds=0.0
            )