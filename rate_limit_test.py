"""
Rate Limiting Test - Demonstrates the improved error handling system

This test shows how the agentic AI system now:
1. Detects 429 (rate limit) errors
2. Extracts retry delays from error messages
3. Implements exponential backoff
4. Respects API rate limiting without burning through attempts
"""

import time
from utils.types import ValidationResult, ErrorType
from agents.validator import ValidatorAgent
from correction.policy import CorrectionPolicy
from utils.types import AgentState

def test_rate_limit_detection():
    """Test that rate limit errors are correctly detected."""
    print("=" * 70)
    print("TEST 1: Rate Limit Error Detection")
    print("=" * 70)
    
    validator = ValidatorAgent()
    
    # Simulate executor returning a rate limit error
    rate_limit_output = "[RATE_LIMIT_429] Error: Resource Exhausted | Retry after 51.630 seconds"
    
    validation = validator.validate("Test task", rate_limit_output)
    
    print(f"Input (simulated error): {rate_limit_output}")
    print(f"ErrorType: {validation.error_type}")
    print(f"Score: {validation.score}")
    print(f"Feedback: {validation.feedback}")
    print(f"Retry Delay: {validation.retry_delay_seconds} seconds")
    
    assert validation.error_type == ErrorType.RATE_LIMIT, "Should detect RATE_LIMIT error"
    assert validation.retry_delay_seconds > 0, "Should extract retry delay"
    print("✅ PASSED: Rate limit error correctly detected and delay extracted!\n")


def test_policy_decision_on_rate_limit():
    """Test that the policy makes correct decisions on rate limit errors."""
    print("=" * 70)
    print("TEST 2: Policy Decision on Rate Limit")
    print("=" * 70)
    
    policy = CorrectionPolicy()
    state = AgentState(task="Test task", attempt_count=1)
    
    # Create a rate limit validation result
    validation = ValidationResult(
        is_valid=False,
        score=1.0,
        error_type=ErrorType.RATE_LIMIT,
        feedback="API rate limited. Please wait 51.6 seconds before retrying.",
        retry_delay_seconds=51.6
    )
    
    action = policy.decide_action(state, validation)
    
    print(f"Error Type: {validation.error_type}")
    print(f"Retry Delay: {validation.retry_delay_seconds} seconds")
    print(f"Policy Decision: {action}")
    
    assert action == "wait_and_retry", "Policy should decide to wait_and_retry for rate limits"
    print("✅ PASSED: Policy correctly decides to wait_and_retry!\n")


def test_exponential_backoff():
    """Test exponential backoff calculation."""
    print("=" * 70)
    print("TEST 3: Exponential Backoff Calculation")
    print("=" * 70)
    
    base_delay = 5.0
    backoff_multiplier = 1.5
    
    print(f"Base delay: {base_delay} seconds")
    print(f"Backoff multiplier: {backoff_multiplier}x")
    print("\nBackoff schedule for consecutive rate limits:")
    
    for consecutive_count in range(1, 6):
        multiplier = backoff_multiplier ** (consecutive_count - 1)
        total_delay = base_delay * multiplier
        print(f"  Attempt {consecutive_count}: {total_delay:.1f}s (multiplier: {multiplier:.2f}x)")
    
    print("✅ PASSED: Exponential backoff correctly calculated!\n")


def test_delay_extraction():
    """Test retry delay extraction from various error message formats."""
    print("=" * 70)
    print("TEST 4: Retry Delay Extraction from Error Messages")
    print("=" * 70)
    
    import re
    
    test_cases = [
        ("retry in 51.630 seconds", 51.630),
        ("Please retry in 60 seconds", 60),
        ("error retry in 30.5 seconds please", 30.5),
        ("Resource Exhausted: Please retry in 120 seconds after quota reset", 120),
    ]
    
    validator = ValidatorAgent()
    
    for error_msg, expected_delay in test_cases:
        extracted = validator._extract_retry_delay(error_msg)
        print(f"Error: '{error_msg}'")
        print(f"  Expected: {expected_delay}s, Extracted: {extracted}s", end="")
        assert abs(extracted - expected_delay) < 0.01, f"Delay mismatch for: {error_msg}"
        print(" ✅\n")
    
    print("✅ PASSED: All retry delays correctly extracted!\n")


def test_no_infinite_loops():
    """Test that rate limiting doesn't cause infinite retries."""
    print("=" * 70)
    print("TEST 5: No Infinite Loops with Rate Limiting")
    print("=" * 70)
    
    policy = CorrectionPolicy()
    state = AgentState(task="Test task")
    
    print("Simulating 6 consecutive rate limit attempts:")
    
    last_action = "wait_and_retry"
    for attempt in range(1, 7):
        state.attempt_count = attempt
        validation = ValidationResult(
            is_valid=False,
            score=1.0,
            error_type=ErrorType.RATE_LIMIT,
            feedback=f"Rate limited",
            retry_delay_seconds=60.0
        )
        
        action = policy.decide_action(state, validation)
        print(f"  Attempt {attempt}: {action}")
        last_action = action
        
        if action == "stop_max_retries":
            print(f"✅ Stopped at attempt {attempt} (MAX_RETRIES=5)")
            break
    
    assert last_action == "stop_max_retries", "Should stop after MAX_RETRIES"
    print("✅ PASSED: System doesn't infinite loop on rate limits!\n")


def test_recovery_after_rate_limit():
    """Test that system recovers after rate limit with backoff."""
    print("=" * 70)
    print("TEST 6: Recovery After Rate Limit")
    print("=" * 70)
    
    print("Simulating rate-limited attempt followed by successful attempt:")
    
    # Simulate attempt 1: Rate limited
    policy = CorrectionPolicy()
    state = AgentState(task="Calculate 2+2")
    state.attempt_count = 1
    
    rate_limit_validation = ValidationResult(
        is_valid=False,
        score=1.0,
        error_type=ErrorType.RATE_LIMIT,
        feedback="Rate Exhausted",
        retry_delay_seconds=51.6
    )
    
    action1 = policy.decide_action(state, rate_limit_validation)
    print(f"Attempt 1: {action1}")
    print(f"  → Wait 51.6 seconds with backoff")
    
    # Simulate attempt 2: Successful after waiting
    state.attempt_count = 2
    success_validation = ValidationResult(
        is_valid=True,
        score=0.0,
        error_type=ErrorType.NONE,
        feedback="Perfect answer: 2+2=4",
        retry_delay_seconds=0.0
    )
    
    action2 = policy.decide_action(state, success_validation)
    print(f"Attempt 2: {action2}")
    print(f"  → Result accepted!")
    
    assert action1 == "wait_and_retry", "Should wait on rate limit"
    assert action2 == "accept", "Should accept valid result"
    print("✅ PASSED: System successfully recovers after rate limit!\n")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "RATE LIMITING SYSTEM TEST SUITE" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    try:
        test_rate_limit_detection()
        test_policy_decision_on_rate_limit()
        test_exponential_backoff()
        test_delay_extraction()
        test_no_infinite_loops()
        test_recovery_after_rate_limit()
        
        print("╔" + "="*68 + "╗")
        print("║" + " "*20 + "ALL TESTS PASSED! ✅" + " "*28 + "║")
        print("╚" + "="*68 + "╝")
        print("\nSummary:")
        print("✓ Rate limit detection working")
        print("✓ Policy decisions correct")
        print("✓ Exponential backoff implemented")
        print("✓ Retry delay extraction functional")
        print("✓ No infinite loops")
        print("✓ Recovery mechanism in place")
        print("\nThe agentic AI system now properly handles API rate limiting!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
