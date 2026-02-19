import json
from google.genai.types import GenerationConfig
from config import client, MODEL_NAME
from utils.types import ValidationResult, ErrorType
from utils.helpers import clean_json_string

class ValidatorAgent:
    def __init__(self):
        # We use the shared client from config.py
        pass

    def validate(self, task: str, result: str) -> ValidationResult:
        """
        Use Gemini to evaluate the agent's output and return structured validation.
        Returns JSON-parsed ValidationResult with score, error_type, feedback.
        """
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
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,           # low temperature → more deterministic JSON
                    max_output_tokens=300
                )
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
                feedback=reasoning
            )

        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.TOOL,
                feedback=f"Validator failed to parse JSON response: {str(e)}"
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                score=1.0,
                error_type=ErrorType.TOOL,
                feedback=f"Validator crashed: {type(e).__name__}: {str(e)}"
            )