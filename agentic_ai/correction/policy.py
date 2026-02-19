from utils.types import AgentState, ValidationResult, ErrorType

class CorrectionPolicy:
    def decide_action(self, state: AgentState, validation: ValidationResult) -> str:
        # 1. Success
        if validation.is_valid:
            return "accept"

        # 2. Safety Limit
        if state.attempt_count >= 3:           # should match MAX_RETRIES from config
            return "stop_max_retries"

        # 3. Adaptive Strategy
        if validation.error_type == ErrorType.TOOL:
            return "retry_tool_fix"
        elif validation.error_type == ErrorType.HALLUCINATION:
            return "retry_grounding"
        elif validation.error_type == ErrorType.CONSTRAINT:
            return "retry_format_fix"

        # default fallback
        return "retry_standard"