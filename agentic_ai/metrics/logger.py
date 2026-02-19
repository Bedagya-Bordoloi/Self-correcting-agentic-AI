import json
import time
from utils.types import AgentState
from config import LOG_DB_PATH

class MetricsLogger:
    def __init__(self):
        self.logs = []

    def log_step(self, step_num: int, state: AgentState, duration: float):
        entry = {
            "step": step_num,
            "attempt": state.attempt_count,
            "epsilon": state.validation_log[-1].score if state.validation_log else None,
            "error_type": state.validation_log[-1].error_type.value if state.validation_log else None,
            "duration": duration
        }
        self.logs.append(entry)

    def save(self):
        with open(LOG_DB_PATH, "w") as f:
            json.dump(self.logs, f, indent=4)

    def calculate_efficiency(self):
        if not self.logs:
            return 0.0
        initial_eps = self.logs[0].get('epsilon', 1.0)
        final_eps = self.logs[-1].get('epsilon', 1.0)
        return (initial_eps - final_eps) / len(self.logs) if initial_eps > 0 else 0.0