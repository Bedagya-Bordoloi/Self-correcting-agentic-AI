from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

class ErrorType(Enum):
    NONE = "none"
    SEMANTIC = "semantic"       # Logic/fact error
    TOOL = "tool"               # Syntax/API error
    CONSTRAINT = "constraint"   # Formatting/Length violation
    HALLUCINATION = "hallucination"
    RATE_LIMIT = "rate_limit"   # API rate limiting (429 error)

@dataclass
class ValidationResult:
    is_valid: bool
    score: float                # usually interpreted as error distance ε ∈ [0,1]
    error_type: ErrorType
    feedback: str
    retry_delay_seconds: float = 0.0  # When rate limited, how long to wait before retry

@dataclass
class AgentState:
    task: str
    history: List[dict] = field(default_factory=list)
    attempt_count: int = 0
    current_result: Optional[str] = None
    validation_log: List[ValidationResult] = field(default_factory=list)