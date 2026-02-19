from utils.types import AgentState, ValidationResult, ErrorType
from config import MAX_RETRIES

class CorrectionPolicy:
    def decide_action(self, state: AgentState, validation: ValidationResult) -> str:
        # 1. Success
        if validation.is_valid:
            return "accept"

        # 2. Safety Limit
        if state.attempt_count >= MAX_RETRIES:
            return "stop_max_retries"

        # 3. Rate Limiting - HIGHEST PRIORITY (needs special handling with delays)
        if validation.error_type == ErrorType.RATE_LIMIT:
            return "wait_and_retry"
        
        # 4. Adaptive Strategy for other errors
        elif validation.error_type == ErrorType.TOOL:
            return "retry_tool_fix"
        elif validation.error_type == ErrorType.HALLUCINATION:
            return "retry_grounding"
        elif validation.error_type == ErrorType.CONSTRAINT:
            return "retry_format_fix"
        elif validation.error_type == ErrorType.SEMANTIC:
            return "retry_reasoning"

        # default fallback
        return "retry_standard"