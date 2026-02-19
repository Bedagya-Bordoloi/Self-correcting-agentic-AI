from agents.executor import ExecutorAgent

def run_baseline():
    agent = ExecutorAgent()
    task = "Calculate the 10th fibonacci number"
    print("Baseline task:", task)
    result = agent.execute(task)
    print("Result:", result)

if __name__ == "__main__":
    run_baseline()