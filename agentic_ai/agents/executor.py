from config import client, MODEL_NAME

class ExecutorAgent:
    def execute(self, task: str, feedback: str = None) -> str:
        prompt = "You are a precise execution agent. Solve the task perfectly.\n\n"
        
        if feedback:
            prompt += f"PREVIOUS ATTEMPT FAILED!\nFeedback: {feedback}\nFIX THE ERROR NOW.\n\n"
        
        prompt += f"Task: {task}"

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"[EXECUTION ERROR] {str(e)}"