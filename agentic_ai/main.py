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

    print(f"🚀 Starting Self-Correcting Agent: {user_task}\n")

    while True:
        start_time = time.time()
        state.attempt_count += 1
        print(f"--- Attempt {state.attempt_count} ---")

        result = executor.execute(state.task, feedback)
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

        feedback = validation.feedback

    logger.save()
    eff = logger.calculate_efficiency()
    print(f"📊 Correction Efficiency: {eff:.4f} (higher = better self-correction)")
    return state.current_result

if __name__ == "__main__":
    task = "Write a Python script that prints the first 5 prime numbers in reverse order as strings: ['11', '7', '5', '3', '2']"
    run_agentic_workflow(task)