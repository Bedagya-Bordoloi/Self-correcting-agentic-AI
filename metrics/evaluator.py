import json

class ExperimentEvaluator:
    def analyze_log(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} steps from {filepath}")
            # You can add more advanced pandas / statistics analysis here later
            if data:
                print("First entry:", data[0])
                print("Last entry:", data[-1])
        except Exception as e:
            print(f"Error analyzing log: {e}")