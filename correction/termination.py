class TerminationController:
    def should_terminate(self, action: str) -> bool:
        return action in ["accept", "stop_max_retries"]