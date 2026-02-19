from google import genai

client = genai.Client(api_key="AIzaSyB99EyzXY3XG2RZBI2pZoZFDlgfIC-26Vc")  # ← your key here

models = client.models.list()

for model in models:
    print(f"Model name: {model.name}")
    print(f"Display name: {model.display_name}")
    print(f"Supported methods: {model.supported_generation_methods}")
    print("-" * 40)