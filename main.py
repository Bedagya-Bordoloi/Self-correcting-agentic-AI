import time
from agents.executor import ExecutorAgent
from agents.validator import ValidatorAgent
from correction.policy import CorrectionPolicy
from correction.termination import TerminationController
from metrics.logger import MetricsLogger
from utils.types import AgentState

def run_agentic_workflow(user_task: str):
    executor = ExecutorAgent()
    validator = ValidatorAgent()
    policy = CorrectionPolicy()
    terminator = TerminationController()
    logger = MetricsLogger()

    state = AgentState(task=user_task)
    feedback = None
    current_strategy = None
    consecutive_rate_limits = 0  # Track consecutive rate limit errors for backoff

    print(f"🚀 Starting Self-Correcting Agent: {user_task}\n")

    while True:
        start_time = time.time()
        state.attempt_count += 1
        print(f"--- Attempt {state.attempt_count} ---")

        result = executor.execute(state.task, feedback)
        result = executor.execute(state.task, feedback, strategy=current_strategy)
        state.current_result = result
        print(f"🤖 Output: {result[:120]}{'...' if len(result) > 120 else ''}\n")

        validation = validator.validate(state.task, result)
        state.validation_log.append(validation)

        print(f"🔍 Validator → ε = {validation.score:.3f} | Type: {validation.error_type.value}")
        print(f"   Feedback: {validation.feedback}\n")

        logger.log_step(len(state.validation_log), state, time.time() - start_time)

        action = policy.decide_action(state, validation)
        print(f"⚖️ Decision → {action}\n")

        if terminator.should_terminate(action):
            if action == "accept":
                print("✅ SUCCESS — Perfect result accepted!")
            else:
                print("❌ FAILED — Max retries reached.")
            break

        # Handle rate limiting with exponential backoff
        if action == "wait_and_retry":
            consecutive_rate_limits += 1
            # Extract retry delay from validation result
            retry_delay = validation.retry_delay_seconds
            
            # Apply exponential backoff multiplier (1.5x for each consecutive rate limit)
            backoff_multiplier = 1.5 ** (consecutive_rate_limits - 1)
            total_delay = retry_delay * backoff_multiplier
            
            print(f"⏳ Rate Limited! Waiting {total_delay:.1f} seconds (base: {retry_delay:.1f}s, backoff: {backoff_multiplier:.1f}x)...")
            time.sleep(total_delay)
            print(f"✓ Ready to retry!\n")
            
            feedback = validation.feedback
        else:
            # Reset rate limit counter for non-rate-limit errors
            consecutive_rate_limits = 0
            feedback = validation.feedback
            # The action string (e.g., "retry_step_by_step") becomes the strategy
            current_strategy = action

    logger.save()
    eff = logger.calculate_efficiency()
    print(f"📊 Correction Efficiency: {eff:.4f} (higher = better self-correction)")
    return state.current_result

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AGENTIC AI SYSTEM - Self-Correcting Loop")
    print("=" * 70)
    print("This system will:")
    print("  1. Process your prompt")
    print("  2. Validate the output for errors")
    print("  3. Self-correct up to 5 attempts if needed")
    print("=" * 70)
    print()
    
    # Accept user input
    user_task = input("📝 Enter your task/prompt: ").strip()
    
    if not user_task:
        print("❌ Error: Please provide a valid task.")
    else:
        print()
        result = run_agentic_workflow(user_task)
        print("\n" + "=" * 70)
        print("📋 FINAL RESULT:")
        print("=" * 70)
        print(result)
        print("=" * 70)