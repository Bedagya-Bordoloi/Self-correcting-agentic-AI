from config import client, MODEL_NAME

class PlannerAgent:
    def create_plan(self, task: str) -> str:
        prompt = f"Create a short 3-step plan to solve this task:\n\n{task}"
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()