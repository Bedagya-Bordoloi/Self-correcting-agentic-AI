import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# System Configuration
MAX_RETRIES = 3
ACCEPTANCE_THRESHOLD = 0.2
MODEL_NAME = "gemini-2.5-flash"             # ← this is the correct, working name for your key

# Securely load the Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

# Shared client
client = genai.Client(api_key=GOOGLE_API_KEY)

LOG_DB_PATH = "experiment_logs.json"