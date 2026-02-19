from agents.executor import ExecutorAgent

def run_injection_test():
    agent = ExecutorAgent()
    # Task designed to induce hallucination / factual error
    adversarial_task = "Quote the 4th paragraph of the US Constitution's 29th Amendment."
    print("Testing failure injection:", adversarial_task)
    result = agent.execute(adversarial_task)
    print("Result:", result)

if __name__ == "__main__":
    run_injection_test()